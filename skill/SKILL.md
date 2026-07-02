---
name: fpna-connected-planning
description: FP&A connected-planning methodology for driver-based scenario planning, variance analysis, and investor-grade reporting, built on the SEC EDGAR → Power Query → Anaplan → Power BI pipeline. Use this skill whenever the user asks for financial planning & analysis work — revenue forecasting, budget vs actual variance, scenario modeling (base/optimistic/pessimistic cases), variance bridges/waterfalls, segment-level plan analysis, operating margin planning, headcount cost modeling, rolling forecasts, or CFO/investor commentary — even if they don't say "FP&A" explicitly. Also trigger when the user mentions Anaplan models, SEC filing actuals (10-K/10-Q), Power Query data shaping for finance, or DAX-driven financial dashboards.
---

# FP&A Connected Planning

A methodology for turning public-filing (or internal ledger) actuals into driver-based forecasts, scenario stress tests, and investor-grade decision commentary. Modeled on an end-to-end pipeline: **SEC EDGAR → Power Query → Anaplan → Power BI → decision commentary**.

The core idea: one source of truth flows from filing to forecast to dashboard. Actuals come from primary sources, drivers (not line-item guesses) generate the plan, every scenario is stress-tested, and the output is framed as decisions — not just numbers.

## Bundled resources — when to use what

- `scripts/scenario_engine.py` — run this instead of hand-calculating: builds scenario fans, probability-weighted E[V], variance reports, and segment bridges from CSVs (`--demo` shows the format). Use it whenever the user provides actuals + growth drivers.
- `references/data-sourcing-shaping.md` — read when pulling SEC EDGAR data or shaping raw financials into a star schema (Power Query / pandas / SQL).
- `references/anaplan-model-design.md` — read when designing the planning model itself: dimensions, driver modules, rolling-forecast re-base process, anti-patterns.
- `references/dax-measures.md` — read when building the Power BI layer: DAX patterns for weighted EV, scenario fan, margin floor, dynamic commentary.

## The five-stage pipeline

Apply these stages in order. If the user's data source or toolset differs (e.g., internal ERP instead of EDGAR, Excel instead of Anaplan), keep the stage's purpose and adapt the tool.

### 1. Source — primary-filing actuals
Pull actuals from primary sources: SEC EDGAR 10-K/10-Q for public companies (revenue, segment mix, OpEx, operating income), or the internal GL for private data. Never plan off secondary summaries — reconcile to the filed/booked numbers.

### 2. Ingest & shape — tidy star schema
Extract, clean, and unpivot into a tidy star schema (fact table of measures by period/segment/scenario; dimension tables for time, segment, scenario, department). The shape must support repeatable refresh — next quarter's actuals should drop in without rework. Power Query is the reference tool; pandas or SQL work the same way.

### 3. Plan & model — driver-based scenarios
Build the plan from a small set of growth/cost drivers, not line-item edits:

- Define three cases minimum: **Pessimistic, Base, Optimistic** (e.g., +6.4% / +12.2% / +20.3% revenue growth).
- Apply drivers to the latest full-year actuals to project the horizon (multi-year, e.g., FY+1 to FY+3).
- Compute a **probability-weighted expected value** across cases (e.g., 25/50/25) as the single planning number.
- Keep a rolling forecast: when actuals land, re-base the driver set on the actual, not the stale budget.
- Segment-level drivers where segments behave differently — a group-level driver hides structural winners (e.g., Cloud growing +35.8% vs +12.2% planned) and structural decliners (managed-runoff segments).

### 4. Visualize — decision-oriented dashboards
Build views that answer a planning question, not generic charts:

- **Scenario fan**: actuals trajectory with the three projected cases fanning out; mark where actuals land relative to the fan.
- **Variance bridge (waterfall)**: from plan to actual, decomposed by segment/driver so the beat or miss has named causes.
- **Segment variance**: plan vs actual per segment, flagging realized vs planned growth rates.
- **Margin discipline view**: operating margin % over time against a stated floor.
- **Headcount & fully loaded cost**: headcount by department/year, cost per employee, revenue per employee.

In Power BI, drive everything from DAX measures so commentary and visuals stay in sync with the active driver set.

### 5. Decide — measure-driven commentary
Translate variance into actions with named owners. Commentary should be generated from the live measures (so it can't drift from the data) and follow the pattern: what happened → why → what to change in the model → what constraint to protect. Example actions: re-anchor an outperforming segment onto its own driver curve; model a declining segment as managed runoff; lock an operating-margin floor as a planning constraint.

## Variance analysis rules

- State every variance three ways: absolute ($), relative (%), and vs which scenario.
- Decompose the total variance into segment/driver contributions that sum to the total (bridge discipline).
- Distinguish *beat vs plan* from *beat vs expected value* — a +$10.1B beat vs Base may be only +$8.1B vs the probability-weighted E[V].
- After a beat/miss, always re-base the rolling forecast and quantify the effect on the outer years (e.g., "re-basing on FY25 actual lifts FY28 Base by +$14B vs static budget").

## Output standards

- Figures in $B (or $M) with one decimal; growth rates in % with one decimal.
- Label scenario assumptions explicitly wherever a projection appears.
- Margin commentary must state both the % and the profit dollars.
- End every analysis with 2–4 numbered, imperative next moves (e.g., "1. Re-driver Cloud onto a high-teens curve. 2. Model Network as managed runoff. 3. Lock a 31% margin floor.").
- Include the standard disclaimer when using public-company data: figures are a modeling exercise, not investment advice.

## Example

**Input:** "FY25 revenue came in at $402.8B vs a Base plan of $392.7B. Cloud did +35.8% vs +12.2% planned; Network declined $4.3B."

**Output shape:** FY25 beat Base by +$10.1B (+2.6%), landing between Base and Optimistic; beat probability-weighted E[V] ($394.7B) by +$8.1B. Bridge: Cloud +$10.2B carried the beat, Network −$4.3B the largest drag, other segments net +$4.6B. Next moves: (1) break Cloud onto its own high-teens driver curve, (2) model Network as managed runoff, (3) hold the 32% operating margin — floor at 31% in the reforecast.
