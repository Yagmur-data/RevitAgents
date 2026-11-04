---
name: Revit_Stair scripts index
description: Index of scripts written by/for the Revit_Stair agent — what each does and when to reach for it. Check this (and any shared project library) before writing a new script.
---

# Revit_Stair — scripts index

| Script | Purpose | Reuse when... |
|---|---|---|
| `stair_run.py` | Floor-to-floor height + limits → stair sizing. Design mode (default): `--target-riser 0.17 --blondel 0.63 --min-tread` → n = round(H/target), tread = blondel − 2r raised to the code min (paste example 2.75 m → 16 × 171.9, g 286, 31.0° reproduced). Fixed mode: `--tread`. Other limits (max riser, optional min riser, max risers per flight, max rise between landings, 2R+G bounds, pitch bounds, landing depth) → riser count, equal riser height, 2R+G, pitch, flight split with landing offsets, walking-line `start`/`end` per flight (run length = (risers − 1) × tread), straight or U layout with the intermediate landing outline(s) for a Floor stand-in (straight needs `--width`), `floor_landing_zones` (bottom/top clear zones, `--floor-landing-depth`) and an ADVISORY warning above `--advise-risers-per-flight`. Negative directions as `--dir=-1,0`. Landing outputs checked 2026-10-30 against the built Аэровокзал U-stair (landing x 0.1435–1.388 = model). No code figures built in — limits come from the args. Pure Python. `python -I stair_run.py --height 4.2 --max-riser 0.175 --tread 0.275 [...]` | Every stair before `revit_create_stair`: the walking-line length decides the riser count, so never hand-size it. Tested 2026-10-21 against the Аэровокзал stair (4.2 m → 24 × 175, 12+12, run 3.025 m). |
| `../../Revit_Roof/scripts/docx_standards.py` (shared, Revit_Roof's) | Scans a project Word document for the standards it names; `has_standards` decides whether the skill's own rules are added. | Before every stair code check on a job that has a Word document (stair-code-check §0). |

## Rule
Before writing a new script: read this table (and any shared library for
this domain). Reuse or extend an existing one when it already covers the
need. Only add a new file when nothing existing does, and add its row here
in the same turn you write it.
