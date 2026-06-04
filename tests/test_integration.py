"""
Integration tests — make REAL API calls to DeepSeek.

These tests are excluded from the default pytest run.
Run them with:
    pytest tests/test_integration.py -m integration

They require APPLYSMITH_API_KEY to be set in .env or the environment.
"""
import json

import pytest

from applysmith.llm_client import call_llm, call_llm_json
from applysmith.jd_analyzer import analyze_jd
from applysmith.ideal_candidate import generate_ideal_candidate
from applysmith.resume_generator import generate_resume
from applysmith.models import (
    ExperienceMatch,
    ExperienceSelectionResult,
    IdealCandidate,
    JDAnalysis,
    TailoredResume,
)

# ---------------------------------------------------------------------------
# Minimal fixtures
# ---------------------------------------------------------------------------

SAMPLE_JD = """\
Job Title: Data Analyst Intern
Company: TechCorp

We are looking for a Data Analyst Intern to join our growth team.

Responsibilities:
- Analyze user behavior data using SQL and Python
- Build dashboards in Tableau or Power BI
- Support A/B test design and result interpretation
- Present findings to cross-functional teams

Requirements:
- Currently pursuing a degree in Statistics, CS, or related field
- Proficiency in SQL and Python (pandas, numpy)
- Experience with data visualization tools
- Strong communication skills

Nice to have:
- Familiarity with experimentation frameworks
- Experience with large-scale datasets
"""

SAMPLE_JD_ANALYSIS = JDAnalysis(
    role_type="Data Analytics",
    sub_role="Business / Growth Analytics Intern",
    core_tasks=["SQL analysis", "dashboard building", "A/B test support"],
    required_skills=["SQL", "Python", "data visualization"],
    preferred_skills=["experimentation frameworks"],
    keywords=["SQL", "Python", "Tableau", "A/B testing", "data analysis"],
    hidden_filters=["degree in progress"],
    ideal_candidate_summary="A quantitatively strong student with hands-on SQL and Python experience.",
    resume_strategy="Lead with data projects and quantifiable results.",
    interview_focus=["SQL problem-solving", "statistics", "communication of findings"],
    red_flags=[],
)

SAMPLE_IDEAL_CANDIDATE = IdealCandidate(
    role_type="Data Analytics",
    background_summary="Strong quantitative background with hands-on SQL and Python skills.",
    must_have_experiences=["SQL data analysis project", "visualization work"],
    nice_to_have_experiences=["A/B test design"],
    must_have_skills=["SQL", "Python", "pandas"],
    differentiators=["End-to-end project ownership", "strong presentation skills"],
    red_line_filters=["No SQL experience"],
)

SAMPLE_SELECTION = ExperienceSelectionResult(
    included=[
        ExperienceMatch(
            experience_id="EXP-001",
            experience_name="Sales Data Dashboard",
            match_level="Strong",
            why_matched="Direct SQL + visualization experience",
            suggested_angle="Emphasize business impact and turnaround time",
            risk_notes="",
        )
    ],
    excluded=[],
    packaging_notes="Lead with data impact.",
    capability_gaps=[],
)


# ---------------------------------------------------------------------------
# 1. test_real_jd_analysis
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_real_jd_analysis():
    """Real API call: analyze a sample JD and verify it parses into JDAnalysis."""
    result = analyze_jd(SAMPLE_JD, language="en")

    assert isinstance(result, JDAnalysis)
    assert result.role_type, "role_type should not be empty"
    assert isinstance(result.core_tasks, list), "core_tasks should be a list"
    assert len(result.core_tasks) > 0, "core_tasks should not be empty"
    assert isinstance(result.required_skills, list)
    assert isinstance(result.keywords, list)
    assert result.ideal_candidate_summary, "ideal_candidate_summary should not be empty"
    assert result.resume_strategy, "resume_strategy should not be empty"


# ---------------------------------------------------------------------------
# 2. test_real_ideal_candidate
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_real_ideal_candidate():
    """Real API call: generate ideal candidate profile and verify it parses into IdealCandidate."""
    result = generate_ideal_candidate(SAMPLE_JD_ANALYSIS, language="en")

    assert isinstance(result, IdealCandidate)
    assert result.role_type, "role_type should not be empty"
    assert result.background_summary, "background_summary should not be empty"
    assert isinstance(result.must_have_experiences, list)
    assert len(result.must_have_experiences) > 0
    assert isinstance(result.must_have_skills, list)
    assert len(result.must_have_skills) > 0
    assert isinstance(result.red_line_filters, list)


# ---------------------------------------------------------------------------
# 3. test_real_resume_generation
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_real_resume_generation():
    """Real API call: generate tailored resume and verify it parses into TailoredResume."""
    result = generate_resume(
        selection=SAMPLE_SELECTION,
        ideal=SAMPLE_IDEAL_CANDIDATE,
        target_role="Data Analyst Intern",
        target_company="TechCorp",
        language="en",
    )

    assert isinstance(result, TailoredResume)
    assert result.target_role, "target_role should not be empty"
    assert result.target_company, "target_company should not be empty"
    assert result.summary_statement, "summary_statement should not be empty"
    assert isinstance(result.bullets, list)
    assert len(result.bullets) > 0, "bullets list should not be empty"

    # Verify each bullet has required fields
    for bullet in result.bullets:
        assert bullet.bullet_text, "bullet_text should not be empty"
        assert bullet.claim_level in {"Green", "Yellow", "Red", "Buildable", "Stretch"}, (
            f"Invalid claim_level: {bullet.claim_level}"
        )


# ---------------------------------------------------------------------------
# 4. test_llm_returns_valid_json
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_llm_returns_valid_json():
    """Real API call: verify LLM returns parseable JSON (not markdown-wrapped garbage)."""
    system = (
        "You are a JSON API. Return ONLY a JSON object with exactly two fields: "
        '"status" (string, always "ok") and "echo" (string, the user message repeated). '
        "No markdown. No explanation. No code fences."
    )
    user = "hello integration test"

    raw = call_llm(system, user)

    # Must not be wrapped in markdown fences after extraction
    assert raw.strip(), "Response must not be empty"

    # Import the extractor to simulate what call_llm_json does
    from applysmith.llm_client import _extract_json_str
    cleaned = _extract_json_str(raw)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"LLM response could not be parsed as JSON.\n"
            f"Parse error: {exc}\n"
            f"Raw response:\n{raw}"
        )

    assert isinstance(data, dict), "JSON root must be an object"
    assert "status" in data, f"Expected 'status' key, got keys: {list(data.keys())}"
    assert data["status"] == "ok", f"Expected status='ok', got: {data['status']!r}"
