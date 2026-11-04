---
name: revit-sheet-audit — RF family (ГОСТ / СПДС) for Russian jobs
description: The sheet-layout family for buildings in the Russian Federation — СПДС (ГОСТ Р 21.101, ГОСТ 21.501) plus ЕСКД sheet/line/lettering standards (ГОСТ 2.301 / 2.302 / 2.303 / 2.304). Replaces the TS EN ISO 128 default on Russian jobs. Loaded 2026-10-30 from Al's paste, checked against web copies of the code text; §5 records what the paste got wrong and what could not be verified.
---

# RF family — ГОСТ / СПДС sheet layout (Russian jobs)

**When it applies.** Any job whose client/ТЗ is Russian (first job: Аэровокзал
Северное, `Russia_Aerovokzal/`, whose ТЗ names ГОСТ Р 21.101-2020). On such a
job this family **replaces** the TS EN ISO 128 / ISO 5457 / ISO 7200 / ISO 129 /
ISO 3098 / ISO 19650 rows of the other reference files — families are not
blended. What stays: the R-checklist idea, the scoring (SKILL.md §3), the
report format, and Al's wall/floor/ceiling graphics module (WF1–WF10), which
is an office convention laid on top of any family.

**Edition — ask, record.** ГОСТ Р 21.101-2020 took effect 01.01.2021 and
replaced ГОСТ Р 21.1101-2013. Per stroyinf.ru / Kontur it **lost force on
01.04.2026**, replaced by **ГОСТ Р 21.101-2026** (order of Росстандарт
12.02.2026 № 129-ст per Kontur's note). The 2026 text and any transition
rule could **not** be read (§5). The Аэровокзал ТЗ names the 2020 edition, so
**score against 2020 when the ТЗ/contract names it** and say so in the report
header; ask Al whether the client expects 2026. Header line:
`Basis: RF — ГОСТ Р 21.101-2020 (per ТЗ) + ГОСТ 2.301/2.303/2.304 [+ Al office convention — WF]`.

## 1. Rows (RF-S = sheet, RF-L = lines/lettering, RF-D = dimensions/marks, RF-N = set structure)

Severities are defaults; Revit_Sheet may raise/lower with a stated reason.
"PDF check" = what Revit_Sheet can see; "Build" = what Revit_Drafter does.

| # | Rule (source) | PDF check | Build in Revit | Default |
|---|---|---|---|---|
| RF-S1 | **Stamp (основная надпись) in the bottom-right corner; on A4 along the short side.** Main-set sheets and the graphic part of design documentation use **Форма 3** (ГОСТ Р 21.101-2020 5.2.1–5.2.2, Приложение Ж) | Stamp present, bottom-right, structured as Form 3 (graphs 1–13, 25–27 below) | Needs a loaded title-block family drawn as Form 3. The bridge cannot create or edit .rfa (`revit_list_families` to see what is loaded) → if none is loaded, stop and ask Al for the family | CRITICAL if missing/not a ГОСТ stamp |
| RF-S2 | **Stamp fields.** Graph 1 designation (шифр); 2 enterprise; 3 building name; 4 names of the images ("Общие данные" on the general-data sheet); 6 **stage — П / Р / И**; 7 sheet number (omitted on a single-sheet document); 8 total sheets (**first sheet only**); 9 organisation; 10–13 role / surname / signature / date; 25 scale; 26 format; 27 customer. **Разработал and Нормоконтроль are mandatory**; ГИП (ГАП) signs the general-data sheet and the most significant sheets | Every graph filled and consistent (stage letter, sheet n of N, scale matches the image) | `revit_set_parameter` on the sheet; titleblock parameters must exist in the family | CRITICAL: designation / stage / sheet no. blank or contradicting; WARNING: other graph empty |
| RF-S3 | **Designation (шифр) = base code + "-" + марка**, e.g. `2345-12-АР` (4.1.2, 4.2.4); a set may split `АР1; АР2; КЖ1…` (4.2.3); `2345-12-ЭО.1` form allowed (4.2.5) | Pattern consistent across the whole set | Sheet number / designation parameter | WARNING |
| RF-S4 | **Frame and margins:** frame 20 mm on the left (binding), 5 mm on the other three sides; outer frame and stamp outline thick solid, inner stamp lines thin solid (ГОСТ 2.301-68; ГОСТ Р 21.101 5.2.5) | Margins and weights as stated | In the titleblock family (not editable here) | WARNING |
| RF-S5 | **Formats:** A0 841×1189, A1 594×841, A2 420×594, A3 297×420, A4 210×297 (A4 vertical only); extended formats = short side × integer (A2×3 594×1261, A3×3 420×891, A4×3 297×630) (ГОСТ 2.301-68) | Sheet size is one of these | Sheet size comes from the titleblock family | WARNING; ADVISORY for an extended format without need |
| RF-S6 | **Language: Russian** for all drawing text, stamp and notes (client = RF). Abbreviations per ГОСТ 2.316 / ГОСТ Р 21.101 Таблица Е.1 (5.1.11) | No English/Turkish leftovers (family names, "SITE", "NOTES" from a template) | Text notes / tag families / sheet names in Russian | WARNING |
| RF-L1 | **Lines (ГОСТ 2.303-68):** basic line s = 0.5–1.4 mm by image size and complexity; **thin lines s/3 … s/2**; the same line type keeps the same thickness on all images at one scale. Types: сплошная толстая (visible/section outlines), сплошная тонкая (dimension, extension, hatch, leaders), штриховая (hidden), **штрихпунктирная тонкая (axes, centre lines)**, разомкнутая (section lines), волнистая / с изломами (breaks). In building sections, visible contours beyond the cut plane **may** be thin | Cut > visible > thin hierarchy; axes dash-dot thin; same type = same weight | `revit_set_view_display_style` / view templates; object styles are not editable through the bridge → report, do not promise | WARNING |
| RF-L2 | **Lettering (ГОСТ 2.304-81):** heights 2.5, 3.5, 5, 7, 10, 14, 20, 28, 40 mm (1.8 only type B, not recommended); **Type A d = h/14, Type B d = h/10, both sloped 75°** (≈ 15° off vertical — same thing as the paste's "15° slanted"); tolerance ±0.5 mm. **Axis, mark and name letters 1.5–2× the size of the dimension figures** (ГОСТ 21.1101-2013 5.4.7) | One type and one slope across the set; heights from the series; axis letters larger than dimension text | Text-note / tag types (not editable here) | ADVISORY (R10-style) |
| RF-D1 | **Coordination axes (ГОСТ Р 21.101-2020 5.3):** thin dash-dot with **long dashes**; circles Ø 6–12 mm; digits on the side with **more** axes, left → right; letters bottom → top; marks mainly on the **left and bottom** sides, repeated top/right where the axes differ; **no gaps**; after the letters run out use doubled letters АА, ББ, ВВ; additional axes as fractions. **Cyrillic letters NOT used: Ё, З, Й, О, Х, Ц, Ч, Щ, Ъ, Ы, Ь.** Latin only if needed, excluding I and O | Bubble Ø, letters, no gaps, no forbidden letter, bubbles on left and bottom | Grid names are text; bubble side via grid end-bubble visibility; heads/extents by `revit_set_grid_vertical_extents` (elevations only) | CRITICAL: a forbidden letter or a gap; WARNING: bubbles on wrong sides |
| RF-D2 | **Elevation marks (5.4.3):** metres, **3 decimals, comma as separator, no unit symbol**; **zero is written without a sign** (`0.000`), `+` above, `−` below; zero level = usually finished floor of the first storey; on sections and facades the mark sits on an extension/contour line as thin 45° strokes 2–4 mm; **on plans the figure is in a rectangle** | Format of every mark; zero without ±; rectangles on plans | Spot-elevation family / format (not editable here) | WARNING |
| RF-D3 | **Dimensions:** in **mm without unit**; master plans, external networks and transport: metres to 2 decimals (5.4.1) | No "mm" suffixes; unit consistent per sheet | Project units + dimension style | WARNING |
| RF-D4 | **Scales (ГОСТ 2.302-68):** 1:1; 1:2; 1:2.5; 1:4; 1:5; 1:10; 1:15; 1:20; 1:25; 1:40; **1:50; 1:75; 1:100; 1:200; 1:400; 1:500**; 1:800; 1:1000; large site plans also 1:2000 … 1:50000. Scale in stamp graph 25; images get a scale only where the product/СПДС standard requires it (5.1.6 + ГОСТ 2.316) | Every view's scale is in the series; stamp scale = principal view | `revit_place_view_on_sheet` scale / view scale | WARNING |
| RF-N1 | **Set structure:** each main set has a марка (АР, КР, КЖ, ОВ, ВК, ЭО … — full table Г.1 not read) and starts with **«Общие данные»**: ведомость рабочих чертежей основного комплекта (Форма 1), ведомость ссылочных и прилагаемых документов (Форма 2), общие указания (clauses numbered straight through), условные обозначения (4.3.1–4.3.5) | Sheet 1 of the set is the general-data sheet; its list matches the actual sheets | A schedule can carry the list; the sheet list comes from `revit_list_sheets` | WARNING |

## 2. How the other reference files change on an RF job

- `sheet-sizes-and-title-blocks.md` (ISO 5457/7200, ISO 19650, NCS numbering): **not applied.** RF-S1–S5 replace §§1–3. Do not score the numbering against ISO 19650 or UDS.
- `line-weights-and-types.md`: ISO series 0.13 … 2.0 and the scale tables are **not** the RF rule; use RF-L1. (ГОСТ s 0.5–1.4 mm is a range, not a 1:√2 series.)
- `dimensioning-and-lettering.md`: ISO 129 / ISO 3098 rows give way to RF-D3 / RF-L2.
- `symbols-and-drawing-arrangement.md`: north arrow / scale bar / revision cloud still apply as good practice (ГОСТ Р 21.101 has its own change-table, graphs 14–19 of the stamp — a revision row there replaces the ISO revision block).
- `recurring-issues-checklist.md`: R1–R12 are run with the RF row as the "standard basis" (R1 → RF-S2, R2 → RF-L1, R4/R5/R6 unchanged, R7 → RF-S4, R8 → stamp graphs 14–19, R9 → RF-D3, R10 → RF-L2, R11 → north arrow only, R12 unchanged).
- `wall-floor-ceiling-graphics.md` (WF1–WF10): applies as before; its UDS sheet codes (`A-101` …) are **not** used on Russian sheets.

## 3. Revit specifics for this family

- **Title block.** The Form 3 stamp is a title-block family. The bridge has no family-editing tool, so Revit_Drafter checks `revit_list_families` (titleblocks) and reports if no ГОСТ stamp is loaded rather than faking one with text notes. The first job's family comes from Al.
- **Cyrillic.** Grid names, sheet names and text notes are plain text in Revit, so Cyrillic is expected; confirm on the first Russian sheet that a Cyrillic name round-trips through `revit_create_sheet` / `revit_set_parameter` before relying on it (not yet tested).
- **Axes in the Аэровокзал model:** 11 axes, bubbles raised above the building on four elevations (`revit_set_grid_vertical_extents`, 2026-10-26). RF-D1 still needs the bubbles on the left/bottom of each plan and Russian letters from the allowed set.
- **PDF check limits.** Revit_Sheet reads PDFs: it can verify stamp structure, letters, formats and visible weights, but not the true mm of a form or the exact stroke thickness — it reports "NOT CHECKABLE" for those, never a pass.

## 4. What this family does not cover

Content of the drawings (ГОСТ 21.501-2018: floor-plan/section/facade content, symbols) — only its scale-table summary was read; ГОСТ 21.201 (conventional symbols) and ГОСТ 21.204 (master-plan symbols) not loaded. Structural/MEP marks beyond АР. Fire-safety text on sheets. Electronic-document (XML, signature) rules of the 2026 edition.

## 5. Corrections to Al's paste and unverified items (HR, 2026-10-30)

Al's text was checked against web copies of ГОСТ Р 21.101-2020 (meganorm.ru), ГОСТ Р 21.101-2020 п.5.3–5.4 (sarrztech.ru), ГОСТ 21.1101-2013 (spds.ru), ГОСТ 2.301/2.302/2.303/2.304 (spds.ru, gostam.ru) and stroyinf.ru / Kontur status pages. The scanned official PDFs (acs-nnov.ru, modul.org) have no text layer, so the form drawings could not be read.

**Slips in the paste:**
1. "ГОСТ Р 21.1101-2013 / ГОСТ Р 21.101-2020" lists the old one as if current — 21.1101-2013 was **replaced** by 21.101-2020, and 21.101-2020 itself by **21.101-2026 from 01.04.2026**.
2. **ГОСТ 2.104-2006** (title blocks) belongs to ЕСКД (mechanical drawings). Construction sheets use the **СПДС stamp forms of ГОСТ Р 21.101** (Приложение Ж). Do not score a construction sheet against 2.104.
3. **Form numbers.** The paste calls Form 4 the continuation-sheet stamp (185×15) and Form 2 a left-margin stamp. In the 2020 text: **Form 3** = main-set working drawings; **Form 4** = first sheet of building-product drawings; **Form 5** = first/title sheets of text documents (and sketches); **Form 6** = subsequent sheets of product drawings/text documents/sketches, also later sheets of a graphic part when all share one name; **Forms 1 and 2 are the ведомость forms** (Приложение В). The left-margin strip carries graphs 10–13 («Согласовано», on the first sheet) — not "Form 2". No "form 2a" exists in this text.
4. **Extended formats.** The paste gives A3×3 = 297×1261 and A4×3 = 210×891 — wrong. Extension multiplies the **short** side: A3×3 = 420×891, A4×3 = 297×630, A2×3 = 594×1261.
5. **Axis letters.** The paste's excluded list (З, Й, О, Х, Ъ, Ы, Ь) misses **Ё, Ц, Ч, Щ**. Also: digits go on the side with more axes; marks are mainly on the left and bottom, repeated top/right where axes differ.
6. **Elevation mark.** The paste says an arrow triangle "pointing down". The text: thin **45° strokes 2–4 mm** on extension lines for sections/facades, and a **rectangle on plans**; zero **without sign** (`0.000`). The paste's `0.000` is right; a `±0.000` (used on the Libya sheet, ISO practice) is not the RF form.
7. **Font.** "15° slanted or upright, Type B" — ГОСТ 2.304 allows Type **A and B**, both sloped ≈ 75° from the baseline (= 15° off vertical); the text does not say Type B is the usual choice and has no upright variant.
8. "Form 3 = 185×55, Form 4 = 185×15–23" and "left-margin form 20 mm": **not readable** in the official text (images). 185×55 for Form 3 comes from a secondary site (smetomer.ru) and agrees with common SPDS practice; 185×15 for continuation sheets is **not confirmed** — treat the stamp *structure* (graphs) as checkable and the *millimetres* as "to confirm against the Приложение Ж drawing".

**Not verified / not read:** ГОСТ Р 21.101-2026 text, its transition clause and changes; the full марки table (Таблица Г.1); the sheet-numbering rule (сквозная vs within the set); ГОСТ 21.501-2018 body (its scale table is from a search summary: plans/sections/facades 1:50, 1:100, 1:200, 1:400, 1:500; products 1:5, 1:10, 1:20); absolute (Baltic) marks in brackets; the elevation triangle's size; minimum text heights on drawings.

## Sources

ГОСТ Р 21.101-2020 (meganorm.ru; sarrztech.ru п.5.3, 5.4), ГОСТ 21.1101-2013 (spds.ru п.5), ГОСТ 2.301-68 / 2.302-68 / 2.303-68 / 2.304-81 (spds.ru, gostam.ru), ГОСТ 21.501-2018 (search summaries only), status of ГОСТ Р 21.101-2020/2026 (files.stroyinf.ru, Kontur). A working synthesis, not a reproduction of the standard; the official text governs if a figure disagrees.
