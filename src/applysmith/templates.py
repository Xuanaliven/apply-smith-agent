"""
Markdown template generators for ApplySmith.
"""


def pipeline_template(name: str, industry: str, role_category: str) -> str:
    return f"""# Pipeline: {name}

## Target Industry
{industry}

## Target Roles
{role_category}

## Candidate Profile
<!-- Summarize your relevant background for this pipeline -->

## Opportunity Score
| Dimension | Score | Notes |
|-----------|-------|-------|
| Fit Score | - | |
| Buildability Score | - | |
| Market Breadth | - | |
| Differentiation Score | - | |
| Interview Defensibility | - | |
| ROI Level | - | |

## Current Ceiling
<!-- What you can honestly claim right now -->

## Packaging Ceiling
<!-- What you can claim with better framing of existing experience -->

## Buildable Ceiling
<!-- What you can claim after 4-8 weeks of focused portfolio work -->

## Capability Gaps
- [ ] Gap 1
- [ ] Gap 2

## Weekly Actions
- [ ] Week 1:

## Application Records
| Date | Company | Role | Channel | Status | Next Action |
|------|---------|------|---------|--------|-------------|
"""


def application_files() -> dict[str, str]:
    files = {}

    files["01_jd_original.md"] = """# JD: Original

## Job Title
<!-- Paste job title here -->

## Company
<!-- Company name -->

## Date Posted / Retrieved
<!-- Date -->

## Source URL / Channel
<!-- Where you found this JD -->

## Full JD Text
<!-- Paste the complete JD here, unedited -->
"""

    files["02_jd_analysis.md"] = """# JD Analysis

## Hard Requirements
<!-- Must-have qualifications listed in JD -->

## Soft Requirements
<!-- Nice-to-have or implied qualifications -->

## Key Metrics Mentioned
<!-- Any KPIs, metrics, or measurable outcomes mentioned -->

## Red Flags
<!-- Anything concerning: vague scope, unrealistic demands, etc. -->

## Inferred Business Unit
<!-- Which business unit likely owns this role, and why -->

## Inferred Pain Points
<!-- What problem is this hire solving for the team? -->

## Keywords to Reflect in Resume
<!-- List keywords from JD to mirror in your materials -->
"""

    files["03_company_dossier_snapshot.md"] = """# Company Dossier Snapshot

## Company
<!-- Company name -->

## Snapshot Date
<!-- Date this snapshot was taken -->

## Business Overview
<!-- Brief summary of what the company does -->

## Relevant Business Segments
<!-- Which segments relate to this role -->

## Strategic Direction
<!-- Recent strategic priorities based on public sources -->

## Why This Company Now
<!-- Your thesis for why this company/timing makes sense -->
"""

    files["04_business_unit_hypothesis.md"] = """# Business Unit Hypothesis

## Job Title
<!-- Role you are applying for -->

## Most Likely Business Unit
<!-- Your best guess and rationale -->

## Alternative Business Units
<!-- Other possibilities with rationale -->

## Confidence Level
<!-- High / Medium / Low — with justification -->

## Key Evidence
<!-- What JD signals, company structure, or public info supports this -->

## Implications for Resume
<!-- How this hypothesis changes what you emphasize -->
"""

    files["05_ideal_candidate.md"] = """# Ideal Candidate Profile

## Reconstructed Profile
<!-- Based on JD and business unit hypothesis, what does the ideal candidate look like? -->

## Background They Expect
<!-- Likely educational and work history patterns -->

## Skills They Prioritize
<!-- Ranked list of what they are really looking for -->

## Mindset / Soft Skills
<!-- What working style or attitude does this role require -->

## Gap Between You and Ideal
<!-- Honest assessment of where you fall short -->

## How to Bridge the Gap in Materials
<!-- Framing, emphasis, or portfolio work to close the gap -->
"""

    files["06_selected_experiences.md"] = """# Selected Experiences

## Selection Rationale
<!-- Why these experiences were chosen for this application -->

## Experience 1
- **Source**: <!-- Experience atom ID or description -->
- **Relevance**: <!-- Why it fits this JD -->
- **Claim Level**: <!-- Green / Yellow / Red / Buildable / Stretch -->
- **Tailoring Notes**: <!-- How to adapt for this application -->

## Experience 2
- **Source**:
- **Relevance**:
- **Claim Level**:
- **Tailoring Notes**:

## Experience 3
- **Source**:
- **Relevance**:
- **Claim Level**:
- **Tailoring Notes**:
"""

    files["07_tailored_resume.md"] = """# Tailored Resume

<!--
This file contains your tailored resume for this specific application.
Build it by selecting from your experience atoms, not by editing a generic resume.
Every claim here should have a corresponding entry in 08_claim_check_report.md
-->

## Header
<!-- Name, contact, target role -->

## Summary / Objective (optional)
<!-- 2-3 lines max, tailored to this specific role -->

## Experience

### [Role Title] | [Company/Organization] | [Date Range]
-
-
-

### [Role Title] | [Company/Organization] | [Date Range]
-
-
-

## Education
<!-- Degree, institution, graduation date, relevant coursework -->

## Skills
<!-- Tailored skills list relevant to this JD -->

## Projects (if applicable)
<!-- Portfolio or self-initiated projects — label clearly as such -->
"""

    files["08_claim_check_report.md"] = """# Claim Check Report

<!--
Every factual claim in your resume must have an entry here.
Claim levels: Green (fully evidenced), Yellow (partially evidenced),
Red (unsupported), Buildable (can be earned), Stretch (needs framing)
-->

| Claim | Source | Level | Evidence | Interview Risk | Recommended Action |
|-------|--------|-------|----------|---------------|-------------------|
| | | | | | |
| | | | | | |
"""

    files["09_interview_defense.md"] = """# Interview Defense

## Role Understanding
<!-- How you would explain what this role does and why it matters -->

## Why This Company
<!-- Your genuine, researched answer — not generic flattery -->

## Why This Role
<!-- What draws you to this specific function -->

## Key Story Preparation

### Story 1: [Competency]
- **Situation**:
- **Task**:
- **Action**:
- **Result**:
- **Claim Level**:

### Story 2: [Competency]
- **Situation**:
- **Task**:
- **Action**:
- **Result**:
- **Claim Level**:

## Anticipated Hard Questions
<!-- Questions where your background is weak — prepare honest answers -->

## Questions to Ask Interviewer
<!-- Thoughtful questions that show you understand the business -->
"""

    files["10_question_bank_links.md"] = """# Question Bank Links

## Role Category
<!-- Which role category question bank applies here -->

## Linked Question Files
<!-- Reference paths to relevant question bank files -->

## Company-Specific Questions
<!-- Any questions specific to this company's known interview style -->

## Technical Prep
<!-- Any technical assessments or case prep needed -->
"""

    files["11_application_log.md"] = """# Application Log

## Company
<!-- -->

## Role
<!-- -->

## Pipeline
<!-- -->

## Timeline

| Date | Event | Notes |
|------|-------|-------|
| | Application submitted | |
| | | |

## Contact Log

| Date | Person | Channel | Notes |
|------|--------|---------|-------|
| | | | |

## Outcome
<!-- Final result and key learnings -->
"""

    return files


def company_dossier_template(company: str, industry: str, ticker: str | None = None) -> str:
    ticker_str = ticker if ticker else "N/A"
    return f"""# Company Dossier: {company}

**Industry**: {industry}
**Ticker**: {ticker_str}
**Last Updated**: <!-- Date -->

---

## Basic Profile
| Field | Value |
|-------|-------|
| Full Name | {company} |
| Ownership Type | <!-- State-owned / Private / Listed / Foreign --> |
| Founded | <!-- Year --> |
| Headquarters | <!-- City, Country --> |
| Employee Count | <!-- Approximate --> |
| Revenue Scale | <!-- Approximate annual revenue --> |

## Business Segments
<!-- List the main business units or product lines -->

- Segment 1:
- Segment 2:
- Segment 3:

## Organization Map
<!-- Describe the known organizational structure relevant to job seekers -->
<!-- Use public information only: org charts, LinkedIn, official site -->

## Recruiting Role Map
<!-- Which roles does this company typically hire, by business unit? -->

| Business Unit | Common Roles | Typical Headcount Season |
|---------------|-------------|-------------------------|
| | | |

## Business Unit Differences
<!-- How do different BUs differ in culture, rigor, candidate profile? -->
<!-- Mark everything here as hypothesis unless sourced from public info -->

## Public Sources
<!-- Links or references to annual reports, investor relations, official news -->

- [ ] Annual Report:
- [ ] Investor Day slides:
- [ ] Official careers page:
- [ ] LinkedIn company page:

## Social / Employee Signals
> ⚠️ WARNING: This section contains low-confidence, scope-limited signals.
> Sources: employee posts, third-party forums, recruiting platforms.
> Do not treat as authoritative. Verify through official channels.
> Do not record confidential or internally-sourced information here.

<!-- Add public signals here, with source and date -->

## Resume Strategy
<!-- How to frame your resume for this company -->
<!-- Consider: what they value, what they screen for, how to stand out -->

## Interview Preparation
<!-- Known interview formats, focus areas, and preparation tips -->
<!-- Use only publicly available information -->

## Risk Notes
<!-- Any red flags, instability signals, or reasons to proceed carefully -->
"""
