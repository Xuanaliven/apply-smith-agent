import os
from pathlib import Path


def get_root() -> Path:
    env_root = os.environ.get("APPLYSMITH_ROOT")
    if env_root:
        return Path(env_root)
    return Path.cwd()


def data_dir() -> Path:
    return get_root() / "data"


def master_profile_dir() -> Path:
    return data_dir() / "master_profile"


def industry_maps_dir() -> Path:
    return data_dir() / "industry_maps"


def role_schemas_dir() -> Path:
    return data_dir() / "role_schemas"


def capability_roadmaps_dir() -> Path:
    return data_dir() / "capability_roadmaps"


def company_dossiers_dir() -> Path:
    return data_dir() / "company_dossiers"


def company_sources_dir() -> Path:
    return data_dir() / "company_sources"


def question_bank_dir() -> Path:
    return data_dir() / "question_bank"


def external_signals_dir() -> Path:
    return data_dir() / "external_signals"


def pipelines_dir() -> Path:
    return get_root() / "pipelines"


def strategy_dir() -> Path:
    return get_root() / "strategy"


def applications_dir() -> Path:
    return get_root() / "applications"


INIT_MARKER = ".applysmith_initialized"


def is_initialized() -> bool:
    return (get_root() / INIT_MARKER).exists()


def mark_initialized() -> None:
    (get_root() / INIT_MARKER).touch()
