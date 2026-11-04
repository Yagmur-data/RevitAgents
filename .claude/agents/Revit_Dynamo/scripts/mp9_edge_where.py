#!/usr/bin/env python3
"""mp9_edge_where.py - WHERE are the long triangle edges of a baklava lattice?

  python mp9_edge_where.py BAKLAVA_PANELS.bkl L LIMIT_M OUT.json [ratio_report]

Rebuilds the lattice with the MashProject9_v11 node code (offline, stub Revit) and, for every edge longer than LIMIT_M (m), classifies it:
open-rim edge (one triangle) or interior; valence of its two end vertices (6 = regular; 5/7/8 = cone/irregular; rim vertices counted separately);
edge direction class (is it the hidden diagonal of a rhombus = shared edge of the two halves, or a rhombus side / lone-triangle side);
plan region (x bin, y bin of 50 m) and z. Also prints the ratio table (share of edges above 1.1/1.2/1.3/1.4/1.5 x L) and the longest 15 edges
with coordinates. Pure python, a minute for 150,000 triangles. Used to decide whether a hard maximum edge needs a smaller L or a different mechanism.
"""
import json
import math
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")
import mp9_selftest as T          # noqa: E402
import mp9_stubs as S             # noqa: E402
from graph_inputs import graph_inputs  # noqa: E402


def main():
    bkl, L, limit, out_path = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    ws = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    dyn = os.path.join(ws, "ForDynamo", "baklava-panels", "MashProject9_v11.dyn")
    code = T.node_code(dyn)
    IN = graph_inputs(dyn)
    IN[28] = tempfile.mkdtemp()
    IN[20] = L
    IN[51] = 0
    IN[26] = False
    # need a fake engine dir only to get the node's namespace: use the folder of the bkl (must hold baklava_report.json)
    S.W.reset("mass")
    out, ns = T.run_code(code, IN, os.path.dirname(bkl))
    n_sub, panels = ns["read_panels"](bkl)
    lat = ns["lattice_from_panels"](panels, n_sub)
    ns["lattice_checks"](lat)
    nodes, tris = lat["nodes"], lat["tris"]
    edges = lat["edges"]
    val = {}
    rim_v = set()
    for (a, b), c in edges.items():
        val[a] = val.get(a, 0) + 1
        val[b] = val.get(b, 0) + 1
        if c == 1:
            rim_v.add(a)
            rim_v.add(b)
    # hidden diagonals: the edge shared by the two halves of a rhombus = first_tri[pi] and +1
    diag = set()
    for pi in range(len(lat["first_tri"])):
        t0 = lat["first_tri"][pi]
        if lat["tri_half"][t0] == 0:
            sh = sorted(set(tris[t0]) & set(tris[t0 + 1]))
            diag.add((sh[0], sh[1]))
    lens = []
    for (a, b), c in edges.items():
        p, q = nodes[a], nodes[b]
        lens.append((math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2), a, b, c))
    lens.sort(reverse=True)
    n = len(lens)
    print("L=%g: %d edges, longest %.3f m (ratio %.3f)" % (L, n, lens[0][0], lens[0][0] / L))
    ratios = {}
    for r in (1.1, 1.2, 1.3, 1.4, 1.5):
        ratios["share_above_%.1fL" % r] = round(sum(1 for x in lens if x[0] > r * L) / n, 5)
    print(ratios)
    over = [x for x in lens if x[0] > limit]
    rep = {"L": L, "limit_m": limit, "edges": n, "longest_m": round(lens[0][0], 3), "ratio_table": ratios, "edges_over_limit": len(over),
           "share_over_limit": round(len(over) / n, 6)}
    cls = {"rim": 0, "interior": 0, "diagonal(hidden)": 0, "side/lone": 0, "an_endpoint_on_rim": 0, "an_endpoint_irregular(valence!=6, not rim)": 0, "both_endpoints_regular": 0}
    bins = {}
    for ln, a, b, c in over:
        cls["rim" if c == 1 else "interior"] += 1
        cls["diagonal(hidden)" if ((a, b) if a < b else (b, a)) in diag else "side/lone"] += 1
        if a in rim_v or b in rim_v:
            cls["an_endpoint_on_rim"] += 1
        elif val[a] != 6 or val[b] != 6:
            cls["an_endpoint_irregular(valence!=6, not rim)"] += 1
        else:
            cls["both_endpoints_regular"] += 1
        mx = (nodes[a][0] + nodes[b][0]) / 2
        my = (nodes[a][1] + nodes[b][1]) / 2
        key = "x%03d_y%03d" % (int(mx // 50) * 50, int(my // 50) * 50)
        bins[key] = bins.get(key, 0) + 1
    rep["classes_of_edges_over_limit"] = cls
    rep["regions_50m_bins_over_limit(top12)"] = dict(sorted(bins.items(), key=lambda kv: -kv[1])[:12])
    rep["longest_15"] = [{"len_m": round(ln, 3), "rim": c == 1, "valences": [val[a], val[b]], "diagonal": ((a, b) if a < b else (b, a)) in diag,
                          "mid_xyz_m": [round((nodes[a][k] + nodes[b][k]) / 2, 1) for k in range(3)]} for ln, a, b, c in lens[:15]]
    # same classification for the long tail relative to L (>1.25 L) when no edge exceeds the limit
    tail = [x for x in lens if x[0] > 1.25 * L]
    rep["edges_over_1.25L"] = len(tail)
    rep["tail_over_1.25L_rim"] = sum(1 for x in tail if x[3] == 1)
    rep["tail_over_1.25L_diag"] = sum(1 for x in tail if ((x[1], x[2]) if x[1] < x[2] else (x[2], x[1])) in diag)
    json.dump(rep, open(out_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(rep, ensure_ascii=False, indent=1)[:2500])


if __name__ == "__main__":
    main()
