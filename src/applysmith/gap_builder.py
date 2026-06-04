"""
Capability Gap Builder — generates a concrete learning + simulation plan for each gap.
"""
import re
from typing import List

from .llm_client import call_llm_json
from .models import CapabilityGapPlan, SimulationProject
from .prompts.gap_builder import GAP_BUILDER_SYSTEM


def build_gap_plan(
    gaps: List[str],
    target_role: str,
    target_company: str,
    language: str = "en",
) -> CapabilityGapPlan:
    """Generate a capability gap plan from a list of identified gaps."""
    if language == "zh":
        system = (
            GAP_BUILDER_SYSTEM
            + "\nWrite all values in Simplified Chinese (简体中文), "
            "but keep learning_resources URLs, dataset names, technical terms, "
            "skill names, and tool names in English. "
            "Keep resume_bullet_template in English."
        )
    else:
        system = GAP_BUILDER_SYSTEM

    user = (
        f"Target role: {target_role}\n"
        f"Target company: {target_company}\n\n"
        "## Capability Gaps to Address\n"
        + "\n".join(f"- {g}" for g in gaps)
    )
    plan = call_llm_json(system, user, CapabilityGapPlan)

    # Fix 1: strip specific numbers/percentages from bullet templates.
    cleaned_projects = []
    for proj in plan.simulation_projects:
        template = _sanitize_bullet_template(proj.resume_bullet_template)
        if template != proj.resume_bullet_template:
            proj = SimulationProject(
                **{**proj.model_dump(), "resume_bullet_template": template}
            )
        cleaned_projects.append(proj)

    # Fix 2: if LLM returned empty gaps but priority_order is populated, use it as fallback.
    effective_gaps = plan.gaps if plan.gaps else list(plan.priority_order)

    return CapabilityGapPlan(
        **{
            **plan.model_dump(),
            "gaps": effective_gaps,
            "simulation_projects": [p.model_dump() for p in cleaned_projects],
        }
    )


def _sanitize_bullet_template(template: str) -> str:
    """Replace concrete percentages and multipliers in a bullet template with [METRIC]."""
    return re.sub(r"\d+\.?\d*%|\d+x", "[METRIC]", template, flags=re.IGNORECASE)
