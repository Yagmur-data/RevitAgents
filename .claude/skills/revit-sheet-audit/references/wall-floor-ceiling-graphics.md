---
name: revit-sheet-audit — wall / floor / ceiling graphics module
description: Category 7 of revit-sheet-audit — how walls, floor slabs, floor finishes and ceilings must be shown on sections (1:5–1:100), details, floor finish plans and reflected ceiling plans (RCP). Al's office convention, sent 2026-10-30, layered on top of the chosen standard family as a client/office manual (SKILL.md §1, last bullet). Used by Revit_Sheet (scoring) and Revit_Drafter (drafting).
---

# Wall / floor / ceiling graphics (WF1–WF8)

**Basis.** Al's office convention (two texts sent 2026-10-30; full wording
in `.claude/skills/wall-floor-code-check/references/al-wall-floor-drawing.md`;
Al gave no source documents for his bracketed references). It is applied as
an **office manual on top of the job's standard family** (§1 of SKILL.md):
the family still governs sheet sizes, title blocks, numbering and the
line-weight series; this module adds what walls, slabs, finishes and
ceilings must show. Report header: `Basis: TS EN ISO 128 (default) + Al
office convention — wall/floor/ceiling (2026-10-30)`.

**Checked against the existing rubric (HR, 2026-10-30):** Al's weights all
sit on the ISO 128 series and keep the cut > projection > dimension order
of `line-weights-and-types.md` (1:50: 0.25 / 0.35 / 0.70; 1:100: 0.25 /
0.35 / 0.50). One difference: at 1:20 / 1:10 that file has thin 0.35,
while Al's dimension lines are 0.25 — on details, Al's 0.25 is accepted,
because the office manual supplies the specifics. Al's sheet-layout line
(grid bubbles, scale, north arrow, detail/section markers placed "per CSI
UDS / NCS") applies **only when the job's family is US NCS**; under the TS
EN ISO 128 default the same items are checked against ISO 5457 / 7200 /
7519 as before — the families are not blended.

**Third text (2026-10-30)** — flooring & finishes, drywall partitions and
suspended ceilings; Al names CSI UDS / NCS, ISO 128 / ISO 7519, BS EN 13964
and IBC ch. 25 / ASTM C840 as the frame (those documents themselves are not
loaded here). It added the joint-grid and build-up line weights (WF1), SSL
(WF4), ceiling frame/T-grid (WF6), WF9 drywall and WF10 legend. Its UDS
sheet codes (`A-101` floor plan, `A-102` RCP, `A-103` floor finish plan,
`A-501` system/detail sections) are numbering under the **US NCS** family
only. **Russian jobs:** the Аэровокзал ТЗ requires **ГОСТ Р 21.101-2020**
for drawings. That family is now loaded (`russia-gost-spds.md`, 2026-10-30):
on that job WF graphics apply, and sheet numbering/title blocks are scored
against the RF rows, never UDS or ISO 19650; say so in the report header.

Applies to: building sections and wall sections (1:100, 1:50), system
details (1:20, 1:10, 1:5), floor finish plans (zemin kaplama planı) and
reflected ceiling plans (RCP / yansıtılmış tavan planı). Other sheets: skip.

| # | Check | Al's convention | Default severity |
|---|---|---|---|
| WF1 | **Line hierarchy on sections/details** | Cut walls, RC walls/columns and slabs: heaviest line, 0.50–0.70 mm (up to 1.00 at detail scales). Elements seen beyond the cut (wall edges, parapets, slab edges): medium 0.35–0.50. Build-up lines inside the section (screed, membranes, skirting) and the floor finish line: 0.25–0.35. Grid/axis: chain-dot 0.25–0.35. Dimension and extension lines: thin 0.25. Tile/stone/timber joint grid in plan: finest, 0.13–0.18. Hidden beams under the slab, lintel outlines, slab voids and ceiling lines above the cut: dashed | WARNING (cut elements not the heaviest line = WARNING even if R2 passes) |
| WF2 | **Material hatches distinguishable and consistent** | Brick/masonry: 45° single or double parallel lines. Concrete: fine dots + small triangles; reinforced concrete: extra cross lines or dark fill. Thermal/acoustic insulation (stone wool, EPS/XPS): wavy or zigzag line. Plaster, mortar, adhesive (3–5 mm), screed: very fine dots. DPC / waterproofing membrane: dark band or special membrane line. In plan, finishes drawn to scale: tiles as a grid, parquet as herringbone/basket pattern, natural stone | WARNING when two different materials share a hatch or a cut element is unhatched; ADVISORY when a different hatch is used consistently with a legend |
| WF3 | **Build-up order and leader notes** | Floor, top → bottom: finish (type + thickness, e.g. 15 mm laminate, 10 mm porcelain) → adhesive/mortar → levelling screed (typically 30–50 mm) → water/thermal/acoustic layer → RC slab (type + thickness, e.g. 150 mm RC slab, waffle slab) → ceiling plaster or suspended ceiling (plenum, hangers, main/cross profiles, boards drawn to scale). Wall, outside → inside: cladding / external render → insulation → wall body (brick / aerated concrete / block) → internal plaster → finish/paint. Leaders aligned vertically, one per layer, listed in build order | WARNING (missing layer or thickness); ADVISORY (unaligned leaders) |
| WF4 | **Levels** | Plan: FFL in every room (`FFL +2.750`, `FFL 12.335` or a dot/cross symbol relative to ±0.000). Section/elevation: level arrows (filled/open) on projection lines outside the drawing, both structural slab level (SSL / kaba, e.g. +2.690) and finished floor (FFL / bitmiş, +2.750) | WARNING missing; **CRITICAL** when a level on the sheet contradicts the model (level elevation / floor offset) — it governs construction |
| WF5 | **Floor finish plan** | Cut at ~1.00 m looking down; walls/structure in cut weight; tiled areas: starter tile marked and joint axes in thin line; transitions between finishes: threshold profiles, expansion/movement joints; room tag = name + area (m²) + finish code (K01 epoxy, K02 laminate …) keyed to a sheet legend | WARNING (legend missing or a code without a legend entry = R6-type mismatch → CRITICAL) |
| WF6 | **Reflected ceiling plan** | Same orientation as the floor plan (mirror on the floor). Modular ceilings (60×60, 60×120): visible or concealed T-grid in thin line; monolithic plasterboard: seamless surface with ceiling boundaries, coffers/light troughs, its frame (T-24, C-channel, hangers) drawn to scale in the detail section. Ceiling height per room relative to finished floor (`FCL = +2.60` or "tavan yüksekliği 260 cm"). Light fittings (recessed/surface, LED lines, spots), HVAC supply/return diffusers and grilles, sprinkler heads, smoke detectors, PA speakers when those systems are modelled; access panels outlined dashed/thin | WARNING (FCL missing, orientation wrong); ADVISORY (MEP items missing when the MEP model is linked) |
| WF7 | **Modular chain dimensions** | Wall thicknesses, openings and slab thicknesses on 100 / 300 mm modules where the design uses them; chains run inside → outside | ADVISORY |
| WF8 | **Grid bubbles** | Reference axes named in bubbles with letters and numbers on plans and sections | WARNING when grids are shown without bubbles/names |
| WF9 | **Drywall partitions** | Plan: double-line wall boundary; at detail/large scale the C-stud / U-runner axes and labels. Section/detail: gypsum board layers to scale (12.5 mm standard, 15 mm or fire-rated Type X noted), cavity mineral/glass wool as a wavy line. Partition types coded on plan (`W1`, `W2` …) with a legend entry for each code | WARNING (code without legend entry → CRITICAL, same as R6); ADVISORY (stud axes missing at 1:20 or larger) |
| WF10 | **Legend / keynotes** | Every hatch, line type, wall type and floor/finish type used on the sheet is defined in the sheet's symbol legend or keynote list | WARNING per undefined item; a code used but defined nowhere in the set → CRITICAL |

## How the two agents use this

- **Revit_Drafter** drafts sections, details, floor finish plans and RCPs to
  WF1–WF8 before the first export: object styles / view-template line
  weights, fill patterns per material, spot elevations (FFL/FCL) or level
  heads, material tags in build order, a finish legend and ceiling heights.
  Model gaps (no finish layer, no ceilings, floor offsets wrong) are not
  drawn around — hand them to **Revit_WallFloor** (floors/walls) or
  Revit_Guide (ceilings) and say so in the job log.
- **Revit_Sheet** scores WF1–WF8 like the other categories, citing
  "Al office convention WFn" as the standard basis in the defect table.
