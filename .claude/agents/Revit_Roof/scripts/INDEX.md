---
name: Revit_Roof scripts index
description: Index of scripts written by/for the Revit_Roof agent — what each does and when to reach for it. Check this (and any shared project library) before writing a new script.
---

# Revit_Roof — scripts index

| Script | Purpose | Reuse when... |
|---|---|---|
| `roof_footprint.py` | Outline (m, plan XY) → CCW `profile` offset outward by the eave overhang (mitred corners) + `edgeSlopesDeg` for hip / gable (ridge long or short) / shed / flat; prints edge lengths/directions so you can name which edge slopes. Pure Python, no deps. `python -I roof_footprint.py in.json` | Any footprint roof: always run the wall outer-face outline through it rather than hand-offsetting corners. Gable/shed are 4-sided only — it refuses others instead of guessing. |
| `docx_standards.py` | Scans a project Word document (ТЗ / specification `.docx`) for the standards it already names (СП, ГОСТ, СНиП, TS EN, EN, ISO, IBC, NFPA, ASTM, ICAO… plus general "comply with СП/ГОСТ" clauses) and its roof mentions; prints JSON with `has_standards`. `python -I docx_standards.py file.docx [--context N]` | Before every roof code check on a job that has a Word document — `has_standards: true` means the skill's own rules are not added (roof-code-check §0). |

## Rule
Before writing a new script: read this table (and any shared library for
this domain). Reuse or extend an existing one when it already covers the
need. Only add a new file when nothing existing does, and add its row here
in the same turn you write it.
