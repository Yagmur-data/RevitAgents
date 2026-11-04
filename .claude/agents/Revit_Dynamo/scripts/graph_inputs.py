# -*- coding: utf-8 -*-
"""graph_inputs.py - read the saved input values of a Dynamo graph in Python-node PORT ORDER (IN[0], IN[1], ...).

  python graph_inputs.py FILE.dyn [--node ID]        prints index, label, value
  from graph_inputs import graph_inputs; IN = graph_inputs(path)    -> list usable as the node's IN

Follows each connector from the Python node's input port back to the input node that feeds it and takes
that node's InputValue (DoubleSlider -> float, IntegerSlider -> int, BoolSelector -> bool, StringInput -> str,
Filename/Directory -> absolute path: HintPath if it exists, else InputValue resolved against the .dyn folder;
'.' stays '.'). Unconnected ports give None. Pure stdlib; does not run Dynamo.
"""
import json
import os
import sys


def load(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def graph_inputs(path, node_id=None, with_labels=False):
    d = load(path)
    nodes = {n["Id"]: n for n in d["Nodes"]}
    views = {v["Id"]: v.get("Name", "") for v in d["View"]["NodeViews"]}
    py = [n for n in d["Nodes"] if "Python" in n.get("ConcreteType", "")]
    if node_id:
        py = [n for n in py if n["Id"].startswith(node_id)]
    if not py:
        raise SystemExit("no Python node")
    py = py[0]
    out_owner = {}
    for n in d["Nodes"]:
        for o in n.get("Outputs", []):
            out_owner[o["Id"]] = n
    feeding = {c["End"]: c["Start"] for c in d["Connectors"]}
    base = os.path.dirname(os.path.abspath(path))
    values, labels = [], []
    for p in py["Inputs"]:
        src = feeding.get(p["Id"])
        node = out_owner.get(src) if src else None
        if node is None or "InputValue" not in node:
            values.append(None)
            labels.append("(unconnected)")
            continue
        v = node["InputValue"]
        ct = node["ConcreteType"]
        if "Filename" in ct or "Directory" in ct:
            hp = node.get("HintPath")
            if hp and os.path.exists(hp):
                v = hp
            elif v not in (".", "") and not os.path.isabs(v):
                v = os.path.normpath(os.path.join(base, v))
        elif "DoubleSlider" in ct:
            v = float(v)
        elif "IntegerSlider" in ct:
            v = int(v)
        values.append(v)
        labels.append(views.get(node["Id"], ""))
    return (values, labels) if with_labels else values


if __name__ == "__main__":
    vals, labs = graph_inputs(sys.argv[1], sys.argv[sys.argv.index("--node") + 1] if "--node" in sys.argv else None, True)
    for i, (v, l) in enumerate(zip(vals, labs)):
        print("IN[%d] %-95s = %r" % (i, l[:95], v))
