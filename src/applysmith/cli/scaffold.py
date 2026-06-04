"""
Scaffold commands: hello, init, new-pipeline, new-application, new-company-dossier.
"""
import typer

from . import app
from ..paths import is_initialized, get_root
from ..package_generator import (
    initialize_project,
    create_pipeline,
    create_application,
    create_company_dossier as _create_company_dossier,
)
from ..onboarding import run_onboarding


@app.command()
def hello():
    """Check that ApplySmith is installed and ready."""
    typer.echo("ApplySmith is ready.")


@app.command()
def init():
    """Initialize ApplySmith in the current directory."""
    if is_initialized():
        typer.echo("ApplySmith is already initialized in this directory.")
        raise typer.Exit(1)

    answers = run_onboarding()
    initialize_project(answers)

    typer.echo("\nApplySmith initialized successfully!")
    typer.echo(f"  Root directory : {get_root()}")
    typer.echo(f"  Pipelines created: {len(answers.get('industries', []))}")
    typer.echo("\nNext steps:")
    typer.echo("  1. Fill in data/master_profile/profile_questions.md")
    typer.echo("  2. Add your experience atoms to data/master_profile/experience_atoms.md")
    typer.echo("  3. Review your pipelines in pipelines/")
    typer.echo("  4. Run: applysmith new-application --help")


@app.command(name="new-pipeline")
def new_pipeline(
    name: str = typer.Option(..., help="Pipeline name (used as filename slug)"),
    industry: str = typer.Option(..., help="Target industry"),
    role_category: str = typer.Option(..., help="Target role category"),
):
    """Create a new career pipeline."""
    try:
        path = create_pipeline(name, industry, role_category)
        typer.echo(f"Pipeline created: {path}")
    except FileExistsError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)


@app.command(name="new-application")
def new_application(
    company: str = typer.Option(..., help="Company name"),
    role: str = typer.Option(..., help="Role title"),
    date: str = typer.Option(..., help="Application date in YYYY-MM-DD format"),
    channel: str = typer.Option(..., help="Application channel (e.g., campus portal, LinkedIn, referral)"),
    pipeline: str = typer.Option(..., help="Pipeline name this application belongs to"),
):
    """Create a new application folder with all 11 working files."""
    try:
        folder = create_application(company, role, date, channel, pipeline)
        typer.echo(f"Application folder created: {folder}")
        typer.echo("  11 working files generated. Start with 01_jd_original.md.")
    except FileExistsError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)


@app.command(name="new-company-dossier")
def new_company_dossier(
    company: str = typer.Option(..., help="Company name"),
    industry: str = typer.Option(..., help="Industry"),
    ticker: str = typer.Option(None, help="Stock ticker (optional)"),
):
    """Create a new company dossier."""
    try:
        path = _create_company_dossier(company, industry, ticker)
        typer.echo(f"Company dossier created: {path}")
    except FileExistsError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)
