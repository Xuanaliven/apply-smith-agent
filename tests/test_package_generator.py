"""
Tests for package_generator.py — all run in a tmp_path with APPLYSMITH_ROOT set.
"""
import os
import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def set_root(tmp_path, monkeypatch):
    """Point APPLYSMITH_ROOT at tmp_path for every test in this module."""
    monkeypatch.setenv("APPLYSMITH_ROOT", str(tmp_path))
    return tmp_path


def test_init_creates_all_folders(tmp_path):
    from applysmith.package_generator import initialize_project

    answers = {
        "stage": "Autumn recruiting (秋招)",
        "industries": ["Internet / Platform"],
        "roles": ["Data Analysis / Business Analysis"],
        "company_count": 5,
    }
    initialize_project(answers)

    # Check key directories
    assert (tmp_path / "data" / "master_profile").is_dir()
    assert (tmp_path / "data" / "industry_maps").is_dir()
    assert (tmp_path / "data" / "role_schemas").is_dir()
    assert (tmp_path / "data" / "capability_roadmaps").is_dir()
    assert (tmp_path / "data" / "company_dossiers").is_dir()
    assert (tmp_path / "data" / "company_sources" / "annual_reports").is_dir()
    assert (tmp_path / "data" / "company_sources" / "job_descriptions").is_dir()
    assert (tmp_path / "data" / "question_bank").is_dir()
    assert (tmp_path / "data" / "external_signals" / "imported").is_dir()
    assert (tmp_path / "pipelines").is_dir()
    assert (tmp_path / "strategy").is_dir()
    assert (tmp_path / "applications").is_dir()

    # Check init marker
    assert (tmp_path / ".applysmith_initialized").exists()

    # Check strategy files
    assert (tmp_path / "strategy" / "target_map.md").exists()
    assert (tmp_path / "strategy" / "opportunity_scores.md").exists()
    assert (tmp_path / "strategy" / "weekly_plan.md").exists()
    assert (tmp_path / "strategy" / "capability_gap_board.md").exists()

    # Check master profile files
    assert (tmp_path / "data" / "master_profile" / "profile_questions.md").exists()
    assert (tmp_path / "data" / "master_profile" / "experience_atoms.md").exists()
    assert (tmp_path / "data" / "master_profile" / "skills.md").exists()
    assert (tmp_path / "data" / "master_profile" / "forbidden_claims.md").exists()


def test_new_pipeline_creates_file(tmp_path):
    from applysmith.package_generator import create_pipeline

    path = create_pipeline("tech_ops", "Internet / Platform", "Data Analysis")
    assert path.exists()

    content = path.read_text(encoding="utf-8")
    # Check all required section headers
    assert "# Pipeline: tech_ops" in content
    assert "## Target Industry" in content
    assert "## Target Roles" in content
    assert "## Candidate Profile" in content
    assert "## Opportunity Score" in content
    assert "## Current Ceiling" in content
    assert "## Packaging Ceiling" in content
    assert "## Buildable Ceiling" in content
    assert "## Capability Gaps" in content
    assert "## Weekly Actions" in content
    assert "## Application Records" in content


def test_new_application_creates_11_files(tmp_path):
    from applysmith.package_generator import create_application

    folder = create_application(
        company="ByteDance",
        role="Data Analyst",
        date_str="2025-09-01",
        channel="campus portal",
        pipeline="internet_platform",
    )
    assert folder.is_dir()

    files = list(folder.iterdir())
    assert len(files) == 11, f"Expected 11 files, got {len(files)}: {[f.name for f in files]}"

    # Check specific filenames exist
    names = {f.name for f in files}
    for expected in [
        "01_jd_original.md",
        "02_jd_analysis.md",
        "03_company_dossier_snapshot.md",
        "04_business_unit_hypothesis.md",
        "05_ideal_candidate.md",
        "06_selected_experiences.md",
        "07_tailored_resume.md",
        "08_claim_check_report.md",
        "09_interview_defense.md",
        "10_question_bank_links.md",
        "11_application_log.md",
    ]:
        assert expected in names, f"Missing file: {expected}"


def test_no_overwrite_pipeline(tmp_path):
    from applysmith.package_generator import create_pipeline

    create_pipeline("fintech", "Finance", "Data Analysis")

    with pytest.raises(FileExistsError):
        create_pipeline("fintech", "Finance", "Data Analysis")


def test_no_overwrite_application(tmp_path):
    from applysmith.package_generator import create_application

    create_application(
        company="Alibaba",
        role="Operations",
        date_str="2025-08-15",
        channel="LinkedIn",
        pipeline="ecommerce",
    )

    with pytest.raises(FileExistsError):
        create_application(
            company="Alibaba",
            role="Operations",
            date_str="2025-08-15",
            channel="LinkedIn",
            pipeline="ecommerce",
        )
