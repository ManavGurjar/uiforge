"""Tests for UIForge data models."""

from uiforge.models import DesignTokens, UIComponent, LayoutAnalysis


def test_design_tokens_defaults():
    tokens = DesignTokens()
    assert tokens.primary_color == "#3B82F6"
    assert tokens.border_radius == "md"


def test_design_tokens_tailwind_colors():
    tokens = DesignTokens(primary_color="#FF0000")
    colors = tokens.tailwind_config_colors()
    assert colors["primary"] == "#FF0000"
    assert "secondary" in colors
    assert "accent" in colors


def test_ui_component_filename():
    c = UIComponent(name="Sidebar", type="sidebar")
    assert c.filename == "Sidebar.tsx"
    assert c.import_path == "@/components/Sidebar"


def test_ui_component_children():
    child = UIComponent(name="NavItem", type="button")
    parent = UIComponent(name="Sidebar", type="sidebar", children=[child])
    assert len(parent.children) == 1
    assert parent.children[0].name == "NavItem"


def test_layout_analysis_structure():
    tokens = DesignTokens()
    components = [
        UIComponent(name="Topbar", type="navigation"),
        UIComponent(name="StatsCard", type="card", is_repeating=True),
    ]
    analysis = LayoutAnalysis(
        page_type="dashboard",
        layout="sidebar-main",
        page_name="Dashboard",
        components=components,
        tokens=tokens,
    )
    assert analysis.page_name == "Dashboard"
    assert len(analysis.components) == 2
    assert analysis.components[1].is_repeating is True
