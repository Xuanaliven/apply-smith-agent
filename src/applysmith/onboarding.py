"""
Interactive CLI onboarding for ApplySmith.
"""
import typer
from typing import List

STAGE_OPTIONS = [
    "Summer internship",
    "Autumn recruiting (秋招)",
    "Spring recruiting (春招)",
    "Social recruiting (社招)",
    "Career change",
]

INDUSTRY_OPTIONS = [
    "Internet / Platform",
    "E-commerce",
    "New Energy / EV / Photovoltaic",
    "Finance / Securities / Fund",
    "Consulting / Strategy",
    "Manufacturing / Supply Chain",
    "State-owned Enterprise / Digital Transformation",
    "Defense / Aerospace",
    "Healthcare / Biotech",
    "Consumer Goods / Retail",
    "Other",
]

ROLE_OPTIONS = [
    "Operations (User / Content / Activity)",
    "Advertising / Marketing",
    "Data Analysis / Business Analysis",
    "Product Management",
    "Industry Research / Strategy",
    "Supply Chain / Procurement",
    "Finance / Accounting",
    "Sales / BD",
    "Other",
]


def ask_stage() -> str:
    """Ask Q1: recruiting stage."""
    typer.echo("\nQ1. What is your recruiting stage?")
    for i, option in enumerate(STAGE_OPTIONS, 1):
        typer.echo(f"  {i}. {option}")

    while True:
        raw = typer.prompt("Enter the number of your stage").strip()
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(STAGE_OPTIONS):
                return STAGE_OPTIONS[idx - 1]
        typer.echo(f"  Please enter a number between 1 and {len(STAGE_OPTIONS)}.")


def ask_multi_select(prompt: str, options: List[str]) -> List[str]:
    """
    Generic multi-select: show numbered list, accept comma-separated numbers.
    If "Other" is selected, prompt for a custom value.
    """
    typer.echo(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        typer.echo(f"  {i}. {option}")

    while True:
        raw = typer.prompt("Enter numbers separated by commas (e.g. 1,3,5)").strip()
        raw = raw.replace("，", ",")
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        valid = True
        selected_indices = []
        for p in parts:
            if p.isdigit():
                idx = int(p)
                if 1 <= idx <= len(options):
                    selected_indices.append(idx)
                else:
                    typer.echo(f"  '{p}' is out of range. Please use numbers 1-{len(options)}.")
                    valid = False
                    break
            else:
                typer.echo(f"  '{p}' is not a valid number.")
                valid = False
                break

        if not valid or not selected_indices:
            if not selected_indices:
                typer.echo("  Please select at least one option.")
            continue

        selected_values = []
        for idx in selected_indices:
            val = options[idx - 1]
            if val == "Other":
                custom = typer.prompt("  You selected 'Other' — please type your custom value").strip()
                if custom:
                    selected_values.append(custom)
                else:
                    typer.echo("  Custom value cannot be empty.")
                    valid = False
                    break
            else:
                selected_values.append(val)

        if valid and selected_values:
            return selected_values


def ask_company_count() -> int:
    """Ask Q4: number of target companies."""
    typer.echo("\nQ4. How many target companies are you tracking? (Enter a number, e.g. 10)")
    while True:
        raw = typer.prompt("Number of target companies").strip()
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        typer.echo("  Please enter a positive integer.")


def run_onboarding() -> dict:
    """
    Run the full onboarding questionnaire and return an answers dict.

    Returns:
        {
            "stage": str,
            "industries": List[str],
            "roles": List[str],
            "company_count": int,
        }
    """
    typer.echo("\n" + "=" * 60)
    typer.echo("  Welcome to ApplySmith — Career Strategy OS")
    typer.echo("  Let's set up your recruiting strategy.")
    typer.echo("=" * 60)

    stage = ask_stage()

    industries = ask_multi_select(
        "Q2. Which industries are you targeting? (Select all that apply)",
        INDUSTRY_OPTIONS,
    )

    roles = ask_multi_select(
        "Q3. Which role categories are you targeting? (Select all that apply)",
        ROLE_OPTIONS,
    )

    company_count = ask_company_count()

    typer.echo("\n" + "-" * 60)
    typer.echo("  Onboarding summary:")
    typer.echo(f"  Stage        : {stage}")
    typer.echo(f"  Industries   : {', '.join(industries)}")
    typer.echo(f"  Roles        : {', '.join(roles)}")
    typer.echo(f"  Company count: {company_count}")
    typer.echo("-" * 60 + "\n")

    return {
        "stage": stage,
        "industries": industries,
        "roles": roles,
        "company_count": company_count,
    }
