#!/usr/bin/env python3
"""dyn_tool.py - inspect / validate / extract / embed / extend / build Dynamo 3.x (.dyn) graphs.

Schema source: real Dynamo 3.3.2 files on this machine (MashProject2.dyn,
DynamoOption1V4_FIXED.dyn, and the samples under
C:\\Program Files\\Autodesk\\Revit 2025\\AddIns\\DynamoForRevit\\NodeHelpSharedDocs).
Pure stdlib, no Dynamo/Revit needed - it only edits the JSON text. It can NOT
run a graph; running is done by the user inside Dynamo (see the
dynamo-revit-authoring skill).

  inspect  FILE                          summary: nodes, inputs, python nodes, packages
  validate FILE [FILE ...]               structural + python lint; exit 1 on any ERROR
  extract  FILE --out CODE.py [--node ID]   pull a Python node's code into a .py
  embed    FILE --py CODE.py --out NEW.dyn [--node ID]
                                         copy FILE with a Python node's code replaced;
                                         refuses to overwrite FILE (copy-first rule)
  extend   FILE --out NEW.dyn [--py CODE.py] [--input 'kind|label|value[|min|max|step]' ...]
           [--set 'node label=value' ...] [--name NAME] [--description TXT]
                                         copy FILE; optionally replace the Python code, append new input nodes wired
                                         to NEW ports IN[n]..., change values of existing input nodes (by their canvas
                                         label), rename. Copy-first (refuses --out == FILE), new Uuid, then validates.
  build    --py CODE.py --name NAME --out NEW.dyn
           [--input 'kind|label|value[|min|max|step]' ...] [--no-watch]
           [--description TXT] [--run-type Manual|Automatic]
                                         new graph: input nodes -> CPython3 node -> Watch.
                                         kinds: bool int double string file dir
"""
import argparse
import json
import os
import re
import sys
import uuid

DYNAMO_VERSION = "3.3.2.11986"  # View.Dynamo.Version written by the user's Dynamo
PY_CONCRETE = "PythonNodeModels.PythonNode, PythonNodeModels"
WATCH_CONCRETE = "CoreNodeModels.Watch, CoreNodeModels"
TOP_KEYS = ["Uuid", "IsCustomNode", "Description", "Name", "ElementResolver", "Inputs",
            "Outputs", "Nodes", "Connectors", "Dependencies", "NodeLibraryDependencies",
            "EnableLegacyPolyCurveBehavior", "Thumbnail", "GraphDocumentationURL",
            "ExtensionWorkspaceData", "Author", "Linting", "Bindings", "View"]
# Names removed from the Revit 2025 API (checked against RevitAPI.xml 25.5.0.57 on this
# machine: no T:BuiltInParameterGroup / ParameterType / UnitType / DisplayUnitType).
REMOVED_2025 = ["BuiltInParameterGroup", "ParameterType", "DisplayUnitType"]


def gid():
    return uuid.uuid4().hex


def load(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def save(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def match_eol(code, like=""):
    """Re-encode code's line endings to match `like` (an existing Code string); LF if none.
    Dynamo 3.3.2 on this machine writes Code with LF; some scripted graphs use CRLF."""
    code = code.replace("\r\n", "\n")
    return code.replace("\n", "\r\n") if "\r\n" in like else code


def py_nodes(d):
    return [n for n in d.get("Nodes", []) if "Python" in n.get("ConcreteType", "")]


def port(name, desc):
    return {"Id": gid(), "Name": name, "Description": desc, "UsingDefaultValue": False,
            "Level": 2, "UseLevels": False, "KeepListStructure": False}


# ---------------------------------------------------------------- validate
def validate(path):
    errs, warns = [], []
    try:
        d = load(path)
    except Exception as exc:  # noqa: BLE001
        return [f"not valid JSON: {exc}"], []
    for k in TOP_KEYS:
        if k not in d:
            errs.append(f"missing top-level key '{k}'")
    nodes = d.get("Nodes", [])
    node_ids, out_ports, in_ports, seen_ports = set(), {}, {}, set()
    for n in nodes:
        for k in ("ConcreteType", "Id", "NodeType", "Inputs", "Outputs"):
            if k not in n:
                errs.append(f"node {n.get('Id', '?')[:8]} missing '{k}'")
        nid = n.get("Id")
        if nid in node_ids:
            errs.append(f"duplicate node Id {nid}")
        node_ids.add(nid)
        for side, bag in (("Inputs", in_ports), ("Outputs", out_ports)):
            for p in n.get(side, []):
                if p["Id"] in seen_ports:
                    errs.append(f"duplicate port Id {p['Id']}")
                seen_ports.add(p["Id"])
                bag[p["Id"]] = nid
    fed = set()
    for c in d.get("Connectors", []):
        if c.get("Start") not in out_ports:
            errs.append(f"connector {c.get('Id', '?')[:8]}: Start is not an output port")
        if c.get("End") not in in_ports:
            errs.append(f"connector {c.get('Id', '?')[:8]}: End is not an input port")
        if c.get("End") in fed:
            errs.append(f"input port {c.get('End')[:8]} has more than one connector")
        fed.add(c.get("End"))
    views = {v["Id"] for v in d.get("View", {}).get("NodeViews", [])}
    for v in views - node_ids:
        errs.append(f"NodeView {v[:8]} has no node")
    for nid in node_ids - views:
        warns.append(f"node {str(nid)[:8]} has no NodeView (Dynamo will place it at 0,0)")
    for n in py_nodes(d):
        tag = f"python node {n['Id'][:8]}"
        eng = n.get("Engine")
        if eng != "CPython3":
            errs.append(f"{tag}: Engine is {eng!r}; pin 'CPython3' (no default engine is set on this machine)")
        code = n.get("Code", "")
        try:
            compile(code, "<python node>", "exec")
        except SyntaxError as exc:
            errs.append(f"{tag}: Python syntax error line {exc.lineno}: {exc.msg}")
        if not re.search(r"(^|\n)\s*OUT\s*=", code):
            warns.append(f"{tag}: never assigns OUT")
        names = [p["Name"] for p in n.get("Inputs", [])]
        if names != [f"IN[{i}]" for i in range(len(names))]:
            errs.append(f"{tag}: input ports must be IN[0]..IN[n], got {names}")
        if re.search(r"\.IntegerValue\b", code):
            warns.append(f"{tag}: ElementId.IntegerValue is obsolete - use .Value (Int64)")
        for bad in REMOVED_2025:
            if re.search(r"\b%s\b" % bad, code):
                errs.append(f"{tag}: '{bad}' no longer exists in the Revit 2025 API")
        if re.search(r"(?<![A-Za-z])Transaction\(", code) and "ForceCloseTransaction" not in code:
            warns.append(f"{tag}: opens its own Transaction without TransactionManager.Instance.ForceCloseTransaction()")
        if re.search(r"^\s*print\s+[^(\s=]", code, re.M):
            errs.append(f"{tag}: Python-2 print statement (CPython3 engine)")
    return errs, warns


def cmd_validate(a):
    bad = 0
    for f in a.files:
        errs, warns = validate(f)
        status = "FAIL" if errs else "ok"
        print(f"{status:4}  {f}  ({len(errs)} error, {len(warns)} warning)")
        for e in errs:
            print("   ERROR  ", e)
        for w in warns:
            print("   warning", w)
        bad += bool(errs)
    return 1 if bad else 0


# ---------------------------------------------------------------- inspect
def cmd_inspect(a):
    d = load(a.file)
    v = d.get("View", {}).get("Dynamo", {})
    print(f"Name: {d.get('Name')} | Dynamo {v.get('Version')} | RunType {v.get('RunType')} | Uuid {d.get('Uuid')}")
    print(f"Description: {d.get('Description') or '-'}")
    names = {x["Id"]: x["Name"] for x in d.get("View", {}).get("NodeViews", [])}
    print(f"Nodes: {len(d['Nodes'])}  Connectors: {len(d['Connectors'])}")
    for n in d["Nodes"]:
        extra = ""
        if "InputValue" in n:
            extra = f" = {n['InputValue']!r}"
            if "MinimumValue" in n:
                extra += f" [{n['MinimumValue']}..{n['MaximumValue']} step {n['StepValue']}]"
        if "Python" in n["ConcreteType"]:
            extra = f" engine={n.get('Engine')} code={len(n.get('Code', ''))} chars, ports={len(n['Inputs'])} in"
        print(f"  {n['Id'][:8]}  {n['ConcreteType'].split(',')[0].split('.')[-1]:14} {names.get(n['Id'], '')}{extra}")
    for p in d.get("NodeLibraryDependencies", []):
        print(f"  external/package dependency: {p.get('Name')} ({p.get('ReferenceType')})")
    return 0


# ---------------------------------------------------------------- extract / embed
def pick_py(d, node_id):
    cands = py_nodes(d)
    if node_id:
        cands = [n for n in cands if n["Id"].startswith(node_id)]
    if len(cands) != 1:
        sys.exit(f"expected exactly one python node, found {len(cands)} - pass --node <id prefix>")
    return cands[0]


def cmd_extract(a):
    code = pick_py(load(a.file), a.node).get("Code", "").replace("\r\n", "\n")
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(code)
    print(f"wrote {a.out} ({len(code.splitlines())} lines)")
    return 0


def cmd_embed(a):
    if os.path.abspath(a.out) == os.path.abspath(a.file):
        sys.exit("refusing to overwrite the source graph - pick a different --out (copy-first)")
    d = load(a.file)
    n = pick_py(d, a.node)
    with open(a.py, encoding="utf-8-sig") as fh:
        n["Code"] = match_eol(fh.read(), n.get("Code", ""))
    n["Engine"] = "CPython3"
    save(a.out, d)
    print(f"wrote {a.out}")
    return cmd_validate(argparse.Namespace(files=[a.out]))


def cmd_extend(a):
    if os.path.abspath(a.out) == os.path.abspath(a.file):
        sys.exit("refusing to overwrite the source graph - pick a different --out (copy-first)")
    d = load(a.file)
    n = pick_py(d, a.node)
    if a.py:
        with open(a.py, encoding="utf-8-sig") as fh:
            n["Code"] = match_eol(fh.read(), n.get("Code", ""))
        n["Engine"] = "CPython3"
    views = d["View"]["NodeViews"]
    by_label = {v["Name"]: v["Id"] for v in views}
    by_id = {x["Id"]: x for x in d["Nodes"]}
    for item in a.set or []:
        label, _, val = item.rpartition("=")      # labels may contain "=" (e.g. "... 0 = strict family"); the value is after the LAST "="
        if label not in by_label:
            sys.exit(f"--set: no node labelled {label!r}")
        node = by_id[by_label[label]]
        if "InputValue" not in node:
            sys.exit(f"--set: node {label!r} has no InputValue")
        old = node["InputValue"]
        if isinstance(old, bool):
            new = val.lower() in ("1", "true", "yes")
        elif isinstance(old, int):
            new = int(val)
        elif isinstance(old, float):
            new = float(val)
        else:
            new = val
        node["InputValue"] = new
        if "HintPath" in node:
            node["HintPath"] = val
    start = len(n["Inputs"])
    ymax = max([v.get("Y", 0.0) for v in views] + [0.0])
    for i, spec in enumerate(a.input or []):
        node, label = input_node(spec)
        d["Nodes"].append(node)
        p_ = port(f"IN[{start + i}]", f"Input #{start + i}")
        n["Inputs"].append(p_)
        d["Connectors"].append({"Start": node["Outputs"][0]["Id"], "End": p_["Id"], "Id": gid(), "IsHidden": "False"})
        views.append({"Id": node["Id"], "Name": label, "IsSetAsInput": False, "IsSetAsOutput": False,
                      "Excluded": False, "ShowGeometry": False, "X": 0.0, "Y": ymax + 140.0 * (i + 1)})
    if a.name:
        d["Name"] = a.name
    if a.description:
        d["Description"] = a.description
    d["Uuid"] = str(uuid.uuid4())
    save(a.out, d)
    print(f"wrote {a.out} (python node now has {len(n['Inputs'])} inputs)")
    return cmd_validate(argparse.Namespace(files=[a.out]))


# ---------------------------------------------------------------- build
def input_node(spec):
    parts = spec.split("|")
    if len(parts) < 3:
        sys.exit(f"--input needs 'kind|label|value', got {spec!r}")
    kind, label, value = parts[0], parts[1], parts[2]
    rng = parts[3:6]
    base = {"Id": gid(), "Inputs": [], "Replication": "Disabled"}
    if kind == "bool":
        n = dict(ConcreteType="CoreNodeModels.Input.BoolSelector, CoreNodeModels", NodeType="BooleanInputNode",
                 Outputs=[port("", "Boolean")], Description="Enables selection between True and False",
                 InputValue=value.lower() in ("1", "true", "yes"))
    elif kind in ("int", "double"):
        is_int = kind == "int"
        cast = int if is_int else float
        lo, hi, st = (cast(x) for x in (rng + ["0", "100", "1" if is_int else "0.1"][len(rng):])[:3])
        n = dict(ConcreteType="CoreNodeModels.Input.%sSlider, CoreNodeModels" % ("Integer" if is_int else "Double"),
                 NumberType="Integer" if is_int else "Double", MaximumValue=hi, MinimumValue=lo, StepValue=st,
                 NodeType="NumberInputNode", Outputs=[port("", "Int64" if is_int else "Double")],
                 Description="Produces integer values" if is_int else "Produces numeric values",
                 InputValue=cast(value))
    elif kind == "string":
        n = dict(ConcreteType="CoreNodeModels.Input.StringInput, CoreNodeModels", NodeType="StringInputNode",
                 InputValue=value, Outputs=[port("", "String")], Description="Creates a string")
    elif kind in ("file", "dir"):
        is_file = kind == "file"
        n = dict(ConcreteType="CoreNodeModels.Input.%s, CoreNodeModels" % ("Filename" if is_file else "Directory"),
                 NodeType="ExtensionNode",
                 Outputs=[port("", "Filename" if is_file else "Directory path")],
                 Description=("Allows you to select a file on the system and returns its file path" if is_file
                              else "Allows you to select a directory on the system and returns its path"),
                 HintPath=value, InputValue=value)
    else:
        sys.exit(f"unknown input kind {kind!r} (bool int double string file dir)")
    base.update(n)
    return base, label


def cmd_build(a):
    if not a.input:
        sys.exit("at least one --input is required (a python node with a dangling IN[0] may not run)")
    with open(a.py, encoding="utf-8-sig") as fh:
        code = match_eol(fh.read())
    inputs = [input_node(s) for s in a.input]
    py = {"ConcreteType": PY_CONCRETE, "Code": code, "Engine": "CPython3", "VariableInputPorts": True,
          "Id": gid(), "NodeType": "PythonScriptNode",
          "Inputs": [port(f"IN[{i}]", f"Input #{i}") for i in range(len(inputs))],
          "Outputs": [port("OUT", "Result of the python script")],
          "Replication": "Disabled", "Description": "Runs an embedded Python script."}
    nodes = [n for n, _ in inputs] + [py]
    conns = [{"Start": n["Outputs"][0]["Id"], "End": py["Inputs"][i]["Id"], "Id": gid(), "IsHidden": "False"}
             for i, (n, _) in enumerate(inputs)]
    views = [{"Id": n["Id"], "Name": lbl, "IsSetAsInput": False, "IsSetAsOutput": False, "Excluded": False,
              "ShowGeometry": False, "X": 0.0, "Y": 130.0 * i} for i, (n, lbl) in enumerate(inputs)]
    views.append({"Id": py["Id"], "Name": os.path.splitext(os.path.basename(a.py))[0], "IsSetAsInput": False,
                  "IsSetAsOutput": False, "Excluded": False, "ShowGeometry": True,
                  "X": 560.0, "Y": 130.0 * max(len(inputs) - 1, 0) / 2})
    if not a.no_watch:
        w = {"ConcreteType": WATCH_CONCRETE, "WatchWidth": 320.0, "WatchHeight": 240.0, "Id": gid(),
             "NodeType": "ExtensionNode", "Inputs": [port("", "Node to show output from")],
             "Outputs": [port("", "Node output")], "Replication": "Disabled",
             "Description": "Visualizes a node's output"}
        nodes.append(w)
        conns.append({"Start": py["Outputs"][0]["Id"], "End": w["Inputs"][0]["Id"], "Id": gid(), "IsHidden": "False"})
        views.append({"Id": w["Id"], "Name": "Watch", "IsSetAsInput": False, "IsSetAsOutput": False,
                      "Excluded": False, "ShowGeometry": True, "X": 1000.0, "Y": 0.0})
    d = {"Uuid": str(uuid.uuid4()), "IsCustomNode": False, "Description": a.description, "Name": a.name,
         "ElementResolver": {"ResolutionMap": {}}, "Inputs": [], "Outputs": [], "Nodes": nodes,
         "Connectors": conns, "Dependencies": [], "NodeLibraryDependencies": [],
         "EnableLegacyPolyCurveBehavior": True, "Thumbnail": "", "GraphDocumentationURL": None,
         "ExtensionWorkspaceData": [
             {"ExtensionGuid": "28992e1d-abb9-417f-8b1b-05e053bee670", "Name": "Properties", "Version": "3.3", "Data": {}},
             {"ExtensionGuid": "DFBD9CC0-DB40-457A-939E-8C8555555A9D", "Name": "Generative Design", "Version": "8.2", "Data": {}}],
         "Author": "None provided",
         "Linting": {"activeLinter": "None", "activeLinterId": "7b75fb44-43fd-4631-a878-29f4d5d8399a",
                     "warningCount": 0, "errorCount": 0},
         "Bindings": [],
         "View": {"Dynamo": {"ScaleFactor": 1.0, "HasRunWithoutCrash": False, "IsVisibleInDynamoLibrary": True,
                             "Version": DYNAMO_VERSION, "RunType": a.run_type, "RunPeriod": "1000"},
                  "Camera": {"Name": "_Background Preview", "EyeX": -17.0, "EyeY": 24.0, "EyeZ": 50.0,
                             "LookX": 12.0, "LookY": -13.0, "LookZ": -58.0, "UpX": 0.0, "UpY": 1.0, "UpZ": 0.0},
                  "ConnectorPins": [], "NodeViews": views, "Annotations": [], "X": 0.0, "Y": 0.0, "Zoom": 0.8}}
    if os.path.exists(a.out) and not a.force:
        sys.exit(f"{a.out} exists - pass --force to replace a graph this tool built, or pick a new name")
    save(a.out, d)
    print(f"wrote {a.out}")
    return cmd_validate(argparse.Namespace(files=[a.out]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inspect"); p.add_argument("file"); p.set_defaults(fn=cmd_inspect)
    p = sub.add_parser("validate"); p.add_argument("files", nargs="+"); p.set_defaults(fn=cmd_validate)
    p = sub.add_parser("extract"); p.add_argument("file"); p.add_argument("--out", required=True)
    p.add_argument("--node"); p.set_defaults(fn=cmd_extract)
    p = sub.add_parser("embed"); p.add_argument("file"); p.add_argument("--py", required=True)
    p.add_argument("--out", required=True); p.add_argument("--node"); p.set_defaults(fn=cmd_embed)
    p = sub.add_parser("extend"); p.add_argument("file"); p.add_argument("--out", required=True)
    p.add_argument("--py"); p.add_argument("--node"); p.add_argument("--input", action="append")
    p.add_argument("--set", action="append"); p.add_argument("--name"); p.add_argument("--description")
    p.set_defaults(fn=cmd_extend)
    p = sub.add_parser("build"); p.add_argument("--py", required=True); p.add_argument("--name", required=True)
    p.add_argument("--out", required=True); p.add_argument("--input", action="append")
    p.add_argument("--no-watch", action="store_true"); p.add_argument("--description", default="")
    p.add_argument("--run-type", default="Manual", choices=["Manual", "Automatic"])
    p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_build)
    a = ap.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
