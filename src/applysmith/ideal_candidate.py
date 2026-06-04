"""
Ideal Candidate Generator — derives the ideal candidate profile from JDAnalysis.
"""
from .llm_client import call_llm_json
from .models import IdealCandidate, JDAnalysis
from .prompts.ideal_candidate import IDEAL_CANDIDATE_SYSTEM


def generate_ideal_candidate(jd_analysis: JDAnalysis, language: str = "en") -> IdealCandidate:
    """Generate an ideal candidate profile from a JDAnalysis object."""
    if language == "zh":
        system = (
            IDEAL_CANDIDATE_SYSTEM
            + "\nWrite all values in Simplified Chinese (简体中文), "
            "but keep technical terms, skill names, tool names, "
            "and proper nouns in English."
        )
    else:
        system = IDEAL_CANDIDATE_SYSTEM

    user = jd_analysis.model_dump_json(indent=2)
    return call_llm_json(system, user, IdealCandidate)
