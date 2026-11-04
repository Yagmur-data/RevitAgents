---
name: revit-sheet-audit — symbols and drawing arrangement
description: ISO 7519 drawing-hierarchy/arrangement principles plus the north-arrow, scale-bar, and revision-cloud conventions a Revit sheet audit checks for.
---

# Symbols and drawing arrangement

## 1. Drawing hierarchy and arrangement — ISO 7519

ISO 7519 sets out a hierarchy of construction-drawing types and expects a
set to be arranged and presented consistently through it:
site plan → site layout drawing → general arrangement (GA) drawing →
assembly drawing → component drawing → detail drawing.

**Pass/fail checks:** the sheet set, read in sheet-number order, actually
goes from broad (site/GA) to specific (assembly/detail) — a detail sheet
numbered ahead of the GA plan it belongs to, or a GA plan missing entirely
from a set that includes its details, is a defect. Within one sheet, plans
are ordered low-to-high, then sections, then elevations, then details —
not an arbitrary order.

## 2. North arrow

- Placed in the **upper-left corner** of the sheet by the most common
  convention (acceptable alternative: directly adjacent to the plan it
  orients, if the title block occupies the upper-left).
- Required on every plan view where orientation matters (floor plans,
  site/layout plans); not required on sections, elevations, details, or
  schedules.
- If the project uses both **plan north** (drawing-sheet-up convention) and
  **true north** (actual geographic north), both arrows must be shown and
  clearly distinguished — a single unlabeled arrow when the project is
  known to use a rotated plan-north is a defect.

## 3. Scale bar

- A graphic scale bar should accompany the stated numeric scale on any
  sheet likely to be printed or viewed at a reduced size (i.e. essentially
  every plotted sheet) — the numeric scale alone is not sufficient,
  because it becomes wrong the moment the sheet is reproduced at a
  different size.
- The scale bar's graduations must actually match the view's stated scale
  — a copy-pasted scale bar left over from a different view's scale is a
  defect (and a common Revit multi-view-per-sheet mistake).

## 4. Revision marking

- A **revision cloud** encircles the specific area that changed since the
  previous issued revision.
- A **revision delta/triangle tag** (a small numbered triangle or circle)
  ties that cloud to a row in the title block's revision-history table —
  the cloud alone, without a delta tag and a matching title-block row, is
  incomplete.
- Once a sheet is reissued, prior revision clouds from earlier rounds
  should be removed (or clearly superseded) — accumulating clouds from
  multiple past rounds on a current issue is a defect, not a complete
  history (the complete history belongs in the title-block revision table,
  per `sheet-sizes-and-title-blocks.md` §2).

**Pass/fail checks (feeds R-codes in `recurring-issues-checklist.md`):**
north arrow present on every plan, in a consistent location across the
set; scale bar present and graduated to the view's actual scale; any
revision cloud on the current issue has a matching delta tag and
title-block row; no stale clouds from already-superseded rounds remain.
