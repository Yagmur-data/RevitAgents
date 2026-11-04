---
name: Revit_DoorWindow lessons
description: Curated, rule-form corrections distilled from activity_log.md — read this before every task, not just the raw log. One durable rule per line.
---

# Revit_DoorWindow — lessons

Each line is one standing rule, stated as a concrete instruction, promoted
here from the activity log once it's proven worth remembering permanently.
Don't duplicate the chronological log here — only the distilled rule.

Seeded by HR on 2026-10-21 from Revit_Guide's read-only + dry-run survey of
Project1 (Аэровокзал Северное) and the workspace's revit-mcp-traps memory:

- A `revit_place_family_instance` dry run proves only that family/type/host
  resolve: a point 2 m off the wall or 5 m past its end still returns
  `placed: true`. Prove the position with `opening_layout.py` before and the
  read-back (location, `Host Id`) after.
- Always pass `familyName` + `familyTypeName` + `category`: "900 x 2100mm"
  exists in three door families and a bare type name takes the first match.
- No tool returns a wall's location curve; `revit_get_element_info` gives a
  bbox in FEET that extends into wall joins (wall 1658711: bbox x −0.1435…25.0
  m, Length 25.0, line 0…25 at y 16.0). Use `wall_line.py` with `--joins`.
- Placed windows come in with `Sill Height` 0 — set it right after placing
  (type `Default Sill Height` is 900 on the Casement-Double types here).
  Hosted placement on L2 with `location.z` = 0 puts the window on L2 with Sill 0
  relative to L2 (no doubling, verified 2026-10-22) — always place at z = 0 and set
  `Sill Height` afterwards.
- Non-hosted placement on an upper level can double "Elevation from Level";
  always place hosted and check Sill/Head relative to the level (L2 = 4.2 m
  in Project1).
- Door flip state is geometry, not a parameter: read it with
  `revit_get_doors`, set it only at placement (`flipFacing` / `flipHand`).
  Re-flipping a placed door = delete + re-place, same type and `Mark`.
- Curtain walls ("M_Exterior Glazing", ids 1658715…1658723 in Project1) can't
  host ordinary doors/windows — check the host wall family before placing.
- Door type `Fire Rating` is an empty string on the M_Door types in Project1
  (windows carry "0.5h"); a fire door needs a duplicated type with the rating
  set, with the user's yes.
- Project1 numbering: instance `Mark` runs from 100 upward; continue it, never
  reuse a Mark.
- Аэровокзал Северное (Russia_Aerovokzal, Project1): its ТЗ cites СП → basis `ТЗ — RF: СП 1.13130.2020 (ред.
  16.06.2025) + СП 59.13330.2020`, rules `door-window-code-check` §3b. Known inputs: Ф3.3, building < 28 m;
  fire-resistance degree and С-class not given — ask before RF-F2 / RF-H1. Read
  `Russia_Aerovokzal/standards_ru.md` first. (HR, 2026-10-21)
- Revit `Width` on a door type is not the clear width «в свету»: estimate clear = Width − Thickness − 0.01 and
  report "borderline" when only the nominal width passes (skill §3b note 1). A 900 door (~0.85 clear) does not
  prove the 0.9 m accessible width.
- Window facing has no tool: read it from the bbox — the exterior side reaches only 0.1735 m past the centreline on
  the 287 mm panel wall, the interior side ~0.62 m. Same values on every window = consistent facing. (from/to room
  is NOT evidence on exterior openings — see the 2026-10-23 door lesson.) (2026-10-22)
- Read a window/door position back with `revit_get_element_geometry`: bbox centre along the wall = insertion point
  (exact on the M_ families), far shorter output than `revit_get_element_info`. (2026-10-22)
- In `opening_layout.py --existing`, add every partition that meets the host wall as a 0.125 m "opening" at its
  centreline, so `--min-gap` also proves the clearance to partition faces. Check per floor on two-storey walls.
  (2026-10-22)
- Revit auto-assigns the next free Mark (per category) to a placed window — read it before setting one. (2026-10-22)
- A hosted door's DEFAULT facing depends on the host wall's direction (Project1: west wall default faced in, east
  wall too, but with opposite vectors) — place, read facing, and re-place your own fresh instance with the flags.
  `flipFacing` keeps the hinge jamb; `flipHand` moves it. (2026-10-23)
- Hinge side of an M_ single door: `handX/Y` from `revit_get_doors` points to the hinge jamb (verified on plan
  arcs, Two_Lite); the 3D leaf is modelled open, so the bbox reaches ~0.875 m past the wall face on the swing side
  and overhangs the rough opening ~19 mm on the hinge side. (2026-10-23)
- `revit_get_element_rooms` from/to room does NOT follow the swing — exterior doors give fromRoom null / toRoom the
  room, interior doors keep the same from/to after a flipFacing re-place (2026-10-26). Swing = `facingX/Y` + bbox.
  (2026-10-23, widened 2026-10-26)
- On every door job run `revit_check_clearance` (bbox, 0 mm) doors x OST_Furniture + OST_PlumbingFixtures — the
  door bbox carries the 90-deg open leaf; then test the swing arc (quarter disc r = leaf) against nearby fixture
  bboxes by hand, the bbox check misses the arc. After a delete + re-place, read the Mark: Revit sometimes re-uses
  the freed one, sometimes assigns the next. (2026-10-26)
- Deleting a tagged door also deletes its tag (dry-run delete returns 2 ids: door + Door Tag) — a delete + re-place must
  re-tag it in the plan; list the tag when asking for the yes. (2026-10-30)
