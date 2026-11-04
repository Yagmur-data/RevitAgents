---
name: revit-sheet-audit — line weights and line types
description: Concrete line-weight and line-type values from ISO 128 / TS EN ISO 128 (Turkish default), BS EN ISO 128, and the US National CAD Standard / AIA CAD Layer Guidelines. Numbers are the actual standard values (not non-binding examples) — use them as pass/fail thresholds.
---

# Line weights and line types

## 1. ISO 128 / TS EN ISO 128 (default basis) and BS EN ISO 128

TS EN ISO 128 is TSE's identical adoption of ISO 128 (successor to the older
TS 88 series — TS 88-20 / EN ISO 128-20 covers general line conventions, TS
88-24 / EN ISO 128-24 covers mechanical-engineering-specific lines). BS EN
ISO 128 is the UK's identical adoption of the same international standard —
treat its line-weight/line-type values as numerically identical to TS EN ISO
128; only the drawing-numbering convention differs (see
`sheet-sizes-and-title-blocks.md` §3).

**Standard thickness series** (ratio 1:√2 ≈ 1:1.4), mm:
`0.13 — 0.18 — 0.25 — 0.35 — 0.50 — 0.70 — 1.00 — 1.40 — 2.00`

Pick ONE "thick" weight and one "thin" weight for the sheet from this
series so the ratio between them is **at least 2:1** — this is the
pass/fail check, not just a suggestion.

**By drawing scale** (thin / medium / thick, mm):
| Scale | Thin | Medium | Thick |
|---|---|---|---|
| 1:100 and smaller (site, block plans) | 0.25 | 0.35 | 0.50 |
| 1:50 (floor plans) | 0.25 | 0.35 | 0.70 |
| 1:20 / 1:10 and details | 0.35 | 0.50 | 1.00 |

**Line-type usage on an architectural sheet** (ISO 128 types, letter codes
A/B/etc. from ISO 128-20/24; thickness per the table above):
| Line type | Thickness tier | Use |
|---|---|---|
| Solid thick (ISO type A — continuous wide) | Thick | Cut-plane edges: section-cut walls, columns, slabs — the heaviest line on the sheet |
| Solid medium (continuous) | Medium | Visible outlines of elements in elevation/view: door & window frames, visible edges, furniture outlines |
| Solid thin (ISO type B — continuous narrow) | Thin | Dimension lines, extension lines, axis/grid reference lines, hatching, leader lines |
| Dashed (hidden line) | Medium | Hidden/above-cut-plane elements: upper cabinets, overhead soffits, foundations below, anything not actually cut |
| Chain-dot (long-dash-dot) | Medium (thin body) / thick ends | Grid/axis lines (thin-to-medium body); section-cut-plane indicator lines use thick ends with a direction arrow |
| Dotted thin | Thin | Elements behind the view direction, or a swept/travel path (e.g. door swing arcs) |

**Pass/fail checks for Revit_Sheet:**
- At least 3 distinct, consistently-applied line weights are visible on the
  sheet (cut-plane heaviest, hidden/dashed medium, dimension/hatch finest) —
  fewer than 3, or inconsistent weight-to-meaning mapping, is a defect.
- The thick:thin ratio actually used is ≥ 2:1.
- Dashed lines are only used for genuinely hidden/above-plane content, not
  as a stylistic substitute for a solid line.

## 2. US National CAD Standard (NCS) / AIA CAD Layer Guidelines

NCS = AIA CAD Layer Guidelines (layer naming) + CSI Uniform Drawing System
(UDS Module 04 — drafting conventions, line weights & dimensioning) +
NIBS plotting guidelines, bundled as one standard. Use this family instead
of TS EN ISO 128 when the user says a US/North-American client or
AIA/CSI-governed contract applies.

**Pen-weight convention** (AIA/NCS numbered pen system, not raw mm — maps to
a plot-style pen table in the CAD/BIM software):
| Pen # | Typical use |
|---|---|
| Pen 4 | Boundary lines, legends, dimensions, notation/annotation text |
| Pen 7 | Construction lines, walls, border and title block |
| Pen 11 | Below-grade utilities: sewer/drainage pipework, manholes |

**Layer naming** (AIA 256-style: `Discipline-Major-Minor-Status`): first
letter = discipline code (A = Architectural, C = Civil, E = Electrical, S =
Structural, M = Mechanical, P = Plumbing, etc.), followed by a major group
and minor modifier, e.g. `A-DOOR` for doors, `A-WALL` for walls. On a Revit
sheet audit this maps to: are object-style/line-weight overrides on
Revit-native categories at least *consistent* with the discipline's
intended pen weight (heavy for walls/structure, light for
dimensions/annotation) even though Revit itself doesn't use AIA layer names
directly.

**Pass/fail checks:** same structural checks as §1 (≥3 weights, ≥2:1 ratio,
dashed reserved for hidden content) — only the naming/pen-number vocabulary
differs, not the visual hierarchy requirement itself.

## 3. Applying this in Revit

Revit's own "Line Weights" settings (model/perspective/annotation tables)
and object styles are the mechanism; what this reference fixes is the
**target hierarchy** to check the result against, regardless of which raw
Revit line-weight index number was used. A sheet fails category 3 (line
weight / graphics legibility, see `../SKILL.md` §2) if the *visual* result
doesn't match this hierarchy, even if the underlying numbers look
plausible in isolation.
