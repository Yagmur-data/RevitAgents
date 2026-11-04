---
name: roof-code-check — airport terminal & hangar module
description: Extra roof rules applied on top of SKILL.md §3 when the building is an airport terminal or an aircraft hangar — obstacle limitation surfaces (ICAO Annex 14 / STANAG 7174), Class A roof covering, NFPA 415 / NFPA 409, ASCE 7 / IBC 1609 wind uplift and edge systems, acoustics, smoke control, lightning protection, closed drainage and wildlife hazard. Supplied by Al 2026-10-21.
---

# Airport terminal & hangar module

Apply **in addition to** SKILL.md §3 (R1–R12) when the user says, or the
project makes clear, that the building is an airport **terminal** or an
aircraft **hangar** — and **only** when the project's Word document names no
standards of its own (SKILL.md §0). If it does, this module is not added. Basis tag in the report header:
`IBC 2024 + airport module (supplied 2026-10-21)`. Same family rule as
SKILL.md §1: these are ICAO / NATO / US (NFPA, ASCE, ANSI/SPRI, FM) documents;
a Russian (СП) or Turkish (TS/EN, SHGM) airport project needs its own
figures — ask, don't substitute these.

Source: Al's pasted summary (2026-10-21), citation markers without a source
list, so **supplied, not independently verified**. Three references in it
were corrected by HR — see §3; the report must not repeat the uncorrected
ones.

## 1. Before building — ask once, in one message

1. **Terminal or hangar?** (Civil or military airfield? — STANAG 7174
   only applies to military/NATO fields.)
2. **OLS limit**: the highest allowed absolute elevation (m AMSL) over the
   roof's footprint, from the aerodrome's obstacle limitation surface
   drawing — and the **absolute elevation of the level** the roof sits on
   (Revit levels are relative to the project base point). Without both, A1
   is KONTROL EDİLEMEDİ, never assumed fine.

## 2. Rules

| ID | Rule (supplied basis) | Check with | On fail |
|---|---|---|---|
| **A1 OLS / height limit** | Terminal and hangar roofs near runways and approach/take-off corridors must not penetrate the Obstacle Limitation Surfaces (ICAO Annex 14; STANAG 7174 on military fields). **Every** rooftop element counts: parapets, mechanical equipment, antennas. | Before build: predicted top = eave elevation + (half span × tan slope) for gable/hip, or eave elevation + (full span × tan slope) for a shed; add the roof type's thickness. After build: roof bounding-box max, then also the highest wall top (parapet) and any rooftop element found on the roof (R11). Convert to absolute with the level's absolute elevation. | Predicted top above the limit → **BLOCK** (offer a lower slope or a different form that fits, and give the clearance). Parapet/equipment above the limit after build → **FLAG** with the exceedance in metres. |
| **A2 Roof fire class** | Terminal roof covering and insulation assemblies: **Class A** (UL 790 / ASTM E108), non-combustible or limited-combustible materials. | R5 check, now with a required value: the roof type's "Fire Rating" must declare Class A. | Declares B/C → **UYGUN DEĞİL** (FLAG; type change is the user's call). Empty → KONTROL EDİLEMEDİ. |
| **A3 NFPA 415 / NFPA 409** | Terminal roofs and loading-walkway (jet bridge) connections per NFPA 415; hangar roof construction with NFPA 409 foam/water suppression and fire barriers integrated. | — | **MÜHENDİS** always (fire engineer / sprinkler designer). |
| **A4 Wind uplift & roof edges** | Wide clear-span roofs on exposed airfields: uplift calculation per ASCE 7 and IBC 1609; edge systems tested to ANSI/SPRI ES-1 or FM 4435; parapet heights as the wind design needs. | Report measured parapet height (R4 measurement) so the engineer has it. | **MÜHENDİS** always; never claim a parapet height "satisfies wind". |
| **A5 Acoustics** | Roof build-up and ceiling junctions attenuate jet/apron noise: high sound-transmission-loss build-up with acoustic membranes/insulation (see §3 on NRC vs STC/Rw). | Roof type layers (R8 method): is there an identifiable acoustic layer/membrane? | None identifiable → **FLAG**; the attenuation value itself → **MÜHENDİS** (acoustic consultant). |
| **A6 Smoke control** | Smoke barriers, dampers at roof/ceiling junctions and mechanical smoke exhaust vents so smoke does not spread through the terminal. | — | **MÜHENDİS**; combine with R7 in the report. |
| **A7 Rooftop structures** | Mechanical screens and penthouses: non-combustible, within height and area limits — and inside the OLS (A1). | R11 elements on the roof feed A1's height check. | Height → A1; materials/area → **MÜHENDİS**. |
| **A8 Lightning protection** | Metal edge systems, gutters and roof coverings bonded into the lightning protection system (see §3 for the standard). | — | **MÜHENDİS** (electrical). |
| **A9 Closed drainage & wildlife hazard** | Low-slope roofs: primary + overflow drainage (R6), with rainwater taken away in **closed pipes** — no open ponds or standing water near the apron or approach corridors that attract birds. | R1 (no ponding) and R6 (drains present). On an airport, a flat roof whose falls are not modeled is reported with this risk named. | Missing drains → **FLAG — kuş riski (açık su birikmesi) dahil**; site drainage routing → **MÜHENDİS**. |

## 3. Corrections HR made to the supplied text

Recorded so a later session doesn't "fix" them back:

- **Class A test standard.** The text says "Class A … ASTM E84 or UL 790".
  ASTM E84 is the surface-burning (flame spread / smoke developed) test for
  materials and interior finishes, not the external roof fire test. The
  roof covering class comes from **UL 790 / ASTM E108**; E84 may still apply
  to individual insulation/finish materials. Report A2 against UL 790 /
  ASTM E108.
- **"Ceiling radiation dampers" ≠ smoke dampers.** Ceiling radiation
  dampers protect openings in fire-resistance-rated floor/roof–ceiling
  assemblies against radiant heat; they are not smoke-control devices.
  A6 keeps "smoke dampers / smoke barriers / exhaust vents" and lists
  ceiling radiation dampers separately, if at all.
- **NRC is not sound transmission loss.** NRC ≥ 0.65 is an absorption
  rating (how much sound an interior surface soaks up). Keeping apron noise
  out is transmission loss (STC / Rw, or an indoor dBA limit). A5 reports
  the build-up's layers; the target value is the acoustic consultant's.
- **ANSI/SPRI GT-1 is the gutter-system test standard**, not a lightning
  protection standard. Gutters/edges are tested to GT-1 / ES-1; lightning
  protection is designed to NFPA 780 (US) or IEC 62305 / TS EN 62305.
  A8 names those.

## 4. Report

Same table as SKILL.md §4. Put A1 first (it is the only airport rule that
can stop a build) with the numbers: `limit … m AMSL / roof top … m AMSL /
clearance … m`. Group A3, A4, A6, A8 on one MÜHENDİS line.
