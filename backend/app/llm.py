"""OpenRouter chat models. Missing key returns None so callers can skip."""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
CHAT_MODEL = "google/gemma-4-26b-a4b-it:free"


def make_chat_model(temperature: float) -> ChatOpenAI | None:
    api_key = os.getenv("OPEN_ROUTE_API_KEY")
    if not api_key:
        return None
    return ChatOpenAI(
        model=CHAT_MODEL,
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
        temperature=temperature,
    )
