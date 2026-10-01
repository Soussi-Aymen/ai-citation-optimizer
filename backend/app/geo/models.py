from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class CheckStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    SKIPPED = "skipped"
    ERROR = "error"


class CheckResult(BaseModel):
    id: str
    name: str
    tier: Literal["fast", "deep"]
    status: CheckStatus
    evidence: dict[str, Any] = Field(default_factory=dict)
    fix_hint: str = ""
