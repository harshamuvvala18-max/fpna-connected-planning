# Anaplan Model Design for Driver-Based Scenario Planning

How to structure the planning engine. Concepts transfer to any planning tool (Excel, Pigment, Workday Adaptive) — the module names are Anaplan's.

## Dimensions (lists)

- **Time**: fiscal years FY16–FY28 (or months for rolling forecast granularity)
- **Scenario**: Actual, Pessimistic, Base, Optimistic — a real list member each, never hard-coded columns
- **Segment**: business segments (e.g., Search, Cloud, YouTube, Subscriptions, Network)
- **Department**: for headcount/cost modules (R&D, S&M, G&A, Ops)
- **Version**: Budget (static, locked at year start) vs Rolling Forecast (re-based on actuals)

## Modules

### 1. Driver Assumptions
Dimensions: Scenario × Segment (× Time if drivers vary by year).
Line items: `Revenue Growth %`, `Margin %`, `Headcount Growth %`, `Scenario Weight`.
This is the ONLY module planners edit. Everything downstream is formula-driven. Example driver set: Pessimistic +6.4%, Base +12.2%, Optimistic +20.3%, weights 25/50/25.

### 2. Revenue Projection
Dimensions: Scenario × Segment × Time.
`Revenue = PREVIOUS(Revenue) * (1 + Driver Assumptions.Revenue Growth %)`, seeded from the last actual year. Segment-level drivers matter: a group driver hides a segment growing 3× plan and a segment in decline.

### 3. Expense & Margin
Derive OpEx from revenue ratios (COGS %, R&D %, S&M %, G&A %) with a margin-floor check line item: `Margin Breach = Operating Margin % < Floor %`.

### 4. Headcount & Fully Loaded Cost
Department × Time. `Fully Loaded Cost = Headcount * Cost per Head` (salary + benefits + overhead). Tie growth to the revenue driver or plan explicitly per department.

### 5. Variance & Bridge
Scenario × Segment × Time. `Variance = Actual − Selected Scenario`; export this module as the source for the Power BI bridge visual.

## Rolling forecast discipline

When a year's actuals land:

1. Load actuals into the Actual scenario (never overwrite plan versions).
2. Lock the Budget version — it stays as filed for accountability.
3. Re-base the Rolling Forecast: seed projections from the new actual, review each segment's realized growth vs its driver, and re-anchor drivers where actuals diverge structurally (e.g., realized +35.8% vs planned +12.2% → give that segment its own curve).
4. Quantify the re-base effect on outer years and report it ("FY28 Base +$14B vs static budget").

## Anti-patterns

- Line-item budget edits scattered across modules — all planning changes go through Driver Assumptions.
- Scenario as separate models/files — one model, scenario as a dimension.
- Overwriting budget with forecast — keep both versions; variance to the locked budget is the accountability metric.
