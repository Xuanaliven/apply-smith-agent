# External Signals

This folder stores external intelligence files — market research, job description archives, news articles, industry reports, and other inputs that inform your strategy but are not part of your master profile or pipeline files.

## What Counts as a Signal

- Job description PDFs or text files you saved from a posting
- News articles about a target company (funding, layoffs, strategy pivots)
- Industry reports or whitepapers
- Screenshots or notes from recruiter conversations (remove identifying info)
- Salary benchmarking data from public sources
- Competitor analysis notes

## What Does NOT Belong Here

- Confidential information received privately from employees
- Internal company documents obtained without authorization
- Personally identifiable information about individuals at target companies

## How to Import a Signal

Use the CLI:

```bash
applysmith import-signal --file path/to/signal.md --pipeline "internet-platform"
```

This will:
1. Copy the file into `data/external_signals/imported/`
2. Add a reference note in the specified pipeline file

## Folder Structure

```
external_signals/
  imported/          ← all imported signal files land here
  README.md          ← this file
```

## Naming Convention

When importing, use descriptive filenames:
- `2024-03_bytedance_layoff_news.md`
- `2024-04_ads-ops-JD-from-linkedin.md`
- `2024-05_internet-sector-salary-benchmark.md`

## Confidentiality Reminder

Never record or store information that was shared with you in confidence. If a contact tells you something about their employer that they would not want shared publicly, keep it in your head — not in this system.
