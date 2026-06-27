<div align="center">

# UIForge

**Convert any UI screenshot into production-ready React components.**

[![PyPI version](https://img.shields.io/pypi/v/uiforge-cli.svg?color=7c3aed)](https://pypi.org/project/uiforge-cli/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![CI](https://github.com/ManavGurjar/uiforge/actions/workflows/ci.yml/badge.svg)](https://github.com/ManavGurjar/uiforge/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

Take a screenshot of any UI. Get a complete, runnable React project in seconds.

```bash
uiforge dashboard.png
```

**Not this:**
```tsx
<div style="position:absolute;left:143px;top:492px;width:241px">
  <div>
    <div>
```

**This:**
```tsx
<DashboardLayout>
  <Sidebar />
  <Topbar />
  <StatsGrid>
    <RevenueCard title="Total Revenue" value="$48,295" trend="+12%" />
    <OrdersCard title="Orders" value="1,429" trend="+8%" />
    <VisitorsCard title="Visitors" value="24.5k" trend="+3%" />
  </StatsGrid>
  <SalesChart />
  <RecentOrders />
</DashboardLayout>
```

Semantic, named, composable — ready to `npm run dev`.

---

## Install

```bash
pip install uiforge-cli
```

Or try without installing:
```bash
uvx uiforge-cli dashboard.png
```

UIForge uses Claude's vision API. Set your key:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

> Get a free key at [console.anthropic.com](https://console.anthropic.com)

---

## Usage

```bash
uiforge dashboard.png                          # React + Vite (default)
uiforge dashboard.png --framework next         # Next.js
uiforge dashboard.png --output ./my-app        # custom output dir
uiforge dashboard.png --context "dark SaaS"   # hint for better results
uiforge dashboard.png --dry-run                # analyze only, no codegen
```

---

## What you get

```
my-app/
├── src/
│   ├── Dashboard.tsx          ← main page, composes everything
│   ├── components/
│   │   ├── Sidebar.tsx        ← each component is its own file
│   │   ├── Topbar.tsx
│   │   ├── StatsGrid.tsx
│   │   ├── RevenueCard.tsx
│   │   ├── SalesChart.tsx     ← recharts, wired up
│   │   └── RecentOrders.tsx   ← real table with mock data
│   ├── lib/utils.ts           ← cn() helper
│   └── globals.css            ← colors extracted from your screenshot
├── package.json
├── tailwind.config.js         ← exact colors from the image
└── tsconfig.json
```

```bash
cd my-app && npm install && npm run dev
```

It runs.

---

## How it works

UIForge runs a 3-step pipeline:

**1 — Analyze**

Claude Vision reads the screenshot and returns a structured component tree: names, types, hierarchy, Shadcn/UI matches, Lucide icon suggestions, and exact hex colors from the image.

**2 — Generate**

Each component is generated independently. UIForge instructs the model to use Tailwind classes only (no `position: absolute`), wire in Shadcn/UI primitives where detected, add Framer Motion hover animations, and include realistic placeholder data.

**3 — Scaffold**

A complete project is written to disk — `package.json`, `tailwind.config.js` with the extracted color palette, `tsconfig.json`, `globals.css`, and all component files.

---

## Generated stack

| | |
|---|---|
| Framework | React 18 + TypeScript |
| Styling | Tailwind CSS (colors from your screenshot) |
| Components | Shadcn/UI |
| Icons | Lucide React |
| Animation | Framer Motion |
| Charts | Recharts |
| Build | Vite or Next.js |

---

## Why not the other tools?

| | Most tools | UIForge |
|---|---|---|
| Output | `<div style="left:143px">` | Tailwind classes |
| Structure | One 1500-line file | One file per component |
| Runs immediately | No | `npm install && npm run dev` |
| Component names | `Component1`, `Box3` | `Sidebar`, `StatsCard` |
| Design tokens | Ignored | Colors wired into `tailwind.config.js` |
| Charts | Static image | Working Recharts component |
| Shadcn/UI | Never | Auto-detected and used |

---

## Roadmap

- [ ] `--dark` — generate light + dark theme variants
- [ ] `--responsive` — one screenshot → desktop + tablet + mobile
- [ ] `--vue` / `--svelte` / `--flutter` output targets
- [ ] URL input: `uiforge https://dribbble.com/shots/...`
- [ ] Render validation — screenshot the output, compare to original, auto-fix
- [ ] Storybook story generation
- [ ] Figma token export

---

## Contributing

Good first issues:
- Vue 3 + Composition API output target
- Better chart detection (pie, area, scatter)
- `--responsive` flag implementation
- Render validation loop
- Test fixtures (screenshots + expected component trees)

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup.

---

## License

MIT
