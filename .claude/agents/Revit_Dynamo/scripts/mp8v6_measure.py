#!/usr/bin/env python3
"""mp8v6_measure.py - numbers for the MashProject8 v15 round (Al's 4 notes of 2026-10-14), measured on an engine shell STL or the panels (.bkl) in the frame of
Al's footprint STL. Offline, no Revit, no Dynamo.

  python mp8v6_measure.py plan   SHELL.stl ADAPTER.json FOOTPRINT.stl [--res 0.25]     plan outline of the shell vs the footprint outline (gap list, dent components)
  python mp8v6_measure.py bridge SHELL.stl ADAPTER.json                                 bridge section (width x height, circle deviation) per Y along the corridor + underside profile

Library use (the preview and selftest scripts import it): load_user_mesh, plan_compare, corridor_edges, bridge_sections, underside_profile.
Frame: the engine STL is rotated back to the footprint frame with the adapter record's map (x' = a X + b Y + e, y' = c X + d Y + f; inverse = transpose).
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import footprint_adapter as FA  # noqa: E402


def read_stl(path):
    data = open(path, 'rb').read()
    n = int(np.frombuffer(data[80:84], '<u4')[0])
    a = np.frombuffer(data[84:84 + 50 * n], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
    return a['v'].astype(np.float64)       # (n, 3, 3)


def to_user_xy(m, x, y):
    u, v = x - m[4], y - m[5]
    return m[0] * u + m[2] * v, m[1] * u + m[3] * v


def load_user_mesh(stl_path, adapter_json):
    """triangles (n,3,3) in the footprint frame (X, Y, Z in metres)."""
    ad = json.load(open(adapter_json))
    T = read_stl(stl_path)
    X, Y = to_user_xy(ad['map'], T[:, :, 0], T[:, :, 1])
    U = T.copy()
    U[:, :, 0], U[:, :, 1] = X, Y
    return U, ad


def footprint_outline(path):
    P, zb, zt = FA.read_outline(path)
    return np.array(P)


def raster_polys(polys, res, x0, y0, W, H):
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    for p in polys:
        d.polygon([((q[0] - x0) / res, (q[1] - y0) / res) for q in p], fill=1)
    return np.asarray(im).astype(bool)


def shell_mask(U, res, x0, y0, W, H):
    sel = U[:, :, 2].mean(axis=1) > -1e9
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    xs = (U[sel][:, :, 0] - x0) / res
    ys = (U[sel][:, :, 1] - y0) / res
    for i in range(len(xs)):
        d.polygon([(xs[i, 0], ys[i, 0]), (xs[i, 1], ys[i, 1]), (xs[i, 2], ys[i, 2])], fill=1)
    return np.asarray(im).astype(bool)


def plan_compare_mask(S, P, res=0.25, tol=0.5, cut=(30.0, 450.0), x0=-30.0, y0=-20.0):
    """same as plan_compare but with a ready shell/panel plan mask S (bool grid, origin x0/y0, cell res)."""
    H, W = S.shape
    T = raster_polys([P], res, x0, y0, W, H)
    dT = ndimage.distance_transform_edt(~T) * res
    dS = ndimage.distance_transform_edt(~S) * res
    over = S & ~T & (dT > tol)
    under = T & ~S & (dS > tol)
    out = dict(res=res, x0=x0, y0=y0, S=S, T=T, over=over, under=under, dT=dT, dS=dS)
    out['area_S'] = float(S.sum() * res * res)
    out['area_T'] = float(T.sum() * res * res)
    out['area_over'] = float(over.sum() * res * res)
    out['area_under'] = float(under.sum() * res * res)
    out['comps'] = components(out, tol, cut)
    return out


def plan_compare(U, P, res=0.25, tol=0.5, cut=(30.0, 450.0)):
    """shell plan mask S vs footprint mask T. Returns dict with grids and components of (S xor T) pixels farther than `tol` m from the other outline."""
    x0, y0 = -30.0, -20.0
    W, H = int((540.0 - x0) / res), int((560.0 - y0) / res)
    S = shell_mask(U, res, x0, y0, W, H)
    S = ndimage.binary_closing(S, iterations=2)          # 2 px = 0.5 m: closes the 1-pixel seams between rasterised triangles
    T = raster_polys([P], res, x0, y0, W, H)
    dT = ndimage.distance_transform_edt(~T) * res         # distance to the footprint area (outside pixels)
    dTi = ndimage.distance_transform_edt(T) * res         # distance to the footprint boundary (inside pixels)
    dS = ndimage.distance_transform_edt(~S) * res
    dSi = ndimage.distance_transform_edt(S) * res
    over = S & ~T & (dT > tol)                            # shell beyond the footprint outline by more than tol
    under = T & ~S & (dS > tol)                           # footprint area without shell, farther than tol from any shell
    out = dict(res=res, x0=x0, y0=y0, S=S, T=T, over=over, under=under, dT=dT, dS=dS)
    out['area_S'] = float(S.sum() * res * res)
    out['area_T'] = float(T.sum() * res * res)
    out['area_over'] = float(over.sum() * res * res)
    out['area_under'] = float(under.sum() * res * res)
    out['comps'] = components(out, tol, cut)
    return out


def components(pc, tol, cut):
    res, x0, y0 = pc['res'], pc['x0'], pc['y0']
    res_l = []
    for kind, M, D in (('over', pc['over'], pc['dT']), ('under', pc['under'], pc['dS'])):
        lab, n = ndimage.label(M)
        for k in range(1, n + 1):
            sel = lab == k
            area = float(sel.sum() * res * res)
            if area < 4.0:
                continue
            yy, xx = np.nonzero(sel)
            cx, cy = x0 + (xx.mean() + 0.5) * res, y0 + (yy.mean() + 0.5) * res
            res_l.append(dict(kind=kind, area=round(area, 1), cx=round(cx, 1), cy=round(cy, 1), depth=round(float(D[sel].max()), 2),
                              x=(round(x0 + xx.min() * res, 1), round(x0 + (xx.max() + 1) * res, 1)), y=(round(y0 + yy.min() * res, 1), round(y0 + (yy.max() + 1) * res, 1))))
    res_l.sort(key=lambda c: -c['area'])
    return res_l


def corridor_edges(pc, ys=range(150, 441, 10)):
    """shell plan extent across the corridor (X of the left/right plan edge in the band 150..300) per Y: only the corridor part near x = 240 is read."""
    res, x0, y0 = pc['res'], pc['x0'], pc['y0']
    S = pc['S']
    rows = []
    for Y in ys:
        r = int((Y - y0) / res)
        row = S[r]
        cx = int((240.0 - x0) / res)
        if not row[cx]:
            rows.append((Y, None, None))
            continue
        a = cx
        while a > 0 and row[a - 1]:
            a -= 1
        b = cx
        while b < len(row) - 1 and row[b + 1]:
            b += 1
        rows.append((Y, round(x0 + a * res, 2), round(x0 + (b + 1) * res, 2)))
    return rows


def sections_at(U, Ys, half=0.6, xr=(150.0, 330.0)):
    """YZ... for the corridor the sections are X-Z planes: for each Y return vertices of triangles' vertices within |Y - y| < half and X in xr."""
    V = U.reshape(-1, 3)
    out = {}
    for y in Ys:
        s = (np.abs(V[:, 1] - y) < half) & (V[:, 0] > xr[0]) & (V[:, 0] < xr[1])
        out[y] = V[s]
    return out


def bridge_sections(U, Ys=range(160, 441, 20)):
    """per Y: top z / bottom z on the centre line (x = 240), plan width (max X - min X of the section), height, centre z, aspect."""
    rows = []
    for y, S in sections_at(U, Ys).items():
        if len(S) < 10:
            rows.append(dict(y=y))
            continue
        c = np.abs(S[:, 0] - 240.0) < 0.8
        top = float(S[c, 2].max()) if c.any() else float('nan')
        bot = float(S[c, 2].min()) if c.any() else float('nan')
        w = float(S[:, 0].max() - S[:, 0].min())
        rows.append(dict(y=y, top=round(top, 2), bottom=round(bot, 2), height=round(top - bot, 2), width=round(w, 2), zc=round(0.5 * (top + bot), 2)))
    return rows


def underside_profile(U, Ys):
    """lowest z of the shell on the bridge centre line (|x - 240| < 0.8) per Y (ground = 0)."""
    V = U.reshape(-1, 3)
    c = np.abs(V[:, 0] - 240.0) < 0.8
    Vc = V[c]
    prof = []
    for y in Ys:
        s = np.abs(Vc[:, 1] - y) < 0.6
        prof.append((float(y), float(Vc[s, 2].min()) if s.any() else float('nan'), float(Vc[s, 2].max()) if s.any() else float('nan')))
    return prof


def read_bkl(path):
    """BAKLAVA_PANELS.bkl -> (n_sub, rh (nr,(n+1)^2,3), tr (nt,(n+1)(n+2)/2,3)) float64 metres, engine frame."""
    data = open(path, 'rb').read()
    assert data[:4] == b'BKLV'
    ver, n, nr, nt = np.frombuffer(data[4:20], '<u4')
    n, nr, nt = int(n), int(nr), int(nt)
    pr, pt = (n + 1) * (n + 1), (n + 1) * (n + 2) // 2
    a = np.frombuffer(data[20:], dtype='<f4').astype(np.float64).reshape(-1, 3)
    assert len(a) == nr * pr + nt * pt
    return n, a[:nr * pr].reshape(nr, pr, 3), a[nr * pr:].reshape(nt, pt, 3)


def bkl_to_user(path, adapter_json):
    n, rh, tr = read_bkl(path)
    m = json.load(open(adapter_json))['map']
    for arr in (rh, tr):
        arr[..., 0], arr[..., 1] = to_user_xy(m, arr[..., 0], arr[..., 1])
    return n, rh, tr


def panel_corner_sets(n, rh, tr):
    """corner points: rhombi (nr,4,3) in ring order, triangles (nt,3,3)."""
    ri = [0, n, (n + 1) * (n + 1) - 1, n * (n + 1)]
    ti = [0, n, (n + 1) * (n + 2) // 2 - 1]
    return rh[:, ri, :], tr[:, ti, :]


def rim_points(n, rh, tr, plane_origin, plane_normal, tol=0.06):
    """all panel grid points within tol of the (vertical) cut plane: plan point + normal (nx, ny)."""
    P = np.vstack([rh.reshape(-1, 3), tr.reshape(-1, 3)])
    d = (P[:, 0] - plane_origin[0]) * plane_normal[0] + (P[:, 1] - plane_origin[1]) * plane_normal[1]
    return P[np.abs(d) < tol]


def foot_angles(U, y_lo=150.0, y_hi=440.0, step=2.0):
    """underside z on the bridge centre line per Y (2 m steps) and its slope angle (deg) -> dict with the profile, the steepest angle at the left (thin wing, Y ~ 438) and right (thick wing, Y ~ 152) foot
    and the length of the part of each ramp within 1.5 deg of its steepest angle (a constant-angle ramp has a long plateau)."""
    Ys = np.arange(y_lo, y_hi + 1e-6, step)
    prof = underside_profile(U, Ys)
    z = np.array([p[1] for p in prof])
    ang = np.degrees(np.arctan2(np.gradient(z, Ys), 1.0))
    out = dict(Y=Ys, z=z, angle=ang)
    mid = 0.5 * (y_lo + y_hi)
    for nm, sel in (('thin_foot', Ys > mid), ('thick_foot', Ys <= mid)):
        a = np.abs(ang[sel])
        a_s = np.convolve(a, np.ones(3) / 3.0, mode='same')
        k = int(np.argmax(a_s))
        mx = float(a_s[k])
        out[nm] = dict(max_angle=round(mx, 1), plateau_len=round(float((a_s >= mx - 1.5).sum() * step), 1), y_at_max=round(float(Ys[sel][k]), 1))
    return out


def main():
    a = sys.argv[1:]
    if len(a) < 3 or a[0] not in ('plan', 'bridge'):
        print(__doc__)
        return 2
    U, ad = load_user_mesh(a[1], a[2])
    if a[0] == 'plan':
        P = footprint_outline(a[3])
        pc = plan_compare(U, P)
        print('shell area %.0f m2, footprint %.0f m2, overshoot > 0.5 m %.0f m2, missing > 0.5 m %.0f m2' % (pc['area_S'], pc['area_T'], pc['area_over'], pc['area_under']))
        for c in pc['comps'][:20]:
            print(c)
        print('corridor edges (Y, left X, right X); footprint 226.5 / 253.5')
        for r in corridor_edges(pc):
            print(r)
    else:
        for r in bridge_sections(U):
            print(r)
    return 0


if __name__ == '__main__':
    sys.exit(main())


def slice_plane_y(U, y0):
    """intersection points (X, Z) of the plane Y = y0 with the triangle edges (vectorised)."""
    s = U[:, :, 1] - y0
    pts = []
    for a, b in ((0, 1), (1, 2), (2, 0)):
        sa, sb = s[:, a], s[:, b]
        m = (sa * sb) < 0
        t = sa[m] / (sa[m] - sb[m])
        A, B = U[m][:, a, :], U[m][:, b, :]
        P = A + (B - A) * t[:, None]
        pts.append(P[:, [0, 2]])
    return np.vstack(pts)


def section_ellipse(U, y0, x_lo=200.0, x_hi=280.0):
    """bridge section at Y = y0 (points with x in x_lo..x_hi): best-fit axis-aligned ellipse (centre, A = half width, B = half height), max deviation (m) and the lowest / highest z."""
    from scipy.optimize import least_squares
    P = slice_plane_y(U, y0)
    P = P[(P[:, 0] > x_lo) & (P[:, 0] < x_hi)]
    f = lambda p: (np.hypot((P[:, 0] - p[0]) / p[2], (P[:, 1] - p[1]) / p[3]) - 1.0) * np.sqrt(p[2] * p[3])
    s = least_squares(f, [P[:, 0].mean(), P[:, 1].mean(), np.ptp(P[:, 0]) / 2, np.ptp(P[:, 1]) / 2])
    r = f(s.x)
    return dict(centre=(round(float(s.x[0]), 2), round(float(s.x[1]), 2)), A=round(float(s.x[2]), 2), B=round(float(s.x[3]), 2), max_dev=round(float(np.abs(r).max()), 3), z_min=round(float(P[:, 1].min()), 2), z_max=round(float(P[:, 1].max()), 2))


# ---------------------------------------------------------------------------------------------------------------------------------------------
# end-on view of an arm: mouth rim vs see-through APERTURE (Al's screenshot of the left end shows the aperture, not the rim)
# ---------------------------------------------------------------------------------------------------------------------------------------------
NB_AP = 360


def slice_plane_x(U, x0):
    """intersection points (Y, Z) of the plane X = x0 with the triangle edges (vectorised)."""
    s = U[:, :, 0] - x0
    pts = []
    for a, b in ((0, 1), (1, 2), (2, 0)):
        sa, sb = s[:, a], s[:, b]
        m = (sa * sb) < 0
        t = sa[m] / (sa[m] - sb[m])
        A, B = U[m][:, a, :], U[m][:, b, :]
        P = A + (B - A) * t[:, None]
        pts.append(P[:, 1:3])
    return np.vstack(pts)


def radial_profile(P, c, y_keep=437.0, nb=NB_AP):
    """radius of the (single, star-shaped) section loop about c per angle bin; P = (Y,Z) points, only Y > y_keep (the thin wing; the corridor opening is excluded)."""
    q = P[P[:, 0] > y_keep]
    ang = np.arctan2(q[:, 1] - c[1], q[:, 0] - c[0])
    r = np.hypot(q[:, 0] - c[0], q[:, 1] - c[1])
    o = np.argsort(ang)
    ang, r = ang[o], r[o]
    th = (np.arange(nb) + 0.5) / nb * 2 * np.pi - np.pi
    return th, np.interp(th, np.r_[ang - 2 * np.pi, ang, ang + 2 * np.pi], np.r_[r, r, r])


def fit_ellipse_pts(P):
    from scipy.optimize import least_squares
    f = lambda p: (np.hypot((P[:, 0] - p[0]) / p[2], (P[:, 1] - p[1]) / p[3]) - 1.0) * np.sqrt(p[2] * p[3])
    s = least_squares(f, [P[:, 0].mean(), P[:, 1].mean(), np.ptp(P[:, 0]) / 2, np.ptp(P[:, 1]) / 2])
    return s.x, f(s.x)


def aperture_curves(U, xs=None, c=(473.0, 21.5), skip=(222.0, 258.0)):
    """radial profiles of the arm sections at X = xs (default 30.5..450 step 10, the bridge junction slices skipped). Returns (theta, R (n_slices, nb), used_x).
    rim = R[0] (mouth), aperture = R.min(axis=0): the see-through hole = intersection of all sections."""
    xs = np.arange(30.5, 450, 10.0) if xs is None else xs
    R, used = [], []
    for x0 in xs:
        if skip[0] < x0 < skip[1]:
            continue
        th, r = radial_profile(slice_plane_x(U, x0), c)
        R.append(r)
        used.append(float(x0))
    return th, np.array(R), used


def describe_curve(th, r, c):
    P = np.c_[c[0] + r * np.cos(th), c[1] + r * np.sin(th)]
    p, res = fit_ellipse_pts(P)
    out = dict(centre=(round(float(p[0]), 2), round(float(p[1]), 2)), A=round(float(p[2]), 2), B=round(float(p[3]), 2), max_dev=round(float(np.abs(res).max()), 3),
               max_dev_pct_B=round(float(np.abs(res).max() / p[3] * 100), 2), rms=round(float(np.sqrt((res ** 2).mean())), 3), height=round(float(np.ptp(P[:, 1])), 2), width=round(float(np.ptp(P[:, 0])), 2))
    for nm, Q in (('top', P[P[:, 1] > p[1]]), ('bottom', P[P[:, 1] <= p[1]])):
        q, rr = fit_ellipse_pts(Q)
        out[nm] = dict(B=round(float(q[3]), 2), rms=round(float(np.sqrt((rr ** 2).mean())), 3))
    return out, P


def image_contour(path):
    """contour pixels (x, y_down) of a thin-line ellipse screenshot (Al's 5.png): per column top/bottom dark pixel + per row left/right, grid lines / cross-hair removed."""
    from PIL import Image
    im = np.asarray(Image.open(path).convert('L')).astype(float)
    dark = im < 160
    pts = []
    for x in range(36, 525):
        if abs(x - 272) <= 1:
            continue
        col = np.nonzero(dark[140:460, x])[0] + 140
        col = col[np.abs(col - 301) > 1]
        if len(col):
            pts += [(x, col.min()), (x, col.max())]
    for y in range(150, 448):
        if abs(y - 301) <= 1:
            continue
        row = np.nonzero(dark[y, 30:520])[0] + 30
        row = row[(np.abs(row - 272) > 1) & (np.abs(row - 22) > 3) & (np.abs(row - 530) > 3)]
        if len(row) > 0 and (row.min() < 80 or row.max() > 480):
            if row.min() < 80:
                pts.append((row.min(), y))
            if row.max() > 480:
                pts.append((row.max(), y))
    return np.array(pts, float)
