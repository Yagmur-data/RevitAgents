---
name: revit-sheet-audit — output format
description: Exact report structure Revit_Sheet must produce — mirrors Arch_Reviewer's format (no author line, compact preamble that doubles as the scorecard, one merged defect table) so the two review agents stay consistent.
---

# Report format

No author/"Prepared by"/reviewer line anywhere. No section listing the
tooling/scripts used to produce the report. One file per PDF:
`ForRevitReview/reports/<pdf-stem>/<pdf-stem>.md`.

```markdown
# Prodim Revit Sheet Quality Control

**Date:** <YYYY-MM-DD>
**Basis applied:** <Default (TS EN ISO 128) | Project-specific: <name>, mechanics per <family>>
**Sources:** <pdf file name(s) only — no directory paths>

## Reviewed sheets

| Sheet | Score | Status |
|---|---|---|
| A-101 — Zemin Kat Planı | 96 | APPROVED — RELEASE |
| A-102 — 1. Kat Planı | 68 | REVISE & RESUBMIT |
| A-400 — Kesitler | 100 | APPROVED — RELEASE — no issues detected |

## Defect table

| Sheet | Location | Category / R-code | Observed issue | Remediation | Severity | Drafter response |
|---|---|---|---|---|---|---|
| A-102 | Mutfak, 1. Kat Planı | Tagging / R5 | Mutfak kapısı etiketlenmemiş, kapı cetvelinde aynı tip başka yerlerde etiketli | Kapıyı `revit_tag_element` ile etiketle | CRITICAL | |
```

Rules:
- A clean sheet gets one line in "Reviewed sheets" (score + status + "no
  issues detected") and **no row** in the defect table — never silently
  skip a sheet.
- One merged defect table for every sheet in the job, not one table per
  sheet.
- "Drafter response" column is left blank by Revit_Sheet — Revit_Drafter
  (or the user) fills it in to confirm the fix or record an objection.
- Score and status per sheet (scoring formula: `../SKILL.md` §3) appear in
  "Reviewed sheets" — that list IS the scorecard, there is no separate
  executive-summary section.
- Cite the category name and R-code (`recurring-issues-checklist.md`) in
  every defect row, plus the specific reference file section if it adds
  precision (e.g. "ISO 7200, see sheet-sizes-and-title-blocks.md §2") —
  never cite a document's file path, only the standard's own name.
