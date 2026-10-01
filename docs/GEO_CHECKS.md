# GEO checks

Pluggable checks in `backend/app/geo/`. Each check returns `pass`, `warn`, `fail`, `skipped`, or `error`, plus evidence and a fix hint. A timeout becomes `skipped`. Any other exception becomes `error`. One check cannot fail the audit.

## Registry and context

`catalog.py` registers the checks. `registry.py` runs one tier with `asyncio.gather` and a per-check timeout.

`AuditContext` is built once per audit: URL, raw HTML, response headers, redirect chain, and Playwright rendered HTML/text when the browser step succeeds. Entering the context starts the llms.txt probe, the robots.txt fetch, and the smartphone HTML fetch on one HTTP client, so they overlap Playwright. The sitemap stays lazy. Checks await those tasks. The audit browser closes when the desktop render finishes, unless `mobile_render` will run. That check opens one more context in the same browser and the browser closes as soon as it finishes. `BROWSER_MAX_HOLD_S` is only a backstop.

Tiers:

- **fast** — runs with the Playwright audit and returns on `POST /api/audit` and `POST /api/generate-fix`.
- **deep** — does not block. The first response includes `geo_job_id`. `GET /api/geo-jobs/{job_id}` returns deep checks as each one finishes (`asyncio.as_completed`).

`InMemoryTTLCache` stores each `pass`, `warn`, or `fail` result for 10 minutes (`DEFAULT_TTL_S = 600`), keyed by normalized URL plus check id. `skipped` and `error` are not stored. A repeat audit reruns only the missing checks. `geo_job_id` is null only when every check is already cached. Otherwise the job runs the missing deep checks.

Thresholds live in `backend/app/geo/config.py`.

## Fast checks

| id | What it looks at | Thresholds | Fix hint when it fails or warns |
|----|------------------|------------|----------------------------------|
| `ai_bot_access` | GPTBot, OAI-SearchBot, PerplexityBot, ClaudeBot, Google-Extended versus one browser user agent; robots.txt, `X-Robots-Tag`, meta robots | Body shorter than `BOT_BODY_RATIO_FAIL` (0.5) of the baseline, or 403/429/challenge markers | Allow the blocked agent and serve the same HTML a browser receives |
| `bot_view_diff` | Title, H1, main word count, primary content in raw HTML versus rendered text | Reuses `TEXT_DELTA_CRITICAL` (2000) and `TEXT_DELTA_MODERATE` (500) from `js_dependency.py` | Put the primary copy in the raw HTML |
| `answer_readiness` | HTML only | `QUESTION_HEADING_MIN_SHARE` 0.2, answer window 100–150 words, `MIN_MAIN_WORDS` 80 | Add a direct answer under a question heading |
| `schema_validation` | JSON-LD `@type`, `sameAs`, `author`, `datePublished`, `dateModified` | Expected type from `expected_schema_type(url)` | Add the missing JSON-LD fields for that type |
| `freshness_consistency` | JSON-LD `dateModified`, sitemap `lastmod`, `Last-Modified` | `STALE_AFTER_DAYS` 180, `DATE_CONFLICT_DAYS` 7. Timeout is 6 seconds | Update the stale or conflicting dates |
| `canonical_and_redirects` | Redirect chain, canonical href, noindex | Warn at `REDIRECT_CHAIN_WARN` 2, fail at `REDIRECT_CHAIN_FAIL` 4 | Point the canonical at the final URL and shorten the chain |
| `llms_txt` | `/llms.txt` on the analyzed domain and whether it lists the page | Fail when the file is missing, warn when the page is absent | Publish `/llms.txt` and list this page |
| `mobile_parity` | Smartphone HTML versus the desktop raw fetch: title, H1, main-text ratio, JSON-LD on both, final host, viewport meta, `rel=alternate` with `media` | Warn below `MOBILE_MAIN_TEXT_RATIO_WARN` (0.8) or on viewport/alternate issues. Fail below `MOBILE_MAIN_TEXT_RATIO_FAIL` (0.5), on a different H1, or on a different final host. Timeout 8 seconds. The fetch starts with the audit, so added wait is about 0 unless that GET is the slowest check | Serve the same main content to mobile visitors and add a viewport meta tag |

`freshness_consistency` is the check that can add wait when sitemap discovery is slower than Playwright. Its timeout caps that wait. `mobile_parity` only awaits a fetch that already started. Worst case is its 8 second timeout. A failing check cannot fail the audit.

## Deep checks

| id | What it looks at | Bounds | Fix hint |
|----|------------------|--------|----------|
| `orphan_page_check` | Sitemap URLs that a crawl never links | `MAX_CRAWL_PAGES` 25, `MAX_CRAWL_SECONDS` 10, `MAX_DEPTH` 2 | Add an internal link from the homepage or a section index |
| `llm_citability_review` | Main text plus uncited Peec prompts, or questions built from the title and H1 | Temperature 0, structured output, one retry inside the check timeout | Add a direct answer for each question in the main HTML |
| `mobile_render` | Rendered phone text versus desktop rendered text, and a fixed or sticky element covering most of the viewport | Same text ratios as `mobile_parity`. Off unless `MOBILE_RENDER_ENABLED` is set or `mobile_parity` is warn or fail. Timeout `MOBILE_RENDER_TIMEOUT_S` (12). `BROWSER_MAX_HOLD_S` is that timeout plus `BROWSER_HOLD_MARGIN_S` (8) | Serve the same main content, and remove or delay interstitials that cover the page |

Citability uses `make_chat_model(0)` in `backend/app/llm.py`: OpenRouter `https://openrouter.ai/api/v1`, model `google/gemma-4-26b-a4b-it:free`, env `OPEN_ROUTE_API_KEY`. A missing key returns `skipped` with no retry. HTTP 429 or a transient network error retries once when `Retry-After` fits in the check timeout, then returns `skipped`.

Fail and warn hints from fast checks are appended to the generate-fix checklist on the first response. The dashboard appends deep hints as the job updates.

## What to fix first

The numbered list is a hand-set heuristic. Each check has an assumed citation impact and an assumed fix effort in `frontend/src/lib/geoChecks.ts`. Higher assumed impact comes first, then the smaller change. That order is not a measured result.
