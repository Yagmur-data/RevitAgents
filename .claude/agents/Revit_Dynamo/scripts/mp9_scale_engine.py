#!/usr/bin/env python3
"""mp9_scale_engine.py - measure the REAL MashEngine.exe at a small panel edge L (offline, nothing touches Revit or the user's files).

  python mp9_scale_engine.py OUT_DIR WORK_DIR L [L ...] [--h H] [--n N] [--settings settings.json] [--set KEY=VALUE ...] [--reuse]

Takes the settings the MashProject8/9 node sends to the engine (default: OUT_DIR/settings_base.json = Al's saved v10 values, panel gap 0),
overrides PANEL_EDGE = L (and optionally h = Mesh spacing, PANEL_SUBDIV = n), runs the exe DIRECTLY (no 1500 s node timeout), one L after the
other, and records per L: wall seconds, the engine's own panel-stage seconds, peak summed working set of all MashEngine.exe processes (sampled
every 5 s with tasklist), the .bkl size, the engine report (counts, quality, warnings, irregular share, valence histogram), then rebuilds the
lattice triangles with the MashProject9_v11 node code (matches_engine_report, edge-length statistics: min/mean/p50/p95/p99/p99.9/max, share
of edges above 3.0 / 3.3 / 3.6 m, angle shares). Writes OUT_DIR/L<L>[_h<H>][_n<N>]_report.json and appends OUT_DIR/summary.jsonl.
The big files (.bkl) stay in WORK_DIR (outside the workspace); the 40 MB shell STL is deleted.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")
import mp9_selftest as T          # noqa: E402
import mp9_stubs as S             # noqa: E402
from graph_inputs import graph_inputs  # noqa: E402


def sample_memory(stop, peak):
    while not stop.is_set():
        try:
            out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq MashEngine.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True,
                                 encoding="cp1254", errors="replace").stdout
            total = 0
            for line in out.splitlines():
                parts = [p.strip('"') for p in line.split('","')]
                if len(parts) >= 5 and parts[0].lower().startswith("mashengine"):
                    digits = re.sub(r"[^0-9]", "", parts[4])
                    total += int(digits) if digits else 0
            peak[0] = max(peak[0], total)
        except Exception:
            pass
        stop.wait(5.0)


def pct(sorted_values, p):
    return sorted_values[min(len(sorted_values) - 1, int(p * (len(sorted_values) - 1) + 0.5))]


def edge_stats(lat, ns):
    nodes = lat["nodes"]
    lengths = []
    for (a, b) in lat["edges"]:
        p, q = nodes[a], nodes[b]
        lengths.append(math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2))
    lengths.sort()
    n = len(lengths)
    return {"edges": n, "min": round(lengths[0], 3), "mean": round(sum(lengths) / n, 3), "p50": round(pct(lengths, 0.5), 3), "p95": round(pct(lengths, 0.95), 3),
            "p99": round(pct(lengths, 0.99), 3), "p99.9": round(pct(lengths, 0.999), 3), "max": round(lengths[-1], 3),
            "share_above_3.0m": round(sum(1 for v in lengths if v > 3.0) / n, 4), "share_above_3.3m": round(sum(1 for v in lengths if v > 3.3) / n, 4),
            "share_above_3.6m": round(sum(1 for v in lengths if v > 3.6) / n, 4), "count_above_3.0m": sum(1 for v in lengths if v > 3.0),
            "count_above_3.3m": sum(1 for v in lengths if v > 3.3)}


def main():
    argv = sys.argv[1:]
    out_dir, work_dir = argv[0], argv[1]
    opts = {}
    rest = []
    i = 2
    while i < len(argv):
        if argv[i] == "--reuse":
            opts["reuse"] = "1"
            i += 1
        elif argv[i] == "--set":
            opts.setdefault("set", []).append(argv[i + 1])
            i += 2
        elif argv[i] in ("--h", "--n", "--settings"):
            opts[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            rest.append(argv[i])
            i += 1
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(work_dir, exist_ok=True)
    base_path = opts.get("settings", os.path.join(out_dir, "settings_base.json"))
    base = json.load(open(base_path, encoding="utf-8"))
    ws = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    pkg = os.path.join(ws, "MashProject8", "MashProject8_Paylas_V3")
    exe = os.path.join(pkg, "Engine", "MashEngine.exe")
    footprint = os.path.join(pkg, "Footprint.stl")
    dyn = os.path.join(ws, "ForDynamo", "baklava-panels", "MashProject9_v11.dyn")     # working copy (the root copy may have been re-saved by the user with WRITE=True)
    code = T.node_code(dyn)
    base_in = graph_inputs(dyn)
    for Ltxt in rest:
        L = float(Ltxt)
        tag = "L%s" % Ltxt.replace(".", "_")
        if "h" in opts:
            tag += "_h%s" % opts["h"].replace(".", "_")
        if "n" in opts:
            tag += "_n%s" % opts["n"]
        for kv in opts.get("set", []):
            tag += "_" + kv.replace("=", "").replace(".", "_")
        run_dir = os.path.join(work_dir, tag)
        reuse = "reuse" in opts and os.path.isfile(os.path.join(run_dir, "BAKLAVA_PANELS.bkl")) and os.path.isfile(os.path.join(run_dir, "baklava_report.json"))
        if not reuse:
            shutil.rmtree(run_dir, ignore_errors=True)
            os.makedirs(run_dir)
        st = dict(base)
        st["PANEL_EDGE"] = L
        st["PANEL_GAP"] = 0.0
        if "h" in opts:
            st["h"] = float(opts["h"])
        if "n" in opts:
            st["PANEL_SUBDIV"] = int(opts["n"])
        for kv in opts.get("set", []):
            k, v = kv.split("=", 1)
            st[k] = (v.lower() == "true") if v.lower() in ("true", "false") else float(v)
        sp = os.path.join(run_dir, "settings.json")
        if not reuse:
            json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, allow_nan=False)
        env = os.environ.copy()
        env["MPLBACKEND"] = "Agg"
        env["PYTHONIOENCODING"] = "utf-8"
        env.pop("PYTHONHOME", None)
        env.pop("PYTHONPATH", None)
        peak = [0]
        stop = threading.Event()
        th = threading.Thread(target=sample_memory, args=(stop, peak), daemon=True)
        th.start()
        t0 = time.time()
        print("[%s] start %s  L=%g h=%g n=%d" % (time.strftime("%H:%M:%S"), tag, L, st["h"], st["PANEL_SUBDIV"]), flush=True)
        res = {"tag": tag, "L": L, "h": st["h"], "n_sub": st["PANEL_SUBDIV"], "settings_file": sp}
        if reuse:
            stop.set()
            res["note"] = "engine output of an earlier run reused; wall seconds = mtime(BAKLAVA_PANELS.bkl) - mtime(settings.json); memory peak not recorded"
            res["engine_wall_seconds"] = round(os.path.getmtime(os.path.join(run_dir, "BAKLAVA_PANELS.bkl")) - os.path.getmtime(sp), 1)
            res["peak_working_set_MB_all_MashEngine_processes"] = None
            res["returncode"] = "reused"
            rep = {"Panels": json.load(open(os.path.join(run_dir, "baklava_report.json"), encoding="utf-8"))}
        else:
            try:
                proc = subprocess.run([exe, "--footprint", footprint, "--settings", sp, "--output-dir", run_dir], cwd=os.path.dirname(exe), env=env,
                                      capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=7200,
                                      creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                res["returncode"] = proc.returncode
                res["stderr_tail"] = proc.stderr[-600:]
                try:
                    rep = json.loads(proc.stdout.strip().splitlines()[-1])
                except Exception:
                    rep = {}
                    res["stdout_tail"] = proc.stdout[-600:]
            except subprocess.TimeoutExpired:
                rep = {}
                res["returncode"] = "timeout 7200 s"
            stop.set()
            res["engine_wall_seconds"] = round(time.time() - t0, 1)
            res["peak_working_set_MB_all_MashEngine_processes"] = round(peak[0] / 1024.0)
        stl = os.path.join(run_dir, "AYARLANABILIR_GAUSS_KABUK.stl")
        if os.path.isfile(stl):
            res["shell_stl_MB"] = round(os.path.getsize(stl) / 2 ** 20, 1)
            os.remove(stl)
        res["engine_report"] = rep
        panels = rep.get("Panels", {}) if isinstance(rep, dict) else {}
        bkl = os.path.join(run_dir, "BAKLAVA_PANELS.bkl")
        res["bkl_MB"] = round(os.path.getsize(bkl) / 2 ** 20, 2) if os.path.isfile(bkl) else None
        res["engine_panel_stage_seconds"] = panels.get("seconds")
        if panels and os.path.isfile(bkl):
            json.dump(panels, open(os.path.join(run_dir, "baklava_report.json"), "w", encoding="utf-8"), indent=1)
            IN = list(base_in)
            IN[28] = tempfile.mkdtemp(prefix="mp9scale_")
            IN[20] = L
            IN[21] = st["PANEL_SUBDIV"]
            IN[51] = 0
            IN[26] = False          # NEVER write: the analysis is a dry run (a graph saved by the user may carry WRITE=True)
            S.W.reset("mass")
            t1 = time.time()
            out, ns = T.run_code(code, IN, run_dir)
            res["node_dry_run_seconds_python_side"] = round(time.time() - t1, 1)
            res["node_status"] = out.get("Status")
            res["node_message"] = out.get("Message")
            d = out.get("data", {})
            if out.get("status") == "dry-run":
                q = d["triangle_quality"]
                res["lattice"] = d["lattice"]
                res["panel_counts"] = d["panel_counts"]
                res["triangle_quality"] = q
                res["node_warnings"] = d.get("warnings")
                res["estimate_node_model_minutes"] = d["estimate"]["minutes"]
                n_sub, pl = ns["read_panels"](bkl)
                lat = ns["lattice_from_panels"](pl, n_sub)
                ns["lattice_checks"](lat)
                res["edge_length_m"] = edge_stats(lat, ns)
                res["matches_engine_report"] = d["lattice"]["matches_engine_report"]
        res["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
        json.dump(res, open(os.path.join(out_dir, tag + "_report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        with open(os.path.join(out_dir, "summary.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps({k: res.get(k) for k in ("tag", "L", "h", "n_sub", "returncode", "engine_wall_seconds", "peak_working_set_MB_all_MashEngine_processes", "bkl_MB",
                                                         "matches_engine_report", "panel_counts", "edge_length_m")}, ensure_ascii=False) + "\n")
        print("[%s] done %s: wall %.0f s, peak %s MB, triangles %s, edge max %s" % (time.strftime("%H:%M:%S"), tag, res["engine_wall_seconds"],
              res["peak_working_set_MB_all_MashEngine_processes"], (res.get("panel_counts") or {}).get("triangles_total"), (res.get("edge_length_m") or {}).get("max")), flush=True)


if __name__ == "__main__":
    main()
