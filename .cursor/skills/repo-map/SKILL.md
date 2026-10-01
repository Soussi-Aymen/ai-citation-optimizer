---
name: repo-map
description: >-
  Task-to-file lookup for AI Citation Optimizer. Read this before searching
  the repo for routes, GEO checks, the audit, the matrix, Docker, or tests.
---

# Repo map

Open the row you need. Do not search the repo first. `docs/AGENT_CONTEXT.md` is the API contract. `docs/ARCHITECTURE.md` is the diagram.

| Task | File | Symbol |
|------|------|--------|
| Route or response shape | `backend/app/main.py` | route handlers |
| Playwright audit, browser lifetime, guidance | `backend/app/agent.py` | `fetch_and_analyze`, `_audit_body` |
| OpenRouter model | `backend/app/llm.py` | `make_chat_model`, `OPEN_ROUTE_API_KEY` |
| Check list | `backend/app/geo/checks/__init__.py` | `FAST_CHECKS`, `DEEP_CHECKS` |
| Run one tier, timeouts | `backend/app/geo/registry.py` | `run_tier`, `run_check` |
| Shared page data | `backend/app/geo/context.py` | `AuditContext` async context manager, `load_raw_context` |
| Per-check result store | `backend/app/geo/cache.py` | `InMemoryTTLCache.get`, `put` |
| Deep job polling | `backend/app/geo/jobs.py` | `attach_geo`, `get_job` |
| Thresholds and user agents | `backend/app/geo/config.py` | `AI_BOT_USER_AGENTS` |
| Citability | `backend/app/geo/checks/llm_citability_review.py` | `LlmCitabilityReviewCheck` |
| No-JS text helpers | `backend/app/geo/checks/bot_view_diff.py` | `_text`, `_words` |
| llms.txt probe and template | `backend/app/llms_txt_analyzer.py`, `backend/app/geo/checks/llms_txt.py` | `probe_llms_txt`, `LlmsTxtCheck` |
| Sitemap gaps | `backend/app/sitemap_analyzer.py` | `fetch_sitemap_urls` |
| Peec | `backend/app/peec_client.py` | `PeecClient` |
| Matrix UI | `frontend/src/components/GeoCheckMatrix.tsx` | `GeoCheckMatrix` |
| Fix order | `frontend/src/lib/geoChecks.ts`, `frontend/src/components/FixPriorityList.tsx` | `prioritizeFixes` |
| Dashboard / deep audit pages | `frontend/src/pages/Dashboard.tsx`, `frontend/src/pages/PageDetail.tsx` | pages |
| Tailwind | `frontend/src/index.css`, `frontend/vite.config.ts` | `@tailwindcss/vite` |
| Docker | `docker-compose.yml`, `docker-compose.prod.yml`, `backend/Dockerfile`, `frontend/Dockerfile.prod` | |
| Tests | `backend/tests/test_geo_*.py`, `frontend/src/components/GeoCheckMatrix.test.tsx` | |
| Full check | `sh scripts/validate.sh` | |
| Related-only pre-commit | `.husky/pre-commit` | |
| CI | `.github/workflows/ci.yml` | push and pull request |
