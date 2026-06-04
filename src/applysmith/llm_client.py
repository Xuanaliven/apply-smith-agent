"""
LLM client for ApplySmith — provider-agnostic via litellm.
"""
import json
import logging
import time
from typing import Callable, Optional, Type, TypeVar

import litellm

from .config import get_config

T = TypeVar("T")
logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_BACKOFF_DELAYS = (1, 3, 9)  # seconds before each retry attempt


def _is_retryable(exc: BaseException) -> bool:
    """Return True if the exception warrants a retry (timeout or 5xx)."""
    retryable = []
    for name in ("Timeout", "ServiceUnavailableError", "APIConnectionError", "InternalServerError"):
        cls = getattr(litellm.exceptions, name, None)
        if cls is not None:
            retryable.append(cls)
    return bool(retryable) and isinstance(exc, tuple(retryable))


def _repair_inner_quotes(s: str) -> str:
    """
    Walk through the JSON text and replace unescaped inner quotes in string values
    with single quotes.

    Heuristic: a quote is the "closing" quote of a JSON string when the next
    non-space character after it is a JSON structural token (:, ,, }, ], newline).
    Any other unescaped quote inside a string value is treated as an inner quote
    and replaced with a single quote character.
    """
    result = []
    i = 0
    n = len(s)

    while i < n:
        if s[i] != '"':
            result.append(s[i])
            i += 1
            continue

        # Start of a JSON string — scan for its real closing quote
        result.append('"')
        j = i + 1
        while j < n:
            ch = s[j]
            if ch == '\\' and j + 1 < n:
                # Properly escaped character — keep both chars
                result.append(ch)
                result.append(s[j + 1])
                j += 2
            elif ch == '"':
                # Peek past whitespace to find the next structural token
                k = j + 1
                while k < n and s[k] in ' \t':
                    k += 1
                if k >= n or s[k] in ':,}]\n\r':
                    # Structural token follows → this is the real closing quote
                    result.append('"')
                    j += 1
                    break
                else:
                    # Unescaped inner quote → replace with single quote
                    result.append("'")
                    j += 1
            else:
                result.append(ch)
                j += 1
        i = j

    return ''.join(result)


def _extract_json_str(raw: str) -> str:
    """Strip markdown code fences, normalize punctuation, and repair common JSON errors."""
    cleaned = raw.strip()

    # 1. Strip markdown code fences
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = (
            "\n".join(lines[1:-1]) if lines[-1].strip() == "```"
            else "\n".join(lines[1:])
        )

    # 2. Normalize Chinese / curly punctuation to ASCII equivalents
    cleaned = (
        cleaned
        .replace("，", ",")
        .replace("。", ".")
        .replace("\u201c", '"')   # " left double quotation mark
        .replace("\u201d", '"')   # " right double quotation mark
        .replace("\u2018", "'")   # ' left single quotation mark
        .replace("\u2019", "'")   # ' right single quotation mark
    )

    # 3. If already valid JSON, return as-is
    try:
        json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError:
        pass

    # 4. Attempt to repair unescaped inner quotes
    repaired = _repair_inner_quotes(cleaned)
    try:
        json.loads(repaired)
        logger.debug("JSON auto-repair: replaced unescaped inner quotes in LLM response")
        return repaired
    except json.JSONDecodeError:
        pass

    # 5. Return cleaned text so the caller raises a clear error with context
    return cleaned


def call_llm(system: str, user: str) -> str:
    """
    Call the configured LLM. Retries up to _MAX_RETRIES times with exponential
    backoff (1s, 3s, 9s) on timeout or 5xx errors.
    Raises ValueError for empty responses.
    """
    config = get_config()

    if not config.api_key:
        raise ValueError(
            "APPLYSMITH_API_KEY is not set. "
            "Copy .env.example to .env and add your API key."
        )

    kwargs = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "api_key": config.api_key,
    }
    if config.api_base:
        kwargs["api_base"] = config.api_base

    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = litellm.completion(**kwargs)
            content = response.choices[0].message.content
            if not content or not content.strip():
                raise ValueError("LLM returned an empty response.")
            return content
        except ValueError:
            raise
        except Exception as exc:
            if _is_retryable(exc) and attempt < _MAX_RETRIES:
                delay = _BACKOFF_DELAYS[attempt]
                logger.warning(
                    "LLM call failed (attempt %d/%d), retrying in %ds: %s",
                    attempt + 1, _MAX_RETRIES + 1, delay, exc,
                )
                time.sleep(delay)
            else:
                raise

    raise RuntimeError("Unreachable")  # pragma: no cover


def call_llm_json(
    system: str,
    user: str,
    model_class: Type[T],
    transform: Optional[Callable[[dict], dict]] = None,
) -> T:
    """
    Call LLM, parse JSON response, validate against a Pydantic model class.

    Args:
        system: System prompt.
        user: User message.
        model_class: Pydantic model class to validate against.
        transform: Optional dict→dict function applied before Pydantic validation.
                   Use this to fix field-name typos or rename keys before validation.

    Returns:
        Validated model instance.

    Raises:
        ValueError: on empty response, invalid JSON, or failed Pydantic validation.
    """
    raw = call_llm(system, user)
    cleaned = _extract_json_str(raw)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned invalid JSON.\n"
            f"Parse error: {exc}\n"
            f"Raw response:\n{raw}"
        ) from exc

    if transform is not None:
        data = transform(data)

    try:
        return model_class(**data)
    except Exception as exc:
        raise ValueError(
            f"LLM response failed Pydantic validation ({model_class.__name__}).\n"
            f"Error: {exc}\n"
            f"Data: {json.dumps(data, ensure_ascii=False, indent=2)}"
        ) from exc
