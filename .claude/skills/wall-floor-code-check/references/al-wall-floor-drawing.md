---
name: Al's wall / floor / ceiling drawing conventions
description: Al's own two texts (sent 2026-10-30) on line weights, material hatches, levels, build-up notation and how floor slab, floor finish and ceiling are shown in sections (1:5–1:100), the floor finish plan and the reflected ceiling plan (RCP). Used by wall-floor-code-check §3d (build-up, FFL/FCL) and, for the graphics, by Revit_Drafter / Revit_Sheet. Footnote markers of the source were removed; translated into English from Al's Turkish original, content otherwise as sent.
---

# Wall, floor, finish and ceiling representation (Al, 2026-10-30)

Two texts; the second is §5–§9. Al gave no source document names (the bracketed footnote numbers were removed).

In architectural and interior-design projects, the floor slab, the floor
finish and the ceiling are shown in two basic view planes: section drawings
(1:5, 1:10, 1:20 detail sections and 1:50, 1:100 general sections) and plan
drawings (the Floor Finish Plan and the Reflected Ceiling Plan / RCP).

## 1. Layer order in section and detail drawings (top to bottom)

| Layer | Representation | Thickness / note |
|---|---|---|
| A. Floor finish | Thin/medium line 0.25–0.35 mm. Hatch: ceramic/tile grid; timber parquet double line/section hatch; carpet/PVC fine dots or blank | Type + thickness are written (e.g. 15 mm laminate parquet, 10 mm porcelain ceramic) |
| B. Adhesive / mortar | Fine dot/stipple hatch | 3–5 mm |
| C. Levelling screed | Very fine dot hatch | typically 30–50 mm |
| D. Thermal / acoustic / water insulation (insulation, DPC) | Thermal/acoustic: zigzag or wavy line; damp/water (DPC/membrane): dark thick band or a special dashed line | — |
| E. Structural slab | Cut in section, so the heaviest line 0.50–0.70 mm, or the reinforced-concrete hatch (dots + small triangles) | Type + thickness are written (e.g. 150 mm RC slab, waffle slab) |
| F. Ceiling | Directly plastered ceiling: thin plaster on the slab soffit. Suspended ceiling: plenum void, hanger rods, main/cross profiles, ceiling boards (plasterboard, stone-wool tile, linear metal) to scale | — |

## 2. Floor finish plan

1. The plan is a view from above onto the finished floor (cut at the 1.00 m level, looking down).
2. Walls and structural members are cut → heavy line.
3. Ceramic/marble/tile: the joint starting point (starter tile) is indicated; joint axes in thin line.
4. Material transitions: threshold profiles and expansion/movement joints are shown.
5. Finished floor level `FFL +2.750`, or with a dot-in-circle mark, in the middle of the room.
6. Room tag: name, area (m²), floor finish code (e.g. K01 epoxy, K02 laminate parquet), referenced to the sheet legend.

## 3. Reflected ceiling plan (RCP)

A view of the ceiling as seen in a mirror laid on the floor — the orientation coincides exactly with the floor plan.

1. Modular suspended ceiling (60×60, 60×120): profile axes in thin line; plasterboard ceiling: ceiling boundaries, coffer/light-cove details.
2. Ceiling level, net from the finished floor: `FCL = +2.60 m` or ceiling height 260 cm.
3. Integration: lighting (recessed/surface-mounted, LED line, spot); HVAC supply and return diffusers and grilles; sprinklers, smoke detectors, emergency PA speakers; access panels in dashed/thin line.

## 4. Dimensioning and notation

- Leader lines: in detail sections the layers are listed in order with leader arrows, aligned vertically.
- On plan, finished level `FFL +0.000`; in section, structural and finished levels with vertically aligned arrows (e.g. structural slab `+2.690`, finished floor `+2.750`).

## 5. Line weights and types (second text)

- Section lines (heavy continuous): cut load-bearing walls, RC shear walls/columns, floor slabs — 0.50–1.00 mm depending on scale.
- Elevation lines (medium continuous): wall outlines, parapets, slab edges that are not cut but seen beyond — 0.35–0.50 mm.
- Grid lines dash-dot 0.25–0.35 mm; dimension and extension lines thin continuous 0.25 mm.
- Hidden / upper-level elements (dashed): beams under the slab, lintel outlines, slab openings at the level above, suspended ceiling lines.

## 6. Material hatches

- Brick/masonry: single or double parallel lines at 45°. Concrete/RC: fine dots + small triangles; in reinforced concrete an additional diagonal line or a dark fill. Thermal insulation (stone wool, EPS/XPS): wavy/zigzag. Plaster/mortar: very fine stipple.
- In a floor section: DPC as a dark band/membrane line, screed fine dots, thermal/acoustic insulation zigzag, RC slab with the reinforced-concrete symbol — layer by layer.
- On plan, finishes to scale: ceramic grid, timber parquet herringbone/basket-weave, natural stone.

## 7. Levels and dimensioning

- On plan: the abbreviation FFL, or a point marked `x` relative to ±0.000 (e.g. `FFL 12.335`, `+2.750`).
- In section/elevation: a filled/open arrow on a projection line extended outside the drawing (structural `+2.690`, finished `+2.750`).
- Modular dimensioning: wall thicknesses, door and window openings, slab thicknesses on 100 / 300 mm modules; chain dimensions from inside to outside.

## 8. Layer notation in section details (1:10, 1:20, 1:50)

- With aligned leader lines, in construction order, outside to inside or top to bottom.
- Floor: finish (ceramic/parquet) → adhesive → levelling screed → water/thermal insulation membrane → RC slab → ceiling plaster / suspended ceiling.
- Wall: external cladding / external render → thermal insulation → wall body (brick/aerated concrete/block) → internal plaster → internal paint/finish.

## 9. Sheet layout

- Reference grids in bubbles, with letters and numbers.
- Scale, north arrow, detail markers and section-direction symbols on the sheet margin strip and in the title area per CSI UDS / NCS rules (HR note: only on jobs where the US NCS family is chosen; under the TS EN ISO 128 default, ISO 5457/7200/7519 — `revit-sheet-audit/references/wall-floor-ceiling-graphics.md`).

## 10. Third text (Al, 2026-10-30) — floor finish, drywall partitions and suspended ceilings

The framework Al cited: CSI UDS / NCS, ISO 128 / ISO 7519, BS EN 13964 (suspended ceilings), IBC Chapter 25 / ASTM C840 (gypsum board systems). Bracketed source numbers were removed; no source list was given.

**Floor / finish — line hierarchy**
- Section line 0.50–0.70 mm: the cut RC floor slab and the structural shell.
- Medium line 0.25–0.35 mm: levelling screed, insulation membranes, skirting lines, slab edges seen beyond.
- Thin line 0.13–0.18 mm: ceramic, marble, timber finish joints (plan).

**Hatches**: structural slab with the reinforced-concrete symbol (fine dots + small triangles) or a dark solid fill; screed fine stipple; thermal/acoustic insulation wavy/zigzag; finish: ceramic/tile grid to scale, timber parquet herringbone / basket-weave / straight plank, natural stone/marble joint grid at panel size.

**Level and construction notation**: FFL (finished floor, `FFL +3.500`, `FFL 12.335`, in the middle of the room or at level points); **SSL** (Structural Slab Level — top of the structural rough RC slab); starter tile (laying direction and joint axis); layer list on a vertical leader, outside to inside / top to bottom — example: 10 mm porcelain ceramic → adhesive → 40 mm levelling screed → waterproofing → 150 mm RC slab.

**Drywall partition**
- Plan: wall edges as a double line; inside, the axes and labels of the galvanised C and U profiles (C-stud, U-runner).
- Section/detail: plasterboard layers as vertical lines to scale (12.5 mm standard, 15 mm or fire-resistant Type X); stone-wool/glass-wool infill inside the profiles as a wavy line.
- Wall type coding: on plan, referenced to a legend (e.g. `W1` single-layer plasterboard wall, `W2` double-layer Type X acoustic wall).

**Suspended ceiling (EN 13964 / RCP)**
- RCP: looking up as seen in a mirror laid on the floor; the ceiling sheet coincides exactly with the floor plan.
- FCL relative to the finished floor (`FCL = +2.60 m`).
- Monolithic plasterboard ceiling: a single jointless surface; framing (T-24, C-channel, hanger rods) to scale in the detail section. Modular ceiling (60×60 / 60×120): T-grid with exposed or concealed carriers, in thin line on plan.
- Integration: lighting (spot, LED strip, luminaire), HVAC diffusers/grilles, sprinklers, smoke detectors, access panels in dashed/thin line.

**Sheet layout (CSI UDS / NCS)**: `A-101` ground floor plan, `A-102` RCP, `A-103` floor finish plan, `A-501` system and detail sections; all hatches, line types and wall/floor types defined in the legend at the sheet edge (keynotes & symbols).
