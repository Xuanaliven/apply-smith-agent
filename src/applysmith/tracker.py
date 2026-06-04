"""
Application Tracker — scan, update, and summarize application folders.
"""
import json
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from .models import ApplicationStatus, TrackerSummary, VALID_TRACKER_STATUSES
from .paths import applications_dir

# The 11 standard working files created in every application folder.
STANDARD_APP_FILES = [
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
]

_STALE_DAYS = 7  # Flag awaiting/interview apps with no update for this many days.


def _parse_log_section(content: str, section: str) -> str:
    """Extract text content from a '## Section' block in a markdown file."""
    pattern = rf"## {re.escape(section)}\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return ""
    text = match.group(1).strip()
    # Strip HTML comments like <!-- ... -->
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL).strip()
    return text


def _parse_date_from_folder(folder_name: str) -> str:
    """Extract date (YYYY-MM-DD) from a folder name like 2026_05_30_company_role."""
    m = re.match(r"(\d{4})_(\d{2})_(\d{2})", folder_name)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return ""


def scan_applications(
    apps_dir: Optional[Path] = None,
    pipeline_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> List[ApplicationStatus]:
    """
    Scan all application folders and return a list of ApplicationStatus objects.

    Reads metadata from:
      - 11_application_log.md  (company, role, pipeline)
      - tracker_status.json    (status, channel, next_action, notes, last_updated)

    Also checks which of the 11 standard files exist (files_complete / files_missing).
    """
    base = apps_dir or applications_dir()
    if not base.exists():
        return []

    results = []
    for folder in sorted(base.iterdir()):
        if not folder.is_dir():
            continue

        # Read tracker_status.json sidecar if present
        status_file = folder / "tracker_status.json"
        status_data: Dict = {}
        if status_file.exists():
            status_data = json.loads(status_file.read_text(encoding="utf-8"))

        # Parse company / role / pipeline from 11_application_log.md
        company = role = pipeline = ""
        log_file = folder / "11_application_log.md"
        if log_file.exists():
            content = log_file.read_text(encoding="utf-8")
            company = _parse_log_section(content, "Company")
            role = _parse_log_section(content, "Role")
            pipeline = _parse_log_section(content, "Pipeline")

        # Fall back to values stored in tracker_status.json if log is unpopulated
        company = company or status_data.get("company", "")
        role = role or status_data.get("role", "")
        pipeline = pipeline or status_data.get("pipeline", "")

        # File completeness check
        files_complete = [f for f in STANDARD_APP_FILES if (folder / f).exists()]
        files_missing = [f for f in STANDARD_APP_FILES if not (folder / f).exists()]

        app_status = ApplicationStatus(
            folder=folder.name,
            company=company,
            role=role,
            pipeline=pipeline,
            date=_parse_date_from_folder(folder.name),
            channel=status_data.get("channel", ""),
            status=status_data.get("status", "draft"),
            next_action=status_data.get("next_action", ""),
            notes=status_data.get("notes", ""),
            last_updated=status_data.get("last_updated", ""),
            files_complete=files_complete,
            files_missing=files_missing,
        )

        if pipeline_filter and app_status.pipeline != pipeline_filter:
            continue
        if status_filter and app_status.status != status_filter:
            continue

        results.append(app_status)

    return results


def get_summary(apps_dir: Optional[Path] = None) -> TrackerSummary:
    """Aggregate all application statuses into a TrackerSummary."""
    apps = scan_applications(apps_dir)

    by_status: Dict[str, int] = {}
    by_pipeline: Dict[str, int] = {}

    for app in apps:
        by_status[app.status] = by_status.get(app.status, 0) + 1
        if app.pipeline:
            by_pipeline[app.pipeline] = by_pipeline.get(app.pipeline, 0) + 1

    return TrackerSummary(
        total=len(apps),
        by_status=by_status,
        by_pipeline=by_pipeline,
        applications=apps,
    )


def update_status(
    folder: str,
    status: str,
    next_action: Optional[str] = None,
    notes: Optional[str] = None,
    apps_dir: Optional[Path] = None,
) -> ApplicationStatus:
    """
    Write or update tracker_status.json in the application folder.
    Also appends a status update entry to 11_application_log.md.
    Returns the updated ApplicationStatus.
    Raises ValueError for invalid status, FileNotFoundError if folder missing.
    """
    if status not in VALID_TRACKER_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. Must be one of: {sorted(VALID_TRACKER_STATUSES)}"
        )

    base = apps_dir or applications_dir()
    app_folder = base / folder
    if not app_folder.exists():
        raise FileNotFoundError(f"Application folder not found: {app_folder}")

    status_file = app_folder / "tracker_status.json"
    data: Dict = {}
    if status_file.exists():
        data = json.loads(status_file.read_text(encoding="utf-8"))

    today = date.today().isoformat()
    data["status"] = status
    data["last_updated"] = today
    if next_action is not None:
        data["next_action"] = next_action
    if notes is not None:
        data["notes"] = notes

    status_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Append a status update entry to 11_application_log.md
    log_file = app_folder / "11_application_log.md"
    if log_file.exists():
        log_entry_parts = [f"\n## Status Update — {today}", f"**Status:** {status}"]
        if next_action:
            log_entry_parts.append(f"**Next Action:** {next_action}")
        if notes:
            log_entry_parts.append(f"**Notes:** {notes}")
        log_entry = "\n".join(log_entry_parts) + "\n"
        existing = log_file.read_text(encoding="utf-8")
        log_file.write_text(existing + log_entry, encoding="utf-8")

    # Return the fresh ApplicationStatus for this folder
    updated = scan_applications(base)
    for app in updated:
        if app.folder == folder:
            return app

    # Fallback (should not be reached)
    return ApplicationStatus(
        folder=folder,
        company=data.get("company", ""),
        role=data.get("role", ""),
        pipeline=data.get("pipeline", ""),
        date=_parse_date_from_folder(folder),
        channel=data.get("channel", ""),
        status=status,
        next_action=data.get("next_action", ""),
        notes=data.get("notes", ""),
        last_updated=today,
    )


def weekly_review(apps_dir: Optional[Path] = None) -> List[ApplicationStatus]:
    """
    Return applications with status 'awaiting' or 'interview' that have
    had no status update in _STALE_DAYS or more days.
    """
    apps = scan_applications(apps_dir)
    today = date.today()
    stale = []

    for app in apps:
        if app.status not in ("awaiting", "interview"):
            continue

        # Determine the reference date: last_updated, then folder date, then today
        ref_str = app.last_updated or app.date
        if ref_str:
            try:
                ref_date = date.fromisoformat(ref_str)
            except ValueError:
                ref_date = today
        else:
            ref_date = today

        if (today - ref_date) >= timedelta(days=_STALE_DAYS):
            stale.append(app)

    return stale
