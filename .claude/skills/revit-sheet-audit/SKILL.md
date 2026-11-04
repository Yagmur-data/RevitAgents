---
name: revit-sheet-audit
description: "The authoritative Revit sheet-layout (paftalama) graphics-QA rubric — concrete values from ISO 128/TS EN ISO 128 (Turkish default), BS EN ISO 128, and US NCS/AIA for line weights & types; ISO 5457/7200 for sheet sizes & title blocks; ISO 129 for dimensioning; ISO 3098 for lettering; ISO 7519 plus north-arrow/scale-bar/revision-cloud convention for drawing arrangement & symbols; ISO 19650/BS 1192 or US NCS for drawing numbering; the RF family (ГОСТ / СПДС: ГОСТ Р 21.101 stamp, axes, elevation marks, ГОСТ 2.301/2.303/2.304) replacing those on Russian jobs (2026-10-30); plus Al's office module for walls, drywall partitions, floors, finishes and ceilings on sections, details, floor finish plans and reflected ceiling plans (WF1-WF10, 2026-10-30). Used by Revit_Sheet (scoring/reporting) and Revit_Drafter (drafting to the yardstick before export) as the real rubric, replacing their inline baseline checklist."
---

# revit-sheet-audit

All notes added to this skill must be written in English.

A Revit sheet audit checks the **graphics and presentation** of a sheet
(pafta) against concrete, named drafting standards — not a vague "looks fine"
judgement, and not a country-independent set of non-binding examples (that
approach is `arch-graphics-review`'s; this skill deliberately keeps the
real standard families separate instead, because the user wants the actual
figures enforced).

## 1. Which standard family governs — ask, record, apply consistently

Ask whether a project-specific standard applies, same intake pattern as
`arch-graphics-review`. If none is stated:

- **Default: TS EN ISO 128** (Turkish Standard, TSE's identical adoption of
  ISO 128 — mandatory on official Turkish architectural/engineering
  projects). Use this unless told otherwise.
- **BS EN ISO 128** — same line-weight/type values as TS EN ISO 128/ISO
  128, paired with BS 1192/ISO 19650 drawing numbering. Use for UK/
  Commonwealth-governed projects.
- **US National CAD Standard (NCS) / AIA CAD Layer Guidelines** — different
  pen-weight and layer-naming vocabulary, same underlying visual-hierarchy
  requirement. Use for US/North-American-client projects.
- **RF — ГОСТ / СПДС (Russian jobs; added 2026-10-30).** For any building
  in the Russian Federation / a Russian-client ТЗ, `references/russia-gost-spds.md`
  **replaces** the ISO sheet/title-block/numbering/dimension/lettering rows
  (families are not blended): СПДС stamp Form 3, ГОСТ 2.301 formats and
  frame, ГОСТ 2.303 lines, ГОСТ 2.304 lettering, ГОСТ Р 21.101 axes and
  elevation marks, марка/шифр numbering, Russian-language sheets. Record the
  edition (ТЗ names ГОСТ Р 21.101-2020; 2026 edition in force from
  01.04.2026 — ask).
- A client's own CAD/BIM manual, when given, supplies project-specific
  specifics (units, sheet-code format, symbol/legend conventions) layered
  on top of whichever family's mechanics apply.

Record the basis in the report header exactly as
`references/audit-output-format.md` specifies, and apply it to **every**
sheet in the job — a mixed basis within one set is itself a defect.

## 2. Review categories (six + the wall/floor/ceiling module)

1. **Sheet metadata & title block** — `references/sheet-sizes-and-title-blocks.md` §§1-2 (ISO 216/5457/7200): frame/margins correct, title block in the right place for the sheet size, every required field filled and consistent.
2. **Drawing numbering** — `references/sheet-sizes-and-title-blocks.md` §3 (ISO 19650/BS 1192 or US NCS, per the basis chosen in §1): sheet numbers follow the agreed scheme consistently across the set.
3. **Line weight & line-type hierarchy** — `references/line-weights-and-types.md`: at least 3 distinct weights, ≥2:1 thick:thin ratio, correct type-to-meaning mapping (solid/dashed/chain-dot).
4. **Dimensioning** — `references/dimensioning-and-lettering.md` §1 (ISO 129): closed chains, no duplicate dimensioning, out-of-scale values underlined, auxiliary values parenthesised.
5. **Lettering & legibility** — `references/dimensioning-and-lettering.md` §2 (ISO 3098): nominal heights used consistently per text role, consistent orientation.
6. **Drawing arrangement & symbols** — `references/symbols-and-drawing-arrangement.md` (ISO 7519, north arrow, scale bar, revision marking): logical sheet-set order, north arrow/scale bar present and correct, revision clouds properly tagged and not stale.
7. **Wall / floor / ceiling graphics** (sections, details, floor finish plans, RCPs only) — `references/wall-floor-ceiling-graphics.md` (Al's office convention, 2026-10-30, layered on the chosen family): cut-element line hierarchy, material hatches, build-up leaders, FFL/FCL and structural levels, floor finish legend, RCP content, modular chains, grid bubbles, drywall partitions and type codes, legend/keynotes (WF1-WF10).

**On an RF job** categories 1-6 are scored against the RF-S/RF-L/RF-D/RF-N
rows of `references/russia-gost-spds.md` §1 (its §2 says how each ISO
reference file is replaced); category 7 (WF) applies unchanged.

Run the **R1-R12 recurring-defect sweep** (`references/recurring-issues-checklist.md`)
on every sheet in addition to the categories — these are the failures
most likely to recur, so a miss here is treated as more serious than a
category-level miss.

## 3. Scoring

Start at 100, deduct a fixed penalty per defect by severity — **CRITICAL
−20, WARNING −8, ADVISORY −2** — floor at 0. Map to a release band:
**90-100 APPROVED — RELEASE; 75-89 APPROVED WITH MINOR COMMENTS; 60-74
REVISE & RESUBMIT; 0-59 REJECTED.** Apply the **CRITICAL hard cap**: any
CRITICAL defect caps the band at REVISE & RESUBMIT regardless of the
numeric score (still show the computed score). This is the same formula
`Arch_Reviewer` uses — kept identical on purpose so `Revit_Drafter`'s "> 90"
exit criterion means the same thing it does for `C3D_Drafter`.

## 4. Report format

Exact structure: `references/audit-output-format.md`. No author line, no
tooling listed, the per-sheet score/status list IS the scorecard, one
merged defect table with a "Drafter response" column.

## 5. Graphics only

This skill audits presentation, not design adequacy (room sizes, code
compliance, structural design). A design concern gets one ADVISORY note
and nothing more — don't expand the audit into a design review.

## 6. How the two agents use this

- **Revit_Sheet** (`.claude/agents/Revit_Sheet.md`) loads this skill to
  score and report — it never edits anything.
- **Revit_Drafter** (`.claude/agents/Revit_Drafter.md`) loads it to
  self-check every sheet against §§2-3 *before* the first export, so the
  first Revit_Sheet submission already scores well, then implements every
  defect Revit_Sheet reports until the sheet clears the exit criterion.

## Sources

Figures and field lists in the reference files are a working synthesis of
publicly described standard content (ISO 128/128-20/128-24, TS EN ISO 128 /
TS 88-20/24, BS EN ISO 128, ISO 5457, ISO 7200, ISO 129-1, ISO 3098-1,
ISO 7519, ISO 19650/BS 1192, US NCS/AIA CAD Layer Guidelines; RF family:
ГОСТ Р 21.101-2020, ГОСТ 2.301/2.302/2.303/2.304, ГОСТ 21.1101-2013), not a
verbatim reproduction of any paid standard document. Treat them as the
working rubric for this workspace; if a formal copy of a cited standard
disagrees on a specific figure, the paid standard document governs and this
file should be corrected to match.
