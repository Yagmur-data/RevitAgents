---
name: Revit_Roof lessons
description: Curated, rule-form corrections distilled from activity_log.md — read this before every task, not just the raw log. One durable rule per line.
---

# Revit_Roof — lessons

Each line is one standing rule, stated as a concrete instruction, promoted
here from the activity log once it's proven worth remembering permanently.
Don't duplicate the chronological log here — only the distilled rule.

- `revit_create_roof` failing with `NewFootPrintRoof rejected argument ''
  (ArgumentNullException)` means the pre-fix add-in DLL is loaded (null
  `ModelCurveArray` out-arg). Stop and ask for the add-in rebuild; never fall
  back to a Floor without the user's explicit OK. (Seeded by HR 2026-10-21
  from the Аэровокзал job, where the roof had to be modeled as a Floor.)
  Since the 2026-10-26 deploy the tool works (dry run + real run OK, `edgeSlopesDeg` echoed); that error now
  means the deploy was rolled back or a second Revit loaded an old DLL.
- A flat FootPrintRoof sits ON its level (bottom = level elevation, top = level + thickness). For "roof top at
  the level" set Base Offset From Level = −thickness right after creating, then re-read the bbox. (2026-10-26)
- Deleting a sketch-based Floor/Roof takes its sketch with it (~28 ids: sketch plane, sketch, boundary lines,
  span edge, auto sketch dims). Dry-run the delete, check that the extras are only that sketch, and name them. (2026-10-26)
- Roof types are listed by `revit_list_elements` category `OST_Roofs`
  (`typeId: -1` = type); `revit_list_family_types` does not return RoofTypes.
  The type list includes "Sloped Glazing" — never use it as a default.
  (Checked live 2026-10-21.)
- Аэровокзал Северное (Russia_Aerovokzal): the ТЗ names standards (СП 478.1325800.2019, ГОСТ Р 21.101-2020, general
  СП/ГОСТ/СНиП clause), so roof-code-check's IBC rules and airport module are NOT added (skill §0). Basis = ТЗ / RF
  norms; no roof figures in the ТЗ → ask Al for СП values, report measurements only. Read
  `Russia_Aerovokzal/model_notes.md` first (roof is currently a 300 mm Floor stand-in). (Al, 2026-10-21)
  Al's RF airport figures (2026-10-21) are in `Russia_Aerovokzal/standards_ru.md` — no roof figures and no OLS
  limit among them; still ask for СП 17.13330 values and the OLS height.
