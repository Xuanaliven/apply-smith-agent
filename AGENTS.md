# AGENTS.md — ApplySmith Operating Rules

This document defines the operating principles for ApplySmith and any agents or processes that interact with it. All users, contributors, and AI agents working with this system must follow these rules.

---

## 1. ApplySmith Is a Career Strategy OS, Not a Resume Beautifier

ApplySmith's job is to help you make better targeting decisions, identify real capability gaps, and build a defensible case for the roles you pursue. It is not a tool for making a weak profile look stronger than it is.

If your background does not match a role, ApplySmith should tell you that clearly — and then help you decide whether to close the gap, reframe what you have, or target a different role.

**What this means in practice:**
- Do not use ApplySmith just to generate a polished resume from scratch
- Always start with a JD, not with your profile
- Use the ceiling framework honestly: current ceiling, packaging ceiling, buildable ceiling

---

## 2. Workflow Is JD-First, Not Profile-First

Every application starts with a real job description. You analyze the JD, form a business unit hypothesis, reconstruct the ideal candidate profile, and only then select from your experience atoms.

The profile-first approach (polish your resume, then spray it everywhere) is what ApplySmith is designed to replace. A master profile exists in this system only as a retrieval and validation source — not as a starting point for any individual application.

**Order of operations:**
1. Find a real JD
2. Analyze the JD (`02_jd_analysis.md`)
3. Form business unit hypothesis (`04_business_unit_hypothesis.md`)
4. Reconstruct ideal candidate (`05_ideal_candidate.md`)
5. Select experience atoms (`06_selected_experiences.md`)
6. Build the tailored resume (`07_tailored_resume.md`)
7. Validate all claims (`08_claim_check_report.md`)

---

## 3. Master Profile Is for Retrieval and Validation Only

The master profile (`data/master_profile/`) is a structured inventory of what you have done, what tools you have used, and what you can honestly claim. It is a library, not a ceiling.

**What this means:**
- You may aspire to roles that your master profile does not currently support
- Aspiration is fine — but it must be labeled honestly (Buildable or Stretch level)
- The master profile should reflect reality, not your best-case self-description
- If you build a new capability, update the master profile with a new experience atom

---

## 4. The System Must Give Faithful Advice, Not Flattery

If a user's profile is weak for a role, the system should say so clearly. If a claim cannot be defended in an interview, the claim must be flagged as Red. If a capability gap exists, it should be documented — not glossed over.

This system is only valuable if the user can trust its assessments. Inflating confidence levels to make users feel better is actively harmful — it leads to claims that collapse under interview pressure.

---

## 5. Support Multi-Thread Recruiting Pipelines

Job seekers should pursue multiple directions simultaneously. ApplySmith supports parallel pipelines across different industries and role types. Each pipeline has its own:
- Opportunity score
- Capability gap analysis
- Weekly action items
- Application records

Managing multiple pipelines is not spreading thin — it is intelligent risk management during a high-stakes search.

---

## 6. Distinguish the Three Ceilings

Every pipeline and application must distinguish between three levels:

| Ceiling | Definition |
|---------|-----------|
| **Current Ceiling** | What you can honestly claim right now, fully supported by evidence you can defend in an interview |
| **Packaging Ceiling** | What you can claim after better framing of existing experience — no new work required, just clearer articulation |
| **Buildable Ceiling** | What you can claim after 4–8 weeks of deliberate capability building (portfolio projects, self-initiated work, public datasets) |

Anything above the buildable ceiling requires more than 8 weeks of work and is a long-term development goal, not a near-term resume strategy.

---

## 7. Simulated Projects Must Be Labeled Clearly

Portfolio projects, self-initiated analyses, and capability-building exercises are legitimate and valuable — but they must be labeled honestly.

**Acceptable labels:**
- "Portfolio project — self-initiated"
- "Independent analysis using [public dataset]"
- "Personal project: [description]"

**Not acceptable:**
- Presenting a portfolio project as a real company internship
- Attributing work done on a public dataset to a real employer
- Claiming a team project as solo work

Misrepresenting the nature of work is a claim integrity violation. It is not just an ethical problem — it is a practical one. Interviewers probe for context, and false context collapses immediately.

---

## 8. Every Resume Claim Needs a Source and a Risk Level

Every factual claim in a tailored resume must have a corresponding entry in `08_claim_check_report.md` with:

- **Source**: which experience atom or project it comes from
- **Claim Level**: one of Green / Yellow / Red / Buildable / Stretch

| Level | Meaning |
|-------|---------|
| Green | Fully evidenced; can be defended in detail under pressure |
| Yellow | Partially evidenced; requires careful framing; prepare caveats |
| Red | Not currently supported by evidence; do not include |
| Buildable | Can be earned with deliberate practice; label as portfolio/self-initiated |
| Stretch | Possible with significant effort; use only if there is time before the application |

No claim should appear in the final resume without a claim level assessment.

---

## 9. Company Dossiers Use Public Information Only

`data/company_dossiers/` contains research on target companies. All entries must be sourced from:
- Official annual reports and financial disclosures
- Investor relations materials (earnings calls, investor day presentations)
- Official company news and press releases
- Official careers page and job postings
- LinkedIn company page (public information only)

**Not acceptable sources for Company Dossiers:**
- Information shared privately by current or former employees
- Internal documents obtained without authorization
- Unverified rumors or speculation presented as fact

---

## 10. Social / Employee Signals Are Low-Confidence

The Social / Employee Signals section in every company dossier must carry an explicit warning that its contents are low-confidence and scope-limited. Sources include employee forum posts, third-party review platforms, and peer word-of-mouth. These signals:

- Cannot be verified
- May be outdated, biased, or from edge cases
- Should never be cited as facts to others
- Should never override official public information

Always label the source and date of each signal. Treat the section as a hypothesis list, not a fact sheet.

---

## 11. Do Not Record or Spread Confidential Information

ApplySmith is a personal tool. It should never become a vehicle for recording, organizing, or spreading information that:
- Was shared with you in confidence by someone at a target company
- Is internal to a company and not intended for public disclosure
- Could damage an individual's reputation or a company's competitive position

If you receive information that feels confidential, keep it out of the system.

---

## 12. ApplySmith Does Not Scrape Social Media

ApplySmith is a local strategy tool. It does not scrape, crawl, or automatically harvest data from social media platforms, job boards, or any external service. All signals must be imported manually by the user using `applysmith import-signal`.

This is both a technical design choice and an ethical one. Automated scraping of social platforms violates platform terms of service and creates legal and reputational risk for users.

---

## 13. SignalScout Is a Separate External Intelligence Agent

SignalScout is a companion agent for external intelligence gathering. It handles structured research from public sources including news, company disclosures, and job posting aggregation. It is a separate tool with its own rules and scope.

ApplySmith handles strategy, packaging, and claim validation. SignalScout handles structured external research. The two tools are complementary but distinct.

**Do not conflate them.** ApplySmith does not perform external searches. SignalScout does not do resume tailoring or claim checking.

---

## Summary: What ApplySmith Is and Is Not

| ApplySmith IS | ApplySmith IS NOT |
|---------------|------------------|
| A career strategy framework | A resume template generator |
| JD-first and claim-validated | A profile-first polish tool |
| Multi-pipeline and honest | Optimistic or flattering |
| Local, private, markdown-based | A web service or scraping tool |
| A thinking framework | A replacement for human judgment |
