"""
Metric Extractor — parses experience_atoms.md and builds a per-experience metric whitelist.

The whitelist maps experience_id → list of allowed metric tokens (numbers + units).
Any number appearing in a resume bullet that is NOT in the whitelist for that experience
is considered fabricated.
"""
import re
from typing import Dict, List, Set


def extract_metrics(atoms_text: str) -> Dict[str, List[str]]:
    """
    Parse raw experience_atoms text and extract allowed metric tokens per experience.

    Returns: {experience_id: [metric_token, ...]}
    e.g. {"EXP-001": ["30天", "1天"], "EXP-002": ["8%", "5%"], "EXP-003": []}
    """
    result: Dict[str, List[str]] = {}
    current_id: str | None = None

    for line in atoms_text.splitlines():
        # Match experience ID header: ## EXP-001 or ## EXP-001: name
        id_match = re.match(r"^##\s+(EXP-\d+)", line)
        if id_match:
            current_id = id_match.group(1)
            result[current_id] = []
            continue

        # Match metric line
        if current_id is not None and re.match(r"^-\s+metric\s*:", line, re.IGNORECASE):
            metric_value = re.sub(r"^-\s+metric\s*:\s*", "", line, flags=re.IGNORECASE).strip()
            tokens = _extract_tokens(metric_value)
            result[current_id].extend(tokens)

    return result


def _extract_tokens(text: str) -> List[str]:
    """
    Extract numeric metric tokens from a metric string.
    Captures: percentages (8%), numbers with Chinese units (30天), numbers with + (1000+).
    Skips range expressions like "0-1" or "1-3" (used idiomatically, not as real metrics).
    """
    # Remove idiomatic range expressions (e.g. "0-1独立完成", "1-3年经验")
    # before extraction so they don't contribute false tokens.
    cleaned = re.sub(r"\b\d+-\d+\b", "", text)

    # Primary: numbers that have a unit or suffix.
    # Decimal part (?:\.\d+)? handles "2.91%", "4.5分", "31.7万条", "8.5s".
    # Unit list includes "s" for seconds ("8s", "30s").
    #
    # Fallback: bare significant decimals (must have a decimal point).
    # Catches dimensionless ratio metrics like "167.9" (net value per 1K coupons)
    # that appear in metric fields without a recognised unit suffix.
    # Bare *integers* are still excluded — too ambiguous (e.g. "3" from "3个品").
    # Unit-bearing pattern is tried first; bare decimal only fires when it fails.
    pattern = (
        r"\d+(?:\.\d+)?(?:[%+]|[天月年周小时分秒条个万亿ks]+\+?|\+)"
        r"|\d+\.\d+"
    )
    tokens = re.findall(pattern, cleaned)

    # Deduplicate while preserving order
    seen: set = set()
    unique = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique


def allowed_digits(whitelist: Dict[str, List[str]]) -> Dict[str, Set[str]]:
    """
    Convert whitelist to a mapping of experience_id → set of allowed digit sequences.
    Used for fast lookup during bullet validation.

    e.g. {"EXP-001": {"30", "1"}, "EXP-002": {"8", "5"}}
    """
    result: Dict[str, Set[str]] = {}
    for exp_id, tokens in whitelist.items():
        digits: Set[str] = set()
        for token in tokens:
            for d in re.findall(r"\d+", token):
                digits.add(d)
        result[exp_id] = digits
    return result
