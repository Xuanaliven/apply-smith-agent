"""
Phase 6 tests — Application Tracker.
No real API calls; all filesystem operations use tmp_path.
"""
import json
from datetime import date, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from applysmith.cli import app
from applysmith.models import ApplicationStatus, TrackerSummary, VALID_TRACKER_STATUSES
from applysmith.tracker import scan_applications, get_summary, update_status, weekly_review

runner = CliRunner()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LOG_TEMPLATE = """\
# Application Log

## Company
{company}

## Role
{role}

## Pipeline
{pipeline}

## Timeline

| Date | Event | Notes |
|------|-------|-------|
| {date} | Application submitted | |

## Contact Log

| Date | Person | Channel | Notes |
|------|--------|---------|-------|
| | | | |

## Outcome
<!-- Final result and key learnings -->
"""


def _make_app_folder(tmp_path: Path, folder_name: str, company: str, role: str,
                     pipeline: str, date: str = "2026-05-30") -> Path:
    """Create a minimal application folder with 11_application_log.md."""
    folder = tmp_path / folder_name
    folder.mkdir()
    log = folder / "11_application_log.md"
    log.write_text(
        LOG_TEMPLATE.format(company=company, role=role, pipeline=pipeline, date=date),
        encoding="utf-8",
    )
    return folder


# ---------------------------------------------------------------------------
# 1. test_scan_empty_dir
# ---------------------------------------------------------------------------

def test_scan_empty_dir(tmp_path):
    """scan_applications returns empty list when directory has no subfolders."""
    result = scan_applications(apps_dir=tmp_path)
    assert result == []


# ---------------------------------------------------------------------------
# 2. test_scan_single_application
# ---------------------------------------------------------------------------

def test_scan_single_application(tmp_path):
    """scan_applications correctly reads company, role, pipeline from log file."""
    _make_app_folder(
        tmp_path,
        folder_name="2026_05_30_dewu_growth_product_intern",
        company="得物",
        role="增长产品实习生",
        pipeline="internet_platform",
    )

    apps = scan_applications(apps_dir=tmp_path)

    assert len(apps) == 1
    a = apps[0]
    assert isinstance(a, ApplicationStatus)
    assert a.folder == "2026_05_30_dewu_growth_product_intern"
    assert a.company == "得物"
    assert a.role == "增长产品实习生"
    assert a.pipeline == "internet_platform"
    assert a.date == "2026-05-30"
    assert a.status == "draft"  # default


# ---------------------------------------------------------------------------
# 3. test_update_status_creates_sidecar
# ---------------------------------------------------------------------------

def test_update_status_creates_sidecar(tmp_path):
    """update_status writes tracker_status.json and returns updated ApplicationStatus."""
    _make_app_folder(
        tmp_path,
        folder_name="2026_05_30_dewu_growth_product_intern",
        company="得物",
        role="增长产品实习生",
        pipeline="internet_platform",
    )

    result = update_status(
        folder="2026_05_30_dewu_growth_product_intern",
        status="interview",
        next_action="Prepare for HR interview",
        apps_dir=tmp_path,
    )

    assert isinstance(result, ApplicationStatus)
    assert result.status == "interview"
    assert result.next_action == "Prepare for HR interview"
    assert result.last_updated == date.today().isoformat()

    sidecar = tmp_path / "2026_05_30_dewu_growth_product_intern" / "tracker_status.json"
    assert sidecar.exists()
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    assert data["status"] == "interview"
    assert data["next_action"] == "Prepare for HR interview"
    assert data["last_updated"] == date.today().isoformat()


# ---------------------------------------------------------------------------
# 4. test_update_invalid_status_raises
# ---------------------------------------------------------------------------

def test_update_invalid_status_raises(tmp_path):
    """update_status raises ValueError for an unrecognized status string."""
    _make_app_folder(
        tmp_path,
        folder_name="2026_05_30_dewu_growth_product_intern",
        company="得物",
        role="增长产品实习生",
        pipeline="internet_platform",
    )

    with pytest.raises(ValueError, match="Invalid status"):
        update_status(
            folder="2026_05_30_dewu_growth_product_intern",
            status="Ghosted",  # not a valid status
            apps_dir=tmp_path,
        )


# ---------------------------------------------------------------------------
# 5. test_get_summary_aggregates
# ---------------------------------------------------------------------------

def test_get_summary_aggregates(tmp_path):
    """get_summary correctly aggregates by_status and by_pipeline."""
    _make_app_folder(tmp_path, "2026_05_30_dewu_growth_product_intern",
                     "得物", "增长产品实习生", "internet_platform")
    _make_app_folder(tmp_path, "2026_05_31_bytedance_data_analyst_intern",
                     "ByteDance", "Data Analyst Intern", "internet_platform")
    _make_app_folder(tmp_path, "2026_06_01_catl_supply_chain_intern",
                     "CATL", "Supply Chain Intern", "new_energy")

    # Update two of them
    update_status("2026_05_31_bytedance_data_analyst_intern", "awaiting",
                  apps_dir=tmp_path)
    update_status("2026_06_01_catl_supply_chain_intern", "rejected",
                  apps_dir=tmp_path)

    summary = get_summary(apps_dir=tmp_path)

    assert isinstance(summary, TrackerSummary)
    assert summary.total == 3
    assert summary.by_status["draft"] == 1
    assert summary.by_status["awaiting"] == 1
    assert summary.by_status["rejected"] == 1
    assert summary.by_pipeline["internet_platform"] == 2
    assert summary.by_pipeline["new_energy"] == 1


# ---------------------------------------------------------------------------
# 6. test_track_command (merged list + summary)
# ---------------------------------------------------------------------------

def test_track_command(tmp_path):
    """track CLI command lists applications and shows summary counts."""
    import applysmith.tracker as tracker_mod
    import applysmith.paths as paths_mod

    original_apps_dir = paths_mod.applications_dir

    def patched_apps_dir():
        return tmp_path

    paths_mod.applications_dir = patched_apps_dir
    tracker_mod.applications_dir = patched_apps_dir

    try:
        _make_app_folder(tmp_path, "2026_05_30_dewu_growth_product_intern",
                         "得物", "增长产品实习生", "internet_platform")
        _make_app_folder(tmp_path, "2026_06_01_catl_supply_chain_intern",
                         "CATL", "Supply Chain Intern", "new_energy")

        # List all
        result = runner.invoke(app, ["track"])
        assert result.exit_code == 0, result.output
        assert "得物" in result.output
        assert "CATL" in result.output
        assert "Total: 2" in result.output
        assert "By status:" in result.output

        # Filter by pipeline
        result = runner.invoke(app, ["track", "--pipeline", "internet_platform"])
        assert result.exit_code == 0, result.output
        assert "得物" in result.output
        assert "CATL" not in result.output
        assert "Total: 1" in result.output
    finally:
        paths_mod.applications_dir = original_apps_dir
        tracker_mod.applications_dir = original_apps_dir


# ---------------------------------------------------------------------------
# 7. test_file_completeness
# ---------------------------------------------------------------------------

def test_file_completeness(tmp_path):
    """scan_applications reports which of the 11 standard files are present/missing."""
    from applysmith.tracker import STANDARD_APP_FILES

    folder = _make_app_folder(tmp_path, "2026_05_30_dewu_growth_product_intern",
                               "得物", "增长产品实习生", "internet_platform")

    # Create only 3 of the 11 standard files (11_application_log.md already exists)
    (folder / "01_jd_original.md").write_text("JD", encoding="utf-8")
    (folder / "02_jd_analysis.md").write_text("Analysis", encoding="utf-8")

    apps = scan_applications(apps_dir=tmp_path)
    assert len(apps) == 1
    a = apps[0]

    assert "11_application_log.md" in a.files_complete
    assert "01_jd_original.md" in a.files_complete
    assert "02_jd_analysis.md" in a.files_complete

    # Remaining 8 files should be missing
    for f in STANDARD_APP_FILES:
        if f not in ("11_application_log.md", "01_jd_original.md", "02_jd_analysis.md"):
            assert f in a.files_missing, f"{f} should be in files_missing"

    assert len(a.files_complete) == 3
    assert len(a.files_missing) == 8


# ---------------------------------------------------------------------------
# 8. test_log_appending_on_update
# ---------------------------------------------------------------------------

def test_log_appending_on_update(tmp_path):
    """update_status appends a ## Status Update section to 11_application_log.md."""
    folder = _make_app_folder(tmp_path, "2026_05_30_dewu_growth_product_intern",
                               "得物", "增长产品实习生", "internet_platform")
    log_file = folder / "11_application_log.md"
    original_content = log_file.read_text(encoding="utf-8")

    update_status(
        folder="2026_05_30_dewu_growth_product_intern",
        status="submitted",
        next_action="Wait for response",
        notes="Applied via LinkedIn",
        apps_dir=tmp_path,
    )

    updated_content = log_file.read_text(encoding="utf-8")
    assert updated_content.startswith(original_content.rstrip())
    assert "## Status Update" in updated_content
    assert "**Status:** submitted" in updated_content
    assert "**Next Action:** Wait for response" in updated_content
    assert "**Notes:** Applied via LinkedIn" in updated_content
    assert date.today().isoformat() in updated_content


# ---------------------------------------------------------------------------
# 9. test_weekly_review
# ---------------------------------------------------------------------------

def test_weekly_review(tmp_path):
    """weekly_review returns awaiting/interview apps stale for 7+ days."""
    # App 1: awaiting, last updated 10 days ago → stale
    folder1 = _make_app_folder(tmp_path, "2026_05_24_stale_awaiting",
                                "CompA", "Role A", "pipeline_x")
    stale_date = (date.today() - timedelta(days=10)).isoformat()
    (folder1 / "tracker_status.json").write_text(
        json.dumps({"status": "awaiting", "last_updated": stale_date}),
        encoding="utf-8",
    )

    # App 2: interview, last updated 1 day ago → NOT stale
    folder2 = _make_app_folder(tmp_path, "2026_06_03_fresh_interview",
                                "CompB", "Role B", "pipeline_x")
    fresh_date = (date.today() - timedelta(days=1)).isoformat()
    (folder2 / "tracker_status.json").write_text(
        json.dumps({"status": "interview", "last_updated": fresh_date}),
        encoding="utf-8",
    )

    # App 3: draft → never flagged by weekly_review
    _make_app_folder(tmp_path, "2026_06_01_draft_app",
                     "CompC", "Role C", "pipeline_y")

    stale = weekly_review(apps_dir=tmp_path)

    assert len(stale) == 1
    assert stale[0].folder == "2026_05_24_stale_awaiting"
    assert stale[0].status == "awaiting"


# ---------------------------------------------------------------------------
# 10. test_weekly_review_command
# ---------------------------------------------------------------------------

def test_weekly_review_command(tmp_path):
    """weekly-review CLI command prints stale apps or a clean message."""
    import applysmith.tracker as tracker_mod
    import applysmith.paths as paths_mod

    original_apps_dir = paths_mod.applications_dir

    def patched_apps_dir():
        return tmp_path

    paths_mod.applications_dir = patched_apps_dir
    tracker_mod.applications_dir = patched_apps_dir

    try:
        # No apps at all → clean message
        result = runner.invoke(app, ["weekly-review"])
        assert result.exit_code == 0, result.output
        assert "No stale" in result.output

        # Add a stale awaiting app
        folder = _make_app_folder(tmp_path, "2026_05_24_stale_awaiting",
                                   "CompA", "Role A", "pipeline_x")
        stale_date = (date.today() - timedelta(days=10)).isoformat()
        (folder / "tracker_status.json").write_text(
            json.dumps({"status": "awaiting", "last_updated": stale_date}),
            encoding="utf-8",
        )

        result = runner.invoke(app, ["weekly-review"])
        assert result.exit_code == 0, result.output
        assert "2026_05_24_stale_awaiting" in result.output
        assert "awaiting" in result.output
    finally:
        paths_mod.applications_dir = original_apps_dir
        tracker_mod.applications_dir = original_apps_dir
