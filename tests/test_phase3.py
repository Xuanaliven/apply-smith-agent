"""
Phase 3 tests — resume generator, claim checker, and CLI commands.
No real API calls: call_llm is always mocked.
"""
import json
from unittest.mock import patch

from typer.testing import CliRunner

from applysmith.cli import app
from applysmith.resume_generator import generate_resume
from applysmith.claim_checker import check_claims
from applysmith.metric_extractor import extract_metrics
from applysmith.models import (
    ExperienceMatch,
    ExperienceSelectionResult,
    IdealCandidate,
    TailoredResume,
    ClaimCheckReport,
    ResumeBullet,
)

runner = CliRunner()

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

IDEAL = IdealCandidate(
    role_type="Growth PM",
    background_summary="3+ years PM, growth focus.",
    must_have_experiences=["Led A/B experiments"],
    nice_to_have_experiences=["E-commerce background"],
    must_have_skills=["SQL", "A/B testing"],
    differentiators=["TikTok familiarity"],
    red_line_filters=["No PM experience"],
)

SELECTION = ExperienceSelectionResult(
    included=[
        ExperienceMatch(
            experience_id="exp_001",
            experience_name="Growth experiment at Acme",
            match_level="Strong",
            why_matched="Matches A/B testing requirement",
            suggested_angle="Frame as funnel optimization",
            risk_notes="",
        )
    ],
    excluded=[
        ExperienceMatch(
            experience_id="exp_002",
            experience_name="Hardware supply chain",
            match_level="Irrelevant",
            why_matched="Not relevant",
            suggested_angle="",
            risk_notes="",
        )
    ],
    packaging_notes="Lead with growth experiments.",
    capability_gaps=["No TikTok experience"],
)

MOCK_RESUME = {
    "target_role": "Growth PM",
    "target_company": "ByteDance",
    "summary_statement": "Data-driven PM with 3 years of growth experience.",
    "bullets": [
        {
            "experience_name": "Growth experiment at Acme",
            "bullet_text": "Drove 18% increase in D30 retention by redesigning onboarding A/B tests.",
            "claim_level": "Green",
            "evidence": "Retention uplift measured in company analytics dashboard.",
            "interview_risk": "May be asked for exact experiment details.",
            "recommended_action": "Prepare specific experiment setup and results.",
            "metric_source": "Retention uplift: 18% increase in D30 measured in analytics dashboard.",
        }
    ],
    "packaging_notes": "Lead with retention and growth metrics.",
}

MOCK_CLAIM_CHECK = {
    "bullets": [
        {
            "experience_name": "Growth experiment at Acme",
            "bullet_text": "Drove 18% increase in D30 retention by redesigning onboarding A/B tests.",
            "claim_level": "Yellow",
            "evidence": "Dashboard data available but not externally verifiable.",
            "interview_risk": "Interviewer may push for statistical significance details.",
            "recommended_action": "Prepare sample size and confidence interval.",
            "metric_source": "Retention uplift: 18% increase in D30 measured in analytics dashboard.",
        }
    ],
    "overall_risk": "Low",
    "summary": "Resume is mostly defensible. One bullet needs supporting data for interview.",
}


# ---------------------------------------------------------------------------
# 1. test_resume_generator_mock
# ---------------------------------------------------------------------------

def test_resume_generator_mock():
    """TailoredResume is correctly parsed from mocked LLM JSON response."""
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_RESUME)):
        result = generate_resume(SELECTION, IDEAL, "Growth PM", "ByteDance")

    assert isinstance(result, TailoredResume)
    assert result.target_role == "Growth PM"
    assert result.target_company == "ByteDance"
    assert len(result.bullets) == 1
    assert result.bullets[0].claim_level == "Green"


# ---------------------------------------------------------------------------
# 2. test_claim_checker_mock
# ---------------------------------------------------------------------------

def test_claim_checker_mock():
    """ClaimCheckReport is correctly parsed from mocked LLM JSON response."""
    resume = TailoredResume(**MOCK_RESUME)

    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_CLAIM_CHECK)):
        result = check_claims(resume)

    assert isinstance(result, ClaimCheckReport)
    assert result.overall_risk == "Low"
    assert len(result.bullets) == 1
    assert result.bullets[0].claim_level == "Yellow"


# ---------------------------------------------------------------------------
# 3. test_generate_resume_command
# ---------------------------------------------------------------------------

def test_generate_resume_command(tmp_path):
    """generate-resume writes 07_tailored_resume.md and .json correctly."""
    (tmp_path / "05_ideal_candidate.json").write_text(IDEAL.model_dump_json(), encoding="utf-8")
    (tmp_path / "06_selected_experiences.json").write_text(SELECTION.model_dump_json(), encoding="utf-8")

    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_RESUME)):
        result = runner.invoke(
            app,
            ["generate-resume", "--app", str(tmp_path), "--company", "ByteDance", "--role", "Growth PM"],
        )

    assert result.exit_code == 0, result.output
    md = tmp_path / "07_tailored_resume.md"
    assert md.exists()
    content = md.read_text(encoding="utf-8")
    assert "## Target Role" in content
    assert "Growth PM at ByteDance" in content
    assert "Generated by ApplySmith" in content
    assert (tmp_path / "07_tailored_resume.json").exists()
    assert "1 bullets" in result.output


# ---------------------------------------------------------------------------
# 4. test_check_claims_command
# ---------------------------------------------------------------------------

def test_check_claims_command(tmp_path):
    """check-claims writes 08_claim_check_report.md and .json correctly."""
    resume = TailoredResume(**MOCK_RESUME)
    (tmp_path / "07_tailored_resume.json").write_text(resume.model_dump_json(), encoding="utf-8")

    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(MOCK_CLAIM_CHECK)):
        result = runner.invoke(app, ["check-claims", "--app", str(tmp_path)])

    assert result.exit_code == 0, result.output
    md = tmp_path / "08_claim_check_report.md"
    assert md.exists()
    content = md.read_text(encoding="utf-8")
    assert "## Overall Risk: Low" in content
    assert "Generated by ApplySmith" in content
    assert (tmp_path / "08_claim_check_report.json").exists()
    assert "Overall risk: Low" in result.output


# ---------------------------------------------------------------------------
# 5. test_claim_levels
# ---------------------------------------------------------------------------

def test_claim_levels(tmp_path):
    """All 5 claim levels appear in the correct sections of the report."""
    resume = TailoredResume(**MOCK_RESUME)
    (tmp_path / "07_tailored_resume.json").write_text(resume.model_dump_json(), encoding="utf-8")

    all_levels_check = {
        "bullets": [
            {
                "experience_name": "exp A",
                "bullet_text": "Bullet Green",
                "claim_level": "Green",
                "evidence": "e",
                "interview_risk": "",
                "recommended_action": "",
            },
            {
                "experience_name": "exp B",
                "bullet_text": "Bullet Yellow",
                "claim_level": "Yellow",
                "evidence": "e",
                "interview_risk": "r",
                "recommended_action": "a",
            },
            {
                "experience_name": "exp C",
                "bullet_text": "Bullet Red",
                "claim_level": "Red",
                "evidence": "e",
                "interview_risk": "r",
                "recommended_action": "a",
            },
            {
                "experience_name": "exp D",
                "bullet_text": "Bullet Buildable",
                "claim_level": "Buildable",
                "evidence": "e",
                "interview_risk": "",
                "recommended_action": "build it",
            },
            {
                "experience_name": "exp E",
                "bullet_text": "Bullet Stretch",
                "claim_level": "Stretch",
                "evidence": "e",
                "interview_risk": "r",
                "recommended_action": "a",
            },
        ],
        "overall_risk": "High",
        "summary": "Mixed bag.",
    }

    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(all_levels_check)):
        result = runner.invoke(app, ["check-claims", "--app", str(tmp_path)])

    assert result.exit_code == 0, result.output
    content = (tmp_path / "08_claim_check_report.md").read_text(encoding="utf-8")
    assert "Green Claims" in content
    assert "Yellow Claims" in content
    assert "Red Claims" in content
    assert "Buildable Claims" in content
    assert "Stretch Claims" in content
    # Count summary line
    assert "Green: 1" in result.output
    assert "Yellow: 1" in result.output
    assert "Red: 1" in result.output


# ---------------------------------------------------------------------------
# 6. test_metric_whitelist_extraction
# ---------------------------------------------------------------------------

SAMPLE_ATOMS = """\
# Experience Atoms

## EXP-001
- experience_name: 产品运营实习
- metric: 商单数据更新时间由30天提升为1天

## EXP-002
- experience_name: 数据运营实习
- metric: 东莞区域月度销售额增长8%；库存过期损耗降低5%

## EXP-003
- experience_name: BodyBuilder.ai
- metric: 全流程0-1独立完成

## EXP-004
- experience_name: 硕士课程项目
- metric: GPA未提及
"""


def test_metric_whitelist_extraction():
    """extract_metrics correctly parses metric tokens per experience."""
    wl = extract_metrics(SAMPLE_ATOMS)

    assert set(wl.keys()) == {"EXP-001", "EXP-002", "EXP-003", "EXP-004"}

    # EXP-001: "30天" and "1天"
    exp001_digits = {t for t in wl["EXP-001"]}
    assert any("30" in t for t in exp001_digits), f"Expected 30-based token, got {exp001_digits}"
    assert any("1" in t for t in exp001_digits), f"Expected 1-based token, got {exp001_digits}"

    # EXP-002: "8%" and "5%"
    assert any("8" in t for t in wl["EXP-002"])
    assert any("5" in t for t in wl["EXP-002"])

    # EXP-003 and EXP-004 have no numeric metrics
    assert wl["EXP-003"] == [], f"Expected empty, got {wl['EXP-003']}"
    assert wl["EXP-004"] == [], f"Expected empty, got {wl['EXP-004']}"


# ---------------------------------------------------------------------------
# 7. test_whitelist_enforced
# ---------------------------------------------------------------------------

# Selection with EXP-001 (allowed: "30天", "1天" → digits {"30","1"})
_SELECTION_FOR_WHITELIST = ExperienceSelectionResult(
    included=[
        ExperienceMatch(
            experience_id="EXP-001",
            experience_name="产品运营实习",
            match_level="Strong",
            why_matched="Data pipeline work",
            suggested_angle="Frame as efficiency gain",
            risk_notes="",
        )
    ],
    excluded=[],
    packaging_notes="Lead with data.",
    capability_gaps=[],
)

_IDEAL_FOR_WHITELIST = IdealCandidate(
    role_type="Growth PM",
    background_summary="Data-driven PM.",
    must_have_experiences=["Data analysis"],
    nice_to_have_experiences=[],
    must_have_skills=["SQL"],
    differentiators=[],
    red_line_filters=[],
)

# LLM returns a bullet with fabricated "50+" (not in EXP-001 whitelist {30, 1})
_MOCK_RESUME_FABRICATED = {
    "target_role": "Growth PM",
    "target_company": "TestCo",
    "summary_statement": "Experienced candidate.",
    "bullets": [
        {
            "experience_name": "产品运营实习",
            "bullet_text": "Built 50+ dashboards reducing report time by 80%.",
            "claim_level": "Green",
            "evidence": "Project artifacts",
            "interview_risk": "May be challenged",
            "recommended_action": "Prepare details",
            "metric_source": "商单数据更新时间由30天提升为1天",
        }
    ],
    "packaging_notes": "Lead with data.",
}

_WHITELIST = {"EXP-001": ["30天", "1天"], "EXP-002": ["8%", "5%"], "EXP-003": [], "EXP-004": []}


def test_whitelist_enforced():
    """Bullets with fabricated numbers are flagged Red and numbers are stripped."""
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(_MOCK_RESUME_FABRICATED)):
        result = generate_resume(
            _SELECTION_FOR_WHITELIST,
            _IDEAL_FOR_WHITELIST,
            "Growth PM",
            "TestCo",
            metric_whitelist=_WHITELIST,
        )

    assert len(result.bullets) == 1
    bullet = result.bullets[0]

    # claim_level must be overridden to Red
    assert bullet.claim_level == "Red", f"Expected Red, got {bullet.claim_level}"

    # Fabricated numbers must be stripped from bullet_text
    import re
    remaining_nums = re.findall(r"\d+", bullet.bullet_text)
    allowed = {"30", "1"}
    fabricated_remaining = [n for n in remaining_nums if n not in allowed]
    assert not fabricated_remaining, (
        f"Fabricated numbers still in bullet: {fabricated_remaining}\n"
        f"Bullet text: {bullet.bullet_text}"
    )


# ---------------------------------------------------------------------------
# 8. test_metric_source_required_when_numbers_present
# ---------------------------------------------------------------------------

_ATOMS_SAMPLE = """\
## EXP-001
- experience_name: 产品运营实习
- metric: 退货率降低1.2%
"""

# Separate atoms sample for coupon / context-swap tests
_ATOMS_COUPON = """\
## EXP-004
- experience_name: O2O补贴策略
- metric: 核销率仅2.91%
"""

# Atoms sample for report-time context-swap test
_ATOMS_REPORT = """\
## EXP-003
- experience_name: 财务BP专员
- metric: 核算耗时从每日约1小时压缩至10分钟
"""

_SELECTION_SOURCE = ExperienceSelectionResult(
    included=[
        ExperienceMatch(
            experience_id="EXP-001",
            experience_name="产品运营实习",
            match_level="Strong",
            why_matched="Direct ops match",
            suggested_angle="Frame as efficiency gain",
            risk_notes="",
        )
    ],
    excluded=[],
    packaging_notes="Lead with data.",
    capability_gaps=[],
)

_IDEAL_SOURCE = IdealCandidate(
    role_type="Ops",
    background_summary="Operations background.",
    must_have_experiences=["Data analysis"],
    nice_to_have_experiences=[],
    must_have_skills=["SQL"],
    differentiators=[],
    red_line_filters=[],
)


def test_metric_source_required_when_numbers_present():
    """bullet with number but empty metric_source → Red."""
    mock = {
        "target_role": "Ops",
        "target_company": "TestCo",
        "summary_statement": "Experienced ops candidate.",
        "bullets": [{
            "experience_name": "产品运营实习",
            "bullet_text": "Reduced return rate by 2% through optimization.",
            "claim_level": "Green",
            "evidence": "Project data",
            "interview_risk": "May be challenged",
            "recommended_action": "Prepare details",
            "metric_source": "",  # EMPTY — should trigger Red
        }],
        "packaging_notes": "Lead with results.",
    }
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(mock)):
        result = generate_resume(
            _SELECTION_SOURCE, _IDEAL_SOURCE, "Ops", "TestCo",
            metric_whitelist={"EXP-001": ["1.2%"]},
            atoms_raw=_ATOMS_SAMPLE,
        )
    assert result.bullets[0].claim_level == "Red"
    assert "METRIC SOURCE MISSING" in result.bullets[0].interview_risk


# ---------------------------------------------------------------------------
# 9. test_metric_source_numbers_in_atoms
# ---------------------------------------------------------------------------

def test_metric_source_numbers_in_atoms():
    """Step 2: number in metric_source (91) not found in atoms (only 2.91) → Red."""
    _sel = ExperienceSelectionResult(
        included=[ExperienceMatch(
            experience_id="EXP-004", experience_name="O2O补贴策略",
            match_level="Strong", why_matched="Coupon ops", suggested_angle="", risk_notes="",
        )],
        excluded=[], packaging_notes="Lead with data.", capability_gaps=[],
    )
    _ideal = IdealCandidate(
        role_type="Ops", background_summary="Ops background.",
        must_have_experiences=[], nice_to_have_experiences=[],
        must_have_skills=[], differentiators=[], red_line_filters=[],
    )
    mock = {
        "target_role": "Ops",
        "target_company": "TestCo",
        "summary_statement": "Experienced candidate.",
        "bullets": [{
            "experience_name": "O2O补贴策略",
            "bullet_text": "Designed coupon strategy achieving 91% redemption rate.",
            "claim_level": "Green",
            "evidence": "Project report",
            "interview_risk": "",
            "recommended_action": "",
            # 91 does NOT exist in atoms — atoms only has 2.91
            "metric_source": "核销率提升至91%",
        }],
        "packaging_notes": "Lead with results.",
    }
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(mock)):
        result = generate_resume(
            _sel, _ideal, "Ops", "TestCo",
            metric_whitelist={"EXP-004": ["2.91%"]},
            atoms_raw=_ATOMS_COUPON,
        )
    assert result.bullets[0].claim_level == "Red"
    assert "NOT IN ATOMS" in result.bullets[0].interview_risk


# ---------------------------------------------------------------------------
# 10. test_metric_in_bullet_must_be_in_source
# ---------------------------------------------------------------------------

def test_metric_in_bullet_must_be_in_source():
    """bullet has '2%' but metric_source contains '1.2%' only → Red."""
    mock = {
        "target_role": "Ops",
        "target_company": "TestCo",
        "summary_statement": "Experienced candidate.",
        "bullets": [{
            "experience_name": "产品运营实习",
            "bullet_text": "Reduced return rate by 2%.",  # 2 is not in source
            "claim_level": "Green",
            "evidence": "Project data",
            "interview_risk": "",
            "recommended_action": "",
            "metric_source": "退货率比发布当月降低 1.2%",  # verbatim in atoms, but "2" mismatch
        }],
        "packaging_notes": "Lead with results.",
    }
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(mock)):
        result = generate_resume(
            _SELECTION_SOURCE, _IDEAL_SOURCE, "Ops", "TestCo",
            metric_whitelist={"EXP-001": ["1.2%"]},
            atoms_raw=_ATOMS_SAMPLE,
        )
    # "2" from "2%" is absent from metric_source "退货率比发布当月降低 1.2%"
    assert result.bullets[0].claim_level == "Red"
    assert "MISMATCH" in result.bullets[0].interview_risk or "MISSING" in result.bullets[0].interview_risk


# ---------------------------------------------------------------------------
# 11. test_no_numbers_no_source_required
# ---------------------------------------------------------------------------

def test_no_numbers_no_source_required():
    """bullet without numbers and empty metric_source → OK (not flagged Red)."""
    mock = {
        "target_role": "Ops",
        "target_company": "TestCo",
        "summary_statement": "Experienced candidate.",
        "bullets": [{
            "experience_name": "产品运营实习",
            "bullet_text": "Led cross-functional process redesign initiative.",
            "claim_level": "Green",
            "evidence": "Project outcomes",
            "interview_risk": "",
            "recommended_action": "",
            "metric_source": "",  # OK — no numbers in bullet
        }],
        "packaging_notes": "Lead with results.",
    }
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(mock)):
        result = generate_resume(
            _SELECTION_SOURCE, _IDEAL_SOURCE, "Ops", "TestCo",
            metric_whitelist={"EXP-001": ["1.2%"]},
            atoms_raw=_ATOMS_SAMPLE,
        )
    assert result.bullets[0].claim_level == "Green"


# ---------------------------------------------------------------------------
# 12. test_correct_attribution_passes
# ---------------------------------------------------------------------------

def test_correct_attribution_passes():
    """Paraphrased metric_source that shares keywords with atoms → Green.
    metric_source says '退货率减少了1.2%' (paraphrase); atoms says '退货率降低1.2%'.
    Shared keyword '退货率' (3-char CJK n-gram) satisfies Step 3."""
    mock = {
        "target_role": "Ops",
        "target_company": "TestCo",
        "summary_statement": "Experienced candidate.",
        "bullets": [{
            "experience_name": "产品运营实习",
            "bullet_text": "Optimized listings, reducing return rate by 1.2%.",
            "claim_level": "Green",
            "evidence": "Project data",
            "interview_risk": "",
            "recommended_action": "",
            # paraphrase: "减少了" instead of "降低", but shares "退货率" near 1.2
            "metric_source": "退货率减少了1.2%",
        }],
        "packaging_notes": "Lead with results.",
    }
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(mock)):
        result = generate_resume(
            _SELECTION_SOURCE, _IDEAL_SOURCE, "Ops", "TestCo",
            metric_whitelist={"EXP-001": ["1.2%"]},
            atoms_raw=_ATOMS_SAMPLE,
        )
    assert result.bullets[0].claim_level == "Green"
    assert result.bullets[0].metric_source == "退货率减少了1.2%"


# ---------------------------------------------------------------------------
# 13. test_context_keyword_required
# ---------------------------------------------------------------------------

_SELECTION_REPORT = ExperienceSelectionResult(
    included=[ExperienceMatch(
        experience_id="EXP-003", experience_name="财务BP专员",
        match_level="Strong", why_matched="Platform launch", suggested_angle="", risk_notes="",
    )],
    excluded=[], packaging_notes="", capability_gaps=[],
)


def test_context_keyword_required():
    """Step 3: numbers (1, 10) exist in atoms but context keywords don't match → Red.

    metric_source context: '报告生成时间' (3-4 char n-grams: 报告生, 告生成, 生成时, 成时间, 时间从, ...)
    atoms context near 1:  '核算耗时' (核算耗, 算耗时, 耗时从, ...)
    No shared n-grams → context mismatch → Red.
    """
    mock = {
        "target_role": "Ops",
        "target_company": "TestCo",
        "summary_statement": "Experienced candidate.",
        "bullets": [{
            "experience_name": "财务BP专员",
            "bullet_text": "Led platform launch reducing report preparation from 1 hour to 10 minutes.",
            "claim_level": "Green",
            "evidence": "Platform records",
            "interview_risk": "",
            "recommended_action": "",
            # numbers 1 and 10 exist in atoms, but surrounding context differs
            "metric_source": "报告生成时间从1小时缩短到10分钟",
        }],
        "packaging_notes": "",
    }
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(mock)):
        result = generate_resume(
            _SELECTION_REPORT, _IDEAL_SOURCE, "Ops", "TestCo",
            metric_whitelist={"EXP-003": ["1小时", "10分"]},
            atoms_raw=_ATOMS_REPORT,
        )
    assert result.bullets[0].claim_level == "Red"
    assert "CONTEXT MISMATCH" in result.bullets[0].interview_risk


# ---------------------------------------------------------------------------
# 14. test_paraphrase_with_shared_keywords_passes
# ---------------------------------------------------------------------------

_ATOMS_RETURN_SHORT = """\
## EXP-001
- experience_name: 产品运营实习
- metric: 退货率降低1.2%
"""


def test_paraphrase_with_shared_keywords_passes():
    """Paraphrased metric_source '退货率比发布当月降低1.2%' vs atoms '退货率降低1.2%'.

    Shared 3-char keyword '退货率' appears in both contexts near 1.2 → Step 3 passes.
    """
    mock = {
        "target_role": "Ops",
        "target_company": "TestCo",
        "summary_statement": "Experienced candidate.",
        "bullets": [{
            "experience_name": "产品运营实习",
            "bullet_text": "Reduced return rate by 1.2% through listing optimization.",
            "claim_level": "Green",
            "evidence": "Ops records",
            "interview_risk": "",
            "recommended_action": "",
            # longer paraphrase — not verbatim, but shares 退货率 near 1.2
            "metric_source": "退货率比发布当月降低1.2%",
        }],
        "packaging_notes": "",
    }
    with patch("applysmith.llm_client.call_llm", return_value=json.dumps(mock)):
        result = generate_resume(
            _SELECTION_SOURCE, _IDEAL_SOURCE, "Ops", "TestCo",
            metric_whitelist={"EXP-001": ["1.2%"]},
            atoms_raw=_ATOMS_RETURN_SHORT,
        )
    assert result.bullets[0].claim_level == "Green"
