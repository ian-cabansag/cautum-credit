"""Configuration. Never logs or exposes API keys."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


# Required by MGT 409: find .env in repository FIRST, then one folder above.
def load_settings_env(root):
    for candidate in (root / ".env", root.parent / ".env"):
        if candidate.is_file():
            load_dotenv(candidate, override=False)
            return candidate
    return None


load_settings_env(ROOT)

MAX_UPLOAD_BYTES = 2_000_000
MAX_ROWS = 2500
try:
    MAX_AI_CALLS = int(os.getenv("MAX_AI_CALLS", "25"))
    if not 0 <= MAX_AI_CALLS <= 500:
        raise ValueError()
except ValueError:
    raise ValueError("MAX_AI_CALLS must be an integer from 0 to 500.") from None


def provider() -> tuple[str, str, str] | None:
    if os.getenv("PORTKEY_API_KEY"):
        return (
            "portkey",
            os.environ["PORTKEY_API_KEY"],
            os.getenv("PORTKEY_MODEL", "gpt-6-luna"),
        )
    if os.getenv("OPENAI_API_KEY"):
        return (
            "openai",
            os.environ["OPENAI_API_KEY"],
            os.getenv("OPENAI_MODEL", "gpt-6-astra"),
        )
    return None
