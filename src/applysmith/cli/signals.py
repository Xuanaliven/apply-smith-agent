"""
Signal commands: import-signal.
"""
import typer

from . import app


@app.command(name="import-signal")
def import_signal_cmd(
    file: str = typer.Option(..., help="Path to the signal file to import"),
    pipeline: str = typer.Option(..., help="Pipeline name to link this signal to"),
):
    """Import an external signal file into the project."""
    from ..package_generator import import_signal

    try:
        dest = import_signal(file, pipeline)
        typer.echo(f"Signal imported: {dest}")
        typer.echo(f"  Linked to pipeline: {pipeline}")
    except FileNotFoundError as e:
        typer.echo(f"Error: Source file not found — {e}")
        raise typer.Exit(1)
    except FileExistsError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)
