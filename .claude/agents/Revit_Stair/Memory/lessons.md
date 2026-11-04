---
name: Revit_Stair lessons
description: Curated, rule-form corrections distilled from activity_log.md — read this before every task, not just the raw log. One durable rule per line.
---

# Revit_Stair — lessons

Each line is one standing rule, stated as a concrete instruction, promoted
here from the activity log once it's proven worth remembering permanently.
Don't duplicate the chronological log here — only the distilled rule.

- `revit_create_stair` sets the riser count from the walking-line LENGTH:
  size the line as (risers − 1) × tread with `stair_run.py`, and always read
  back `Actual Number of Risers` — the add-in deletes Revit's "stair
  incomplete" warning, so a short line still returns ok. (Seeded by HR
  2026-10-21 from the Аэровокзал job / revit-mcp-traps memory.)
- Stair types are listed by `revit_list_elements` category `OST_Stairs`
  (`typeId: -1` = type). Type limits live on the type: `Maximum Riser
  Height`, `Minimum Tread Depth`, `Minimum Run Width`; the instance has
  `Actual Riser Height` / `Actual Number of Risers` (read-only) and `Actual
  Tread Depth` / `Desired Number of Risers` (writable). (Checked live on
  Project1 2026-10-21: type "M_Stair-Metal-Plate Stringer" = 178 / 275 /
  1000 mm.)
- A stair spans storeys: its `levelId` reads -1; take the base level from the
  `Base Level` parameter. (Checked live 2026-10-21.)
- Since the 2026-10-26 add-in deploy `revit_duplicate_family_type` takes any ElementType: RailingType verified
  live ("Ограждение 1200mm" from "1100mm"); StairsType not yet — dry-run it the first time and log the result here.
  `revit_set_parameter` now picks the writable same-named parameter, so a RailingType's top rail "Height" can be set.
- Аэровокзал Северное (Russia_Aerovokzal, Project1): two stairs L1 → "Площадка
  лестницы +2.100" → L2, type M_Stair-Metal-Plate Stringer, 12 × 175 mm,
  tread 275 mm. Its ТЗ names СП/ГОСТ standards → stair-code-check §0 applies
  (no US/UK/Neufert rules added). Basis = `ТЗ — RF: СП 1.13130.2020 (ред. 16.06.2025)`: the skill's
  §3b RF rules **do** apply (Al, 2026-10-21 — supersedes "measurements only"). Inputs: Ф3.3, ≤ 200 people
  on L2 → RF1 1.2 m, children present. Read `Russia_Aerovokzal/model_notes.md` first.
- Reading an existing stair: run width is `Actual Run Width` on the run (OST_StairsRuns); hosted handrails
  are OST_StairsRailing (OST_Railings stays empty); a slab opening drawn as a sketch loop has no
  OST_FloorOpening element — read its edge from a high-res plan export (`pixelSize` 4096) cropped with PIL
  in the scratchpad, calibrated on known stair bbox x values. (2026-10-21, Аэровокзал.) If the plan draws no slab
  edge: the Floor's faceCount (= sketch edges + 2) tells a notch from an inner loop, and the area delta against the
  last known outline gives the notch extent. (2026-10-30.)
- LD3 door swing: `revit_get_doors` facing = the side the leaf swings into; HandOrientation points to the HINGE jamb
  (Project1: hand (0,1) → hinge on +y; confirmed on L2 plan crops for 1679418 / 1679589 / 1679592). Fully open leaf
  = hinge + facing × leaf width. (2026-10-30.)
- Compare US limits in exact millimetres (1 in = 25.4 mm): max riser 177.8, min tread 279.4. Size the stair from
  the skill's limits, not the Revit type's (default type says 178 / 275, which fails the US general/egress rules).
  (HR, 2026-10-21, when stair-code-check was filled.)
- Default basis is US (IBC/IRC + NFPA 101) for every job without a project document, Turkish projects included;
  don't ask the basis again unless the user or project names UK/TR/another code. (Al, 2026-10-21)
- Size every stair with the Blondel design method (skill §4 step 0): `stair_run.py --target-riser 0.17 --blondel 0.63`
  (0.66 exterior) + the family's `--max-riser/--min-tread`; never take the fewest-risers result as the design.
  (Al's second paste, 2026-10-21.)
- (Superseded 2026-10-26, see above: duplicating StairsType/RailingType was refused on 2026-10-21 only because the
  old add-in took FamilySymbols only.)
  Don't raise a stair type's `Minimum Run Width` while runs of that type are narrower: on 2026-10-21 that call
  timed out and the bridge stopped answering (suspected Revit modal error). Widen the new runs via `Actual Run
  Width`, or delete the old stairs first. (Аэровокзал, 2026-10-21.)
- Landing depth: measure from the run's end (nosing line = walking-line end); the top riser sits 25 + 6 mm behind it
  under the landing, so the stair bbox overhangs 32 mm at the top end only. Report both values when margins are tight.
- A free-standing `revit_create_railing` rail sits ~12.5 mm left of its path (bbox centre ≠ path); read the bbox and keep
  it on the slab (path ≥ 50 mm inside a slab/landing edge). (Аэровокзал, 2026-10-21.)
- `revit_create_stair` builds the run with the DOCUMENT-DEFAULT stair type's tread/run width (Project1: 613631 → 255 / 1360)
  and swaps to `stairsTypeName` afterwards. For another tread: draw the line as (n − 1) × default tread, then set the
  stair's `Actual Tread Depth`; the run grows from its fixed start. Too many risers → set the run's `Relative Top
  Height` to the storey height. Read back after every build. (Аэровокзал external stairs, 2026-10-26.)
- Assembled-stair stringers sit outside the run width (bbox = run + 2 × stringer); each new run gets two hosted
  "Handrail - Rectangular" 900 rails 76 mm inside its edges (clear = run − 0.152). (2026-10-26.)
- An Assembled-stair stringer foot bears on the base level for ≈ 0.5 m behind the first riser: a ground landing / pad under an
  external stair must run that far under the run, not stop at the riser line. Façade elevations show the foot side-on (calibrate
  on grids) without creating a section. (Аэровокзал external stairs, 2026-10-30.)
- Every stair job plans and checks its landings — bottom, top and intermediate — with the skill's §3c LD block; the
  report has one LD line per landing. `stair_run.py --floor-landing-depth` gives the top/bottom zones that must be free
  of walls and door swings. (Al, 2026-10-30: "the intermediate-landing issue is important".)
- Multi-flight stairs: build ONE Stairs element with `create_stair` `runs` (+ `treadDepth`, `runWidth`, `desiredRisers`, `stairsTypeName`) — real StairsLanding, no intermediate level or Floor stand-in. Automatic landing for straight/collinear runs; pass `landingProfiles` for a U-stair in a walled cell. If the session's `revit_create_stair` schema lacks `runs` (MCP server not restarted since 2026-10-30), the add-in accepts it on /mcp directly; `revit_batch` refuses it. (Аэровокзал, 2026-10-30.)
