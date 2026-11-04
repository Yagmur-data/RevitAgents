---
name: door-window-code-check
description: Door and window rules the Revit_DoorWindow agent builds to and reports against — geometric build checks (opening inside the wall, no overlap, fits the wall height, hosted, swing/hand, sill/level) plus code rules for doors (clear width and height, swing direction, swing into corridors and stair landings, thresholds, outside-door landing, self-closing + seals, fire-door type, accessible doors and the clear space in front of them, glazed-door marking, distance to the nearest evacuation exit, station combined-hall exits) and windows (emergency exit through a window, sill / fall protection, daylight). RF family loaded 2026-10-21 from the code text of СП 1.13130.2020 (Изм. 1–3), СП 59.13330.2020 (Изм. 1–4) and 123-ФЗ table 24 (verifying Al's Аэровокзал paste); US/UK/TR families named but not loaded. Says for each rule how the agent checks it in the live Revit model, what it does when a rule fails, and which items are engineer-only.
---

# door-window-code-check

What a door or window placed by `Revit_DoorWindow` has to satisfy, and how
the agent proves it — or says plainly that it can't. A **build-to + report**
rubric, not a certification: the agent never writes that a door or window
"complies with the code".

The geometric build checks (§3 G1–G6) need no standard and always run. Code
rows run only for a family that is loaded (§1); for any other family they
are KONTROL EDİLEMEDİ with the measured value. **Never fill a figure from
memory or borrow one from another family or another skill.**

## 0. Project document first — don't add this skill's rules on top

Same rule as `stair-code-check` §0 / `roof-code-check` §0 (Al, 2026-10-21):
if the job has a Word document (ТЗ / şartname), scan it with
`python -I .claude/agents/Revit_Roof/scripts/docx_standards.py <file.docx>`.

- **It names standards**: those are the basis; this skill's other families
  are not added. When it cites Russian norms (СП / пожарная безопасность /
  доступность, even as a general clause), the **RF rules (§3b) are the
  figures for those cited standards and are applied** — as for stairs.
  Report header: `Basis: <file> — RF: СП 1.13130.2020 (ред. 16.06.2025) + СП 59.13330.2020`.
- **No document, or it names no standards**: use §1.

## 1. Basis — one code family per job

| Family | Documents | State |
|---|---|---|
| **RF** | **СП 1.13130.2020** «Эвакуационные пути и выходы» (Приказ МЧС № 194; Изм. 1 № 1203 от 21.11.2023, Изм. 2 № 681 от 21.08.2024, Изм. 3 № 502 от 16.06.2025); **СП 59.13330.2020** «Доступность зданий и сооружений для МГН» (Изм. 1–4, last № 938/пр от 27.12.2024); **123-ФЗ** table 24 (fire-door types) | **Loaded 2026-10-21**, from the code text (consolidated copies at tiflocentre.ru, read and quote-checked by HR; cross-check against an official copy before a submission). Russian jobs and jobs whose ТЗ cites СП. |
| US | IBC ch. 10 (§1010 doors), §1015/§1031, §2406, ICC A117.1 / ADA | **not loaded** |
| UK | Approved Documents B, K, M, Q | **not loaded** |
| TR | Binaların Yangından Korunması Hakkında Yönetmelik, Planlı Alanlar İmar Yönetmeliği, TS 9111 | **not loaded** |

- A job without a document and with no family named: there is **no default
  family for doors/windows yet** (stairs default to US — Al has not said the
  same for doors). Report G rows, measurements, and ask Al once which family
  applies; don't assume US.
- Never mix families in one job. Values are in metres "в свету" as the code
  measures them (§3b note 1).

### Inputs the agent needs (ask only when a rule needs one)

| Input | Needed by | Note |
|---|---|---|
| **Number of people** using the door / route (fewer than 15? 50 or more?) | RF-D2, RF-D3, RF-A1 | From the user, or the room's design occupancy; never invented |
| **Functional class** (Ф…), and room category А/Б if industrial | RF-D3 exceptions, RF-H1 | Аэровокзал: Ф3.3 (job notes) |
| **Fire-resistance degree** (I–V) and **structural fire-hazard class** (С0–С3) of the building | RF-F2, RF-H1 | Not in the model — ask; record in the job notes |
| **Accessible route?** (wheelchair users / М4 present) | RF-A1…A4 | Public buildings normally yes |
| **Smoke-ventilated corridors / rooms** | RF-F1 | From the user / MEP; not in the model |
| Hall **volume** (m³) | RF-H1 | Room `Volume` if computed, else area × height |

## 2. Status words (Turkish report)

Same as `stair-code-check` §2: **UYGUN**, **UYGUN DEĞİL**, **ÖNERİ**,
**KONTROL EDİLEMEDİ**, **MÜHENDİS**.

## 3. Geometric build checks (no standard needed — always run)

| ID | Rule | Check with | On fail |
|---|---|---|---|
| **G1 Inside the wall** | Opening edges stay inside the host wall, at least the jamb distance the user/type needs from each wall end and from wall joins | `opening_layout.py --min-end`; after: instance bbox vs wall line | **BLOCK** |
| **G2 No overlap** | No overlap with existing doors/windows/openings in the same wall; minimum pier if the user gives one | `opening_layout.py --existing --min-gap` | **BLOCK** |
| **G3 Fits the wall height** | Head height ≤ wall height (minus any lintel the user names); sill + height = head | wall `Unconnected Height` vs instance `Head Height` | **BLOCK** |
| **G4 Hosted, opening cut** | Instance has the intended `Host Id` | read-back | fix before reporting |
| **G5 Swing / hand as asked** | Opens to the side the user named, hinge on the named side; doesn't swing into a stair flight or another door's swing | `revit_get_doors` facing/hand + `revit_get_element_rooms` | **FLAG**, fix by re-placing |
| **G6 Level / elevation** | Instance level = wall base level; window `Sill Height` as planned | read-back `Level`, `Sill Height`, `Head Height` | fix before reporting |

## 3b. RF rules — СП 1.13130.2020 + СП 59.13330.2020

Clause numbers are those of the amended text (Изм. 1–3 for СП 1; the door
rules are **4.2.18–4.2.27** there). Quotes are verbatim, shortened.

**Note 1 — clear width in Revit.** The code measures «в свету» — «минимальное
расстояние между выступающими конструкциями» (СП 1 4.1.4); СП 59 6.1.5:
«Ширину дверного проема измеряют при открывании двери на 90°». Revit's door
type `Width` is the nominal leaf/opening width; the clear width is smaller
by the stop/frame and, at 90°, the leaf thickness (`Thickness` 45 mm on the
M_Door types). Working rule (*HR*): clear ≈ `Width` − `Thickness` − 0.01 m;
**UYGUN** only if that estimate meets the limit; if `Width` itself meets it
but the estimate doesn't → **KONTROL EDİLEMEDİ (sınırda — doğrama detayına
bağlı)**; if `Width` is below the limit → **UYGUN DEĞİL**. Height the same
way with `Height` (no deduction for the leaf).

**Note 2 — double doors.** 4.2.27: «При использовании двупольных дверей с
"пассивным" (зафиксированным) дверным полотном ширина эвакуационного выхода
определяется только шириной выхода через "активное"…». A double door counts with
its full `Width` only if both leaves open; ask when it matters, else state
the assumption.

### Doors on escape routes (СП 1.13130.2020)

| ID | Rule | Figure (code text) | Check with | On fail |
|---|---|---|---|---|
| **RF-D1 Clear height** | 4.2.18: «Высота эвакуационных выходов в свету должна быть, как правило, не менее 1,9 м» | **≥ 1.9**; 1.8 in rooms without permanent occupancy / single workplace; < 1.9 → top edge marked per ГОСТ 12.4.026 | Type `Height` (note 1) | **BLOCK** |
| **RF-D2 Clear width** | 4.2.19: «…как правило, не менее 0,8 м… при числе эвакуирующихся… 50 человек и более должна быть не менее 1,2 м» | **≥ 0.8**; **≥ 1.2** for 50 people or more; 0.6 allowed from technical rooms/storerooms ≤ 20 m², WC/shower cabins, single-workplace rooms | Type `Width` (notes 1, 2) + people count | **BLOCK** |
| **RF-D3 Swing direction** | 4.2.22: «Двери эвакуационных выходов и двери, расположенные на путях эвакуации должны открываться по направлению выхода из здания» | Exceptions (not regulated): а) Ф1.3/Ф1.4; б) rooms/routes for **15 people or fewer** (not category А/Б); в) storerooms ≤ 200 m² without permanent workplaces; г) exits to type-3 stair landings; д) external doors in the northern climate zone; е) doors in partitions dividing corridors; ж) category Б rooms with combustible dust | `revit_get_doors` facing + `revit_get_element_rooms` from/to vs the side toward the exit | **BLOCK** (choose `flipFacing` before placing) |
| **RF-D4 Swing into a corridor** | 4.3.4: corridor width reduced «на половину ширины дверного полотна» (doors on one side, or both sides ≥ 10 m apart), «на ширину дверного полотна» (both sides, closer) | Required corridor width 4.3.3: **1.2** for more than 50 people, **0.7** to a single workplace, else **1.0** | Corridor clear width (walls' faces) − the reduction vs the required width | **FLAG** |
| **RF-D5 Swing into a stairwell** | 4.4.2: «Двери, выходящие на лестничную клетку, в максимально открытом положении не должны уменьшать требуемую ширину лестничных площадок и маршей» | Open leaf (width around the hinge, `Swing Angle`) stays outside the required landing/flight band | Leaf arc vs the landing outline (Revit_Stair's numbers); coordinate with Revit_Stair | **BLOCK** for a new door; FLAG for an existing one |
| **RF-D6 Threshold** | 4.3.5: no steps on escape routes «за исключением порогов в дверных проемах высотой не более 50 мм» | **≤ 0.05** (accessible doors: RF-A2) | Door `Threshold` parameter if it carries a height; else KONTROL EDİLEMEDİ | **FLAG** |
| **RF-D7 Outside-door landing** | 4.2.21: level landing at least «1,5 ширины полотна наружной двери» | depth and width ≥ **1.5 × leaf width** | Floor/landing outline outside the door | **FLAG** |
| **RF-D8 Stairwell exit width** | 4.2.20: exits from a stairwell to the outside/vestibule ≥ the required flight width; several exits sharing a required 1.2 m → each **≥ 0.9** | as stated | Door `Width` vs the stair's required width (stair-code-check RF1) | **BLOCK** |

### Fire and smoke (СП 1.13130.2020, 123-ФЗ)

| ID | Rule | Figure (code text) | Check with | On fail |
|---|---|---|---|---|
| **RF-F1 Self-closing + seals** | 4.2.24: doors of evacuation exits from rooms and corridors protected by smoke ventilation, and doors in partitions dividing corridors, «должны быть оборудованы приспособлениями для самозакрывания и уплотнением в притворах» (exceptions in 4.2.24: doors from rooms without smoke ventilation into a ventilated corridor; bottom seal where no threshold and no smoke ventilation; doors held open must close automatically in a fire). 4.4.6: exits from rooms and floors to stairwells — the same, except apartment doors | yes / no | Door type name / `Hardware` / a closer parameter if the family has one; usually not modeled → KONTROL EDİLEMEDİ, list the doors it applies to | **FLAG** (hardware spec: MÜHENDİS) |
| **RF-F2 Fire-door type** | Fire-safe zone type 1 for МГН (9.2.1, 9.2.2): openings filled «противопожарными дверями не ниже 1-го типа в высотных зданиях и зданиях I степени огнестойкости и не ниже 2-го типа в зданиях II - IV степени»; types per 123-ФЗ table 24: **1st type = EI 60, 2nd = EI 30, 3rd = EI 15** (glazing > 25 % → EIW) | by fire-resistance degree | Door type `Fire Rating` (empty on the M_Door types → duplicate the type and set it, with a yes) | **FLAG**; which rooms are safe zones: MÜHENDİS |

### Accessible doors (СП 59.13330.2020)

| ID | Rule | Figure (code text) | Check with | On fail |
|---|---|---|---|---|
| **RF-A1 Accessible clear width** | 6.1.5: «…должны иметь ширину в свету не менее 0,9 м» (0.8 in reconstruction in a load-bearing wall; double entrance doors: one leaf ≥ 0.9); 6.2.4: door leaves, openings and exits to stairwells ≥ **0.9**, ≥ **1.2** if the reveal is deeper than 1.0 m; 6.2.21: evacuation doors ≥ **1.2** for more than 15 people of М2–М4 or more than 5 of НМ/НТ, ≥ 0.9 where М4 users are present | as stated | Type `Width` (note 1, measured at 90°) | **BLOCK** on an accessible route |
| **RF-A2 Accessible threshold** | 6.2.4: thresholds «не должны превышать 0,014 м» | **≤ 0.014** | as RF-D6 | **FLAG** |
| **RF-A3 Clear space in front** | 6.2.2: «…при открывании от себя должна быть не менее 1,2 м, а при открывании к себе - не менее 1,5 м при ширине не менее 1,5 м» | push side **1.2** deep; pull side **1.5 × 1.5** | `revit_check_clearance` (bbox) or the room outline in front of the door, using the facing side | **FLAG** |
| **RF-A4 Entrance landing / tambour** | 6.1.4: entrance landing with a ramp **2.2 × 2.2**, without a ramp **1.6 × 2.2** (new), 1.4 × 1.8 (reconstruction), 1.9 × 1.2 with automatic sliding doors; 6.1.8: tambour **2.45 × 1.6** with doors in line | as stated | Landing / tambour outline | **FLAG** |
| **RF-A5 Glazed doors** | 6.1.6: contrast marking ≥ 0.1 × 0.2 m (or Ø 0.1–0.2) at **0.9–1.0 m and 1.3–1.4 m**, both sides; not needed if the glass is narrower than 0.3 m, its bottom edge is at 0.85 m or higher, or an opaque band ≥ 0.1 m lies within 0.85–1.4 m | yes / no | Family glazing (Vision_Lite / Two_Lite types have glass) — marking isn't modeled → list the doors | **FLAG** / KONTROL EDİLEMEDİ |
| **RF-A6 Opening force** | 6.1.5 / СП 1 9.3.8: «Усилие открывания двери не должно превышать 50 Нм» | ≤ 50 Nm | Not modeled | **MÜHENDİS** |

### Halls and stations (СП 1.13130.2020 section 7)

| ID | Rule | Figure (code text) | Check with | On fail |
|---|---|---|---|---|
| **RF-H1 Distance to the nearest exit** | 7.1.4 table 5, halls without spectator seats («Залы ожиданий для посетителей, кассовые…»): max distance to the nearest evacuation exit by building class and hall volume (up to 5 / over 5 to 10 / over 10 thousand m³) — С0: **30 / 45 / 55 m**; С1 + III–IV degree: **20 / 30 / –**; С2, С3 + V degree: **15 / – / –**. If rooms of more than 5 people open into the hall, the distance includes the longest route from those rooms. | as stated | Straight-line distance from the farthest point of the room outline to the nearest exit door (lower bound of the real walking path) → UYGUN only if well under; else KONTROL EDİLEMEDİ (path not measurable with the tools) | **FLAG** |
| **RF-H2 Station combined hall** | 7.8.1 «Вокзалы»: «Выходы из 50% лестничных клеток, а также коридоров зданий вокзалов в объединенный пассажирский зал, имеющий выходы непосредственно наружу, на наружную открытую эстакаду или на платформу, допускается считать эвакуационными» — a **permission**, not a requirement; whether the 50 % also limits the corridors is ambiguous in the text | ≤ 50 % of stairwells | Count stairwell exits into the hall vs total; report, don't decide | **MÜHENDİS** (evacuation design) |
| **RF-H3 МГН share** | 9.1.3 table 21: «Вокзалы, аэровокзалы — 2% общей вместимости здания» (groups М2–М4) | ≥ 2 % | Input to RF-A1 (6.2.21 "more than 15 people of М2–М4") | report as input |

### Windows (СП 1.13130.2020)

| ID | Rule | Figure (code text) | Check with | On fail |
|---|---|---|---|---|
| **RF-W1 Emergency exit through a window** | 4.2.4 г: an emergency exit (аварийный выход) through a window/door at least **0.75 × 1.5 m**, from floors between −4.5 m and +5.0 m; such exits are not counted as evacuation exits | as stated | Type `Width`/`Height` (openable part only if the family says so) | **FLAG**, only when the user names the window as an emergency exit |
| **RF-W2 Sill / fall protection** | Not loaded: СП 54.13330.2022 / СП 118.13330.2022 not verified | — | `Sill Height` + height above the ground below | KONTROL EDİLEMEDİ |
| **RF-W3 Daylight** | Not loaded: СП 52.13330.2016 / СанПиН 1.2.3685-21 not verified | — | Window area per room vs room `Area` (measurement only) | KONTROL EDİLEMEDİ |

Always **MÜHENDİS**: door hardware/closers and panic bars, fire-rating
certification, smoke-control design, evacuation calculation, safety-glass
specification.

## 4. How the agent uses this

1. **Before placing:** basis (§0/§1) and the inputs in §1 that the door's
   rules need; run G1–G3 on `opening_layout.py`'s numbers and the BLOCK rows
   that can be checked from the chosen type (RF-D1, RF-D2, RF-D3 side,
   RF-D5, RF-D8, RF-A1). A BLOCK stops the placement: give the failing and
   the compliant value (e.g. "900'lük kapı net ~0.85 m, 50+ kişi için 1.2 m
   gerekli — 1800'lük çift kanat?") and wait.
2. **After placing and reading back:** G4–G6, then the rest of the rows that
   apply.
3. **Report** short, at the end of the reply:

   ```
   Kapı/pencere kontrolü — esas: ТЗ — RF: СП 1.13130.2020 (ред. 16.06.2025) + СП 59.13330.2020
   | Kural | Ölçülen | Durum |
   | G1 Duvar içinde, uçlara ≥ 0.10 | 0.85 / 4.25 | UYGUN |
   | RF-D1 Yükseklik ≥ 1.9 | 2.10 | UYGUN |
   | RF-D2 Genişlik ≥ 0.8 (< 50 kişi) | Width 0.90 → net ~0.85 | UYGUN |
   | RF-D3 Çıkış yönüne açılır | koridora açılıyor | UYGUN |
   | RF-A1 Erişilebilir ≥ 0.9 | net ~0.85 | KONTROL EDİLEMEDİ (sınırda) |
   | RF-F1 Kendiliğinden kapanma + conta | modellenmedi | KONTROL EDİLEMEDİ |
   | RF-A6, donanım | — | MÜHENDİS |
   ```

   Only rows that apply. Never write "kapı yönetmeliğe uygun".
4. A wrong or outdated figure is fixed **here** (and noted in §5), not
   overridden in one job.

## 5. Corrections to Al's Аэровокзал paste (2026-10-21)

The paste's door items were checked against the code text; what it said →
what the text says:

- **"EI 30 evacuation doors in buildings over 28 m"** — **no such clause** in
  СП 1.13130.2020 or СП 2.13130.2020 (2022 copy). For ≥ 28 m the text sets
  **walls/partitions of common escape routes ≥ (R)EI(W) 45** (СП 1 7.1.11,
  СП 2 5.2.7) — not doors. EI 30 doors appear only in narrower cases (school
  stairwells 7.12.20, tambours at stairwells without smoke protection 9.2.2,
  doors to МГН ramps 9.3.5). Not used as a rule. СП 7.13130 / СП 4.13130 not
  read — if Al has the source, add it here.
- **"Fire-safe zones need doors of at least EI 60"** — only for high-rise and
  fire-resistance degree I buildings (1st-type doors = EI 60); **degree II–IV
  need 2nd-type doors = EI 30** (9.2.2 + 123-ФЗ table 24). "Дымогазо-
  непроницаемые" doors are for type-4 zones in stairwells (9.2.7).
- **Self-closing + seals** — right, but the clause is **4.2.24** (and 4.4.6
  for stairwell doors); the paste's general reading omitted its exceptions.
- **"50 % of stairwells/corridors into the combined passenger hall"** —
  right (7.8.1), but it is a **permission** ("допускается"), not a duty.
- **30 / 45 / 55 m** — right for С0 (7.1.4 table 5), but the table is for
  all halls without spectator seats, not only stations, and has С1–С3 rows.
- **2 % МГН** — right; source is СП 1.13130.2020 9.1.3 table 21 (not СП 59),
  and it counts groups М2–М4.
- Acoustics (60/75 dBA, ГОСТ 31937 tests) and façade K0 are not door/window
  rules — filed in the job's `standards_ru.md`, not here.
- Door width/height/swing/threshold/accessibility rows (RF-D1…D8, RF-A*,
  RF-W1) were **not in the paste**: added by HR from the same code text, so
  the RF family can check a door at all.
