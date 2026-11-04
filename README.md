# Revit agents (Claude Code)

Claude Code agents that work in an open Revit 2025 document, and the rule
sets (skills) they use. They talk to Revit through the [RevitMCPServer](https://github.com/KenLP/RevitMCPServer)
add-in.

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

Requirements: Windows, Revit 2025, [Claude Code](https://claude.com/claude-code),
Git, Node.js, .NET SDK 10, Python 3.

1. Clone this repo into a working folder:

   ```bash
   git clone https://github.com/Yagmur-data/RevitAgents.git "Claude Projects"
   ```

2. The tools the agents need (multi-run `create_stair`, the `create_roof`
   fix, `create_railing`, `set_wall_type_layers` …) live in RevitMCPServer's
   **fork**. Clone it inside the same folder:

   ```bash
   git clone -b revit-agents https://github.com/Yagmur-data/RevitMCPServer.git "Claude Projects/RevitMCPServer"
   ```

3. Build the add-in and the MCP server (**with Revit closed** — the build copies
   the add-in into `%APPDATA%\Autodesk\Revit\Addins\2025`):

   ```bash
   dotnet build "Claude Projects/RevitMCPServer/src/RevitAddin/RevitMCPAddin.csproj" -c Release -p:RevitVersion=2025
   ```

   ```bash
   cd "Claude Projects/RevitMCPServer/src/McpServer" && npm install && npm run build
   ```

   `-p:RevitVersion=2025` is required; the default is 2026. For Revit 2025 the
   fork targets .NET 10 (Revit **2025.5** and later); on an older 2025
   update the build/load fails — update Revit first.

4. Copy `.mcp.example.json` to `.mcp.json` and replace the path in it
   with your own `RevitMCPServer\src\McpServer\dist\index.js` path.

5. Open Revit 2025 (a single Revit), open a project, start Claude Code in this
   folder and type: *"Let's start with Revit_Guide"*.

## Updating

```bash
git -C "Claude Projects" pull
```

```bash
git -C "Claude Projects/RevitMCPServer" pull
```

If RevitMCPServer has changed, run the build from step 3 again (with Revit
closed). If an agent's `lessons.md` has changed on your own machine, `pull`
may ask for a merge; if you don't want to keep your change, first revert it
with `git -C "Claude Projects" checkout -- .claude`.

Note: the agent files (agent definitions, skills, lessons, script indexes) are
kept in English; the agents still answer in the user's language.

## Known traps

[docs/revit-mcp-traps.md](docs/revit-mcp-traps.md) — e.g. an "unauthorized"
error is usually caused by two Revits being open at the same time.
