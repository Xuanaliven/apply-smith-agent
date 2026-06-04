"""
Resume Generator — writes tailored resume bullets from selected experiences.

Architectural safeguards against metric fabrication (applied in order):
  1. Before calling LLM: inject per-experience metric whitelist into the prompt so the
     model knows exactly which numbers it is allowed to use.
  2. After LLM returns — Pass 1 (_validate_bullets): strip any number not present in the
     whitelist for that experience; override claim_level to Red.
  3. After LLM returns — Pass 2 (_validate_metric_sources): require every number in a
     bullet to be traceable to a verbatim metric_source phrase from experience_atoms.
     Mismatches are stripped and flagged Red.
"""
import logging
import re
from typing import Dict, List, Optional, Set

from .llm_client import call_llm_json
from .metric_extractor import allowed_digits
from .models import ExperienceSelectionResult, IdealCandidate, ResumeBullet, TailoredResume
from .prompts.resume_gen import RESUME_GEN_SYSTEM

logger = logging.getLogger(__name__)


def _build_whitelist_block(
    selection: ExperienceSelectionResult,
    metric_whitelist: Dict[str, List[str]],
) -> str:
    """Build the whitelist section injected into the user prompt."""
    lines = ["## Metric Whitelist (ONLY these numbers are allowed per experience)"]
    for exp in selection.included:
        tokens = metric_whitelist.get(exp.experience_id, [])
        if tokens:
            lines.append(f"- {exp.experience_id} ({exp.experience_name}): {', '.join(tokens)}")
        else:
            lines.append(f"- {exp.experience_id} ({exp.experience_name}): none — write bullet without numbers")
    return "\n".join(lines)


def _validate_bullets(
    bullets: List[ResumeBullet],
    name_to_id: Dict[str, str],
    digit_whitelist: Dict[str, Set[str]],
) -> List[ResumeBullet]:
    """
    Post-generation validator. For each bullet:
    - Find its experience_id via name_to_id mapping.
    - Extract all digit sequences from bullet_text.
    - Any digit NOT in the whitelist for that experience → strip it and flag Red.
    Returns a new list (original objects are not mutated).
    """
    validated = []
    for b in bullets:
        exp_id = name_to_id.get(b.experience_name)
        if exp_id is None:
            validated.append(b)
            continue

        allowed = digit_whitelist.get(exp_id, set())
        nums_in_bullet = re.findall(r"\d+", b.bullet_text)
        fabricated = [n for n in nums_in_bullet if n not in allowed]

        if not fabricated:
            validated.append(b)
            continue

        # Strip fabricated numbers from bullet_text
        cleaned_text = b.bullet_text
        for num in fabricated:
            # Match the digit possibly followed by unit chars or % or +
            cleaned_text = re.sub(
                rf"(?<!\d){re.escape(num)}(?:[%+天月年周小时分秒条个万亿k]+\+?|\+)?(?!\d)",
                "[X]",
                cleaned_text,
            )

        validated.append(
            ResumeBullet(
                experience_name=b.experience_name,
                bullet_text=cleaned_text,
                claim_level="Red",
                evidence=b.evidence,
                interview_risk=f"[FABRICATED METRIC DETECTED — original number(s) stripped: "
                               f"{', '.join(fabricated)}] {b.interview_risk}",
                recommended_action=b.recommended_action,
            )
        )
    return validated


_NUM_PATTERN = re.compile(r"\d+\.?\d*")

# Unit suffixes stripped when matching fabricated numbers in bullet text
_UNIT_SUFFIX = r"(?:[%+天月年周小时分秒条个万亿k]+\+?|\+)?"


def _validate_metric_sources(
    bullets: List[ResumeBullet],
    atoms_raw: Optional[str] = None,
) -> List[ResumeBullet]:
    """
    Pass 2 validator: ensure every number in bullet_text has a verbatim metric_source.

    Rules:
      - If bullet has numbers but metric_source is empty → Red, strip numbers.
      - If metric_source provided but a number in bullet_text is absent from
        metric_source → Red, strip that number.
      - If atoms_raw provided and metric_source is not a substring of atoms_raw
        (whitespace-normalised, case-insensitive) → Red, strip all numbers.
    """
    _atoms_normalised = (
        re.sub(r"\s+", " ", atoms_raw).lower() if atoms_raw else None
    )

    def _strip_all_nums(text: str) -> str:
        return re.sub(r"\d+\.?\d*" + _UNIT_SUFFIX, "[X]", text)

    def _strip_num(text: str, num: str) -> str:
        return re.sub(
            rf"(?<!\d){re.escape(num)}{_UNIT_SUFFIX}(?!\d)",
            "[X]",
            text,
        )

    def _flag(b: ResumeBullet, cleaned_text: str, risk_prefix: str) -> ResumeBullet:
        return ResumeBullet(
            experience_name=b.experience_name,
            bullet_text=cleaned_text,
            claim_level="Red",
            evidence=b.evidence,
            interview_risk=risk_prefix + b.interview_risk,
            recommended_action="Verify metric source or remove number from bullet",
            metric_source=b.metric_source,
        )

    validated = []
    for b in bullets:
        nums = _NUM_PATTERN.findall(b.bullet_text)

        if not nums:
            validated.append(b)
            continue

        # Rule 1: numbers present but no metric_source
        if not b.metric_source:
            logger.debug(
                "metric_source missing for bullet with numbers — flagging Red: %r",
                b.bullet_text[:80],
            )
            validated.append(_flag(
                b,
                _strip_all_nums(b.bullet_text),
                "[METRIC SOURCE MISSING — no verbatim attribution provided] ",
            ))
            continue

        # Rule 2b: metric_source not found verbatim in atoms_raw
        if _atoms_normalised is not None:
            normalised_src = re.sub(r"\s+", " ", b.metric_source).strip().lower()
            if normalised_src and normalised_src not in _atoms_normalised:
                logger.debug(
                    "metric_source not found verbatim in atoms — flagging Red: %r",
                    b.metric_source[:80],
                )
                validated.append(_flag(
                    b,
                    _strip_all_nums(b.bullet_text),
                    "[METRIC SOURCE NOT FOUND IN ATOMS — not verbatim] ",
                ))
                continue

        # Rule 2a: each number in bullet_text must appear in metric_source
        # Compare against numbers extracted from metric_source (not substring),
        # so "2" does not falsely match inside "1.2%".
        source_nums = set(_NUM_PATTERN.findall(b.metric_source))
        bad_nums = [n for n in nums if n not in source_nums]
        if bad_nums:
            logger.debug(
                "Numbers %s in bullet not in metric_source — flagging Red: %r",
                bad_nums,
                b.bullet_text[:80],
            )
            cleaned = b.bullet_text
            for num in bad_nums:
                cleaned = _strip_num(cleaned, num)
            validated.append(_flag(
                b,
                cleaned,
                f"[METRIC MISMATCH — {', '.join(bad_nums)} in bullet absent from metric_source] ",
            ))
            continue

        validated.append(b)

    return validated


def generate_resume(
    selection: ExperienceSelectionResult,
    ideal: IdealCandidate,
    target_role: str,
    target_company: str,
    language: str = "en",
    metric_whitelist: Optional[Dict[str, List[str]]] = None,
    atoms_raw: Optional[str] = None,
) -> TailoredResume:
    """Generate tailored resume bullets from selected experiences."""
    if language == "zh":
        system = (
            RESUME_GEN_SYSTEM
            + "\nWrite all values in Simplified Chinese (简体中文), "
            "but keep bullet_text in English (resume bullets must stay in English). "
            "Keep technical terms, skill names, tool names, and proper nouns in English."
        )
    else:
        system = RESUME_GEN_SYSTEM

    # Build name→id mapping for validation
    name_to_id = {exp.experience_name: exp.experience_id for exp in selection.included}

    # Inject whitelist if provided
    whitelist_block = ""
    if metric_whitelist is not None:
        whitelist_block = "\n\n" + _build_whitelist_block(selection, metric_whitelist)

    user = (
        f"Target role: {target_role}\nTarget company: {target_company}\n\n"
        "## Ideal Candidate\n" + ideal.model_dump_json(indent=2)
        + "\n\n## Selected Experiences\n" + selection.model_dump_json(indent=2)
        + whitelist_block
    )

    def _fix_packing_notes(data: dict) -> dict:
        """Tolerate 'packing_notes' typo from LLM."""
        if "packing_notes" in data and "packaging_notes" not in data:
            data["packaging_notes"] = data.pop("packing_notes")
        return data

    resume = call_llm_json(system, user, TailoredResume, transform=_fix_packing_notes)

    # Post-generation validation — only when metric constraints are active
    if metric_whitelist is not None or atoms_raw is not None:
        bullets = resume.bullets

        # Pass 1: whitelist digit check
        if metric_whitelist is not None:
            digit_wl = allowed_digits(metric_whitelist)
            bullets = _validate_bullets(bullets, name_to_id, digit_wl)

        # Pass 2: verbatim source attribution check
        bullets = _validate_metric_sources(bullets, atoms_raw)

        resume = TailoredResume(
            target_role=resume.target_role,
            target_company=resume.target_company,
            summary_statement=resume.summary_statement,
            bullets=bullets,
            packaging_notes=resume.packaging_notes,
        )

    return resume
