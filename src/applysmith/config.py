"""
ApplySmith configuration — loads from .env file and environment variables.
"""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (cwd when the CLI is invoked).
# silent=True so missing .env is not an error.
load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)


@dataclass
class Config:
    model: str
    api_key: str | None
    api_base: str | None
    language: str  # "en" or "zh"


def get_config() -> Config:
    return Config(
        model=os.environ.get("APPLYSMITH_MODEL", "deepseek/deepseek-chat"),
        api_key=os.environ.get("APPLYSMITH_API_KEY"),
        api_base=os.environ.get("APPLYSMITH_API_BASE") or None,
        language=os.environ.get("APPLYSMITH_LANGUAGE", "en"),
    )
