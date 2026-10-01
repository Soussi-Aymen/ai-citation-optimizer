"""Registered GEO checks."""

from .checks import DEEP_CHECKS, FAST_CHECKS

CHECKS: list = list(FAST_CHECKS) + list(DEEP_CHECKS)
