"""
Claim Checker — independent second-pass audit of resume bullet risk levels.
"""
from typing import Optional

from .llm_client import call_llm_json
from .metric_validator import _NUM_PATTERN, validate_metric_sources
from .models import ClaimCheckReport, ResumeBullet, TailoredResume
from .prompts.claim_check import CLAIM_CHECK_SYSTEM


def check_claims(
    resume: TailoredResume,
    language: str = "en",
    atoms_raw: Optional[str] = None,
) -> ClaimCheckReport:
    """Run an independent claim audit on a tailored resume.

    Args:
        resume: The tailored resume to audit.
        language: Output language ("en" or "zh").
        atoms_raw: Optional raw text of experience_atoms.md used to verify that
                   metric_source attributions pass the same 3-step structural
                   validator used by the resume generator.
    """
    if language == "zh":
        system = (
            CLAIM_CHECK_SYSTEM
            + "\nWrite evidence, interview_risk, recommended_action, and summary "
            "in Simplified Chinese (简体中文). Keep bullet_text in English."
        )
    else:
        system = CLAIM_CHECK_SYSTEM

    report = call_llm_json(system, resume.model_dump_json(indent=2), ClaimCheckReport)

    # Build lookup: bullet_text → metric_source from the original resume.
    # The LLM's claim-check response doesn't re-state metric_source, so we
    # restore it from the generator output before running structural validation.
    source_lookup = {b.bullet_text: b.metric_source for b in resume.bullets}

    # Restore metric_source into each checker bullet
    restored: list[ResumeBullet] = []
    for b in report.bullets:
        ms = source_lookup.get(b.bullet_text, b.metric_source)
        restored.append(ResumeBullet(
            experience_name=b.experience_name,
            bullet_text=b.bullet_text,
            claim_level=b.claim_level,
            evidence=b.evidence,
            interview_risk=b.interview_risk,
            recommended_action=b.recommended_action,
            metric_source=ms,
        ))

    # Apply same 3-step structural validator as resume_generator
    fixed = validate_metric_sources(restored, atoms_raw)

    return ClaimCheckReport(
        overall_risk=report.overall_risk,
        summary=report.summary,
        bullets=fixed,
    )
