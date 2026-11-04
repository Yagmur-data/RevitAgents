#!/usr/bin/env python3
"""panel_clip.py - pure-Python (no numpy) clipping of baklava panels to straight plan lines. The block between the BEGIN / END markers is embedded verbatim in the Dynamo node
(MashProject8_v15.py); mp8v6_make_node.py copies it and panel_node_selftest.py compares the two texts (kit-block rule, same as footprint_adapter.py).

Why: the engine squares the thin wing ends of Al's footprint (its end cut is vertical), but the STL has SLANTED ends (30 deg, 'triangular transitions'). The adapter (FPAD3) cuts the shell
0.6 m beyond the end of the wing and gives the node the two bevel lines (clip_lines, user frame); the node clips every panel that crosses a line: each panel is a patch of planar
sub-triangles (rhombus 2 n^2, triangle patch n^2), every sub-triangle is clipped to the half plane (Sutherland-Hodgman, z interpolated linearly = exact for a planar triangle), so the new
panel edge lies EXACTLY on the line. Panels that are not touched keep their (kind, points) form; clipped panels become kind + 2 with a plain triangle list (9 floats per triangle).

  python panel_clip.py           runs the self tests
"""
import array
import math

# ==== PANEL CLIP BEGIN ====
CLIP_VERSION = 'PCLIP1'
CLIP_MIN_PIECE_M2 = 0.02        # a clipped sub-triangle smaller than this (about 14 x 28 cm) is dropped (Revit rejects degenerate faces)
CLIP_MIN_KEEP = 0.03            # a panel with less than 3 % of its area left after clipping is dropped completely


CLIP_SNAP_M = 0.004             # a vertex closer than this to the line counts as ON the line (no new vertex 1 mm away from an old one: Revit rejects edges shorter than 0.8 mm)


def _clip_tri(tri, px, py, nx, ny):
    """clip one planar triangle (three (x, y, z)) to the half plane (x - px) * nx + (y - py) * ny >= 0 -> list of 0..2 triangles."""
    s = [(p[0] - px) * nx + (p[1] - py) * ny for p in tri]
    s = [0.0 if abs(v) < CLIP_SNAP_M else v for v in s]
    if s[0] >= -1e-9 and s[1] >= -1e-9 and s[2] >= -1e-9:
        return [tri]
    if s[0] <= 1e-9 and s[1] <= 1e-9 and s[2] <= 1e-9:
        return []
    poly = []
    for i in range(3):
        a, b, sa, sb = tri[i], tri[(i + 1) % 3], s[i], s[(i + 1) % 3]
        if sa >= 0.0:
            poly.append(a)
        if (sa > 0.0 and sb < 0.0) or (sa < 0.0 and sb > 0.0):
            t = sa / (sa - sb)
            poly.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]), a[2] + t * (b[2] - a[2])))
    if len(poly) < 3:
        return []
    return [(poly[0], poly[k], poly[k + 1]) for k in range(1, len(poly) - 1)]


def _tri_area(t):
    ux, uy, uz = t[1][0] - t[0][0], t[1][1] - t[0][1], t[1][2] - t[0][2]
    vx, vy, vz = t[2][0] - t[0][0], t[2][1] - t[0][1], t[2][2] - t[0][2]
    cx, cy, cz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    return 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz)


def clip_panels(panels, tri_tables, lines):
    """panels: list of (kind, array('f')) with kind 0 = rhombus grid, 1 = triangle patch (tri_tables[kind] = sub-triangle index triples);
    lines: [{'point': [x, y], 'normal': [nx, ny], 'box': [xmin, xmax, ymin, ymax]}] (user frame; kept side = normal direction; the line only acts inside its box).
    Returns (new_panels, stats). Panels that are not touched are returned as they are (same objects)."""
    out, partial, removed, fractions, dropped_pieces = [], 0, 0, [], 0
    area_before = area_after = 0.0
    for kind, v in panels:
        n = len(v) // 3
        xs = [v[3 * k] for k in range(n)]
        ys = [v[3 * k + 1] for k in range(n)]
        hit = []
        for ln in lines:
            b = ln['box']
            if max(xs) < b[0] or min(xs) > b[1] or max(ys) < b[2] or min(ys) > b[3]:
                continue
            px, py = ln['point']
            nx, ny = ln['normal']
            if min((xs[k] - px) * nx + (ys[k] - py) * ny for k in range(n)) < -1e-9:
                hit.append((px, py, nx, ny))
        if not hit:
            out.append((kind, v))
            continue
        tris = [tuple((v[3 * i], v[3 * i + 1], v[3 * i + 2]) for i in tri) for tri in tri_tables[kind]]
        total = sum(_tri_area(t) for t in tris)
        pieces = tris
        for (px, py, nx, ny) in hit:
            nxt = []
            for t in pieces:
                nxt.extend(_clip_tri(t, px, py, nx, ny))
            pieces = nxt
        kept = [t for t in pieces if _tri_area(t) >= CLIP_MIN_PIECE_M2]
        dropped_pieces += len(pieces) - len(kept)
        left = sum(_tri_area(t) for t in kept)
        area_before += total
        if not kept or left < CLIP_MIN_KEEP * total:
            removed += 1
            continue
        area_after += left
        partial += 1
        fractions.append(left / total)
        flat = array.array('f')
        for t in kept:
            for p in t:
                flat.extend(p)
        out.append((kind + 2, flat))
    fractions.sort()
    stats = {'version': CLIP_VERSION, 'panels_in': len(panels), 'panels_out': len(out), 'partial': partial, 'removed': removed, 'dropped_pieces': dropped_pieces,
             'area_removed_m2': round(area_before - area_after, 1),
             'remaining_fraction_min': round(fractions[0], 3) if fractions else None, 'remaining_fraction_median': round(fractions[len(fractions) // 2], 3) if fractions else None,
             'partial_below_30pct': sum(1 for f in fractions if f < 0.3), 'partial_below_50pct': sum(1 for f in fractions if f < 0.5)}
    return out, stats
# ==== PANEL CLIP END ====


def _selftest():
    import random
    fails = []

    def chk(name, cond, info=''):
        print(('PASS ' if cond else 'FAIL ') + name + ('  ' + str(info) if info else ''))
        if not cond:
            fails.append(name)
    # 1) triangle fully inside / outside / crossing
    t = ((1.0, 1.0, 5.0), (3.0, 1.0, 5.0), (1.0, 3.0, 5.0))
    chk('inside kept as is', _clip_tri(t, 0.0, 0.0, 1.0, 0.0) == [t])
    chk('outside dropped', _clip_tri(t, 10.0, 0.0, 1.0, 0.0) == [])
    r = _clip_tri(t, 2.0, 0.0, 1.0, 0.0)      # keep x >= 2
    a = sum(_tri_area(q) for q in r)
    chk('crossing: exact area (the part of the triangle with x >= 2 is 0.5 * 1 * 1)', abs(a - 0.5) < 1e-12, a)
    chk('crossing: every new vertex lies on x >= 2 and the cut edge is ON the line', all(p[0] >= 2.0 - 1e-12 for q in r for p in q) and any(abs(p[0] - 2.0) < 1e-12 for q in r for p in q))
    # 2) z is interpolated linearly (planar triangle stays planar)
    t = ((0.0, 0.0, 0.0), (4.0, 0.0, 4.0), (0.0, 4.0, 8.0))      # plane z = x + 2 y
    r = _clip_tri(t, 1.0, 0.0, 1.0, 0.0)
    chk('z interpolation keeps the plane z = x + 2 y', all(abs(p[2] - (p[0] + 2 * p[1])) < 1e-12 for q in r for p in q))
    # 3) slanted line through a rhombus grid: kept area + removed area = total, edge on the line
    n = 4
    tabs = {0: [], 1: []}
    for i in range(n):
        for j in range(n):
            v00, v10, v11, v01 = i * (n + 1) + j, (i + 1) * (n + 1) + j, (i + 1) * (n + 1) + j + 1, i * (n + 1) + j + 1
            tabs[0] += [(v00, v10, v11), (v00, v11, v01)]
    bary = [(i, j) for i in range(n + 1) for j in range(n + 1 - i)]
    bi = dict((ij, k) for k, ij in enumerate(bary))
    for i in range(n):
        for j in range(n - i):
            tabs[1].append((bi[(i, j)], bi[(i + 1, j)], bi[(i, j + 1)]))
            if i + j < n - 1:
                tabs[1].append((bi[(i + 1, j)], bi[(i + 1, j + 1)], bi[(i, j + 1)]))
    pts = array.array('f')
    for i in range(n + 1):
        for j in range(n + 1):
            pts.extend((10.0 + 1.5 * j + 0.5 * i, 20.0 + 1.5 * i, 0.1 * i))          # a leaning rhombus, 6 m sides
    tot = sum(_tri_area(tuple((pts[3 * k], pts[3 * k + 1], pts[3 * k + 2]) for k in tri)) for tri in tabs[0])
    line = {'point': [14.0, 20.0], 'normal': [0.866025, 0.5], 'box': [0.0, 100.0, 0.0, 100.0]}
    o, st = clip_panels([(0, pts)], tabs, [line])
    chk('rhombus crossing the line becomes kind 2', len(o) == 1 and o[0][0] == 2 and st['partial'] == 1, st)
    k_area = sum(_tri_area(tuple(tuple(o[0][1][9 * q + 3 * p + c] for c in range(3)) for p in range(3))) for q in range(len(o[0][1]) // 9))
    nx_, ny_ = 0.866025, 0.5
    s_all = [(o[0][1][3 * k] - 14.0) * nx_ + (o[0][1][3 * k + 1] - 20.0) * ny_ for k in range(len(o[0][1]) // 3)]
    chk('all clipped vertices are on the kept side (>= -1e-4 m, float32)', min(s_all) >= -1e-4, min(s_all))
    chk('some clipped vertices lie ON the line (|s| < 1e-4 m)', sum(1 for s in s_all if abs(s) < 1e-4) >= 2)
    chk('kept area < total and > 0', 0 < k_area < tot, (k_area, tot))
    # 4) outside the box the line does nothing; fully outside panels are removed; untouched panels are the same objects
    far = array.array('f', [x + 500.0 if k % 3 == 0 else x for k, x in enumerate(pts)])
    o, st = clip_panels([(0, far)], tabs, [line])
    chk('panel outside the box is returned untouched (same object)', o[0][1] is far and st['partial'] == 0 and st['removed'] == 0)
    gone = array.array('f', [x - 50.0 if k % 3 == 0 else x for k, x in enumerate(pts)])
    line_wide = dict(line, box=[-100.0, 100.0, 0.0, 100.0])
    o, st = clip_panels([(0, gone)], tabs, [line_wide])
    chk('panel completely on the wrong side is removed', len(o) == 0 and st['removed'] == 1, st)
    # 5) random triangles: area conservation (kept + clipped-away = total) for random lines
    random.seed(7)
    ok = True
    for _ in range(300):
        tri = tuple((random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(0, 3)) for _ in range(3))
        ang = random.uniform(0, 6.28)
        nx, ny = math.cos(ang), math.sin(ang)
        a_keep = sum(_tri_area(q) for q in _clip_tri(tri, 0.3, -0.2, nx, ny))
        a_cut = sum(_tri_area(q) for q in _clip_tri(tri, 0.3, -0.2, -nx, -ny))
        ok = ok and abs(a_keep + a_cut - _tri_area(tri)) < 1e-9
    chk('random triangles: area of both sides adds up to the whole', ok)
    # 6) no result edge shorter than 2 mm for realistic triangles (equilateral, 1..2 m sides) with a vertex a hair (up to 8 mm) off the line: Revit refuses edges < 0.8 mm
    shortest = 1e9
    for _ in range(4000):
        u = random.choice((-1, 1)) * random.uniform(0.0, 0.008)
        L = random.uniform(1.0, 2.0)
        phi = random.uniform(0, 6.2832)
        a = (2.0 + u, 0.0, 0.0)
        tri = (a, (a[0] + L * math.cos(phi), L * math.sin(phi), 0.0), (a[0] + L * math.cos(phi + 1.0472), L * math.sin(phi + 1.0472), 0.0))
        for q in _clip_tri(tri, 2.0, 0.0, 1.0, 0.0):
            for k in range(3):
                shortest = min(shortest, math.dist(q[k], q[(k + 1) % 3]))
    chk('no clipped edge shorter than 2 mm for equilateral triangles with a vertex up to 8 mm off the line', shortest >= 0.002, round(shortest, 5))
    print('ALL PASS' if not fails else 'FAILED: ' + ', '.join(fails))
    return 1 if fails else 0


if __name__ == '__main__':
    import sys
    sys.exit(_selftest())
