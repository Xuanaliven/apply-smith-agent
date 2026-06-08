"""
Claim Checker — independent second-pass audit of resume bullet risk levels.

Role split:
  - Structural validation (validate_metric_sources) is the authoritative metric
    fabrication check — same 3 steps as resume_generator.
  - The LLM provides qualitative interview-risk commentary but cannot override
    a structurally-validated Green bullet back to Red.

Final claim_level logic:
  1. If structural validation flags a bullet (metric mismatch, missing source,
     context swap) → Red, regardless of LLM opinion.
  2. If structural validation passes → use the generator's claim_level from
     07_tailored_resume.json (the authoritative validated output). The LLM's
     risk commentary is preserved but does not override the claim_level.
"""
from typing import Optional

from .llm_client import call_llm_json
from .metric_validator import _NUM_PATTERN, validate_metric_sources
from .models import ClaimCheckReport, ResumeBullet, TailoredResume
from .prompts.claim_check import CLAIM_CHECK_SYSTEM

# Prefixes added by validate_metric_sources when it flags a bullet
_VALIDATOR_FLAGS = (
    "[METRIC SOURCE MISSING",
    "[METRIC MISMATCH",
    "[METRIC NUMBER NOT IN ATOMS",
    "[CONTEXT MISMATCH",
    "[AUTO-FLAGGED",
)


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

    # Lookups keyed by bullet_text from the generator's validated output.
    # The LLM checker receives the same JSON so bullet_text should match exactly.
    source_lookup = {b.bullet_text: b.metric_source for b in resume.bullets}
    gen_level_lookup = {b.bullet_text: b.claim_level for b in resume.bullets}

    # Restore metric_source (the checker LLM doesn't re-emit this field)
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
    validated = validate_metric_sources(restored, atoms_raw)

    # Resolve final claim_level:
    #   - Validator flagged → Red (structural failure overrides everything)
    #   - Validator passed, checker says Red → restore generator's level.
    #     The checker LLM doesn't see atoms and often over-flags valid metrics.
    #     Structural validation is the authoritative metric-fabrication check.
    #   - Validator passed, checker says Yellow/Green/etc. → keep checker's level.
    #     Qualitative interview-risk downgrades (e.g. Green→Yellow) are valid.
    final: list[ResumeBullet] = []
    for b in validated:
        validator_flagged = any(flag in b.interview_risk for flag in _VALIDATOR_FLAGS)
        if validator_flagged:
            # Structural validation failed → Red is authoritative
            final.append(b)
        elif b.claim_level == "Red":
            # Checker said Red but structural validation passed → restore
            # generator's level (checker was over-conservative without atoms)
            gen_level = gen_level_lookup.get(b.bullet_text, b.claim_level)
            final.append(ResumeBullet(
                experience_name=b.experience_name,
                bullet_text=b.bullet_text,
                claim_level=gen_level,
                evidence=b.evidence,
                interview_risk=b.interview_risk,
                recommended_action=b.recommended_action,
                metric_source=b.metric_source,
            ))
        else:
            # Checker's qualitative level (Yellow, Green, Buildable, Stretch) → keep
            final.append(b)

    # Fill in any generator bullets the checker LLM omitted from its output.
    # The LLM sometimes truncates when it has "nothing to add" for Green bullets.
    # Only apply when the checker returned FEWER bullets than the generator —
    # if the checker returned equal or more, it's producing its own content
    # and we shouldn't silently inject generator bullets.
    if len(report.bullets) < len(resume.bullets):
        checked_texts = {b.bullet_text for b in final}
        for b in resume.bullets:
            if b.bullet_text not in checked_texts:
                final.append(b)

    return ClaimCheckReport(
        overall_risk=report.overall_risk,
        summary=report.summary,
        bullets=final,
    )
