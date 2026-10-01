"""Named thresholds and bot identities for GEO checks."""

AI_BOT_USER_AGENTS: dict[str, str] = {
    "GPTBot": (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; "
        "GPTBot/1.2; +https://openai.com/gptbot"
    ),
    "OAI-SearchBot": (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; "
        "OAI-SearchBot/1.0; +https://openai.com/searchbot"
    ),
    "PerplexityBot": (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; "
        "PerplexityBot/1.0; +https://perplexity.ai/perplexitybot"
    ),
    "ClaudeBot": (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; "
        "ClaudeBot/1.0; +https://www.anthropic.com"
    ),
    "Google-Extended": (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; "
        "Google-Extended"
    ),
}

BASELINE_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

MOBILE_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
)

# Mobile main text divided by desktop main text.
MOBILE_MAIN_TEXT_RATIO_WARN = 0.8
MOBILE_MAIN_TEXT_RATIO_FAIL = 0.5

# Bot HTML shorter than this fraction of the baseline body is a content gap.
BOT_BODY_RATIO_FAIL = 0.5
CHALLENGE_MARKERS = ("just a moment", "cf-challenge", "captcha", "access denied")

# Answer readiness
QUESTION_HEADING_MIN_SHARE = 0.2
DIRECT_ANSWER_WINDOW_MIN_WORDS = 100
DIRECT_ANSWER_WINDOW_MAX_WORDS = 150
MIN_MAIN_WORDS = 80

# Freshness: dateModified or lastmod older than this many days is stale.
STALE_AFTER_DAYS = 180
# Dates that disagree by more than this many days are contradictory.
DATE_CONFLICT_DAYS = 7

# Canonical and redirects
REDIRECT_CHAIN_WARN = 2
REDIRECT_CHAIN_FAIL = 4

# Orphan crawl bounds (deep tier)
MAX_CRAWL_PAGES = 25
MAX_CRAWL_SECONDS = 10
MAX_DEPTH = 2
