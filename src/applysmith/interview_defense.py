"""
Interview Defense Generator — produces bullet-by-bullet interview prep from resume + claim check.
"""
from .llm_client import call_llm_json
from .models import ClaimCheckReport, InterviewDefenseReport, TailoredResume
from .prompts.interview_defense import INTERVIEW_DEFENSE_SYSTEM


def generate_defense(
    resume: TailoredResume,
    claim_report: ClaimCheckReport,
    language: str = "en",
) -> InterviewDefenseReport:
    """Generate interview defense materials from a tailored resume and claim check report."""
    if language == "zh":
        system = (
            INTERVIEW_DEFENSE_SYSTEM
            + "\nWrite all values in Simplified Chinese (简体中文), "
            "but keep bullet_text and likely_questions in English where possible. "
            "Keep technical terms, skill names, tool names, and proper nouns in English."
        )
    else:
        system = INTERVIEW_DEFENSE_SYSTEM

    user = (
        "## Tailored Resume\n" + resume.model_dump_json(indent=2)
        + "\n\n## Claim Check Report\n" + claim_report.model_dump_json(indent=2)
    )
    return call_llm_json(system, user, InterviewDefenseReport)
