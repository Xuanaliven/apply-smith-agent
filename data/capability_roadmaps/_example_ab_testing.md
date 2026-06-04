# Capability Roadmap: A/B Testing

## What This Capability Is

A/B testing (also called controlled experimentation or split testing) is the practice of comparing two or more variants of a product, message, or experience by randomly assigning users to each variant and measuring the difference in a target metric. It is the gold standard for causal inference in product and marketing decisions.

Mastery of A/B testing signals analytical rigor, product thinking, and statistical literacy — valued in product, data, operations, and growth roles.

---

## Learning Path

### Stage 1 — Foundations (1–2 weeks)

- **Core concepts**:
  - Null hypothesis and alternative hypothesis
  - Statistical significance: p-value, confidence interval (95% CI)
  - Type I error (false positive) and Type II error (false negative)
  - Statistical power (typically 80%)
  - Sample size calculation formula
- **Resources**:
  - Any introductory statistics textbook (chapters on hypothesis testing)
  - Evan Miller's sample size calculator (free, online)
  - "Trustworthy Online Controlled Experiments" (book) — chapters 1–4

### Stage 2 — Experiment Design (1–2 weeks)

- **What to learn**:
  - How to write a clear hypothesis: "If we change X, then Y will increase by Z% because..."
  - Choosing the right primary metric (OEC — Overall Evaluation Criterion)
  - Defining guardrail metrics (metrics that must not regress)
  - Selecting the randomization unit: user-level, session-level, device-level
  - Calculating required experiment duration (traffic, sample size, expected lift)
  - Pre-experiment checks: SRM (Sample Ratio Mismatch), AA test

### Stage 3 — Common Pitfalls (1 week)

- **Novelty effect**: users behave differently because something is new, not because it is better — solution: run longer, focus on returning user cohort
- **Network effects**: treatment leaks to control group via social features — solution: cluster randomization
- **Peeking problem**: stopping the test early when results look good inflates false positive rate — solution: set end date before launch; use sequential testing if you must peek
- **Multiple testing**: running many variants inflates false positive rate — solution: Bonferroni correction or preregistration
- **Metric sensitivity**: some metrics take longer to show stable signal (e.g., D30 retention vs. D1 activation)

### Stage 4 — Analysis (1–2 weeks)

- **Two-sample t-test** for continuous metrics (e.g., session length, revenue per user)
- **Chi-square test** for proportions (e.g., CTR, conversion rate)
- **Confidence intervals**: how to interpret them, how to communicate uncertainty
- **Effect size**: statistical significance ≠ practical significance — a tiny lift on 10M users may be significant but not worth shipping
- **Python implementation**: `scipy.stats.ttest_ind`, `scipy.stats.chi2_contingency`, bootstrapped CI

---

## Public Datasets to Practice With

| Dataset | Source | How to Use |
|---------|--------|-----------|
| E-commerce A/B test dataset | Kaggle | Two landing page variants; analyze conversion rate difference |
| Udacity A/B Testing dataset | Udacity free course | Classic enrollment experiment; full analysis walkthrough available |
| Cookie Cats mobile game | Kaggle | Gate placement experiment; cohort retention analysis |
| Any behavioral event log | Kaggle, government open data | Simulate treatment/control by random assignment |

---

## How to Frame as Portfolio Project

**Project title**: "A/B Test Analysis: Evaluating Impact of [Feature] on [Metric]"

**Structure**:
1. Business context: what problem were you solving?
2. Hypothesis: state the null and alternative hypothesis
3. Experiment design: randomization unit, primary metric, guardrail metrics, sample size calculation
4. Results: show the distribution, the test statistic, p-value, and confidence interval
5. Decision recommendation: ship, iterate, or abandon — and why
6. Limitations: what could have biased the result?

**Example framing**:
> "Designed and analyzed a simulated A/B test on [Kaggle e-commerce dataset] to evaluate the impact of a checkout page redesign on conversion rate. Calculated required sample size (n=3,800 per variant at 80% power, 5% significance), ran test for the equivalent of 14 days, and concluded a statistically significant 9% lift in conversion (95% CI: [4.2%, 13.8%])."

---

## Resume Bullet Examples

- "Designed A/B test framework for checkout flow redesign, calculating required sample size (n=3,800/variant); confirmed 9% CVR lift at 95% CI"
- "Identified novelty effect in homepage experiment causing inflated 7-day retention; revised holdout to 28 days and revised conclusion"
- "Built experiment analysis template in Python (scipy + pandas) used by 4-person ops team for all subsequent retention experiments"
- "Ran 6 sequential A/B tests on push notification copy; highest-performing variant achieved 2.3x CTR vs. control"

---

## Claim Level Guidance

| Bullet Type | Likely Level | Notes |
|-------------|-------------|-------|
| Real experiment at work/internship with data | Green | Document the context carefully |
| Portfolio project on public dataset | Buildable / Green | Label clearly as portfolio project |
| Described a test you observed but did not run | Yellow | Be precise about your actual role |
| Claimed full ownership of an experiment you only supported | Red | Do not do this |
