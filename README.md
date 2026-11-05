# Revit agents (Claude Code)

Claude Code agents that work in an open Revit 2025 document, and the rule
sets (skills) they use. They talk to Revit through the [RevitMCPServer](https://github.com/KenLP/RevitMCPServer)
add-in (MIT, by Le Phu); a ready-to-install build of it ships in `revit-mcp/`.

## Agents (`.claude/agents/`)

| Agent | What it does |
|---|---|
| **Revit_Guide** | Front door for a first-time user; turns plain sentences such as "draw a 5-metre wall" into `revit_*` calls and hands the work to the specialist agents below. |
| **Revit_WallFloor** | Draws/fixes/checks walls and floors (overlapping walls, open joins, wall tops not tied to a level…). |
| **Revit_DoorWindow** | Places, moves and checks doors/windows (inside the wall or not, overlaps, sill, swing direction). |
| **Revit_Stair** | Calculates and builds stairs (riser/tread, landing, railing) and checks them against the code. |
| **Revit_Roof** | Builds real FootPrintRoof roofs (hip/gable/shed/flat, eaves) and checks them. |
| **Revit_Drafter** | Sets up sheets, places views, exports them to PDF, has Revit_Sheet review them, and fixes them until the score is > 90. |
| **Revit_Sheet** | Reviews sheet PDFs for graphics (ISO 128 / ГОСТ-СПДС …) and writes a report. Never touches Revit. |
| **Revit_Dynamo** | Writes/fixes Dynamo 3.3 `.dyn` graphs and Python nodes; the user runs them, the agent reads the result. |

Each agent's folder has `scripts/` (calculation scripts) and `Memory/lessons.md`
(learned rules). `Memory/activity_log.md` is kept on each user's own
machine and does not go into the repo.

Skills (`.claude/skills/`): `work-discipline`, `revit-sheet-audit`,
`dynamo-revit-authoring`, `wall-floor-code-check`, `door-window-code-check`,
`stair-code-check`, `roof-code-check`.

## Installation (once)

Requirements: Windows, **Revit 2025.5 or later** (the add-in targets .NET 10),
[Claude Code](https://claude.com/claude-code), [Git](https://git-scm.com),
[Node.js](https://nodejs.org) LTS, Python 3.

1. Clone this repo into a working folder:

   ```bash
   git clone https://github.com/Yagmur-data/RevitAgents.git "Claude Projects"
   ```

2. **Close Revit**, then double-click `revit-mcp\Install.cmd`. It
   - copies the Revit 2025 add-in into `%APPDATA%\Autodesk\Revit\Addins\2025`,
   - installs the MCP server (the bridge between Claude Code and Revit) into
     `%LOCALAPPDATA%\RevitMCPServer` and runs `npm install` there,
   - writes the `revit-2025` server into `.mcp.json` in the working folder
     (an existing `.mcp.json` is backed up and its other servers are kept).

   The add-in in `revit-mcp/` is built from the
   [RevitMCPServer fork](https://github.com/Yagmur-data/RevitMCPServer/tree/revit-agents),
   which adds the tools these agents need (multi-run `create_stair`, the
   `create_roof` fix, `create_railing`, `set_wall_type_layers` …).
   `revit-mcp/VERSION.txt` says which fork commit it is.

3. Open Revit 2025 (a single Revit), open a project, start Claude Code in this
   folder, approve the `revit-2025` server when asked, and type:
   *"Let's start with Revit_Guide"*.

To remove the add-in and the server, run `revit-mcp\uninstall.ps1 -KeepClientConfig`
in PowerShell, then delete the `revit-2025` entry from `.mcp.json`.

### Building the add-in yourself (developers only)

```bash
git clone -b revit-agents https://github.com/Yagmur-data/RevitMCPServer.git "Claude Projects/RevitMCPServer"
```

```bash
dotnet build "Claude Projects/RevitMCPServer/src/RevitAddin/RevitMCPAddin.csproj" -c Release -p:RevitVersion=2025
```

`-p:RevitVersion=2025` is required (the default is 2026). The build copies the
add-in into Revit's add-in folder, so close Revit first. Needs the .NET 10 SDK.

## Updating

```bash
git -C "Claude Projects" pull
```

If the pull changed anything in `revit-mcp/` (a new `VERSION.txt`), close
Revit and run `revit-mcp\Install.cmd` again. If an agent's `lessons.md` has
changed on your own machine, `pull` may ask for a merge; if you don't want to
keep your change, first revert it with `git -C "Claude Projects" checkout -- .claude`.

Note: the agent files (agent definitions, skills, lessons, script indexes) are
kept in English; the agents still answer in the user's language.

## Known traps

[docs/revit-mcp-traps.md](docs/revit-mcp-traps.md) — e.g. an "unauthorized"
error is usually caused by two Revits being open at the same time.
