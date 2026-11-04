#!/usr/bin/env python3
"""footprint_adapter.py - pure-Python (no numpy) footprint adapter for the MashEngine 'H layout': recognises Al's 'I' footprint (bridge corridor along an axis,
a thin wing, a thick wing, junction fillets already in the outline), derives EVERY adapter value from the outline measures and writes the ENGINE-FRAME footprint STL
plus the adapter record. The block between the BEGIN / END markers is embedded verbatim in the Dynamo node (MashProject8_v14.py) and imported by make_footprint_v5.py
and the selftests (kit-block rule: the selftest compares the two texts).

  python footprint_adapter.py IN.stl OUT_DIR            derive + print the parameters (writes OUT_DIR/<stem>.engine_<md5-8>.stl and .adapter.json)

Why (measured 2026-10-14): MashEngine.exe carries the old H layout in code - junction corner targets (61.01,219.64) (59.64,271.85) (338.83,218.39) (336.49,287.59),
bridge centre line (48.3,245.7)->(349.7,253.0), thin 'left arm' x<100 / thick 'right body' x>300, dome (200,250), end cuts ymin+30 / ymax-30, foot points x = 48.3 / 349.7,
radius sampling x' = 20..430. A footprint of the same family works only after (1) a rotation so the corridor runs along +x and the thin wing is on the left, (2) the fillet arcs
become sharp corners (the engine re-creates them from Corner Fillet Radius) and the long corridor edges get intermediate vertices (two ADJACENT fillet corners make
koseleri_yuvarlat fail), (3) a shift dy so the corridor centre sits on the engine centre line (249.4), (4) a shift dx so the junction walls sit symmetrically around the engine foot points
(limited so the thin wing's closed outer edge stays inside the radius sampling start x' = 20), (5) the 'one ellipse mouth' inset: thin wing arm width w0 -> inset (w0-24)/2, cap depth (w0+24)/2,
outer corners kept as tabs, (6) UC_KESIM_PAYI = 30 + dy. Results come back through the inverse of the same affine map.
"""
import hashlib
import json
import math
import os
import struct

# ==== FOOTPRINT ADAPTER BEGIN ====
ADAPTER_VERSION = 'FPAD3'
ENGINE_FOOT_L, ENGINE_FOOT_R = 48.3, 349.7     # x' of the engine's bridge foot points (mean of the old junction corners)
ENGINE_MID_Y = 249.4                           # mean y' of the engine's bridge centre line
CUT_FROM_END = 0.6                             # FPAD3: the shell is cut 0.6 m beyond the ends of the wings (FPAD2: 30 m). The engine squares the end bevel of the thin wing
                                               # (ARM_END_STRAIGHTEN); the slanted end of the footprint is made by CLIPPING the panels to the bevel lines (clip_lines, done in the node)
TAB_LEN = 4.0                                  # length (along y') of the x' = 0 anchor tabs at the ends of the polygon (FPAD2: 20 m); the cut must lie outside the tab (cut y' = CUT_FROM_END + dy >= 10)
CAP_LEGACY = 24.0                              # cap depth of the original design
REF_X_START = 20.0                             # the engine samples the radius along the centre line from x' = 20: the cap edge must be inside
EDGE_MARGIN = 2.0
FOOT_COMP = (0.2, 0.05)                        # foot height compensation (left, right) in m, measured for Footprint_261014 (engine centre line vs corridor centre)


class AdapterError(ValueError):
    pass


def _stl_triangles(path):
    with open(path, 'rb') as f:
        data = f.read()
    tris = []
    if len(data) >= 84:
        n = struct.unpack_from('<I', data, 80)[0]
        if len(data) == 84 + 50 * n and n > 0:
            for i in range(n):
                v = struct.unpack_from('<12fH', data, 84 + 50 * i)
                tris.append((tuple(v[3:6]), tuple(v[6:9]), tuple(v[9:12])))
            return tris
    pts = []
    for line in data.decode('utf-8-sig', 'replace').splitlines():
        parts = line.split()
        if parts and parts[0].lower() == 'vertex' and len(parts) == 4:
            pts.append(tuple(float(x) for x in parts[1:]))
            if len(pts) == 3:
                tris.append(tuple(pts))
                pts = []
    if not tris:
        raise AdapterError('The footprint STL has no triangles.')
    return tris


def _area2(P):
    n = len(P)
    return sum(P[i][0] * P[(i + 1) % n][1] - P[i][1] * P[(i + 1) % n][0] for i in range(n))


def _seg_intersect(a, b, c, d):
    def cr(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return cr(c, d, a) * cr(c, d, b) < 0 and cr(a, b, c) * cr(a, b, d) < 0


def _is_simple(P):
    n = len(P)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(i - j) in (1, n - 1):
                continue
            if _seg_intersect(P[i], P[(i + 1) % n], P[j], P[(j + 1) % n]):
                return False
    return True


def read_outline(path):
    """top-face outline of an extruded-footprint STL (millimetres) -> (counter-clockwise polygon in METRES, z_bottom_mm, z_top_mm)."""
    tris = _stl_triangles(path)
    zt = max(v[2] for t in tris for v in t)
    zb = min(v[2] for t in tris for v in t)
    top = [t for t in tris if all(abs(v[2] - zt) <= 1e-6 for v in t)]
    key = lambda v: (round(v[0], 3), round(v[1], 3))      # noqa: E731  (STL is float32 millimetres)
    cnt, geo = {}, {}
    for t in top:
        for k in range(3):
            a, b = key(t[k]), key(t[(k + 1) % 3])
            if a == b:
                continue
            e = (a, b) if a < b else (b, a)
            cnt[e] = cnt.get(e, 0) + 1
            geo[a] = t[k]
            geo[b] = t[(k + 1) % 3]
    edges = [e for e, c in cnt.items() if c == 1]
    if len(edges) < 4:
        raise AdapterError('The footprint STL has no outline (top face boundary has %d edges).' % len(edges))
    adj = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    if any(len(v) != 2 for v in adj.values()):
        raise AdapterError('The footprint outline is not one simple loop.')
    start = min(adj)
    loop, prev, cur = [start], None, start
    while True:
        nxt = [j for j in adj[cur] if j != prev]
        j = nxt[0]
        if j == start:
            break
        loop.append(j)
        prev, cur = cur, j
        if len(loop) > len(adj) + 1:
            raise AdapterError('The footprint outline loop does not close.')
    if len(loop) != len(adj):
        raise AdapterError('The footprint has more than one outline loop (holes or separate parts).')
    P = [(geo[k][0] * 0.001, geo[k][1] * 0.001) for k in loop]
    if _area2(P) < 0:
        P.reverse()
    return P, zb, zt


def _inter(a, b, c, d):
    rx, ry, sx, sy = b[0] - a[0], b[1] - a[1], d[0] - c[0], d[1] - c[1]
    den = rx * sy - ry * sx
    t = ((c[0] - a[0]) * sy - (c[1] - a[1]) * sx) / den
    return (a[0] + t * rx, a[1] + t * ry)


def unround(P, max_seg=12.0, turn_lo=4.0, turn_hi=28.0):
    """replace every circular-arc run (consecutive short segments, same-sign turns of 4..28 deg) by its sharp corner and subdivide every edge between two such
    corners into collinear pieces <= 40 m. Returns (polygon, [(corner, radius, turn_deg), ...])."""
    n = len(P)
    seg = [math.hypot(P[(i + 1) % n][0] - P[i][0], P[(i + 1) % n][1] - P[i][1]) for i in range(n)]
    ang = [math.degrees(math.atan2(P[(i + 1) % n][1] - P[i][1], P[(i + 1) % n][0] - P[i][0])) for i in range(n)]
    turn = [(ang[(i + 1) % n] - ang[i] + 180.0) % 360.0 - 180.0 for i in range(n)]    # turn[i] = heading change at vertex i+1
    is_arc = [seg[(v - 1) % n] <= max_seg and seg[v] <= max_seg and turn_lo <= abs(turn[(v - 1) % n]) <= turn_hi for v in range(n)]
    runs, v = [], 0
    while v < n:
        if is_arc[v] and not is_arc[(v - 1) % n]:
            w = v
            while is_arc[(w + 1) % n]:
                w = (w + 1) % n
            runs.append((v, w))
            v = w + 1
        else:
            v += 1
    keep, corner_at, corners = [True] * n, {}, []
    for a, b in runs:
        i0, i1 = (a - 1) % n, (b + 1) % n
        c = _inter(P[(i0 - 1) % n], P[i0], P[i1], P[(i1 + 1) % n])
        idx, q = [], i0
        while True:
            idx.append(q)
            if q == i1:
                break
            q = (q + 1) % n
        tot = abs(sum(turn[(k - 1) % n] for k in idx))
        r = math.hypot(c[0] - P[i0][0], c[1] - P[i0][1]) / max(math.tan(math.radians(tot) / 2.0), 1e-9) if tot else float('nan')
        corners.append((c, r, tot))
        for q in idx:
            keep[q] = False
        corner_at[i0] = c
    out, is_corner = [], []
    for v in range(n):
        if v in corner_at:
            out.append(corner_at[v])
            is_corner.append(True)
        elif keep[v]:
            out.append(P[v])
            is_corner.append(False)
    res, m = [], len(out)
    for i in range(m):
        res.append(out[i])
        j = (i + 1) % m
        if is_corner[i] and is_corner[j]:
            L = math.hypot(out[j][0] - out[i][0], out[j][1] - out[i][1])
            k = int(math.ceil(L / 40.0))
            for q in range(1, k):
                res.append((out[i][0] + (out[j][0] - out[i][0]) * q / k, out[i][1] + (out[j][1] - out[i][1]) * q / k))
    return res, corners


def _drop_collinear(P, tol_deg=0.05):
    n = len(P)
    keep = []
    for i in range(n):
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]
        u, v = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
        t = abs(math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])))
        if t > tol_deg:
            keep.append(b)
    return keep


def _measures(P, Pu):
    xs, ys = [p[0] for p in P], [p[1] for p in P]
    return 'bbox X %.1f..%.1f Y %.1f..%.1f, %d outline vertices (%d after un-rounding)' % (min(xs), max(xs), min(ys), max(ys), len(P), len(Pu))


def analyze(P):
    """recognise the I layout in a counter-clockwise outline (metres). Returns the layout dict or raises AdapterError with the measures."""
    Pu, corners = unround(P)
    Pc = _drop_collinear(Pu)               # straight runs as single edges (the corridor edges were subdivided by unround)
    n = len(Pc)
    X0, X1 = min(p[0] for p in Pc), max(p[0] for p in Pc)
    Y0, Y1 = min(p[1] for p in Pc), max(p[1] for p in Pc)
    W, H = X1 - X0, Y1 - Y0
    cand = {'y': [], 'x': []}
    for i in range(n):
        a, b = Pc[i], Pc[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        if abs(dx) <= 0.02 and L >= 0.15 * H:
            cand['y'].append((i, a[0], min(a[1], b[1]), max(a[1], b[1]), dy < 0))     # vertical edge, 'down' = interior on +x
        if abs(dy) <= 0.02 and L >= 0.15 * W:
            cand['x'].append((i, a[1], min(a[0], b[0]), max(a[0], b[0]), dx > 0))     # horizontal edge, 'right' = interior above
    found = []
    for axis, edges, extent in (('y', cand['y'], W), ('x', cand['x'], H)):
        for e1 in edges:
            for e2 in edges:
                if e1[0] == e2[0] or not e1[4] or e2[4] or e2[1] <= e1[1]:
                    continue
                gap = e2[1] - e1[1]
                lo, hi = max(e1[2], e2[2]), min(e1[3], e2[3])
                if gap <= 0.2 * extent and hi - lo >= 0.5 * max(e1[3] - e1[2], e2[3] - e2[2]) and abs(e1[2] - e2[2]) <= 0.5 and abs(e1[3] - e2[3]) <= 0.5:
                    found.append((axis, e1[1], e2[1], lo, hi))
    if len(found) != 1:
        raise AdapterError('This footprint does not fit the I layout (one straight bridge corridor between a thin and a thick wing): found %d corridor candidates. Measures: %s.' %
                           (len(found), _measures(P, Pu)))
    axis, c0, c1, ca, cb = found[0]
    cw = c1 - c0
    if axis == 'y':
        lo_depth, hi_depth, lo_ext, hi_ext = ca - Y0, Y1 - cb, Y0, Y1
        cross_lo, cross_hi = X0, X1
    else:
        lo_depth, hi_depth, lo_ext, hi_ext = ca - X0, X1 - cb, X0, X1
        cross_lo, cross_hi = Y0, Y1
    if min(lo_depth, hi_depth) < 10.0 or max(lo_depth, hi_depth) < 1.2 * min(lo_depth, hi_depth):
        raise AdapterError('This footprint does not fit the I layout: the two wings are %.1f and %.1f m deep (need a thin and a clearly thicker wing, both >= 10 m). Measures: %s.' %
                           (lo_depth, hi_depth, _measures(P, Pu)))
    thin_high = hi_depth < lo_depth
    thin_depth, thick_depth = (hi_depth, lo_depth) if thin_high else (lo_depth, hi_depth)
    # the thin wing outer edge must be straight, perpendicular to the corridor, and span the whole length of the footprint (the cuts are 30 m from its ends)
    ext = 1 if axis == 'y' else 0     # coordinate along the corridor
    cr = 0 if axis == 'y' else 1      # coordinate across the corridor
    outer_val = (Y1 if axis == 'y' else X1) if thin_high else (Y0 if axis == 'y' else X0)
    outer = [p for p in Pc if abs(p[ext] - outer_val) <= 0.02]
    if len(outer) != 2:
        raise AdapterError('This footprint does not fit the I layout: the thin wing outer edge must be one straight edge (found %d vertices on it). Measures: %s.' % (len(outer), _measures(P, Pu)))
    span = sorted(p[cr] for p in outer)
    if span[0] - cross_lo > 2.0 or cross_hi - span[1] > 2.0:
        raise AdapterError('This footprint does not fit the I layout: the thin wing outer edge (%.1f..%.1f) must span the footprint (%.1f..%.1f). Measures: %s.' %
                           (span[0], span[1], cross_lo, cross_hi, _measures(P, Pu)))
    cross_len = cross_hi - cross_lo
    inner_val = cb if thin_high else ca                                  # junction end of the thin wing along the corridor axis
    inner = sorted(p[cr] for p in Pc if abs(p[ext] - inner_val) <= 0.02)
    bevel = max(inner[0] - cross_lo, cross_hi - inner[-1]) if len(inner) >= 2 else 0.0   # how far the thin wing inner edge is set back from its ends (end bevel)
    # FPAD3: the end bevel lines (outer corner -> inner-wall end corner, one per end, USER frame) = the lines the node clips the panels to (kept side = towards the other end)
    outer_pts = sorted([p for p in Pc if abs(p[ext] - outer_val) <= 0.02], key=lambda p: p[cr])
    inner_pts = sorted([p for p in Pc if abs(p[ext] - inner_val) <= 0.02], key=lambda p: p[cr])
    clip = []
    if len(inner_pts) >= 2 and len(outer_pts) == 2:
        for k_end, (A, B, other) in enumerate(((outer_pts[0], inner_pts[0], outer_pts[1]), (outer_pts[1], inner_pts[-1], outer_pts[0]))):
            if abs(A[cr] - B[cr]) <= 0.5:
                continue                                   # square end: nothing to clip
            dx_, dy_ = B[0] - A[0], B[1] - A[1]
            ln_ = math.hypot(dx_, dy_)
            nx_, ny_ = -dy_ / ln_, dx_ / ln_
            if (other[0] - A[0]) * nx_ + (other[1] - A[1]) * ny_ < 0:
                nx_, ny_ = -nx_, -ny_
            lo_c, hi_c = (min(A[cr], B[cr]) - 5.0, max(A[cr], B[cr]) + 60.0) if k_end == 0 else (min(A[cr], B[cr]) - 60.0, max(A[cr], B[cr]) + 5.0)
            lo_e, hi_e = (inner_val - 12.0, outer_val + 45.0) if thin_high else (outer_val - 45.0, inner_val + 12.0)
            box = [lo_c, hi_c, lo_e, hi_e] if axis == 'y' else [lo_e, hi_e, lo_c, hi_c]       # [xmin, xmax, ymin, ymax] in the user frame
            clip.append({'point': [round(A[0], 3), round(A[1], 3)], 'normal': [round(nx_, 6), round(ny_, 6)], 'box': [round(v, 3) for v in box]})
    if cross_len < 100.0 or cw < 5.0 or cw > 80.0:
        raise AdapterError('This footprint does not fit the I layout: wing length %.1f m / corridor width %.1f m out of range. Measures: %s.' % (cross_len, cw, _measures(P, Pu)))
    # engine-frame map: x' along the corridor (thin wing at x' = 0), y' across; pure rotation (det +1)
    if axis == 'y':
        m = (0.0, -1.0, 1.0, 0.0, Y1, -X0) if thin_high else (0.0, 1.0, -1.0, 0.0, -Y0, X1)
    else:
        m = (1.0, 0.0, 0.0, 1.0, -X0, -Y0) if thin_high is False else (-1.0, 0.0, 0.0, -1.0, X1, Y1)
    # m = (a, b, c, d, e, f):  x' = a X + b Y + e ,  y' = c X + d Y + f
    r3 = lambda v: round(v, 3)      # noqa: E731  (the STL carries ~1e-9 noise; the engine lattice is sensitive to 1e-14 changes of the bridge width)
    return {'axis': axis, 'thin_high': thin_high, 'corridor_width': r3(cw), 'corridor_lo': c0, 'corridor_hi': c1, 'corridor_len': r3(cb - ca), 'thin_depth': r3(thin_depth), 'thick_depth': r3(thick_depth),
            'wing_length': r3(cross_len), 'bevel_len': r3(bevel), 'clip_lines': clip, 'map': m, 'unrounded': [(round(c[0][0], 3), round(c[0][1], 3), round(c[1], 3), round(c[2], 2)) for c in corners], 'Pu': Pu}


def apply_map(m, X, Y):
    return m[0] * X + m[1] * Y + m[4], m[2] * X + m[3] * Y + m[5]


def invert_map(m, x, y):
    """inverse of the rotation map (transpose): (x', y') -> (X, Y)."""
    u, v = x - m[4], y - m[5]
    return m[0] * u + m[2] * v, m[1] * u + m[3] * v


def _ear_clip(P):
    idx, tris = list(range(len(P))), []

    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def inside(p, a, b, c):
        return cross(a, b, p) >= -1e-12 and cross(b, c, p) >= -1e-12 and cross(c, a, p) >= -1e-12
    guard = 0
    while len(idx) > 3 and guard < 100000:
        guard += 1
        k_n = len(idx)
        for k in range(k_n):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % k_n]
            a, b, c = P[i0], P[i1], P[i2]
            if cross(a, b, c) <= 1e-9:
                continue
            if any(inside(P[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2))
            idx.pop(k)
            break
        else:
            raise AdapterError('Ear clipping failed (polygon not simple?).')
    tris.append(tuple(idx))
    return tris


def write_engine_stl(path, P, header, z0=0.0, z1=0.01):
    """binary STL (mm): top face z1, bottom z0, side walls. P in metres. Triangles are emitted in vertex order so that polygon vertex 0 is the engine's loop start."""
    pts = [(p[0] * 1000.0, p[1] * 1000.0) for p in P]
    tris = _ear_clip(pts)
    tris = [tuple(t[k:] + t[:k]) for t in tris for k in [t.index(min(t))]]
    tris.sort()
    out = []
    for i, j, k in tris:
        out.append(((pts[i][0], pts[i][1], z1), (pts[j][0], pts[j][1], z1), (pts[k][0], pts[k][1], z1)))
        out.append(((pts[k][0], pts[k][1], z0), (pts[j][0], pts[j][1], z0), (pts[i][0], pts[i][1], z0)))
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        out.append(((a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1)))
        out.append(((a[0], a[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)))
    with open(path, 'wb') as fh:
        fh.write(header.encode('ascii', 'replace')[:80].ljust(80, b'\0'))
        fh.write(struct.pack('<I', len(out)))
        for t in out:
            u = (t[1][0] - t[0][0], t[1][1] - t[0][1], t[1][2] - t[0][2])
            w = (t[2][0] - t[0][0], t[2][1] - t[0][1], t[2][2] - t[0][2])
            nx, ny, nz = u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]
            ln = math.sqrt(nx * nx + ny * ny + nz * nz)
            nx, ny, nz = (nx / ln, ny / ln, nz / ln) if ln > 0 else (0.0, 0.0, 0.0)
            fh.write(struct.pack('<12fH', nx, ny, nz, *(t[0] + t[1] + t[2]), 0))
    return len(out)


def build_engine_polygon(P, lay, jog=TAB_LEN, inset_mode='auto'):
    """outline (user frame, metres) + layout -> (engine-frame polygon, info). Every value is derived from the outline measures."""
    m = lay['map']
    Q = [apply_map(m, p[0], p[1]) for p in lay['Pu']]
    # the un-rounded polygon is already min-normalised by the map (x' = 0 at the thin wing outer edge, y' >= 0)
    ymin = min(q[1] for q in Q)
    Q = [(q[0], q[1] - ymin) for q in Q]
    wall_l, wall_r = lay['thin_depth'], lay['thin_depth'] + lay['corridor_len']
    cc = 0.5 * (lay['corridor_lo'] + lay['corridor_hi'])                     # corridor centre across the corridor (user frame)
    yc = apply_map(m, cc, 0.0)[1] - ymin if lay['axis'] == 'y' else apply_map(m, 0.0, cc)[1] - ymin
    dy = round(ENGINE_MID_Y - yc, 3)
    Q = [(q[0], q[1] + dy) for q in Q]
    uc = max(CUT_FROM_END + dy, TAB_LEN + 6.0)      # the cut must lie >= 6 m behind the anchor tab (a cut inside the tab zone lengthens the cap: mouth 6.6 % B off at dy 1.4 in the variant test)
    # thin wing arm width at the cut plane (outer edge x' = 0 .. inner wall x' = wall_l): width of the polygon along x' at y' = uc + 0.04, thin side only
    w0 = lay['thin_depth']             # arm width = depth of the thin wing (the engine squares the end bevel along the inner wall, so the mouth has the full depth)
    inset = round(max((w0 - CAP_LEGACY) / 2.0, 0.0), 3) if inset_mode == 'auto' else float(inset_mode)
    dx_sym = (ENGINE_FOOT_L + ENGINE_FOOT_R - wall_l - wall_r) / 2.0
    dx = round(max(min(dx_sym, REF_X_START - EDGE_MARGIN - inset), 0.0), 3)
    if inset + dx > REF_X_START - 0.5:
        raise AdapterError('The thin wing is too deep (%.1f m) for the engine radius sampling (cap edge would leave the footprint).' % w0)
    lows = [i for i, q in enumerate(Q) if abs(q[0]) < 1e-6]
    if len(lows) != 2:
        raise AdapterError('Expected two outer-edge corners of the thin wing, got %d.' % len(lows))
    # shift along x'; the two outer corners stay on x' = 0 (anchor); extend the outer corners along y' by dy (lower to y' = 0, upper by dy)
    Q = [(q[0] + dx if abs(q[0]) > 1e-6 else 0.0, q[1]) for q in Q]
    i_lo = min(lows, key=lambda i: Q[i][1])
    i_hi = max(lows, key=lambda i: Q[i][1])
    Q[i_lo] = (0.0, 0.0)
    Q[i_hi] = (0.0, Q[i_hi][1] + dy)
    # inset: the outer edge moves to x' = dx + inset; both corners stay as tabs (the engine does B -= B.min(0) and takes ymin / ymax from the polygon)
    n = len(Q)
    iu, il = (i_hi, i_lo)
    if (iu + 1) % n != il:
        raise AdapterError('Outer-edge corners are not consecutive (outline orientation).')
    y_hi_v, y_lo_v = Q[iu][1], Q[il][1]
    # FPAD3: square the wing ends: the inner-wall end corner of each bevel moves along the inner wall to the y' of its outer corner (the engine's ARM_END_STRAIGHTEN does the same for the
    # old footprint; here it is done in the polygon so that the tab can be short). The slanted bevel is restored by clipping the panels to lay['clip_lines'] in the node.
    for i_in, i_out in (((il + 1) % n, il), ((iu - 1) % n, iu)):
        if abs(Q[i_in][0] - (wall_l + dx)) < 1e-6:
            Q[i_in] = (Q[i_in][0], Q[i_out][1])
    tot_inset = inset + dx
    new = []
    for i in range(n):
        new.append(Q[i])
        if i == iu:
            new += [(0.0, y_hi_v - jog), (tot_inset, y_hi_v - jog), (tot_inset, y_lo_v + jog), (0.0, y_lo_v + jog)]
    Q = new
    if not _is_simple(Q):
        raise AdapterError('The engine-frame polygon is not simple.')
    # start at the thick wing's outer edge (largest x', then smallest y'): far from the four junction corners (loop start must not be a fillet corner)
    st = min(range(len(Q)), key=lambda i: (-Q[i][0], Q[i][1]))
    Q = Q[st:] + Q[:st]
    mx = max(q[0] for q in Q)
    my = max(q[1] for q in Q)
    # full map user -> engine incl. the shifts: x'' = x' + dx (outer corners excepted), y'' = y' - ymin + dy
    full = (m[0], m[1], m[2], m[3], m[4] + dx, m[5] - ymin + dy)
    info = {'adapter': ADAPTER_VERSION, 'axis': lay['axis'], 'map': list(full), 'dx': dx, 'dy': dy, 'inset_m': inset, 'cap_depth_m': w0 - inset, 'thin_wing_width_at_cut_m': w0,
            'uc_kesim_payi': uc, 'corridor_width_m': lay['corridor_width'], 'corridor_length_m': lay['corridor_len'], 'thin_wing_depth_m': lay['thin_depth'],
            'thick_wing_depth_m': lay['thick_depth'], 'thin_wing_on_high_side': lay['thin_high'], 'jog_y_m': jog, 'engine_x_range': [0.0, mx], 'engine_y_range': [0.0, my],
            'wall_x_engine': [wall_l + dx, wall_r + dx], 'foot_points_x_engine': [ENGINE_FOOT_L, ENGINE_FOOT_R], 'foot_height_comp_m': list(FOOT_COMP),
            'unrounded_corners': lay['unrounded']}
    warns = []
    d_l, d_r = wall_l + dx - ENGINE_FOOT_L, ENGINE_FOOT_R - (wall_r + dx)      # how far the engine foot points lie INSIDE the wings (>= 0: foot point inside the wing)
    info['foot_point_inside_wing_m'] = [round(d_l, 2), round(d_r, 2)]
    if not (-1.5 <= d_l <= 15.0 and -1.5 <= d_r <= 15.0):
        warns.append("The bridge feet may NOT reach the ground: the engine puts its foot points at x' = %.1f / %.1f but the junction walls of this footprint are at x' = %.1f / %.1f "
                     "(foot point inside the wing by %.1f / %.1f m; usable range -1.5..15). Corridor length %.1f m (the engine layout expects about %.1f m, usable about 271..304)." %
                     (ENGINE_FOOT_L, ENGINE_FOOT_R, wall_l + dx, wall_r + dx, d_l, d_r, lay['corridor_len'], ENGINE_FOOT_R - ENGINE_FOOT_L))
    info['clip_lines'] = lay.get('clip_lines', [])
    info['cut_beyond_wing_end_m'] = round(uc - dy, 3)
    if uc - dy > 2.0:
        warns.append("The shell can only be cut %.1f m beyond the end of the wings (the engine frame leaves %.1f m behind the wing end): the outer %.1f m of the wing ends are cut straight, not slanted." % (uc - dy, dy, uc - dy))
    info['bevel_len_m'] = lay['bevel_len']
    if lay['bevel_len'] > 60.0:
        warns.append("The end bevel of the thin wing (%.1f m) is very long: the engine squares the wing end and the panels are clipped to the bevel lines in the node; check the wing ends in the dry run." % lay['bevel_len'])
    if abs(lay['corridor_width'] - 27.0) > 12.0:
        warns.append("Corridor width %.1f m is far from the 27 m this adapter was tested with (23..31 m tested)." % lay['corridor_width'])
    if abs(w0 - 46.0) > 10.0:
        warns.append("Thin wing depth %.1f m is far from the 46 m this adapter was tested with: the mouth ellipse deviates more (0.35..0.5 m measured at 40 / 54 m)." % w0)
    info['warnings'] = warns
    return Q, info


def derive(path, out_dir):
    """read the user footprint STL, recognise the I layout, write <out_dir>/<stem>.engine_<md5-8>.stl and .adapter.json. Returns (engine_stl_path, info)."""
    md5 = hashlib.md5(open(path, 'rb').read()).hexdigest()
    P, zb, zt = read_outline(path)
    lay = analyze(P)
    Q, info = build_engine_polygon(P, lay)
    stem = os.path.splitext(os.path.basename(path))[0]
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    out = os.path.join(out_dir, '%s.engine_%s.stl' % (stem, md5[:8]))
    hdr = 'MashProject8 engine-frame footprint of %s (%s, %s)' % (os.path.basename(path), md5[:8], ADAPTER_VERSION)
    cnt = write_engine_stl(out, Q, hdr)
    info.update(source=os.path.basename(path), source_md5=md5, stl_triangles=cnt,
                frame='x\' = a X + b Y + e, y\' = c X + d Y + f with map = (a, b, c, d, e, f) (pure rotation, det +1); inverse = transpose')
    info['engine_stl_md5'] = hashlib.md5(open(out, 'rb').read()).hexdigest()
    with open(os.path.splitext(out)[0] + '.adapter.json', 'w') as fh:
        json.dump(info, fh, indent=1)
    return out, info
# ==== FOOTPRINT ADAPTER END ====


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    o, i = derive(sys.argv[1], sys.argv[2])
    print('wrote', o)
    print(json.dumps({k: i[k] for k in i if k not in ('unrounded_corners', 'frame')}, indent=1))
