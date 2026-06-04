"""
Tests for onboarding.py — mock typer.prompt to simulate user input.
"""
import pytest
from unittest.mock import patch, call


@pytest.fixture(autouse=True)
def set_root(tmp_path, monkeypatch):
    """Point APPLYSMITH_ROOT at tmp_path for every test in this module."""
    monkeypatch.setenv("APPLYSMITH_ROOT", str(tmp_path))
    return tmp_path


def test_onboarding_returns_dict():
    """
    Simulate user selecting:
      Q1 stage = 1 (Summer internship)
      Q2 industries = 1,3 (Internet / Platform, New Energy / EV / Photovoltaic)
      Q3 roles = 1,2 (Operations..., Advertising / Marketing)
      Q4 company count = 5
    """
    from applysmith.onboarding import run_onboarding, STAGE_OPTIONS, INDUSTRY_OPTIONS, ROLE_OPTIONS

    prompt_responses = iter([
        "1",      # Q1: stage = Summer internship
        "1,3",    # Q2: industries = Internet / Platform, New Energy / EV / Photovoltaic
        "1,2",    # Q3: roles = Operations..., Advertising / Marketing
        "5",      # Q4: company count
    ])

    with patch("applysmith.onboarding.typer.prompt", side_effect=lambda *a, **kw: next(prompt_responses)):
        result = run_onboarding()

    assert isinstance(result, dict)
    assert "stage" in result
    assert "industries" in result
    assert "roles" in result
    assert "company_count" in result

    assert result["stage"] == STAGE_OPTIONS[0]  # "Summer internship"
    assert result["industries"] == [INDUSTRY_OPTIONS[0], INDUSTRY_OPTIONS[2]]
    assert result["roles"] == [ROLE_OPTIONS[0], ROLE_OPTIONS[1]]
    assert result["company_count"] == 5


def test_onboarding_other_industry():
    """
    Simulate user selecting 'Other' for industry and typing a custom value.
    """
    from applysmith.onboarding import run_onboarding

    # Q1=1, Q2=11 (Other -> custom), Q3=3, Q4=3
    prompt_responses = iter([
        "1",              # Q1: stage
        "11",             # Q2: industries = Other
        "Gaming",         # custom industry name
        "3",              # Q3: roles
        "3",              # Q4: company count
    ])

    with patch("applysmith.onboarding.typer.prompt", side_effect=lambda *a, **kw: next(prompt_responses)):
        result = run_onboarding()

    assert "Gaming" in result["industries"]


def test_initialize_creates_pipelines_from_answers(tmp_path):
    """
    Calling initialize_project with known answers should create
    the expected pipeline files.
    """
    from applysmith.package_generator import initialize_project

    answers = {
        "stage": "Autumn recruiting (秋招)",
        "industries": ["Internet / Platform", "Finance / Securities / Fund"],
        "roles": ["Data Analysis / Business Analysis"],
        "company_count": 10,
    }
    initialize_project(answers)

    pipelines_dir = tmp_path / "pipelines"
    pipeline_files = list(pipelines_dir.glob("*.md"))
    pipeline_names = {f.stem for f in pipeline_files}

    # Slugified: "internet_platform" and "finance_securities_fund"
    assert "internet__platform" in pipeline_names or any("internet" in n for n in pipeline_names), \
        f"Expected internet pipeline, got: {pipeline_names}"
    assert any("finance" in n for n in pipeline_names), \
        f"Expected finance pipeline, got: {pipeline_names}"

    # Should have exactly 2 pipelines (one per industry)
    assert len(pipeline_files) == 2, f"Expected 2 pipeline files, got {len(pipeline_files)}: {pipeline_names}"
