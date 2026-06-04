# Capability Roadmap: SQL Analytics

## What This Capability Is

SQL (Structured Query Language) is the primary tool for extracting, transforming, and analyzing data in relational databases. For analyst, operations, and product roles, SQL proficiency is often a hard requirement — not a nice-to-have. Strong SQL means writing queries that are correct, readable, and efficient, and being able to structure complex multi-step analyses without getting lost.

---

## Learning Path

### Stage 1 — Core Syntax (1 week)

```sql
-- SELECT and filtering
SELECT column1, column2
FROM table
WHERE condition
ORDER BY column DESC
LIMIT 100;

-- Aggregation
SELECT category, COUNT(*), SUM(amount), AVG(value)
FROM table
GROUP BY category
HAVING COUNT(*) > 10;
```

- **What to practice**: SELECT, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT
- **Resource**: SQLZoo (free, browser-based), Mode Analytics SQL Tutorial

### Stage 2 — Joins (1 week)

```sql
-- INNER JOIN: only matching rows
SELECT a.user_id, a.name, b.order_count
FROM users a
INNER JOIN orders b ON a.user_id = b.user_id;

-- LEFT JOIN: all rows from left, nulls where no match
SELECT a.user_id, COALESCE(b.order_count, 0) AS order_count
FROM users a
LEFT JOIN orders b ON a.user_id = b.user_id;
```

- **Types**: INNER, LEFT, RIGHT, FULL OUTER, CROSS, SELF JOIN
- **Common pattern**: user table joined to event log — know how to count events per user
- **Pitfall**: many-to-many joins can explode row count — always verify with COUNT before aggregating

### Stage 3 — Window Functions (1–2 weeks)

Window functions are the single most differentiating SQL skill for analyst roles.

```sql
-- ROW_NUMBER: rank users by spend within each region
SELECT user_id, region, total_spend,
       ROW_NUMBER() OVER (PARTITION BY region ORDER BY total_spend DESC) AS rank
FROM user_summary;

-- LAG/LEAD: compare current value to previous row
SELECT user_id, event_date, revenue,
       LAG(revenue) OVER (PARTITION BY user_id ORDER BY event_date) AS prev_revenue,
       revenue - LAG(revenue) OVER (PARTITION BY user_id ORDER BY event_date) AS delta
FROM user_revenue;

-- Running total
SELECT order_date, daily_revenue,
       SUM(daily_revenue) OVER (ORDER BY order_date) AS cumulative_revenue
FROM daily_sales;
```

- **Key functions**: ROW_NUMBER, RANK, DENSE_RANK, NTILE, LAG, LEAD, FIRST_VALUE, LAST_VALUE, SUM/AVG OVER
- **Concepts**: PARTITION BY, ORDER BY within window, frame specification (ROWS BETWEEN)

### Stage 4 — CTEs and Subqueries (1 week)

```sql
-- CTE: readable, reusable intermediate results
WITH active_users AS (
    SELECT user_id
    FROM events
    WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
    HAVING COUNT(*) >= 3
),
user_revenue AS (
    SELECT user_id, SUM(amount) AS total_revenue
    FROM orders
    GROUP BY user_id
)
SELECT a.user_id, r.total_revenue
FROM active_users a
LEFT JOIN user_revenue r ON a.user_id = r.user_id;
```

- Use CTEs to break complex problems into named steps
- Avoid deeply nested subqueries — they are hard to read and debug
- Know when to use a CTE vs. a temporary table vs. a subquery

### Stage 5 — Analytical Patterns (1–2 weeks)

| Pattern | SQL Technique |
|---------|--------------|
| Funnel analysis | COUNT DISTINCT by step, CASE WHEN to label stage |
| Cohort retention | DATE_TRUNC for cohort month, JOIN events to cohort table |
| RFM segmentation | NTILE on recency, frequency, monetary with window functions |
| First/last event | ROW_NUMBER + PARTITION BY + filter WHERE rank = 1 |
| Session construction | LAG to detect session gaps, cumulative session ID |
| YoY / MoM comparison | LAG with period offset, date_trunc to month |

---

## Public Datasets to Practice With

| Dataset | Source | Recommended Practice |
|---------|--------|---------------------|
| E-commerce transaction data | Kaggle (multiple) | Funnel analysis, cohort retention, RFM |
| Northwind database | GitHub / Mode | Classic joins and aggregations |
| Stack Overflow annual survey | Mode Analytics Public | Complex filtering, GROUP BY |
| BigQuery public datasets | Google Cloud | Large-scale query optimization |
| NYC taxi trip data | NYC Open Data / BigQuery | Window functions, time-series patterns |

---

## How to Frame as Portfolio Project

**Project title**: "End-to-End Funnel and Retention Analysis Using SQL"

**Structure**:
1. Dataset description and business context
2. Key questions you answered
3. SQL queries (document the hardest ones with comments)
4. Findings: where does the funnel drop off? Which cohort retains best?
5. Recommendations based on findings
6. SQL file or notebook published on GitHub

**Example framing**:
> "Built an end-to-end funnel analysis using SQL on a public e-commerce event log dataset (Kaggle, 500K+ events). Identified checkout abandonment as the largest drop-off (62% exit rate). Used CTEs and window functions to calculate 30-day cohort retention, finding a 22% improvement in retention for users who completed a wishlist action within 48 hours of registration."

---

## Resume Bullet Examples

- "Built automated daily retention report using SQL window functions (LAG, PARTITION BY cohort_month), reducing manual reporting time by 80%"
- "Wrote multi-step CTE query to segment 500K+ users by behavioral cohort for targeted re-engagement campaign"
- "Designed funnel analysis query with CASE WHEN stage labeling, identifying 62% drop-off at checkout — finding led to product fix"
- "Refactored 200-line nested subquery into 6-step CTE pipeline, reducing query runtime from 4 minutes to 45 seconds"

---

## Claim Level Guidance

| Bullet Type | Likely Level | Notes |
|-------------|-------------|-------|
| SQL written on real job/internship data | Green | Keep the context; remove any confidential details |
| SQL written on public dataset portfolio project | Buildable / Green | Label as portfolio project |
| Claimed you "built" a query that was someone else's template | Red | Do not do this |
| Claimed query optimization results without benchmarks | Yellow | Add caveats or remove the specific numbers |
