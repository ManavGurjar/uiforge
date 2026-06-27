"""Data models for UIForge pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DesignTokens:
    primary_color: str = "#3B82F6"
    secondary_color: str = "#6B7280"
    background_color: str = "#FFFFFF"
    surface_color: str = "#F9FAFB"
    text_color: str = "#111827"
    text_muted: str = "#6B7280"
    accent_color: str = "#8B5CF6"
    border_color: str = "#E5E7EB"
    success_color: str = "#10B981"
    warning_color: str = "#F59E0B"
    danger_color: str = "#EF4444"
    border_radius: str = "md"
    font_family: str = "inter"
    spacing_unit: str = "4"

    def tailwind_config_colors(self) -> dict[str, str]:
        return {
            "primary": self.primary_color,
            "secondary": self.secondary_color,
            "accent": self.accent_color,
            "success": self.success_color,
            "warning": self.warning_color,
            "danger": self.danger_color,
        }


@dataclass
class UIComponent:
    name: str
    type: str
    description: str = ""
    children: list[UIComponent] = field(default_factory=list)
    props: dict[str, Any] = field(default_factory=dict)
    shadcn_component: str | None = None
    is_repeating: bool = False
    lucide_icon: str | None = None

    @property
    def filename(self) -> str:
        return f"{self.name}.tsx"

    @property
    def import_path(self) -> str:
        return f"@/components/{self.name}"


@dataclass
class LayoutAnalysis:
    page_type: str
    layout: str
    page_name: str
    components: list[UIComponent]
    tokens: DesignTokens
    raw: dict[str, Any] = field(default_factory=dict)


SHADCN_COMPONENTS = {
    "button", "input", "card", "badge", "table", "dialog", "dropdown-menu",
    "select", "tabs", "avatar", "progress", "separator", "skeleton",
    "tooltip", "popover", "sheet", "alert", "checkbox", "switch",
    "slider", "textarea", "label", "scroll-area",
}

COMPONENT_TYPE_MAP = {
    "navigation": "nav",
    "sidebar": "aside",
    "card": "div",
    "table": "div",
    "chart": "div",
    "form": "form",
    "header": "header",
    "footer": "footer",
    "hero": "section",
    "modal": "div",
    "tabs": "div",
    "button": "button",
    "input": "input",
    "list": "ul",
    "grid": "div",
    "stats": "div",
    "profile": "div",
    "search": "div",
    "pagination": "div",
}
