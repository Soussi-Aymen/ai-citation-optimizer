# GEO checks

Pluggable checks in `backend/app/geo/`. Each check returns `pass`, `warn`, `fail`, `skipped`, or `error`, plus evidence and a fix hint. A timeout becomes `skipped`. Any other exception becomes `error`. One check cannot fail the audit.

## Registry and context

`catalog.py` registers the checks. `registry.py` runs one tier with `asyncio.gather` and a per-check timeout.

`AuditContext` is built once per audit: URL, raw HTML, response headers, redirect chain, and Playwright rendered HTML/text when the browser step succeeds. Checks read that object. `robots.txt` and the sitemap are loaded lazily and reused.

Tiers:

- **fast** — runs with the Playwright audit and returns on `POST /api/audit` and `POST /api/generate-fix`.
- **deep** — does not block. The first response includes `geo_job_id`. `GET /api/geo-jobs/{job_id}` returns deep checks as each one finishes (`asyncio.as_completed`).

`InMemoryTTLCache` stores finished fast and deep results for 10 minutes (`DEFAULT_TTL_S = 600`), keyed by normalized URL (lowercase host, no fragment, no trailing slash). A cache hit sets `geo_job_id` to null and returns both tiers.

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

`freshness_consistency` is the check that can add wait when sitemap discovery is slower than Playwright. Its timeout caps that wait.

## Deep checks

| id | What it looks at | Bounds | Fix hint |
|----|------------------|--------|----------|
| `orphan_page_check` | Sitemap URLs that a crawl never links | `MAX_CRAWL_PAGES` 25, `MAX_CRAWL_SECONDS` 10, `MAX_DEPTH` 2 | Add an internal link from the homepage or a section index |
| `llm_citability_review` | Main text plus uncited Peec prompts, or questions built from the title and H1 | Temperature 0, structured output, no retry | Add a direct answer for each question in the main HTML |

Citability uses `make_chat_model(0)` in `backend/app/llm.py`: OpenRouter `https://openrouter.ai/api/v1`, model `google/gemma-4-26b-a4b-it:free`, env `OPEN_ROUTE_API_KEY`. A missing key or HTTP 429 returns `skipped`.

Fail and warn hints from fast checks are appended to the generate-fix checklist on the first response. The dashboard appends deep hints as the job updates.
