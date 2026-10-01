"""Structured citability review. One retry on 429 or a transient network error."""

import asyncio
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from ...llm import make_chat_model
from ..base import GeoCheck
from ..context import AuditContext
from ..models import CheckResult, CheckStatus

# Leave at least this long for the second model call after Retry-After.
_MIN_RETRY_BUDGET_S = 1.0
_RATE_LIMIT_REASON = "model rate limited, retry later"
_MISSING_KEY_REASON = "API key not configured"
_NETWORK_REASON = "temporary network error, retry later"
_TRANSIENT_ERRORS = {
    "APIConnectionError",
    "APITimeoutError",
    "ConnectError",
    "NetworkError",
    "TimeoutException",
}


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
        started = time.monotonic()
        model = make_chat_model(0)
        if model is None:
            return self._skipped(questions, _MISSING_KEY_REASON)
        text = (ctx.rendered_text or _visible_text(ctx.raw_html or ""))[:6000]
        prompt = (
            "Review whether this page can be cited for the questions. "
            "Return the structured fields only.\n"
            "Questions:\n- " + "\n- ".join(questions) + "\n\n"
            f"Page text:\n{text}"
        )
        structured = model.with_structured_output(CitabilityReview)
        review = None
        for attempt in range(2):
            try:
                review = await structured.ainvoke(prompt)
                break
            except Exception as exc:
                retryable = _is_rate_limit(exc) or _is_transient(exc)
                if not retryable:
                    raise
                if attempt == 1 or not _retry_fits(exc, started, self.timeout_s):
                    reason = (
                        _RATE_LIMIT_REASON if _is_rate_limit(exc) else _NETWORK_REASON
                    )
                    return self._skipped(questions, reason)
                await asyncio.sleep(_retry_after_seconds(exc))
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

    def _skipped(self, questions: list[str], reason: str) -> CheckResult:
        hint = (
            "Set OPEN_ROUTE_API_KEY to review whether this page answers citation questions."
            if reason == _MISSING_KEY_REASON
            else "Citability review was skipped. Retry this audit in a moment."
        )
        return self.finish(
            CheckStatus.SKIPPED,
            CitabilityEvidence(questions=questions, reason=reason),
            hint,
        )


def _retry_fits(exc: Exception, started: float, timeout_s: float) -> bool:
    delay = _retry_after_seconds(exc)
    remaining = timeout_s - (time.monotonic() - started)
    return remaining >= delay + _MIN_RETRY_BUDGET_S


def _retry_after_seconds(exc: Exception) -> float:
    raw = _header(exc, "retry-after")
    if raw is None:
        return 0.0
    try:
        return max(0.0, float(raw))
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return 0.0
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())


def _header(exc: Exception, name: str) -> str | None:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None) or getattr(exc, "headers", None)
    if headers is None:
        return None
    value = headers.get(name) or headers.get(name.title())
    if value is None:
        return None
    return str(value)


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


def _is_transient(exc: Exception) -> bool:
    return type(exc).__name__ in _TRANSIENT_ERRORS or any(
        type(item).__name__ in _TRANSIENT_ERRORS for item in _causes(exc)
    )


def _causes(exc: Exception):
    current = exc
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        current = current.__cause__ or current.__context__
        if current is not None:
            yield current
