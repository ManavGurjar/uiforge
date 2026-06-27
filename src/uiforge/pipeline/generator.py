"""Code generation — produces TSX component files from UIComponent trees."""

from __future__ import annotations

import anthropic
from anthropic.types import TextBlock

from uiforge.models import DesignTokens, LayoutAnalysis, UIComponent

COMPONENT_PROMPT = """You are a senior React/TypeScript developer. Generate a production-quality React component.

## Component spec
Name: {name}
Type: {type}
Description: {description}
Props detected: {props}
Children: {children}
Shadcn/UI component: {shadcn}
Lucide icon: {icon}

## Design tokens (use these exact values in Tailwind)
Primary: {primary}
Secondary: {secondary}
Background: {bg}
Surface: {surface}
Text: {text}
Muted text: {muted}
Border radius: {radius}

## Rules — follow exactly
1. Use Tailwind CSS only — no inline styles, no CSS modules
2. Use Shadcn/UI components when shadcn_component is specified
3. Use Lucide React for icons: `import {{ {icon_import} }} from 'lucide-react'`
4. Export as named export AND default export
5. Use TypeScript interfaces for props
6. Use realistic placeholder data that matches the description
7. For charts use recharts library
8. Framer Motion for animations on cards/buttons: subtle hover scale
9. Never use absolute positioning or hardcoded pixel values
10. Component must be self-contained and immediately renderable

## Output format
Return ONLY the TypeScript code. No markdown fences, no explanation.
Start with imports, end with `export default ComponentName`"""

PAGE_PROMPT = """You are a senior React/TypeScript developer. Generate the main page component that composes all sub-components.

## Page spec
Page name: {page_name}
Layout: {layout}
Page type: {page_type}

## Components to compose (already exist as separate files)
{component_list}

## Design tokens
Primary: {primary}
Background: {bg}
Surface: {surface}
Border radius: {radius}

## Rules
1. Import all components from '@/components/ComponentName'
2. Layout using Tailwind flex/grid — no absolute positioning
3. The layout must match: {layout}
   - sidebar-main: flex row, sidebar on left (w-64), main content fills rest
   - full-width: single column, full width sections
   - split: two equal columns
   - centered: max-w-7xl mx-auto
   - grid: CSS grid layout
4. Add `min-h-screen bg-background` to root element
5. TypeScript, named + default export

Return ONLY the TypeScript code."""


def _component_children_summary(component: UIComponent) -> str:
    if not component.children:
        return "none"
    return ", ".join(c.name for c in component.children)


def generate_component(
    component: UIComponent,
    tokens: DesignTokens,
    model: str = "claude-sonnet-4-6",
) -> str:
    client = anthropic.Anthropic()

    icon_import = component.lucide_icon or "Circle"

    prompt = COMPONENT_PROMPT.format(
        name=component.name,
        type=component.type,
        description=component.description or f"A {component.type} component",
        props=component.props,
        children=_component_children_summary(component),
        shadcn=component.shadcn_component or "none",
        icon=component.lucide_icon or "none",
        icon_import=icon_import,
        primary=tokens.primary_color,
        secondary=tokens.secondary_color,
        bg=tokens.background_color,
        surface=tokens.surface_color,
        text=tokens.text_color,
        muted=tokens.text_muted,
        radius=tokens.border_radius,
    )

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    code = next(b for b in response.content if isinstance(b, TextBlock)).text.strip()
    if code.startswith("```"):
        import re
        code = re.sub(r"^```(?:tsx?|typescript|jsx?)?\n?", "", code)
        code = re.sub(r"\n?```$", "", code)
    return code


def generate_page(
    analysis: LayoutAnalysis,
    top_level_components: list[UIComponent],
    model: str = "claude-sonnet-4-6",
) -> str:
    client = anthropic.Anthropic()

    component_list = "\n".join(
        f"- {c.name}: {c.description or c.type}" for c in top_level_components
    )

    prompt = PAGE_PROMPT.format(
        page_name=analysis.page_name,
        layout=analysis.layout,
        page_type=analysis.page_type,
        component_list=component_list,
        primary=analysis.tokens.primary_color,
        bg=analysis.tokens.background_color,
        surface=analysis.tokens.surface_color,
        radius=analysis.tokens.border_radius,
    )

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    code = next(b for b in response.content if isinstance(b, TextBlock)).text.strip()
    if code.startswith("```"):
        import re
        code = re.sub(r"^```(?:tsx?|typescript|jsx?)?\n?", "", code)
        code = re.sub(r"\n?```$", "", code)
    return code


def _flatten_components(components: list[UIComponent]) -> list[UIComponent]:
    result: list[UIComponent] = []
    for c in components:
        result.append(c)
        if c.children:
            result.extend(_flatten_components(c.children))
    return result


def generate_all(
    analysis: LayoutAnalysis,
    model: str = "claude-sonnet-4-6",
    on_progress: object = None,
) -> dict[str, str]:
    all_components = _flatten_components(analysis.components)

    generated: dict[str, str] = {}

    for component in all_components:
        if on_progress:
            on_progress(component.name)  # type: ignore[operator]
        code = generate_component(component, analysis.tokens, model=model)
        generated[component.name] = code

    if on_progress:
        on_progress(analysis.page_name)  # type: ignore[operator]
    page_code = generate_page(analysis, analysis.components, model=model)
    generated[f"pages/{analysis.page_name}"] = page_code

    return generated
