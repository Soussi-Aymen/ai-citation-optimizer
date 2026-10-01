import json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from pydantic import BaseModel

from ..base import GeoCheck
from ..config import DATE_CONFLICT_DAYS, STALE_AFTER_DAYS
from ..context import AuditContext
from ..models import CheckStatus


class FreshnessEvidence(BaseModel):
    json_ld_modified: str = ""
    sitemap_lastmod: str = ""
    last_modified_header: str = ""
    stale: bool = False
    contradictory: bool = False
    missing: list[str] = []


class FreshnessConsistencyCheck(GeoCheck):
    id = "freshness_consistency"
    name = "Freshness consistency"
    tier = "fast"
    timeout_s = 6
    evidence_model = FreshnessEvidence

    async def run(self, ctx: AuditContext):
        json_ld = _json_ld_modified(ctx.rendered_html or ctx.raw_html or "")
        header = _header_date(ctx.headers.get("last-modified", ""))
        sitemap_raw = ""
        try:
            sitemap = await ctx.sitemap()
            sitemap_raw = _sitemap_lastmod(sitemap, ctx.final_url or ctx.url)
        except Exception:
            sitemap_raw = ""
        dates = {
            "dateModified": _parse_iso(json_ld),
            "sitemap lastmod": _parse_iso(sitemap_raw),
            "Last-Modified": header,
        }
        present = {name: value for name, value in dates.items() if value is not None}
        evidence = FreshnessEvidence(
            json_ld_modified=json_ld,
            sitemap_lastmod=sitemap_raw,
            last_modified_header=ctx.headers.get("last-modified", ""),
            missing=[name for name, value in dates.items() if value is None],
        )
        now = datetime.now(timezone.utc)
        if (
            present
            and max(present.values()) < now
            and (now - max(present.values())).days > STALE_AFTER_DAYS
        ):
            evidence.stale = True
        if len(present) >= 2:
            ordered = sorted(present.values())
            if (ordered[-1] - ordered[0]).days > DATE_CONFLICT_DAYS:
                evidence.contradictory = True
        if evidence.contradictory or len(evidence.missing) == 3:
            status = CheckStatus.FAIL
            hint = "Publish one dateModified and keep sitemap lastmod and Last-Modified in agreement."
        elif evidence.stale or evidence.missing:
            status = CheckStatus.WARN
            hint = (
                f"Update dateModified when the page changes. "
                f"Content older than {STALE_AFTER_DAYS} days is treated as stale."
            )
        else:
            status = CheckStatus.PASS
            hint = "Published dates agree."
        return self.finish(status, evidence, hint)


def _json_ld_modified(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            parsed = json.loads(script.string or script.get_text() or "")
        except json.JSONDecodeError:
            continue
        items = parsed if isinstance(parsed, list) else [parsed]
        for item in items:
            if isinstance(item, dict) and item.get("dateModified"):
                return str(item["dateModified"])
    return ""


def _sitemap_lastmod(sitemap: dict, url: str) -> str:
    entries = sitemap.get("entries") or []
    target = url.rstrip("/")
    for entry in entries:
        if str(entry.get("loc", "")).rstrip("/") == target:
            return str(entry.get("lastmod") or "")
    return ""


def _header_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
