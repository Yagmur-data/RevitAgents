---
name: Revit_Sheet lessons
description: Curated, rule-form corrections distilled from activity_log.md — read this before every audit run, not just the raw log. One durable rule per line.
---

# Revit_Sheet — lessons

Each line is one standing rule, stated as a concrete instruction, promoted
here from the activity log once it's proven worth remembering permanently.
Don't duplicate the chronological log here — only the distilled rule.

- (2026-10-01) The `revit-sheet-audit` skill is now installed at
  `.claude/skills/revit-sheet-audit/SKILL.md` + `references/*.md` — built
  from real named standards (ISO 128/TS EN ISO 128 default, BS EN ISO 128,
  US NCS/AIA) the user supplied plus web research (ISO 5457/7200, ISO 129,
  ISO 3098, ISO 7519, ISO 19650/BS 1192). It is now the primary rubric; the
  inline baseline in Revit_Sheet.md rules 3-5a is fallback-only (skill
  missing/deleted case) — don't treat it as equivalent, and say so in the
  report if it's ever actually used.
- (2026-09-29, superseded) Originally this agent held live `mcp__revit-2025`
  tools and a `Task` tool to delegate fixes to Revit_Guide. Rebuilt to match
  the `C3D_Drafter` / `Arch_Reviewer` split found in the user's
  `Desktop/claude.zip`: this agent is now the pure reviewer (PDF-only, no
  Revit connection, no `Task`, never edits anything) and `Revit_Drafter` is
  the one that composes sheets, calls this agent, and implements every fix
  itself. If a task seems to need a live Revit connection or a model edit,
  that request belongs to `Revit_Drafter` (or `Revit_Guide`), not this
  agent.
- `Desktop/claude.zip` is a full backup of the "Claudeworks" workspace this
  log's earlier entries (HR's own history) describe — `C3D_Drafter.md`,
  `Arch_Reviewer.md`, `arch-graphics-review` skill, `work-discipline` skill
  all live there. Worth checking before reinventing a pattern HR has
  already built once.
- (2026-11-04) On re-reviews print the raw (unfloored) score beside the floored one — when the stamp rows alone cost 76 points every sheet shows 0 and progress is invisible.
- (2026-11-04) When the Drafter adds a ledger/schedule with new marks, read the tag TEXT on the plans (get_text dict) and compare to the ledger marks — a tag can show Type Mark while the ledger lists instance Mark; also verify the ledger counts per level against the tag counts.
