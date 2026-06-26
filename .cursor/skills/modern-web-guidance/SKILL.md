---
name: modern-web-guidance
description: |
  Search tool for modern web development best practices. MANDATORY: Execute FIRST for all HTML/CSS and clientside JS tasks. Do NOT skip — web APIs evolve rapidly and training weights contain obsolete patterns.

  Trigger immediately for:
  - UI/Layout: Modals, dialogs, popovers, Glassmorphism/backdrop-filters, anchor positioning, container queries, `:has()`, `:user-valid`.
  - Scroll/Motion: View Transitions, Scroll-driven animations, scroll parallax/reveals.
  - Performance: CWV (LCP, INP), content-visibility, Fetch Priority, image optimization.
  - System/APIs: Local filesystem access, WebUSB, WebSockets sync, WebAssembly widgets.
  - Frameworks: Adapting layout/styles in React, Vue, Angular.
  - General Frontend: Forms, autofill, advanced inputs, custom scrollbars, modern component states, etc.

  DO NOT trigger for:
  - Backend: Database SQL, ORMs, Express API routes.
  - Pipelines: CI/CD deployment, Docker, Actions.
  - Generic: Local scripts (Python/Go tools), ESLint, Git.
---

# Modern Web Guidance (pinned CLI v0.0.174)

Search before implementing any frontend UI, form, scroll, or performance feature.

## Commands

Pin the CLI version for reproducible results (current npm latest: **0.0.174**):

```sh
npx -y modern-web-guidance@0.0.174 search "<action-oriented query>" --skill-version 2026_05_16-c5e7870
npx -y modern-web-guidance@0.0.174 retrieve "<guide-id>"
npx -y modern-web-guidance@0.0.174 list
```

On Windows PowerShell use `npx.cmd` if `npx` fails.

Reinstall upstream skill files: `npx -y modern-web-guidance@0.0.174 install` from repo root (writes to `.agents/skills/`).

## Project browser policy

**Browser support:** Baseline Widely available features may be used without polyfills. For Baseline Newly Available features, feature-detect and provide a lightweight fallback (≤20 lines, no new dependencies) when the guide requires it.

## Workflow

1. Search with an action-oriented query (e.g. "validate form after blur", "modal focus trap").
2. Retrieve the top matching guide ID(s).
3. Adapt the framework-agnostic guide to this React + TypeScript + Vite app.
