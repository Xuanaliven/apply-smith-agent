"""
Phase 2 tests — ideal candidate generator, experience matcher, and CLI commands.
No real API calls: call_llm is always mocked.
"""
import json
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from applysmith.cli import app
from applysmith.ideal_candidate import generate_ideal_candidate
from applysmith.experience_matcher import match_experiences
from applysmith.models import IdealCandidate, ExperienceSelectionResult, JDAnalysis

runner = CliRunner()

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SAMPLE_JD_ANALYSIS = JDAnalysis(
    role_type="Product Manager",
    sub_role="Growth PM",
    core_tasks=["Define growth metrics", "Run A/B tests"],
    required_skills=["SQL", "Product sense"],
    preferred_skills=["Python"],
    keywords=["growth", "retention"],
    hidden_filters=["Startup experience preferred"],
    ideal_candidate_summary="Data-driven PM with 3+ years growth experience.",
    resume_strategy="Lead with quantified growth wins.",
    interview_focus=["Metric selection"],
    red_flags=["Vague success criteria"],
)

MOCK_IDEAL_CANDIDATE = {
    "role_type": "Growth Product Manager",
    "background_summary": "3+ years PM, 1+ year growth focus, strong SQL skills.",
    "must_have_experiences": ["Led A/B experiments", "Owned funnel metrics"],
    "nice_to_have_experiences": ["E-commerce background"],
    "must_have_skills": ["SQL", "A/B testing"],
    "differentiators": ["TikTok ecosystem familiarity"],
    "red_line_filters": ["No PM experience"],
}

MOCK_EXPERIENCE_SELECTION = {
    "included": [
        {
            "experience_id": "exp_001",
            "experience_name": "Growth experiment at Acme",
            "match_level": "Strong",
            "why_matched": "Directly matches A/B testing requirement",
            "suggested_angle": "Frame as funnel optimization initiative",
            "risk_notes": "",
        }
    ],
    "excluded": [
        {
            "experience_id": "exp_002",
            "experience_name": "Hardware supply chain project",
            "match_level": "Irrelevant",
            "why_matched": "No relevance to growth PM role",
            "suggested_angle": "",
            "risk_notes": "",
        }
    ],
    "packaging_notes": "Lead with growth experiments, quantify impact.",
    "capability_gaps": ["No TikTok ecosystem experience"],
}

SAMPLE_ATOMS_TEXT = """
## exp_001: Growth experiment at Acme
Type: product
Period: 2022-2023

## exp_002: Hardware supply chain project
Type: operations
Period: 2020-2021
"""


# ---------------------------------------------------------------------------
# 1. test_ideal_candidate_mock
# ---------------------------------------------------------------------------

def test_ideal_candidate_mock():
    """IdealCandidate is correctly parsed from mocked LLM JSON response."""
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_IDEAL_CANDIDATE)):
        result = generate_ideal_candidate(SAMPLE_JD_ANALYSIS)

    assert isinstance(result, IdealCandidate)
    assert result.role_type == "Growth Product Manager"
    assert "SQL" in result.must_have_skills
    assert len(result.red_line_filters) == 1


# ---------------------------------------------------------------------------
# 2. test_experience_matcher_mock
# ---------------------------------------------------------------------------

def test_experience_matcher_mock():
    """ExperienceSelectionResult is correctly parsed from mocked LLM JSON response."""
    ideal = IdealCandidate(**MOCK_IDEAL_CANDIDATE)

    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_EXPERIENCE_SELECTION)):
        result = match_experiences(ideal, SAMPLE_ATOMS_TEXT)

    assert isinstance(result, ExperienceSelectionResult)
    assert len(result.included) == 1
    assert result.included[0].match_level == "Strong"
    assert len(result.excluded) == 1
    assert result.excluded[0].match_level == "Irrelevant"
    assert len(result.capability_gaps) == 1


# ---------------------------------------------------------------------------
# 3. test_generate_candidate_profile_command
# ---------------------------------------------------------------------------

def test_generate_candidate_profile_command(tmp_path):
    """generate-candidate-profile writes 05_ideal_candidate.md correctly."""
    # Create the required JSON sidecar
    sidecar = tmp_path / "02_jd_analysis.json"
    sidecar.write_text(SAMPLE_JD_ANALYSIS.model_dump_json(), encoding="utf-8")
    (tmp_path / "02_jd_analysis.md").write_text("# JD Analysis", encoding="utf-8")

    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_IDEAL_CANDIDATE)):
        result = runner.invoke(app, ["generate-candidate-profile", "--app", str(tmp_path)])

    assert result.exit_code == 0, result.output
    out_file = tmp_path / "05_ideal_candidate.md"
    assert out_file.exists(), "05_ideal_candidate.md was not created"
    content = out_file.read_text(encoding="utf-8")
    assert "## Role Type" in content
    assert "Growth Product Manager" in content
    assert "Generated by ApplySmith" in content

    # JSON sidecar for downstream commands
    assert (tmp_path / "05_ideal_candidate.json").exists()


# ---------------------------------------------------------------------------
# 4. test_match_experiences_command
# ---------------------------------------------------------------------------

def test_match_experiences_command(tmp_path):
    """match-experiences writes 06_selected_experiences.md correctly."""
    # Create required sidecar
    ideal = IdealCandidate(**MOCK_IDEAL_CANDIDATE)
    sidecar = tmp_path / "05_ideal_candidate.json"
    sidecar.write_text(ideal.model_dump_json(), encoding="utf-8")

    atoms_file = tmp_path / "experience_atoms.md"
    atoms_file.write_text(SAMPLE_ATOMS_TEXT, encoding="utf-8")

    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_EXPERIENCE_SELECTION)):
        result = runner.invoke(
            app,
            ["match-experiences", "--app", str(tmp_path), "--profile", str(atoms_file)],
        )

    assert result.exit_code == 0, result.output
    out_file = tmp_path / "06_selected_experiences.md"
    assert out_file.exists(), "06_selected_experiences.md was not created"
    content = out_file.read_text(encoding="utf-8")
    assert "## Included Experiences" in content
    assert "Growth experiment at Acme" in content
    assert "## Capability Gaps" in content
    assert "1 experiences matched" in result.output
