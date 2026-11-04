---
name: dyn-file-format
description: The Dynamo 3.3.2 .dyn JSON schema as actually written on this machine — top-level keys, node ConcreteType/NodeType pairs, port and connector shape, View/NodeViews — so graphs can be generated or edited as text without breaking Dynamo.
---

# .dyn file format (Dynamo 3.3.2)

A `.dyn` is plain JSON (UTF-8, read with BOM tolerance). Sources: the user's
`MashProject2.dyn`, `DynamoOption1V4_FIXED.dyn`, and Autodesk's samples in
`...\DynamoForRevit\NodeHelpSharedDocs\*.dyn`. Prefer `dyn_tool.py build/embed`
over hand-editing; this file explains what it emits.

## Top level (all keys present in every file)

`Uuid` (dashed GUID) · `IsCustomNode` (false) · `Description` · `Name` ·
`ElementResolver` (`{"ResolutionMap": {}}`) · `Inputs`/`Outputs` (`[]` unless
the graph is published for Dynamo Player) · `Nodes` · `Connectors` ·
`Dependencies` · `NodeLibraryDependencies` (packages / external files:
`{"Name","ReferenceType":"External","Nodes":[nodeId]}`) ·
`EnableLegacyPolyCurveBehavior` · `Thumbnail` · `GraphDocumentationURL` (null) ·
`ExtensionWorkspaceData` · `Author` · `Linting` · `Bindings` · `View`.

## Identifiers

Node, port and connector `Id`s are 32-hex GUIDs **without dashes**; they must
be unique across the whole file. Only `Uuid` is dashed.

## Ports (every node's `Inputs` / `Outputs` entries)

```json
{"Id": "...", "Name": "IN[0]", "Description": "Input #0", "UsingDefaultValue": false,
 "Level": 2, "UseLevels": false, "KeepListStructure": false}
```

## Node types seen (ConcreteType → NodeType)

| ConcreteType (before the comma) | NodeType | Extra fields |
|---|---|---|
| `PythonNodeModels.PythonNode` | `PythonScriptNode` | `Code`, `Engine` (`"CPython3"`), `VariableInputPorts: true`; inputs named `IN[0]…`, one output named `OUT` |
| `CoreNodeModels.Input.DoubleSlider` | `NumberInputNode` | `NumberType:"Double"`, `MinimumValue`, `MaximumValue`, `StepValue`, `InputValue` |
| `CoreNodeModels.Input.IntegerSlider` | `NumberInputNode` | `NumberType:"Integer"`, same range fields, integer values |
| `CoreNodeModels.Input.DoubleInput` | `NumberInputNode` | `InputValue` |
| `CoreNodeModels.Input.BoolSelector` | `BooleanInputNode` | `InputValue` true/false |
| `CoreNodeModels.Input.StringInput` | `StringInputNode` | `InputValue` |
| `CoreNodeModels.Input.Filename` | `ExtensionNode` | `HintPath`, `InputValue` (relative path allowed, e.g. `.\Footprint.stl`) |
| `CoreNodeModels.Input.Directory` | `ExtensionNode` | `HintPath`, `InputValue` |
| `CoreNodeModels.Watch` | `ExtensionNode` | `WatchWidth`, `WatchHeight` |

All nodes also carry `Replication` (`"Disabled"`) and `Description`. Input
nodes have `"Inputs": []`. Library/Revit nodes (not used by the user's graphs)
use `FunctionSignature` and `NodeType:"FunctionNode"` — take their exact
form from a real sample rather than inventing it.

## Connectors

```json
{"Start": "<output port Id>", "End": "<input port Id>", "Id": "...", "IsHidden": "False"}
```
`IsHidden` is the **string** `"False"`. One connector per input port.

## View

`View.Dynamo` = `{ScaleFactor, HasRunWithoutCrash, IsVisibleInDynamoLibrary,
Version:"3.3.2.11986", RunType:"Manual"|"Automatic", RunPeriod:"1000"}`.
`View.NodeViews[]` = `{Id, Name, IsSetAsInput, IsSetAsOutput, Excluded,
ShowGeometry, X, Y}` — `Name` is the title shown on the canvas (use it for
labels such as `Bridge Width (m)`). Also `Camera`, `ConnectorPins`,
`Annotations`, `X`, `Y`, `Zoom`.

## Line endings

Dynamo 3.3.2 stores the Python `Code` string with LF; scripted graphs may use
CRLF. Both load. `dyn_tool.py embed` preserves whichever the node already uses.
