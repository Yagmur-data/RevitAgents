#!/usr/bin/env python3
"""make_footprint_v4.py - build the MashProject8_V4 Footprint.stl from the original MashProject8 Footprint.stl (never edits the original).

  python make_footprint_v4.py IN.stl OUT.stl [--inset M] [--jog-y Y]

WHY. The engine closes each left arm with a half-ellipse 'cap' (depth = SOL_C_DERINLIGI) that starts at the footprint's left outer edge; between that cap and the
seam-side rounding (ARM_SECTION_WIDTH) the arm section is a flat plateau, so the mouth is a stadium / rounded rectangle, never one ellipse. ONE ellipse needs
cap depth == the arm footprint width at the mouth. The original arm is 46.2 m wide and the cap 24 m deep (mouth 70.2 m wide: x -11.9 .. 58.3 at y = 30). To keep that
outer extent the footprint arm must be T/2 = 35.1 m wide and the cap 35.1 m deep: the left outer edge moves INSIDE by 46.2 - 35.1 = 11.1 m (the cap then covers what was
the outer half of the arm). Nothing else in the footprint changes (bridge, fillet corners, right body, seam).
ANCHOR. The engine normalises with B -= B.min(0); the corner (0, 488.64) is the only vertex at x = 0, so it is KEPT as a small tab behind the cut plane (the shell is cut at
y = ymax - 30 = 462.97): the left edge runs on the ORIGINAL line up to y = JOG_Y (470) and jogs to the inset edge there. Without it the whole shell would shift by 11 m in x.
VERTEX ORDER. The engine walks the boundary from trimesh's vertex 0 and its corner-fillet search rejects a loop that starts on a fillet corner, so the polygon is written starting
at the original loop start (343.4, 13.51) and the STL triangles are emitted in vertex order (checked: the engine's own loop walk starts at the same vertex as the original's).
Output: binary STL in mm like the AutoCAD original (top face z = 0.01 mm, bottom z = 0, side walls; only the top face is read by the engine). Deterministic: same input -> same bytes.
"""
import argparse
import struct
import sys

import numpy as np
import trimesh


def loop_from_stl(path):
    m = trimesh.load(path, force='mesh', process=True)
    V, F = m.vertices, m.faces
    zmax = V[:, 2].max()
    Ft = F[np.all(np.isclose(V[F, 2], zmax, atol=1e-6), axis=1)]
    E = np.vstack([Ft[:, [0, 1]], Ft[:, [1, 2]], Ft[:, [2, 0]]])
    _, ids, cnt = np.unique(np.sort(E, 1), axis=0, return_index=True, return_counts=True)
    BE = E[ids[cnt == 1]]
    adj = {}
    for a, b in BE:
        adj.setdefault(int(a), []).append(int(b))
        adj.setdefault(int(b), []).append(int(a))
    start = int(BE[0, 0])
    loop, prev, cur = [start], -1, start
    while True:
        j = [k for k in adj[cur] if k != prev][0]
        if j == start:
            break
        loop.append(j)
        prev, cur = cur, j
    return V[loop, :2].copy(), float(V[:, 2].min()), float(zmax)


def area2(p):
    return float(np.sum(p[:, 0] * np.roll(p[:, 1], -1) - p[:, 1] * np.roll(p[:, 0], -1)))


def ear_clip(P):
    """triangulate a simple CCW polygon (n,2) -> list of (i,j,k)."""
    idx = list(range(len(P)))
    tris = []

    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def inside(p, a, b, c):
        return cross(a, b, p) >= -1e-12 and cross(b, c, p) >= -1e-12 and cross(c, a, p) >= -1e-12
    guard = 0
    while len(idx) > 3 and guard < 100000:
        guard += 1
        n = len(idx)
        for k in range(n):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % n]
            a, b, c = P[i0], P[i1], P[i2]
            if cross(a, b, c) <= 1e-9:
                continue
            if any(inside(P[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2))
            idx.pop(k)
            break
        else:
            raise RuntimeError('ear clipping failed (polygon not simple?)')
    tris.append(tuple(idx))
    return tris


def seg_intersect(a, b, c, d):
    def cr(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    d1, d2, d3, d4 = cr(c, d, a), cr(c, d, b), cr(a, b, c), cr(a, b, d)
    return (d1 * d2 < 0) and (d3 * d4 < 0)


def is_simple(P):
    n = len(P)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(i - j) in (1, n - 1):
                continue
            if seg_intersect(P[i], P[(i + 1) % n], P[j], P[(j + 1) % n]):
                return False
    return True


def write_stl(path, P, z0, z1, header):
    tris = ear_clip(P)
    # the engine starts its boundary walk at trimesh's vertex 0 and its corner-fillet search does not accept a loop that starts ON a fillet
    # corner (index wrap): emit the triangles so that polygon vertex 0 (= the original loop start) is also the first vertex of the STL.
    tris = [tuple(t[k:] + t[:k]) for t in tris for k in [t.index(min(t))]]
    tris.sort(key=lambda t: t)
    out = []

    def add(a, b, c):
        out.append((a, b, c))
    for i, j, k in tris:   # top (CCW seen from +z)
        add((*P[i], z1), (*P[j], z1), (*P[k], z1))
        add((*P[k], z0), (*P[j], z0), (*P[i], z0))
    n = len(P)
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        add((*a, z0), (*b, z0), (*b, z1))
        add((*a, z0), (*b, z1), (*a, z1))
    with open(path, 'wb') as fh:
        fh.write(header.encode('ascii', 'replace')[:80].ljust(80, b'\0'))
        fh.write(struct.pack('<I', len(out)))
        for t in out:
            a, b, c = (np.array(v, float) for v in t)
            nrm = np.cross(b - a, c - a)
            ln = np.linalg.norm(nrm)
            nrm = nrm / ln if ln > 0 else nrm
            fh.write(struct.pack('<12fH', *nrm, *a, *b, *c, 0))
    return len(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--inset', type=float, default=11.1, help='metres the left outer arm edge moves inside (default 11.1)')
    ap.add_argument('--jog-y', type=float, default=470.0, help='y (m, footprint frame) where the kept corner tab ends (default 470)')
    a = ap.parse_args()
    P, z0, z1 = loop_from_stl(a.src)
    if area2(P) < 0:
        P = P[::-1]
    Pm = P * 0.001
    mn = Pm.min(0)
    Q = Pm - mn                                  # engine frame: min x = min y = 0
    n = len(Q)
    iA = int(np.argmin(Q[:, 0]))                 # (0, 488.64) the anchor corner
    nxt = (iA + 1) % n
    iB = int(np.argmin(Q[:, 1] + 1e6 * (Q[:, 0] > 100)))   # (12.86, 0): lowest vertex of the left arm
    if nxt != iB:
        raise SystemExit('left edge is not (corner, bottom-left) in this order - unexpected footprint (A=%d next=%d B=%d)' % (iA, nxt, iB))
    A, B = Q[iA], Q[iB]
    slope = (A[0] - B[0]) / (A[1] - B[1])        # dx/dy of the left edge
    xe = lambda y: B[0] + (y - B[1]) * slope     # noqa: E731
    jy = float(a.jog_y)
    new = []
    for i in range(n):
        if i == iB:
            new.append((B[0] + a.inset, B[1]))
        else:
            new.append(tuple(Q[i]))
        if i == iA:
            new.append((xe(jy), jy))                    # back on the ORIGINAL left edge
            new.append((xe(jy) + a.inset, jy))          # jog to the inset edge
    N = np.array(new)
    if not is_simple(N):
        raise SystemExit('modified polygon is not simple')
    if abs(area2(N)) > abs(area2(Q)):
        raise SystemExit('area grew - unexpected')
    abs_pts = (N + mn) * 1000.0                  # back to the original absolute mm frame
    hdr = 'MashProject8_V4 footprint: left arm outer edge inset %.2f m (see make_footprint_v4.py)' % a.inset
    cnt = write_stl(a.dst, abs_pts, z0, z1, hdr)
    print('wrote %s  (%d vertices, %d STL triangles, area %.1f -> %.1f m2, inset %.2f m, jog at y=%.1f)' %
          (a.dst, len(N), cnt, abs(area2(Q)) / 2, abs(area2(N)) / 2, a.inset, jy))
    return 0


if __name__ == '__main__':
    sys.exit(main())
