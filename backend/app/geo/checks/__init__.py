"""Fast-tier GEO checks."""

from .ai_bot_access import AiBotAccessCheck
from .answer_readiness import AnswerReadinessCheck
from .bot_view_diff import BotViewDiffCheck
from .canonical_and_redirects import CanonicalAndRedirectsCheck
from .freshness_consistency import FreshnessConsistencyCheck
from .llm_citability_review import LlmCitabilityReviewCheck
from .orphan_page_check import OrphanPageCheck
from .schema_validation import SchemaValidationCheck

FAST_CHECKS = [
    AiBotAccessCheck(),
    BotViewDiffCheck(),
    AnswerReadinessCheck(),
    SchemaValidationCheck(),
    FreshnessConsistencyCheck(),
    CanonicalAndRedirectsCheck(),
]

DEEP_CHECKS = [
    OrphanPageCheck(),
    LlmCitabilityReviewCheck(),
]
