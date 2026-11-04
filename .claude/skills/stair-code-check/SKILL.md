---
name: stair-code-check
description: Stair code rules the Revit_Stair agent builds to and reports against — riser height, tread depth, uniformity, step formula (2R+G) and pitch, rise between landings, clear width by occupant load, landing depth, headroom, handrail height/both sides/grip/extensions, intermediate handrails, guard height and openings, landings (every job: top/bottom/intermediate — size, door swing, level surface, headroom, open edges; §3c), open risers, exterior walking surface, industrial access; plus the Blondel design method (target riser 170, 2R+G 630) used to size every stair. Two code families as supplied by Al on 2026-10-21 — US (IBC/IRC + NFPA 101, default) and UK (BS 5395-1 / Approved Document K) — plus Neufert ergonomics as advisory only; and an RF family (СП 1.13130.2020, from the code text) for Russian jobs. Says for each rule how the agent checks it in the live Revit model, what it does when a rule fails, and which items are engineer-only.
---

# stair-code-check

What a stair built by `Revit_Stair` has to satisfy, and how the agent proves
it — or says plainly that it can't. This is a **build-to + report** rubric,
not a certification: the agent never states that a stair "complies with the
code"; it reports which checked rules pass, which fail, and which it could
not check.

## 0. Project document first — don't add this skill's rules on top

If the project comes with a Word document (ТЗ / şartname / technical
specification, `.docx`), scan it first:
`python -I .claude/agents/Revit_Roof/scripts/docx_standards.py <file.docx>`.

- **The document names standards** (`has_standards: true`): **those are the
  basis. Do not add this skill's US/UK rules (§3) or the Neufert advisory
  rows.** When the document cites Russian norms (СП / пожарная безопасность,
  even as a general clause), the RF rules (§3b) are the figures for those
  cited standards and **are** applied (Al, 2026-10-21).
  Check only what the document itself requires with figures, or figures the
  user supplies for the standards it cites; everything else is KONTROL
  EDİLEMEDİ — name the cited standard and ask for its figure. Plain
  measurements (riser, tread, width, riser count) are still reported,
  without a pass/fail status.
  Report header: `Basis: <document file name> — <cited standards>`.
- **No document, or it names no standards**: use §1.

(Same rule as `roof-code-check` §0 — Al, 2026-10-21: "eğer verilen word
dosyasında zaten standartlar varsa ekleme".)

## 1. Basis — one code family per job

Source: the stair summary Al pasted on 2026-10-21 (IBC, NFPA 101, BS,
Neufert). Its citation markers had no source list, so figures are **as
supplied, not independently verified**, except cells marked *HR* (added or
corrected by HR from the named clause — verify the edition in use). §5 lists
what was corrected and why.

| Family | Documents | Use |
|---|---|---|
| **US (default)** | IBC 2021 ch. 10 (§1011 stairways, §1014 handrails, §1015 guards), IRC R311.7 for dwellings, NFPA 101 §7.2.2 | Default when no project document and the user names nothing else — **including Turkish projects** (confirmed by Al, 2026-10-21). Report header `US — IBC/IRC + NFPA 101 (supplied 2026-10-21)`. Where IBC and NFPA 101 differ, the stricter value is listed. |
| **UK** | BS 5395-1, Approved Document K (England) | Only when the user/project says UK/BS. Header `UK — BS 5395-1 / ADK (supplied 2026-10-21)`. |
| **Neufert (advisory)** | Neufert, Bauentwurfslehre; Blondel step formula | **Not a code.** Ergonomic rows added to every job that has no project document, status ÖNERİ, never BLOCK. |
| **RF** | СП 1.13130.2020 «Эвакуационные пути и выходы» (Приказ МЧС № 194, ред. 16.06.2025, Изм. 1–3) + 123-ФЗ | Russian jobs, and jobs whose ТЗ cites СП / пожарная безопасность generally (§0 — these are then the "figures for the cited standards"). Rules in §3b, quoted from the code text (sudact.ru, read 2026-10-21) — not from a summary. Header `RF — СП 1.13130.2020 (ред. 16.06.2025)`. |
| **TR — not loaded** | Binaların Yangından Korunması Hakkında Yönetmelik, Planlı Alanlar İmar Yönetmeliği, TS 9111 (erişilebilirlik) | None of their figures are here yet. On a Turkish-basis job: say so, report measurements, ask Al for the values — **never fill a TR check with a US/UK number.** |

- Never mix US and UK figures in one job. Neufert rows are labelled
  advisory so they never read as a code requirement.
- Don't ask which family applies: use US unless the user or the project
  names UK, TR or another code. Record the family in the report header.
- Convert inches exactly (1 in = 25.4 mm) and compare at 0.1 mm: US max
  riser is **177.8 mm**, so a Revit type limit of 178 mm is not enough proof.

### Stair use — ask it when not stated

| Use | US | UK |
|---|---|---|
| **Konut içi** (inside one dwelling unit) | IRC R311.7 / IBC 1011.5.2 exception 3 (R-3, R-2 within units) | ADK "private stair" |
| **Genel / kamusal** (common, public, commercial) | IBC 1011 / NFPA 101 new stairs | ADK "general access stair" |
| **Kaçış merdiveni** (required exit stair) | Same as genel; plus enclosure/fire items S15 | ADK general access + ADB items (S15) |
| **Dış mekân** (exterior steps/stair) | Code limits of its use (genel or konut içi) + S18; landscape comfort rows N7 | same |
| **Endüstriyel ekipman erişimi** | Supplied 230 / 255 mm "NFPA 101" — **not verified** (see §5); FLAG only. OSHA 1910.25 is the usual US reference — not loaded | — |

Width (S6) also needs the **occupant load** the stair serves — ask for it
(or "50 kişiden az mı?") when the use is genel/kaçış.

## 2. Status words (Turkish report)

| Status | Meaning | Agent behaviour |
|---|---|---|
| **UYGUN** | Checked in the model, meets the value | report |
| **UYGUN DEĞİL** | Checked in the model, fails | BLOCK rules: stop before building, tell the user, offer the compliant value; FLAG rules: build, report prominently |
| **ÖNERİ** | Neufert ergonomic row outside the comfort range | report, never blocks |
| **KONTROL EDİLEMEDİ** | No figure for this family, or needs data the model/tools don't have | report what is missing |
| **MÜHENDİS** | Structural/fire-engineering item, out of the agent's scope | list it so it isn't forgotten; never mark it passed |

## 3. Rules

Values in mm unless noted. `—` = no figure for that family → KONTROL
EDİLEMEDİ.

| ID | Rule | US (IBC/IRC + NFPA 101) | UK (BS / ADK) | Check with | On fail |
|---|---|---|---|---|---|
| **S1 Riser height** | Konut içi | max **196.9** (7¾ in) *HR: IRC R311.7.5.1 / IBC 1011.5.2 exc. 3* | max **220** | Before: `stair_run.py` riser. After: instance `Actual Riser Height`. | **BLOCK** |
| | Genel / kaçış | min **101.6** (4 in), max **177.8** (7 in) | max **170** *HR: ADK table 1.1 general access, min 150* | same | **BLOCK** |
| **S2 Tread depth (going)** | Konut içi | min **254** (10 in) *HR, same clauses as S1* | min **220** | Before: tread sent. After: `Actual Tread Depth`. | **BLOCK** |
| | Genel / kaçış | min **279.4** (11 in) | min **250** *HR: ADK table 1.1* | same | **BLOCK** |
| **S3 Uniformity** | Max difference | adjacent risers/treads **4.8** (3/16 in, NFPA 101 7.2.2.3.6); largest − smallest in a flight **9.5** (3/8 in, IBC 1011.5.4) | — | `stair_run.py` gives equal risers; after: `Actual Number of Risers` × `Actual Riser Height` = floor-to-floor ± 1 mm (per-riser values are not exposed by the API). | **FLAG** (fix it — agent rule 7) |
| **S4 Step formula** | 2R + G | — (no US rule) | **550 – 700** *HR: ADK 1.5* | `stair_run.py --step-min/--step-max`; after: from read-back R and G. | UK: **BLOCK** |
| **S5 Rise between landings** | Max vertical rise of one flight | **3658** (12 ft, IBC 1011.8) | max **16** risers per flight *HR: ADK 1.14 for general access/utility; verify for private* | `stair_run.py --max-flight-rise` / `--max-risers-per-flight`; after: each stair element's height. | **BLOCK** (offer the landing split) |
| **S6 Clear width** | Konut içi | min **914** (36 in, IRC R311.7.1) | — (supplied 800–900 "local", source unknown → not used) | Type `Minimum Run Width` / actual run width. Clear width between handrails isn't readable — state that the run width includes handrails if they project. | **BLOCK** if the run width you will build is below it |
| | Genel / kaçış | occupant load **< 50: min 914** (36 in); **≥ 50: min 1118** (44 in) (IBC 1011.2); larger loads: per-occupant egress width calc → MÜHENDİS | — | same + occupant load from the user | **BLOCK** |
| **S7 Landing** | Width; depth in the direction of travel | width ≥ stair width; depth ≥ stair width, **need not exceed 1219** (48 in) on a straight run (IBC 1011.6) *HR: corrected, see §5* | width and depth ≥ stair width *HR: ADK 1.15* | `--landing-depth` / landing outline from `stair_run.py`; after: the Floor stand-in's outline. | **BLOCK** |
| **S8 Headroom** | Clear height above the nosing line / landing | min **2032** (80 in, IBC 1011.3) | min **2000** | Section view + bottoms of floors/beams above the run (`revit_get_element_info` elevations); no ray-cast tool. | **FLAG**; not measurable → KONTROL EDİLEMEDİ |
| **S9 Handrail height** | Above the nosing line | **864 – 965** (34–38 in, IBC 1014.2) | **900 – 1000** | Railing type height (`revit_get_element_info` on the type). A free-standing railing is not a stair handrail. | **FLAG** (agent can't add a hosted handrail) |
| **S10 Handrail sides** | Both sides | both sides, except konut içi (one side allowed) (IBC 1014.1) | — | Railings on/along each side of the stair. | **FLAG** |
| **S11 Intermediate handrail** | Wide stairs | every part of the required width within **762** (30 in) of a handrail → needed when width > **1524** (60 in) (IBC 1014.9) *HR: supplied "1.40 / 1.80 m" replaced, see §5* | width > **1800** → divide into flights ≥ 1000 wide | Run width. | **FLAG** |
| **S12 Handrail grip & clearance** | Circular Ø; wall gap | Ø **32 – 51** (1¼–2 in); ≥ **38** (1½ in) to the wall (IBC 1014.3.1, 1014.8) | — | Railing type parameters if exposed; else KONTROL EDİLEMEDİ. | **FLAG** |
| **S13 Handrail extensions** | Top / bottom | top: horizontal ≥ **305** (12 in) beyond the top riser; bottom: continue sloping one **tread depth** beyond the bottom riser (IBC 1014.6) *HR: corrected, see §5* | — | Not modeled by the agent's railing tool → normally KONTROL EDİLEMEDİ. | **FLAG** |
| **S14 Guard** | Height at landings/open sides; openings | height ≥ **1067** (42 in, IBC 1015.3); konut içi ≥ **914** (36 in, IRC R312.1.2); openings: a **102** (4 in) sphere must not pass (IBC 1015.4) — on open sides of the stair itself **111** (4⅜ in) *HR* | — | Railing type height and baluster spacing if exposed. | **FLAG** |
| **S15 Escape stair** | Enclosure, fire rating, travel distance, materials | — | — | Only when the stair is a required exit stair. | **MÜHENDİS** / KONTROL EDİLEMEDİ |
| **S16 Structure** | Loads, stringer/slab design | — | — | — | **MÜHENDİS** always |
| **S17 Open risers** | Allowed or not | not permitted on genel/kaçış and accessible stairs (IBC 1011.5.5.3, ADA 504.3); konut içi allowed if a **102** (4 in) sphere can't pass the opening | — | Run type ("Run Type" on the stair type → its riser setting / type name, e.g. "No Riser", "open"). | genel/kaçış: **BLOCK** before build; konut içi: FLAG (opening size) |
| **S18 Exterior walking surface** | Tread/landing slope; water | slope **≤ 2 %** (1:48) in any direction (IBC 1011.7.1); outdoor treads/landings must not let water accumulate (drainage by design) | — | Not modeled (treads are flat in Revit) → KONTROL EDİLEMEDİ; say how water is to be shed. | KONTROL EDİLEMEDİ |
| **S19 Industrial equipment access** | Riser / tread | supplied: max **230** riser, min **255** tread — **citation not verified** | — | as S1/S2 | **FLAG** only, until Al confirms the source |

## 3b. RF rules — СП 1.13130.2020 (evacuation stairs)

Researched by HR from the code text (sudact.ru, Приказ МЧС № 194 ред.
16.06.2025) at Al's request, 2026-10-21. Clause numbers are the code's.
All dimensions are **clear ("в свету", 4.1.4)** — width between walls /
handrail faces, not the Revit run width if handrails project. Geometric
tolerance 5 % (4.1.5) — used only to report, never to pass a value that
fails the stated minimum.

Inputs to ask: **functional fire-hazard class** (Ф1.1 … Ф5; airport
terminal / station = **Ф3.3**), **people on any floor above the first**
(≤ 200 / > 200 / > 600), building height, whether children may be present.

| ID | Rule (clause) | Value | Check with | On fail |
|---|---|---|---|---|
| **RF1 Width** (4.4.1) | Clear width of the evacuation path on the stair ≥ the required width of any exit onto it, and ≥: | **1.35 m** — Ф1.1, Ф2.1, Ф2.2, Ф3.4, Ф4.1, any building with > 200 people on a floor above the first, public buildings > 50 m · **1.6 m** — > 600 people on a floor above the first · **1.2 m** — all other buildings except Ф1.4, Ф5 (and Ф1.3 > 75 m) · **1.05 m** — Ф1.3 < 75 m · **0.7 m** — stairs to single workplaces / ≤ 5 people · **0.9 m** — all other cases | Run width (type `Minimum Run Width` / instance run width) minus handrail projection. **Ф3.3 ≤ 200 people → 1.2 m** (case "в"; HR reading: "е" covers what "в" excludes, e.g. Ф1.4, Ф5). | **BLOCK** |
| **RF2 Headroom** (4.4.1, 4.4.9) | Clear height of the stair evacuation path; nothing protruding from walls below it | ≥ **2.2 m** above treads and landings | Section view; bottom of the slab/beam above each flight (`revit_get_element_info` elevations). | **FLAG**; not measurable → KONTROL EDİLEMEDİ |
| **RF3 Landings** (4.4.2) | Landing width; landing in front of swing-door lifts; intermediate landing in a straight flight; doors | width ≥ flight width; at swing-door lifts ≥ flight width + ½ lift door, and ≥ **1.6 m**; intermediate landing in a straight flight length ≥ **1.0 m**; open doors must not reduce the required landing/flight width | `stair_run.py --landing-depth`; landing outline (Floor stand-in) vs. run width. | **BLOCK** |
| **RF4 Slope, tread, riser** (4.4.3) | As a rule | slope ≤ **1:1** (45°); tread ≥ **250 mm** (not for external stairs); riser **50 – 220 mm**. Exceptions: open stairs to single workplaces up to 2:1; curved stairs tread ≥ 220 mm in the narrow part; stairs to technical floors/attics/non-used roofs or service rooms ≤ 5 workplaces tread ≥ 120 mm | `stair_run.py --max-riser 0.22 --min-riser 0.05 --min-tread 0.25 --pitch-max 45`; after: read-back values. | **BLOCK** |
| **RF5 Risers per flight** (4.4.4) | Between landings (not curved stairs) | **3 – 16**; up to **18** in single-flight stairs and in one flight of a two-/three-flight stair within the first floor | `--max-risers-per-flight 16` (18 where allowed); after: `Actual Number of Risers` per flight. | **BLOCK** |
| **RF6 Uniformity, no winders** (4.3.6) | On evacuation paths | no curved stairs, winders, or steps of different tread or riser within the stair / stair cell (exceptions: service rooms ≤ 5 people, curved main stairs per 4.4; flights to technical floors/roof) | Equal risers from `stair_run.py`; read-back R × n = height; RF flights in one stair must share R and G. | **BLOCK** before build; read-back mismatch → FLAG + fix |
| **RF7 Guards & handrails** (4.3.5) | | stair rise > **0.45 m** → guards with handrails; flight width > **1.5 m** → handrails both sides; ≥ **2.4 m** → intermediate handrails; where children may be present and the gap between flights ≥ **0.3 m**, or at drops ≥ 1 m → guard height ≥ **1.2 m** (other guard heights are not set by СП 1.13130 → KONTROL EDİLEMEDİ) | Railings along the stair; gap between U-flights from `stair_run.py --gap`. | **FLAG** (agent can't add a hosted handrail) |
| **RF8 Merged flights** (4.4.5) | Where several flights join into one | joint flight width ≥ sum of the joined widths | Only when the layout merges flights. | **BLOCK** |
| **RF9 Stair cell & fire items** (4.4.6 – 4.4.23) | Door self-closers, stair-cell type (Л1/Л2/Н1-Н3), daylight openings ≥ 1.2 m², exit to outside, no equipment/lifts/pipes in the cell, smoke protection (СП 7.13130) | — | Not modeled by the agent. | **MÜHENDİS** / KONTROL EDİLEMEDİ |
| **RF10 Structure / fire rating** | Fire resistance of flights and landings (123-ФЗ, by fire-resistance degree) | — | — | **MÜHENDİS** |
| **RF11 External open stair, 3rd type** (4.4.7) | Evacuation stair outside the building without a stair cell | non-combustible (except degree V buildings); placed, as a rule, at blind wall parts of class ≥ K1 and ≥ REI(EI) 30; **landings at the level of the evacuation exits; guards ≥ 1.2 m**; every point of the stair's ground projection ≥ **1 m** from the projection of any window opening (glazed wall parts allowed if ≥ EIW 30). As the only exit: only from technical rooms ≤ 300 m², ≤ 2nd floor and ≤ 9 m, ≤ 5 people — otherwise stair cells are required | Landing Floor at each exit door's level; guard type height; plan distance from the stair's footprint to window bboxes on that façade. | Landing/guard: **BLOCK** before build, FLAG after; window distance < 1 m: **FLAG**; materials/REI: MÜHENDİS |

RF has no step formula (2R+G) and no pitch comfort rule: under RF, size with
the §4 design method but report N-rows only when no project document applies
(§0).

## 3c. Landings (sahanlıklar) — checked on every stair job

Al, 2026-10-30: "ara sahanlık meselesi önemli". Landings are not an extra:
every stair job plans and checks the **bottom and top floor landings** and
every **intermediate landing**, in the job's family. These rows gather what
§3 / §3b say about landings and add the landing-only rules from Al's
landing paste (2026-10-30; corrections in §5). Measure depth from the run's
nosing line (agent lesson: the top riser sits 32 mm behind it).

| ID | Rule | US (IBC/IRC + NFPA 101) | UK (BS / ADK) | RF (СП 1.13130.2020) | Check with | On fail |
|---|---|---|---|---|---|---|
| **LD1 Where** | A landing is required | at the **top and bottom of every stair** (IBC 1011.6) *HR*; between flights when the rise reaches **3658** (S5) | top and bottom of every flight *HR: ADK 1.15, verify*; between flights after **16** risers (S5) | between flights after **16** risers (18 in the RF5 cases); landings at every exit level of an external 3rd-type stair (RF11) | `stair_run.py` flight split; `floor_landing_zones` for top/bottom | **BLOCK** |
| **LD2 Size** | Width across, depth along the walk | width ≥ stair width; depth ≥ stair width, **need not exceed 1219** on a straight run (IBC 1011.6) | width and depth ≥ stair width *HR* | width ≥ flight width; straight-flight intermediate landing ≥ **1.0 m** long; at swing-door lifts ≥ flight + ½ door and ≥ **1.6 m** (4.4.2) | `--landing-depth`, `--floor-landing-depth`, `--width`; after: landing Floor bbox vs. run width (`Actual Run Width`) | **BLOCK** |
| **LD3 Door swing** | Doors opening onto a landing | during the swing ≥ **½** of the required landing width stays clear; fully open, the leaf projects ≤ **178** (7 in) into it (IBC 1005.7.1) *HR* | a door swinging across a bottom landing leaves ≥ **400** clear across the full flight width *HR: ADK 1.16, verify* | an open door must not reduce the required landing or flight width (4.4.2) | Doors whose bbox touches a landing or `floor_landing_zones` outline (`revit_get_doors`: host, swing, hand, width); swing arc = leaf width around the hinge jamb | **BLOCK** before build; on an existing stair FLAG + hand the door to Revit_DoorWindow |
| **LD4 Level surface** | Slope, steps in the landing | ≤ **2 %** (1:48) in any direction — every landing, not only outdoors (IBC 1011.7.1) | level; ground landing ≤ **1:60** *HR: ADK 1.15, verify* | no split landings (разрезные площадки) on evacuation paths (4.3.6) | Landing Floor `Slope` empty/0 and its top = landing level exactly; one Floor per landing | **FLAG** |
| **LD5 Headroom** | Clear height above the landing | ≥ **2032** (S8) | ≥ **2000** (S8) | ≥ **2200** (RF2) | Bottom of the slab/beam above the landing − landing level | **FLAG**; not measurable → KONTROL EDİLEMEDİ |
| **LD6 Open edges** | Guard on a landing edge with a drop | guard where the drop > **762** (30 in, IBC 1015.2) *HR*; height per S14 | per S14 *HR* | stair rise > 0.45 m → guards with handrails; children + gap ≥ 0.3 m or drop ≥ 1 m → ≥ **1.2 m** (4.3.5); external 3rd type ≥ **1.2 m** (4.4.7) | Free-standing railing along each open landing edge (agent lesson: keep the path ≥ 50 mm inside the slab edge) | **FLAG** |
| **LD7 Rest landing (comfort)** | Break long climbs | ÖNERİ: a landing every **12–14** risers (supplied; see §5) | same | same | `stair_run.py --advise-risers-per-flight 14` | ÖNERİ |
| **LD8 Landing in the model** | The landing really carries the walk | Floor stand-in top = landing level (± 1 mm); edge on the run's nosing line, no gap to either run; outline ≥ LD2; the report says "Floor stand-in, not a stair landing"; supports/structure | — | — | Landing Floor bbox vs. run bboxes; level/offset parameters | gap/level mismatch: **FLAG** + fix; structure: **MÜHENDİS** |

### Neufert ergonomics (advisory rows, status ÖNERİ)

| ID | Rule | Value | Check with |
|---|---|---|---|
| **N1 Step formula** | 2R + G | **600 – 660** (Blondel; ideal **620 – 630**, average adult step 610–640) | `stair_run.py` step value |
| **N2 Optimum ratio** | R / G | **170 / 290** | riser and tread |
| **N3 Pitch** | Climbing angle | **30° – 37°** comfortable, ideal **30° – 35°** | `stair_run.py` pitch |
| **N4 Pitch max** | Konut içi | ≤ **42°** — in the UK family this is a code limit (ADK private stair) → **BLOCK** there, ÖNERİ elsewhere | same |
| **N5 Risers per flight** | Comfort | ≤ **18** | riser count per flight |
| **N6 Design riser** | Target riser to start from | **160 – 175** | `--target-riser` (§4 step 1) |
| **N7 Exterior steps** | Landscape comfort | 2R + G = **660** (26 in); riser **100 – 175**; tread **300 – 450** | `stair_run.py --blondel 0.66` for exterior steps |

## 4. How the agent uses this

0. **Size the stair (design method, supplied 2026-10-21):** H = finished
   floor to finished floor → n = round(H / target riser 170) → r = H / n
   (more risers if r exceeds the family's max) → g = 630 − 2r (660 for
   exterior steps), raised to the code minimum tread if below → pitch
   = atan(r / g). `stair_run.py --target-riser 0.17 --blondel 0.63
   --max-riser … --min-tread …` does exactly this (worked example: H 2750 →
   16 × 171.9, g 286, 31.0°). Use a fixed `--tread` only when the user
   gives one.
1. **Before building:** decide the basis (§0/§1), the use and (genel/kaçış)
   the occupant load; run S1, S2, S4, S5, S6, S7, S17 (and S19 for
   industrial) and N1–N7 on the numbers from `stair_run.py`. A BLOCK result
   stops the build: tell the user the failing value and the compliant one,
   one question, wait.
2. **After building and verifying (agent rule 7):** re-run S1–S5 on the
   read-back values, then S8–S14 and S18 where they apply.
2a. **Landings (§3c) before and after, every job:** before building, run
   LD1–LD3 and LD7 on the `stair_run.py` landings and `floor_landing_zones`
   (walls, door swings, other stairs inside a zone = fail); after building,
   LD2, LD4–LD6 and LD8 on the model. The report table always has an LD
   block, one line per landing ("Alt kat sahanlığı L1", "Ara sahanlık
   +2.100", "Üst kat sahanlığı L2").
3. **Report** at the end of the reply, short:

   ```
   Yönetmelik kontrolü — esas: US — IBC/IRC + NFPA 101 (supplied 2026-10-21), kullanım: genel, < 50 kişi
   | Kural | Ölçülen | Durum |
   | S1 Rıht 101.6–177.8 | 175.0 | UYGUN |
   | S2 Basamak ≥ 279.4 | 275 | UYGUN DEĞİL |
   | S5 Kol yüksekliği ≤ 3658 | 2100 | UYGUN |
   | S6 Genişlik ≥ 914 | 1000 | UYGUN |
   | S9–S10 Küpeşte | modellenmedi | KONTROL EDİLEMEDİ |
   | N1 2R+G 600–660 (öneri) | 625 | UYGUN |
   | S15–S16 | — | MÜHENDİS |
   ```

   Only rules that apply; MÜHENDİS rows grouped on one line. Never write a
   summary like "merdiven yönetmeliğe uygun".
4. If a rule's figure turns out wrong or outdated, fix it **here** (and say
   so in the agent's activity log) — don't override it ad hoc in one job.

## 5. Corrections to the supplied text (2026-10-21)

Recorded so a later session doesn't "fix" them back to the pasted wording:

- **Landing depth** — pasted "minimum 48 in (1220 mm) on straight runs".
  IBC 1011.6: depth ≥ the stair width, **but need not exceed 48 in** on a
  straight run — 48 in is a cap, not a minimum.
- **Handrail extensions** — pasted "12 in horizontal at start and end".
  IBC 1014.6: 12 in horizontal at the **top** only; at the **bottom** the
  rail continues sloping for one tread depth.
- **Dwelling riser** — pasted "max 7.75 – 8.25 in". Current IRC/IBC dwelling
  limit is **7¾ in / tread 10 in**; 8¼ in / 9 in are older or local-amendment
  figures and are not used.
- **Uniformity** — the 3/16 in adjacent-step tolerance is NFPA 101
  7.2.2.3.6; the 3/8 in whole-flight tolerance is IBC 1011.5.4. Both kept,
  attributed separately.
- **Central handrail threshold** — pasted "1.40 m or 1.80 m". 1.80 m is the
  UK figure (ADK); 1.40 m has no identified source and is not used; the US
  rule is the 30 in reach (→ > 60 in / 1524 mm).
- **Guard height** — pasted "36–42 in". 42 in is the general IBC value; 36 in
  applies only within dwellings (IRC). Split by use.
- Not used (no identifiable source): residential width "800–900 mm local",
  "1000–1100 mm for high-capacity buildings".

Second paste (2026-10-21, design method + extra uses):

- **Exterior tread slope** — pasted "a 2 % (1/4 in per 12 in) front-to-back
  slope must be given". IBC 1011.7.1 makes 2 % (1:48) a **maximum** slope of
  treads and landings in any direction; shedding water is required, a 2 %
  fall is not. Encoded as "≤ 2 %" (S18).
- **Industrial equipment access 230 / 255 mm "NFPA 101"** — not found in
  NFPA 101's stair table (new 7 in / 11 in, existing 8 in / 9 in); NFPA 101
  points industrial equipment access to §40.2.5.3, whose figures were not
  verified. Kept as S19 with FLAG only; OSHA 1910.25 is the usual US
  reference for industrial stairs.
- **Exterior figures** (2R+G = 660, riser 100–175, tread 300–450) are
  landscape comfort guidance, not code → advisory N7; exterior stairs still
  meet their use's code limits.
- "AGS" in the dwelling row has no identified document; the dwelling figures
  stay as in S1/S2.

Landing paste (2026-10-30, intermediate landings):

- **"A landing every 12–14 risers (≈ 1.5 m rise)"** — the two halves don't
  agree (12 × 170 mm ≈ 2.0 m, 1.5 m ≈ 9 risers). Kept as the riser count only,
  advisory (LD7); the 1.5 m figure is not used. The binding limits stay
  S5 / RF5.
- **Door swing "must not dangerously narrow the landing"** — replaced by the
  measurable rules: US IBC 1005.7.1 (½ width during the swing, ≤ 7 in fully
  open), UK ADK 400 mm, RF 4.4.2 (no reduction of the required width).
- **"Landings may slope up to 2 % for drainage"** — IBC 1011.7.1's 2 % is a
  maximum for every stair walking surface (all landings), not a drainage
  allowance for outdoor landings only.
- **Headroom 2030 mm** — IBC 1011.3 is 80 in = **2032 mm**; used as 2032.
- **Landing at top and bottom of every stair** (IBC 1011.6) and **guards at
  landing drops > 30 in** (IBC 1015.2) were not in the paste; added by HR
  because a landing check without them is incomplete.
- "Metric Handbook" is a UK design guide, not a code; "AGS" is still
  unidentified — neither is used as a basis.
- RF11 (external 3rd-type stairs, СП 1.13130.2020 4.4.7) added from the code
  text read on 2026-10-21 — Revit_Stair's 2026-10-26 log asked for it.
