"""Vision analysis pipeline — sends image to Claude, returns structured LayoutAnalysis."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path

import anthropic

from uiforge.models import DesignTokens, LayoutAnalysis, UIComponent

ANALYSIS_PROMPT = """You are a senior React architect analyzing a UI screenshot.

Analyze this image and return ONLY valid JSON (no markdown, no explanation) with this exact structure:

{
  "page_type": "dashboard|landing|form|auth|profile|settings|ecommerce|blog|other",
  "layout": "sidebar-main|full-width|split|centered|grid",
  "page_name": "PascalCaseName (e.g. Dashboard, LoginPage, ProductListing)",
  "components": [
    {
      "name": "PascalCaseName",
      "type": "navigation|sidebar|topbar|card|stats-card|table|chart|form|hero|footer|header|modal|tabs|search|pagination|profile|list|grid|button|badge|avatar",
      "description": "one sentence describing what this component shows/does",
      "shadcn_component": "Card|Button|Table|Badge|Avatar|Tabs|Dialog|Select|Input|null",
      "lucide_icon": "most-fitting-lucide-icon-name or null",
      "is_repeating": false,
      "props": {
        "title": "extracted text if visible",
        "variant": "default|outline|ghost|destructive|secondary",
        "color": "primary|secondary|success|warning|danger|neutral"
      },
      "children": []
    }
  ],
  "design_tokens": {
    "primary_color": "#hex",
    "secondary_color": "#hex",
    "background_color": "#hex",
    "surface_color": "#hex",
    "text_color": "#hex",
    "text_muted": "#hex",
    "accent_color": "#hex",
    "border_color": "#hex",
    "success_color": "#hex",
    "warning_color": "#hex",
    "danger_color": "#hex",
    "border_radius": "none|sm|md|lg|xl|full",
    "font_family": "inter|roboto|poppins|system|custom"
  }
}

Rules:
- Give every distinct UI region its own named component (never generic names like Component1)
- Nest children inside their parent (sidebar items inside Sidebar, cards inside StatsGrid)
- For repeating elements (table rows, card grids) set is_repeating=true on the container
- Extract real text content from the image for props.title
- Choose the best Shadcn/UI equivalent or null if none fits
- Pick the exact hex colors you see in the image
- Use PascalCase for all component names"""


def _parse_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    return json.loads(text)


def _build_component(raw: dict) -> UIComponent:
    children = [_build_component(c) for c in raw.get("children", [])]
    props = raw.get("props", {})
    if not isinstance(props, dict):
        props = {}
    return UIComponent(
        name=raw.get("name", "UnknownComponent"),
        type=raw.get("type", "div"),
        description=raw.get("description", ""),
        children=children,
        props=props,
        shadcn_component=raw.get("shadcn_component") or None,
        is_repeating=bool(raw.get("is_repeating", False)),
        lucide_icon=raw.get("lucide_icon") or None,
    )


def _build_tokens(raw: dict) -> DesignTokens:
    dt = raw.get("design_tokens", {})
    return DesignTokens(
        primary_color=dt.get("primary_color", "#3B82F6"),
        secondary_color=dt.get("secondary_color", "#6B7280"),
        background_color=dt.get("background_color", "#FFFFFF"),
        surface_color=dt.get("surface_color", "#F9FAFB"),
        text_color=dt.get("text_color", "#111827"),
        text_muted=dt.get("text_muted", "#6B7280"),
        accent_color=dt.get("accent_color", "#8B5CF6"),
        border_color=dt.get("border_color", "#E5E7EB"),
        success_color=dt.get("success_color", "#10B981"),
        warning_color=dt.get("warning_color", "#F59E0B"),
        danger_color=dt.get("danger_color", "#EF4444"),
        border_radius=dt.get("border_radius", "md"),
        font_family=dt.get("font_family", "inter"),
    )


def analyze_image(
    image_path: Path,
    model: str = "claude-sonnet-4-6",
    extra_context: str = "",
) -> LayoutAnalysis:
    client = anthropic.Anthropic()

    suffix = image_path.suffix.lower()
    media_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_map.get(suffix, "image/png")
    image_data = base64.standard_b64encode(image_path.read_bytes()).decode()

    prompt = ANALYSIS_PROMPT
    if extra_context:
        prompt += f"\n\nAdditional context from user: {extra_context}"

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    raw_text = response.content[0].text
    raw = _parse_response(raw_text)

    components = [_build_component(c) for c in raw.get("components", [])]
    tokens = _build_tokens(raw)

    return LayoutAnalysis(
        page_type=raw.get("page_type", "other"),
        layout=raw.get("layout", "full-width"),
        page_name=raw.get("page_name", "App"),
        components=components,
        tokens=tokens,
        raw=raw,
    )
