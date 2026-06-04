"""
Phase 5 tests — capability gap builder and CLI command.
No real API calls: call_llm is always mocked.
"""
import json
from unittest.mock import patch

from typer.testing import CliRunner

from applysmith.cli import app
from applysmith.gap_builder import build_gap_plan
from applysmith.models import (
    CapabilityGapPlan,
    ExperienceMatch,
    ExperienceSelectionResult,
    LearningTask,
    SimulationProject,
    TailoredResume,
    ResumeBullet,
)

runner = CliRunner()

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

GAPS = [
    "No Google Ads or Meta Ads hands-on experience",
    "No A/B test design in a production environment",
    "No CAC / ROAS attribution analysis experience",
]

MOCK_GAP_PLAN = {
    "target_role": "增长产品实习生",
    "target_company": "得物",
    "gaps": GAPS,
    "learning_tasks": [
        {
            "skill": "Google Ads",
            "why_needed": "Core tool for the role",
            "learning_resources": [
                "Google Skillshop — Google Ads certification (free)",
                "Coursera: Google Digital Marketing & E-commerce",
            ],
            "estimated_hours": "20-30 hours",
            "priority": "High",
        },
        {
            "skill": "A/B Test Design",
            "why_needed": "Required for experiment-driven optimization",
            "learning_resources": [
                "Udacity: A/B Testing (free audit)",
                "Book: Trustworthy Online Controlled Experiments",
            ],
            "estimated_hours": "15-20 hours",
            "priority": "High",
        },
    ],
    "simulation_projects": [
        {
            "skill": "Google Ads",
            "project_title": "E-commerce Ad Performance Analysis",
            "project_type": "portfolio_project",
            "dataset_suggestions": [
                "Kaggle: Google Merchandise Store dataset (public GA4 export)",
                "Google Analytics Demo Account data",
            ],
            "deliverables": [
                "Campaign performance dashboard",
                "Optimization recommendations report",
                "A/B test design proposal",
            ],
            "resume_bullet_template": (
                "Analyzed [DATASET] ad campaign data to identify [INSIGHT], "
                "proposing optimization strategy projected to improve [METRIC]"
            ),
            "interview_defense_notes": (
                "Be upfront this is a portfolio project using public data. "
                "Focus on methodology and analytical thinking, not scale."
            ),
            "warning": (
                "This is a self-initiated project. "
                "Never present it as a real company internship."
            ),
        }
    ],
    "priority_order": [
        "Complete Google Ads certification",
        "Build ad performance portfolio project",
        "Study A/B test design fundamentals",
    ],
    "weekly_action_plan": (
        "Week 1-2: Complete Google Skillshop certification. "
        "Week 3-4: Download GA4 public dataset and build dashboard. "
        "Week 5-6: Design and document an A/B test proposal for a mock campaign."
    ),
}

SELECTION = ExperienceSelectionResult(
    included=[
        ExperienceMatch(
            experience_id="EXP-001",
            experience_name="产品运营实习",
            match_level="Weak",
            why_matched="General product skills",
            suggested_angle="Frame as data product work",
            risk_notes="",
        )
    ],
    excluded=[],
    packaging_notes="Lead with data.",
    capability_gaps=GAPS,
)

RESUME = TailoredResume(
    target_role="增长产品实习生",
    target_company="得物",
    summary_statement="Data-driven candidate.",
    bullets=[
        ResumeBullet(
            experience_name="产品运营实习",
            bullet_text="Built dashboards.",
            claim_level="Green",
            evidence="e",
            interview_risk="r",
            recommended_action="a",
        )
    ],
    packaging_notes="Lead with data.",
)


# ---------------------------------------------------------------------------
# 1. test_gap_builder_mock
# ---------------------------------------------------------------------------

def test_gap_builder_mock():
    """CapabilityGapPlan is correctly parsed from mocked LLM JSON response."""
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_GAP_PLAN)):
        result = build_gap_plan(GAPS, "增长产品实习生", "得物")

    assert isinstance(result, CapabilityGapPlan)
    assert result.target_role == "增长产品实习生"
    assert len(result.gaps) == 3
    assert len(result.learning_tasks) == 2
    assert len(result.simulation_projects) == 1
    assert result.learning_tasks[0].priority == "High"


# ---------------------------------------------------------------------------
# 2. test_build_gap_plan_command
# ---------------------------------------------------------------------------

def test_build_gap_plan_command(tmp_path):
    """build-gap-plan writes gap_plan.md and gap_plan.json correctly."""
    (tmp_path / "06_selected_experiences.json").write_text(
        SELECTION.model_dump_json(), encoding="utf-8"
    )
    (tmp_path / "07_tailored_resume.json").write_text(
        RESUME.model_dump_json(), encoding="utf-8"
    )

    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_GAP_PLAN)):
        result = runner.invoke(app, ["build-gap-plan", "--app", str(tmp_path)])

    assert result.exit_code == 0, result.output
    md = tmp_path / "gap_plan.md"
    assert md.exists()
    content = md.read_text(encoding="utf-8")
    assert "# Capability Gap Plan" in content
    assert "## Identified Gaps" in content
    assert "## Learning Tasks" in content
    assert "## Simulation Projects" in content
    assert "Generated by ApplySmith" in content
    assert (tmp_path / "gap_plan.json").exists()
    assert "3 gaps identified" in result.output
    assert "2 learning tasks" in result.output
    assert "1 projects suggested" in result.output


# ---------------------------------------------------------------------------
# 3. test_simulation_project_warning
# ---------------------------------------------------------------------------

def test_simulation_project_warning():
    """Every SimulationProject must contain a non-empty warning field."""
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_GAP_PLAN)):
        result = build_gap_plan(GAPS, "增长产品实习生", "得物")

    for proj in result.simulation_projects:
        assert proj.warning, f"Project '{proj.project_title}' has empty warning"
        assert "self-initiated" in proj.warning.lower() or "portfolio" in proj.warning.lower(), (
            f"Warning does not mention self-initiated/portfolio: {proj.warning}"
        )


# ---------------------------------------------------------------------------
# 4. test_no_fabricated_projects
# ---------------------------------------------------------------------------

def test_no_fabricated_projects():
    """project_type must be one of the three allowed values for all projects."""
    from applysmith.models import VALID_PROJECT_TYPES

    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_GAP_PLAN)):
        result = build_gap_plan(GAPS, "增长产品实习生", "得物")

    for proj in result.simulation_projects:
        assert proj.project_type in VALID_PROJECT_TYPES, (
            f"Invalid project_type '{proj.project_type}' for project '{proj.project_title}'"
        )
