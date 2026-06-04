"""
Package generator: creates all folders and files for an ApplySmith project.
"""
import re
import shutil
from pathlib import Path

from .paths import (
    data_dir, master_profile_dir, industry_maps_dir, role_schemas_dir,
    capability_roadmaps_dir, company_dossiers_dir, company_sources_dir,
    question_bank_dir, external_signals_dir, pipelines_dir, strategy_dir,
    applications_dir, mark_initialized,
)
from .templates import (
    pipeline_template, application_files, company_dossier_template,
)


def get_example_files_source() -> Path:
    """Return the path to the bundled example data files."""
    return Path(__file__).parent / "data"


def _slugify(text: str) -> str:
    """Convert a string to a filesystem-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "_", text)
    text = re.sub(r"-+", "_", text)
    return text


# ---------------------------------------------------------------------------
# Folder creation
# ---------------------------------------------------------------------------

def create_all_folders() -> None:
    """Create every directory in the ApplySmith project structure."""
    dirs = [
        data_dir(),
        master_profile_dir(),
        industry_maps_dir(),
        role_schemas_dir(),
        capability_roadmaps_dir(),
        company_dossiers_dir(),
        company_sources_dir(),
        company_sources_dir() / "annual_reports",
        company_sources_dir() / "investor_relations",
        company_sources_dir() / "job_descriptions",
        company_sources_dir() / "news",
        company_sources_dir() / "social_signals",
        question_bank_dir(),
        external_signals_dir(),
        external_signals_dir() / "imported",
        pipelines_dir(),
        strategy_dir(),
        applications_dir(),
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Strategy files
# ---------------------------------------------------------------------------

def create_strategy_files() -> None:
    s = strategy_dir()
    s.mkdir(parents=True, exist_ok=True)

    target_map = s / "target_map.md"
    if not target_map.exists():
        target_map.write_text(
            """# Target Map

## Pipelines Overview
| Pipeline | Industry | Role Category | Company Count | Status |
|----------|----------|--------------|---------------|--------|
| | | | | |

## Target Companies
| Company | Industry | Role | Pipeline | Priority | Notes |
|---------|----------|------|----------|----------|-------|
| | | | | | |
""",
            encoding="utf-8",
        )

    opportunity_scores = s / "opportunity_scores.md"
    if not opportunity_scores.exists():
        opportunity_scores.write_text(
            """# Opportunity Scores

| Pipeline | Fit Score | Buildability | Market Breadth | Differentiation | Defensibility | ROI Level | Judgment |
|----------|-----------|-------------|----------------|-----------------|---------------|-----------|----------|
| | | | | | | | |
""",
            encoding="utf-8",
        )

    weekly_plan = s / "weekly_plan.md"
    if not weekly_plan.exists():
        weekly_plan.write_text(
            """# Weekly Plan

## Week of: [DATE]

### Priority Actions
- [ ]
- [ ]
- [ ]

### Application Deadlines
| Company | Role | Deadline | Status |
|---------|------|----------|--------|
| | | | |

### Capability Building
- [ ]

### Reflection
<!-- What worked? What to adjust next week? -->
""",
            encoding="utf-8",
        )

    capability_gap_board = s / "capability_gap_board.md"
    if not capability_gap_board.exists():
        capability_gap_board.write_text(
            """# Capability Gap Board

| Capability | Gap Level | Priority | Plan | Target Date | Status |
|-----------|-----------|----------|------|-------------|--------|
| | | | | | |

## In Progress
<!-- Detail current capability building efforts -->

## Completed
<!-- Capabilities you have closed -->
""",
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# Master profile files
# ---------------------------------------------------------------------------

def create_master_profile_files() -> None:
    mp = master_profile_dir()
    mp.mkdir(parents=True, exist_ok=True)

    profile_questions = mp / "profile_questions.md"
    if not profile_questions.exists():
        profile_questions.write_text(
            """# Profile Questions

Fill in your answers below. This is your master profile — a personal database
used for retrieving relevant experiences during application packaging.
Do NOT tailor this file toward any specific job. Be honest and precise.

---

## Basic Info

- **Full Name**:
- **Current Location**:
- **Contact Email**:
- **LinkedIn URL** (optional):
- **Target graduation / availability date**:

---

## Education

For each degree or program:

- **Institution**:
- **Degree / Program**:
- **Major / Field of Study**:
- **GPA** (if competitive):
- **Graduation Date**:
- **Relevant Coursework**: (list up to 5 courses most relevant to target roles)
- **Notable Academic Projects**: (brief descriptions)
- **Awards / Honors**:

---

## Work Experience

Repeat for each role (most recent first):

### Role [1]
- **Company / Organization**:
- **Role Title**:
- **Employment Type**: (Full-time / Internship / Part-time / Contract)
- **Date Range**:
- **Team Size**:
- **What the team/product did** (1-2 sentences):
- **Your primary responsibilities** (bullet list):
- **Key tools or platforms you used**:
- **Metrics you owned or contributed to** (be specific):
- **Most impactful thing you accomplished** (describe with numbers if possible):
- **What you could NOT do or did not accomplish** (honest):

---

## Projects

Repeat for each project:

### Project [1]
- **Project Name**:
- **Type**: (Academic / Self-initiated / Portfolio / Hackathon / Open Source)
- **Date Range**:
- **What problem it solved**:
- **Your specific role and contributions**:
- **Technologies / tools used**:
- **Measurable outcome or result**:
- **Can this be verified?** (public link / repository / submission):

---

## Skills

- **Programming Languages** (rank by proficiency: fluent / working / basic):
- **Data Tools** (SQL, Excel, Python libraries, BI tools):
- **Domain Knowledge** (e.g., digital marketing, supply chain, finance):
- **Languages** (with proficiency level):
- **Certifications** (with issuing body and date):

---

## Target Direction

- **Recruiting stage**: (Summer internship / Autumn 秋招 / Spring 春招 / Social 社招 / Career change)
- **Target industries** (ranked):
- **Target role categories** (ranked):
- **Geographic preference**:
- **Salary expectation** (optional):
- **Constraints or deal-breakers**:
""",
            encoding="utf-8",
        )

    experience_atoms = mp / "experience_atoms.md"
    if not experience_atoms.exists():
        experience_atoms.write_text(
            """# Experience Atoms

An experience atom is the smallest reusable unit of your professional history.
Each atom describes ONE specific thing you did, with a verifiable metric and evidence.
Atoms are the building blocks of tailored resumes. Do not blend multiple experiences.

**Format each atom using the template below.**

---

## Atom Template

```
### [ATOM-ID] [Short Name]

- **Type**: (internship / academic / project / self-initiated / volunteer)
- **Time Period**: (e.g., Jun 2023 – Aug 2023)
- **Raw Fact**: (what actually happened, no spin)
- **Role**: (your title or role on this)
- **Action**: (what YOU specifically did — verb-first)
- **Tool**: (main tool, platform, or method used)
- **Metric**: (quantified result — be honest about confidence level)
- **Evidence**: (how can this be verified? link, artifact, reference)
- **Can Be Reused For**: (list of role categories or skills this supports)
- **Risk Level**: (Green / Yellow / Red)
  - Green: fully evidenced, can defend in interview
  - Yellow: partially evidenced, may need context
  - Red: hard to verify or easy to overclaim — use with extreme caution
```

---

## Example Atom 1

### [ATOM-001] University Research Project — Survey Data Analysis

- **Type**: academic
- **Time Period**: Sep 2022 – Jan 2023
- **Raw Fact**: Collected and analyzed survey data from 200 participants for a thesis on consumer behavior in online shopping
- **Role**: Lead researcher and analyst
- **Action**: Designed the survey instrument, collected responses via online platform, cleaned data in Excel, ran descriptive statistics and chi-square tests
- **Tool**: Excel, SPSS (basic)
- **Metric**: 200 valid responses; identified 3 statistically significant behavioral segments (p < 0.05)
- **Evidence**: Thesis submitted to department; available on request
- **Can Be Reused For**: Data Analysis, User Research, Operations, Market Research
- **Risk Level**: Green

---

## Example Atom 2

### [ATOM-002] Internship — Weekly Performance Reporting

- **Type**: internship
- **Time Period**: Jun 2023 – Aug 2023
- **Raw Fact**: Supported the operations team at a mid-sized e-commerce company by maintaining a weekly reporting dashboard tracking key fulfillment metrics
- **Role**: Operations Intern
- **Action**: Pulled raw data from internal system, cleaned it in Excel, built a template that the team reused weekly; flagged anomalies in delivery time that led to a process review
- **Tool**: Excel, internal OMS (order management system)
- **Metric**: Reduced weekly report preparation time from ~3 hours to ~45 minutes; flagged 2 recurring delay patterns
- **Evidence**: Internship certificate available; supervisor contact available on request
- **Can Be Reused For**: Operations, Data Analysis, Supply Chain, Reporting
- **Risk Level**: Green

---

<!-- Add your own atoms below this line -->
""",
            encoding="utf-8",
        )

    skills = mp / "skills.md"
    if not skills.exists():
        skills.write_text(
            """# Skills Inventory

Rate your proficiency honestly:
- **Fluent**: Can work independently, can defend in technical interview
- **Working**: Can use with documentation/reference, would not put as headline skill
- **Basic**: Aware of concept, limited hands-on practice

---

## Technical Skills

| Skill | Proficiency | Notes / Context |
|-------|------------|-----------------|
| Python | | (e.g., data manipulation, pandas, matplotlib) |
| SQL | | (e.g., SELECT, JOINs, window functions) |
| Excel / Google Sheets | | (e.g., VLOOKUP, pivot tables, charts) |
| R | | |
| Other | | |

---

## Tools & Platforms

| Tool / Platform | Proficiency | Notes / Context |
|----------------|------------|-----------------|
| Tableau / Power BI | | |
| Google Analytics | | |
| Facebook Ads Manager | | |
| Salesforce / CRM | | |
| Notion / Confluence | | |
| Git / GitHub | | |
| Other | | |

---

## Domain Knowledge

| Domain | Level | Notes |
|--------|-------|-------|
| Digital Marketing | | |
| E-commerce Operations | | |
| Supply Chain | | |
| Financial Modeling | | |
| Consumer Behavior | | |
| Other | | |

---

## Languages

| Language | Level | Certifications |
|----------|-------|---------------|
| Mandarin Chinese | | |
| English | | (e.g., CET-6, IELTS, TOEFL score) |
| Other | | |
""",
            encoding="utf-8",
        )

    forbidden_claims = mp / "forbidden_claims.md"
    if not forbidden_claims.exists():
        forbidden_claims.write_text(
            """# Forbidden Claims

This file tracks claims you are NOT allowed to make in any application material.
Review this list before finalizing any resume or cover letter.

A claim becomes "forbidden" when:
- You cannot verify it with evidence
- You could not defend it under direct questioning
- It describes someone else's work as your own
- It exaggerates scope, impact, or ownership beyond what is true
- It misrepresents your role, title, or tenure

Add entries as you discover them. Be honest with yourself.

---

## Format

```
- [ ] [CLAIM]: [WHY IT IS FORBIDDEN]
```

---

## Examples (Starter Entries)

- [ ] "Proficient in Python": Do not claim proficiency in tools you have only briefly used or followed a tutorial on. Use "basic familiarity" or omit.
- [ ] "Led a team of X people": Do not claim team leadership unless you had explicit responsibility for task allocation, performance feedback, or project outcomes.
- [ ] "Increased revenue by X%": Do not claim business impact you did not personally measure or cannot trace to your specific actions.
- [ ] "Managed a budget of X": Do not claim budget ownership unless you had signing authority or direct accountability for spend decisions.
- [ ] "Fluent in [language]": Do not claim fluency unless you can conduct a full professional interview in that language.
- [ ] "5 years of experience in X": Do not round up or aggregate loosely related experience into a single headline number.
- [ ] "Expert in [tool]": "Expert" is a high bar. If you have not used the tool in production at meaningful scale, do not use this word.

---

## My Personal Forbidden Claims

<!-- Add your own entries below this line -->
- [ ]
""",
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# README files
# ---------------------------------------------------------------------------

def create_readme_files() -> None:
    dossiers_readme = company_dossiers_dir() / "README.md"
    company_dossiers_dir().mkdir(parents=True, exist_ok=True)
    if not dossiers_readme.exists():
        dossiers_readme.write_text(
            """# Company Dossiers

This folder contains one markdown file per target company.

## How to Create a Dossier

Use the CLI command:

```
applysmith new-company-dossier --company "Company Name" --industry "Industry" --ticker "TICKER"
```

This will generate a pre-formatted dossier file you can fill in.

## Guidelines

- Use **public information only**: annual reports, investor relations pages, official careers pages, LinkedIn company pages, official press releases.
- The "Social / Employee Signals" section is for low-confidence signals only — mark them as such and do not treat them as authoritative.
- **Never record confidential or internally-sourced information** in these files.
- Update the "Last Updated" field every time you revise a dossier.
- Keep one file per company. Name the file exactly as you want the company to appear in your records.

## File Naming Convention

`[Company Name].md` — use the official company name, capitalized as it appears publicly.

Examples:
- `ByteDance.md`
- `Alibaba Group.md`
- `CATL.md`
""",
            encoding="utf-8",
        )

    signals_readme = external_signals_dir() / "README.md"
    external_signals_dir().mkdir(parents=True, exist_ok=True)
    if not signals_readme.exists():
        signals_readme.write_text(
            """# External Signals

This folder holds external intelligence files you have manually gathered about companies,
roles, or industries. These are inputs to your strategy — not final documents.

## What Counts as an External Signal

- A job description PDF you saved
- A screenshot of a LinkedIn post about company culture
- An exported news article about a company's strategic direction
- An investor presentation or earnings call transcript
- An industry research report

## How to Import a Signal

Use the CLI command:

```
applysmith import-signal --file /path/to/signal_file.pdf --pipeline "pipeline-name"
```

This copies the file into `imported/` and logs it in the specified pipeline file.

## Important Warnings

- **Do NOT store confidential or internally-sourced information here.**
- Social media screenshots and employee forum posts are low-confidence signals. Label them clearly.
- ApplySmith does not scrape social media. All signals must be manually provided by you.
- If you are unsure whether a source is appropriate, err on the side of exclusion.

## Folder Structure

```
external_signals/
  imported/        ← all imported files land here
  README.md        ← this file
```
""",
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# Example files
# ---------------------------------------------------------------------------

def create_example_files() -> None:
    """Write all example/template files with rich placeholder content."""

    # --- industry maps ---
    industry_maps_dir().mkdir(parents=True, exist_ok=True)

    internet_platform = industry_maps_dir() / "_example_internet_platform.md"
    if not internet_platform.exists():
        internet_platform.write_text(
            """# Industry Map: Internet / Platform

## Overview
The Internet / Platform sector includes companies whose core business is operating
digital platforms that aggregate users, content, or commerce at scale. Revenue models
are primarily advertising, transaction fees, and subscription.

## Typical Companies
- Major short video platform (e.g., TikTok / Douyin parent company)
- Leading search engine company
- Large social media platform
- Dominant e-commerce platform operator
- Super-app / messaging platform with embedded financial services

## Common Roles
- Product Manager (growth, monetization, content, platform)
- Data Analyst / Business Analyst
- Operations (Content Operations, User Operations, Activity Operations)
- Advertising Operations / Performance Marketing
- Growth / User Acquisition

## Business Model
- Traffic monetization (advertising as primary revenue)
- Platform transaction fees (take rate on GMV)
- Subscription (membership, premium features)
- Cloud / enterprise services (secondary for some players)

## Required Capabilities
- Data-driven thinking: ability to decompose metrics, hypothesize causes, design experiments
- Cross-functional collaboration: work with product, engineering, sales, finance
- Fast iteration: comfort with ambiguity, A/B test culture, weekly or even daily release cadence
- User empathy: understanding why users behave the way they do, not just what they do

## Resume Keywords
DAU, MAU, retention rate, churn, conversion rate, A/B test, funnel analysis, GMV,
traffic allocation, CTR, CVR, ROAS, user segmentation, cohort analysis, LTV,
activation rate, D1/D7/D30 retention, NPS, feature adoption

## Interview Focus
- Case studies: metric decomposition, root cause analysis of metric drop
- Product sense: design a feature, critique an existing product
- Data interpretation: read a chart, identify anomalies, propose next steps
- Behavioral: cross-team collaboration, handling ambiguity, prioritization under constraints

## Risk Notes
- Intense competition: candidate pools are extremely large; generic resumes do not stand out
- Strong preference for quantifiable impact: vague bullets are screened out quickly
- Platform roles require deep knowledge of the specific product — generic answers fail
- Some large platforms have internal transfer restrictions; know which BU you are targeting

## Suitable Candidate Profile
Analytical, comfortable with ambiguity, strong communicator across functions,
genuine interest in product or data, can back up every claim with a number or
a specific example.
""",
            encoding="utf-8",
        )

    new_energy = industry_maps_dir() / "_example_new_energy.md"
    if not new_energy.exists():
        new_energy.write_text(
            """# Industry Map: New Energy / EV / Photovoltaic

## Overview
The New Energy sector encompasses electric vehicles, battery manufacturing, solar
photovoltaic production, and energy storage systems. It is a capital-intensive,
policy-sensitive, and rapidly evolving industry with strong government backing
in China and increasing global competitive pressure.

## Typical Companies
- Leading EV manufacturer (vertically integrated, sells direct-to-consumer)
- Large photovoltaic module producer (B2B, exports-heavy)
- Major battery manufacturer (supplies OEMs and energy storage projects)
- Energy storage system integrator (combines hardware, software, and service)
- Charging infrastructure operator

## Common Roles
- Supply Chain / Procurement (commodity sourcing, BOM management, supplier audit)
- Operations (manufacturing operations, logistics, after-sales)
- Market / Strategy Analysis (industry research, competitive intelligence)
- Product (hardware-software integration, in-vehicle software, energy management)
- Finance / Controlling (project economics, LCOE modeling, cost analysis)

## Business Model
- Product sales (vehicle, module, battery pack)
- Energy service subscription (e.g., battery-as-a-service, charging subscription)
- Carbon trading and green certificates
- EPC contracts for large-scale solar or storage installations

## Required Capabilities
- Supply chain thinking: understanding the full value chain from raw material to end customer
- Cost analysis: ability to model unit economics, BOM costs, yield rate impact
- Policy awareness: Chinese industrial policy, carbon market, green subsidy regimes
- Engineering literacy: ability to communicate with technical teams, understand product specs

## Resume Keywords
BOM, yield rate, capacity planning, carbon neutrality, LCOE (Levelized Cost of Energy),
energy density, cycle life, supply chain resilience, dual-source strategy,
carbon credit, ESG, EPC, grid parity, SOC (state of charge), VDA, IATF

## Interview Focus
- Industry knowledge: understanding of the competitive landscape, key players, technology trends
- Analytical thinking: cost modeling, scenario analysis, market sizing
- Project management: cross-functional coordination for product launches or supplier audits
- Case: "A key battery supplier announces a 30% price increase — what do you do?"

## Risk Notes
- Policy-sensitive: government subsidies can shift quickly; companies that depend on subsidies carry risk
- Rapid industry change: job scope may shift significantly as technology and market structure evolve
- Some roles in manufacturing-heavy companies have limited career ceiling for non-engineering talent
- International expansion is accelerating — language skills (especially English and German) are increasingly valued

## Suitable Candidate Profile
Analytical, comfortable with technical detail without being an engineer,
strong project management instincts, interested in physical products and
global supply chains, patient with long decision cycles.
""",
            encoding="utf-8",
        )

    finance = industry_maps_dir() / "_example_finance.md"
    if not finance.exists():
        finance.write_text(
            """# Industry Map: Finance / Securities / Fund / Fintech

## Overview
The finance sector in China spans four distinct sub-sectors with meaningfully different
cultures, candidate profiles, and career trajectories: securities (investment banking,
brokerage), public fund management, state-owned banking, and fintech platforms.
Understand which sub-sector you are targeting before packaging your resume.

## Typical Companies
- Mid-size securities brokerage (investment banking, research, asset management departments)
- Leading public fund manager (equity research, fixed income, quantitative strategies)
- Large state-owned bank (corporate banking, retail banking, digital transformation unit)
- Fintech payment platform (product, risk management, operations, data)

## Common Roles
- Research Analyst (sell-side or buy-side; sector coverage or macro)
- Investment Banking Analyst (deal execution, due diligence, financial modeling)
- Product Manager — Fintech (payment products, lending products, wealth management apps)
- Risk Management (credit risk, market risk, model risk)
- Operations / Compliance (process management, regulatory reporting)

## Sub-Sector Differences

| Sub-Sector | Culture | Rigor | Candidate Profile |
|------------|---------|-------|------------------|
| Securities / IB | Project-driven, client-facing, long hours | Very high | Strong modeling, detail-oriented, resilient |
| Public Fund | Research-heavy, autonomous, performance-driven | High (investment) | Independent thinker, strong quantitative or industry depth |
| State-owned Bank | Compliance-heavy, hierarchical, stable | Medium | Reliable, patient, comfortable with process |
| Fintech | Tech-forward, fast iteration, product-centric | High (tech) | Analytical, product sense, comfortable with ambiguity |

## Business Model
- Brokerage: transaction commissions, underwriting fees, margin lending interest
- Fund: management fee (% of AUM), performance fee (% of alpha)
- Bank: net interest margin, fee income, wealth management commissions
- Fintech: transaction take rate, lending spread, SaaS licensing for enterprise clients

## Required Capabilities
- Financial modeling: DCF, LBO, comparable company analysis, scenario modeling
- Regulatory knowledge: understanding of relevant regulatory frameworks (CSRC, CBIRC, PBOC)
- Data analysis: ability to work with financial data, build quantitative frameworks
- Communication: client-facing presentation, written research, board-level reporting

## Resume Keywords
AUM (assets under management), P&L, IRR (internal rate of return), due diligence,
compliance, risk-adjusted return, Sharpe ratio, drawdown, underwriting, NIM
(net interest margin), Basel III, stress testing, alpha, beta, KYC, AML,
fintech: DAU, transaction volume, credit scoring, NPL (non-performing loan ratio)

## Interview Focus
- Case studies: M&A scenario, investment thesis presentation, credit analysis
- Market knowledge: current interest rate environment, recent regulatory changes, sector trends
- Ethical reasoning: conflicts of interest, compliance scenarios, fiduciary duty
- Quantitative: financial modeling test, statistical reasoning (for quant or data roles)

## Risk Notes
- Regulatory exposure: policy changes can rapidly reshape revenue models (e.g., fee compression, fintech crackdowns)
- Cycle sensitivity: IB deal flow and fund performance are highly correlated with market conditions
- Some roles (especially in state-owned banks) have limited upward mobility for non-relationship-based talent
- Compliance requirements mean that certain activities and claims must be verified — take extra care with risk-level claims

## Suitable Candidate Profile
Detail-oriented, comfortable with quantitative work, strong written communication,
genuine interest in markets or financial products, high integrity and comfort
with compliance culture.
""",
            encoding="utf-8",
        )

    # --- role schemas ---
    role_schemas_dir().mkdir(parents=True, exist_ok=True)

    ad_ops = role_schemas_dir() / "_example_ad_ops.md"
    if not ad_ops.exists():
        ad_ops.write_text(
            """# Role Schema: Advertising Operations

## Role Category
Advertising / Marketing

## Sub-Role
Advertising Operations (Ad Ops)

## Overview
Ad Ops is responsible for the end-to-end execution of paid advertising campaigns.
This is an execution-heavy, data-heavy role that sits at the intersection of
marketing strategy and technical platform management.

## Required Capabilities
- Campaign setup and trafficking on major ad platforms (search, social, programmatic)
- Budget pacing and allocation across campaigns and time periods
- Performance monitoring and anomaly detection
- A/B testing of creatives, audiences, bidding strategies
- Reporting and data visualization for internal and external stakeholders

## Preferred Experiences
- Hands-on experience managing live campaigns with real budget (even small amounts)
- Experience pulling and interpreting platform-native analytics
- Any exposure to SQL or BI tools for custom reporting
- Self-initiated analysis of public ad datasets

## Keywords
CTR (click-through rate), CVR (conversion rate), ROAS (return on ad spend),
ACOS (advertising cost of sales), CPC (cost per click), CPM (cost per thousand impressions),
impression share, budget utilization, frequency cap, retargeting, lookalike audience,
search term report, negative keywords, Quality Score, attribution model

## Common Metrics
- CTR: benchmark varies by platform and format (search ~2-5%, display ~0.1%)
- CVR: depends heavily on landing page and product; track trends not absolutes
- ROAS: target varies by margin; e-commerce typically targets 3-5x
- Budget pacing: % of daily budget spent by end of day, ideal 90-105%
- Impression share: how often your ad showed vs. total eligible impressions

## Interview Focus
- Platform familiarity: "Walk me through how you would set up a search campaign"
- Metrics interpretation: "CTR dropped 30% WoW — what do you check first?"
- Case scenario: "Your campaign is under-spending with 2 days left in the month — what do you do?"
- Optimization logic: "How do you decide when to pause a creative?"

## Portfolio Suggestions
- Mock campaign analysis: take a hypothetical campaign brief, design the campaign structure, targeting, and bidding strategy in a document
- Public dataset optimization: use Google Ads or Facebook Ads public case data to build an analysis
- Performance dashboard: build a sample KPI dashboard in Excel, Google Sheets, or a public BI tool
- Write-up: "What I would do to improve campaign X" using publicly available information only
""",
            encoding="utf-8",
        )

    user_ops = role_schemas_dir() / "_example_user_ops.md"
    if not user_ops.exists():
        user_ops.write_text(
            """# Role Schema: User Operations

## Role Category
Operations (User / Content / Activity)

## Sub-Role
User Operations (用户运营)

## Overview
User Operations manages the full user lifecycle — from acquisition and activation
through retention, monetization, and win-back. It is a data-informed, experiment-driven
function that requires both analytical skill and empathy for user psychology.

## Required Capabilities
- User lifecycle management: mapping stages from registration to loyal user
- Retention campaign design and execution (push, email, in-app messaging)
- Churn analysis: identifying at-risk users, root cause investigation
- Community management: forums, group chats, events (for consumer products)
- User feedback loops: collecting, synthesizing, and routing user insights to product

## Preferred Experiences
- Any experience managing a user-facing product, campaign, or community
- Analysis of user behavior data (cohort analysis, funnel drop-off)
- Experience designing or evaluating a retention or re-engagement campaign
- Interviews or surveys with end users

## Keywords
DAU, MAU, retention rate, churn rate, LTV (lifetime value), activation rate,
NPS (Net Promoter Score), D1/D7/D30 retention, ARPU (average revenue per user),
push notification, in-app message, user segmentation, cohort, win-back campaign,
user journey, lifecycle stage

## Common Metrics
- D1 Retention: % of new users who return the next day; benchmark varies by product type
- D30 Retention: % of new users still active after 30 days; <10% is typical for social apps
- Churn Rate: % of active users who lapse in a given period
- LTV: total revenue or engagement value from a user over their active lifetime
- Activation Rate: % of registered users who complete a key first action

## Interview Focus
- User insight questions: "Why do users churn in the first 7 days — what would you investigate?"
- Retention scenario: "Design a campaign to improve D7 retention by 10%"
- Cross-team collaboration: "How would you work with product to prioritize a retention feature?"
- Metrics decomposition: "DAU dropped 15% — walk me through your diagnostic process"

## Portfolio Suggestions
- Retention analysis: take a public dataset with user event logs, build a cohort retention analysis, identify the biggest drop-off, propose interventions
- User segmentation: segment users by behavior, describe each segment's profile, recommend different treatment
- Campaign design document: design a full re-engagement campaign for a hypothetical product — targeting, messaging, channel, success metrics
""",
            encoding="utf-8",
        )

    data_analyst = role_schemas_dir() / "_example_data_analyst.md"
    if not data_analyst.exists():
        data_analyst.write_text(
            """# Role Schema: Data Analyst

## Role Category
Data Analysis / Business Analysis

## Sub-Role
Data Analyst (数据分析师)

## Overview
Data Analysts translate raw business data into actionable insights. The role spans
extraction, transformation, visualization, and communication of findings to non-technical
stakeholders. Increasingly, it also includes experiment design and analysis (A/B testing).

## Required Capabilities
- Data extraction: SQL queries across relational databases (joins, aggregations, window functions)
- Metric tracking: building and maintaining dashboards for business KPIs
- Ad hoc analysis: answering specific business questions quickly and clearly
- A/B test analysis: interpreting experiment results, checking statistical validity
- Business reporting: presenting findings in clear narratives, not just charts

## Preferred Experiences
- End-to-end analysis project: from data pull to recommendation
- SQL proficiency demonstrated through real or portfolio projects
- Dashboard or report built for a real audience (even academic or club context counts)
- Any exposure to A/B test design or statistical significance testing

## SQL Requirements
- Comfortable: SELECT, WHERE, GROUP BY, ORDER BY, HAVING, LIMIT
- Required: INNER/LEFT/RIGHT JOIN, multi-table queries
- Expected for mid-level: window functions (ROW_NUMBER, RANK, LAG, LEAD, SUM OVER)
- Strong plus: CTEs (WITH clauses), subqueries, CASE WHEN, query optimization

## Python (Optional but Valued)
- pandas: data manipulation, groupby, merge
- matplotlib / seaborn: basic visualization
- scipy / statsmodels: statistical tests (optional but differentiating)
- scikit-learn: basic modeling (optional; more relevant for "data scientist" roles)

## Common Metrics
- Funnel conversion rate at each step
- Cohort retention curves
- Revenue attribution by channel or feature
- A/B test: lift %, p-value, confidence interval, required sample size
- Anomaly detection: week-over-week change, seasonality adjustment

## Interview Focus
- SQL problems: live coding or take-home query challenges (expect JOINs and window functions)
- Metric decomposition: "Revenue dropped 20% MoM — how do you investigate?"
- Case analysis: given a dataset or scenario, derive an insight and present a recommendation
- Statistics basics: p-value, confidence interval, Type I/II error, when to stop an experiment

## Portfolio Suggestions
- End-to-end public dataset analysis: Kaggle, government open data, Mode Analytics public datasets
  - Show: data cleaning → SQL or pandas analysis → visualization → written recommendation
- Dashboard in public BI tool: Tableau Public or Metabase with public dataset
- A/B test analysis write-up: design + run + interpret a simulated experiment
- SQL query library: GitHub repository with commented, well-structured SQL queries on real datasets
""",
            encoding="utf-8",
        )

    # --- capability roadmaps ---
    capability_roadmaps_dir().mkdir(parents=True, exist_ok=True)

    ab_testing = capability_roadmaps_dir() / "_example_ab_testing.md"
    if not ab_testing.exists():
        ab_testing.write_text(
            """# Capability Roadmap: A/B Testing

## What This Capability Is
A/B testing (controlled experimentation) is the practice of randomly assigning users
to treatment and control groups to measure the causal effect of a product or marketing change.
It is foundational for data-driven product and operations roles at tech companies.

## What to Learn

### Core Concepts
- Hypothesis design: null hypothesis, alternative hypothesis, directional vs. non-directional tests
- Experiment setup: control group, treatment group, holdout period
- Sample size calculation: power analysis, effect size, significance level (α), power (1-β)
- Statistical significance: p-value, confidence interval (95% CI), t-test basics
- Practical significance vs. statistical significance: a result can be statistically significant but business-irrelevant

### Common Pitfalls
- Novelty effect: users behave differently because something is new, not because it is better
- Network effects / interference: treatment group users affect control group users (social products)
- Peeking: stopping the experiment early when results look good (inflates false positive rate)
- Multiple testing problem: running many tests increases the chance of false positives
- Selection bias: non-random assignment corrupts the experiment

### Statistics Foundations
- Central Limit Theorem (why sample means are normally distributed)
- Z-test vs. T-test (large vs. small samples)
- Chi-square test for proportions (e.g., CTR, conversion rate)
- Bonferroni correction or FDR control for multiple comparisons

## Public Datasets to Practice With
- Kaggle: search "A/B test dataset" — there are several e-commerce click datasets
- UCI Machine Learning Repository: behavioral datasets suitable for experiment simulation
- Mode Analytics public datasets: SQL-accessible product event logs
- Any product event log with timestamps and user IDs can be used to simulate an A/B test

## How to Frame as a Portfolio Project

"Designed and analyzed a simulated A/B test on [public dataset] to evaluate [feature change].
Calculated required sample size using power analysis (α=0.05, power=0.80, expected lift=5%),
ran the test for [X days / Y users], and concluded [result] with 95% confidence interval
[lower bound, upper bound]. Identified [novelty effect / underpowered sample / etc.] as a
key consideration and adjusted interpretation accordingly."

## Resume Bullet Examples
- "Designed A/B test framework for [feature], achieving statistical significance at n=X with p<0.05"
- "Identified novelty effect in experiment causing inflated 7-day retention; revised holdout period and recalculated true lift at +2.1%"
- "Built power analysis tool in Python to pre-calculate required sample sizes for 12 concurrent experiments, reducing underpowered test rate by 40%"
- "Ran 3 A/B tests on push notification copy; winning variant improved D7 retention by 1.8pp (95% CI: 0.6pp–3.0pp)"

## Claim Level Guide for A/B Testing Claims
- **Green**: You personally designed and analyzed a real or well-documented portfolio experiment with correct methodology
- **Yellow**: You assisted on an A/B test but did not own the analysis or design
- **Red**: You observed a test result without understanding the statistical methodology — do not claim
- **Buildable**: Complete a public dataset experiment and document it fully — this becomes Green within 2-3 weeks

## Estimated Build Time
2-4 weeks to go from zero to defensible portfolio project:
- Week 1: Learn core concepts (online resources: Udacity A/B Testing course, Khan Academy stats)
- Week 2: Complete a power analysis and design a simulated experiment
- Week 3: Run the analysis on a public dataset, document findings
- Week 4: Write up and publish (GitHub, portfolio site, or PDF)
""",
            encoding="utf-8",
        )

    sql_analytics = capability_roadmaps_dir() / "_example_sql_analytics.md"
    if not sql_analytics.exists():
        sql_analytics.write_text(
            """# Capability Roadmap: SQL Analytics

## What This Capability Is
SQL (Structured Query Language) is the primary tool for extracting and analyzing
data from relational databases. It is a required skill for data analyst roles and
a strong differentiator for operations and product roles.

## What to Learn

### Foundational SQL (Must Know)
- SELECT, FROM, WHERE, ORDER BY, LIMIT
- Aggregate functions: COUNT, SUM, AVG, MIN, MAX
- GROUP BY, HAVING
- DISTINCT, AS (aliases)
- String functions: CONCAT, UPPER, LOWER, TRIM, LIKE
- Date functions: DATE_TRUNC, DATEDIFF, DATE_ADD, EXTRACT

### Intermediate SQL (Expected for Analyst Roles)
- JOINs: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN
- Multi-table queries with multiple JOINs
- Subqueries (in SELECT, WHERE, FROM clauses)
- CASE WHEN / ELSE / END (conditional logic)
- NULL handling: IS NULL, IS NOT NULL, COALESCE, NULLIF

### Advanced SQL (Differentiating)
- Window functions:
  - Ranking: ROW_NUMBER(), RANK(), DENSE_RANK()
  - Aggregation over partitions: SUM() OVER, AVG() OVER
  - Lag/lead: LAG(), LEAD() for period-over-period comparison
  - Running totals, moving averages
- CTEs (Common Table Expressions): WITH clause for readable multi-step queries
- Query optimization: indexing concepts, avoiding full table scans, EXPLAIN plans

## Public Datasets to Practice With
- Mode Analytics Public Warehouse: free SQL environment with real-world datasets (yammer, marketing)
- BigQuery Public Datasets: massive datasets accessible via free tier (Wikipedia, GitHub, NOAA)
- Kaggle SQL courses: guided SQL practice in notebook environment
- SQLZoo / LeetCode SQL: structured problem sets from basic to advanced
- PostgreSQL Tutorial datasets: downloadable practice databases (DVD rental, Northwind)

## How to Frame as a Portfolio Project

"Built an end-to-end funnel analysis using SQL on [public dataset], identifying the largest
drop-off point (Step 3: checkout initiation at 34% conversion) and estimating revenue impact
of a 5pp improvement at approximately $X in annual incremental revenue. Used CTEs to modularize
the query and window functions to calculate rolling 7-day retention by acquisition cohort."

## Resume Bullet Examples
- "Built automated daily retention report using SQL window functions, reducing manual reporting time by 80%"
- "Wrote multi-step CTE query to segment 500K+ users by behavioral cohort for targeted re-engagement campaign"
- "Identified 3 anomalies in weekly GMV trend using SQL-based diagnostic framework; root cause was a misconfigured promo code"
- "Designed SQL data model for marketing attribution, joining 4 tables to produce single-source-of-truth channel performance view"

## Claim Level Guide for SQL Claims
- **Green**: You can write a correct multi-table JOIN query with window functions under time pressure in an interview
- **Yellow**: You can write basic aggregation queries but need documentation for window functions
- **Red**: You have only used GUI tools (Tableau, etc.) and cannot write SQL from scratch — do not claim
- **Buildable**: 3-4 weeks of focused practice on Mode or LeetCode SQL gets most people to Green for analyst interviews

## Estimated Build Time
3-5 weeks to go from zero to defensible interview-ready SQL:
- Week 1: Complete SQLZoo or Mode SQL Tutorial (foundations)
- Week 2: Practice JOINs and subqueries on real datasets (Mode Analytics public data)
- Week 3: Learn and practice window functions (LeetCode Hard SQL problems)
- Week 4: Build a portfolio project using CTEs and window functions on a public dataset
- Week 5: Timed SQL practice (simulate interview conditions — 20 min per problem)
""",
            encoding="utf-8",
        )

    # --- question bank ---
    question_bank_dir().mkdir(parents=True, exist_ok=True)

    role_questions = question_bank_dir() / "_example_role_questions.md"
    if not role_questions.exists():
        role_questions.write_text(
            """# Question Bank: Operations Role (Generic)

This question bank covers common interview questions for operations roles
(user ops, content ops, activity ops, growth ops). Use this as a starting
point and adapt for the specific company and sub-role.

---

## Background & Motivation

1. Walk me through your background and why you are interested in an operations role.
2. What do you understand this role to involve day-to-day? How does that match your expectations?
3. Why are you interested in this specific company and this specific product?
4. What experience do you have that is most directly relevant to this role?
5. What is the biggest gap between your current background and the ideal candidate for this role? How are you addressing it?

---

## Role Understanding

1. What do you think the primary goal of the operations team is at a company like this?
2. How would you describe the difference between user operations and product management?
3. What metrics would you use to evaluate the health of this product's user base?
4. If you were joining this team tomorrow, what would you want to understand in your first two weeks?
5. What does a "good" operations outcome look like for this type of product?

---

## Behavioral / STAR Format

1. Tell me about a time you had to work with a team to solve a problem you did not fully understand at first.
2. Describe a situation where data led you to change your initial conclusion.
3. Tell me about a project where you had to manage competing priorities with limited time.
4. Give an example of a time you identified a user pain point and took action to address it.
5. Describe a situation where you had to push back on a stakeholder's request. How did you handle it?

---

## Case / Scenario

1. DAU on a social product dropped 15% week-over-week with no major product changes. Walk me through how you would investigate.
2. You have been asked to design a campaign to improve 7-day retention for new users. How do you approach this?
3. You have a budget of 50,000 RMB for a user activation campaign. How do you decide where to spend it?
4. A user segment that used to be highly active has gone quiet over the past month. How do you find out why?
5. The product team wants to launch a new feature in 2 weeks. What do you need to prepare from the operations side?

---

## Data & Metrics

1. What is the difference between a user being "active" and a user being "retained"?
2. If MAU is growing but DAU/MAU ratio is declining, what could that mean?
3. How would you calculate LTV for a subscription product? What assumptions would you need to make?
4. You are comparing two user acquisition channels. Channel A has lower CPA but lower D30 retention. How do you decide which to prioritize?
5. An A/B test shows a positive result with p=0.04. The test ran for 5 days with n=500 users per group. Would you roll out the feature? Why or why not?

---

## Questions to Ask the Interviewer

1. What does success look like in the first 90 days for someone in this role?
2. How does the operations team collaborate with product and engineering here? What does that process look like in practice?
3. What is the biggest operational challenge the team is facing right now?
4. How does the team measure the impact of operations work on business outcomes?
5. What are the most common reasons people in this role struggle or leave within the first year?
""",
            encoding="utf-8",
        )

    # --- company dossiers example ---
    example_company = company_dossiers_dir() / "_example_company.md"
    if not example_company.exists():
        example_company.write_text(
            """# Company Dossier: [COMPANY NAME]

**Industry**: [Fill in: e.g., Internet / E-commerce / New Energy / Finance]
**Ticker**: [Fill in stock ticker, or N/A if private]
**Last Updated**: [Fill in date every time you update this file]

---

## Basic Profile
| Field | Value |
|-------|-------|
| Full Name | [Official registered company name] |
| Ownership Type | [State-owned / Private / Listed / Foreign / Joint Venture] |
| Founded | [Year] |
| Headquarters | [City, Country] |
| Employee Count | [Approximate — use public filings or LinkedIn] |
| Revenue Scale | [Approximate annual revenue — use public filings only] |

## Business Segments
<!-- List the main business units or product lines based on public annual reports or official website -->
<!-- Do not speculate about confidential internal structure -->

- Segment 1: [Name and brief description]
- Segment 2: [Name and brief description]
- Segment 3: [Name and brief description]

## Organization Map
<!-- Describe the known organizational structure relevant to job seekers -->
<!-- Use public information only: org charts, LinkedIn, official site, public job postings -->
<!-- Mark anything uncertain as "(hypothesis)" -->

[Fill in what you can find from public sources. Note date of research.]

## Recruiting Role Map
<!-- Which roles does this company typically hire, by business unit? -->
<!-- Base this on job postings, official careers page, LinkedIn data -->

| Business Unit | Common Roles | Typical Headcount Season |
|---------------|-------------|-------------------------|
| [BU Name] | [Role 1, Role 2] | [e.g., Autumn / Spring / Rolling] |
| | | |

## Business Unit Differences
<!-- How do different BUs differ in culture, rigor, and candidate profile? -->
<!-- Mark everything here as hypothesis unless sourced from public info -->
<!-- Do not record confidential, internally-sourced, or personal employee information -->

[Fill in based on public information. Label each point as (confirmed) or (hypothesis).]

## Public Sources
<!-- Links or references to annual reports, investor relations, official news -->
<!-- Only include publicly accessible sources — no internal documents -->

- [ ] Annual Report: [URL or file path]
- [ ] Investor Day slides: [URL or file path]
- [ ] Official careers page: [URL]
- [ ] LinkedIn company page: [URL]
- [ ] Other: [Description and URL]

## Social / Employee Signals
> ⚠️ WARNING: This section contains low-confidence, scope-limited signals.
> Sources: employee posts, third-party forums, recruiting platforms.
> Do not treat as authoritative. Verify through official channels.
> Do not record confidential or internally-sourced information here.
> Each entry must include: source, date, and confidence assessment.

<!-- Example entry format: -->
<!-- - [SOURCE] [DATE]: "[Summary of signal]" — Confidence: Low | Scope: [Role/BU/Region] -->

## Resume Strategy
<!-- How to frame your resume for this company -->
<!-- Consider: what they value, what they screen for, how to stand out -->
<!-- Base this on JD patterns and public company narrative — not speculation -->

[Fill in after reviewing at least 3 job postings and the company's official strategic narrative.]

## Interview Preparation
<!-- Known interview formats, focus areas, and preparation tips -->
<!-- Use only publicly available information (e.g., official recruitment events, public prep guides) -->

[Fill in based on public sources only.]

## Risk Notes
<!-- Any red flags, instability signals, or reasons to proceed carefully -->
<!-- Include: recent news, financial signals, regulatory actions, layoff reports (from public sources) -->

[Fill in based on public news and filings only.]
""",
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# Strategy files (standalone)
# ---------------------------------------------------------------------------

# (create_strategy_files defined above)

# ---------------------------------------------------------------------------
# Core public API
# ---------------------------------------------------------------------------

def initialize_project(answers: dict) -> None:
    """
    Orchestrate full project initialization.

    answers dict keys:
        stage: str
        industries: List[str]
        roles: List[str]
        company_count: int
    """
    create_all_folders()
    create_master_profile_files()
    create_strategy_files()
    create_readme_files()
    create_example_files()

    # Generate one pipeline per selected industry × role combination
    # Strategy: create one pipeline per industry, using the first selected role
    industries: list = answers.get("industries", [])
    roles: list = answers.get("roles", [])

    primary_role = roles[0] if roles else "General"

    for industry in industries:
        slug = _slugify(industry)
        pipeline_name = slug
        try:
            create_pipeline(pipeline_name, industry, primary_role)
        except FileExistsError:
            pass  # Already exists — skip silently during init

    mark_initialized()


def create_pipeline(name: str, industry: str, role_category: str) -> "Path":
    """Create pipelines/{name}.md. Raises FileExistsError if already exists."""
    from pathlib import Path as _Path
    pdir = pipelines_dir()
    pdir.mkdir(parents=True, exist_ok=True)
    file_path = pdir / f"{name}.md"
    if file_path.exists():
        raise FileExistsError(f"Pipeline already exists: {file_path}")
    content = pipeline_template(name, industry, role_category)
    file_path.write_text(content, encoding="utf-8")
    return file_path


def create_application(
    company: str,
    role: str,
    date_str: str,
    channel: str,
    pipeline: str,
) -> "Path":
    """
    Create the application folder and all 11 working files.
    Raises FileExistsError if the application folder already exists.
    """
    adir = applications_dir()
    adir.mkdir(parents=True, exist_ok=True)

    # Folder name: {date}_{company}_{role} slugified
    folder_name = _slugify(f"{date_str}_{company}_{role}")
    app_folder = adir / folder_name

    if app_folder.exists():
        raise FileExistsError(f"Application folder already exists: {app_folder}")

    app_folder.mkdir(parents=True)

    files = application_files()
    for filename, content in files.items():
        (app_folder / filename).write_text(content, encoding="utf-8")

    return app_folder


def create_company_dossier(
    company: str, industry: str, ticker: str | None = None
) -> "Path":
    """Create the dossier file. Raises FileExistsError if already exists."""
    dossier_dir = company_dossiers_dir()
    dossier_dir.mkdir(parents=True, exist_ok=True)
    file_path = dossier_dir / f"{company}.md"
    if file_path.exists():
        raise FileExistsError(f"Dossier already exists: {file_path}")
    content = company_dossier_template(company, industry, ticker)
    file_path.write_text(content, encoding="utf-8")
    return file_path


def import_signal(file_path: str, pipeline: str) -> "Path":
    """
    Copy a signal file into imported/. Update the pipeline file with a log entry.
    Raises FileExistsError if destination file already exists.
    """
    src = Path(file_path)
    imported_dir = external_signals_dir() / "imported"
    imported_dir.mkdir(parents=True, exist_ok=True)

    dest = imported_dir / src.name
    if dest.exists():
        raise FileExistsError(f"Signal file already exists in imported/: {dest}")

    shutil.copy2(str(src), str(dest))

    # Append a log entry to the pipeline file
    pipeline_file = pipelines_dir() / f"{pipeline}.md"
    if pipeline_file.exists():
        existing = pipeline_file.read_text(encoding="utf-8")
        log_entry = f"\n<!-- Signal imported: {src.name} — {dest} -->\n"
        pipeline_file.write_text(existing + log_entry, encoding="utf-8")

    return dest
