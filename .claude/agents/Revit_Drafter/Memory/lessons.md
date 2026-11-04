---
name: Revit_Drafter lessons
description: Curated, rule-form corrections distilled from activity_log.md — read this before every drafting job, not just the raw log. One durable rule per line.
---

# Revit_Drafter — lessons

Each line is one standing rule, stated as a concrete instruction, promoted
here from the activity log once it's proven worth remembering permanently.
Don't duplicate the chronological log here — only the distilled rule.

- Modeled on `C3D_Drafter` / `Arch_Reviewer` (found in `Desktop/claude.zip`,
  2026-09-29), with one structural difference: Civil3D's "always work on a
  QA-/QAx- copy, never touch the original" rule has no Revit equivalent —
  there is no exposed save-as-copy tool, and the live document IS the
  working copy. Compensate with extra care (rule 3 in Revit_Drafter.md):
  surgical, traceable edits only, and the completion report must say the
  changes are live and still need the user's own save/sync.
- (2026-10-01) The `revit-sheet-audit` skill is now installed — draft to
  its six categories/R1-R12/scoring from the first pass (rule 5), not the
  inline baseline (that's fallback-only now). The skill deliberately keeps
  real standard families (TS EN ISO 128 default / BS EN ISO 128 / US
  NCS-AIA) separate rather than blending them into one standard-independent
  principle set — ask which family applies per its §1, don't assume.
- (2026-11-04) A sheet list cannot be built as a schedule on a sheet through the bridge: create_schedule refuses OST_Sheets and place_view_on_sheet fails on schedules -> use text notes (and say so). Room tags have no readable position, so moves are blind: always re-render the plan with get_view_image. Viewport title text wraps at about 26 characters; keep titles short or the 2nd line hits the scale text.
- (2026-11-04) A RoomTag moved outside its own room turns into "?" (Leader Line = Yes does not help) - keep every tag anchored inside its room; narrow rooms cannot be fixed by moving. get_tags_in_view gives exact positions (m, origin axis 1/A) for door tags only; room tags are found via find_elements OST_RoomTags (id order = room number order). create_aligned_dimension takes Level ids as references in sections.
