# AI Citation Optimizer

AI Citation Optimizer helps early-stage brands like Nothing Phone, Attio, and BYD close the AI search visibility gap against Apple, Salesforce, and Tesla — built on top of Peec AI's MCP to turn monitoring data into automated action.

![AI Search Dashboard](artifacts/screenshots/dashboard.png)

![Actionable Fix Instructions](artifacts/screenshots/how_to_fix.png)

![Growth Opportunity Analysis](artifacts/screenshots/growth_opportunity.png)

## Key Features

- **Deep Technical AI Audit:** Simulates an AI indexer using a Headless Chromium instance (via Playwright & CDP) to capture and analyze precise technical layers—like Unused JS, JS-to-Text ratio, and DOM depth—that specifically cause AI search bots to fail or time out.
- **Automated Sitemap-to-Citation Mapping:** Instantly identifies the "Discovery Gap" by cross-referencing your sitemap against real-time AI citations, revealing exactly which high-value pages are being ignored by LLM crawlers.
- **Actionable AI-Readiness Fixes:** Provides step-by-step technical instructions, generated copy-paste JSON-LD schema snippets, and **llms.txt templates** for the analyzed site to improve AI discovery and LLM ingestion.
- **Instant Outreach Content Drafting:** Uses Gemini to draft tailored collaboration pitches, Reddit comments, and PR emails for specific gaps identified in your optimization roadmap.
- **Dynamic Growth Projection:** Uses a realistic 50% recovery model to project visibility and citation growth based on technical gap closure and off-page strategic actions.

## How We Measure & Optimize for AI Crawlers

Unlike traditional search engines, AI search bots (like ChatGPT-Search, Perplexity, and Gemini) have much stricter timeouts and struggle with heavy client-side rendering. Our tool identifies these blockers through a **Technical Health Matrix** and prescribes targeted fixes.

### 1. The Measurement Layers (Playwright + CDP)

When you audit a URL, our backend spins up a Headless Chromium browser and attaches via the Chrome DevTools Protocol (CDP) to measure exact AI-crawler blockers:

- **JS Dependency & Bloat:** We measure the delta between raw HTML length and fully rendered text. High JS dependency means AI bots might only see a blank page.
- **Unused JavaScript (Dead Code):** We use CDP precise coverage traces to determine what percentage of downloaded JS functions are actually executed. Dead code wastes the crawler's strict execution budget.
- **JS Bundle Payload Size:** Tracks the exact weight of downloaded JavaScript. Heavy bundles cause AI crawlers to time out before indexing the content.
- **Largest Contentful Paint (LCP):** Evaluates how fast the main content renders for the bot.
- **Console Errors:** Traps live JS errors during the render phase, which often completely break an AI bot's ability to "see" the page.
- **Structured Data (JSON-LD):** Detects if semantic markup exists to feed the LLM easily digestible context.
- **LLM Discovery File (llms.txt):** Probes the analyzed domain for `/llms.txt` in parallel with the browser audit and checks whether the page is listed in the site's curated AI index ([llmstxt.org](https://llmstxt.org/) spec).

### 2. The Improvement Layers (Actionable Fixes)

Instead of just showing raw data, the tool turns these metrics into immediate action:

- **Unified Action Plan:** Every audit generates a single, comprehensive "General Chromium Optimization Tips" section. This provides a framework-agnostic implementation plan to solve all flagged technical issues (JS bloat, LCP, console errors) in one centralized view.
- **Deep Technical Health Matrix:** Replaces generic scores with a detailed list of bot-centric metrics, including JS Hydration impact, Unused JS coverage, LCP, and **llms.txt status**, with explicit 🔴/🟡/✅ status indicators.
- **Copy-Paste Schema Generation:** Automatically generates custom JSON-LD (e.g., `Product`, `Organization`) tailored to the specific URL path to accelerate AI entity recognition.
- **llms.txt Template Generation:** When the analyzed site lacks `/llms.txt` or does not list the page, generates a ready-to-deploy markdown file for `https://your-domain/llms.txt`.

## Architecture

![AI Architecture Overview](artifacts/screenshots/ai_architecture.jpg)

- **Backend**: FastAPI (Python 3.11+)
- **AI Orchestration**: LangChain (for structured chains and prompt templates)
- **AI Agent**: Playwright (for rendered HTML analysis) + Gemini 2.5 Flash
- **Data Provider**: Peec AI API (for citation metrics and domain visibility)
- **Frontend**: React + Vite + TypeScript (strict) + pnpm (Tailwind CSS)
- **Code Quality**: Ruff (backend), ESLint + `tsc` (frontend), optional git pre-commit via Docker
- **Web standards**: Frontend UI follows [modern-web-guidance](https://github.com/GoogleChrome/modern-web-guidance) patterns — accessible forms, native `<details>` disclosures, ARIA tabs, `:focus-visible`, and `prefers-reduced-motion`
- **Progress Tracking**: Dynamic visibility progress visualization at the top of the dashboard

## Getting Started

Docker Compose is the **default, cross-platform** way to run the app (Windows, macOS, WSL/Linux). No local Python or pnpm required — only Docker.

### 1. API keys

Copy the example env file and add your keys:

```bash
cp .env.example .env          # macOS, WSL, Git Bash
```

```powershell
Copy-Item .env.example .env   # Windows PowerShell
```

```env
GEMINI_API_KEY=your_gemini_api_key
PEEC_API_KEY=your_peec_api_key   # optional — Peec features hide if missing or invalid
```

### 2. Start the app

```bash
docker compose up --build
```

**App URL:** [http://localhost:5173](http://localhost:5173)  
**API docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### Platform notes

| Platform | Requirement |
|----------|-------------|
| **Windows / macOS** | [Docker Desktop](https://www.docker.com/products/docker-desktop/) running |
| **WSL Ubuntu** | Docker Desktop with **Settings → Resources → WSL Integration → Ubuntu** enabled |

Frontend dependencies live in the **Docker volume** `frontend_node_modules`, not on your host. If you have `frontend/node_modules/` from an old local setup, delete it — Docker does not need it:

```bash
rm -rf frontend/node_modules
```

**WSL one-time Docker permission** (if `docker ps` fails):

```bash
sudo usermod -aG docker $USER
# then close and reopen Ubuntu (or: wsl --shutdown in PowerShell)
```

---

## Commands (reference)

```bash
docker compose up --build           # start backend + frontend
docker compose down                 # stop services
sh scripts/validate.sh              # lint + test (all checks)
sh scripts/validate.sh --tests-only # pytest + vitest only
sh scripts/validate.sh --lint-only  # ruff + eslint + tsc only
```

### Tests

All checks run **inside Docker**:

```bash
sh scripts/validate.sh
docker compose run --rm --no-deps backend pytest
docker compose run --rm --no-deps frontend pnpm test:run
```

| Layer | Runner | What is covered |
|-------|--------|-----------------|
| **Backend unit** | pytest | Peec client, sitemap analyzer, llms.txt probe, agent fix generation |
| **Backend API** | pytest | FastAPI routes with mocked dependencies |
| **Backend integration** | pytest (`-m integration`) | Playwright audit on react.dev — optional, excluded by default |
| **Frontend** | vitest | API base URL helper, Dashboard form and Peec visibility toggling |

Playwright integration test (optional):

```bash
docker compose run --rm backend pytest -m integration
```

### Pre-commit hook (optional)

```bash
git config core.hooksPath .husky   # one-time
```

Every `git commit` then runs `sh scripts/validate.sh`. Skip once: `git commit --no-verify`.

---

## Optional: local development without Docker

For faster hot-reload iteration, you can run services natively. This path is **not required** for normal use.

```bash
# Backend — Python 3.10+ with venv
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
playwright install chromium
uvicorn app.main:app --reload --port 8000

# Frontend — Node 20+ with pnpm
cd frontend
corepack enable && pnpm install
pnpm dev
```

## API Endpoints

- `GET /api/gaps?domain=<domain>`: Returns a list of non-cited pages, overall performance metrics, and competitor visibility data.
- `GET /api/benchmark?domain=<domain>`: Provides the detailed optimization roadmap, competitor breakdown, and gap sources.
- `POST /api/audit`: Conducts a deep crawlability and AI-readiness audit of a specific URL.
- `POST /api/generate-fix`: Generates an actionable fix checklist, JSON-LD schema, live Playwright metrics, and an **llms.txt template** for the analyzed site.
- `POST /api/generate-content`: Drafts targeted outreach content (emails, comments, scripts) for specific optimization roadmap items.

## Example Usage

1. Enter your domain (e.g., `nothing.tech`) on the Dashboard.
2. Review the **Growth Opportunity** and **Competitor Advantage Breakdown** to see where you stand. (Note: Estimated progress in a realistic benchmark shows around 50% improvement for targeted businesses).
3. Check the **Optimization Roadmap** for high-priority actions and click "Draft Content" to instantly generate outreach emails or comments.
4. Drill down into specific **Gap Sources** (YouTube, Reddit, Editorial) to identify missed citation opportunities.
5. In the **Pages Missing** section, click "How to Fix" to get step-by-step instructions, live JS performance metrics, and an **llms.txt template** to publish on the analyzed domain. Expand guidance sections inline for framework-agnostic fixes. Open **View Deep Technical Audit Report** for the full signal breakdown.

## Developer Docs

Compact reference docs for contributors and AI coding agents (start with `docs/AGENT_CONTEXT.md`):

- [`docs/AGENT_CONTEXT.md`](docs/AGENT_CONTEXT.md) — file map and key symbols (token-optimized)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design and data flows
- [`docs/JS_CITATION_AUDIT.md`](docs/JS_CITATION_AUDIT.md) — Playwright JS metrics and thresholds
- [`docs/LLMS_TXT_INTEGRATION.md`](docs/LLMS_TXT_INTEGRATION.md) — llms.txt probe, guidance, and UI

### Modern web guidance (frontend)

UI and layout work should follow **[modern-web-guidance](https://github.com/GoogleChrome/modern-web-guidance)** (pinned CLI `0.0.174`). Search before implementing forms, tabs, disclosures, or motion:

```bash
npx -y modern-web-guidance@0.0.174 search "<what you are building>" --skill-version 2026_05_16-c5e7870
npx -y modern-web-guidance@0.0.174 retrieve "<guide-id>"
```

Project skill for Cursor agents: `.cursor/skills/modern-web-guidance/SKILL.md`  
Reinstall upstream skill files (from `frontend/`): `cd frontend && npx -y modern-web-guidance@0.0.174 install`

**Patterns used in this app:**

- Visible form labels, `autocomplete`, and `aria-describedby` for errors (domain search)
- Native `<details>` / `<summary>` for expandable fix panels and guidance steps
- WAI-ARIA tablist with keyboard navigation (Gap Sources tabs)
- Global `:focus-visible` rings and `prefers-reduced-motion` for animations
