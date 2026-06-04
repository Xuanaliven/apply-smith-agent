"""
Tests for JSON repair logic in _extract_json_str and _repair_inner_quotes.
No real API calls are made.
"""
import json

import pytest

from applysmith.llm_client import _extract_json_str, _repair_inner_quotes


# ---------------------------------------------------------------------------
# _repair_inner_quotes unit tests
# ---------------------------------------------------------------------------

class TestRepairInnerQuotes:
    def test_no_inner_quotes(self):
        """Valid JSON with no inner quotes is returned unchanged."""
        s = '{"key": "clean value"}'
        assert _repair_inner_quotes(s) == s

    def test_single_inner_quote_pair(self):
        """A single pair of inner quotes is replaced with single quotes."""
        broken = '{"key": "value with "inner" quotes"}'
        result = _repair_inner_quotes(broken)
        data = json.loads(result)
        assert "inner" in data["key"]
        assert '"' not in data["key"]

    def test_chinese_inner_quotes(self):
        """Chinese text with unescaped inner quotes is repaired."""
        broken = '{"overall_strategy": "将经历锚定在"用户增长"这一主题"}'
        result = _repair_inner_quotes(broken)
        data = json.loads(result)
        assert "用户增长" in data["overall_strategy"]

    def test_escaped_quotes_preserved(self):
        """Already-escaped quotes inside strings are left alone."""
        s = '{"key": "value with \\"escaped\\" quotes"}'
        result = _repair_inner_quotes(s)
        data = json.loads(result)
        assert data["key"] == 'value with "escaped" quotes'

    def test_multiple_inner_quote_pairs(self):
        """Multiple inner quote pairs in one value are all replaced."""
        broken = '{"key": "first "A" and second "B" term"}'
        result = _repair_inner_quotes(broken)
        data = json.loads(result)
        assert "A" in data["key"]
        assert "B" in data["key"]
        assert '"' not in data["key"]

    def test_preserves_other_fields(self):
        """Repair does not corrupt other fields in the JSON object."""
        broken = '{"strategy": "use "growth" hacking", "score": 42, "tags": ["a", "b"]}'
        result = _repair_inner_quotes(broken)
        data = json.loads(result)
        assert data["score"] == 42
        assert data["tags"] == ["a", "b"]
        assert "growth" in data["strategy"]


# ---------------------------------------------------------------------------
# _extract_json_str: unescaped inner quotes
# ---------------------------------------------------------------------------

class TestExtractJsonStrInnerQuotes:
    def test_unescaped_inner_quotes(self):
        """Input with unescaped inner quotes parses correctly after repair."""
        raw = '{"overall_strategy": "将经历锚定在"用户增长"这一主题"}'
        cleaned = _extract_json_str(raw)
        data = json.loads(cleaned)
        assert "用户增长" in data["overall_strategy"]

    def test_unescaped_english_inner_quotes(self):
        """English value with inner double quotes is repaired."""
        raw = '{"summary": "focus on the "growth" angle"}'
        cleaned = _extract_json_str(raw)
        data = json.loads(cleaned)
        assert "growth" in data["summary"]

    def test_already_valid_json_unchanged(self):
        """Valid JSON is returned without modification."""
        raw = '{"key": "plain value", "num": 1}'
        cleaned = _extract_json_str(raw)
        assert json.loads(cleaned) == {"key": "plain value", "num": 1}


# ---------------------------------------------------------------------------
# _extract_json_str: Chinese / curly quotes (full-width)
# ---------------------------------------------------------------------------

class TestExtractJsonStrChineseQuotes:
    def test_curly_double_quotes_normalized(self):
        """Unicode curly double quotes \u201c\u201d inside a value are normalized to straight quotes,
        which may then be repaired if they break JSON structure."""
        # After normalization, \u201c and \u201d become " — the repair should then
        # handle any resulting structural breakage
        raw = '{"key": "value with \u201ccurly\u201d quotes"}'
        cleaned = _extract_json_str(raw)
        data = json.loads(cleaned)
        assert "curly" in data["key"]

    def test_curly_single_quotes_normalized(self):
        """Unicode curly single quotes \u2018\u2019 are normalized to straight apostrophes."""
        raw = '{"key": "it\u2019s a value"}'
        cleaned = _extract_json_str(raw)
        data = json.loads(cleaned)
        assert "it's a value" == data["key"]

    def test_chinese_comma_normalized(self):
        """Full-width Chinese comma is replaced with ASCII comma."""
        raw = '{"a": "one"\uff0c"b": "two"}'
        # \uff0c is ，
        raw = '{"a": "one"\uff0c "b": "two"}'
        cleaned = _extract_json_str(raw)
        # After normalization the comma becomes ASCII; try parsing
        # (the structure here isn't valid JSON regardless, but normalization is tested)
        assert "," in cleaned

    def test_full_chinese_punctuation_value(self):
        """A realistic Chinese LLM output with full-width punctuation is repaired."""
        # Simulates: {"strategy": "将经历锚定在"用户增长"这一主题，提升DAU。"}
        raw = (
            '{"strategy": '
            '"\u5c06\u7ecf\u5386\u9526\u5b9a\u5728'
            '"\u7528\u6237\u589e\u957f"'
            '\u8fd9\u4e00\u4e3b\u9898\uff0c\u63d0\u5347DAU\u3002"}'
        )
        cleaned = _extract_json_str(raw)
        data = json.loads(cleaned)
        assert "用户增长" in data["strategy"]


# ---------------------------------------------------------------------------
# _extract_json_str: mixed quote styles
# ---------------------------------------------------------------------------

class TestExtractJsonStrMixedQuotes:
    def test_markdown_fence_plus_inner_quotes(self):
        """Markdown fences are stripped and inner quotes are repaired."""
        raw = '```json\n{"key": "value with "inner" term"}\n```'
        cleaned = _extract_json_str(raw)
        data = json.loads(cleaned)
        assert "inner" in data["key"]

    def test_curly_quotes_become_inner_quotes(self):
        """Curly quotes normalized to straight quotes, then repaired if needed."""
        # \u201c and \u201d are " and " — after normalization they become "
        # which may break the JSON structure and need repair
        raw = '{"note": "see \u201cFigure 1\u201d for details"}'
        cleaned = _extract_json_str(raw)
        data = json.loads(cleaned)
        assert "Figure 1" in data["note"]

    def test_mixed_chinese_and_english_inner_quotes(self):
        """Mixed Chinese text with English inner-quoted terms is repaired."""
        raw = '{"summary": "利用"A/B testing"方法验证假设"}'
        cleaned = _extract_json_str(raw)
        data = json.loads(cleaned)
        assert "A/B testing" in data["summary"]


# ---------------------------------------------------------------------------
# _extract_json_str: completely broken JSON still raises a clear error
# ---------------------------------------------------------------------------

class TestExtractJsonStrMalformed:
    def test_malformed_passthrough_raises(self):
        """Completely broken JSON still raises a clear JSONDecodeError after repair attempt."""
        raw = "this is not json at all {{{{"
        cleaned = _extract_json_str(raw)
        with pytest.raises(json.JSONDecodeError):
            json.loads(cleaned)

    def test_truncated_json_raises(self):
        """Truncated JSON raises JSONDecodeError after repair attempt."""
        raw = '{"key": "value'
        cleaned = _extract_json_str(raw)
        with pytest.raises(json.JSONDecodeError):
            json.loads(cleaned)

    def test_empty_input_raises(self):
        """Empty string raises JSONDecodeError."""
        cleaned = _extract_json_str("")
        with pytest.raises(json.JSONDecodeError):
            json.loads(cleaned)
