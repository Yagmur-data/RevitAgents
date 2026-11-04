---
name: revit-sheet-audit — sheet sizes, title blocks, and drawing numbering
description: ISO 216/5457 sheet sizes and margins, ISO 7200 title-block required fields, and the two competing drawing-numbering conventions (ISO 19650/BS 1192 vs US NCS sheet-numbering) a Revit sheet audit checks against.
---

# Sheet sizes, title blocks, and drawing numbering

## 1. Sheet sizes and layout — ISO 216 / ISO 5457 (TS EN ISO 128 / BS EN ISO
128 basis)

- ISO A-series sheet sizes, A0 down to A4 (A1/A3 most common for
  architectural sets).
- **Margins**: 20 mm on the binding (left) edge for filing, 10 mm on the
  other three edges.
- A continuous **0.7 mm** frame line marks the drawing space inside those
  margins — this is itself one of the "thick" weights from
  `line-weights-and-types.md`, so check it isn't drawn thinner than the
  sheet's own heaviest content line.
- A0–A3 sheets are landscape with the title block at the bottom-right
  corner; A4 is portrait with the title block across the bottom (shorter)
  edge.

**Pass/fail checks:** sheet frame present at the correct margins; title
block in the standard corner/edge for its sheet size; frame line weight not
thinner than the heaviest content line on the sheet.

## 2. Title-block required fields — ISO 7200

Minimum fields a compliant title block must carry, all of which map to
Revit sheet/title-block parameters and should be checked as filled and
internally consistent:
- Drawing number / unique identifier
- Drawing title / subject
- Owner / legal company name
- Scale and units
- Projection-method symbol (first-angle / third-angle), where relevant
- Date of issue
- Revision history (revision number, date, description, who)
- Author / checker / approval signatures or initials
- Sheet "X of Y" when the set has multiple sheets

Title-block width is capped at **170 mm** in the ISO scheme (so it fits a
folded A4 cover sheet) — mostly relevant for ISO/TS EN ISO 128 projects;
not a hard constraint under NCS, but excessive title-block width crowding
the drawing space is still a legibility defect either way.

**Pass/fail checks (R1 in `recurring-issues-checklist.md`):** every field
above is present and non-empty; the scale noted in the title block matches
the actual plotted scale of the principal view on that sheet; revision
history has an entry for every round the sheet has actually gone through a
Revit_Sheet review cycle.

## 3. Drawing / sheet numbering conventions

Two families; pick per the basis chosen in `../SKILL.md` §1 and use it
*consistently* across the whole set — a mixed numbering scheme on one job
is itself a defect.

### 3a. ISO 19650 / BS 1192 (use when BS EN ISO 128 is the governing family,
or the project is BIM-managed under an ISO 19650 contract regardless of
drafting-line family)

Container/file identifier built from ordered fields:
`Project – Originator – Volume/System – Level/Location – Type – Role –
Number – Suitability – Revision`
- Project: 2-6 alphanumeric characters.
- Originator: 3-6 characters identifying the authoring company —must be
  unique to that company.
- Volume/System: 1-2 characters.
- Level/Location: always 2 characters; `ZZ` = multiple levels, `XX` = not
  applicable.
- Type / Role / Number: discipline and document-type coding per the
  project's own BIM Execution Plan.
- Suitability + Revision: status code (e.g. S0, A, B…) + revision number.

**Pass/fail check:** every sheet number in the set actually follows the
agreed field order and character-count rules — a sheet number that's
missing a field, or whose Level/Location isn't 2 characters, is a defect.

### 3b. US NCS sheet organisation (use when NCS/AIA is the governing
family)

Sheet numbers follow `<Discipline Letter><Sheet Type Digit><Sequence>`,
e.g. `A-101` (Architectural, Plans, sheet 01). Discipline letters match the
AIA layer-naming discipline codes in `line-weights-and-types.md` §2.

**Pass/fail check:** discipline letter matches what's actually drawn on the
sheet (an architectural plan numbered under a structural discipline letter
is a defect); sheet-type digit is used consistently across the set (all
plans share one digit, all sections another, etc.).

### 3c. Default / unspecified

If the user hasn't adopted either formal numbering scheme, don't invent
one — just check **internal consistency**: every sheet in the set follows
the same pattern the project has already established, with no gaps or
duplicate numbers.
