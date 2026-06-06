"""
Resume Generator — writes tailored resume bullets from selected experiences.

Architectural safeguards against metric fabrication (applied in order):
  1. Before calling LLM: inject per-experience metric whitelist into the prompt so the
     model knows exactly which numbers it is allowed to use.
  2. After LLM returns — Pass 1 (_validate_bullets): strip any number not present in the
     whitelist for that experience; override claim_level to Red.
  3. After LLM returns — Pass 2 (_validate_metric_sources): structural validation:
       Step 1  Numbers in bullet_text must appear in metric_source (set comparison).
       Step 2  Numbers in metric_source must appear in atoms_raw.
               Catches 91% invented from 2.91%, or "2%" vs real "1.2%".
       Step 3  Context anchor: for each number in metric_source the surrounding
               keywords (3-4 char CJK n-grams; 3+ char English words) must overlap
               with the context around that same number in atoms_raw.  Allows
               legitimate paraphrasing while blocking context-swapped metrics.
"""
import logging
import re
from typing import Dict, List, Optional, Set

from .llm_client import call_llm_json
from .metric_extractor import allowed_digits
from .models import ExperienceSelectionResult, IdealCandidate, ResumeBullet, TailoredResume
from .prompts.resume_gen import RESUME_GEN_SYSTEM

logger = logging.getLogger(__name__)


def _build_whitelist_block(
    selection: ExperienceSelectionResult,
    metric_whitelist: Dict[str, List[str]],
) -> str:
    """Build the whitelist section injected into the user prompt."""
    lines = ["## Metric Whitelist (ONLY these numbers are allowed per experience)"]
    for exp in selection.included:
        tokens = metric_whitelist.get(exp.experience_id, [])
        if tokens:
            lines.append(f"- {exp.experience_id} ({exp.experience_name}): {', '.join(tokens)}")
        else:
            lines.append(f"- {exp.experience_id} ({exp.experience_name}): none — write bullet without numbers")
    return "\n".join(lines)


def _validate_bullets(
    bullets: List[ResumeBullet],
    name_to_id: Dict[str, str],
    digit_whitelist: Dict[str, Set[str]],
) -> List[ResumeBullet]:
    """
    Post-generation validator. For each bullet:
    - Find its experience_id via name_to_id mapping.
    - Extract all digit sequences from bullet_text.
    - Any digit NOT in the whitelist for that experience → strip it and flag Red.
    Returns a new list (original objects are not mutated).
    """
    validated = []
    for b in bullets:
        exp_id = name_to_id.get(b.experience_name)
        if exp_id is None:
            validated.append(b)
            continue

        allowed = digit_whitelist.get(exp_id, set())
        nums_in_bullet = re.findall(r"\d+", b.bullet_text)
        fabricated = [n for n in nums_in_bullet if n not in allowed]

        if not fabricated:
            validated.append(b)
            continue

        # Strip fabricated numbers from bullet_text
        cleaned_text = b.bullet_text
        for num in fabricated:
            # Match the digit possibly followed by unit chars or % or +
            cleaned_text = re.sub(
                rf"(?<!\d){re.escape(num)}(?:[%+天月年周小时分秒条个万亿k]+\+?|\+)?(?!\d)",
                "[X]",
                cleaned_text,
            )

        validated.append(
            ResumeBullet(
                experience_name=b.experience_name,
                bullet_text=cleaned_text,
                claim_level="Red",
                evidence=b.evidence,
                interview_risk=f"[FABRICATED METRIC DETECTED — original number(s) stripped: "
                               f"{', '.join(fabricated)}] {b.interview_risk}",
                recommended_action=b.recommended_action,
            )
        )
    return validated


_NUM_PATTERN = re.compile(r"\d+\.?\d*")

# Unit suffixes stripped when replacing fabricated numbers in bullet text
_UNIT_SUFFIX = r"(?:[%+天月年周小时分秒条个万亿k]+\+?|\+)?"

# CJK Unicode block
_CJK_RE = re.compile(r"[\u4e00-\u9fff]+")

# English/general stopwords to exclude from keyword matching
_STOPWORDS_EN = frozenset({"the", "and", "to", "of", "in", "for", "with", "by", "a", "an"})


def _extract_keywords(text: str) -> frozenset:
    """
    Extract semantic keywords for context comparison.

    - Chinese: all 3-4 character CJK n-grams from contiguous CJK runs.
    - English: words of 3+ ASCII letters, lowercased, stopwords removed.

    3-char minimum for CJK avoids noise from generic 2-char pairs like 小时/分钟
    that appear near any time-based metric.
    """
    kws: set[str] = set()
    for chunk in _CJK_RE.findall(text):
        for n in (3, 4):
            for i in range(len(chunk) - n + 1):
                kws.add(chunk[i : i + n])
    for word in re.findall(r"[a-zA-Z]{3,}", text):
        w = word.lower()
        if w not in _STOPWORDS_EN:
            kws.add(w)
    return frozenset(kws)


def _context_keywords(num: str, text: str, window: int = 20) -> frozenset:
    """Keywords from the context window surrounding the first occurrence of `num` in `text`."""
    m = re.search(r"(?<![.\d])" + re.escape(num) + r"(?![.\d])", text)
    if not m:
        return frozenset()
    ctx = text[max(0, m.start() - window) : m.start()] + text[m.end() : m.end() + window]
    return _extract_keywords(ctx)


def _atoms_context_keywords(num: str, atoms_raw: str, window: int = 30) -> frozenset:
    """Union of keywords from ALL occurrences of `num` in atoms_raw."""
    kws: set[str] = set()
    for m in re.finditer(r"(?<![.\d])" + re.escape(num) + r"(?![.\d])", atoms_raw):
        ctx = (
            atoms_raw[max(0, m.start() - window) : m.start()]
            + atoms_raw[m.end() : m.end() + window]
        )
        kws.update(_extract_keywords(ctx))
    return frozenset(kws)


def _validate_metric_sources(
    bullets: List[ResumeBullet],
    atoms_raw: Optional[str] = None,
) -> List[ResumeBullet]:
    """
    Pass 2 validator — structural validation (three steps):

    Step 1  Numbers in bullet_text must appear (exact set) in metric_source.
            "2" does not pass when source only has "1.2".

    Step 2  (requires atoms_raw) Numbers in metric_source must appear in atoms_raw.
            Catches "91%" invented from "2.91%".

    Step 3  (requires atoms_raw) Context anchor: keywords around each number in
            metric_source must overlap with keywords around that same number in atoms.
            Allows paraphrasing ("退货率比发布当月降低" ≈ "退货率降低") while blocking
            context swaps ("报告生成时间" ≠ "核算耗时").

    Paraphrasing is explicitly OK as long as Steps 1-3 pass.
    """
    atoms_nums = set(_NUM_PATTERN.findall(atoms_raw)) if atoms_raw else None

    def _strip_all(text: str) -> str:
        return re.sub(r"\d+\.?\d*" + _UNIT_SUFFIX, "[X]", text)

    def _strip_num(text: str, num: str) -> str:
        return re.sub(rf"(?<!\d){re.escape(num)}{_UNIT_SUFFIX}(?!\d)", "[X]", text)

    def _flag(b: ResumeBullet, cleaned: str, prefix: str) -> ResumeBullet:
        return ResumeBullet(
            experience_name=b.experience_name,
            bullet_text=cleaned,
            claim_level="Red",
            evidence=b.evidence,
            interview_risk=prefix + b.interview_risk,
            recommended_action="Verify metric source or remove number from bullet",
            metric_source=b.metric_source,
        )

    validated = []
    for b in bullets:
        nums = _NUM_PATTERN.findall(b.bullet_text)

        if not nums:
            validated.append(b)
            continue

        # ── Pre-check: metric_source must be present when numbers exist ─────────
        if not b.metric_source:
            logger.debug("metric_source missing for bullet — flagging Red: %r", b.bullet_text[:80])
            validated.append(_flag(b, _strip_all(b.bullet_text),
                                   "[METRIC SOURCE MISSING — no attribution provided] "))
            continue

        # ── Step 1: numbers in bullet must appear in metric_source ───────────────
        source_nums = set(_NUM_PATTERN.findall(b.metric_source))
        bad = [n for n in nums if n not in source_nums]
        if bad:
            logger.debug("Step 1 fail — %s absent from metric_source: %r", bad, b.bullet_text[:80])
            cleaned = b.bullet_text
            for n in bad:
                cleaned = _strip_num(cleaned, n)
            validated.append(_flag(cleaned=cleaned, b=b,
                                   prefix=f"[METRIC MISMATCH — {', '.join(bad)} not in metric_source] "))
            continue

        if atoms_raw is not None:
            # ── Step 2: numbers in metric_source must appear in atoms ────────────
            bad_src = [n for n in source_nums if n not in atoms_nums]
            if bad_src:
                logger.debug("Step 2 fail — %s not in atoms: %r", bad_src, b.metric_source[:80])
                validated.append(_flag(b, _strip_all(b.bullet_text),
                                       f"[METRIC NUMBER NOT IN ATOMS — "
                                       f"{', '.join(bad_src)} absent from experience_atoms] "))
                continue

            # ── Step 3: context anchor ───────────────────────────────────────────
            failed_num = None
            for num in source_nums:
                src_kws = _context_keywords(num, b.metric_source)
                if not src_kws:
                    continue  # no surrounding context to verify
                atm_kws = _atoms_context_keywords(num, atoms_raw)
                if not (src_kws & atm_kws):
                    failed_num = num
                    break

            if failed_num is not None:
                logger.debug("Step 3 fail — context mismatch for %s: %r",
                             failed_num, b.metric_source[:80])
                validated.append(_flag(b, _strip_all(b.bullet_text),
                                       f"[CONTEXT MISMATCH — metric_source context for "
                                       f"{failed_num} shares no keywords with atoms] "))
                continue

        validated.append(b)

    return validated


def generate_resume(
    selection: ExperienceSelectionResult,
    ideal: IdealCandidate,
    target_role: str,
    target_company: str,
    language: str = "en",
    metric_whitelist: Optional[Dict[str, List[str]]] = None,
    atoms_raw: Optional[str] = None,
) -> TailoredResume:
    """Generate tailored resume bullets from selected experiences."""
    if language == "zh":
        system = (
            RESUME_GEN_SYSTEM
            + "\nWrite all values in Simplified Chinese (简体中文), "
            "but keep bullet_text in English (resume bullets must stay in English). "
            "Keep technical terms, skill names, tool names, and proper nouns in English."
        )
    else:
        system = RESUME_GEN_SYSTEM

    # Build name→id mapping for validation
    name_to_id = {exp.experience_name: exp.experience_id for exp in selection.included}

    # Inject whitelist if provided
    whitelist_block = ""
    if metric_whitelist is not None:
        whitelist_block = "\n\n" + _build_whitelist_block(selection, metric_whitelist)

    user = (
        f"Target role: {target_role}\nTarget company: {target_company}\n\n"
        "## Ideal Candidate\n" + ideal.model_dump_json(indent=2)
        + "\n\n## Selected Experiences\n" + selection.model_dump_json(indent=2)
        + whitelist_block
    )

    def _fix_packing_notes(data: dict) -> dict:
        """Tolerate 'packing_notes' typo from LLM."""
        if "packing_notes" in data and "packaging_notes" not in data:
            data["packaging_notes"] = data.pop("packing_notes")
        return data

    resume = call_llm_json(system, user, TailoredResume, transform=_fix_packing_notes)

    # Post-generation validation — only when metric constraints are active
    if metric_whitelist is not None or atoms_raw is not None:
        bullets = resume.bullets

        # Pass 1: whitelist digit check
        if metric_whitelist is not None:
            digit_wl = allowed_digits(metric_whitelist)
            bullets = _validate_bullets(bullets, name_to_id, digit_wl)

        # Pass 2: verbatim source attribution check
        bullets = _validate_metric_sources(bullets, atoms_raw)

        resume = TailoredResume(
            target_role=resume.target_role,
            target_company=resume.target_company,
            summary_statement=resume.summary_statement,
            bullets=bullets,
            packaging_notes=resume.packaging_notes,
        )

    return resume
