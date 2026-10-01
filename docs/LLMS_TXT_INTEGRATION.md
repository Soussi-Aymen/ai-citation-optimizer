# llms.txt Integration (implemented)

**Scope:** Probe and recommend `/llms.txt` on the **analyzed website** — runs in parallel with JS audit in `fetch_and_analyze`.

## Code locations

| Piece | File |
|-------|------|
| Probe + parse + template | `backend/app/llms_txt_analyzer.py` |
| Fast GEO check | `backend/app/geo/checks/llms_txt.py` |
| Early task | `backend/app/geo/context.py` `AuditContext.llms_txt` |
| Signal copy + guidance | `backend/app/agent.py` → `_audit_body`, `_generate_guidance`, `build_fix_instructions` |
| API (unchanged route) | `backend/app/main.py` → `POST /api/generate-fix` returns `llms_txt_template` |
| Health matrix row | `frontend/src/pages/Dashboard.tsx` |
| Template copy block | `frontend/src/pages/Dashboard.tsx` |
| Audit signals card | `frontend/src/pages/PageDetail.tsx` |
| Unit tests | `backend/tests/test_llms_txt.py`, `backend/tests/test_geo_context.py` |

## Signals (in `metrics` / `signals`)

- `has_llms_txt` — 200 response from `/llms.txt` or `/llm.txt`
- `llms_txt_valid` — has `# H1` per spec
- `llms_txt_lists_page` — analyzed URL appears in link list
- `llms_txt_link_count`, `llms_txt_url`, `domain`

## Guidance `id: llms_txt`

- **Bad** — no file on domain
- **Medium/Bad** — file exists but page not listed

## Template

`build_llms_txt_template(url)` in `llms_txt_analyzer.py` — user deploys at `https://{analyzed-domain}/llms.txt`.

## Not in this repo

No root `llms.txt` in the optimizer project itself.
