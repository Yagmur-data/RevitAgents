---
name: Revit_Sheet scripts index
description: Index of scripts written by/for the Revit_Sheet agent — what each does and when to reach for it. Check this (and the revit-sheet-audit skill, once installed) before writing a new script.
---

# Revit_Sheet — scripts index

| Script | Purpose | Reuse when... |
|---|---|---|
| pdf_render.py | Render PDF pages to PNG, crop by page fractions (`--crop`), dump line widths/fonts (PyMuPDF) | Every review: first look + zoomed screenshots |
| write_md_rf_batch.py | One-off generator of the 7 per-sheet .md files for the 2026-11-04 Aerovokzal RF review | Template for a re-review of the same set (edit rows inline) |

## Rule
Before writing a new script: read this table and the `revit-sheet-audit`
skill's own script library, if that skill has been installed. Reuse or
extend an existing one when it already covers the need. Only add a new
file when nothing existing does, and add its row here in the same turn you
write it.
