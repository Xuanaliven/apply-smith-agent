from pathlib import Path
from .paths import strategy_dir


def get_strategy_summary() -> dict:
    """Read strategy files and return a summary dict."""
    s = strategy_dir()
    summary = {}
    for fname in [
        "target_map.md",
        "opportunity_scores.md",
        "weekly_plan.md",
        "capability_gap_board.md",
    ]:
        fpath = s / fname
        summary[fname] = (
            fpath.read_text(encoding="utf-8") if fpath.exists() else "(not found)"
        )
    return summary
