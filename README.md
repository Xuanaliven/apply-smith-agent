# ApplySmith

A local Career Strategy OS for job seekers.

ApplySmith is a CLI tool for managing a rigorous, JD-first job search. No LLM API. No web UI. No database. Everything lives in markdown files that you own.

---

## Philosophy

Most job search tools treat the resume as the starting point. ApplySmith treats the job description as the starting point.

The result is a system built around three honest questions:

1. **What can I honestly claim right now?** (Current ceiling)
2. **What can I claim with better framing of what I already have?** (Packaging ceiling)
3. **What can I claim after deliberate practice over the next 4–8 weeks?** (Buildable ceiling)

ApplySmith will not flatter you. If your profile does not fit a role, it will tell you that — and then help you decide whether to close the gap or redirect your effort.

---

## Quick Start

### Install

```bash
cd your-job-search-folder
pip install /path/to/apply-smith-agent
```

Or install in development mode from the project root:

```bash
pip install -e ".[dev]"
```

### Initialize

```bash
applysmith init
```

This runs an onboarding questionnaire and sets up your folder structure, starter pipelines, and example files.

### Verify

```bash
applysmith hello
# ApplySmith is ready.
```

---

## All Commands

### `applysmith hello`

Check that the tool is installed and ready.

```bash
applysmith hello
```

---

### `applysmith init`

Initialize ApplySmith in the current directory. Runs the onboarding questionnaire first, then generates your folder structure, pipelines, and role schemas based on your answers.

```bash
applysmith init
```

If already initialized, prints a warning and stops. Will not overwrite existing files.

---

### `applysmith new-pipeline`

Create a new career pipeline for a specific industry and role category.

```bash
applysmith new-pipeline \
  --name "internet-data" \
  --industry "Internet / Platform" \
  --role-category "Data Analysis / Business Analysis"
```

Creates `pipelines/internet-data.md` with all required sections.

---

### `applysmith new-application`

Create a new application folder with all 11 working files.

```bash
applysmith new-application \
  --company "Meituan" \
  --role "Data Analyst" \
  --date "2024-03-15" \
  --channel "campus-portal" \
  --pipeline "internet-data"
```

Creates `applications/2024-03-15_Meituan_Data-Analyst_campus-portal/` with:

```
01_jd_original.md          ← paste the full JD here
02_jd_analysis.md          ← break down requirements and keywords
03_company_dossier_snapshot.md
04_business_unit_hypothesis.md
05_ideal_candidate.md
06_selected_experiences.md
07_tailored_resume.md
08_claim_check_report.md   ← every claim needs a risk level
09_interview_defense.md
10_question_bank_links.md
11_application_log.md
```

---

### `applysmith new-company-dossier`

Create a new company research file.

```bash
applysmith new-company-dossier \
  --company "ByteDance" \
  --industry "Internet / Platform" \
  --ticker "unlisted"
```

Creates `data/company_dossiers/ByteDance.md`.

---

### `applysmith import-signal`

Import an external signal file (news article, job posting, industry report) into the project and link it to a pipeline.

```bash
applysmith import-signal \
  --file ~/Downloads/meituan-layoff-news.md \
  --pipeline "internet-data"
```

Copies the file to `data/external_signals/imported/` and adds a reference in the specified pipeline file.

---

## File Structure

```
your-project/
  data/
    master_profile/       ← your background inventory (fill this in)
    industry_maps/        ← industry research cards
    role_schemas/         ← role requirement breakdowns
    capability_roadmaps/  ← how to build specific skills
    company_dossiers/     ← public research on target companies
    company_sources/      ← raw source files (JDs, annual reports, etc.)
    question_bank/        ← interview question collections by role
    external_signals/     ← imported intelligence files

  pipelines/              ← one file per industry+role track
  strategy/               ← target map, opportunity scores, weekly plan
  applications/           ← one folder per application, 11 files each
```

### Files Prefixed with `_example_`

These are reference templates showing correct format and realistic placeholder content. Copy and rename them to create your own files. Do not edit the example files directly.

---

## Guiding Principles

See `AGENTS.md` for the full operating rules. Key principles:

- **JD-first**: every application starts with a real job description
- **Three ceilings**: distinguish current, packaging, and buildable ceiling
- **Claim validation**: every resume claim gets a risk level (Green / Yellow / Red / Buildable / Stretch)
- **Public info only**: company dossiers use only public sources
- **No flattery**: if the fit is weak, the system says so

---

## Running Tests

```bash
pytest
```

All tests run in isolated temporary directories and do not touch your actual project files.

---

## Contributing

This is Phase 0. Contributions should follow the rules in `AGENTS.md`. The core constraint: no LLM API, no web UI, no database. Markdown files only.
