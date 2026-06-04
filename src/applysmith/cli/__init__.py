"""
ApplySmith CLI — Career Strategy OS for job seekers.
"""
import typer

app = typer.Typer(help="ApplySmith — Career Strategy OS for job seekers")

# Import submodules after defining app — each one registers its commands via @app.command()
from . import scaffold  # noqa: F401, E402
from . import analysis  # noqa: F401, E402
from . import generation  # noqa: F401, E402
from . import tracker  # noqa: F401, E402
from . import signals  # noqa: F401, E402

__all__ = ["app"]
