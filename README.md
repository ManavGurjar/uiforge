# UIForge

> **Convert any UI screenshot into production-ready React components.**

[![PyPI version](https://img.shields.io/pypi/v/uiforge.svg?color=violet)](https://pypi.org/project/uiforge/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![CI](https://github.com/ManavGurjar/uiforge/actions/workflows/ci.yml/badge.svg)](https://github.com/ManavGurjar/uiforge/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

```bash
uiforge dashboard.png
```

**Output:**

```tsx
<DashboardLayout>
  <Sidebar />
  <Topbar />
  <StatsGrid>
    <RevenueCard />
    <OrdersCard />
    <VisitorsCard />
  </StatsGrid>
  <SalesChart />
  <RecentOrders />
</DashboardLayout>
```

Not `<div><div><div>`. Semantic, named, composable components — ready to `npm run dev`.

---

## Why UIForge?

There are dozens of "screenshot to HTML" tools. UIForge is different:

| Feature | Others | UIForge |
|---|---|---|
| Output | `<div style="position:absolute;left:143px">` | Clean Tailwind + Shadcn/UI |
| Structure | One 1500-line component | Separate `Sidebar.tsx`, `StatsCard.tsx`, etc. |
| Stack | Raw HTML | React + TypeScript + Vite + Tailwind |
| Interactivity | Static HTML | Working dropdowns, modals, tabs |
| Run immediately | No | `npm install && npm run dev` |

## Install

```bash
pip install uiforge

# or with uv (recommended — no install needed)
uvx uiforge dashboard.png
```

## Setup

UIForge uses Claude's vision capabilities. Get a free API key at [console.anthropic.com](https://console.anthropic.com).

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
# Basic — generates a React + Vite + Tailwind project
uiforge dashboard.png

# Choose output directory
uiforge dashboard.png --output ./my-app

# Next.js instead of Vite
uiforge dashboard.png --framework next

# Add context to improve detection
uiforge dashboard.png --context "dark SaaS admin dashboard with sidebar"

# Analyze only (no code generation)
uiforge dashboard.png --dry-run

# Open VS Code when done
uiforge dashboard.png --open
```

## What gets generated

```
my-app/
├── src/
│   ├── Dashboard.tsx          ← main page composing all components
│   ├── components/
│   │   ├── Sidebar.tsx
│   │   ├── Topbar.tsx
│   │   ├── StatsGrid.tsx
│   │   ├── RevenueCard.tsx
│   │   ├── SalesChart.tsx
│   │   └── RecentOrders.tsx
│   ├── lib/
│   │   └── utils.ts
│   └── globals.css
├── package.json               ← React 18 + Tailwind + Shadcn + Framer Motion
├── tailwind.config.js         ← colors extracted from your screenshot
├── tsconfig.json
└── README.md
```

## The pipeline

UIForge runs a 3-step pipeline:

```
Screenshot
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  Step 1 — Vision Analysis (Claude)                      │
│  • Identifies layout: sidebar-main, grid, centered...   │
│  • Names components: Sidebar, StatsCard, TopNav...      │
│  • Extracts design tokens: colors, border radius, fonts │
│  • Detects Shadcn/UI equivalents: Card, Badge, Table... │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  Step 2 — Code Generation (Claude)                      │
│  • Generates each component independently               │
│  • Uses Tailwind CSS (never inline styles)              │
│  • Wires Shadcn/UI components where detected            │
│  • Adds Framer Motion hover animations                  │
│  • Adds Lucide icons matching the original              │
│  • Generates realistic placeholder data                 │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  Step 3 — Project Scaffold                              │
│  • Writes all .tsx files                                │
│  • Generates package.json, tailwind.config.js           │
│  • Creates globals.css with extracted CSS variables     │
│  • Ready: npm install && npm run dev                    │
└─────────────────────────────────────────────────────────┘
```

## Generated stack

- **React 18** + TypeScript
- **Tailwind CSS** (colors extracted from your screenshot)
- **Shadcn/UI** components (Card, Table, Badge, Button, etc.)
- **Lucide React** icons
- **Framer Motion** animations
- **Recharts** for data visualization
- **Vite** or **Next.js**

## Roadmap

- [ ] `--dark` — automatically generate dark mode variants
- [ ] `--responsive` — desktop screenshot → mobile + tablet layouts
- [ ] `--vue` / `--svelte` / `--flutter` framework targets
- [ ] `--figma` — export Figma-compatible tokens
- [ ] URL support: `uiforge https://dribbble.com/shots/...`
- [ ] Video support: `uiforge recording.mp4` (extract frames)
- [ ] Validation loop — render generated UI, compare to original, auto-fix
- [ ] Storybook stories generation
- [ ] i18n scaffolding

## Contributing

UIForge is looking for contributors! Great first issues:

- Add support for Vue 3 + Composition API output
- Improve chart detection (pie, bar, line, area)
- Add `--responsive` flag for mobile layouts
- Implement the render-validation loop
- Add test fixtures (UI screenshots + expected component trees)

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions.

## License

MIT — see [LICENSE](LICENSE).

---

<p align="center">
  Made with ♥ · <a href="https://github.com/ManavGurjar/uiforge/issues">Report a bug</a> · <a href="https://github.com/ManavGurjar/uiforge/discussions">Discussions</a>
</p>
