"""
Phase 4 tests — interview defense generator and CLI command.
No real API calls: call_llm is always mocked.
"""
import json
from unittest.mock import patch

from typer.testing import CliRunner

from applysmith.cli import app
from applysmith.interview_defense import generate_defense
from applysmith.models import (
    BulletDefense,
    ClaimCheckReport,
    InterviewDefenseReport,
    ResumeBullet,
    TailoredResume,
)

runner = CliRunner()

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

RESUME = TailoredResume(
    target_role="增长产品实习生",
    target_company="得物",
    summary_statement="Data-driven PM candidate with internship experience.",
    bullets=[
        ResumeBullet(
            experience_name="数据运营实习",
            bullet_text="Built sales forecasting model using SQL that improved forecast accuracy.",
            claim_level="Green",
            evidence="实习期间实际参与",
            interview_risk="May be asked for model details",
            recommended_action="Prepare model specifics",
        ),
        ResumeBullet(
            experience_name="BodyBuilder.ai",
            bullet_text="Owned end-to-end product lifecycle integrating AI pose estimation model.",
            claim_level="Buildable",
            evidence="Self-initiated project",
            interview_risk="Not a commercial product",
            recommended_action="Clarify scope and limitations",
        ),
    ],
    packaging_notes="Lead with data skills.",
)

CLAIM_REPORT = ClaimCheckReport(
    overall_risk="Medium",
    summary="Mostly defensible. One Buildable claim needs clarification.",
    bullets=[
        ResumeBullet(
            experience_name="数据运营实习",
            bullet_text="Built sales forecasting model using SQL that improved forecast accuracy.",
            claim_level="Green",
            evidence="实习期间实际参与",
            interview_risk="May be asked for model details",
            recommended_action="Prepare model specifics",
        ),
        ResumeBullet(
            experience_name="BodyBuilder.ai",
            bullet_text="Owned end-to-end product lifecycle integrating AI pose estimation model.",
            claim_level="Red",
            evidence="Self-initiated project only",
            interview_risk="No commercial validation",
            recommended_action="Soften or remove",
        ),
    ],
)

MOCK_DEFENSE = {
    "target_role": "增长产品实习生",
    "target_company": "得物",
    "overall_strategy": "Lead with data skills. Be transparent about project scope.",
    "bullet_defenses": [
        {
            "bullet_text": "Built sales forecasting model using SQL that improved forecast accuracy.",
            "claim_level": "Green",
            "likely_questions": [
                "What data did you use for this model?",
                "How did you measure accuracy improvement?",
                "What was the business impact?",
            ],
            "answer_framework": "STAR: Situation — fragmented sales data. Task — build forecast model. Action — SQL pipeline + regression. Result — measurable accuracy gain.",
            "key_talking_points": ["SQL pipeline", "Cross-team collaboration", "Measurable metric"],
            "risk_boundary": "Do not overstate the model complexity.",
            "evidence_to_prepare": ["Model schema", "Sample output", "Business metric before/after"],
            "what_not_to_say": ["We used ML", "It was fully automated"],
        },
        {
            "bullet_text": "Owned end-to-end product lifecycle integrating AI pose estimation model.",
            "claim_level": "Red",
            "likely_questions": [
                "How many users did this product have?",
                "Was this deployed to production?",
                "What was the business outcome?",
                "How did you validate the AI model accuracy?",
            ],
            "answer_framework": "Be upfront: self-initiated project. Focus on process and learnings.",
            "key_talking_points": ["End-to-end ownership", "AI integration", "Product thinking"],
            "risk_boundary": "Do not imply this was a commercial product.",
            "evidence_to_prepare": ["PRD document", "Demo or screenshots", "Competitive analysis"],
            "what_not_to_say": ["Our users", "We launched", "It went viral"],
        },
    ],
    "general_questions": [
        "Why 得物?",
        "Why growth product?",
        "Where do you see yourself in 3 years?",
    ],
    "capability_gap_questions": [
        "You don't have Google/Meta ads experience — how would you ramp up?",
        "Have you ever run a real A/B test in a production environment?",
    ],
}


# ---------------------------------------------------------------------------
# 1. test_interview_defense_mock
# ---------------------------------------------------------------------------

def test_interview_defense_mock():
    """InterviewDefenseReport is correctly parsed from mocked LLM JSON response."""
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_DEFENSE)):
        result = generate_defense(RESUME, CLAIM_REPORT)

    assert isinstance(result, InterviewDefenseReport)
    assert result.target_role == "增长产品实习生"
    assert result.target_company == "得物"
    assert len(result.bullet_defenses) == 2
    assert len(result.general_questions) == 3
    assert len(result.capability_gap_questions) == 2


# ---------------------------------------------------------------------------
# 2. test_generate_defense_command
# ---------------------------------------------------------------------------

def test_generate_defense_command(tmp_path):
    """generate-defense writes 09_interview_defense.md and .json correctly."""
    (tmp_path / "07_tailored_resume.json").write_text(RESUME.model_dump_json(), encoding="utf-8")
    (tmp_path / "08_claim_check_report.json").write_text(CLAIM_REPORT.model_dump_json(), encoding="utf-8")

    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_DEFENSE)):
        result = runner.invoke(app, ["generate-defense", "--app", str(tmp_path)])

    assert result.exit_code == 0, result.output
    md = tmp_path / "09_interview_defense.md"
    assert md.exists()
    content = md.read_text(encoding="utf-8")
    assert "# Interview Defense Guide" in content
    assert "## Overall Strategy" in content
    assert "## Bullet-by-Bullet Defense" in content
    assert "Generated by ApplySmith" in content
    assert (tmp_path / "09_interview_defense.json").exists()
    assert "2 bullets defended" in result.output
    assert "2 gap questions identified" in result.output


# ---------------------------------------------------------------------------
# 3. test_gap_questions_present
# ---------------------------------------------------------------------------

def test_gap_questions_present(tmp_path):
    """Capability gap questions appear in the output markdown."""
    (tmp_path / "07_tailored_resume.json").write_text(RESUME.model_dump_json(), encoding="utf-8")
    (tmp_path / "08_claim_check_report.json").write_text(CLAIM_REPORT.model_dump_json(), encoding="utf-8")

    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_DEFENSE)):
        runner.invoke(app, ["generate-defense", "--app", str(tmp_path)])

    content = (tmp_path / "09_interview_defense.md").read_text(encoding="utf-8")
    assert "## Capability Gap Questions" in content
    assert "Google/Meta" in content
    assert "A/B test" in content


# ---------------------------------------------------------------------------
# 4. test_red_claims_get_more_questions
# ---------------------------------------------------------------------------

def test_red_claims_get_more_questions():
    """Red claim bullets have at least 3 likely_questions."""
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_DEFENSE)):
        result = generate_defense(RESUME, CLAIM_REPORT)

    red_defenses = [bd for bd in result.bullet_defenses if bd.claim_level == "Red"]
    assert red_defenses, "Expected at least one Red claim defense"
    for bd in red_defenses:
        assert len(bd.likely_questions) >= 3, (
            f"Red claim '{bd.bullet_text[:40]}' has only {len(bd.likely_questions)} questions"
        )
