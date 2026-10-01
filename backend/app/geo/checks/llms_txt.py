"""llms.txt as a fast GEO check. The probe starts when the audit context opens."""

from pydantic import BaseModel

from ..base import GeoCheck
from ..context import AuditContext
from ..models import CheckStatus


class LlmsTxtEvidence(BaseModel):
    has_llms_txt: bool = False
    llms_txt_valid: bool = False
    llms_txt_lists_page: bool = False
    llms_txt_link_count: int = 0
    llms_txt_url: str | None = None


class LlmsTxtCheck(GeoCheck):
    id = "llms_txt"
    name = "llms.txt"
    tier = "fast"
    timeout_s = 10
    evidence_model = LlmsTxtEvidence

    async def run(self, ctx: AuditContext):
        signals = await ctx.llms_txt()
        evidence = LlmsTxtEvidence.model_validate(signals)
        if not evidence.has_llms_txt:
            return self.finish(
                CheckStatus.FAIL,
                evidence,
                "Publish an /llms.txt file that lists this page.",
            )
        if not evidence.llms_txt_lists_page:
            return self.finish(
                CheckStatus.WARN,
                evidence,
                "Add this page to the site's /llms.txt link list.",
            )
        return self.finish(CheckStatus.PASS, evidence, "")
