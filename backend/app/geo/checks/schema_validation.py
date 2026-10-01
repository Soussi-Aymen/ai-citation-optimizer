import json

from bs4 import BeautifulSoup
from pydantic import BaseModel

from ..base import GeoCheck
from ..context import AuditContext
from ..models import CheckStatus
from ..schema_type import expected_schema_type


class SchemaEvidence(BaseModel):
    blocks: int = 0
    types: list[str] = []
    expected_type: str = ""
    has_expected_type: bool = False
    has_same_as: bool = False
    has_author: bool = False
    has_date_published: bool = False
    has_date_modified: bool = False
    malformed: bool = False


class SchemaValidationCheck(GeoCheck):
    id = "schema_validation"
    name = "JSON-LD validation"
    tier = "fast"
    timeout_s = 2
    evidence_model = SchemaEvidence

    async def run(self, ctx: AuditContext):
        html = ctx.rendered_html or ctx.raw_html or ""
        soup = BeautifulSoup(html, "html.parser")
        scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
        objects: list[dict] = []
        malformed = False
        for script in scripts:
            raw = script.string or script.get_text() or ""
            if not raw.strip():
                malformed = True
                continue
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                malformed = True
                continue
            objects.extend(_flatten(parsed))
        expected = expected_schema_type(ctx.url)
        types = [str(item.get("@type")) for item in objects if item.get("@type")]
        evidence = SchemaEvidence(
            blocks=len(scripts),
            types=types,
            expected_type=expected,
            has_expected_type=expected in types,
            has_same_as=any(item.get("sameAs") for item in objects),
            has_author=any(item.get("author") for item in objects),
            has_date_published=any(item.get("datePublished") for item in objects),
            has_date_modified=any(item.get("dateModified") for item in objects),
            malformed=malformed,
        )
        if malformed or not evidence.has_expected_type:
            status = CheckStatus.FAIL
            hint = (
                f"Add valid JSON-LD with @type {expected}, plus author and "
                "dateModified when the page is an article."
            )
        elif not (
            evidence.has_author and evidence.has_date_modified and evidence.has_same_as
        ):
            status = CheckStatus.WARN
            hint = "Add sameAs, author, datePublished, and dateModified to the JSON-LD."
        else:
            status = CheckStatus.PASS
            hint = "JSON-LD matches the expected page type."
        return self.finish(status, evidence, hint)


def _flatten(parsed) -> list[dict]:
    if isinstance(parsed, list):
        found: list[dict] = []
        for item in parsed:
            found.extend(_flatten(item))
        return found
    if isinstance(parsed, dict):
        graph = parsed.get("@graph")
        if isinstance(graph, list):
            return _flatten(graph)
        return [parsed]
    return []
