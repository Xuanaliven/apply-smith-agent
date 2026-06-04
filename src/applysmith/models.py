from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict
from datetime import date


class IndustryCard(BaseModel):
    industry_name: str
    typical_companies: List[str]
    common_roles: List[str]
    required_capabilities: List[str]
    resume_keywords: List[str]
    interview_focus: List[str]
    risk_notes: str
    suitable_candidate_profile: str


class RoleSchema(BaseModel):
    role_category: str
    sub_role: str
    required_capabilities: List[str]
    preferred_experiences: List[str]
    keywords: List[str]
    common_metrics: List[str]
    interview_focus: List[str]
    portfolio_suggestions: List[str]


class ExperienceAtom(BaseModel):
    id: str
    experience_name: str
    type: str
    time_period: str
    raw_fact: str
    role: str
    action: str
    tool: str
    metric: str
    evidence: str
    can_be_reused_for: List[str]
    risk_level: str


class CareerPipeline(BaseModel):
    name: str
    industry: str
    role_category: str
    candidate_profile: str
    fit_score: float
    buildability_score: float
    current_ceiling: str
    packaging_ceiling: str
    buildable_ceiling: str
    capability_gaps: List[str]
    weekly_actions: List[str]


class ApplicationRecord(BaseModel):
    company: str
    role_title: str
    role_category: str
    date: str
    channel: str
    pipeline: str
    status: str
    jd_path: str
    resume_path: str
    selected_experiences: List[str]
    risk_summary: str
    next_action: str


VALID_CLAIM_LEVELS = {"Green", "Yellow", "Red", "Buildable", "Stretch"}


class ClaimCheck(BaseModel):
    claim_text: str
    claim_source: str
    claim_level: str
    evidence: str
    risk_flags: List[str]
    interview_risk: str
    recommended_action: str

    @field_validator("claim_level")
    @classmethod
    def validate_claim_level(cls, v):
        if v not in VALID_CLAIM_LEVELS:
            raise ValueError(f"claim_level must be one of {VALID_CLAIM_LEVELS}")
        return v


class CompanyDossier(BaseModel):
    company_name: str
    ticker: Optional[str] = None
    ownership_type: str
    industry: str
    business_segments: List[str]
    main_products: List[str]
    revenue_logic: str
    strategic_keywords: List[str]
    public_sources: List[str]
    last_updated: str


class BusinessUnitProfile(BaseModel):
    company_name: str
    business_unit_name: str
    known_products: List[str]
    known_roles: List[str]
    candidate_profile: str
    preferred_background: str
    common_keywords: List[str]
    source_confidence: str
    risk_notes: str


class RoleLandingHypothesis(BaseModel):
    company_name: str
    job_title: str
    jd_keywords: List[str]
    likely_business_unit: str
    alternative_business_units: List[str]
    why_this_guess: str
    confidence_level: str
    resume_strategy: str
    interview_focus: str


class OpportunityScore(BaseModel):
    pipeline: str
    fit_score: float
    buildability_score: float
    market_breadth: str
    differentiation_score: float
    interview_defensibility: str
    roi_level: str
    judgment: str
    next_action: str


class JDAnalysis(BaseModel):
    role_type: str
    sub_role: str
    core_tasks: List[str]
    required_skills: List[str]
    preferred_skills: List[str]
    keywords: List[str]
    hidden_filters: List[str]
    ideal_candidate_summary: str
    resume_strategy: str
    interview_focus: List[str]
    red_flags: List[str]


class IdealCandidate(BaseModel):
    role_type: str
    background_summary: str
    must_have_experiences: List[str]
    nice_to_have_experiences: List[str]
    must_have_skills: List[str]
    differentiators: List[str]
    red_line_filters: List[str]


VALID_MATCH_LEVELS = {"Strong", "Partial", "Weak", "Irrelevant"}


class ExperienceMatch(BaseModel):
    experience_id: str
    experience_name: str
    match_level: str
    why_matched: str
    suggested_angle: str
    risk_notes: str

    @field_validator("match_level")
    @classmethod
    def validate_match_level(cls, v):
        if v not in VALID_MATCH_LEVELS:
            raise ValueError(f"match_level must be one of {VALID_MATCH_LEVELS}")
        return v


class ExperienceSelectionResult(BaseModel):
    included: List[ExperienceMatch]
    excluded: List[ExperienceMatch]
    packaging_notes: str
    capability_gaps: List[str]


class ResumeBullet(BaseModel):
    experience_name: str
    bullet_text: str
    claim_level: str
    evidence: str
    interview_risk: str
    recommended_action: str
    metric_source: str = ""
    """Exact verbatim phrase from experience_atoms that supports any metric in bullet_text.
    Empty string if no metric is used."""

    @field_validator("claim_level")
    @classmethod
    def validate_claim_level(cls, v):
        if v not in VALID_CLAIM_LEVELS:
            raise ValueError(f"claim_level must be one of {VALID_CLAIM_LEVELS}")
        return v


class TailoredResume(BaseModel):
    target_role: str
    target_company: str
    summary_statement: str
    bullets: List[ResumeBullet]
    packaging_notes: str


class ClaimCheckReport(BaseModel):
    overall_risk: str
    summary: str
    bullets: List[ResumeBullet]


class BulletDefense(BaseModel):
    bullet_text: str
    claim_level: str
    likely_questions: List[str]
    answer_framework: str
    key_talking_points: List[str]
    risk_boundary: str
    evidence_to_prepare: List[str]
    what_not_to_say: List[str]


class InterviewDefenseReport(BaseModel):
    target_role: str
    target_company: str
    overall_strategy: str
    bullet_defenses: List[BulletDefense]
    general_questions: List[str]
    capability_gap_questions: List[str]


VALID_PROJECT_TYPES = {"portfolio_project", "self_initiated_project", "course_like_project"}
VALID_PRIORITIES = {"High", "Medium", "Low"}


class LearningTask(BaseModel):
    skill: str
    why_needed: str
    learning_resources: List[str]
    estimated_hours: str
    priority: str

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        if v not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}")
        return v


class SimulationProject(BaseModel):
    skill: str
    project_title: str
    project_type: str
    dataset_suggestions: List[str]
    deliverables: List[str]
    resume_bullet_template: str
    interview_defense_notes: str
    warning: str

    @field_validator("project_type")
    @classmethod
    def validate_project_type(cls, v):
        if v not in VALID_PROJECT_TYPES:
            raise ValueError(f"project_type must be one of {VALID_PROJECT_TYPES}")
        return v


class CapabilityGapPlan(BaseModel):
    target_role: str
    target_company: str
    gaps: List[str]
    learning_tasks: List[LearningTask]
    simulation_projects: List[SimulationProject]
    priority_order: List[str]
    weekly_action_plan: str


VALID_TRACKER_STATUSES = {
    "draft", "submitted", "awaiting", "interview",
    "offer", "rejected", "withdrawn",
}


class ApplicationStatus(BaseModel):
    folder: str
    company: str
    role: str
    pipeline: str
    date: str
    channel: str = ""
    status: str = "draft"
    next_action: str = ""
    notes: str = ""
    last_updated: str = ""
    files_complete: List[str] = []
    files_missing: List[str] = []

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in VALID_TRACKER_STATUSES:
            raise ValueError(f"status must be one of {VALID_TRACKER_STATUSES}")
        return v


class TrackerSummary(BaseModel):
    total: int
    by_status: Dict[str, int]
    by_pipeline: Dict[str, int]
    applications: List[ApplicationStatus]
