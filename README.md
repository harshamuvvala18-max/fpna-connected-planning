# fpna-connected-planning

Driver-based FP&A scenario planning on Alphabet Inc. public-filing actuals. SEC EDGAR -> Power Query -> Anaplan -> Power BI.

Live dashboard site: https://harshamuvvala18-max.github.io/fpna-connected-planning/

## Claude Skill

This repo also publishes a reusable Claude Skill that teaches Claude the full connected-planning methodology: driver-based scenario fans, probability-weighted expected value, variance bridges, rolling-forecast re-basing, and DAX/Anaplan patterns.

Install: download `fpna-connected-planning.skill` and add it in the Claude app (Settings -> Capabilities -> Skills), or open the file with Claude and click Save skill.

Source is browsable under `skill/` (SKILL.md, reference guides, and a runnable `scenario_engine.py` -- try `python skill/scripts/scenario_engine.py --demo`).

Built by Harsha Vivekananda Muvvala. MIT licensed.
