import asyncio
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel

from ..base import GeoCheck
from ..config import (
    AI_BOT_USER_AGENTS,
    BASELINE_USER_AGENT,
    BOT_BODY_RATIO_FAIL,
    CHALLENGE_MARKERS,
)
from ..context import AuditContext
from ..models import CheckStatus

FETCH_TIMEOUT_S = 5.0


class AiBotEvidence(BaseModel):
    blocked_agents: list[str] = []
    challenged_agents: list[str] = []
    thin_agents: list[str] = []
    robots_blocked: list[str] = []
    x_robots_tag: str = ""
    meta_robots: str = ""


class AiBotAccessCheck(GeoCheck):
    id = "ai_bot_access"
    name = "AI bot access"
    tier = "fast"
    timeout_s = 8
    evidence_model = AiBotEvidence

    async def run(self, ctx: AuditContext):
        fetches = await self._fetch_all(ctx.url)
        baseline = fetches.get("baseline")
        evidence = AiBotEvidence()
        if baseline is None or baseline["status"] is None:
            return self.finish(
                CheckStatus.SKIPPED,
                evidence,
                "Could not fetch a baseline copy of the page.",
            )
        for name, item in fetches.items():
            if name == "baseline":
                continue
            status = item["status"]
            body = item["body"] or ""
            if status in (403, 429) or status is None:
                evidence.blocked_agents.append(name)
            elif _looks_like_challenge(body):
                evidence.challenged_agents.append(name)
            elif (
                baseline["length"]
                and item["length"] / baseline["length"] < BOT_BODY_RATIO_FAIL
            ):
                evidence.thin_agents.append(name)
        robots = await ctx.robots_txt()
        path = urlparse(ctx.final_url or ctx.url).path or "/"
        if robots:
            for name in AI_BOT_USER_AGENTS:
                if not _robots_allows(robots, name, path):
                    evidence.robots_blocked.append(name)
        evidence.x_robots_tag = ctx.headers.get("x-robots-tag", "")
        evidence.meta_robots = _meta_robots(ctx.raw_html)
        noindex = (
            "noindex" in evidence.x_robots_tag.lower()
            or "noindex" in evidence.meta_robots
        )
        blocked = evidence.blocked_agents or evidence.robots_blocked or noindex
        challenged = evidence.challenged_agents or evidence.thin_agents
        if blocked:
            status = CheckStatus.FAIL
            hint = (
                "Allow the listed AI crawlers in robots.txt and the server, "
                "and remove noindex from this URL."
            )
        elif challenged:
            status = CheckStatus.WARN
            hint = (
                "Serve the same HTML to AI crawlers that a browser receives, "
                "without interstitial challenge pages."
            )
        else:
            status = CheckStatus.PASS
            hint = "AI crawlers can fetch this URL."
        return self.finish(status, evidence, hint)

    async def _fetch_all(self, url: str) -> dict[str, dict]:
        agents = {"baseline": BASELINE_USER_AGENT, **AI_BOT_USER_AGENTS}

        async def one(name: str, ua: str) -> tuple[str, dict]:
            try:
                async with httpx.AsyncClient(
                    timeout=FETCH_TIMEOUT_S, follow_redirects=True
                ) as client:
                    response = await client.get(url, headers={"User-Agent": ua})
                return name, {
                    "status": response.status_code,
                    "body": response.text,
                    "length": len(response.text),
                }
            except Exception:
                return name, {"status": None, "body": "", "length": 0}

        pairs = await asyncio.gather(*(one(name, ua) for name, ua in agents.items()))
        return dict(pairs)


def _looks_like_challenge(body: str) -> bool:
    lowered = body.lower()
    return any(marker in lowered for marker in CHALLENGE_MARKERS)


def _meta_robots(html: str) -> str:
    lowered = html.lower()
    marker = 'name="robots"'
    idx = lowered.find(marker)
    if idx == -1:
        return ""
    snippet = html[idx : idx + 200]
    content = snippet.lower().split('content="', 1)
    if len(content) < 2:
        return ""
    return content[1].split('"', 1)[0]


def _robots_allows(robots_txt: str, agent: str, path: str) -> bool:
    groups = _robot_groups(robots_txt)
    rules = groups.get(agent.lower()) or groups.get("*") or []
    allowed = True
    matched_len = -1
    for directive, rule_path in rules:
        if path.startswith(rule_path) and len(rule_path) > matched_len:
            matched_len = len(rule_path)
            allowed = directive == "allow"
    return allowed


def _robot_groups(robots_txt: str) -> dict[str, list[tuple[str, str]]]:
    groups: dict[str, list[tuple[str, str]]] = {}
    current: list[str] = []
    for raw in robots_txt.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = [part.strip() for part in line.split(":", 1)]
        if key.lower() == "user-agent":
            current = [value.lower()]
            groups.setdefault(value.lower(), [])
        elif key.lower() in ("allow", "disallow") and current:
            for agent in current:
                groups.setdefault(agent, []).append((key.lower(), value or "/"))
    return groups
