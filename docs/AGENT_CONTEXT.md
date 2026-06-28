# Agent Context (token-optimized)

> @-reference this file at session start. Points to exact files — avoid reading the whole repo.

## What this project does

Peec AI → sitemap/citation gaps → Playwright JS audit + **target-site /llms.txt probe** → fix templates (JSON-LD + llms.txt) + Gemini outreach.

## File map (where to edit)

| Feature | File | Key symbols |
|---------|------|-------------|
| API routes | `backend/app/main.py` | `/api/gaps`, `/api/generate-fix`, `/api/audit` |
| Playwright + guidance | `backend/app/agent.py` | `CrawlabilityAgent`, `fetch_and_analyze`, `_generate_guidance`, `build_fix_instructions` |
| **llms.txt probe + template** | `backend/app/llms_txt_analyzer.py` | `probe_llms_txt`, `build_llms_txt_template`, `parse_llms_txt_links` |
| Sitemap gaps | `backend/app/sitemap_analyzer.py` | `fetch_sitemap_urls`, `get_ai_citation_gaps` |
| Peec API | `backend/app/peec_client.py` | `PeecClient` |
| Fix panel UI | `frontend/src/pages/Dashboard.jsx` | Technical Health Matrix ~L514, llms.txt template ~L605 |
| Deep audit UI | `frontend/src/pages/PageDetail.jsx` | signals grid ~L143, llms.txt card |

## llms.txt flow (implemented)

1. `fetch_and_analyze(url)` starts `probe_llms_txt(domain, url)` **in parallel** with Playwright
2. Signals merged: `has_llms_txt`, `llms_txt_valid`, `llms_txt_lists_page`, `llms_txt_link_count`, `llms_txt_url`, `domain`
3. `_generate_guidance` → `id: llms_txt` when missing or page not listed
4. `build_fix_instructions` → `llms_txt_template` + checklist item
5. Dashboard matrix row + copy-paste template block

## API: POST /api/generate-fix

Returns: `metrics`, `guidance`, `checklist`, `json_ld`, **`llms_txt_template`**

## JS audit signals (same `metrics` object)

`js_impact`, `unused_js_pct`, `js_payload_mb`, `lcp_seconds`, `console_errors`, `has_json_ld`, `text_delta`, `load_time_ms`

Guidance IDs: `js_hydration`, `js_payload`, `unused_js`, `console_errors`, `lcp`, `structured_data`, `load_time`, **`llms_txt`**

## Tests

- `backend/tests/test_api_integration.py` — FastAPI routes with mocked Peec/sitemap/agent
- `backend/tests/test_peec_client.py` — Peec availability and auth handling
- `backend/tests/test_sitemap_analyzer.py` — citation gap logic
- `backend/tests/test_agent_fix.py` — `build_fix_instructions` unit tests
- `backend/tests/test_agent.py` — Playwright integration (`pytest -m integration`)
- `backend/tests/test_llms_txt.py` — llms.txt parse/template unit tests
- `frontend/src/lib/api.test.js` — API base URL helper
- `frontend/src/pages/Dashboard.test.jsx` — Peec UI visibility integration tests

Run: `sh scripts/validate.sh` (lint + tests via Docker Compose).

## Dev workflow

Docker Compose is the only required tooling at the repo root:

```bash
docker compose up --build                              # dev — hot reload
docker compose -f docker-compose.prod.yml up --build   # prod — nginx + slim images
sh scripts/validate.sh                                 # lint + test in containers
```

## Known bugs (unchanged)

- `build_fix_instructions` Nothing-branded JSON-LD
- Frontend uses `VITE_API_URL` via `frontend/src/lib/api.js` (defaults to localhost:8000)
- `main.py` L170: benchmark `len(sitemap_urls)` on dict

## Env

`PEEC_API_KEY`, `GEMINI_API_KEY` in root `.env`

## More detail

- `docs/LLMS_TXT_INTEGRATION.md` — llms.txt design
- `docs/JS_CITATION_AUDIT.md` — JS thresholds
- `docs/ARCHITECTURE.md` — system diagram
