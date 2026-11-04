---
name: wall-floor-code-check — RF sources
description: RF family source table (123-ФЗ, СП 2/4/29/50/51/59/118/478) read 2026-10-30 — clause, verbatim quote, URL, edition per figure. Detail behind SKILL.md §3c.
---

# RF wall / floor rules: code-text extract for the Аэровокзал Северное job

Researched 2026-10-30 from the code text. Every figure below was read in the text at the URL given; quotes are verbatim (≤ 25 words, sometimes shortened with "…").
Job context: 2 storeys, 26 × 16 m (416 m² per floor), Ф3.3, non-capital / quick-erect. Fire-resistance degree and С-class are not decided yet, so rules are given for every degree.

Source note: docs.cntd.ru refused connections from this machine, so it was not used. The sources were:
consultant.ru for 123-ФЗ and СП 4; pravo.ppt.ru (KonsultantPlus-based legal portal) for СП 2;
meganorm.ru (KonsultantPlus text) for СП 29 and СП 51; tiflocentre.ru for СП 59, СП 118 and СП 478; base.garant.ru for СП 50 and СП 121.
None of these is an official minstroyrf or МЧС copy. Cross-check against an official copy before any submission.

---

## 1. 123-ФЗ «Технический регламент о требованиях пожарной безопасности»

Edition read: **ред. от 04.08.2026** (consultant.ru). Tables 21 and 23 are in the ред. 117-ФЗ of 10.07.2012.

URLs:
- T21 = https://www.consultant.ru/document/cons_doc_LAW_78699/82621340ca1a9518ffc84bae9a0442c389a93026/
- T23 = https://www.consultant.ru/document/cons_doc_LAW_78699/36dda4551e83122c0d8a96024dd59f4fce906cfb/
- A87 = https://www.consultant.ru/document/cons_doc_LAW_78699/fe6f2e75d44b06464b0f0475d61eba4f72f58ba7/
- A88 = https://www.consultant.ru/document/cons_doc_LAW_78699/3b87f9d76941059df91fe2051986107e0ac00a1a/

### Table 21: fire resistance of building elements by degree (ст. 87 ч. 2)

| Degree | Несущие стены, колонны и др. несущие элементы | Наружные ненесущие стены | Перекрытия междуэтажные (в т.ч. чердачные и над подвалами) | Бесчердачное покрытие: настилы (в т.ч. с утеплителем) | Бесчердачное покрытие: фермы, балки, прогоны | Лестничные клетки: внутренние стены | Лестничные клетки: марши и площадки |
|---|---|---|---|---|---|---|---|
| I | R 120 | E 30 | REI 60 | RE 30 | R 30 | REI 120 | R 60 |
| II | R 90 | E 15 | REI 45 | RE 15 | R 15 | REI 90 | R 60 |
| III | R 45 | E 15 | REI 45 | RE 15 | R 15 | REI 60 | R 45 |
| IV | R 15 | E 15 | REI 15 | RE 15 | R 15 | REI 45 | R 15 |
| V | не нормируется | не нормируется | не нормируется | не нормируется | не нормируется | не нормируется | не нормируется |

| Rule | Value | Clause | Verbatim quote | URL |
|---|---|---|---|---|
| Element limits follow the chosen degree | table 21 | ст. 87 ч. 2 | «Пределы огнестойкости строительных конструкций должны соответствовать принятой степени огнестойкости зданий, сооружений и пожарных отсеков.» | A87 |
| Which elements count as load-bearing | defined by fire-safety normative documents (СП 2 5.4.2) | Табл. 21, примечание | «Порядок отнесения строительных конструкций к несущим элементам здания и сооружения устанавливается нормативными документами по пожарной безопасности.» | T21 |
| Openings, doors and windows: not rated except in fire barriers | — | ст. 87 ч. 3 | «Пределы огнестойкости заполнения проемов (дверей, ворот, окон и люков)… не нормируются, за исключением заполнения проемов в противопожарных преградах.» | A87 |
| Н1 stair flights and landings | R15, К0 allowed | ст. 87 ч. 4 | «На незадымляемых лестничных клетках типа Н1 допускается предусматривать лестничные площадки и марши с пределом огнестойкости R15 класса пожарной опасности К0.» | A87 |
| Facade finish, degree I–III | not Г2–Г4; facade systems must not spread fire | ст. 87 ч. 11 | «не допускается выполнять отделку внешних поверхностей наружных стен из материалов групп горючести Г2 - Г4» | A87 |

### Table 23: fire barriers (ст. 88 ч. 2)

| Barrier | Type | Fire resistance | Type of opening fill | Type of tambour-lock |
|---|---|---|---|---|
| Стены | 1 | REI 150 | 1 | 1 |
| Стены | 2 | REI 45 | 2 | 2 |
| Перегородки | 1 | EI 45 | 2 | 1 |
| Перегородки | 2 | EI 15 | 3 | 2 |
| Светопрозрачные перегородки, остекление > 25 % | 1 | EIW 45 | 2 | 1 |
| Светопрозрачные перегородки, остекление > 25 % | 2 | EIW 15 | 3 | 2 |
| Перекрытия | 1 | REI 150 | 1 | 1 |
| Перекрытия | 2 | REI 60 | 2 | 1 |
| Перекрытия | 3 | REI 45 | 2 | 1 |
| Перекрытия | 4 | REI 15 | 3 | 2 |

| Rule | Value | Clause | Verbatim quote | URL |
|---|---|---|---|---|
| Fire walls run full height | full height, or up to a type-1 fire floor | ст. 88 ч. 5 | «Противопожарные стены должны возводиться на всю высоту здания или сооружения либо до противопожарных перекрытий 1-го типа» | A88 |
| Junctions of fire barriers | ≥ the rating of the barrier | ст. 88 ч. 6 | «Места сопряжения противопожарных стен, перекрытий и перегородок… должны иметь предел огнестойкости не менее предела огнестойкости сопрягаемых преград.» | A88 |
| Openings in fire barriers | total ≤ 25 % of barrier area | ст. 88 ч. 9 | «Общая площадь проемов в противопожарных преградах не должна превышать 25 процентов их площади.» | A88 |
| Windows in fire barriers | non-opening | ст. 88 ч. 8 | «Окна в противопожарных преградах должны быть неоткрывающимися» | A88 |
| Shaft and channel enclosures | partition type 1 + floor type 3 | ст. 88 ч. 15 | «…должны соответствовать требованиям, предъявляемым к противопожарным перегородкам 1-го типа и перекрытиям 3-го типа.» | A88 |

---

## 2. СП 2.13130.2020 «Обеспечение огнестойкости объектов защиты»

Editions read:
- **Consolidated text ред. 20.06.2023 (with Изм. 1, Приказ МЧС № 641).** URL **S2** = https://pravo.ppt.ru/prikaz/mchs/n-151-237845
- **Изм. 2 (Приказ МЧС от 06.11.2025 № 999, in force 01.01.2026), read in full.** URL **S2i2** = https://pravo.ppt.ru/prikaz/mchs/n-999-320515

Where Изм. 2 rewrote a clause, the Изм. 2 wording is the one given below.

### Which table applies to Ф3.3

| Rule | Value | Clause | Verbatim quote | URL |
|---|---|---|---|---|
| Public buildings (incl. Ф3.3) use **table 6.9**. Table 6.10 is only for Ф3.5 and table 6.11 only for Ф3.1 | table 6.9 | 6.7.1 | «…площадь этажа в пределах пожарного отсека общественных зданий… следует принимать в соответствии с таблицей 6.9» | S2 |
| Air terminals are Ф3.3 | — | СП 478 9.1.1 | «аэровокзалы следует относить к общественным зданиям по обслуживанию населения класса функциональной пожарной опасности Ф3.3» | see §9 |

### Table 6.9 (not changed by Изм. 2)

Columns: allowed height, then floor area within a fire compartment (m²) by number of above-ground storeys.

| Degree | С-class | Allowed height, m | 1 storey | 2 storeys | 3 | 4–5 | 6–9 | 10–16 |
|---|---|---|---|---|---|---|---|---|
| I | С0 | 50 | 6000 | 5000 | 5000 | 5000 | 5000 | 2500 |
| II | С0 | 50 | 6000 | 4000 | 4000 | 4000 | 4000 | 2200 |
| II | С1 | 28 | 5000 | 3000 | 3000 | 2000 | 1200 | – |
| III | С0 | 15 | 3000 | 2000 | 2000 | 1200 | – | – |
| III | С1 | 12 | 2000 | 1400 | 1200 | 800 | – | – |
| IV | С0 | 9 | 2000 | 1400 | – | – | – | – |
| IV | С1 | 6 | 2000 | 1400 | – | – | – | – |
| IV | С2, С3 | 6 | 1200 | 800 | – | – | – | – |
| V | С1–С3 (as printed in this copy) | 6 | 1200 | 800 | – | – | – | – |

At 416 m² per floor and 2 storeys, every row allows the area. **Height is the binding check:** IV/С1, IV/С2–С3 and V are limited to 6 m; IV/С0 to 9 m.

| Rule | Value | Clause | Verbatim quote | URL |
|---|---|---|---|---|
| Dash in the table | that degree cannot have that number of storeys | T6.9 прим. 1 | «Прочерк в таблице означает, что здание данной степени огнестойкости не может иметь указанное число этажей.» | S2 |
| **IV degree, 2 storeys: load-bearing elements** | **≥ R 45** (overrides R 15 in 123-ФЗ table 21) | T6.9 прим. 2 | «В зданиях IV степени огнестойкости высотой два этажа несущие элементы здания должны иметь предел огнестойкости не ниже R 45.» | S2 |
| Sprinklers, I–II degree С0 | floor area may be doubled at most | 6.7.2 | «…при наличии автоматического пожаротушения площадь этажа в пределах пожарного отсека может быть увеличена не более чем вдвое» | S2 |
| Stations, I–II degree С0 | fire sections with drencher + EI 60 curtains instead of type-1 fire walls | 6.7.4 | «…противопожарными шторами с пределом огнестойкости не менее EI 60, с длиной выпуска рабочего полотна до уровня пола» | S2 |
| Air terminal, I degree | floor between fire walls up to 10 000 m² (conditions on basements) | 6.7.5 | «В зданиях аэровокзалов I степени огнестойкости площадь этажа между противопожарными стенами может быть увеличена до 10 000 м2» | S2 |
| Air terminal, I degree С0 + sprinklers | floor area between fire walls not limited | 6.7.6 | «…оборудованных автоматическими установками пожаротушения, площадь этажа между противопожарными стенами не нормируется.» | S2 |
| **Ф3.3 in С1–С3: walls, partitions, floors** | class К0, insulation НГ | 6.7.11 (Изм. 2) | «Наружные стены, внутренние стены, перегородки и перекрытия зданий, классов Ф1.1, Ф2.1, Ф3.3… в зданиях… С1 - С3… должны иметь класс пожарной опасности K0.» | S2i2 |
| Parts of different height (I–III degree), windows facing the lower roof | lower roof ≥ RE 45, К0; insulation НГ within 6 m | 6.7.1 абз. 2 (Изм. 2) | «…конструкции покрытия низкой части должны иметь предел огнестойкости не менее RE 45 и класс пожарной опасности K0.» | S2i2 |
| Attached canopies, terraces, galleries | degree may be one step lower | 6.7.7 | «Степень огнестойкости пристроенных к зданию навесов, террас и галерей допускается принимать на одну величину ниже» | S2 |

### Walls, partitions and floors: general rules (section 5)

| Rule | Value | Clause | Verbatim quote | URL |
|---|---|---|---|---|
| **Partitions to corridors, halls and vestibules (evacuation routes), building < 28 m** | **I–III: (R)EI(W) 30; IV: (R)EI(W) 15; К0** (≥ 28 m: 45) | 5.2.7 абз. 3 (Изм. 2) | «…в зданиях меньшей высоты I - III степеней огнестойкости - не менее (R)EI(W) 30, IV степени огнестойкости - не менее (R)EI(W) 15.» | S2i2 |
| Same partitions: floor to slab | run from floor to the floor/roof slab, also above suspended ceilings | 5.2.7 абз. 1–2 | «Пути эвакуации… должны отделяться от помещений стенами и перегородками, предусмотренными от пола до перекрытия (покрытия).» | S2 |
| Doors and windows in those partitions | doors not rated; windows non-opening; unrated windows only if windows + doors ≤ 25 % | 5.2.7 (Изм. 2, new paragraph) | «…суммарная площадь окон и дверей в пределах каждого помещения не превышает 25% от площади ограждающей конструкции» | S2i2 |
| Cavities in walls, partitions and floors (I–IV degree) | floor cavities cut at room/corridor outline and into ≤ 54 m² sections; cavities behind combustible linings ≤ 3 m² | 5.2.2 (Изм. 2) | «…дополнительно разделены на участки площадью не более 54 м2» | S2i2 |
| Timber-frame enclosing walls, public buildings I–III degree | no combustible insulation | 5.2.11 (Изм. 2, new) | «…с применением ограждающих конструкций на деревянном каркасе не допускается использование в качестве утеплителя этих конструкций горючих материалов.» | S2i2 |
| Load-bearing elements: definition | walls, columns, bracing, floor and roof elements that give overall stability | 5.4.2 | «К несущим элементам зданий следует относить несущие стены, колонны, а также связи, диафрагмы жесткости, фермы, элементы перекрытий…» | S2 |
| Fire partitions with suspended ceilings or raised floors | divide the space above and below | 5.2.6 | «Противопожарные перегородки в помещениях с подвесными потолками и фальшполами должны разделять пространство над и под ними.» | S2 |
| Fire barriers: combustibility class | К0 or К1 depending on С-class | 5.3.3 | «Противопожарные преграды, в зависимости от класса конструктивной пожарной опасности здания, должны соответствовать классу пожарной опасности К0 или К1.» | S2 |
| Openings in fire barriers | ≤ 25 % (no limit if fills match the barrier rating, except type-1 walls) | 5.3.4 | «Общая площадь проемов в противопожарных преградах, за исключением ограждений лифтовых шахт, не должна превышать 25% их площади.» | S2 |
| Pier at the outer wall where a type-2 fire wall or type-1 partition meets it | ≥ 1.0 m (type-2 partition: ≥ 0.8 m) | 5.3.6 (Изм. 2) | «…противопожарных стен 2-го типа и перегородок 1-го типа должны быть предусмотрены простенки шириной не менее 1,0 м» | S2i2 |
| Fire compartments: what separates them | type-1 fire walls and/or type-1 fire floors | 5.4.7 | «Для выделения пожарных отсеков применяются противопожарные стены 1-го типа и (или) перекрытия 1-го типа.» | S2 |
| **Type-1 fire wall above the roof** | ≥ 60 cm if any roof element is Г3/Г4; ≥ 30 cm if Г1/Г2; none if the roof is all НГ (the wall must still cut through it) | 5.4.10 (not changed by Изм. 2) | «не менее чем на 60 см, если хотя бы один из элементов… покрытия… выполнен из материалов групп Г3, Г4» | S2 |
| **Type-1 fire wall at the facade** | must cut combustible outer walls and insulation, projecting ≥ 0.3 m; adjoining E 60 / К0 wall strips of total width ≥ 1.5 m (public premises) | 5.4.11 а) (Изм. 2) | «Размер выступа противопожарных стен относительно пересекаемых горючих материалов должен быть не менее 0.3 м.» | S2i2 |
| Type-1 fire wall with an НГ facade | may stay flush with the facade, or not cut it if the junction is rated like the wall; E 60 / К0 strips still required | 5.4.11 б), в) (Изм. 2) | «…наружные стены, выполненные из негорючих материалов (НГ), допускается разделять противопожарной стеной 1-го типа без выступа за наружную плоскость фасада.» | S2i2 |
| Old 5.4.12 (ribbon glazing) | deleted | Изм. 2 | «пункт 5.4.12 признать утратившим силу» | S2i2 |
| Type-1 fire floor at the facade | cuts the outer wall, projects ≥ 30 cm; spandrel ≥ 1.2 m, E 60 | 5.4.17 | «…выступать за наружную плоскость стены не менее чем на 30 см… междуэтажный пояс… высотой не менее 1,2 метра с пределом огнестойкости не менее E 60.» | S2 |
| **Spandrel (междуэтажный пояс), I–III degree, facades with unrated openings or glazing** | vertical height **≥ 1.2 m**, width ≥ the opening below | 5.4.18 а) | «…высота междуэтажного пояса по вертикали… должна быть не менее 1,2 м и ширина не менее ширины нижерасположенного проема.» | S2 |
| Spandrel fire rating | = outer non-load-bearing wall rating if unrated areas ≤ 6 m²; = floor rating if > 6 m² (E 60 is enough when the floor is > REI 60) | 5.4.18 а) | «…равным пределу огнестойкости наружных ненесущих стен, при устройстве ненормируемых по огнестойкости участков стен (проемов) площадью не более 6 м2» | S2 |
| Spandrel < 1.2 m | add НГ horizontal projection; projection + spandrel ≥ 1.2 m | 5.4.18 а) | «Сумма размеров горизонтальной проекции выступа и вертикальной проекции междуэтажного пояса должна быть не менее 1,2 м.» | S2 |
| Pier where rated internal walls or partitions meet the facade | ≥ 0.8 m | 5.4.18 б) | «…в местах примыкания нормируемых по огнестойкости внутренних стен и перегородок ширина простенков должна быть не менее 0,8 м» | S2 |
| Spandrel rule exemptions | one-storey buildings, stair enclosures, wet rooms, В4/Д rooms, etc. | 5.4.18 г) | «…не распространяются: … на одноэтажные здания и на места примыкания наружных стен к покрытию здания» | S2 |
| Single multi-level glazed passenger hall in a terminal | spandrels may be omitted inside one room (СП 478) | СП 478 9.3.2 | «…допускается не предусматривать пожарные пояса для одного помещения с разными уровнями, кроме мест примыкания к наружным ограждающим конструкциям» | see §9 |
| Stair enclosure meets the facade: pier to openings | ≥ 1.2 m (public premises) | 5.4.16 д) | «…1,2 м при примыкании к стене лестничной клетки… общественных… помещений» | S2 |
| Outer load-bearing walls: integrity (E) | ≥ the E required for non-load-bearing outer walls | 5.4.18 абз. 1 | «Предел огнестойкости наружных несущих и самонесущих стен по потере целостности (E) должен быть не менее требуемого предела огнестойкости для наружных ненесущих стен.» | S2 |
| Plinth insulation | combustible allowed up to 0.8 m above ground, behind ≥ 30 mm НГ protection | 5.2.3 | «…на высоту не более 0,8 м от уровня земли (или отмостки) при их защите с внешней стороны негорючими материалами толщиной не менее 30 мм» | S2 |

---

## 3. СП 4.13130.2013 «Ограничение распространения пожара…»

Edition read: **ред. от 27.06.2023** (consultant.ru).
- S4a = https://www.consultant.ru/document/cons_doc_LAW_148575/25fbb2855a682f36d144a46fee90248fed2ac4ca/
- S4b = https://www.consultant.ru/document/cons_doc_LAW_148575/3fb4b1205956b74efde1bfc75cc3e3d73e2fd800/

| Rule | Value | Clause | Verbatim quote | URL |
|---|---|---|---|---|
| Ф3.3: production, storage and technical rooms separated by fire barriers per 5.1.2 | see next row | 5.5.7 | «Размещаемые в зданиях… Ф3.3 - Ф3.7… помещения производственного, складского назначения… следует выделять противопожарными преградами в соответствии с пунктом 5.1.2.» | S4b |
| Fire-hazard rooms (other than В4 and Д) separated from rooms and corridors | **I–III degree: type-1 fire partitions; IV degree: type-2** | 5.1.2 | «…в зданиях I, II и III степеней огнестойкости - противопожарными перегородками 1-го типа, в зданиях IV степени огнестойкости - противопожарными перегородками 2-го типа» | S4a |
| 5.1.2 exemptions | wet and plumbing rooms, sanitary/household rooms, storerooms ≤ 10 m², food preparation | 5.1.2 | «…для кладовых любого назначения площадью до 10 м2, за исключением хранения изделий с горючими газами или легковоспламеняющимися жидкостями» | S4a |
| Categories А and Б | not allowed in public buildings | 5.1.2 | «Помещения взрывопожароопасных категорий А и Б размещать в жилых и общественных зданиях не допускается.» | S4a |
| Food blocks (catering) | I–III: type-1 partitions; IV: type-2 | 5.5.2 | «Пищеблоки… I, II и III степеней огнестойкости следует отделять от других помещений и общих коридоров противопожарными перегородками 1-го типа» | S4b |

---

## 4. СП 29.13330.2011 «Полы»

Edition read: **ред. от 28.11.2025, with Изм. 1 (№ 1549/пр), Изм. 2 (№ 982/пр), Изм. 3 (№ 1061/пр) and Изм. 4 (Приказ Минстроя 28.11.2025 № 757/пр).**
URL **S29** = https://meganorm.ru/mega_doc/norm_update_01022026/pravila/0/sp_29_13330_2011_svod_pravil_poly_aktualizirovannaya.html

| Rule | Value | Clause | Verbatim quote | URL |
|---|---|---|---|---|
| **Wet-room floor slope** (medium or high liquid exposure) | **0.5–1 %** seamless and slab finishes; **1–2 %** brick and concrete finishes | 4.5 | «0,5 - 1% - при бесшовных покрытиях и покрытиях из плит (кроме бетонных покрытий всех видов); 1 - 2% - при покрытиях из кирпича и бетонов всех видов.» | S29 |
| Drainage direction | to trays, channels and drains without crossing the building's movement joints | 4.5 | «…отвод сточных вод в лотки, каналы и трапы без пересечения деформационных швов здания.» | S29 |
| How the slope is formed | on slabs: screed or variable-thickness concrete; on ground: by grading | 4.7 | «Уклон полов на перекрытиях следует создавать стяжкой или бетонным покрытием переменной толщины, а полов на грунте - соответствующей планировкой» | S29 |
| **Toilet / bathroom floor level** | **15–20 mm below** the adjacent rooms, **or a threshold ≤ 20 mm**; same level allowed with full-area waterproofing | 4.8 (Изм. 1, 2, 4) | «…должен быть на 15 - 20 мм ниже уровня пола в смежных помещениях либо полы… должны быть отделены порогом высотой не более 20 мм.» | S29 |
| Where liquids spread | water carried on shoes or wheels reaches 20 m from the wet point (mineral oils 100 m) | 4.4 | «…водой и водными растворами - на 20 м, минеральными маслами и эмульсиями - на 100 м.» | S29 |
| Slip resistance, shod foot, public rooms | Kдоп ≥ 0.35 dry, ≥ 0.4 wet, ≥ 0.5 oily | 5.25 | «по сухим покрытиям полов - не менее 0,35; то же, по влажным - не менее 0,4; то же, по замасленным - не менее 0,5.» | S29 |
| **Minimum screed thickness** (slope screed at drains) | **20 mm** on slabs; **40 mm** on thermal/acoustic layers | 8.2 | «…при укладке ее по плитам перекрытия - 20 мм, по тепло- и звукоизоляционному слою - 40 мм.» | S29 |
| Screed over pipes | ≥ pipe diameter + 45 mm | 8.2 | «Толщина стяжки для укрытия трубопроводов… должна быть не менее чем на 45 мм больше диаметра трубопроводов.» | S29 |
| Screed strength | ≥ B12.5 / M150; under polymer finishes ≥ B15 / M200 | 8.3, 8.4 | «…монолитные стяжки из бетона класса не ниже В12,5… с пределом прочности на сжатие не ниже 15 МПа (марки по прочности М150).» | S29 |
| Self-levelling screed | ≥ 1.5 × the largest aggregate size | 8.7 | «…должна быть не менее 1,5 диаметра максимального наполнителя, содержащегося в композиции.» | S29 |
| Point loads > 20 kN | screed on insulation ≥ 100 mm, ≥ B22.5 | 8.9 | «…приниматься толщиной не менее 100 мм из бетона класса не ниже B22,5.» | S29 |
| **Floor on ground: underlayer thickness** | sand ≥ 60; slag/gravel/crushed stone ≥ 80; **concrete in public buildings ≥ 80 mm** | 9.4 | «…бетонного в жилых и общественных зданиях . . . 80» | S29 |
| Concrete underlayer with no levelling screed | ≥ 120 mm | 9.5 | «…без выравнивающей стяжки его толщина должна составлять не менее 120 мм.» | S29 |
| Rigid underlayer concrete | ≥ B22.5 (Изм. 4) | 9.2 | «Жесткий подстилающий слой бетонный, железобетонный, сталефибробетонный должен выполняться из бетона класса не ниже В22,5.» | S29 |
| Floor on ground: edge insulation | strip ≥ 0.8 m wide along outer walls (when the slab bottom is above, or ≤ 0.5 m below, the apron) | 9.13 | «…следует укладывать по грунту слой шириной не менее 0,8 м из неорганического влагостойкого утеплителя» | S29 |
| Floor on ground: waterproofing | needed in the capillary-rise zone, below the apron level, and with acids | 7.7 | «В полах по грунту гидроизоляция под бетонным подстилающим слоем должна быть предусмотрена: при расположении в зоне опасного капиллярного поднятия грунтовых вод» | S29 |
| Ground under floors | no peat, black soil or soils with E < 5 MPa | 10.2 | «Не допускается применять в качестве основания под полы торф, чернозем и другие растительные грунты, а также слабые грунты с модулем деформации менее 5 МПа.» | S29 |
| **Flatness (2 m straightedge)** | **НЕ НАЙДЕНО in the current СП 29**: 5.18–5.20 deleted by Изм. 1 | 5.18–5.20 | «5.18 - 5.20 Исключены с 16.05.2018. - Изменение N 1» | S29 |
| No steps between boards (timber, parquet, linoleum, laminate) | not allowed | 5.21 | «В полах дощатых, паркетных, из линолеума и ламинированного паркета уступы между смежными изделиями не допускаются.» | S29 |
| Terminal: floor finish in main halls (СП 478) | natural hard stone or other high-strength materials per СП 29 | СП 478 8.5 | «Покрытие полов, облицовку стен и колонн в операционных залах… следует предусматривать из естественного камня твердых пород или из других высокопрочных материалов» | see §9 |

---

## 5. СП 59.13330.2020 «Доступность зданий и сооружений для МГН»

Edition read: **tiflocentre.ru consolidated text "с изменениями № 1-4"**. The amendments are visible in the text:
- Изм. 1: 31.05.2022 № 434/пр
- Изм. 2: 21.11.2023 № 833/пр
- Изм. 3: 19.09.2024 № 630/пр
- Изм. 4: 27.12.2024 № 938/пр

URL **S59** = https://tiflocentre.ru/documents/sp59-13330-2020.php

Caution: this HTML copy renders slopes as "%" where the ratios show per mille is meant (e.g. «1:20 (50%)» means 50 ‰ = 5 %). Use the ratio.

| Rule | Value | Clause | Verbatim quote | URL |
|---|---|---|---|---|
| **Level difference in door openings / thresholds** | **none; where unavoidable, ≤ 0.014 m** | 6.2.4 | «Дверные проемы не должны иметь порогов и перепадов высот пола. При необходимости устройства порогов… их высота или перепад высот не должны превышать 0,014 м.» | S59 |
| Floor-level change inside a building | stairs, ramps or lifts; guard heights per СП 118 | 6.2.8 | «При перепаде высот пола в здании или сооружении следует предусматривать лестницы, пандусы или подъемные устройства, доступные для МГН.» | S59 |
| When a ramp is needed (outdoor stairs) | ramp from 0.014 m up to 6.0 m of rise; platform lift up to 3.0 m; lift from 3.0 m | 5.1.14 (Изм. 1) | «пандусы при перепаде высот от 0,014 м до 6,0 м» | S59 |
| **Ramp: max slope and flight length** (table 5.1) | ≤ 1:12.5 absolute max. Flight ≤ 15 m at 1:33–1:25; ≤ 12 m at 1:25–1:20; ≤ 9 m at 1:20–1:16.7; ≤ 6 m at 1:16–1:12.5 | 5.1.14, табл. 5.1, прим. 1 | «Не допускаются марши пандуса с продольным уклоном более 80% (1:12,5).» | S59 |
| Ramp on general (indoor) routes | slope ≤ 1:20 (5 %) | 6.2.9 | «Ширину марша пандуса на общих путях движения следует принимать согласно 6.2.1, расстояние между поручнями - по ширине пандуса, а уклон - не более 1:20 (5%).» | S59 |
| Ramp landings (indoor) | ≥ 1.5 m along travel, every 0.5 m of rise; 1.5 × 1.5 m at top and bottom | 6.2.9 | «На пандусе при прямом пути движения через каждые 0,5 м подъема должна быть горизонтальная площадка размером не менее 1,5 м по ходу движения.» | S59 |
| One-way ramp width | 0.9–1.0 m between handrails | 6.2.9 | «…с односторонним движением следует принимать в пределах от 0,9 до 1,0 м.» | S59 |
| Ramp edge kerb / handrails | kerb ≥ 0.05 m; handrails at 0.9 and 0.7 m | 6.2.10, 6.2.11 | «Поручни следует располагать на высоте 0,9 м, у пандусов - дополнительно на высоте 0,7 м.» | S59 |
| Outdoor ramp landings | ≥ 1.5 × 1.5 m one-way; 1.8 × 1.5 m two-way | 5.1.16 | «…при движении в одном направлении - ширина - 1,5 м, длина - 1,5 м» | S59 |
| **Slip resistance (paths, ramps, stairs outside)** | longitudinal adhesion 0.6–0.75 kN/kN; ≥ 0.4 in wet or freezing weather | 5.1.11 | «…продольный коэффициент сцепления 0,6 - 0,75 кН/кН, в условиях сырой погоды и отрицательных температур - не менее 0,4 кН/кН.» | S59 |
| Ramp surface | non-slip, contrasting | 5.1.17 | «Поверхность пандуса должна быть нескользкой, выделена цветом или текстурой, контрастной относительно прилегающей поверхности.» | S59 |
| Carpets | pile ≤ 0.013 m, fixed down | 6.2.7 | «…не разрешается применять ворсовые ковры с высотой ворса более 0,013 м.» | S59 |
| **Corridor clear width** | **≥ 1.8 m**; 1.5–1.2 m with 2 m passing pockets; ≥ 1.4 m by calculation (≤ 1 wheelchair user per floor) | 6.2.1 (Изм. 3) | «Ширина путей движения (в коридорах, галереях и т.п.) должна быть не менее 1,8 м» | S59 |
| Corridor clear height | ≥ 2.1 m | 6.2.1 | «Высота проходов по всей их длине и ширине должна составлять в свету не менее 2,1 м.» | S59 |
| Projections from walls on circulation routes | ≤ 0.1 m between 0.7 and 2.1 m above the floor | 6.2.6 | «…не выступать более чем на 0,1 м на высоте от 0,7 до 2,1 м от уровня пола.» | S59 |
| Doorway clear width | ≥ 0.9 m | 6.1.5 / 6.2.4 | «Ширина дверных полотен и открытых проемов в стене… должна быть не менее 0,9 м.» | S59 |

---

## 6. СП 118.13330.2022 «Общественные здания и сооружения»

Edition read: **tiflocentre.ru consolidated text "с изменениями № 1-5"**. The page does not mark which wording is amended (uncertain, see the list below).
URL **S118** = https://tiflocentre.ru/documents/sp-118-13330-2022.php

| Rule | Value | Clause | Verbatim quote | URL |
|---|---|---|---|---|
| **Clear room height** (rooms with permanent or mass occupancy) | **≥ 3 m** floor to ceiling, including a suspended ceiling | 4.26 | «Высоту помещений с постоянным и (или) массовым пребыванием людей в чистоте (от пола до потолка, в том числе подвесного)… следует принимать не менее 3 м» | S118 |
| Allowed reduced clear heights | 2.7 m administrative and office rooms; 2.6 m (≤ 20 % of area); 2.4 m corridors, visitor halls and unoccupied rooms; 2.2 m service corridors and ancillary rooms | 4.27 | «2,7 – в административных и служебных помещениях… 2,4 – в коридорах… 2,2 – в коридорах и помещениях вспомогательного назначения.» | S118 |
| Mezzanines | allowed in rooms ≥ 4.7 m clear; passages under and over them ≥ 2.2 m | 4.26 | «…высота которых в чистоте равна или более 4,7 м, допускается устройство промежуточных уровней или антресолей.» | S118 |
| **Floor-to-floor (storey) height** | **НЕ НАЙДЕНО**: no minimum storey height in the text, only clear room heights | — | — | S118 |
| Entrance platform level | ≥ 0.15 m above the pavement (may be at floor level if protected from rain) | 5.1 | «Отметка площадки перед входом… должна быть выше отметки тротуара перед входом не менее чем на 0,15 м.» | S118 |
| **Guards inside the building** | **≥ 0.9 m** | 6.12 | «Высота ограждений внутри здания, в том числе лестниц и пандусов, должна быть не менее 0,9 м.» | S118 |
| **Guards ≥ 1.2 m** | floor-level difference **> 1.0 m**; gap between flights > 0.3 m; rooms where children may be | 6.12 | «При наличии просвета между маршами… более 0,3 м, перепаде отметок пола более 1,0 м… высота ограждения должна быть не менее 1,2 м.» | S118 |
| External balconies, galleries, terraces, accessible roofs | ≥ 1.2 m | 6.12 | «Высота ограждений наружных балконов, лоджий, галерей… террас, эксплуатируемых кровель должна быть не менее 1,2 м.» | S118 |
| Guard design | continuous, with handrails, ≥ 0.3 kN/m | 6.12 | «Ограждения должны быть непрерывными, оборудованы поручнями и рассчитаны на восприятие нагрузок не менее 0,3 кН/м.» | S118 |
| **0.45 m threshold** | applies only to **porches**: ≥ 3 steps and > 0.45 m above the pavement → guard ≥ 0.9 m | 6.10 | «Высота ограждения крыльца при подъеме на три ступеньки и более и высотой от уровня тротуаров более 0,45 м должна быть не менее 0,9 м.» | S118 |
| Children (incl. retail and leisure buildings with children aged 1–8) | stair guards ≥ 1.2 m; balusters ≤ 0.1 m apart | 6.13 | «…высота ограждений лестниц, используемых детьми, должна быть не менее 1,2 м» | S118 |
| Roof guard on a non-accessible roof (> 10 m) | ≥ 0.6 m (not triggered: 2 storeys) | 6.14 | «Высота ограждений неэксплуатируемых кровель для общественных зданий выше 10 м должна быть не менее 0,6 м» | S118 |
| Enclosing elements (facades, glazing, partitions) | designed per СП 70.13330 and СП 426.1325800 | 6.7 | «…конструкции перегородок и пр.) проектируют по СП 70.13330, СП 426.1325800.» | S118 |

---

## 7. СП 50.13330.2024 «Тепловая защита зданий»

Edition read: **СП 50.13330.2024** (Приказ Минстроя 15.05.2024 № 327/пр; Дата введения 16.06.2024; revision of СП 50.13330.2012). No amendments are listed.
URL **S50** = https://base.garant.ru/409274974/

Climate data (ГСОП of the site) is engineer-only.

| Rule | Value | Clause | Verbatim quote | URL |
|---|---|---|---|---|
| Required R0 | R0норм = R0тр × m_p, with m_p = 1 in this formula (may be lowered only via the specific heat-consumption check) | 5.2 | «В расчете по формуле (5.1) принимается равным 1.» | S50 |
| ГСОП | (t_в − t_от) · z_от, climate data from СП 131.13330 | 5.2, ф. (5.2) | «ГСОП = (t в - t от)z от, (5.2)» | S50 |
| Interpolation formula | R0тр = a·ГСОП + b, with a and b from table 3 | Табл. 3, прим. 1 | «a, b - коэффициенты, значения которых следует принимать по данным настоящей таблицы для соответствующих категорий зданий.» | S50 |
| **Category 2 «Общественные, кроме указанных выше, административные и бытовые» (applies to Ф3.3): walls incl. walls in ground** | **a = 0.0003, b = 1.2** | Табл. 3, кат. 2 | «2 Общественные, кроме указанных выше, административные и бытовые» … «а | 0,0003 | - | - | - | 0,000025» … «b | 1,2 | - | - | - | 0,25» | S50 |
| **Category 2: roofs and floors over passages** | **a, b = "–" (not given)**; table points: 1000→1.5; 2000→2.0; 4000→2.8; 6000→3.4; 8000→3.9; 10000→4.4; 12000→4.8 | Табл. 3, кат. 2, гр. 4 | «Покрытий и перекрытий над проездами» | S50 |
| **Category 2: attic floors, floors over unheated crawl spaces and basements, floors on ground** | **a, b = "–" (not given)**; table points: 1000→1.2; 2000→1.6; 4000→2.2; 6000→2.7; 8000→3.1; 10000→3.5; 12000→3.8 | Табл. 3, кат. 2, гр. 5 | «Перекрытий чердачных, перекрытий над неотапливаемыми подпольями и подвалами, полов по грунту» | S50 |
| Category 2: windows and glazed facades | table points 0.49 … 0.8; a, b "–" | Табл. 3, кат. 2, гр. 6 | (same table) | S50 |
| Different room temperature | multiply by n_t | 5.2 / ф. (5.3) | «…умножаются на коэффициент n t, который рассчитывается по формуле» | S50 |
| **Scope exclusion** | not applicable to temporary buildings in use ≤ 2 heating seasons, or buildings heated less than 3 days/week or seasonally | 1.2 | «…временных зданий, находящихся в эксплуатации не более двух отопительных сезонов» | S50 |
| Glazing inner surface temperature | ≥ 3 °C (non-industrial) | 5.7 | «…должна быть не ниже 3°С, для производственных зданий - не ниже 0°С.» | S50 |
| Design indoor RH, other public rooms | 50 % | 5.7 | «других помещений общественных зданий (за исключением вышеуказанных) - 50%.» | S50 |

---

## 8. СП 51.13330.2011 «Защита от шума»

Edition read: **ред. от 12.12.2023, with Изм. 1 (№ 770/пр), Изм. 2 (№ 953/пр) and Изм. 4 (№ 909/пр, in force 13.01.2024)**. Table 2 is in the Изм. 2 wording.
URL **S51** = https://meganorm.ru/mega_doc/norm/pravila/0/sp_51_13330_2011_svod_pravil_zashchita_ot_shuma.html

| Rule | Rw,req, dB | Lnw,req, dB | Clause | Verbatim quote | URL |
|---|---|---|---|---|---|
| Floors between workrooms and offices, and separating them from public areas (vestibules, halls) | 45 | 63 | 9.2, табл. 2, поз. 20 | «Перекрытия между рабочими комнатами, кабинетами, секретариатами и отделяющие эти помещения от помещений общего пользования (вестибюли, холлы)» | S51 |
| Walls and partitions between offices, and offices vs workrooms | 45 | – | табл. 2, поз. 21 | «Стены и перегородки между кабинетами и отделяющие кабинеты от рабочих комнат» | S51 |
| Walls and partitions between offices of different firms | 48 | – | табл. 2, поз. 22 | «Стены и перегородки между офисами различных фирм, между кабинетами различных фирм» | S51 |

**Station / terminal halls:** НЕ НАЙДЕНО. Table 2 has no row for вокзал or аэровокзал. Only the "Административные здания, офисы" rows above apply, to the staff and office part.

---

## 9. Terminal-specific СП

| Document | Wall/floor rule? | Clause / Verbatim quote | URL |
|---|---|---|---|
| СП 121.13330.2019 «Аэродромы» (Приказ № 64/пр) | **None.** It covers airfield structures only. | 1.1 «…распространяется на вновь строящиеся и реконструируемые сооружения аэродромов (вертодромов).» | https://base.garant.ru/72280786/ |
| **СП 478.1325800.2019 «Здания и комплексы аэровокзальные»** (Приказ № 794/пр, in force 11.06.2020; tiflocentre status "Действующий" 30.10.2026; Изм. 3 was a 2025 draft, adoption not confirmed) | Yes (rows below) | — | https://tiflocentre.ru/documents/sp_478.1325800.2019.php |
| СП 478, scope | new, reconstructed and overhauled terminals; **not seasonal-use buildings** | 1.1/1.2 «…не распространяется на проектирование зданий и сооружений сезонного использования» | same |
| СП 478, Ф3.3 | terminal = Ф3.3 | 9.1.1 (quoted in §2) | same |
| СП 478, degree / С-class | per СП 2.13130 and fire-compartment area | 9.3.1 «Степень огнестойкости и класс конструктивной пожарной опасности зданий аэровокзалов следует предусматривать по СП 2.13130 с учетом площади пожарного отсека.» | same |
| СП 478, baggage-handling zones | enclosure ≥ EI 45, openings EI 30 | 9.4.6 «…ограждающими конструкциями с пределом огнестойкости не менее EI 45 с заполнением проемов с пределом огнестойкости EI 30.» | same |
| СП 478, multi-storey (double-height) halls | separated by ≥ EI 45 | 9.4.7 «Многосветные залы должны отделяться от остальной части здания ограждающими конструкциями с пределом огнестойкости не менее EI 45.» | same |
| СП 478, underground floor with В1/В2 rooms | separating floor ≥ REI 150 (not relevant: no basement assumed) | 9.4.5 «…должны отделяться от надземных перекрытием с пределом огнестойкости не менее REI 150.» | same |
| СП 478, single glazed multi-level hall | spandrels may be omitted inside one room | 9.3.2 (quoted in §2) | same |
| СП 478, finishes | hard stone or high-strength floors and wall cladding in main halls; walls and floors washable and disinfectable | 8.5; 12.4 «Поверхности стен и полов основных помещений должны быть доступными для проведения влажной уборки и дезинфекции.» | same |
| СП 478, impact protection | protect columns, wall corners and door openings where baggage moves | 8.6 «…следует предусматривать защиту колонн, выступов стен и проемов дверей или ворот от повреждения средствами транспорта и механизации.» | same |

---

## НЕ НАЙДЕНО / uncertain

1. **СП 118: minimum floor-to-floor (storey) height** is НЕ НАЙДЕНО. Only clear room heights exist (4.26 / 4.27).
2. **СП 29: floor flatness tolerance (2 m straightedge)** is НЕ НАЙДЕНО in the current text; 5.18–5.20 were deleted by Изм. 1. The tolerance now lives in the works standard (СП 71.13330), which was not read.
3. **СП 29: max level difference between adjacent ordinary rooms** is НЕ НАЙДЕНО. Only the wet-room rule exists (4.8: 15–20 mm lower, or threshold ≤ 20 mm). For accessible routes use СП 59 6.2.4 (≤ 0.014 m).
4. **СП 51: no Rw/Lnw row for station or terminal halls.** Only the offices rows apply.
5. **СП 50 category 2: no a/b for roofs or floors.** Interpolate linearly between the table points; the text gives the formula only where a and b are printed.
6. **СП 118 copy (tiflocentre):** it says "с изм. 1–5" but does not mark amended clauses, and no approval order for Изм. 5 was found. Verify 4.26 / 4.27 / 6.12 against an official or amendment-marked copy.
7. **СП 59 copy (tiflocentre):** slopes are printed as "%" where per mille is meant, and table 5.1's "total length" column is partly garbled (only 110 m and 36 m are legible). Trust the ratios. The landing interval "every 0.5 m of rise" in 6.2.9 is as printed; confirm against an official copy.
8. **СП 2 table 6.9, row V:** this copy prints "С1 - С3"; the С-class column for V should be confirmed on an official copy. The figures 6 m / 1200 / 800 are as printed.
9. **СП 4.13130.2013:** read at ред. 27.06.2023. No later amendment was confirmed (an Изм. 5 draft exists on normacs; adoption not confirmed).
10. **Applicability caveats for a "non-capital, quick-erect" building:**
    - СП 50 does not apply to temporary buildings in use ≤ 2 heating seasons, or to seasonal ones (1.2).
    - СП 478 does not apply to seasonal-use buildings (1.2).
    - The client must state whether the terminal is temporary or seasonal before these two are used.
11. **Not covered here:** СП 1.13130 corridor and evacuation widths, and «пожарно-техническая высота» (which governs the table 6.9 height limit; definition in СП 1.13130).

## Corrections (commonly quoted figures the text contradicts)

1. **"Ф3.3 → table 6.10 of СП 2":** wrong. 6.7.1 sends public buildings to **table 6.9**; table 6.10 is Ф3.5 only and table 6.11 is Ф3.1.
2. **"IV degree: load-bearing R 15 (123-ФЗ table 21)":** for a **2-storey** IV-degree building, СП 2 table 6.9 note 2 requires **≥ R 45**.
3. **"Corridor partitions need EI 45 only in buildings ≥ 28 m; nothing below that":** outdated. Изм. 2 (from 01.01.2026) requires **(R)EI(W) 30** for I–III degree and **(R)EI(W) 15** for IV degree below 28 m, class К0 (5.2.7).
4. **"Type-1 fire wall projects 30 cm beyond the facade (old 5.4.11)":** Изм. 2 rewrote it.
   - Now it must **cut combustible facade materials**, projecting **≥ 0.3 m beyond them**.
   - E 60 / К0 wall strips of total width **≥ 1.5 m** are required (2 m / 3 m for В3–В2 / А, Б, В1).
   - НГ facades may be cut flush, or not cut at all.
   - Old 5.4.12 is deleted.
5. **Fire wall above the roof:** "always 60 cm" is wrong. It is **60 cm if any roof element is Г3/Г4, 30 cm if Г1/Г2, 0 if all НГ** (5.4.10).
6. **Spandrel 1.2 m:** applies only to **I–III degree** buildings with unrated openings. Its rating is the outer-wall E (≤ 6 m² unrated areas) or the floor rating (> 6 m²). It may be made up by projection + spandrel ≥ 1.2 m. One-storey buildings are exempt (5.4.18).
7. **Guard "required from 0.45 m drop":** in СП 118 the 0.45 m figure is only for **porches** (6.10, ≥ 3 steps → ≥ 0.9 m). Inside the building, guards are ≥ 0.9 m, and **≥ 1.2 m only when the floor drop > 1.0 m** (6.12).
8. **"Guard 1.2 m everywhere":** 1.2 m applies to external balconies, galleries, terraces and accessible roofs, to drops > 1.0 m, flight gaps > 0.3 m, and child areas. Otherwise it is **0.9 m** inside.
9. **Wet-room floor "slope 1–2 %" for all finishes:** 4.5 gives **0.5–1 %** for seamless and slab finishes, and **1–2 %** only for brick and concrete.
10. **Bathroom floor "20 mm lower":** text says **15–20 mm lower, or a threshold ≤ 20 mm**. The same level is allowed with full-area waterproofing (4.8, Изм. 2/4).
11. **"Floor flatness 2 mm per 2 m (СП 29 5.18)":** that clause **was deleted** by Изм. 1 (2018); it is no longer in СП 29.
12. **СП 50 a/b for public buildings "roof a = 0.0004, b = 1.6; attic floor a = 0.00035, b = 1.3":** in **СП 50.13330.2024** (the edition read), category 2 prints **"–" for a and b** in those columns. Only walls have a = 0.0003, b = 1.2. The 2012 coefficients were not verified here.
13. **"Ramp max 1:20 with 0.8 m rise per flight":** СП 59.13330.2020 sets it differently.
    - Indoor general routes: ≤ 1:20 (6.2.9), with a landing **every 0.5 m of rise** (as printed).
    - Steeper flights up to **1:12.5** are allowed only with the short flight lengths of table 5.1 (≤ 6 m at 1:16–1:12.5).
14. **Corridor 1.5 m for accessibility:** base value is **1.8 m**. 1.5–1.2 m is allowed only with 2 m passing pockets, and 1.4 m only by calculation (6.2.1, Изм. 3).
