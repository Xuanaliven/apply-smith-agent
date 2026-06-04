"""
Experience Atoms Parser — robustly parses experience_atoms.md into structured dicts.

Format expected:
    ## EXP-001
    - field_name: value
    - another_field: value
    ...

    ## EXP-002
    ...
"""
import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)

STANDARD_FIELDS = frozenset({
    "experience_name",
    "type",
    "time_period",
    "raw_fact",
    "role",
    "action",
    "tool",
    "metric",
    "evidence",
    "can_be_reused_for",
    "risk_level",
})


def parse_atoms(text: str) -> List[Dict[str, str]]:
    """
    Parse experience_atoms.md text into a list of dicts.

    Each dict contains:
      - "id": the EXP-NNN identifier
      - one key per STANDARD_FIELDS entry (missing fields default to "")

    Unknown fields log a warning but do not crash.
    Empty input returns [].
    """
    if not text or not text.strip():
        return []

    results: List[Dict[str, str]] = []

    # Split on "## EXP-..." headers (capture the ID in the first group)
    parts = re.split(r"(?m)^##\s+(EXP-\S+)", text)

    # parts = [prefix_text, exp_id_1, block_1, exp_id_2, block_2, ...]
    # Skip index 0 (text before the first header)
    i = 1
    while i < len(parts) - 1:
        exp_id = parts[i].strip()
        block = parts[i + 1]
        results.append(_parse_block(exp_id, block))
        i += 2

    return results


def _parse_block(exp_id: str, block: str) -> Dict[str, str]:
    """Parse a single experience block into a dict."""
    atom: Dict[str, str] = {"id": exp_id}

    # Pre-populate all standard fields with empty string defaults
    for field in STANDARD_FIELDS:
        atom[field] = ""

    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue

        # Match "- field_name: value" (allow optional whitespace around colon)
        match = re.match(r"^-\s+([\w][\w\s-]*?)\s*:\s*(.*)", line)
        if not match:
            continue

        raw_name = match.group(1).strip()
        value = match.group(2).strip()

        # Normalize field name: lowercase, spaces/hyphens → underscores
        field_name = re.sub(r"[\s\-]+", "_", raw_name).lower()

        if field_name in STANDARD_FIELDS:
            atom[field_name] = value
        else:
            logger.warning(
                "atom_parser: unrecognized field %r in block %s — skipping",
                field_name,
                exp_id,
            )

    return atom
