"""Project scaffolding — writes the complete runnable project to disk."""

from __future__ import annotations

import json
from pathlib import Path

from uiforge.models import DesignTokens, LayoutAnalysis

RADIUS_MAP = {
    "none": "0px",
    "sm": "0.25rem",
    "md": "0.5rem",
    "lg": "0.75rem",
    "xl": "1rem",
    "full": "9999px",
}


def _package_json(project_name: str, framework: str) -> str:
    next_deps = {
        "next": "^14.2.0",
        "react": "^18.3.0",
        "react-dom": "^18.3.0",
    } if framework == "next" else {
        "react": "^18.3.0",
        "react-dom": "^18.3.0",
    }

    scripts = (
        {"dev": "next dev", "build": "next build", "start": "next start", "lint": "next lint"}
        if framework == "next"
        else {"dev": "vite", "build": "vite build", "preview": "vite preview", "lint": "eslint ."}
    )

    pkg = {
        "name": project_name.lower().replace(" ", "-"),
        "version": "0.1.0",
        "private": True,
        "scripts": scripts,
        "dependencies": {
            **next_deps,
            "@radix-ui/react-icons": "^1.3.0",
            "class-variance-authority": "^0.7.0",
            "clsx": "^2.1.0",
            "framer-motion": "^11.3.0",
            "lucide-react": "^0.400.0",
            "recharts": "^2.12.0",
            "tailwind-merge": "^2.3.0",
            "tailwindcss-animate": "^1.0.7",
        },
        "devDependencies": {
            "@types/node": "^20.0.0",
            "@types/react": "^18.3.0",
            "@types/react-dom": "^18.3.0",
            "autoprefixer": "^10.4.0",
            "eslint": "^8.57.0",
            "postcss": "^8.4.0",
            "tailwindcss": "^3.4.0",
            "typescript": "^5.5.0",
        },
    }

    if framework == "vite":
        pkg["devDependencies"]["@vitejs/plugin-react"] = "^4.3.0"
        pkg["devDependencies"]["vite"] = "^5.3.0"

    return json.dumps(pkg, indent=2)


def _tailwind_config(tokens: DesignTokens) -> str:
    radius = RADIUS_MAP.get(tokens.border_radius, "0.5rem")
    return f"""/** @type {{import('tailwindcss').Config}} */
module.exports = {{
  darkMode: ["class"],
  content: [
    "./src/**/*.{{ts,tsx}}",
    "./app/**/*.{{ts,tsx}}",
    "./pages/**/*.{{ts,tsx}}",
    "./components/**/*.{{ts,tsx}}",
  ],
  theme: {{
    extend: {{
      colors: {{
        primary: {{
          DEFAULT: "{tokens.primary_color}",
          foreground: "#ffffff",
        }},
        secondary: {{
          DEFAULT: "{tokens.secondary_color}",
          foreground: "#ffffff",
        }},
        accent: {{
          DEFAULT: "{tokens.accent_color}",
          foreground: "#ffffff",
        }},
        success: "{tokens.success_color}",
        warning: "{tokens.warning_color}",
        danger: "{tokens.danger_color}",
        background: "{tokens.background_color}",
        surface: "{tokens.surface_color}",
        muted: "{tokens.text_muted}",
        border: "{tokens.border_color}",
      }},
      borderRadius: {{
        DEFAULT: "{radius}",
        sm: "calc({radius} - 4px)",
        md: "{radius}",
        lg: "calc({radius} + 4px)",
        xl: "calc({radius} + 8px)",
      }},
      fontFamily: {{
        sans: ["{tokens.font_family}", "Inter", "system-ui", "sans-serif"],
      }},
    }},
  }},
  plugins: [require("tailwindcss-animate")],
}};
"""


def _tsconfig() -> str:
    return json.dumps({
        "compilerOptions": {
            "target": "ES2017",
            "lib": ["dom", "dom.iterable", "esnext"],
            "allowJs": True,
            "skipLibCheck": True,
            "strict": True,
            "noEmit": True,
            "esModuleInterop": True,
            "module": "esnext",
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "jsx": "preserve",
            "incremental": True,
            "plugins": [{"name": "next"}],
            "paths": {"@/*": ["./src/*"]},
        },
        "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
        "exclude": ["node_modules"],
    }, indent=2)


def _postcss_config() -> str:
    return """module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
"""


def _global_css(tokens: DesignTokens) -> str:
    return f"""@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {{
  :root {{
    --background: {tokens.background_color};
    --foreground: {tokens.text_color};
    --primary: {tokens.primary_color};
    --secondary: {tokens.secondary_color};
    --accent: {tokens.accent_color};
    --muted: {tokens.text_muted};
    --border: {tokens.border_color};
    --surface: {tokens.surface_color};
  }}

  * {{
    @apply border-border;
  }}

  body {{
    @apply bg-background text-foreground;
    font-feature-settings: "rlig" 1, "calt" 1;
  }}
}}
"""


def _vite_config() -> str:
    return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
"""


def _cn_util() -> str:
    return """import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
"""


def _vite_index_html(page_name: str) -> str:
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{page_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""


def _vite_main_tsx(page_name: str) -> str:
    return f"""import React from 'react'
import ReactDOM from 'react-dom/client'
import {page_name} from './{page_name}'
import './globals.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <{page_name} />
  </React.StrictMode>,
)
"""


def _readme(project_name: str, page_name: str, component_names: list[str]) -> str:
    return f"""# {project_name}

> Generated by [UIForge](https://github.com/ManavGurjar/uiforge) — screenshot → production React

## Getting started

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Project structure

```
src/
├── {page_name}.tsx          # Main page
├── components/              # Auto-generated components
{chr(10).join(f"│   ├── {n}.tsx" for n in component_names)}
├── lib/
│   └── utils.ts             # cn() utility
└── globals.css              # Tailwind base styles
```

## Stack

- **React 18** + TypeScript
- **Tailwind CSS** for styling
- **Shadcn/UI** components
- **Lucide React** icons
- **Framer Motion** animations
- **Recharts** for data visualization
- **Vite** for fast development

## Regenerate

```bash
uiforge your-screenshot.png --output .
```

---

*Generated with UIForge*
"""


def scaffold_project(
    output_dir: Path,
    analysis: LayoutAnalysis,
    generated_code: dict[str, str],
    framework: str = "vite",
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    src = output_dir / "src"
    src.mkdir(exist_ok=True)
    (src / "components").mkdir(exist_ok=True)
    (src / "lib").mkdir(exist_ok=True)

    written: list[Path] = []

    def write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)

    component_names = [
        k for k in generated_code if not k.startswith("pages/")
    ]

    write(output_dir / "package.json", _package_json(analysis.page_name, framework))
    write(output_dir / "tailwind.config.js", _tailwind_config(analysis.tokens))
    write(output_dir / "tsconfig.json", _tsconfig())
    write(output_dir / "postcss.config.js", _postcss_config())
    write(src / "globals.css", _global_css(analysis.tokens))
    write(src / "lib" / "utils.ts", _cn_util())

    if framework == "vite":
        write(output_dir / "vite.config.ts", _vite_config())
        write(output_dir / "index.html", _vite_index_html(analysis.page_name))
        write(src / "main.tsx", _vite_main_tsx(analysis.page_name))

    for key, code in generated_code.items():
        if key.startswith("pages/"):
            page_name = key.replace("pages/", "")
            write(src / f"{page_name}.tsx", code)
        else:
            write(src / "components" / f"{key}.tsx", code)

    write(
        output_dir / "README.md",
        _readme(analysis.page_name, analysis.page_name, component_names),
    )

    return written
