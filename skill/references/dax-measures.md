# DAX Measure Library for Connected Planning Dashboards

Pattern library for the Power BI layer. Assumes a star schema with `Fact[Value]` keyed by `Dim_Time`, `Dim_Segment`, `Dim_Scenario` (Actual / Pessimistic / Base / Optimistic), and `Dim_Department`.

## Core measures

```dax
Revenue Actual =
CALCULATE ( SUM ( Fact[Value] ), Dim_Scenario[Scenario] = "Actual" )

Revenue Base =
CALCULATE ( SUM ( Fact[Value] ), Dim_Scenario[Scenario] = "Base" )

Variance vs Base = [Revenue Actual] - [Revenue Base]

Variance vs Base % = DIVIDE ( [Variance vs Base], [Revenue Base] )
```

## Probability-weighted expected value

Weights live in a disconnected `Scenario_Weights` table (e.g., 0.25 / 0.50 / 0.25) so they can be changed without touching the model:

```dax
Weighted EV =
SUMX (
    Scenario_Weights,
    Scenario_Weights[Weight]
        * CALCULATE ( SUM ( Fact[Value] ),
            Dim_Scenario[Scenario] = Scenario_Weights[Scenario] )
)

Beat vs EV = [Revenue Actual] - [Weighted EV]
```

## Scenario fan support

Blend actuals with projections so one line chart shows history plus fan:

```dax
Fan Value =
VAR LastActualYear = CALCULATE ( MAX ( Dim_Time[Year] ), Dim_Scenario[Scenario] = "Actual" )
RETURN
    IF (
        MAX ( Dim_Time[Year] ) <= LastActualYear,
        [Revenue Actual],
        SUM ( Fact[Value] )   -- projected scenario in filter context
    )
```

## Margin discipline

```dax
Operating Margin % = DIVIDE ( [Operating Income], [Revenue Actual] )

Margin Floor Breach =
IF ( [Operating Margin %] < 0.31, "BREACH", "OK" )
```

## Headcount & productivity

```dax
Revenue per Employee = DIVIDE ( [Revenue Actual], [Headcount] )
Cost per Employee    = DIVIDE ( [Fully Loaded Cost], [Headcount] )
```

## Dynamic commentary

Generate the decision panel from measures so narrative can never drift from data:

```dax
Commentary =
VAR Beat = [Variance vs Base]
VAR Dir  = IF ( Beat >= 0, "beat", "missed" )
RETURN
    "FY" & MAX ( Dim_Time[Year] ) & " " & Dir & " Base by "
    & FORMAT ( ABS ( Beat ) / 1e9, "$#,0.0" ) & "B ("
    & FORMAT ( [Variance vs Base %], "+0.0%;-0.0%" ) & "). "
    & "Margin " & FORMAT ( [Operating Margin %], "0.0%" ) & "."
```

Compose longer commentary by concatenating segment-level SUMX passes ranked by contribution (TOPN on ABS variance).
