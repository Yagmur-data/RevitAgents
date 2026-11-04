# -*- coding: utf-8 -*-
"""run_node_offline.py - execute a Dynamo CPython3 Python-node source OFFLINE (no Revit, no Dynamo).

usage: python run_node_offline.py NODE.py ['<json list for IN>'] [key1,key2,...]

Injects IN (default [false]) and runs the file as a module-level script, the way Dynamo does
(`if "IN" in globals():` guards work). Prints selected keys of OUT (default: all, truncated).
Only for nodes whose report/dry-run path does not touch the Revit API (e.g. DynamoOption1V7:
IN[0]=False -> CALCULATED_ONLY report). Anything that imports clr/Autodesk fails here by design.
Proves the numbers of the pure-Python part only; never pythonnet/Revit/Dynamo behaviour.
"""
import json
import sys
import time

src = sys.argv[1]
IN = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [False]
keys = sys.argv[3].split(",") if len(sys.argv) > 3 else None
t0 = time.time()
g = {"IN": IN, "__name__": "__dynamo__"}
with open(src, encoding="utf-8-sig") as f:
    code = f.read()
exec(compile(code, src, "exec"), g)
out = g.get("OUT")
if keys and isinstance(out, dict):
    out = {k: out.get(k) for k in keys if k in out}
print(json.dumps(out, indent=1, default=str)[:12000])
print("secs", round(time.time() - t0, 1))
