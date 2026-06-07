"""
Shared metric validation utilities.

Used by both resume_generator and claim_checker to enforce consistent
3-step structural validation of metric attribution:

  Step 1  Numbers in bullet_text must appear in metric_source (set match).
  Step 2  Numbers in metric_source must appear in atoms_raw.
  Step 3  Context keywords around each number in metric_source must overlap
          with keywords around that same number in atoms_raw.
          Allows paraphrasing; blocks context-swapped metrics.
"""
import logging
import re
from typing import List, Optional

from .models import ResumeBullet

logger = logging.getLogger(__name__)

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

    3-char minimum for CJK avoids noise from generic 2-char pairs like
    小时/分钟 that appear near any time-based metric.
    """
    kws: set = set()
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
    kws: set = set()
    for m in re.finditer(r"(?<![.\d])" + re.escape(num) + r"(?![.\d])", atoms_raw):
        ctx = (
            atoms_raw[max(0, m.start() - window) : m.start()]
            + atoms_raw[m.end() : m.end() + window]
        )
        kws.update(_extract_keywords(ctx))
    return frozenset(kws)


def validate_metric_sources(
    bullets: List[ResumeBullet],
    atoms_raw: Optional[str] = None,
) -> List[ResumeBullet]:
    """
    3-step structural validator for metric attribution.

    Step 1  Numbers in bullet_text must appear (exact set) in metric_source.
            "2" does not pass when source only has "1.2".

    Step 2  (requires atoms_raw) Numbers in metric_source must appear in atoms_raw.
            Catches "91%" invented from "2.91%".

    Step 3  (requires atoms_raw) Context anchor: keywords around each number in
            metric_source must overlap with keywords around that same number in atoms.
            Allows paraphrasing while blocking context swaps.
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
