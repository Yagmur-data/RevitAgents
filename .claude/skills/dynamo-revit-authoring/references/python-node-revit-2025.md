---
name: python-node-revit-2025
description: Reference patterns for a CPython3 Dynamo Python node that reads or writes the open Revit 2025 document — imports, document access, transactions, DirectShape upsert by key, unit conversion, result JSON — distilled from the user's working MashProject2 and DynamoOption1V4 graphs.
---

# CPython3 Python node for Revit 2025

Patterns here are lifted from graphs that already run on this machine; the
read-only skeleton is `.claude/agents/Revit_Dynamo/scripts/link_test.py`.

## Imports and document

```python
import clr
clr.AddReference("RevitAPI"); clr.AddReference("RevitAPIUI"); clr.AddReference("RevitServices")
from Autodesk.Revit.DB import *            # or import names explicitly, as the user's graphs do
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument
if doc is None or doc.IsFamilyDocument:
    raise ValueError("Open a Revit project (.rvt) and run Dynamo from Revit.")
```
`IN[i]` / `OUT` are injected by Dynamo. Typed .NET collections:
`from System.Collections.Generic import List` → `List[ElementId]()`;
`from System import Array` → `Array[GeometryObject](items)`.

## Read-only work

No transaction. `FilteredElementCollector(doc).OfClass(...)`,
`.OfCategory(BuiltInCategory.OST_...)`, `.WhereElementIsNotElementType()`;
scope to the view with `FilteredElementCollector(doc, view.Id)`.

## Writing

```python
TransactionManager.Instance.ForceCloseTransaction()      # if you open your own Transaction
tx = Transaction(doc, "Job name"); tx.Start()
try:
    ...
    tx.Commit()
except Exception:
    if tx.HasStarted(): tx.RollBack()
    raise
```
or, as MashProject2 does: `TransactionManager.Instance.EnsureInTransaction(doc)` →
`SubTransaction(doc).Start()/Commit()/RollBack()` → `TransactionManager.Instance.TransactionTaskDone()`
in `finally`.

## DirectShape upsert by key (idempotent re-run)

```python
APP_ID, KEY = "Dynamo.STL.GaussShell", "GAUSS_KABUK_01"
found = [e for e in FilteredElementCollector(doc).OfClass(DirectShape)
         if e.ApplicationId == APP_ID and e.ApplicationDataId == KEY]
if len(found) > 1: raise ValueError("Duplicate keyed elements - inspect before re-running.")
ds = found[0] if found else DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
ds.ApplicationId, ds.ApplicationDataId, ds.Name = APP_ID, KEY, KEY
ds.SetShape(Array[GeometryObject](geometry))
```
Build `geometry` with `TessellatedShapeBuilder` (user graph: target Mesh, fallback
Salvage, then **verify the triangle count survived** before committing).
To replace/extend the user's existing shell graph, reuse its exact APP_ID/KEY
or you will create a second element next to `GAUSS_KABUK_01`.

## Units

`f = UnitUtils.ConvertToInternalUnits(1.0, UnitTypeId.Meters)` once, multiply
all metre inputs by `f`. The V4 graph exposes `COORD_UNIT` ("m"/"cm"/"mm"/"ft")
via a units dict of `UnitTypeId.*`.

## Parameters

```python
p = elem.LookupParameter("Mark")
if p is not None and not p.IsReadOnly and p.StorageType == StorageType.String:
    p.Set("value")
```
Writes need an open transaction. Report what was skipped (missing/read-only)
instead of failing the whole batch.

## Output and handback

`OUT = {"Status": "...", ...}` for the Watch node, plus a
`<graph>_result.json` (`dynamolink/1`) written with `io.open(..., encoding="utf-8")`
and `ensure_ascii=False` so Turkish text survives.

## Don'ts

`BuiltInParameterGroup`/`ParameterType`/`UnitType`/`DisplayUnitType`
(removed in 2025) · `ElementId.IntegerValue` · Python 2 syntax · IronPython
imports · assuming Dynamo's own geometry units equal feet · long-running
external processes without a timeout (MashProject2 uses a 600 s cap and a
temp folder it cleans up).
