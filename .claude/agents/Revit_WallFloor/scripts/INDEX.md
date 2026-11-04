---
name: Revit_WallFloor scripts index
description: Index of scripts written by/for the Revit_WallFloor agent — what each does and when to reach for it. Check this (and any shared project library) before writing a new script.
---

# Revit_WallFloor — scripts index

| Script | Purpose | Reuse when... |
|---|---|---|
| `wall_floor_audit.py` | Model-integrity audit, no code figures. One JSON in (levels m, walls with bbox + Length + type width + height + top constraint, floors with bbox + thickness; bbox `units` feet = raw tool output) → rebuilt centrelines of axis-aligned walls (join extension resolved against perpendicular centrelines) and the skill's M/F rows: M1 overlapping/duplicate walls, M2 open joins (end misses another wall's line by tol…`--gap-max`), M3 Unconnected tops (tie-to level + Top Offset when the top already sits at a storey level or slab underside; else nearest storey and delta), M4 uneven heights per type/level, F1 foundation slab above the lowest level, F2 floor edges vs the exterior outline (centreline/inner/outer face) or "mostly outside", F3 overlapping floors, storey clear heights. Stair-landing levels (no wall on them) aren't storeys; override with `"storey"`. Slanted/curtain walls → `skipped`. Exit 2 = defects. Tested 2026-10-30 on Project1 L1 (21 walls, 3 floors: 21 M3, 1 M4, slab edges at centreline) + synthetic duplicate/60 mm gap. **2026-10-30 (first live audit):** walls are compared by shared height range, not by base level (M1/M2/join resolution), and F2 uses every wall standing at the floor's elevation — needed where façade walls are based on L1 and run up through L2. A roof can be passed as a `floors` entry (`"family": "Roof"`) so the top storey gets its slab underside. Input builder for Project1: `Russia_Aerovokzal/wallfloor_audit/build_input.py`. **2026-10-30:** a wall with `"outline": false` (site barrier, kerb, garden wall) is left out of the F2 exterior outline (regression: base-slab audit identical). | Every audit ("çizimi kontrol et / düzelt") and after every build: before and after changes, same input shape. |
| `../Revit_DoorWindow/scripts/wall_line.py` (shared) | One axis-aligned wall's location line from bbox + Length + thickness + `--joins`. | Single-wall work (e.g. splitting/extending one wall) when the full audit is more than needed. |
| `../Revit_Roof/scripts/docx_standards.py` (shared) | Scans a project Word document for the standards it names. | Before the code check on a job that has a Word document (`wall-floor-code-check` §0). |

## Rule
Before writing a new script: read this table (and any shared library for
this domain). Reuse or extend an existing one when it already covers the
need. Only add a new file when nothing existing does, and add its row here
in the same turn you write it.
