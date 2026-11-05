# Revit agents — project notes

This folder is a clone of https://github.com/Yagmur-data/RevitAgents: Claude
Code agents that work in an open **Revit 2025** document through the Revit MCP
add-in (tools named `mcp__revit-2025__*`). Setup steps are in `README.md`.

## Agents (`.claude/agents/`)

Route Revit work to the matching agent; a first-time or unsure user starts
with **Revit_Guide**, which hands work to the others.

- **Revit_Guide** — plain-language front door; turns "draw a 5 m wall" into `revit_*` calls.
- **Revit_WallFloor** — walls and floors: draw, fix, check.
- **Revit_DoorWindow** — doors and windows: place, move, check.
- **Revit_Stair** — stairs: calculate, build, check.
- **Revit_Roof** — roofs: hip/gable/shed/flat, eaves, check.
- **Revit_Drafter** — sheets: compose, export PDF, fix until Revit_Sheet scores > 90.
- **Revit_Sheet** — reviews sheet PDFs for graphics; never touches Revit.
- **Revit_Dynamo** — writes/fixes Dynamo `.dyn` graphs; the user runs them.

Agent files are kept in English; answer the user in their language.

## Is the Revit connection set up?

If no `mcp__revit-2025__*` tools are available in this session:

1. **No `revit-2025` entry in `.mcp.json` here** → the add-in is not installed.
   Offer to install it: the user closes Revit, then run
   `powershell -NoProfile -ExecutionPolicy Bypass -File revit-mcp\install-claude-code.ps1`
   from this folder (needs Node.js 18+; it copies the add-in, installs the MCP
   server and writes `.mcp.json`). Show any failure to the user.
2. **The entry exists** → the session started before it was written. Tell the
   user to close Claude Code, open it again in this folder and approve the
   `revit-2025` server.

If the tools exist but `revit_ping` fails: "fetch failed" → Revit 2025 is not
open (or has no project open); "unauthorized" → two Revits are open — close
all, open one. More in `docs/revit-mcp-traps.md`.

## Updates

`git pull` in this folder. If `revit-mcp/VERSION.txt` changed, the add-in
changed: with Revit closed, run the installer from step 1 again, then restart
Claude Code. Changes the agents make to their own `Memory/lessons.md` stay on
this machine; don't commit or push them unless the user maintains the repo.
