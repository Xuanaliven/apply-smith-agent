"""
JD Analyzer — sends a raw JD to LLM and parses the structured response.
"""
from .llm_client import call_llm_json
from .models import JDAnalysis
from .prompts.jd_analysis import JD_ANALYSIS_SYSTEM

_LANG_INSTRUCTIONS = {
    "en": "Write all values in English.",
    "zh": (
        "Write all values in Simplified Chinese (简体中文), "
        "but keep technical terms, skill names, tool names, "
        "and proper nouns in English (e.g. SQL, A/B testing, Python, PRD)."
    ),
}


def _build_system_prompt(language: str) -> str:
    lang_instruction = _LANG_INSTRUCTIONS.get(language, _LANG_INSTRUCTIONS["en"])
    return JD_ANALYSIS_SYSTEM.format(lang_instruction=lang_instruction)


def analyze_jd(jd_text: str, language: str = "en") -> JDAnalysis:
    """Analyze a raw JD and return a structured JDAnalysis."""
    system_prompt = _build_system_prompt(language)
    return call_llm_json(system_prompt, jd_text, JDAnalysis)
