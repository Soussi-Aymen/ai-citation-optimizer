"""Structured citability review. Missing key or HTTP 429 skips without retry."""

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from ...llm import make_chat_model
from ..base import GeoCheck
from ..context import AuditContext
from ..models import CheckResult, CheckStatus


class CitabilityReview(BaseModel):
    answerable: bool
    missing_points: list[str] = Field(default_factory=list)
    fix_hint: str = ""


class CitabilityEvidence(BaseModel):
    questions: list[str] = Field(default_factory=list)
    answerable: bool = False
    missing_points: list[str] = Field(default_factory=list)
    reason: str = ""


class LlmCitabilityReviewCheck(GeoCheck):
    id = "llm_citability_review"
    name = "LLM citability review"
    tier = "deep"
    timeout_s = 20
    evidence_model = CitabilityEvidence

    async def run(self, ctx: AuditContext) -> CheckResult:
        questions = ctx.uncited_prompts or _questions_from_html(ctx.raw_html or "")
        model = make_chat_model(0)
        if model is None:
            return self.finish(
                CheckStatus.SKIPPED,
                CitabilityEvidence(questions=questions, reason="missing_api_key"),
                "Set OPEN_ROUTE_API_KEY to review whether this page answers citation questions.",
            )
        text = (ctx.rendered_text or _visible_text(ctx.raw_html or ""))[:6000]
        try:
            structured = model.with_structured_output(CitabilityReview)
            review = await structured.ainvoke(
                "Review whether this page can be cited for the questions. "
                "Return the structured fields only.\n"
                "Questions:\n- " + "\n- ".join(questions) + "\n\n"
                f"Page text:\n{text}"
            )
        except Exception as exc:
            if _is_rate_limit(exc):
                return self.finish(
                    CheckStatus.SKIPPED,
                    CitabilityEvidence(questions=questions, reason="rate_limited"),
                    "Citability review was skipped because the model rate limit was reached.",
                )
            raise
        if not isinstance(review, CitabilityReview):
            review = CitabilityReview.model_validate(review)
        evidence = CitabilityEvidence(
            questions=questions,
            answerable=review.answerable,
            missing_points=review.missing_points,
        )
        if review.answerable and not review.missing_points:
            return self.finish(CheckStatus.PASS, evidence, "")
        status = CheckStatus.WARN if review.answerable else CheckStatus.FAIL
        hint = (
            review.fix_hint or "Add a direct answer for each question in the main HTML."
        )
        return self.finish(status, evidence, hint)


def _questions_from_html(html: str) -> list[str]:
    soup = BeautifulSoup(html or "", "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(" ", strip=True) if h1_tag else ""
    subject = title or h1 or "this page"
    questions = [f"What is {subject}?", f"Who is {subject} for?"]
    if h1 and h1 != title:
        questions.append(f"What does {h1} explain?")
    return questions


def _visible_text(html: str) -> str:
    return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)


def _is_rate_limit(exc: Exception) -> bool:
    if getattr(exc, "status_code", None) == 429:
        return True
    response = getattr(exc, "response", None)
    if getattr(response, "status_code", None) == 429:
        return True
    return "429" in str(exc)
