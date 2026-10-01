import asyncio
from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel

from .catalog import CHECKS
from .context import AuditContext
from .models import CheckResult, CheckStatus


class GeoCheck(ABC):
    id: str
    name: str
    tier: Literal["fast", "deep"]
    timeout_s: float
    evidence_model: type[BaseModel]

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


def _failed(check: GeoCheck, status: CheckStatus, reason: str) -> CheckResult:
    return CheckResult(
        id=check.id,
        name=check.name,
        tier=check.tier,
        status=status,
        evidence={"reason": reason},
        fix_hint="",
    )


async def run_checks(checks: list[GeoCheck], ctx: AuditContext) -> list[CheckResult]:
    async def one(check: GeoCheck) -> CheckResult:
        try:
            return await asyncio.wait_for(check.run(ctx), timeout=check.timeout_s)
        except (TimeoutError, asyncio.TimeoutError):
            return _failed(check, CheckStatus.SKIPPED, "timeout")
        except Exception as exc:
            return _failed(check, CheckStatus.ERROR, str(exc))

    if not checks:
        return []
    return list(await asyncio.gather(*(one(check) for check in checks)))


def checks_for_tier(tier: str) -> list[GeoCheck]:
    return [check for check in CHECKS if check.tier == tier]


async def run_tier(ctx: AuditContext, tier: str) -> list[CheckResult]:
    return await run_checks(checks_for_tier(tier), ctx)
