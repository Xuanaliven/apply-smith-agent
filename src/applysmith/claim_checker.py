"""
Claim Checker — independent second-pass audit of resume bullet risk levels.
"""
import re
from typing import Optional

from .llm_client import call_llm_json
from .models import ClaimCheckReport, ResumeBullet, TailoredResume
from .prompts.claim_check import CLAIM_CHECK_SYSTEM

_NUM_PATTERN = re.compile(r"\d+\.?\d*")


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
                   metric_source strings are genuine verbatim excerpts.
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
    # restore it from the generator output and use it for post-validation.
    source_lookup = {b.bullet_text: b.metric_source for b in resume.bullets}

    atoms_normalised = (
        re.sub(r"\s+", " ", atoms_raw).lower() if atoms_raw else None
    )

    fixed: list[ResumeBullet] = []
    for b in report.bullets:
        nums = _NUM_PATTERN.findall(b.bullet_text)
        if not nums:
            fixed.append(b)
            continue

        metric_source = source_lookup.get(b.bullet_text, b.metric_source)

        # Rule 1: numbers present but no metric_source → auto-flag Red
        if not metric_source:
            fixed.append(ResumeBullet(
                experience_name=b.experience_name,
                bullet_text=b.bullet_text,
                claim_level="Red",
                evidence=b.evidence,
                interview_risk=(
                    "[AUTO-FLAGGED: numbers present but no metric_source attribution] "
                    + b.interview_risk
                ),
                recommended_action="Add verbatim metric_source or remove number from bullet",
                metric_source="",
            ))
            continue

        # Rule 2: metric_source not found verbatim in atoms_raw → auto-flag Red
        if atoms_normalised is not None:
            src_norm = re.sub(r"\s+", " ", metric_source).strip().lower()
            if src_norm and src_norm not in atoms_normalised:
                fixed.append(ResumeBullet(
                    experience_name=b.experience_name,
                    bullet_text=b.bullet_text,
                    claim_level="Red",
                    evidence=b.evidence,
                    interview_risk=(
                        "[AUTO-FLAGGED: metric_source not found verbatim in atoms] "
                        + b.interview_risk
                    ),
                    recommended_action="Verify metric_source against experience_atoms",
                    metric_source=metric_source,
                ))
                continue

        # Propagate metric_source into the report bullet
        fixed.append(ResumeBullet(
            experience_name=b.experience_name,
            bullet_text=b.bullet_text,
            claim_level=b.claim_level,
            evidence=b.evidence,
            interview_risk=b.interview_risk,
            recommended_action=b.recommended_action,
            metric_source=metric_source,
        ))

    return ClaimCheckReport(
        overall_risk=report.overall_risk,
        summary=report.summary,
        bullets=fixed,
    )
