---
name: revit-sheet-audit — dimensioning and lettering
description: ISO 129 dimensioning rules and ISO 3098 lettering-height rules, as concrete pass/fail checks for a Revit sheet's dimension strings and annotation text.
---

# Dimensioning and lettering

## 1. Dimensioning — ISO 129 (TS EN ISO 128-family and BS EN ISO 128
projects; treat as good practice even under NCS, which doesn't fully
codify this)

- **Readable from bottom or right.** All dimensions, symbols, and
  annotations must be oriented to be read from the bottom or the
  right-hand side of the sheet (the two "main reading directions") — not
  upside-down or at an arbitrary angle.
- **Complete and shown directly on the drawing.** Don't leave a dimension
  chain open or imply a value "by subtraction" — show it.
- **Dimension each feature once.** The same distance/feature must not be
  dimensioned twice in different places on the same sheet (a common
  Revit copy-paste artifact across views) — that's a defect, not
  redundancy-as-safety.
- **Out-of-scale values are underlined.** If a dimension doesn't match the
  plotted scale (a deliberate override), ISO 129 requires underlining that
  value — an un-underlined out-of-scale dimension is a defect.
- **Auxiliary (reference) dimensions go in parentheses** and are never
  toleranced — if a Revit dimension string includes a reference/"ref"
  value, confirm it's parenthesised, not presented as a controlling
  dimension.

**Pass/fail checks (R-codes in `recurring-issues-checklist.md`):** every
dimension string closes (no floating/open chains); no feature dimensioned
twice on the same sheet; any out-of-scale value is underlined; auxiliary
values are parenthesised.

## 2. Lettering — ISO 3098

- **Nominal letter heights** (mm, same 1:√2-style progression as the line
  weights): `1.8 — 2.5 — 3.5 — 5 — 7 — 10 — 14 — 20`. Height is measured on
  the upper-case (capital) letter outline.
- **Orientation:** upright, or sloped at 75° from horizontal — pick one and
  use it consistently across the sheet/set, don't mix upright and sloped
  text.
- **Line width of the lettering stroke itself** is tied to height: roughly
  h/10 for the heavier lettering type, h/14 for the lighter type — i.e.
  larger text should also look visibly "bolder," not just bigger at the
  same stroke weight.

**Suggested height-to-purpose mapping for an architectural sheet** (pick
the nominal size closest to these at final plot scale):
| Text role | Nominal height |
|---|---|
| Sheet title / main heading | 7 or 10 mm |
| View/drawing titles | 5 mm |
| Dimension text, tags, schedule body text | 2.5 or 3.5 mm |
| Fine print — notes, legends, small annotation | 1.8 or 2.5 mm |

**Pass/fail checks:** text height is one of the nominal ISO sizes (or the
project's own documented equivalent) rather than an arbitrary value; the
same text role (e.g. all dimension text) uses the same height across the
whole sheet/set; upright and sloped lettering aren't mixed on one sheet.
