#!/usr/bin/env python3
"""engine_capture.py - run a MashProject8-family graph's Python node OFFLINE (Revit stubbed) with the graph's own saved
slider values, but with the REAL MashEngine.exe, and keep the engine's panel output.

  python engine_capture.py GRAPH.dyn OUT_DIR [KEY=VALUE ...]      (KEY = input index, e.g. 20=7.0 overrides IN[20])

Writes OUT_DIR/BAKLAVA_PANELS.bkl, OUT_DIR/baklava_report.json (the engine's 'Panels' summary), OUT_DIR/engine_report_full.json
and OUT_DIR/settings.json (what the node sent to the engine). The shell STL is NOT kept (about 40 MB) unless env KEEP_STL=1.
Forces WRITE (IN[26]) False and Result folder (IN[28]) = OUT_DIR. Takes 2-4 minutes for the default shell.
Proves what the engine produces for those values; says nothing about Revit/Dynamo.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import panel_node_selftest as pns          # noqa: E402  (stub builder)
from graph_inputs import graph_inputs, load  # noqa: E402


def node_code(dyn):
    d = load(dyn)
    return [n for n in d["Nodes"] if "Python" in n.get("ConcreteType", "")][0]["Code"]


def main():
    dyn, out_dir = sys.argv[1], sys.argv[2]
    over = dict(a.split("=", 1) for a in sys.argv[3:])
    os.makedirs(out_dir, exist_ok=True)
    IN = graph_inputs(dyn)
    IN[26] = False
    IN[28] = out_dir
    for k, v in over.items():
        k = int(k)
        old = IN[k]
        IN[k] = (v.lower() in ("1", "true")) if isinstance(old, bool) else (type(old)(v) if old is not None else v)
    code = node_code(dyn)
    stubs = pns.build_stubs()
    saved = {k: sys.modules.get(k) for k in stubs}
    sys.modules.update(stubs)
    real_run = subprocess.run

    def run_real(cmd, **kw):
        res = real_run(cmd, **kw)
        td = cmd[cmd.index("--output-dir") + 1]
        for name in ("BAKLAVA_PANELS.bkl", "settings.json") + (("AYARLANABILIR_GAUSS_KABUK.stl",) if os.environ.get("KEEP_STL") else ()):
            if os.path.isfile(os.path.join(td, name)):
                shutil.copy(os.path.join(td, name), os.path.join(out_dir, name))
        try:
            rep = json.loads(res.stdout.strip().splitlines()[-1])
            with open(os.path.join(out_dir, "engine_report_full.json"), "w", encoding="utf-8") as fh:
                json.dump(rep, fh, indent=1)
            with open(os.path.join(out_dir, "baklava_report.json"), "w", encoding="utf-8") as fh:
                json.dump(rep.get("Panels", {}), fh, indent=1)
        except Exception as exc:
            print("could not parse engine report:", exc)
        return res
    subprocess.run = run_real
    ns = {"IN": IN, "__name__": "__node__"}
    try:
        exec(compile(code, "node", "exec"), ns)
    finally:
        subprocess.run = real_run
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    out = ns["OUT"]
    print("node status:", out.get("Status"), out.get("Message", ""))
    pc = (out.get("data") or {}).get("panel_counts")
    print("panel_counts:", pc)
    rep = json.load(open(os.path.join(out_dir, "baklava_report.json"), encoding="utf-8"))
    print("lattice triangles", rep.get("triangles"), "vertices", rep.get("vertices"), "rhombus", rep.get("rhombus_panels"),
          "unpaired", rep.get("triangle_panels"))


if __name__ == "__main__":
    main()
