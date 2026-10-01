import re

from bs4 import BeautifulSoup
from pydantic import BaseModel

from ..base import GeoCheck
from ..config import (
    DIRECT_ANSWER_WINDOW_MAX_WORDS,
    MIN_MAIN_WORDS,
    QUESTION_HEADING_MIN_SHARE,
)
from ..context import AuditContext
from ..models import CheckStatus

QUESTION_RE = re.compile(
    r"^(who|what|when|where|why|how|which|can|does|is|are)\b", re.I
)
STAT_RE = re.compile(r"\b\d+(\.\d+)?%|\b\d{2,}\b")
SOURCE_RE = re.compile(r"\b(according to|source:|cited)\b", re.I)


class AnswerEvidence(BaseModel):
    heading_hierarchy_valid: bool = True
    question_heading_share: float = 0
    direct_answer_in_opening: bool = False
    has_list: bool = False
    has_table: bool = False
    has_faq: bool = False
    has_stat: bool = False
    has_named_source: bool = False
    has_quote: bool = False
    in_main_or_article: bool = False
    main_word_count: int = 0


class AnswerReadinessCheck(GeoCheck):
    id = "answer_readiness"
    name = "Answer readiness"
    tier = "fast"
    timeout_s = 2
    evidence_model = AnswerEvidence

    async def run(self, ctx: AuditContext):
        soup = BeautifulSoup(ctx.raw_html or "", "html.parser")
        if not ctx.raw_html.strip():
            return self.finish(
                CheckStatus.FAIL,
                AnswerEvidence(),
                "Add visible HTML content so an answer can be extracted.",
            )
        headings = soup.find_all(re.compile(r"^h[1-6]$"))
        levels = [int(tag.name[1]) for tag in headings]
        hierarchy_ok = _hierarchy_ok(levels)
        questions = [
            tag for tag in headings if QUESTION_RE.search(tag.get_text(" ", strip=True))
        ]
        share = (len(questions) / len(headings)) if headings else 0
        container = soup.find("main") or soup.find("article")
        main_text = (container or soup.body or soup).get_text(" ", strip=True)
        words = main_text.split()
        opening = " ".join(words[:DIRECT_ANSWER_WINDOW_MAX_WORDS])
        evidence = AnswerEvidence(
            heading_hierarchy_valid=hierarchy_ok,
            question_heading_share=round(share, 2),
            direct_answer_in_opening=_has_direct_answer(opening),
            has_list=bool(soup.find(["ul", "ol"])),
            has_table=bool(soup.find("table")),
            has_faq=bool(soup.find(attrs={"itemtype": re.compile("FAQPage", re.I)}))
            or any("faq" in (tag.get("class") or []) for tag in soup.find_all(True)),
            has_stat=bool(STAT_RE.search(main_text)),
            has_named_source=bool(SOURCE_RE.search(main_text)),
            has_quote=bool(
                soup.find("blockquote") or '"' in main_text or "“" in main_text
            ),
            in_main_or_article=container is not None,
            main_word_count=len(words),
        )
        problems = []
        if not evidence.heading_hierarchy_valid:
            problems.append("fix the heading outline so levels do not skip")
        if headings and evidence.question_heading_share < QUESTION_HEADING_MIN_SHARE:
            problems.append("add question-style headings")
        if (
            not evidence.direct_answer_in_opening
            or evidence.main_word_count < MIN_MAIN_WORDS
        ):
            problems.append("answer the page topic in the first 150 words")
        if not evidence.in_main_or_article:
            problems.append("wrap the main content in main or article")
        if not (evidence.has_list or evidence.has_table or evidence.has_faq):
            problems.append("add a list, table, or FAQ block")
        if problems:
            status = CheckStatus.FAIL if len(problems) >= 3 else CheckStatus.WARN
            hint = "Make the page easier to cite: " + "; ".join(problems) + "."
        else:
            status = CheckStatus.PASS
            hint = "The HTML already presents a citable answer."
        return self.finish(status, evidence, hint)


def _hierarchy_ok(levels: list[int]) -> bool:
    if not levels:
        return False
    if levels[0] != 1:
        return False
    previous = levels[0]
    for level in levels[1:]:
        if level > previous + 1:
            return False
        previous = level
    return True


def _has_direct_answer(opening: str) -> bool:
    sentence = opening.split(".", maxsplit=1)[0].strip()
    return 8 <= len(sentence.split()) <= 40
