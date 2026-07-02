#!/usr/bin/env python3
"""Scenario engine for driver-based FP&A planning.

Given historical actuals and per-scenario growth drivers, produces:
  - multi-year scenario projections (the "fan")
  - probability-weighted expected value per year
  - variance analysis of an actual vs each scenario and vs E[V]
  - a segment-level variance bridge (plan -> actual waterfall)

Usage:
  python scenario_engine.py --demo
  python scenario_engine.py --actuals actuals.csv --drivers drivers.csv \
      [--horizon 3] [--actual-latest 402.8]

actuals.csv: Year,Value            (group level)  or Year,Segment,Value
drivers.csv: Scenario,Growth,Weight (group)       or Scenario,Segment,Growth,Weight
Values in $B. Growth as decimal (0.122 = +12.2%).
"""
import argparse
import csv
import sys
from collections import defaultdict


def project(base_value, growth, years):
    """Compound base_value forward `years` years at `growth`."""
    out, v = [], base_value
    for _ in range(years):
        v *= 1 + growth
        out.append(round(v, 1))
    return out


def scenario_fan(last_actual, drivers, horizon):
    """drivers: {scenario: (growth, weight)} -> {scenario: [yr1..yrN]}"""
    return {s: project(last_actual, g, horizon) for s, (g, _) in drivers.items()}


def weighted_ev(fan, drivers):
    """Probability-weighted expected value per projected year."""
    horizon = len(next(iter(fan.values())))
    ev = []
    for i in range(horizon):
        ev.append(round(sum(fan[s][i] * drivers[s][1] for s in fan), 1))
    return ev


def variance_report(actual, fan, ev, year_index=0):
    """Compare a reported actual against each scenario for one projected year."""
    lines = []
    for s, series in sorted(fan.items(), key=lambda kv: kv[1][year_index]):
        plan = series[year_index]
        d = round(actual - plan, 1)
        pct = round(100 * d / plan, 1)
        lines.append(f"  vs {s:<12} {plan:>8.1f}  Δ {d:+8.1f}B ({pct:+.1f}%)")
    d_ev = round(actual - ev[year_index], 1)
    lines.append(f"  vs E[V]        {ev[year_index]:>8.1f}  Δ {d_ev:+8.1f}B")
    return "\n".join(lines)


def segment_bridge(seg_plan, seg_actual):
    """Waterfall rows from plan to actual, largest absolute impact first."""
    rows = []
    for seg in seg_plan:
        d = round(seg_actual.get(seg, 0.0) - seg_plan[seg], 1)
        rows.append((seg, d))
    rows.sort(key=lambda r: -abs(r[1]))
    total = round(sum(d for _, d in rows), 1)
    return rows, total


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def run(actuals_rows, drivers_rows, horizon, reported_actual=None):
    has_segments = "Segment" in actuals_rows[0]
    # Group-level actual history
    by_year = defaultdict(float)
    for r in actuals_rows:
        by_year[int(r["Year"])] += float(r["Value"])
    last_year = max(by_year)
    last_actual = round(by_year[last_year], 1)

    # Group-level drivers (average if per-segment)
    drv = {}
    for r in drivers_rows:
        s = r["Scenario"]
        g, w = float(r["Growth"]), float(r["Weight"])
        drv.setdefault(s, []).append((g, w))
    drivers = {s: (sum(g for g, _ in v) / len(v), v[0][1]) for s, v in drv.items()}

    fan = scenario_fan(last_actual, drivers, horizon)
    ev = weighted_ev(fan, drivers)

    print(f"Last actual (FY{last_year}): ${last_actual}B")
    print(f"\nScenario fan (FY{last_year + 1}..FY{last_year + horizon}, $B):")
    for s, series in fan.items():
        g = drivers[s][0]
        print(f"  {s:<12} ({g:+.1%}): {series}")
    print(f"  {'E[V]':<12} (weighted): {ev}")

    if reported_actual is not None:
        print(f"\nFY{last_year + 1} reported actual ${reported_actual}B — variance:")
        print(variance_report(reported_actual, fan, ev))

    if has_segments and reported_actual is not None:
        # Per-segment plan at Base vs actual requires segment actuals for the
        # reported year in the input; bridge is shown in --demo.
        pass
    return fan, ev


def demo():
    print("=== DEMO: Alphabet-style connected planning ===\n")
    drivers = {"Pessimistic": (0.064, 0.25), "Base": (0.122, 0.50), "Optimistic": (0.203, 0.25)}
    last_actual = 350.0  # FY24
    fan = scenario_fan(last_actual, drivers, 4)
    ev = weighted_ev(fan, drivers)
    print("Scenario fan FY25-FY28 ($B):")
    for s, series in fan.items():
        print(f"  {s:<12}: {series}")
    print(f"  E[V]       : {ev}")
    print("\nFY25 actual $402.8B — variance:")
    print(variance_report(402.8, fan, ev))
    seg_plan = {"Search": 219.8, "Cloud": 48.3, "YouTube": 40.4, "Subscriptions": 45.0, "Network": 33.2}
    seg_act = {"Search": 224.1, "Cloud": 58.5, "YouTube": 42.1, "Subscriptions": 45.9, "Network": 28.9}
    rows, total = segment_bridge(seg_plan, seg_act)
    print("\nSegment bridge, Base plan -> actual ($B):")
    for seg, d in rows:
        print(f"  {seg:<14} {d:+.1f}")
    print(f"  {'NET':<14} {total:+.1f}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--actuals")
    p.add_argument("--drivers")
    p.add_argument("--horizon", type=int, default=3)
    p.add_argument("--actual-latest", type=float, default=None,
                   help="Reported actual for the first projected year, $B")
    p.add_argument("--demo", action="store_true")
    a = p.parse_args()
    if a.demo:
        demo()
        return
    if not (a.actuals and a.drivers):
        p.error("provide --actuals and --drivers, or --demo")
    run(read_csv(a.actuals), read_csv(a.drivers), a.horizon, a.actual_latest)


if __name__ == "__main__":
    sys.exit(main())
