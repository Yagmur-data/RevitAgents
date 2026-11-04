---
name: roof-code-check
description: Roof code rules the Revit_Roof agent builds to and reports against — minimum drainage slope (1/4:12), steep/low-slope split (3:12), covering-specific minimum slopes, parapet height (30 in / 762 mm), external fire classification (ASTM E108 / UL 790 Class A/B/C), smoke/heat vents, primary + overflow drainage, vapour control, wind uplift, structural loads, rooftop structures and green roofs (ANSI/SPRI VF-1), plus a building-type module for airport terminals and hangars (OLS height limit, NFPA 415/409, ASCE 7). Basis is the IBC / US standards family as supplied by Al on 2026-10-21. Says for each rule whether the agent can check it in the live Revit model, what it does when a rule fails, and which items are engineer-only.
---

# roof-code-check

All notes added to this skill must be written in English.

What a roof built by `Revit_Roof` has to satisfy, and how the agent proves it
— or says plainly that it can't. This is a **build-to + report** rubric, not
a certification: the agent never states that a roof "complies with the code";
it reports which checked rules pass, which fail, and which it could not check.

## 0. Project document first — don't add this skill's rules on top

If the project comes with a Word document (ТЗ / specification / technical
specification, `.docx`), scan it first:
`python -I .claude/agents/Revit_Roof/scripts/docx_standards.py <file.docx>`.

- **The document names standards** (`has_standards: true` — a specific code
  such as СП 478.1325800.2019 / TS EN … / ГОСТ …, or a general "comply with
  СП, ГОСТ, СНиП…" / "the relevant regulations" clause): **those are the basis.
  Do not add this skill's rules (§3) or its building-type modules (§5).**
  Check only what the document itself requires with figures, or figures the
  user supplies for the standards it cites; everything else is
  NOT CHECKABLE — name the cited standard and ask for its figure, never
  fill it from §3. Plain measurements (slope, parapet height, roof top
  elevation) may still be reported, without a pass/fail status.
  Report header: `Basis: <document file name> — <cited standards>`.
- **No document, or it names no standards** (`has_standards: false`): use
  §1 below.

(Al, 2026-10-21: "if the Word file you are given already contains standards,
don't add [these]".)

## 1. Basis — one standard family per job

- **Supplied basis (default): IBC + the US test standards it references**
  (ASTM E108 / UL 790, ASTM D7158, ASTM E1592, ANSI/SPRI VF-1). Source: the
  rule summary Al pasted on 2026-10-21. Its citation markers had no source
  list, so the figures are **as supplied, not independently verified** except
  where §3 says "added by HR". Reports name the basis as
  `IBC (supplied 2026-10-21)`.
- **TS / EN family — not loaded.** Turkish projects are normally governed by
  the Regulation on the Fire Protection of Buildings (Binaların Yangından
  Korunması Hakkında Yönetmelik), TS EN 13501-5
  (external roof fire performance, classes B_ROOF(t1)…(t4)), TS 825
  (thermal insulation) and TS EN 1991-1-3/-4 (snow/wind). None of their
  figures are in this skill yet. If the job is on that basis, say so, run
  only the geometry checks that are basis-independent (R1 "is there any
  drainage slope at all", R4 parapet *height measured*), and ask Al for the
  values — **never fill a TS/EN check with an IBC number.**
- **Never cross-map classes**: ASTM E108 Class A is not "equal to"
  B_ROOF(t1) (different test methods). Report whatever the roof type
  declares in its own family's terms.
- Ask once at job start which basis applies if the project's location or
  client isn't clear from the conversation; record it in the report header
  and use it for every roof in the job.

## 2. Status words

Reports are written in the user's language; these English status words are
the canonical names.

| Status | Meaning | Agent behaviour |
|---|---|---|
| **COMPLIANT** | Checked in the model, meets the value | report |
| **NON-COMPLIANT** | Checked in the model, fails | BLOCK rules: stop before building, tell the user, offer the compliant value; FLAG rules: build, report prominently |
| **NOT CHECKABLE** | Needs data the model/tools don't have | report what is missing |
| **ENGINEER** | Engineering/product-approval item, out of the agent's scope | list it so it isn't forgotten; never mark it passed |

## 3. Rules

Slopes in degrees, because `revit_create_roof` takes degrees:
1/4:12 = 2.08 % = **1.19°** · 2:12 = 16.7 % = **9.46°** · 2.5:12 = 20.8 % =
**11.77°** · 3:12 = 25 % = **14.04°** · 4:12 = 33.3 % = **18.43°**.

| ID | Rule (supplied basis) | Check with | On fail |
|---|---|---|---|
| **R1 Min. drainage slope** | Low-slope roofs: design slope ≥ 1/4:12 (≈2 %) for positive drainage, no ponding. | `edgeSlopesDeg` you are about to send; after build read the roof's slope parameters. | Sloped edge < 1.19° → **BLOCK** (offer 1.19°). A **flat (0°) roof** is allowed only as the Revit convention where the falls come from tapered insulation: build it if asked, report R1 as **NOT CHECKABLE — falls not modeled** and offer a 1.19° shed/hip alternative. |
| **R2 Slope class** | ≥ 3:12 (14.04°) = steep-slope; below = low-slope. | Same slopes. | Informational: decides whether R3-tile/shingle or R6 drainage rules apply. |
| **R3 Covering minimum** | *Added by HR from IBC 1507, verify the edition in use:* asphalt shingles ≥ 2:12 (9.46°), double underlayment from 2:12 up to 4:12; clay/concrete tile ≥ 2.5:12 (11.77°), double underlayment up to 4:12; membranes (built-up, modified bitumen, single-ply) ≥ 1/4:12. | Roof **type name/material** (e.g. "Asphalt Shingle", "EPDM", "Tile") vs. slope. Unknown covering → NOT CHECKABLE. | Below minimum → **BLOCK**. In the underlayment band → FLAG "double underlayment required". |
| **R4 Parapet** | Where a parapet is required at exterior/fire walls, min. 30 in (**762 mm**) above the roof surface; fire-wall continuity through the roof. | Walls under/around the roof edge: top elevation (level + top offset or unconnected height) minus roof surface elevation at that edge. Whether a parapet is *required* depends on fire separation/wall rating — ask, or report as NOT CHECKABLE. | Measured parapet < 762 mm where required → **FLAG** (walls are Revit_Guide's job; don't edit them). |
| **R5 External fire class** | Roof covering/system tested and classified per ASTM E108 / UL 790: Class A (severe exposure, highest), B or C. Required class depends on construction type — not in the supplied text. | Roof **type** parameter "Fire Rating" (or the project's own class parameter) via `revit_get_parameter`. | Empty → **NOT CHECKABLE — class not defined**. Value present → report it; whether it is *enough* is ENGINEER unless the user states the required class. |
| **R6 Primary + overflow drainage** | Low-slope roofs: primary drains **and** secondary/emergency overflow (drains or scuppers). | Look for roof-drain elements on/near the roof (e.g. `revit_find_elements` in plumbing categories, name containing drain / süzgeç (Turkish for "drain", as it appears in element names) / scupper). | None found on a low-slope roof → **FLAG — drainage not modeled** (the agent cannot place them). |
| **R7 Smoke/heat vents** | Certain large industrial/commercial buildings: roof vents, supplied ratio **≥ 1 % of floor area** (supplied figure; applicability and ratio depend on occupancy and code edition). | Compute roof footprint area × 1 % = indicative vent area. | Only when the user says the building is industrial/commercial/large: report the indicative area, status ENGINEER. Vents are not modeled by this agent. |
| **R8 Vapour control & ventilation** | Warm/cold roof build-up with a vapour barrier and, for cold roofs, ventilation, to prevent condensation. | Roof type layers, if `revit_get_element_info` on the type returns them: look for a membrane / vapour-retarder layer. | No identifiable layer → **FLAG**; layers not readable → NOT CHECKABLE. |
| **R9 Wind uplift** | Covering attachment designed for the site's basic wind speed (ASTM D7158 shingles, ASTM E1592 metal panels, etc.). | — | **ENGINEER** always. |
| **R10 Structural loads** | Dead, snow, wind and live (maintenance/equipment) loads carried safely. | — | **ENGINEER** always. |
| **R11 Rooftop structures** | Penthouses, equipment screens, lift overruns: height limits, fire rating, area limits. | Only if such elements are on the roof. | **ENGINEER**; list them. |
| **R12 Green roofs** | Root barrier + drainage/filter layer over the waterproofing, extra structural load, fire per ANSI/SPRI VF-1. | Only when the user asks for a green roof (or the type name says so); check the type's layers as in R8. | Missing layers → FLAG; loads/fire → ENGINEER. |

## 4. How the agent uses this

1. **Before building:** decide the basis (§1); run R1, R2, R3 on the slopes
   and roof type you are about to send. A BLOCK result stops the build: tell
   the user the failing value and the compliant one, one question, wait.
2. **After building and verifying (agent rule 6):** run R4–R8 against the
   live model; add R7, R11, R12 only when they apply.
3. **Report** at the end of the reply, short:

   ```
   Code check — basis: IBC (supplied 2026-10-21)
   | Rule | Measured | Status |
   | R1 Min. slope ≥ 1.19° | 30° | COMPLIANT |
   | R3 Covering (Asphalt Shingle ≥ 9.46°) | 30° | COMPLIANT |
   | R4 Parapet ≥ 762 mm | no parapet, whether required is unknown | NOT CHECKABLE |
   | R5 Fire class | "Fire Rating" empty | NOT CHECKABLE |
   | R9–R10 Wind / loads | — | ENGINEER |
   ```

   Only rules that apply; ENGINEER rows grouped on one line. Never write a
   summary like "the roof complies with the code".
4. If a rule's figure turns out wrong or outdated, fix it **here** (and say
   so in the agent's activity log) — don't override it ad hoc in one job.

## 5. Building-type modules

Extra rules that apply only to certain building types. Load the module
when the building type matches and add its rows to the same report table.

| Building type | Module | Adds |
|---|---|---|
| Airport **terminal** or aircraft **hangar** | `references/airport-terminal-hangar.md` | A1 OLS height limit (can BLOCK a build), A2 Class A requirement, NFPA 415/409, ASCE 7 wind and edge systems, acoustics, smoke control, lightning, closed drainage + bird hazard (A1–A9). |
