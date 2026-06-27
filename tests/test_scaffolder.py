"""Tests for project scaffolder."""

import json
from pathlib import Path
import pytest
from uiforge.models import DesignTokens, LayoutAnalysis, UIComponent
from uiforge.pipeline.scaffolder import scaffold_project, _tailwind_config, _package_json


def _make_analysis() -> LayoutAnalysis:
    return LayoutAnalysis(
        page_type="dashboard",
        layout="sidebar-main",
        page_name="Dashboard",
        components=[
            UIComponent(name="Sidebar", type="sidebar", description="Left nav"),
            UIComponent(name="StatsCard", type="card", description="Metric card"),
        ],
        tokens=DesignTokens(),
    )


def test_tailwind_config_contains_colors():
    tokens = DesignTokens(primary_color="#FF0000")
    cfg = _tailwind_config(tokens)
    assert "#FF0000" in cfg
    assert "tailwindcss-animate" in cfg


def test_package_json_vite():
    pkg = json.loads(_package_json("dashboard", "vite"))
    assert "vite" in pkg["devDependencies"]
    assert "react" in pkg["dependencies"]
    assert "framer-motion" in pkg["dependencies"]
    assert "lucide-react" in pkg["dependencies"]


def test_package_json_next():
    pkg = json.loads(_package_json("dashboard", "next"))
    assert "next" in pkg["dependencies"]
    assert pkg["scripts"]["dev"] == "next dev"


def test_scaffold_project_creates_files(tmp_path: Path):
    analysis = _make_analysis()
    generated = {
        "Sidebar": "export const Sidebar = () => <aside>Sidebar</aside>;\nexport default Sidebar;",
        "StatsCard": "export const StatsCard = () => <div>Card</div>;\nexport default StatsCard;",
        "pages/Dashboard": "import Sidebar from '@/components/Sidebar';\nexport default function Dashboard() { return <div><Sidebar /></div>; }",
    }
    written = scaffold_project(tmp_path, analysis, generated, framework="vite")
    paths = {p.name for p in written}
    assert "package.json" in paths
    assert "tailwind.config.js" in paths
    assert "tsconfig.json" in paths
    assert "globals.css" in paths
    assert "utils.ts" in paths
    assert "Sidebar.tsx" in paths
    assert "StatsCard.tsx" in paths
    assert "Dashboard.tsx" in paths
    assert "README.md" in paths


def test_scaffold_readme_content(tmp_path: Path):
    analysis = _make_analysis()
    generated = {"pages/Dashboard": "export default function Dashboard() { return <div/>; }"}
    scaffold_project(tmp_path, analysis, generated, framework="vite")
    readme = (tmp_path / "README.md").read_text()
    assert "UIForge" in readme
    assert "npm install" in readme
    assert "npm run dev" in readme
