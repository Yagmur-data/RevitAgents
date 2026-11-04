#!/usr/bin/env python3
"""mp8v4_measure.py - numbers for the two MashProject8_V4 complaints, measured on an engine shell STL (offline, no Revit).

  python mp8v4_measure.py mouth STL [STL ...]     left-arm mouth loops (y = 30 / y = 463) vs the best-fit ellipse
  python mp8v4_measure.py feet  STL [STL ...]     bridge-underside / ground contact at the LEFT and RIGHT bridge feet
  python mp8v4_measure.py all   STL [STL ...]     both, one line per STL

Mouth:  the open boundary loop of the shell at the arm end cut (x,z plane). An ellipse (centre xc,zc, semi-axes A,B, axis aligned,
        optional free rotation) is fitted by least squares on the Sampson distance; reported: max / rms deviation of the loop from the
        ellipse in metres, the same as % of the semi-minor axis B, and the worst ellipse part not covered by the loop (Hausdorff).
Feet:   the ground is z = 0. For slices x = XS the lowest shell z on the bridge centre line (|y - yc| < 0.6 m), the lowest z of the
        whole bridge band and the y-width of the shell below z <= CONTACT (0.30 m); 'foot_floor_*' summarises the junction slices.

Library use: `import mp8v4_measure as M; M.mouth_report(mesh)` / `M.feet_report(mesh)` (trimesh meshes).
"""
import sys

import numpy as np
import trimesh
from scipy.optimize import least_squares

# bridge plan line (Engine_Source: kopru_orta_y) and the junction x of the footprint bridge corners (e = 12 included)
_XL, _YL = 0.5 * ((61.01 - 12) + (59.64 - 12)), 0.5 * ((219.64 - 12) + (271.85 + 12))
_XR, _YR = 0.5 * ((338.83 + 12) + (336.49 + 12)), 0.5 * ((218.39 - 12) + (287.59 + 12))
CONTACT = 0.30


CFG = {'yc_const': None, 'left_wall': 58.0, 'right_wall': 337.0, 'bridge_x0': 60.0, 'bridge_x1': 337.0}


def configure(yc=None, left_wall=58.0, right_wall=337.0):
    """layout of the shell being measured: bridge centre line (None = the old footprint's sloping line, else a constant y), arm-wall x of the left / right junction."""
    CFG.update(yc_const=yc, left_wall=left_wall, right_wall=right_wall, bridge_x0=left_wall + 2.0, bridge_x1=right_wall)


def yc(x):
    if CFG['yc_const'] is not None:
        return np.full_like(np.asarray(x, float), CFG['yc_const'])
    q = np.clip((np.asarray(x, float) - _XL) / (_XR - _XL), 0, 1)
    return _YL + q * (_YR - _YL)


def load(path):
    return trimesh.load(path, process=True)


def boundary_loops(mesh):
    F, V = mesh.faces, mesh.vertices
    e = np.sort(np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), axis=1)
    u, c = np.unique(e, axis=0, return_counts=True)
    be = u[c == 1]
    nxt = {}
    for a, b in be:
        nxt.setdefault(int(a), []).append(int(b))
        nxt.setdefault(int(b), []).append(int(a))
    seen, loops = set(), []
    for s in nxt:
        if s in seen:
            continue
        loop, prev, cur = [s], -1, s
        seen.add(s)
        while True:
            cand = [j for j in nxt[cur] if j != prev]
            if not cand:
                break
            j = cand[0]
            if j == s:
                break
            loop.append(j)
            seen.add(j)
            prev, cur = cur, j
            if len(loop) > len(nxt) + 2:
                break
        loops.append(np.asarray(loop))
    return [V[l] for l in loops]


def mouth_loop(mesh, which='front'):
    """left-arm end loop: 'front' (y ~ 30) or 'back' (y ~ ymax-30). Points are (x, y, z) in metres, in boundary order."""
    best = None
    for lp in boundary_loops(mesh):
        ym, xm = lp[:, 1].mean(), lp[:, 0].mean()
        if xm > 150 or np.ptp(lp[:, 1]) > 2.0:
            continue
        if (which == 'front' and ym < 100) or (which == 'back' and ym > 300):
            best = lp
    if best is None:
        raise ValueError('mouth loop not found: ' + which)
    return best


def _ell_pts(p, n=6000):
    xc, zc, A, B, th = p
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x, z = A * np.cos(t), B * np.sin(t)
    c, s = np.cos(th), np.sin(th)
    return np.c_[xc + c * x - s * z, zc + s * x + c * z]


def _sampson(p, pts):
    xc, zc, A, B, th = p
    c, s = np.cos(th), np.sin(th)
    dx, dz = pts[:, 0] - xc, pts[:, 1] - zc
    u, v = c * dx + s * dz, -s * dx + c * dz
    f = (u / A) ** 2 + (v / B) ** 2 - 1.0
    gu, gv = 2 * u / A ** 2, 2 * v / B ** 2
    return f / np.maximum(np.hypot(gu, gv), 1e-9)


def fit_ellipse(pts, free_rotation=False, seed=None):
    """pts (n,2) -> params (xc, zc, A, B, theta), exact distances. Sampson least squares (robust soft_l1-free: plain)."""
    x0 = np.r_[0.5 * (pts[:, 0].min() + pts[:, 0].max()), 0.5 * (pts[:, 1].min() + pts[:, 1].max()),
               0.5 * np.ptp(pts[:, 0]), 0.5 * np.ptp(pts[:, 1]), 0.0] if seed is None else np.asarray(seed, float)
    if free_rotation:
        r = least_squares(lambda q: _sampson(q, pts), x0)
        p = r.x
    else:
        r = least_squares(lambda q: _sampson(np.r_[q, 0.0], pts), x0[:4])
        p = np.r_[r.x, 0.0]
    return p


def exact_dev(p, pts):
    """exact signed distance of pts to the ellipse curve (outside +), by dense sampling, plus the reverse Hausdorff."""
    e = _ell_pts(p)
    from scipy.spatial import cKDTree
    d, _ = cKDTree(e).query(pts)
    xc, zc, A, B, th = p
    c, s = np.cos(th), np.sin(th)
    dx, dz = pts[:, 0] - xc, pts[:, 1] - zc
    u, v = c * dx + s * dz, -s * dx + c * dz
    sign = np.where((u / A) ** 2 + (v / B) ** 2 >= 1.0, 1.0, -1.0)
    d2, _ = cKDTree(pts).query(e)
    return sign * d, float(d2.max())


def mouth_report(mesh, which='front', free_rotation=False):
    lp = mouth_loop(mesh, which)
    pts = lp[:, [0, 2]]
    p = fit_ellipse(pts, free_rotation)
    dev, back = exact_dev(p, pts)
    xc, zc, A, B, th = p
    return dict(loop=which, n=len(pts), xc=float(xc), zc=float(zc), A=float(A), B=float(B), theta_deg=float(np.degrees(th)),
                width=float(np.ptp(pts[:, 0])), height=float(np.ptp(pts[:, 1])),
                max_dev_m=float(np.abs(dev).max()), rms_dev_m=float(np.sqrt(np.mean(dev ** 2))),
                max_dev_pct_B=float(np.abs(dev).max() / B * 100), max_dev_pct_mean_radius=float(np.abs(dev).max() / (0.5 * (A + B)) * 100),
                ellipse_uncovered_m=back, y_plane=float(lp[:, 1].mean()))


def silhouette_points(mesh, x_max=56.0, grid=0.2):
    """end-on (looking along y) outline of the LEFT ARM tube: triangles with every vertex x < x_max, rasterised; outline pixel centres (x, z)."""
    from PIL import Image, ImageDraw
    V, F = mesh.vertices, mesh.faces
    F = F[(V[F, 0].max(axis=1) < x_max)]
    X, Z = V[F][:, :, 0], V[F][:, :, 2]
    x0, z0 = X.min() - 1, Z.min() - 1
    W, H = int((X.max() - x0 + 1) / grid) + 2, int((Z.max() - z0 + 1) / grid) + 2
    im = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(im)
    for t in range(len(F)):
        dr.polygon([((X[t, k] - x0) / grid, (Z[t, k] - z0) / grid) for k in range(3)], fill=255)
    m = np.asarray(im) > 0
    er = m.copy()
    er[1:-1, 1:-1] = m[1:-1, 1:-1] & m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:]
    ys, xs = np.nonzero(m & ~er)
    return np.c_[x0 + (xs + 0.5) * grid, z0 + (ys + 0.5) * grid]


def silhouette_report(mesh, x_max=56.0):
    pts = silhouette_points(mesh, x_max)
    p = fit_ellipse(pts)
    dev, back = exact_dev(p, pts)
    xc, zc, A, B, th = p
    return dict(xc=float(xc), zc=float(zc), A=float(A), B=float(B), width=float(np.ptp(pts[:, 0])), height=float(np.ptp(pts[:, 1])),
                max_dev_m=float(np.abs(dev).max()), rms_dev_m=float(np.sqrt(np.mean(dev ** 2))),
                max_dev_pct_B=float(np.abs(dev).max() / B * 100), ellipse_uncovered_m=back)


XS_FEET = (30, 40, 48, 58, 70, 90, 110, 150, 200, 250, 290, 315, 330, 337, 345, 360, 375)


def slice_stats(V, x0, half=0.6, ystrip=None):
    """lowest z on the bridge centre line, lowest z of the whole slice band, y-width below CONTACT and the z-range of that slice."""
    y0 = float(yc(x0))
    sel = np.abs(V[:, 0] - x0) < half
    cl = sel & (np.abs(V[:, 1] - y0) < 0.6)
    if ystrip is None:
        ystrip = 60.0
    band = sel & (np.abs(V[:, 1] - y0) < ystrip)
    zc = V[cl, 2]
    zb = V[band, 2]
    if len(zb) == 0:
        return None
    # y-width of the shell below CONTACT: lowest z per 0.5 m y-bin
    yb = np.floor((V[band, 1] - (y0 - ystrip)) / 0.5).astype(int)
    low = {}
    for b, z in zip(yb, zb):
        if b not in low or z < low[b]:
            low[b] = z
    width = 0.5 * sum(1 for z in low.values() if z <= CONTACT)
    return dict(x=float(x0), yc=y0, bottom_centre=float(zc.min()) if len(zc) else float('nan'), bottom_band=float(zb.min()),
                top_centre=float(zc.max()) if len(zc) else float('nan'), contact_width_m=float(width),
                width_below_1m=float(0.5 * sum(1 for z in low.values() if z <= 1.0)))


def feet_report(mesh, xs=XS_FEET):
    V = mesh.vertices
    rows = [slice_stats(V, x) for x in xs]
    rows = [r for r in rows if r]
    by = {int(r['x']): r for r in rows}
    # junction slices: the bridge starts at the arm seam (x ~ 58 left, ~337 right)
    lw, rw = CFG['left_wall'], CFG['right_wall']
    left = [r for r in rows if lw - 8 <= r['x'] <= lw + 14]
    right = [r for r in rows if rw - 12 <= r['x'] <= rw + 8]
    out = dict(rows=rows,
               foot_floor_left=min(r['bottom_band'] for r in left) if left else None,
               foot_floor_right=min(r['bottom_band'] for r in right) if right else None,
               foot_centre_left=min(r['bottom_centre'] for r in left) if left else None,
               foot_centre_right=min(r['bottom_centre'] for r in right) if right else None,
               contact_left=max(r['contact_width_m'] for r in left) if left else None,
               contact_right=max(r['contact_width_m'] for r in right) if right else None)
    return out


def _fmt(d):
    return '  '.join('%s %s' % (k, ('%.2f' % v) if isinstance(v, float) else v) for k, v in d.items())


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ('mouth', 'feet', 'all', 'sil'):
        print(__doc__)
        return 2
    mode = sys.argv[1]
    for path in sys.argv[2:]:
        m = load(path)
        print('==', path, '| %d triangles | bbox z %.2f..%.2f' % (len(m.faces), m.vertices[:, 2].min(), m.vertices[:, 2].max()))
        if mode in ('mouth', 'all'):
            for w in ('front', 'back'):
                r = mouth_report(m, w)
                print('  mouth', _fmt({k: r[k] for k in ('loop', 'width', 'height', 'xc', 'zc', 'A', 'B', 'max_dev_m', 'max_dev_pct_B', 'rms_dev_m', 'ellipse_uncovered_m')}))
        if mode in ('sil', 'all'):
            print('  silhouette', _fmt(silhouette_report(m)))
        if mode in ('feet', 'all'):
            f = feet_report(m)
            for r in f['rows']:
                print('  x %5.0f  bottom centre %6.2f  band %6.2f  top centre %6.2f  width<=%.2f m: %5.1f  width<=1 m: %5.1f' %
                      (r['x'], r['bottom_centre'], r['bottom_band'], r['top_centre'], CONTACT, r['contact_width_m'], r['width_below_1m']))
            print('  FEET  left floor %.2f (centre %.2f, contact %.1f m)  right floor %.2f (centre %.2f, contact %.1f m)' %
                  (f['foot_floor_left'], f['foot_centre_left'], f['contact_left'], f['foot_floor_right'], f['foot_centre_right'], f['contact_right']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
