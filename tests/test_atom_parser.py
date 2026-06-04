"""
Tests for the experience atoms parser.
"""
import logging

import pytest

from applysmith.atom_parser import parse_atoms, STANDARD_FIELDS


# ---------------------------------------------------------------------------
# 1. test_standard_format
# ---------------------------------------------------------------------------

STANDARD_INPUT = """\
## EXP-001
- experience_name: 产品运营实习
- type: internship
- time_period: 2023-06 to 2023-08
- raw_fact: Maintained a weekly sales report for the ops team
- role: Operations Intern
- action: Pulled data, built dashboard, flagged anomalies
- tool: SQL, Excel
- metric: 30天提升为1天
- evidence: Internship certificate available
- can_be_reused_for: Data Analysis, Operations
- risk_level: Green

## EXP-002
- experience_name: BodyBuilder.ai
- type: self_initiated
- time_period: 2022-01 to 2022-06
- raw_fact: Built an AI fitness app end-to-end
- role: Solo founder
- action: Designed product, integrated ML model, launched MVP
- tool: Python, React
- metric: 全流程0-1独立完成
- evidence: GitHub repo public
- can_be_reused_for: Product Management, AI
- risk_level: Yellow
"""


def test_standard_format():
    """Normal input parses correctly: two atoms with all fields populated."""
    atoms = parse_atoms(STANDARD_INPUT)

    assert len(atoms) == 2

    a1 = atoms[0]
    assert a1["id"] == "EXP-001"
    assert a1["experience_name"] == "产品运营实习"
    assert a1["type"] == "internship"
    assert a1["metric"] == "30天提升为1天"
    assert a1["risk_level"] == "Green"

    a2 = atoms[1]
    assert a2["id"] == "EXP-002"
    assert a2["experience_name"] == "BodyBuilder.ai"
    assert a2["risk_level"] == "Yellow"


# ---------------------------------------------------------------------------
# 2. test_missing_fields
# ---------------------------------------------------------------------------

MISSING_FIELDS_INPUT = """\
## EXP-001
- experience_name: Minimal Entry
- type: internship
"""


def test_missing_fields():
    """Missing fields default to empty string, no crash."""
    atoms = parse_atoms(MISSING_FIELDS_INPUT)

    assert len(atoms) == 1
    a = atoms[0]
    assert a["id"] == "EXP-001"
    assert a["experience_name"] == "Minimal Entry"
    assert a["type"] == "internship"

    # All other standard fields must exist and be empty
    for field in STANDARD_FIELDS:
        assert field in a, f"Field '{field}' missing from atom"
        if field not in ("experience_name", "type"):
            assert a[field] == "", f"Expected empty for '{field}', got {a[field]!r}"


# ---------------------------------------------------------------------------
# 3. test_extra_whitespace
# ---------------------------------------------------------------------------

WHITESPACE_INPUT = """\

## EXP-001

   - experience_name:   Whitespace Test
   - type:   internship


   - metric:   8%

## EXP-002
- experience_name: Second Entry
"""


def test_extra_whitespace():
    """Extra spaces, blank lines, and indentation are handled gracefully."""
    atoms = parse_atoms(WHITESPACE_INPUT)

    assert len(atoms) == 2

    a1 = atoms[0]
    assert a1["experience_name"] == "Whitespace Test"
    assert a1["type"] == "internship"
    assert a1["metric"] == "8%"

    a2 = atoms[1]
    assert a2["experience_name"] == "Second Entry"


# ---------------------------------------------------------------------------
# 4. test_empty_file
# ---------------------------------------------------------------------------

def test_empty_file():
    """Empty or whitespace-only input returns empty list without crashing."""
    assert parse_atoms("") == []
    assert parse_atoms("   \n\n   ") == []
    assert parse_atoms("\t") == []


# ---------------------------------------------------------------------------
# 5. test_malformed_entry
# ---------------------------------------------------------------------------

MALFORMED_INPUT = """\
## EXP-001
- experience_name: Valid Entry
- type: internship
- totally_wrong_field: some garbage value
- metric: 5%
"""


def test_malformed_entry(caplog):
    """Unrecognized fields log a warning but do not crash; valid fields still parsed."""
    with caplog.at_level(logging.WARNING, logger="applysmith.atom_parser"):
        atoms = parse_atoms(MALFORMED_INPUT)

    assert len(atoms) == 1
    a = atoms[0]
    assert a["experience_name"] == "Valid Entry"
    assert a["metric"] == "5%"
    # Unrecognized field should NOT be in the atom
    assert "totally_wrong_field" not in a

    # A warning should have been logged
    assert any("totally_wrong_field" in msg for msg in caplog.messages), (
        f"Expected warning for 'totally_wrong_field', got: {caplog.messages}"
    )
