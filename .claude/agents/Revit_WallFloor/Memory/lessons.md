---
name: Revit_WallFloor lessons
description: Curated, rule-form corrections distilled from activity_log.md — read this before every task, not just the raw log. One durable rule per line.
---

# Revit_WallFloor — lessons

Each line is one standing rule, stated as a concrete instruction, promoted
here from the activity log once it's proven worth remembering permanently.
Don't duplicate the chronological log here — only the distilled rule.

Seeded by HR on 2026-10-30 from Revit_Guide's read-only + dry-run survey of
Project1 (Аэровокзал Северное) and the workspace's revit-mcp-traps memory:

- `revit_create_wall` and `revit_create_floor` accept an exact duplicate of an existing wall/floor and say
  success, with no overlap warning; model health shows no warning either. Run `wall_floor_audit.py` (M1/F3)
  on the planned element plus its neighbours before creating, and again after.
- Always pass `wallTypeName` and `floorTypeName`: omitted, the wall becomes "M_Exterior - Brick on Mtl. Stud"
  and the floor a **Foundation Slab** ("150mm Foundation Slab"). "Conc 150mm" is a Foundation Slab type,
  "Concrete 150mm" a Floor type — check the family name in `revit_list_floor_types`.
- `revit_create_wall` builds only a centreline, Unconnected-height wall at base offset 0 (args: start, end,
  height, levelName, wallTypeName, structural). Set Top Constraint / Base Offset / Location Line afterwards
  with `revit_set_parameter`: Top Constraint takes `{"id": <levelId>}` (a level name is refused), Location
  Line an integer (2 = Finish Face: Exterior), and Top Offset is read-only until Top Constraint is set - but inside ONE
  `revit_batch` (Top Constraint steps first, then Top Offset steps) it is writable: tie tops in one transaction, no
  intermediate jump to the level (verified 2026-10-30 on 48 walls, curtain walls included).
- Curtain types (M_Exterior Glazing) are accepted by `revit_create_wall` with no warning — choose the type
  on purpose; doors/windows can't be hosted in them.
- No tool returns a wall's location curve; bboxes come in FEET and extend half a wall width into joins.
  `revit_list_wall_types` gives `widthFeet` and `kind` (Basic/Curtain/Stacked) but no function
  (exterior/interior); `revit_list_floor_types` gives no thickness — read the instance `Thickness` (mm).
- Neither create tool returns a changeSummary; a dry run returns a provisional id that is gone afterwards.
  Prove the result with `revit_get_element_geometry` + the audit script, never from the reply.
- A 0.5 mm wall or a self-intersecting floor profile fails with a raw Revit exception — translate it
  (too short / boundary crosses itself) and fix the geometry, don't retry.
- `revit_check_clearance` walls↔walls (clearance 0) does not report joined basic-wall corners, but does
  report touching curtain-wall segments at angled corners (6 false pairs in the L2 glazing bay of Project1).
  Use the audit script for walls; read clearance hits on curtain walls as noise unless the bboxes overlap.
- `revit_get_model_health` / triage give warning groups only, no element ids — they can't locate a defect.
- Moving an exterior wall stretches joined walls AND drags floors whose sketch edge is locked to it (revit-mcp-traps
  memory): re-read floor bboxes/areas after every wall move.
- Project1 (Аэровокзал) state on 2026-10-30 (survey; since the same day 48 walls are tied - see log, only the 5 КДП parapets 1681394-98 stay Unconnected on purpose): L1 exterior panels 9.0 m
  (roof 8.1 + 0.9 parapet) except the north wall 1658711 at 4.2 m; partitions stop at 3.95 = underside of the
  250 mm L2 slab; L1 slab 1682387 edges sat on the exterior wall CENTRELINE (replaced 2026-10-30 by 1682711 at the outer face); L2 slab 1682394 overhangs 2.5 m
  south / 1.4 m north (canopy); "Площадка лестницы +2.100" is a stair-landing level, not a storey. These are
  findings to report, not to change without Al's yes.
- Multi-storey walls belong to their BASE level only: Project1's 9 m façade walls (L1) also enclose L2, so a
  level-by-level comparison shows false free ends on L2 and a wrong L2 slab-edge note. The audit compares walls by
  shared height range since 2026-10-30 — always give it `levels` with elevations.
- The audit only knows floors: pass the roof (FootPrintRoof) as a `floors` entry with `"family": "Roof"` and its
  thickness, or the top storey has no slab underside (no M3 tie target, no clear height). Project1: roof 1682422
  underside +7.800, L2 partitions + КДП curtain walls stop exactly there.
- `revit_query_where` reads door/window `Host Id` directly (OST_Doors / OST_Windows, select ["Host Id"]) — one call
  gives the "what else it touches" list for every wall.
- Al 2026-10-30: the base (ground-floor) slab goes to the exterior walls' OUTER face - the façade panel stands fully on the slab and
  the aprons/landings butt against the slab edge with 0 gap. Never leave the base slab at the wall centreline (Project1 L1 slab is
  now 1682711 at the outer face).
- Changing a floor's outline (no sketch-edit tool): dry-run `revit_create_floor` with the new profile (feet = exact bbox values), then ONE
  `revit_batch` [create_floor, delete_elements old] dry → commit. Before committing, check the dry run's deletedIds are only the old
  floor's own sketch parts (sketch plane, sketch, boundary lines, span-direction edge, automatic sketch dims - 11-13 for a rectangle, Project1 had 13 and 11; same uniqueId prefix as the floor);
  check Host Id on doors/furniture/etc. first and copy back Mark/Comments if set.
- `revit_batch` does not regenerate between steps: geometry reads and `check_clearance` inside a batch (dry or real) see the PRE-batch
  model. Never "test" a change and its clash in one batch - commit, then read/check (2026-10-30).
- Stair soffit heights: don't trust a formula from the stringer type's "Structural Depth On Run" (Project1 soffits were 30-80 mm lower).
  Measure: raise your OWN wall under the flight to a trial top, commit, `check_clearance` axis bbox 0 mm (ElementIntersects, solid) vs
  OST_Stairs, bisect, restore. The probe reads the LOWEST soffit over the wall's footprint - place the probe where you need the value.
- A wall drawn to another wall's FACE is auto-T-joined: its Length/bbox run on to the host's centreline, the solid stops at the face and
  the host is unchanged (check volumes). Use it to butt site walls/barriers against a façade without cutting the panel.
