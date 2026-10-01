import re

from bs4 import BeautifulSoup
from pydantic import BaseModel

from ..base import GeoCheck
from ..context import AuditContext
from ..js_dependency import js_dependency
from ..models import CheckStatus


class BotViewEvidence(BaseModel):
    title: str = ""
    h1: str = ""
    raw_word_count: int = 0
    rendered_word_count: int = 0
    main_word_count: int = 0
    primary_content_in_raw_html: bool = False
    js_impact: str = "LOW"
    text_delta: int = 0


class BotViewDiffCheck(GeoCheck):
    id = "bot_view_diff"
    name = "No-JS crawler view"
    tier = "fast"
    timeout_s = 2
    evidence_model = BotViewEvidence

    async def run(self, ctx: AuditContext):
        raw = BeautifulSoup(ctx.raw_html or "", "html.parser")
        rendered_html = ctx.rendered_html or ctx.raw_html or ""
        rendered = BeautifulSoup(rendered_html, "html.parser")
        title = _text(raw.find("title"))
        h1 = _text(raw.find("h1"))
        main = raw.find("main") or raw.find("article") or raw.body
        main_text = _text(main)
        raw_words = _words(_text(raw))
        rendered_source = (
            ctx.rendered_text if ctx.rendered_text is not None else _text(rendered)
        )
        rendered_words = _words(rendered_source)
        dependency = js_dependency(len(_text(raw)), len(rendered_source))
        primary = bool(h1) and h1.lower() in (ctx.raw_html or "").lower()
        evidence = BotViewEvidence(
            title=title,
            h1=h1,
            raw_word_count=len(raw_words),
            rendered_word_count=len(rendered_words),
            main_word_count=len(_words(main_text)),
            primary_content_in_raw_html=primary and len(raw_words) > 20,
            js_impact=dependency["js_impact"],
            text_delta=dependency["text_delta"],
        )
        if ctx.rendered_html is None:
            status = CheckStatus.WARN
            hint = "Render the page so the no-JS comparison can be completed."
        elif (
            not evidence.primary_content_in_raw_html or evidence.js_impact == "CRITICAL"
        ):
            status = CheckStatus.FAIL
            hint = "Put the title, H1, and main answer in the initial HTML, not only after JavaScript."
        elif evidence.js_impact == "MODERATE":
            status = CheckStatus.WARN
            hint = "Reduce client-rendered text so a no-JS crawler sees the same main content."
        else:
            status = CheckStatus.PASS
            hint = "A no-JS crawler can read the primary content."
        return self.finish(status, evidence, hint)


def _text(node) -> str:
    if node is None:
        return ""
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()


def _words(text: str) -> list[str]:
    return [word for word in text.split(" ") if word]
