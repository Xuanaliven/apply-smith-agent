# Role Schema: Data Analyst

## Role Overview

Data Analysts turn raw data into business decisions. The role spans data extraction, metric definition, dashboard creation, ad hoc analysis, experiment analysis, and business reporting. Seniority is measured not just by technical skill but by the ability to frame the right question, choose the right method, and communicate findings that drive action.

---

## Sub-Roles

| Sub-Role | Focus | Common Employer Type |
|----------|-------|---------------------|
| Business Analyst | Business metric tracking, strategic analysis | Any large company |
| Product Analyst | Feature-level analysis, funnel, A/B tests | Internet / SaaS |
| Marketing Analyst | Campaign attribution, audience analysis | Consumer brand, platform |
| Operations Analyst | Process efficiency, cost analysis | Manufacturing, logistics, ops-heavy firms |
| Risk / Compliance Analyst | Fraud detection, credit scoring, anomaly detection | Finance, fintech |
| Growth Analyst | Acquisition funnel, activation, referral loops | Consumer apps, growth-stage startups |

---

## Responsibilities

- Write and maintain SQL queries for data extraction and transformation
- Define, monitor, and report on core business metrics
- Build and maintain dashboards for teams and leadership
- Conduct ad hoc analysis to answer specific business questions
- Design and analyze A/B experiments (hypothesis, sample size, significance)
- Produce business reports with findings and recommendations
- Collaborate with product, operations, and finance to align on data definitions
- Identify anomalies in data, investigate root causes, escalate as needed

---

## SQL Requirements

| Skill Level | Capabilities |
|-------------|-------------|
| Basic | SELECT, WHERE, GROUP BY, ORDER BY, basic JOINs |
| Intermediate | LEFT/RIGHT/FULL JOINs, subqueries, CASE WHEN, date functions |
| Advanced | Window functions (ROW_NUMBER, RANK, LAG/LEAD, NTILE), CTEs, query optimization |
| Expert | Query execution plan analysis, index strategy, large-table performance |

Most analyst roles require intermediate to advanced SQL. Window functions and CTEs are now standard expectations for any serious analyst position.

---

## Python Requirements

| Usage | Libraries |
|-------|----------|
| Data manipulation | pandas, numpy |
| Visualization | matplotlib, seaborn, plotly |
| Statistics | scipy.stats, statsmodels |
| Machine learning (optional) | scikit-learn |
| Notebook environment | Jupyter |

Python is often secondary to SQL at most analyst roles but strengthens your profile significantly for experiment analysis and advanced segmentation work.

---

## Common Metrics

| Category | Metrics |
|----------|---------|
| Funnel | Impression → click → registration → activation → purchase conversion rates |
| Cohort Retention | D1 / D7 / D30 retention by acquisition cohort |
| Revenue | GMV, ARPU, LTV, revenue per session |
| Experiment | Lift %, p-value, confidence interval, sample size, power |
| Engagement | DAU, session length, feature penetration rate, NPS |
| Operations | Fulfillment rate, processing time, error rate, SLA compliance |

---

## Interview Focus

- **SQL problems**: live coding — write a query to calculate cohort retention, rank users by metric, or find the second-highest value in a column
- **Metric decomposition**: "Revenue dropped 20% last week — walk me through how you investigate this"
- **Case analysis**: "How would you measure the success of a new feature?"
- **Statistics basics**: what is a p-value? When would you use a t-test vs. a chi-square test?
- **A/B testing**: "How do you decide when an experiment has enough data to call a result?"
- **Communication**: "How would you explain a regression result to a non-technical stakeholder?"

---

## Portfolio Suggestions

1. **End-to-end analysis project**: Take a public dataset (Kaggle, government open data, Mode Analytics) and produce a full analysis — question, SQL/Python extraction, findings, recommendations, and limitations
2. **Dashboard build**: Build a dashboard in a free tool (Metabase, Google Looker Studio, or Observable) on a public dataset and share the link
3. **A/B test analysis**: Simulate or use a public A/B test dataset; calculate required sample size, run significance tests, and write up your conclusion with caveats
4. **Funnel analysis**: Find an e-commerce or app dataset with event logs; calculate step-by-step conversion and identify the largest drop-off

---

## Resume Bullet Examples

- "Built end-to-end funnel analysis using SQL on 2M+ event logs, identifying registration-to-activation drop-off; fix increased activation rate by 12%"
- "Designed A/B test for new onboarding flow; calculated sample size (n=4,200), ran test for 14 days, confirmed 95% CI lift of 8% in D7 retention"
- "Automated daily metrics report using Python + SQL, replacing 3-hour manual process with a 10-minute scheduled job"
- "Wrote multi-CTE retention query segmenting users by acquisition channel and cohort month, enabling first channel-level retention breakdown for the marketing team"

> ⚠️ Claim check reminder: Every bullet must have a source in your experience atoms and a risk level (Green / Yellow / Red / Buildable / Stretch). Do not include metrics you cannot defend in an interview.
