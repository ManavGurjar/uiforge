"""Tests for the analyzer pipeline (offline — no API calls)."""

import json
from uiforge.pipeline.analyzer import _parse_response, _build_component, _build_tokens


SAMPLE_RESPONSE = {
    "page_type": "dashboard",
    "layout": "sidebar-main",
    "page_name": "Dashboard",
    "components": [
        {
            "name": "Sidebar",
            "type": "sidebar",
            "description": "Navigation sidebar with menu items",
            "shadcn_component": None,
            "lucide_icon": "LayoutDashboard",
            "is_repeating": False,
            "props": {"title": "Admin"},
            "children": [
                {
                    "name": "NavItem",
                    "type": "button",
                    "description": "Sidebar navigation link",
                    "shadcn_component": "Button",
                    "lucide_icon": "Home",
                    "is_repeating": True,
                    "props": {},
                    "children": [],
                }
            ],
        },
        {
            "name": "StatsGrid",
            "type": "stats",
            "description": "Grid of metric cards",
            "shadcn_component": "Card",
            "lucide_icon": None,
            "is_repeating": False,
            "props": {},
            "children": [],
        },
    ],
    "design_tokens": {
        "primary_color": "#3B82F6",
        "secondary_color": "#6B7280",
        "background_color": "#FFFFFF",
        "surface_color": "#F9FAFB",
        "text_color": "#111827",
        "text_muted": "#6B7280",
        "accent_color": "#8B5CF6",
        "border_color": "#E5E7EB",
        "success_color": "#10B981",
        "warning_color": "#F59E0B",
        "danger_color": "#EF4444",
        "border_radius": "md",
        "font_family": "inter",
    },
}


def test_parse_response_plain_json():
    text = json.dumps(SAMPLE_RESPONSE)
    result = _parse_response(text)
    assert result["page_name"] == "Dashboard"


def test_parse_response_with_markdown_fence():
    text = "```json\n" + json.dumps(SAMPLE_RESPONSE) + "\n```"
    result = _parse_response(text)
    assert result["page_type"] == "dashboard"


def test_build_component_nested():
    raw = SAMPLE_RESPONSE["components"][0]
    component = _build_component(raw)
    assert component.name == "Sidebar"
    assert component.type == "sidebar"
    assert component.lucide_icon == "LayoutDashboard"
    assert len(component.children) == 1
    assert component.children[0].name == "NavItem"
    assert component.children[0].is_repeating is True


def test_build_component_shadcn():
    raw = SAMPLE_RESPONSE["components"][1]
    component = _build_component(raw)
    assert component.shadcn_component == "Card"
    assert component.lucide_icon is None


def test_build_tokens():
    tokens = _build_tokens(SAMPLE_RESPONSE)
    assert tokens.primary_color == "#3B82F6"
    assert tokens.border_radius == "md"
    assert tokens.font_family == "inter"


def test_build_tokens_missing_fields():
    tokens = _build_tokens({})
    assert tokens.primary_color == "#3B82F6"
    assert tokens.border_radius == "md"
