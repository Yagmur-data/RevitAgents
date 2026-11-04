---
name: dynamo-revit-authoring
description: How to author, edit, validate and hand off Dynamo for Revit 3.3 (.dyn) graphs and CPython3 Python nodes for an open Revit 2025 document — the real .dyn JSON schema, this workspace's graph conventions (dry-run toggle, idempotent DirectShape keys, result JSON handback), Revit 2025 API traps verified against the installed RevitAPI, and the honest limits of "connecting" to Dynamo (no live bridge — file handoff only). Used by the Revit_Dynamo agent.
---

# dynamo-revit-authoring

All notes added to this skill must be written in English.

Facts below were checked on this machine on 2026-10-02: Dynamo for Revit
**3.3.2** (`C:\Program Files\Autodesk\Revit 2025\AddIns\DynamoForRevit`,
`DynamoRevitDS.dll` 3.3.2.12194), Revit **2025.5** (`RevitAPI.dll`
25.5.0.57). Re-check with the commands in §6 if the install changes.

## 1. What "connected to Dynamo" really means here

There is **no live bridge**. The `revit_*` MCP tools talk to Revit through the
RevitMCP add-in (TCP 7891); that add-in has no Dynamo command. No
`DynamoCLI`/`DynamoSandbox`/`DynamoPlayer` binaries exist in the Revit 2025
add-in folder, so graphs cannot be run headlessly from here. The link is a
**file handoff with a read-back**:

```
Revit_Dynamo                      the user (in Revit)
 1 read the live model (revit_*)
 2 write ForDynamo/<job>/<graph>.dyn  (+ readable .py copy), validate
 3 give exact run steps ───────────►  4 Manage ▸ Dynamo ▸ Open the .dyn
                                      5 run DRY-RUN (toggle False), read report
 7 read <graph>_result.json ◄───────  6 (after OK) toggle True, run
 8 verify against the live model (revit_*) — never trust the graph's own report alone
```

Never say a graph "ran", "worked" or "created N elements" unless step 7/8
evidence exists. If the user wants zero-touch execution, that is a developer
task on `RevitMCPServer` (a new `revit_run_dynamo` command; Dynamo for Revit
supports journal-driven runs — the journal-data keys, e.g. `dynPath`,
`dynShowUI`, `dynAutomation`, are from memory and **unverified here**). State
that plainly; do not attempt it from this agent.

## 2. Workspace conventions (taken from the user's own graphs)

`MashProject2/3.dyn` and `DynamoOption1V4_FIXED.dyn` share a house style —
follow it so new graphs feel familiar:

1. **One CPython3 Python node** holds the logic (`"Engine": "CPython3"` —
   `DefaultPythonEngine` is unset in `DynamoSettings.xml`, so always pin it).
   Dynamo nodes only for inputs and a Watch on the output.
2. **Inputs as nodes, not literals**: `DoubleSlider`/`IntegerSlider` for numbers
   (unit in the label, e.g. `Bridge Width (m)`), `Filename`/`Directory` for
   paths, `BoolSelector` for toggles. Python reads `IN[i]` in port order.
3. **Dry-run toggle**: any graph that writes to the model takes a Boolean
   (`IN[0]` in the user's V4 graph: "Set IN[0] True to create/update").
   False ⇒ compute and report only. First run is always False.
4. **Idempotent by key**: elements the graph owns are found by
   `DirectShape.ApplicationId` + `ApplicationDataId` (MashProject2:
   `'Dynamo.STL.GaussShell'` + `'GAUSS_KABUK_01'`), replaced in place on re-run
   (`SetShape`), never duplicated. More than one match ⇒ stop with an error.
5. **Transactions**: `TransactionManager.Instance.EnsureInTransaction(doc)` +
   `SubTransaction` + `TransactionTaskDone()` (MashProject2), or
   `ForceCloseTransaction()` before a hand-rolled `Transaction` (V4 graph).
   Roll back on any exception; a half-written shape must never be saved
   (MashProject2 aborts if Revit changes the triangle count).
6. **Units**: sliders are in metres; convert once with
   `UnitUtils.ConvertToInternalUnits(1.0, UnitTypeId.Meters)`. Revit's internal
   unit is feet — never hand a metre/mm number to a Revit API call unconverted.
7. **Never crash silently**: wrap the whole script in `try/except` and set
   `OUT` to `{"Status": "ERROR", "Message": ..., "Details": traceback}` (V4
   graph). Success returns a dict (`Status`, `Element ID`, counts, `Units`).
8. **RunType Manual** for anything that writes.
9. **Handback**: also write the same dict to
   `ForDynamo/<job>/<graph>_result.json` (`schema: "dynamolink/1"`, `graph`,
   `status`, `timestamp`, `data`) so the agent can read it. See
   `scripts/link_test.py` for the reference implementation.

## 3. Method

1. **Intent first.** Which job, new graph or change to an existing one, what
   must the model look like afterwards? One question if a wrong guess is costly.
2. **Ground in the live model** (read-only `revit_*`): categories present,
   parameter names, levels, existing DirectShape keys (`revit_get_element_info`
   shows `ApplicationId`/key only indirectly — see lessons). Do not hard-code
   ElementIds read from the live session into a graph; select by category,
   name, or key so the graph survives reopening the file.
3. **Copy-first.** Never overwrite a user `.dyn`. Work on
   `ForDynamo/<job>/<name>_vN.dyn`. For an existing graph:
   `dyn_tool.py extract` → edit the `.py` → `dyn_tool.py embed --out <new>`.
   Change only what the request names; leave sliders, layout, other nodes alone.
4. **Validate** every produced graph with `dyn_tool.py validate` (errors block
   handoff; explain warnings). Also keep the `.py` next to the `.dyn` so diffs
   are reviewable.
5. **Handoff text** to the user: file path, the exact click path (Revit ▸
   Manage ▸ Dynamo ▸ Open), which inputs to set, "run with toggle False first",
   what the report should look like, where `_result.json` will appear, and
   "save a copy of the .rvt first if the run deletes/replaces elements".
6. **Read back & verify**: read `_result.json`, then re-query the model with
   `revit_*` (counts, ids, bbox, parameters) and compare. Report mismatches.

## 4. Revit 2025 API traps (verified in `RevitAPI.xml` 25.5.0.57)

- `ElementId.Value` (Int64) exists; `ElementId.IntegerValue` still exists but
  is obsolete — write `.Value`. `ElementId(int)` and `ElementId(long)` ctors
  both exist.
- **Gone in 2025**: `BuiltInParameterGroup`, `ParameterType`, `UnitType`,
  `DisplayUnitType`. Use `GroupTypeId`, `SpecTypeId`, `UnitTypeId`.
  `dyn_tool.py validate` flags these.
- Internal length unit = feet (see §2.6).
- Python-node Dynamo-wrapped elements: `UnwrapElement(IN[i])` before touching
  the Revit API; `.ToDSType(True)` / `.InternalElement` to go back.
- Read parameters via `LookupParameter(name)`/`get_Parameter(BuiltInParameter)`;
  check `IsReadOnly` and `StorageType` before `.Set(...)`; shared/instance vs
  type duplicates exist (the MCP `get_element_info` listing repeats names).
- Detail of the Python template, imports, DirectShape/Tessellated pattern:
  `references/python-node-revit-2025.md`.

## 5. Scope boundaries

Graphics-sheet composition → `Revit_Drafter`; sheet PDF QA → `Revit_Sheet`;
direct modelling and a first-time user's plain-language requests →
`Revit_Guide`; changing the RevitMCP add-in (including a Dynamo runner) →
developer session. This skill is for the Dynamo graph itself.

## 6. Re-verify the environment

```
(Get-Item 'C:\Program Files\Autodesk\Revit 2025\AddIns\DynamoForRevit\Revit\DynamoRevitDS.dll').VersionInfo.FileVersion
(Get-Item 'C:\Program Files\Autodesk\Revit 2025\RevitAPI.dll').VersionInfo.FileVersion
Get-ChildItem "$env:APPDATA\Dynamo\Dynamo Revit\3.3\packages"      # installed packages (empty on 2026-10-02)
```

## Files

- `references/dyn-file-format.md` — the .dyn JSON schema as Dynamo 3.3.2 writes it.
- `references/python-node-revit-2025.md` — Python node template and patterns.
- Tooling: `.claude/agents/Revit_Dynamo/scripts/dyn_tool.py`.
