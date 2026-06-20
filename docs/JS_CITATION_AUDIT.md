# JS Citation Audit (current implementation)

AI crawlers (ChatGPT Search, Perplexity, Gemini) have strict timeouts and often skip JS-rendered content. This project measures **page-level** JS blockers via Playwright + CDP.

## Status: implemented

No WIP markers. Full stack: backend metrics → guidance → Dashboard UI.

## Metrics

| Signal | Source | Thresholds | Guidance ID |
|--------|--------|------------|-------------|
| `text_delta` | rendered text − raw HTML text | >500 MODERATE, >2000 CRITICAL | `js_hydration` |
| `js_impact` | derived from text_delta | LOW / MODERATE / CRITICAL | (UI label) |
| `unused_js_pct` | CDP precise coverage | ≥30% Medium, >60% Bad | `unused_js` |
| `js_payload_mb` | sum JS response sizes | ≥1MB Medium, >3MB Bad | `js_payload` |
| `lcp_seconds` | PerformanceObserver | ≥2.5s Medium, >4s Bad | `lcp` |
| `console_errors` | `page.on("pageerror")` | ≥1 Medium, ≥3 Bad | `console_errors` |
| `has_json_ld` | `<script type="application/ld+json">` | missing → Bad | `structured_data` |
| `has_llms_txt` | `llms_txt_analyzer.probe_llms_txt` | missing → Bad | `llms_txt` |
| `llms_txt_lists_page` | link match in probed file | false → Medium/Bad | `llms_txt` |
| `load_time_ms` | wall clock | ≥2000 Medium, ≥4000 Bad | `load_time` |

## Code locations

```
backend/app/llms_txt_analyzer.py  — probe_llms_txt, build_llms_txt_template
backend/app/agent.py              — parallel probe in fetch_and_analyze, guidance id llms_txt
frontend/src/pages/Dashboard.jsx  — matrix row + llms_txt_template copy block
backend/tests/test_llms_txt.py    — unit tests
```

## API usage

`POST /api/generate-fix` body: `{ "url": "https://..." }`

Response includes:
- `metrics` — signals dict
- `guidance` — array of `{id, metric, score, advice, steps}`
- `checklist`, `json_ld`, `problem` — from `build_fix_instructions`

`POST /api/audit` — same signals + Gemini `performance_report`, `ai_readiness`, etc.

## Improvement opportunities (not yet done)

1. **Domain-agnostic fix copy** — `build_fix_instructions` hardcodes "Nothing", Apple/Samsung competitors
2. **Site-wide JS score** — aggregate worst pages from gap list
3. **Framework detection** — infer Next.js/Shopify from HTML for targeted steps
4. **Pre-render recommendation** — tie `js_impact: CRITICAL` to specific SSR/SSG checklist
5. **llms.txt** — implemented: parallel probe in `fetch_and_analyze`, matrix row, template in fix panel

## UI threshold reference (Dashboard.jsx)

```javascript
// js_impact: CRITICAL | MODERATE | LOW
// unused_js_pct: >60 Bad, >=30 Medium
// js_payload_mb: >3 Bad, >=1 Medium
// lcp_seconds: >4 Bad, >=2.5 Medium
// console_errors: >=3 Bad, >=1 Medium
```

Overall crawlability: Bad if any single metric hits Bad threshold; Medium if any Medium; else Good.
