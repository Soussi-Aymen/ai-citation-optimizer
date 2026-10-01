import asyncio

from .base import GeoCheck
from .catalog import CHECKS
from .context import AuditContext
from .models import CheckResult, CheckStatus


def _failed(check: GeoCheck, status: CheckStatus, reason: str) -> CheckResult:
    return CheckResult(
        id=check.id,
        name=check.name,
        tier=check.tier,
        status=status,
        evidence={"reason": reason},
        fix_hint="",
    )


async def run_check(check: GeoCheck, ctx: AuditContext) -> CheckResult:
    try:
        return await asyncio.wait_for(check.run(ctx), timeout=check.timeout_s)
    except (TimeoutError, asyncio.TimeoutError):
        return _failed(check, CheckStatus.SKIPPED, "timeout")
    except Exception as exc:
        return _failed(check, CheckStatus.ERROR, str(exc))


async def run_checks(checks: list[GeoCheck], ctx: AuditContext) -> list[CheckResult]:
    if not checks:
        return []
    return list(await asyncio.gather(*(run_check(check, ctx) for check in checks)))


def checks_for_tier(tier: str) -> list[GeoCheck]:
    return [check for check in CHECKS if check.tier == tier]


async def run_tier(ctx: AuditContext, tier: str) -> list[CheckResult]:
    return await run_checks(checks_for_tier(tier), ctx)
