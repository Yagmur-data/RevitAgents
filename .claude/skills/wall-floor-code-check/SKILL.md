---
name: wall-floor-code-check
description: Wall and floor (döşeme) rules the Revit_WallFloor agent builds to, fixes against and reports on — model-integrity checks that need no standard (duplicate/overlapping walls, open joins, walls not tied to levels, uneven heights, foundation slab used as a floor, slab edges vs the wall outline, overlapping floors, storey clear height, room bounding) plus code rules for walls and floors. TR family (Planlı Alanlar İmar Yönetmeliği (Planned Areas Zoning Regulation), Binaların Yangından Korunması Hakkında Yönetmelik (Regulation on the Fire Protection of Buildings), Binalarda Enerji Performansı (BEP) Yönetmeliği (Energy Performance of Buildings Regulation) / TS 825 — the 2008 Isı Yalıtım Yönetmeliği (Thermal Insulation Regulation) is repealed, Gürültü Yönetmeliği (Noise Regulation), accessibility, TBDY 2018 (Turkish Building Earthquake Code) minimum geometry) and RF family (123-ФЗ, СП 2.13130, СП 29.13330, СП 59.13330, СП 118.13330, СП 50/51.13330) loaded 2026-10-30 from the official text; Al's own conventions (2026-10-30: floor/wall build-up order, structural vs finished level, ceiling height from FFL, modular sizes) in §3d. Says for each rule how the agent checks it in the live Revit model, what it does when a rule fails, and which items are engineer-only.
---

# wall-floor-code-check

What a wall or floor built or fixed by `Revit_WallFloor` has to satisfy,
and how the agent proves it — or says plainly that it can't. A **build-to +
report** rubric, not a certification: the agent never writes that a wall or
floor "complies with the code".

**All notes added to this skill must be written in English.**

The model-integrity rows (§3 M/F) need no standard and always run. Code rows
run only for a family that is loaded (§1); for any other family they are
NOT CHECKABLE with the measured value. **Never fill a figure from memory
or borrow one from another family or another skill.**

## 0. Project document first — don't add this skill's rules on top

Same rule as `stair-code-check` §0 / `door-window-code-check` §0 (Al,
2026-10-21): if the job has a Word document (ТЗ / specification), scan it with
`python -I .claude/agents/Revit_Roof/scripts/docx_standards.py <file.docx>`.

- **It names standards**: those are the basis; other families are not
  added. A ТЗ citing Russian norms (СП / пожарная безопасность, even as a
  general clause) → the **RF rows (§3c) are the figures for those cited
  standards**. Report header: `Basis: <file> — RF: <documents used>`.
- **No document, or it names no standards**: §1.

## 1. Basis — one code family per job

| Family | Documents | State |
|---|---|---|
| **TR** | Planlı Alanlar İmar Yönetmeliği (Planned Areas Zoning Regulation; RG 1/7/2026-33297); Binaların Yangından Korunması Hakkında Yönetmelik (Regulation on the Fire Protection of Buildings; CK 30/6/2025-10026); BEP Yönetmeliği (Energy Performance of Buildings Regulation) + TS 825; Binaların Gürültüye Karşı Korunması Hakkında Yönetmelik (Regulation on the Protection of Buildings against Noise); TBDY 2018 (Turkish Building Earthquake Code) | **Loaded 2026-10-30** from mevzuat.gov.tr (§3b, `references/tr-sources.md`). TS 825 U values, TS 500, TS 9111 / TS 12576 are paid TSE standards — **not loaded**. Turkish jobs without a document. |
| **RF** | 123-ФЗ tables 21/23 (ред. 04.08.2026); СП 2.13130.2020 (Изм. 1 + **Изм. 2**, in force 01.01.2026); СП 4.13130.2013; СП 29.13330.2011 (Изм. 1–4); СП 59.13330.2020 (Изм. 1–4); СП 118.13330.2022; СП 50.13330.2024; СП 51.13330.2011; СП 478.1325800.2019 (air terminals) | **Loaded 2026-10-30** from the code text (§3c, `references/rf-sources.md`; consolidated copies at consultant.ru, pravo.ppt.ru, meganorm.ru, tiflocentre.ru, base.garant.ru — not official МЧС/Минстрой copies: cross-check before a submission). Russian jobs and jobs whose ТЗ cites СП. |
| **Al** | Figures Al sends himself (2026-10-30: "bulduğunu al, ben de ek olarak göndereceğim" — "take what you find, I'll send more as well") | §3d — 2026-10-30 build-up / FFL / FCL conventions loaded; more to come; checked against the family's text, slips in §5 |
| US / UK | IBC / Approved Documents | **not loaded** |

- Never mix families in one job. Figures Al sends go in the **Al** row and
  §3d with his wording and date; where they differ from the official text
  the official text is shown next to them and Al decides (§5).

### Inputs the agent needs (ask only when a rule needs one)

| Input | Needed by | Note |
|---|---|---|
| **Building use** (TR: residential (konut) / commercial (ticaret) / office / public …; RF: Ф class) and **room use** (habitable, wet, corridor, office, hall) | heights, corridor widths, fire rows | Room names/numbers from `revit_list_rooms`; ask when a name doesn't say |
| **Building height** (TR: building height or structure height — the İmar definitions *bina yüksekliği* / *yapı yüksekliği* — for 21.50 / 30.50 m; RF: пожарно-техническая высота, СП 1.13130 definition) | TR-W1, TR-F1, RF-F2 | From levels; say which definition you used |
| **Fire-resistance degree** (RF I–V) and **С-class** (С0–С3); TR: sprinklers yes/no | RF fire rows, TR-F1 (Ek-3/C) | Not in the model — ask; record in the job notes. Аэровокзал: not decided yet |
| **Zone / plan** (TR: residential, commercial, mixed-use; plan-specific storey heights; air-navigation obstacle) | TR-H1, TR-H4 | From the user |
| **Number of people** on an escape route | TR-W1 | From the user or room occupancy |
| **Accessible route?** | TR-F2/F3, RF-F3/F6, RF-W10 | Public buildings: yes |
| **Temporary / seasonal building?** (RF) | СП 50 (thermal), СП 478 (terminal rows) | СП 50 excludes buildings used ≤ 2 heating seasons; СП 478 excludes seasonal ones. Аэровокзал is "non-capital quick-erect" — ask Al |
| Which walls are **fire walls / compartment / corridor / stair / shaft** walls | fire rows | Ask; never infer from a type name alone |

## 2. Status words (Turkish report)

Same as `stair-code-check` §2: **COMPLIANT** (UYGUN), **NON-COMPLIANT**
(UYGUN DEĞİL), **RECOMMENDATION** (ÖNERİ), **NOT CHECKABLE** (KONTROL
EDİLEMEDİ), **ENGINEER** (MÜHENDİS) — the Turkish label in brackets is the
one printed in a Turkish-language report. BLOCK rows stop a build before it
starts (give the failing and the compliant value, wait); FLAG rows are
built and reported prominently.

## 3. Model-integrity checks (no standard needed — always run)

Measured by `wall_floor_audit.py` (Revit_WallFloor/scripts) from the
live model; ids and values go into the report.

| ID | Rule | Check with | On fail |
|---|---|---|---|
| **M1 No duplicate / overlapping walls** | Two walls on one level don't share a line over any length | audit M1 (the bridge accepts duplicates silently) | new wall: **BLOCK**; existing: list, delete the duplicate with the user's yes |
| **M2 Joins closed** | Every wall end lands on another wall's centreline or is a deliberate free end; no gap/overrun of tol…0.5 m | audit M2 | new: fix the plan; existing: move the end, with yes |
| **M3 Tops tied to levels** | Top Constraint = the storey level above (Top Offset = − slab thickness for partitions under a slab), not Unconnected, unless a parapet/free-height wall is intended | audit M3 (`tie_to`, `top_offset_m`) | **FLAG**; fix = `set_parameter` Top Constraint `{id}` then Top Offset, with yes |
| **M4 Consistent heights** | Walls of one type on one level have the same top unless a step is intended (e.g. parapet side) | audit M4 | **FLAG**, ask |
| **M5 Right type** | Exterior outline in an exterior type, partitions in an interior type, no curtain type where a solid wall was meant; Location Line consistent per job | `query_where` Type / Location Line | **FLAG** |
| **M6 Room bounding** | Walls that separate rooms are Room Bounding = Yes; rooms stay placed and enclosed after a change (`revit_list_rooms` area > 0) | `query_where` Room Bounding, `list_rooms` | **FLAG**, fix with yes |
| **F1 Floor type is a floor** | No Foundation Slab family above the lowest level; omitted type never used | audit F1, `list_floor_types` familyName | new: **BLOCK**; existing: re-type with yes |
| **F2 Slab edge convention** | Slab edges follow one convention per job (centreline / inner face / outer face) and close to the exterior walls without gaps; slabs outside the outline are named (apron, canopy, external landing). **Base slab: outer face, no gaps (AL-6)** | audit F2 | base slab short of the outer face or a gap to an apron: **NON-COMPLIANT**; upper slabs: **FLAG**, ask which convention |
| **F3 No duplicate floors** | Floors on one level don't overlap unless a stepped/recessed slab is intended | audit F3 | new: **BLOCK**; existing: list |
| **F4 Level and offset** | Floor on the intended level, `Height Offset From Level` as planned (0 unless a step is intended) | read-back | fix before reporting |
| **F5 Storey clear height** | Level-to-level minus the upper slab = the clear height used by the code rows (H rows) | audit `storey_heights` | feeds the code rows |
| **F6 Walls stand on a slab** | Each storey's walls sit on a floor of that level (no wall over a void unless a façade over a canopy is intended) | floor bbox vs wall centrelines (audit F2 / bbox) | **FLAG** |

## 3b. TR rules — official text read 2026-10-30

Sources, verbatim quotes and URLs: `references/tr-sources.md` (İmar = Planlı
Alanlar İmar Yönetmeliği, last amended RG 1/7/2026-33297; Yangın = Binaların
Yangından Korunması Hakkında Yönetmelik, last CK 30/6/2025-10026; BEP =
Binalarda Enerji Performansı Yönetmeliği, RG 16/5/2026-33255; Gürültü =
Binaların Gürültüye Karşı Korunması Hakkında Yönetmelik, RG 31/5/2018-30437;
TBDY 2018 annex). HR re-checked 7 quotes in the downloaded official PDFs
(İmar 28(4), 29(3), 38(1), 39(2); Yangın 25(1), 27(1), 33(3), 62(2)).

**Heights** (measure: level-to-level minus the upper slab = audit
`storey_heights`; minus a ceiling's offset where one is modelled; room
`Unbounded Height` / `Limit Offset` as a cross-check)

| ID | Rule | Value | Source | Check | On fail |
|---|---|---|---|---|---|
| TR-H1 | Clear height of habitable storeys | ≥ 2.60 m (2.40 m where an air-navigation obstacle limits storeys) | İmar 28(4) | clear height per storey | **BLOCK** |
| TR-H2 | Wet areas, larders, corridors/passages, non-habitable basements, garages, boiler rooms | ≥ 2.20 m | İmar 28(5)(6) | per room type | **BLOCK** |
| TR-H3 | Mezzanine clear height | ≥ 2.40 m | İmar 4(1)(d) | | **BLOCK** |
| TR-H4 | Storey height, slab top to slab top — **maximum** unless the zoning plan sets more: residential 3.60 (4.00 if ≤ 3 storeys excl. basement); commercial ground 4.50 / with mezzanine 5.50 / others 4.00; mixed: ground 4.50/5.50, others 3.60 residential / 4.00 other | maxima | İmar 28(1) | level elevations | **FLAG** (needs zone; public, education, health, sports buildings: set by commission, 28(7) → NOT CHECKABLE) |
| TR-H5 | Escape-route corridor clear height | ≥ 2.10 m | Yangın 33(3) | | **BLOCK** |

**Walls**

| ID | Rule | Value | Source | Check | On fail |
|---|---|---|---|---|---|
| TR-W1 | Corridor clear width, between wall faces: dwelling hall/corridor ≥ 1.20; building entrance corridor to main stair/lift ≥ 2.20 public / 1.50 other; escape routes 50–500 people ≥ 1.00, 501–2000 ≥ 1.50, > 2000 ≥ 2.00, escape route also used as corridor ≥ 1.10, never < 0.80; high-rise ≥ 1.20; hospital ≥ 2.00 | see value | İmar 29(3), 30(1); Yangın 33(1)(2), 49(2) | centreline gap − ½ both thicknesses (audit centrelines) | new: **BLOCK**; existing: **FLAG** |
| TR-W2 | Party wall on a neighbouring plot boundary (attached or block building order — bitişik / blok nizam): no doors or windows | none | İmar 39(4) | hosted openings in that wall (`revit_get_doors`, windows Host Id) | **FLAG** → Revit_DoorWindow |
| TR-W3 | Fire wall between attached-order buildings | ≥ 90 min | Yangın 25(1) | wall type `Fire Rating` | **FLAG**; empty rating → NOT CHECKABLE |
| TR-W4 | Compartment walls (different uses in one building; boiler room, car park, main electrical, transformer, generator rooms) | REI 60, or Ek-3/C if greater | Yangın 4(tt), 24(2), Ek-3/B rows 6–7 | type `Fire Rating` | **FLAG** |
| TR-W5 | Escape-stair enclosure / fire lobby walls (doors 90 min smoke-tight, Revit_DoorWindow); walls between stair, emergency-lift shaft and lobby | REI 120; between them REI 60 | Yangın 38(3), 34(2), Ek-3/B 9a–9b | type `Fire Rating` | **FLAG** |
| TR-W6 | Shafts: lift shaft + machine room ≥ 60 min, non-combustible; protected shafts REI 120; high-rise service shafts ≥ 120 min; boiler room walls ≥ 120 min | see value | Yangın 62(2), Ek-3/B 8, 25(3), 54(2) | type `Fire Rating` | **FLAG** |
| TR-W7 | Spandrel: ≥ 1.00 m fire-resistant solid façade between unprotected openings of consecutive storeys (or a façade sprinkler line) | ≥ 1.00 m | Yangın 27(1) | (storey height − lower window head) + upper sill, per façade stack (windows via `revit_get_element_info`) | **FLAG** (curtain walls: slab-edge seal 27(3)(a) → ENGINEER) |
| TR-W8 | Load-bearing masonry minimum thickness (plaster excluded): cut stone 350, other units / confined / reinforced 240, reinforced panel 200 mm; parapet without a bond beam ≤ 4 × thickness | see value | TBDY 11.5.1 Table 11.4, 11.1.4, 11.5.12 | type width (core) of walls marked load-bearing masonry | **FLAG** + ENGINEER |
| TR-W9 | RC shear wall (perde) thickness ≥ max(storey height/16, 250 mm); 200 mm only under Eq. 7.14; tall buildings ≥ 300 mm | see value | TBDY 7.6.1.2–7.6.1.3, 13.1.6 | type width of Structural walls | **FLAG** + ENGINEER |

**Floors**

| ID | Rule | Value | Source | Check | On fail |
|---|---|---|---|---|---|
| TR-F1 | Floor fire resistance: every floor acts as a fire wall; 2-storey house upper floor REI 30; shop ↔ storey above REI 60 (or Ek-3/C); basement ↔ ground REI 90 (or Ek-3/C); others per Ek-3/C (apartments: basement > 10 m 90, < 10 m 60; above ground < 5 m 30, < 21.50 m 60, < 30.50 m 90, > 30.50 m 120) | see value | Yangın 26(1), Ek-3/B row 3, Ek-3/C | floor type `Fire Rating` if present | **FLAG**; empty → NOT CHECKABLE; other uses: read the Ek-3/C row in `references/tr-sources.md` |
| TR-F2 | No thresholds / level steps at doors (escape doors: none) | 0 | İmar 39(2); Yangın 47(1) | top-of-floor elevation on both sides of each door (floor level + `Height Offset From Level`) | **FLAG** |
| TR-F3 | Level changes: ramps by height climbed ≤ 15 cm 8 % · 16–50 cm 7 % · 51–100 cm 6 % · > 100 cm 5 %; handrails 0.90 + 0.70 m; escape routes: < 4 steps by ramp ≤ 10 % | see value | İmar 30(12)(13); Yangın 36(1)(b)(3), 44(1)(a) | rise / run of the sloped floor or ramp | **BLOCK** for a new step; sloped elements the tools can't build → hand off |
| TR-F4 | Guard ≥ 1.10 m, gaps ≤ 0.10 m at free floor edges (balconies, terraces, gallery voids, landings), gardens > 0.50 m above/below, window sills < 0.90 m | see value | İmar 38(1)(4) | slab edges outside the wall outline / voids (audit F2) with a drop | **FLAG** → railing: Revit_Stair (`revit_create_railing`); sills: Revit_DoorWindow |
| TR-F5 | Escape-corridor floor steps < 4 risers → ramp ≤ 10 %; fire-lobby floor slope to the exit ≤ 1/200 | see value | Yangın 36(1)(b)(3), 34(5) | | **FLAG** |
| TR-F6 | Slab minimums: ribbed (joist) slab top plate ≥ 70 mm; masonry-building slab ≥ 100 mm; precast topping ≥ 70 mm; solid slabs → TS 500 (not loaded) | see value | TBDY 7.11.2, 11.3.7, 8.6.2.6 | floor `Thickness` | **FLAG** + ENGINEER; solid slab → NOT CHECKABLE |
| TR-F7 | Floor finish slip-resistant, wheelchair-suitable; finish at least normal-flammable (high-rise: hardly-flammable); combustible insulation only under ≥ 2 cm screed | qualitative | İmar 30(8); Yangın 26(2)(3) | material names only | NOT CHECKABLE / ENGINEER |

**Engineer-only (listed, never passed)**: TS 825 U values (BEP 9(2); the
table is in the paid TS 825 — not loaded, ask Al), R ≥ 0.80 m²K/W between
independent units (BEP 9(5)), acoustic field values at class C (Gürültü
EK-3: e.g. dwelling ↔ dwelling DnT,A ≥ 52 dB, impact L'nT,w ≤ 54 dB; office
open plan 49 / private 52; plant → dwelling 58 / 48 — these are **field**
values, never compare a type's lab Rw to them), penetration seals, structure.

## 3c. RF rules — code text read 2026-10-30

Sources, verbatim quotes, URLs and editions: `references/rf-sources.md`.
Clause numbers are those of the amended texts. Fire-resistance rows depend
on the **degree and С-class** — without them they are NOT CHECKABLE
with the type's declared `Fire Rating`.

**Heights** (clear = floor to ceiling **including a suspended ceiling** — СП 118 4.26)

| ID | Rule | Value | Source | Check | On fail |
|---|---|---|---|---|---|
| RF-H1 | Clear height of rooms with permanent / mass occupancy (halls, waiting rooms) | ≥ 3.0 m | СП 118 4.26 | storey clear height − ceiling | **BLOCK** |
| RF-H2 | Reduced clear heights: administrative/office rooms ≥ 2.7; up to 20 % of area 2.6; corridors, visitor halls, unoccupied rooms ≥ 2.4; service corridors / ancillary ≥ 2.2 | see value | СП 118 4.27 | per room | **BLOCK** |
| RF-H3 | Mezzanines/intermediate levels only in rooms ≥ 4.7 m clear; ≥ 2.2 m under and over them | see value | СП 118 4.26 | | **BLOCK** |
| RF-H4 | Clear height along accessible routes | ≥ 2.1 m | СП 59 6.2.1 | | **BLOCK** |
| — | No minimum storey (floor-to-floor) height exists in СП 118 | — | НЕ НАЙДЕНО | | report only |

**Walls**

| ID | Rule | Value | Source | Check | On fail |
|---|---|---|---|---|---|
| RF-W1 | Element fire resistance by degree (I / II / III / IV; V not rated): load-bearing walls R 120 / 90 / 45 / 15 (**IV degree, 2 storeys: ≥ R 45**, СП 2 table 6.9 note 2); outer non-load-bearing walls E 30 / 15 / 15 / 15; stair-enclosure walls REI 120 / 90 / 60 / 45 | see value | 123-ФЗ table 21; СП 2 T6.9 прим. 2 | type `Fire Rating` vs the degree | **FLAG**; no degree → NOT CHECKABLE |
| RF-W2 | Fire barriers: type-1 wall REI 150, type-2 REI 45; type-1 partition EI 45, type-2 EI 15 (glazed > 25 %: EIW 45 / 15); openings ≤ 25 % of barrier area; windows in barriers non-opening; fire walls full height or to a type-1 fire floor | see value | 123-ФЗ table 23, ст. 88 ч. 5, 8, 9 | type `Fire Rating`; openings area in the wall | **FLAG** |
| RF-W3 | Type-1 fire wall above the roof: ≥ 0.60 m if any roof element is Г3/Г4, ≥ 0.30 m if Г1/Г2, 0 if all НГ (still cuts the roof); at the façade: cuts combustible façade materials, projects ≥ 0.3 m beyond them, E 60 / К0 strips totalling ≥ 1.5 m (public) | see value | СП 2 5.4.10; 5.4.11 (Изм. 2) | wall top vs roof (Revit_Roof); façade junction | **FLAG** |
| RF-W4 | Partitions of evacuation corridors/halls/vestibules, building < 28 m: I–III (R)EI(W) 30, IV 15, class К0 (≥ 28 m: 45); run **floor to slab**, also above suspended ceilings | see value | СП 2 5.2.7 (Изм. 2) | Top Constraint/Offset reaches the slab underside (audit M3); type `Fire Rating` | **FLAG**; not reaching the slab → **BLOCK** for new walls |
| RF-W5 | Fire-hazard rooms (except В4/Д; wet rooms, sanitary rooms, storerooms ≤ 10 m² exempt) and food blocks in Ф3.3: separated by type-1 fire partitions (I–III) / type-2 (IV) | see value | СП 4 5.5.7 → 5.1.2, 5.5.2 | room uses + enclosing wall types | **FLAG** |
| RF-W6 | Spandrel (I–III degree, façades with unrated openings): ≥ 1.2 m vertical (or projection + spandrel ≥ 1.2 m), width ≥ the opening below; one-storey buildings exempt; inside one multi-level terminal hall may be omitted (СП 478 9.3.2) | ≥ 1.2 m | СП 2 5.4.18 а), г) | (storey height − lower head) + upper sill per façade stack | **FLAG** (curtain walls → ENGINEER) |
| RF-W7 | Piers where rated internal walls/partitions meet the façade ≥ 0.8 m; type-2 fire wall / type-1 partition ≥ 1.0 m; stair enclosure to openings ≥ 1.2 m | see value | СП 2 5.4.18 б), 5.3.6 (Изм. 2), 5.4.16 д) | distance from the wall junction to the nearest window edge | **FLAG** → Revit_DoorWindow |
| RF-W8 | Ф3.3 in С1–С3: outer/inner walls, partitions and floors class К0, insulation НГ | К0 / НГ | СП 2 6.7.11 (Изм. 2) | material names only | NOT CHECKABLE / ENGINEER |
| RF-W9 | Terminal: baggage-handling zones enclosed ≥ EI 45 (openings EI 30); multi-level halls separated ≥ EI 45 | see value | СП 478 9.4.6, 9.4.7 | type `Fire Rating` | **FLAG** (only if СП 478 applies — not seasonal) |
| RF-W10 | Corridor clear width on accessible routes ≥ 1.8 m (1.5–1.2 m with 2 m passing pockets; ≥ 1.4 m by calculation); wall projections ≤ 0.1 m between 0.7 and 2.1 m | see value | СП 59 6.2.1 (Изм. 3), 6.2.6 | centreline gap − ½ both thicknesses | new: **BLOCK**; existing: **FLAG** |

**Floors**

| ID | Rule | Value | Source | Check | On fail |
|---|---|---|---|---|---|
| RF-F1 | Floor (перекрытие) fire resistance by degree: REI 60 / 45 / 45 / 15 (I–IV); fire floors type 1–4: REI 150 / 60 / 45 / 15 | see value | 123-ФЗ tables 21, 23 | floor type `Fire Rating` | **FLAG**; no degree → NOT CHECKABLE |
| RF-F2 | Building height / storeys vs degree and С-class (Ф3.3 → **table 6.9**): allowed height I С0 50, II С0 50, II С1 28, III С0 15, III С1 12, IV С0 9, IV С1 6, IV С2–С3 6, V 6 m; floor area per fire compartment at 2 storeys 5000 / 4000 / 3000 / 2000 / 1400 / 1400 / 1400 / 800 / 800 m² | see value | СП 2 6.7.1, table 6.9 | level elevations (пожарно-техническая высота per СП 1.13130), floor areas | **BLOCK** for a new storey/slab that breaks it |
| RF-F3 | No thresholds / level differences in doorways; where unavoidable ≤ 0.014 m | ≤ 0.014 m | СП 59 6.2.4 | floor tops on both sides of each door | **FLAG** |
| RF-F4 | Toilet/bathroom floor 15–20 mm below adjacent rooms, or a threshold ≤ 20 mm (same level allowed with full-area waterproofing); accessible doors still ≤ 0.014 m (RF-F3) | see value | СП 29 4.8 | `Height Offset From Level` of wet-room floors | **FLAG**; conflict with RF-F3 → report both, Al decides |
| RF-F5 | Wet-room floor slope 0.5–1 % (seamless/slab finishes) or 1–2 % (brick/concrete) toward drains | see value | СП 29 4.5 | sloped floors can't be built by the tools → NOT CHECKABLE unless modelled | report |
| RF-F6 | Level changes inside: stairs, ramps or lifts; indoor ramps ≤ 1:20 with a ≥ 1.5 m landing every 0.5 m of rise (as printed — confirm), absolute max 1:12.5 with table 5.1 flight lengths | see value | СП 59 6.2.8, 6.2.9, 5.1.14 | rise/run of ramps | **BLOCK** for a new step; ramps → hand off |
| RF-F7 | Guards: inside ≥ 0.9 m; ≥ 1.2 m where the floor drop > 1.0 m, flight gap > 0.3 m or children; external balconies, galleries, terraces, accessible roofs ≥ 1.2 m; continuous, ≥ 0.3 kN/m; porches > 0.45 m and ≥ 3 steps ≥ 0.9 m | see value | СП 118 6.10, 6.12 | free slab edges / voids with a drop (audit F2) | **FLAG** → railing: Revit_Stair |
| RF-F8 | Screed minimums: slope screed ≥ 20 mm on slabs, ≥ 40 mm on insulation; over pipes ≥ pipe Ø + 45 mm; floor on ground: concrete underlayer in public buildings ≥ 80 mm (≥ 120 mm without levelling screed), edge insulation strip ≥ 0.8 m | see value | СП 29 8.2, 9.4, 9.5, 9.13 | floor type layers when readable | **FLAG** / ENGINEER |
| RF-F9 | Slip resistance: public rooms ≥ 0.35 dry / 0.4 wet; outdoor routes 0.6–0.75 (≥ 0.4 wet); terminal main halls: hard stone or high-strength finish | see value | СП 29 5.25; СП 59 5.1.11; СП 478 8.5 | material names only | NOT CHECKABLE |

**Engineer-only (listed, never passed)**: thermal R0 (СП 50.13330.2024 —
walls a = 0.0003, b = 1.2 for category 2; roofs/floors from the table
points; needs ГСОП; not applicable to temporary buildings ≤ 2 heating
seasons), acoustics (СП 51 table 2 offices: floors Rw 45 / Lnw 63,
partitions Rw 45, between firms 48; no row for terminal halls; Al's 60/75
dBA figures are in `Russia_Aerovokzal/standards_ru.md`), structure,
penetration seals, К-class of systems.



## 3d. Al's figures

Each figure Al sends goes here with the date and his wording (full text in
`references/al-wall-floor-drawing.md`); where a loaded family's text says
otherwise, the text's value stands next to it and §5 records it. These are
**office conventions for any family** (RECOMMENDATION / build-to defaults), not code
rows — they never turn a code row to COMPLIANT.

**2026-10-30 — wall / floor / ceiling drawing conventions** (three texts; the
graphics part — line weights, hatches, floor finish plan, RCP, leaders —
went to `revit-sheet-audit` as WF1–WF8 for Revit_Drafter / Revit_Sheet).
The modelling part:

| ID | Convention | How Revit_WallFloor uses it | Check vs loaded families |
|---|---|---|---|
| AL-1 | **Floor build-up, top → bottom**: finish (e.g. 15 mm laminate, 10 mm porcelain) → adhesive/mortar 3–5 mm → levelling screed typically 30–50 mm → thermal/acoustic/water layer (DPC) → structural slab (e.g. 150 mm RC) → ceiling plaster or suspended ceiling | A floor type it creates or picks follows this order (finish layer on top, structure below). When the model has only a bare structural slab (Project1: single "Concrete 250mm"), report "finish layer not modelled" — never add finish layers without a yes | RF СП 29 8.2: screed on insulation ≥ **40 mm** — a 30 mm screed over the insulation layer fails RF-F8. TR: combustible insulation needs ≥ 2 cm screed (Yangın 26(3)) — compatible |
| AL-2 | **Structural vs finished level**: both are given (e.g. structural +2.690, finished +2.750 → 60 mm build-up); plans show FFL | Before building, state which one the Revit level is (FFL is the usual choice) and where the structural slab top sits (level − build-up); record it in the job notes and keep it for every storey. Audit F4 checks floors against that choice | — |
| AL-3 | **Ceiling height is given from the finished floor** (FCL, e.g. +2.60 / 260 cm) | Clear-height rows (TR-H*, RF-H*) use FFL → FCL when ceilings exist: read `OST_Ceilings` (`revit_query_where`, Level + Height Offset From Level); without ceilings, use the slab underside and say so | RF-H1 counts a suspended ceiling (СП 118 4.26); TR clear (internal) height likewise floor → ceiling |
| AL-4 | **Wall build-up, outside → inside**: cladding / external render → insulation → wall body (brick / aerated concrete / block) → internal plaster → paint/finish | An exterior wall type it picks has its layers in this order (exterior side out); a type whose exterior side faces in (flipped wall) is an M5 FLAG | — |
| AL-6 | **Base slab carries the whole wall** (Al, 2026-10-30, on Project1 screenshots: "tabanda boşluklar var … taban binaya göre küçük kalıyor" — "there are gaps in the base … the base comes out smaller than the building") — the ground-floor slab runs to the exterior walls' **outer face**; no gap under a panel or between the slab and an adjoining apron/landing slab | Audit F2 at the lowest storey: an edge at the centreline or inner face, or any gap to an adjoining slab, is **NON-COMPLIANT** (not a convention note); new base slabs are drawn to the outer faces | — |
| AL-7 | **Drywall partitions** (Al's third text; named basis IBC Chapter 25 / ASTM C840): light-steel C-stud / U-runner frame, gypsum boards 12.5 mm standard or 15 mm, fire-rated **Type X** where a rating is needed, mineral/glass wool in the cavity; partition types coded on plan with a legend (`W1` single board, `W2` double Type X acoustic …) | When it builds a partition, it picks a wall type whose name/layers state the board count, thickness and Type X if the wall is fire-rated (RF-W4/W5, TR-W4–W6); if the job has a W-code legend it uses the type with that `Type Mark` and reports the code; a new type or a `Type Mark` change needs Al's yes (type change = every instance). No stud/board model exists in the tools → stud size/spacing and fastening are **ENGINEER** | IBC ch. 25 / ASTM C840 / BS EN 13964 figures are **not loaded** (ASTM and EN are paid standards; IBC not researched yet) — only the values Al wrote are used, as conventions. Type X marks a fire-rated board; the **rating itself** still comes from the job's family (RF 123-ФЗ / СП 2, TR Yangın) |
| AL-8 | **Floor levels: FFL and SSL** — finished floor (FFL) and structural slab top (SSL) both recorded; example build-up 10 mm porcelain → adhesive → 40 mm screed → waterproofing → 150 mm RC | Extends AL-2: per job record whether the Revit level is FFL or SSL and the build-up between them; floors it builds keep that relation | 40 mm screed meets RF СП 29 8.2 (≥ 40 mm on insulation, ≥ 20 mm on a slab) |
| AL-9 | **Suspended ceilings** (named basis BS EN 13964): FCL from the finished floor; monolithic plasterboard (T-24, C-channel, hangers) or modular 60×60 / 60×120 T-grid | Ceilings are drawn by Revit_Guide (`revit_create_ceiling`); this agent reads them for FCL (AL-3) and hands a missing/low ceiling to Revit_Guide with the FCL the height rows allow | EN 13964 figures not loaded |
| AL-5 | **Modular dimensions**: wall thicknesses, openings, slab thicknesses on 100 / 300 mm modules | RECOMMENDATION when proposing new wall/slab thicknesses or wall positions; never overrides the user's figures | — |


## 4. How the agent uses this

1. **Before building:** basis (§0/§1) and the §1 inputs the request needs;
   M1/M2/F1/F3 on the planned elements with the audit; the BLOCK code rows
   the request decides (clear height, level steps, fire-wall continuity,
   minimum thickness of the chosen type). A BLOCK stops the build: give the
   failing and the compliant value and wait.
2. **Fixing:** audit → numbered defect list → the user picks → fix one
   class at a time → re-run the audit after each class.
3. **Report** short, at the end of the reply:

   ```
   Wall/floor check — basis: ТЗ — RF: СП 118.13330.2022 + СП 29.13330.2011 + 123-ФЗ
   | Rule | Measured | Status |
   | M1 No overlapping walls | 0 | COMPLIANT |
   | M3 Top tied to level | 21 walls Unconnected | NON-COMPLIANT → fixed (Top Constraint L2, −0.25) |
   | F2 Slab edge | L1 slab on the wall centreline | NOT CHECKABLE (no rule, project choice) |
   | RF-H1 Clear height L1 (hall) | 3.95 (ceiling not modelled) | COMPLIANT |
   | RF-F1 Floor REI | degree not given | NOT CHECKABLE |
   | Thermal / acoustic | — | ENGINEER |
   Handoff: Revit_DoorWindow — re-run G1–G6 for the 3 windows in wall 1658711.
   ```

   Only rows that apply. Never write "the walls comply with the code".
4. A wrong or outdated figure is fixed **here** (and noted in §5), not
   overridden in one job.

## 5. Corrections found while loading (2026-10-30)

What is commonly quoted → what the text says (full list with quotes in the
two reference files):

- **TR:** the 2008 *Binalarda Isı Yalıtım Yönetmeliği* (Regulation on
  Thermal Insulation in Buildings) is **repealed** (BEP
  28(1)) — cite BEP + TS 825. İmar 28(1) storey heights are **maximums**
  (top of slab to top of slab), the minimums are clear heights 2.60 / 2.40 /
  2.20 m. Guard 1.10 m with gaps ≤ 0.10 m; a 0.90 m sill is a trigger, not a
  guard height. 90 min is the attached-order fire wall; compartment walls
  are REI 60 (or Ek-3/C); 120 min is stair/lobby/shaft/boiler walls.
  Ordinary lift shafts 60 min. Spandrel 1.00 m. Noise limits are field
  DnT,A / L'nT,w, not lab Rw. TBDY shear wall ≥ max(h/16, 250 mm) (200 only under
  Eq. 7.14, 300 tall buildings); TBDY sets no solid-slab thickness (TS 500).
  Ramp slope is graded 8/7/6/5 % by rise, escape ramps ≤ 10 %.
- **RF:** Ф3.3 uses СП 2 **table 6.9** (not 6.10). IV degree at 2 storeys:
  load-bearing **≥ R 45**. Since Изм. 2 (01.01.2026) corridor partitions
  below 28 m are (R)EI(W) 30 (I–III) / 15 (IV), К0 — not "nothing below
  28 m". Fire wall above roof 60 / 30 / 0 cm by roof combustibility, not
  "always 60". The type-1 fire-wall façade rule was rewritten by Изм. 2
  (old 5.4.12 deleted). Spandrel 1.2 m only for I–III. Guards 0.45 m is a
  porch rule; inside 0.9 m, 1.2 m above a 1.0 m drop. Wet-room slope
  0.5–1 % or 1–2 % by finish. Bathroom 15–20 mm lower or threshold ≤ 20 mm.
  СП 29 flatness 5.18 deleted (2018). СП 50.2024 prints no a/b for public
  roofs/floors. Accessible corridor base width 1.8 m.
- **Al's 2026-10-30 drawing conventions (§3d):** screed "typically
  30–50 mm" — under RF a screed on an insulation layer must be ≥ 40 mm
  (СП 29 8.2); the sheet-layout line "per CSI UDS / NCS" belongs to the US
  family only (kept separate in `revit-sheet-audit`). Al named no source
  documents for his bracketed references. Third text: its UDS sheet codes
  (A-101 …) are US-family; the Аэровокзал ТЗ requires **ГОСТ Р 21.101-2020**
  for documentation, which governs that job. Its layer lines (0.25–0.35)
  are the in-section build-up lines, the second text's 0.35–0.50 are
  elements seen beyond the cut — both kept, different roles.
- **Uncertain, to confirm on an official copy:** СП 118 copy doesn't mark
  amended wording (4.26 / 4.27 / 6.12); СП 59 6.2.9 "landing every 0.5 m of
  rise" and table 5.1 lengths; СП 2 table 6.9 row V С-class; TR Ek-3/C cell
  alignment; TBDY Table 11.4 headers. HR re-checked 7 TR quotes in the
  official PDFs; the RF quotes were not re-checked by HR.

