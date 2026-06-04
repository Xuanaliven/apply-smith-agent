from pathlib import Path
from .paths import company_dossiers_dir
from .templates import company_dossier_template


def create_dossier(company: str, industry: str, ticker: str | None = None) -> Path:
    """Create a company dossier file. Raises FileExistsError if already exists."""
    dossier_dir = company_dossiers_dir()
    dossier_dir.mkdir(parents=True, exist_ok=True)
    file_path = dossier_dir / f"{company}.md"
    if file_path.exists():
        raise FileExistsError(f"Dossier already exists: {file_path}")
    content = company_dossier_template(company, industry, ticker)
    file_path.write_text(content, encoding="utf-8")
    return file_path
