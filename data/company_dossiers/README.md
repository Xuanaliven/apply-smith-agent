# Company Dossiers

This folder contains research files for companies you are actively targeting or considering.

## What a Dossier Is

A company dossier is a structured research document that captures publicly available information about a company — its business model, organizational structure, recruiting patterns, and strategic direction. It serves as your reference when tailoring resumes, preparing for interviews, and making targeting decisions.

## How to Create a Dossier

Use the CLI command:

```bash
applysmith new-company-dossier --company "CompanyName" --industry "Finance" --ticker "TICKER"
```

This generates a pre-structured file at `data/company_dossiers/CompanyName.md`.

## Rules for This Folder

1. **Public information only.** Use annual reports, investor relations materials, official news, careers pages, and LinkedIn company profiles.
2. **Mark low-confidence signals clearly.** Any information from employee forums, social media, or peer word-of-mouth must be labeled as low-confidence in the Social / Employee Signals section.
3. **Do not record confidential information.** Never record anything learned from employees that was shared privately or that the company would consider sensitive.
4. **Keep dossiers up to date.** Add a "Last Updated" date and refresh before each interview cycle.
5. **One file per company.** Use the company's common name as the filename (e.g., `ByteDance.md`, `Goldman_Sachs.md`).

## Example File

See `_example_company.md` for the full template with all sections.

## Relationship to Applications

When creating a new application, you will create a snapshot (`03_company_dossier_snapshot.md`) inside the application folder. This snapshot captures the state of the dossier at application time — because companies change and you want a record of what you knew when you applied.
