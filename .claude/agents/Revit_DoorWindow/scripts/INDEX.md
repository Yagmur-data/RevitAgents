---
name: Revit_DoorWindow scripts index
description: Index of scripts written by/for the Revit_DoorWindow agent — what each does and when to reach for it. Check this (and any shared project library) before writing a new script.
---

# Revit_DoorWindow — scripts index

| Script | Purpose | Reuse when... |
|---|---|---|
| `wall_line.py` | Axis-aligned wall's location line from what `revit_get_element_info` gives: bbox (`--feet` for raw values), `Length`, thickness, and `--joins` (perpendicular walls' centrelines) to decide which end the join extension sits on → start/end in metres. Refuses slanted/curved walls (thin side ≠ thickness) and flags a non-centreline `Location Line`. Exit 2 + `problems` when unresolved. Pass coordinates as `--opt=x,y`. Tested 2026-10-21 on wall 1658711 (→ 0,16 → 25,16). | Before `opening_layout.py` on every wall — the bridge has no location-curve tool. |
| `opening_layout.py` | Straight wall start/end + opening width → insertion point(s) on the wall location line (centre of each opening) for `revit_place_family_instance`. Modes: `--offset` (near edge from the start, or `--from-end`), `--center-offset`, `--center`, `--count N` (equal piers incl. the wall ends). Checks edges vs wall ends (`--min-end`) and overlaps/gaps against openings already in the wall (`--existing "x,y,w;…"`, `--min-gap`). Exit 2 + `problems` when something doesn't fit. No code figures built in. Pure Python. Tested 2026-10-21 (offset, 3-window distribute, overlap, too-close-to-end). | Every door/window before placing it: never hand-compute a point on a slanted wall; always pass the wall's other openings with `--existing`. |
| `../../Revit_Roof/scripts/docx_standards.py` (shared, Revit_Roof's) | Scans a project Word document for the standards it names. | Before the code check on a job that has a Word document (door-window-code-check §0). |

## Rule
Before writing a new script: read this table (and any shared library for
this domain). Reuse or extend an existing one when it already covers the
need. Only add a new file when nothing existing does, and add its row here
in the same turn you write it.
