from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel

from .context import AuditContext
from .models import CheckResult, CheckStatus


class GeoCheck(ABC):
    id: str
    name: str
    tier: Literal["fast", "deep"]
    timeout_s: float
    evidence_model: type[BaseModel]
    needs_browser: bool = False

    @abstractmethod
    async def run(self, ctx: AuditContext) -> CheckResult: ...

    def finish(
        self, status: CheckStatus, evidence: BaseModel, fix_hint: str
    ) -> CheckResult:
        return CheckResult(
            id=self.id,
            name=self.name,
            tier=self.tier,
            status=status,
            evidence=evidence.model_dump(),
            fix_hint=fix_hint,
        )
