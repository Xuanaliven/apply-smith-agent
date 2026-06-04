"""
Tests for company_dossier.py — all run in a tmp_path with APPLYSMITH_ROOT set.
"""
import pytest


@pytest.fixture(autouse=True)
def set_root(tmp_path, monkeypatch):
    """Point APPLYSMITH_ROOT at tmp_path for every test in this module."""
    monkeypatch.setenv("APPLYSMITH_ROOT", str(tmp_path))
    return tmp_path


def test_create_dossier(tmp_path):
    from applysmith.company_dossier import create_dossier

    path = create_dossier("Tencent", "Internet / Platform", ticker="0700.HK")
    assert path.exists()
    assert path.name == "Tencent.md"

    content = path.read_text(encoding="utf-8")
    assert "# Company Dossier: Tencent" in content
    assert "Internet / Platform" in content
    assert "0700.HK" in content
    assert "## Business Segments" in content
    assert "## Public Sources" in content
    assert "## Social / Employee Signals" in content
    assert "## Resume Strategy" in content
    assert "## Risk Notes" in content


def test_create_dossier_no_ticker(tmp_path):
    from applysmith.company_dossier import create_dossier

    path = create_dossier("CATL", "New Energy / EV")
    content = path.read_text(encoding="utf-8")
    assert "N/A" in content


def test_no_overwrite_dossier(tmp_path):
    from applysmith.company_dossier import create_dossier

    create_dossier("Meituan", "Internet / Platform", ticker="3690.HK")

    with pytest.raises(FileExistsError):
        create_dossier("Meituan", "Internet / Platform", ticker="3690.HK")
