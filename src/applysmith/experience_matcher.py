"""
Experience Matcher — matches user experience atoms against an ideal candidate profile.
"""
from .llm_client import call_llm_json
from .models import ExperienceSelectionResult, IdealCandidate
from .prompts.experience_match import EXPERIENCE_MATCH_SYSTEM


def _fix_packing_notes(data: dict) -> dict:
    """Tolerate field name typo: packing_notes → packaging_notes."""
    if "packing_notes" in data and "packaging_notes" not in data:
        data["packaging_notes"] = data.pop("packing_notes")
    return data


def match_experiences(
    ideal_candidate: IdealCandidate,
    experience_atoms_text: str,
    language: str = "en",
) -> ExperienceSelectionResult:
    """Match user experiences against the ideal candidate profile."""
    if language == "zh":
        system = (
            EXPERIENCE_MATCH_SYSTEM
            + "\nWrite all values in Simplified Chinese (简体中文), "
            "but keep technical terms, skill names, tool names, "
            "and proper nouns in English."
        )
    else:
        system = EXPERIENCE_MATCH_SYSTEM

    user = (
        "## Ideal Candidate Profile\n"
        + ideal_candidate.model_dump_json(indent=2)
        + "\n\n## User Experience Atoms\n"
        + experience_atoms_text
    )
    return call_llm_json(system, user, ExperienceSelectionResult, transform=_fix_packing_notes)
