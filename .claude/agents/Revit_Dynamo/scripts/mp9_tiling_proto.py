#!/usr/bin/env python3
"""mp9_tiling_proto.py - PROTOTYPE (measurement only, not used by any graph): split a baklava lattice into compact, connected tiles of whole panels.

  python mp9_tiling_proto.py BAKLAVA_PANELS.bkl L TILE_SIZE [TILE_SIZE ...] OUT.json

Method: farthest-point seeds on the triangle adjacency graph (geodesic distance between triangle centroids), every panel (both rhombus halves) goes to
the geodesically nearest seed, then 3 balancing sweeps move boundary panels from tiles above 1.3 x the target to a smaller neighbouring tile.
Reports per tile size: tile count, triangles per tile (min / mean / max), connected tiles (should be all), bbox longest/middle ratio, and the share of
EXTRA points caused by shared border nodes appearing in two (or more) tiles' families (points written / lattice vertices - 1).
"""
import heapq
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
    bkl, L = sys.argv[1], float(sys.argv[2])
    sizes = [int(x) for x in sys.argv[3:-1]]
    out_path = sys.argv[-1]
    ws = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    dyn = os.path.join(ws, "ForDynamo", "baklava-panels", "MashProject9_v11.dyn")
    code = T.node_code(dyn)
    IN = graph_inputs(dyn)
    IN[28] = tempfile.mkdtemp()
    IN[20] = L
    IN[51] = 0
    IN[26] = False
    S.W.reset("mass")
    out, ns = T.run_code(code, IN, os.path.dirname(bkl))
    n_sub, panels = ns["read_panels"](bkl)
    lat = ns["lattice_from_panels"](panels, n_sub)
    ns["lattice_checks"](lat)
    ns["build_adjacency"](lat)
    nodes, tris, adj, cent = lat["nodes"], lat["tris"], lat["adj"], lat["cent"]
    T_ = len(tris)
    npan = len(lat["first_tri"])
    panel_of = lat["tri_panel"]
    pan_tris = [ns["panel_triangles"](lat, pi) for pi in range(npan)]

    def d3(a, b):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)

    results = {"L": L, "triangles": T_, "panels": npan, "tiles": {}}
    for target in sizes:
        k = max(1, round(T_ / float(target)))
        # farthest-point seeding (incremental, pruned Dijkstra)
        best = [1e30] * T_
        seeds = [min(range(T_), key=lambda i: (cent[i][0], cent[i][1], i))]
        owner = [-1] * T_

        def relax(seed, idx):
            best[seed] = 0.0
            owner[seed] = idx
            h = [(0.0, seed)]
            while h:
                d, i = heapq.heappop(h)
                if d > best[i] or (d == best[i] and owner[i] != idx and d > 0):
                    continue
                for j in adj[i]:
                    nd = d + d3(cent[i], cent[j])
                    if nd < best[j]:
                        best[j] = nd
                        owner[j] = idx
                        heapq.heappush(h, (nd, j))
        relax(seeds[0], 0)
        for idx in range(1, k):
            s = max(range(T_), key=lambda i: (best[i], -i))
            seeds.append(s)
            relax(s, idx)
        # panels go to the owner of their first triangle
        tile_of_pan = [owner[pan_tris[pi][0]] for pi in range(npan)]
        # neighbour panels
        pan_adj = [set() for _ in range(npan)]
        for i in range(T_):
            for j in adj[i]:
                if panel_of[i] != panel_of[j]:
                    pan_adj[panel_of[i]].add(panel_of[j])
        sizes_t = [0] * k
        for pi in range(npan):
            sizes_t[tile_of_pan[pi]] += len(pan_tris[pi])
        for sweep in range(3):
            for pi in range(npan):
                t = tile_of_pan[pi]
                if sizes_t[t] > 1.3 * target:
                    cands = sorted((sizes_t[tile_of_pan[q]], tile_of_pan[q]) for q in pan_adj[pi] if tile_of_pan[q] != t)
                    if cands and cands[0][0] + len(pan_tris[pi]) < sizes_t[t]:
                        nt = cands[0][1]
                        sizes_t[t] -= len(pan_tris[pi])
                        sizes_t[nt] += len(pan_tris[pi])
                        tile_of_pan[pi] = nt
        members = [[] for _ in range(k)]
        for pi in range(npan):
            members[tile_of_pan[pi]] += pan_tris[pi]
        members = [m for m in members if m]
        conn = 0
        ratios = []
        points_written = 0
        for m in members:
            ms = set(m)
            seen, stack = {m[0]}, [m[0]]
            while stack:
                x = stack.pop()
                for y in adj[x]:
                    if y in ms and y not in seen:
                        seen.add(y)
                        stack.append(y)
            conn += 1 if len(seen) == len(ms) else 0
            used = set(g for i in m for g in tris[i])
            points_written += len(used)
            dims = sorted([max(nodes[g][c] for g in used) - min(nodes[g][c] for g in used) for c in range(3)], reverse=True)
            ratios.append(dims[0] / max(dims[1], 1e-6))
        sz = sorted(len(m) for m in members)
        r = {"tiles": len(members), "triangles_per_tile": {"min": sz[0], "mean": round(T_ / len(members)), "max": sz[-1]}, "connected_tiles": conn,
             "bbox_longest_over_middle": {"median": round(sorted(ratios)[len(ratios) // 2], 2), "max": round(max(ratios), 2)},
             "points_written": points_written, "lattice_vertices": len(nodes), "extra_points_share": round(points_written / float(len(nodes)) - 1, 3)}
        results["tiles"][str(target)] = r
        print(target, r, flush=True)
    json.dump(results, open(out_path, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
