# -*- coding: utf-8 -*-
# DynamoLink smoke test - READ-ONLY (no transaction, changes nothing in the model).
# Dynamo Python node, CPython3. Proves the Dynamo -> file -> Revit_Dynamo handback loop.
#   IN[0] = output folder (Directory node). Writes <folder>/dynamo_link_test_result.json
#   OUT   = the same dict (shown in the Watch node)
import clr
import io
import os
import json
import datetime
import traceback

clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")
from Autodesk.Revit.DB import FilteredElementCollector, DirectShape
from RevitServices.Persistence import DocumentManager

GRAPH = "dynamo_link_test"
SCHEMA = "dynamolink/1"


def collect(doc):
    by_cat = {}
    for e in FilteredElementCollector(doc).WhereElementIsNotElementType():
        cat = e.Category.Name if e.Category is not None else "(no category)"
        by_cat[cat] = by_cat.get(cat, 0) + 1
    shapes = []
    for e in FilteredElementCollector(doc).OfClass(DirectShape):
        shapes.append({"id": e.Id.Value, "name": e.Name,
                       "application_id": e.ApplicationId,
                       "application_data_id": e.ApplicationDataId})
    view = doc.ActiveView
    return {
        "document_title": doc.Title,
        "document_path": doc.PathName,
        "is_family_document": doc.IsFamilyDocument,
        "revit_version": doc.Application.VersionNumber,
        "revit_build": doc.Application.VersionBuild,
        "active_view": {"name": view.Name, "type": view.ViewType.ToString(), "id": view.Id.Value},
        "element_count": sum(by_cat.values()),
        "elements_by_category_top20": sorted(by_cat.items(), key=lambda kv: -kv[1])[:20],
        "direct_shapes": shapes,
    }


def run():
    out_dir = str(IN[0]).strip().strip('"')
    if not os.path.isdir(out_dir):
        raise ValueError("IN[0] must be an existing folder, got: " + out_dir)
    doc = DocumentManager.Instance.CurrentDBDocument
    if doc is None:
        raise ValueError("No active Revit document - run Dynamo from inside Revit.")
    result = {"schema": SCHEMA, "graph": GRAPH, "status": "ok",
              "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
              "data": collect(doc)}
    path = os.path.join(out_dir, GRAPH + "_result.json")
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(result, ensure_ascii=False, indent=2))
    result["written_to"] = path
    return result


try:
    OUT = run()
except Exception as exc:  # noqa: BLE001 - report instead of silently failing in Dynamo
    OUT = {"schema": SCHEMA, "graph": GRAPH, "status": "error", "message": str(exc),
           "details": traceback.format_exc()}
