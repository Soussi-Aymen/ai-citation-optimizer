TEXT_DELTA_CRITICAL = 2000
TEXT_DELTA_MODERATE = 500


def js_dependency(raw_text_length: int, rendered_text_length: int) -> dict:
    """Char delta and js_impact used by the Playwright audit and bot_view_diff."""
    text_delta = rendered_text_length - raw_text_length
    if text_delta > TEXT_DELTA_CRITICAL:
        impact = "CRITICAL"
    elif text_delta > TEXT_DELTA_MODERATE:
        impact = "MODERATE"
    else:
        impact = "LOW"
    return {
        "raw_text_length": raw_text_length,
        "text_delta": text_delta,
        "js_impact": impact,
    }
