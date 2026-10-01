"""Pull uncited prompt strings from a Peec report when that shape is present."""


def extract_uncited_prompts(report: object) -> list[str] | None:
    if not isinstance(report, dict):
        return None
    found: list[str] = []
    data = report.get("data", report)
    items = data if isinstance(data, list) else [data]
    for item in items:
        if not isinstance(item, dict):
            continue
        found.extend(_from_item(item))
    unique = list(dict.fromkeys(text for text in found if text))
    return unique or None


def _from_item(item: dict) -> list[str]:
    found: list[str] = []
    prompts = (
        item.get("uncited_prompts") or item.get("prompts") or item.get("questions")
    )
    if isinstance(prompts, list):
        for prompt in prompts:
            if isinstance(prompt, str) and prompt.strip():
                found.append(prompt.strip())
            elif isinstance(prompt, dict):
                text = (
                    prompt.get("text") or prompt.get("prompt") or prompt.get("question")
                )
                if text and prompt.get("cited") is False:
                    found.append(str(text).strip())
    text = item.get("prompt") or item.get("question")
    if text and item.get("cited") is False:
        found.append(str(text).strip())
    return found
