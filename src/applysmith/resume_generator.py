"""
Resume Generator — writes tailored resume bullets from selected experiences.

Architectural safeguards against metric fabrication (applied in order):
  1. Before calling LLM: inject per-experience metric whitelist AND raw atoms
     text into the prompt so the model knows exactly which numbers and contexts
     it is allowed to use.
  2. After LLM returns — Pass 1 (_validate_bullets): strip any number not present in the
     whitelist for that experience; override claim_level to Red.
  3. After LLM returns — Pass 2 (validate_metric_sources): structural validation:
       Step 1  Numbers in bullet_text must appear in metric_source (set comparison).
       Step 2  Numbers in metric_source must appear in atoms_raw.
               Catches 91% invented from 2.91%, or "2%" vs real "1.2%".
       Step 3  Context anchor: for each number in metric_source the surrounding
               keywords (3-4 char CJK n-grams; 3+ char English words) must overlap
               with the context around that same number in atoms_raw.  Allows
               legitimate paraphrasing while blocking context-swapped metrics.
"""
import logging
import re
from typing import Dict, List, Optional, Set

from .llm_client import call_llm_json
from .metric_extractor import allowed_digits
from .metric_validator import _NUM_PATTERN, _UNIT_SUFFIX, validate_metric_sources
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


def _extract_atoms_for_experiences(atoms_raw: str, experience_ids: List[str]) -> str:
    """Extract only the EXP-XXX sections matching experience_ids from atoms_raw."""
    sections = re.split(r"(?=^## EXP-)", atoms_raw, flags=re.MULTILINE)
    matched = []
    for section in sections:
        for exp_id in experience_ids:
            if section.startswith(f"## {exp_id}"):
                matched.append(section.strip())
                break
    return "\n\n".join(matched)


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

    # Inject raw atoms for the selected experiences so the LLM can quote them accurately
    atoms_block = ""
    if atoms_raw is not None:
        exp_ids = [exp.experience_id for exp in selection.included]
        atoms_excerpt = _extract_atoms_for_experiences(atoms_raw, exp_ids)
        if atoms_excerpt:
            atoms_block = (
                "\n\n=== ORIGINAL ATOMS (metric_source must quote exact phrases from below) ===\n"
                + atoms_excerpt
                + "\n=== END ATOMS ==="
            )

    user = (
        f"Target role: {target_role}\nTarget company: {target_company}\n\n"
        "## Ideal Candidate\n" + ideal.model_dump_json(indent=2)
        + "\n\n## Selected Experiences\n" + selection.model_dump_json(indent=2)
        + whitelist_block
        + atoms_block
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

        # Pass 2: structural source attribution check
        bullets = validate_metric_sources(bullets, atoms_raw)

        resume = TailoredResume(
            target_role=resume.target_role,
            target_company=resume.target_company,
            summary_statement=resume.summary_statement,
            bullets=bullets,
            packaging_notes=resume.packaging_notes,
        )

    return resume
