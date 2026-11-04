---
name: revit-sheet-audit — recurring issues checklist
description: R1-R12 recurring-defect checklist for Revit sheet audits, each tied to a concrete standard clause from the other reference files. Run this on every sheet in addition to the category sweep in SKILL.md §2.
---

# Recurring issues checklist (R1-R12)

Run this sweep on every sheet, in addition to the six categories in
`../SKILL.md` §2. These are the failures most likely to recur — missing
one of these is the main way an audit under-counts real defects.

| # | Defect | Standard basis | Default severity |
|---|---|---|---|
| R1 | Title-block field blank, or contradicts sheet content (wrong scale note, wrong sheet name/number) | ISO 7200 (`sheet-sizes-and-title-blocks.md` §2) | CRITICAL |
| R2 | Fewer than 3 distinct line weights used, or the thick:thin ratio used is below 2:1 | ISO 128/TS EN ISO 128 §1, or NCS §2 (`line-weights-and-types.md`) | WARNING |
| R3 | Dashed/hidden-line convention used for content that isn't actually hidden (stylistic substitute) | ISO 128 line-type table (`line-weights-and-types.md` §1) | ADVISORY |
| R4 | View scale mismatch between sibling views on the same sheet, or between the plotted view and its title-block scale note, with no stated reason | `sheet-sizes-and-title-blocks.md` §2 | CRITICAL |
| R5 | Visible, schedule-relevant element with no tag, where the same element type is tagged elsewhere on the same or a sibling sheet | — (internal consistency) | WARNING |
| R6 | Schedule/tag/model count mismatch — a schedule row with nothing tagged anywhere, or a tagged element missing from its schedule | — (internal consistency) | CRITICAL |
| R7 | View overlapping the sheet border, the title block, or another view | ISO 5457 drawing-space margins (`sheet-sizes-and-title-blocks.md` §1) | WARNING |
| R8 | Missing or stale revision-history entry in the title block for a sheet that has actually changed since a prior review round | ISO 7200 (`sheet-sizes-and-title-blocks.md` §2) | WARNING |
| R9 | Open/floating dimension chain, or the same feature dimensioned twice on one sheet | ISO 129 (`dimensioning-and-lettering.md` §1) | WARNING |
| R10 | Inconsistent lettering height for the same text role (e.g. dimension text) across one sheet, or mixed upright/sloped lettering | ISO 3098 (`dimensioning-and-lettering.md` §2) | ADVISORY |
| R11 | North arrow missing on a plan view, or scale bar missing/mismatched with the view's actual scale | `symbols-and-drawing-arrangement.md` §2-3 | WARNING |
| R12 | Revision cloud with no matching delta tag and title-block row, or a stale cloud left over from an already-superseded round | `symbols-and-drawing-arrangement.md` §4 | ADVISORY |

Severities above are defaults — judge the actual sheet; a severity can be
raised (e.g. R1 missing scale note on a sheet that will govern a
measurement in the field) or lowered with a stated reason.
