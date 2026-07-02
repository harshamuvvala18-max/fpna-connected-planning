# Data Sourcing & Shaping — SEC EDGAR to Star Schema

## Sourcing from SEC EDGAR

- Company filings index: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=<CIK>&type=10-K`
- Structured company facts API (JSON, preferred for automation): `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` (10-digit zero-padded CIK). Key XBRL tags: `Revenues` / `RevenueFromContractWithCustomerExcludingAssessedTax`, `OperatingIncomeLoss`, `ResearchAndDevelopmentExpense`, `SellingAndMarketingExpense`, `GeneralAndAdministrativeExpense`.
- Segment revenue usually lives in the 10-K segment footnote, not top-level tags — extract from the filing tables.
- Always reconcile: extracted totals must tie to the face of the income statement to the $0.1B.

## Power Query shaping pattern

Goal: tidy long format — one row per (Year, Segment, Scenario, Measure) — never wide year-columns.

1. **Source**: pull the filing table or facts JSON.
2. **Promote headers, set types** early so errors surface at the source step.
3. **Unpivot** year columns into (Year, Value) pairs — this is the step that makes refresh repeatable when a new year appears.
4. **Add Scenario column** = "Actual" for filed data.
5. **Merge, don't append, dimension attributes** — segment groupings live in a separate dimension query.
6. Load facts to one table; dimensions (Time, Segment, Scenario, Department) as separate queries → star schema.

Parameterize the CIK and fiscal-year range so the same queries refresh next quarter without edits.

## Star schema

```
Fact_Financials (Year, Segment, Scenario, Measure, Value)
Dim_Time (Year, IsActual, IsPlanHorizon)
Dim_Segment (Segment, Group, IsRunoff)
Dim_Scenario (Scenario, SortOrder)
Scenario_Weights (Scenario, Weight)      -- disconnected, for weighted EV
Dim_Department (Department)              -- headcount facts
```

Grain rule: one fact table per grain. Headcount (Department × Year) is a different grain than financials (Segment × Scenario × Year) — separate fact tables, shared Time dimension.

## Quality gates before planning

- Segment values sum to reported total revenue each year.
- No nulls in keys; Scenario spelled identically across sources.
- Currency and units normalized ($B with one decimal at presentation, raw units in storage).
- Include the disclaimer wherever public-filing data feeds a model: modeling exercise, not investment advice.
