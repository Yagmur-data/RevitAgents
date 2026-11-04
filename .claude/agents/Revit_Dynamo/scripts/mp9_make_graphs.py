#!/usr/bin/env python3
"""mp9_make_graphs.py - (re)build MashProject9_v11.dyn (the single MashProject9 graph) from its node source.

  python mp9_make_graphs.py

Source of truth = the working copy  ForDynamo/baklava-panels/MashProject9_v11.py  (convention of MashProject5..8: .dyn + .py live in
ForDynamo/baklava-panels, the .dyn is also copied to the workspace-root package folder MashProject9/).

Which graph is the BASE (the user's own slider values are kept):
  * the user's saved root copy MashProject9/MashProject9_v11.dyn when it exists:
      - 54 inputs (before the speed tools)  -> extend: new code + the 3 new inputs IN[54..56]
      - 57 inputs                            -> only the code is replaced (idempotent rebuild)
  * else the user's saved MashProject8_Paylas_V3/MashProject8_v10.dyn -> extend with IN[51..56] (defaults)
Always: WRITE TO REVIT = False (the house dry-run default), Panel Gap = 0, absolute engine paths, unused inputs relabelled, panel edge L slider
step 0.05 (range 0..15), RunType Manual. The source graphs are never edited in place; the root copy is replaced by the result.
Validated with dyn_tool.py; HintPaths checked with os.path.exists.
(The earlier O2 version with FormProbe / temporary families is archived in MashProject9/_arsiv_O2/.)
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PKG = os.path.join(WS, "MashProject8", "MashProject8_Paylas_V3")
V10 = os.path.join(PKG, "MashProject8_v10.dyn")
WORK = os.path.join(WS, "ForDynamo", "baklava-panels")
OUT = os.path.join(WS, "MashProject9")
ROOT_DYN = os.path.join(OUT, "MashProject9_v11.dyn")
TOOL = os.path.join(HERE, "dyn_tool.py")
sys.path.insert(0, HERE)
from graph_inputs import graph_inputs  # noqa: E402

DESCRIPTION = ("MashProject9 v11 = next version of the MashProject5..8 line: same STL / engine / sliders / WRITE switch as MashProject8_v10; only the LAST STAGE "
               "is new: every baklava lattice TRIANGLE becomes a real Revit Form (Create Form) and every shared lattice vertex one ReferencePoint, written "
               "straight into the OPEN Conceptual Mass document (File > New > Conceptual Mass > Metric Mass.rft) with the DynamoOption1V7 block. In a project "
               "(e.g. Project1) nothing is created. DRY RUN by default (WRITE TO REVIT = False; works in any document). 'Max triangles' limits the first test "
               "to a compact patch (0 = whole lattice). Re-running with the same Model key replaces the previous result (REBUILD). Opt-in speed tools: Commit every N "
               "Forms (TransactionGroup), Share edge curves, Reuse engine result. Result: MashProject9_v11_result.json + _triangle_map.json in the result folder.")
NEW_SPEED_INPUTS = [
    "--input", "int|Commit every N Forms (0 = one transaction as before; 250 = chunked commits in ONE TransactionGroup: opt-in speed test)|0|0|2000|50",
    "--input", "bool|Share edge curves (False = V7: 3 curves per triangle; True = one curve per lattice edge: opt-in speed test)|False",
    "--input", "bool|Reuse engine result (True = skip the 14+ min engine when settings, STL and exe are unchanged: opt-in)|False",
]
NEW_PATCH_INPUTS = [
    "--input", "int|Max triangles (0 = whole lattice, about 15,500; 1500 = first test patch)|1500|0|16000|50",
    "--input", "double|Patch seed X (m; X = 0 and Y = 0: automatic seed, used when Max triangles is below the total)|0|-50|550|5",
    "--input", "double|Patch seed Y (m; 0 and 0 = automatic; else the nearest triangle on the upper surface)|0|0|500|5",
]


def run(args):
    print(">", " ".join(a if " " not in a else '"%s"' % a for a in args)[:200])
    subprocess.check_call([sys.executable, TOOL] + args)


def main():
    py = os.path.join(WORK, "MashProject9_v11.py")
    for p in (V10, py):
        if not os.path.isfile(p):
            sys.exit("missing " + p)
    dyn = os.path.join(WORK, "MashProject9_v11.dyn")
    engine = os.path.join(PKG, "Engine", "MashEngine.exe")
    footprint = os.path.join(PKG, "Footprint.stl")
    sets = ["--set", "WRITE TO REVIT (False = DRY RUN)=False", "--set", "Panel Gap (m)=0.0",
            "--set", "Select Footprint STL=" + footprint, "--set", "Select MashEngine.exe=" + engine]
    root_inputs = None
    if os.path.isfile(ROOT_DYN):
        try:
            root_inputs = graph_inputs(ROOT_DYN)
        except Exception:
            root_inputs = None
    tmp = dyn + ".build"
    if root_inputs is not None and len(root_inputs) == 57:
        print("base: the user's saved root graph (57 inputs) - code replaced only")
        run(["embed", ROOT_DYN, "--py", py, "--out", tmp])
        shutil.move(tmp, dyn)
    elif root_inputs is not None and len(root_inputs) == 54:
        print("base: the user's saved root graph (54 inputs) - code + 3 new inputs")
        run(["extend", ROOT_DYN, "--out", dyn, "--py", py, "--name", "MashProject9_v11", "--description", DESCRIPTION] + NEW_SPEED_INPUTS)     # labels/values/paths stay as the user saved them
    else:
        print("base: MashProject8_Paylas_V3/MashProject8_v10.dyn - defaults")
        run(["extend", V10, "--out", dyn, "--py", py, "--name", "MashProject9_v11", "--description", DESCRIPTION] + NEW_PATCH_INPUTS + NEW_SPEED_INPUTS + sets +
            ["--set", "Result folder (handback _result.json; . = package folder)=" + OUT])
    with open(dyn, encoding="utf-8") as fh:
        d = json.load(fh)
    rename = {"Panel Gap (m)": "Panel Gap (m) - NOT USED (forced to 0: triangle Forms share their corner points)",
              "Panels per Revit element (1 = one per panel)": "Panels per Revit element - NOT USED (one Form per triangle)",
              "Also update base shell element (False = untouched)": "Also update base shell element - NOT USED (Mass document)",
              "Result folder (handback _result.json; . = package folder)": "Result folder (result json, triangle map, progress, engine cache)",
              "MashProject - English Results engine": "MashProject9 - triangle Forms + ReferencePoints in the open Mass document"}
    by_id = {n["Id"]: n for n in d["Nodes"]}
    for v in d["View"]["NodeViews"]:
        if v["Name"] in rename:
            v["Name"] = rename[v["Name"]]
        if v["Name"].startswith("Baklava Panel Edge L"):
            node = by_id[v["Id"]]
            node["StepValue"] = 0.05                    # 2.75 and 2.7 must be enterable
            node["MinimumValue"], node["MaximumValue"] = 0.0, 15.0
        if v["Name"].startswith("WRITE TO REVIT"):
            by_id[v["Id"]]["InputValue"] = False        # a delivered graph always starts as a DRY RUN
    d["Name"] = "MashProject9_v11"
    d["Description"] = DESCRIPTION
    d["View"]["Dynamo"]["HasRunWithoutCrash"] = False
    d["View"]["Dynamo"]["RunType"] = "Manual"
    with open(dyn, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    for n in d["Nodes"]:
        ct = n.get("ConcreteType", "")
        if "Filename" in ct or "Directory" in ct:
            for key in ("HintPath", "InputValue"):
                if key in n:
                    print("  %-9s %-10s exists=%s  %s" % (ct.split(".")[-1].split(",")[0], key, os.path.exists(n[key]), n[key]))
    os.makedirs(OUT, exist_ok=True)
    shutil.copyfile(dyn, ROOT_DYN)
    run(["validate", dyn, ROOT_DYN])
    print("graph written to", dyn, "and", ROOT_DYN)


if __name__ == "__main__":
    main()
