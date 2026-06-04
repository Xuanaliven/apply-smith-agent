"""
Tracker commands: track, track-update, track-pipeline, weekly-review.
"""
from typing import Optional

import typer

from . import app


@app.command(name="track")
def track_cmd(
    pipeline: Optional[str] = typer.Option(None, "--pipeline", help="Filter by pipeline name"),
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status"),
):
    """List applications and show summary counts."""
    from ..tracker import scan_applications, get_summary

    apps = scan_applications(pipeline_filter=pipeline, status_filter=status)

    if not apps:
        typer.echo("No applications found.")
        return

    # Table
    header = f"{'Folder':<45} {'Status':<12} {'Company':<20} {'Role':<30} {'Pipeline'}"
    typer.echo(header)
    typer.echo("-" * len(header))
    for a in apps:
        typer.echo(
            f"{a.folder:<45} {a.status:<12} {a.company:<20} {a.role:<30} {a.pipeline}"
        )

    typer.echo(f"\nTotal: {len(apps)}")

    # Summary counts (always from unfiltered set so totals are meaningful)
    summary = get_summary()
    typer.echo("\nBy status:")
    for s, count in sorted(summary.by_status.items()):
        typer.echo(f"  {s:<20} {count}")

    if summary.by_pipeline:
        typer.echo("\nBy pipeline:")
        for p, count in sorted(summary.by_pipeline.items()):
            typer.echo(f"  {p:<30} {count}")


@app.command(name="track-update")
def track_update_cmd(
    app_folder: str = typer.Option(..., "--app", help="Application folder name or path"),
    status: str = typer.Option(..., "--status", help="New status"),
    next_action: Optional[str] = typer.Option(None, "--next-action", help="Next action note"),
    notes: Optional[str] = typer.Option(None, "--notes", help="Additional notes"),
):
    """Update the status of an application."""
    from ..tracker import update_status
    from pathlib import Path as _Path

    folder_name = _Path(app_folder).name

    try:
        result = update_status(folder_name, status, next_action=next_action, notes=notes)
    except (ValueError, FileNotFoundError) as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)

    typer.echo(f"Updated: {result.folder}")
    typer.echo(f"  Status: {result.status}")
    if result.next_action:
        typer.echo(f"  Next action: {result.next_action}")
    if result.notes:
        typer.echo(f"  Notes: {result.notes}")
    if result.last_updated:
        typer.echo(f"  Last updated: {result.last_updated}")


@app.command(name="track-pipeline")
def track_pipeline_cmd(
    pipeline: str = typer.Option(..., "--pipeline", help="Pipeline name to inspect"),
):
    """Show all applications in a specific pipeline."""
    from ..tracker import scan_applications

    apps = scan_applications(pipeline_filter=pipeline)

    if not apps:
        typer.echo(f"No applications found for pipeline: {pipeline}")
        return

    typer.echo(f"Pipeline: {pipeline}  ({len(apps)} applications)\n")
    for a in apps:
        typer.echo(f"  [{a.status}] {a.company} — {a.role}")
        if a.next_action:
            typer.echo(f"    Next: {a.next_action}")
        if a.date:
            typer.echo(f"    Date: {a.date}")


@app.command(name="weekly-review")
def weekly_review_cmd():
    """Flag awaiting/interview applications with no update in 7+ days."""
    from ..tracker import weekly_review

    stale = weekly_review()

    if not stale:
        typer.echo("No stale applications. All awaiting/interview apps are up to date.")
        return

    typer.echo(f"Stale applications ({len(stale)} found — no update in 7+ days):\n")
    for a in stale:
        typer.echo(f"  [{a.status}] {a.folder}")
        typer.echo(f"    Company:      {a.company}")
        typer.echo(f"    Role:         {a.role}")
        typer.echo(f"    Last updated: {a.last_updated or a.date or 'unknown'}")
        if a.next_action:
            typer.echo(f"    Next action:  {a.next_action}")
        typer.echo()
