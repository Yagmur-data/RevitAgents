#!/usr/bin/env python3
"""mp8v5_variants.py - robustness test of the footprint adapter: synthetic variants of Al's 'I' footprint (corridor width / position, wing depths, wing length, bevel) go through the
REAL node (MashProject8_v14.dyn via engine_capture.py: adapter -> real MashEngine.exe -> panels mapped back) and are measured. No Revit.

  python mp8v5_variants.py OUTROOT [--workers 4] [--only v0,v1,...] [--no-panels-metrics]

Per variant: node status / warnings / engine error text, panels (count, quality), and from the shell STL (kept with KEEP_STL=1): mouth ellipse deviation (both mouths), foot floors at the junction walls,
lowest z in the bridge band, panel bounds in the variant's own frame, plan outside the variant outline.
"""
import argparse
import json
import math
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, HERE)
import footprint_adapter as FA   # noqa: E402
import mp8v4_measure as M        # noqa: E402

AL = dict(X0=226.5, X1=253.5, Ya=152.0, Yb=438.0, Ymin=0.0, Ytop=484.0, R=30.0,
          thin_outer=(0.0, 480.0), thin_inner=(26.56, 453.44), thick_outer=(75.0, 405.0), thick_stub=39.07, thick_inner=(9.8, 470.2))

VARIANTS = {
    'v0_al_original': {},
    'v1_corridor_31': dict(X0=224.5, X1=255.5),
    'v2_corridor_23': dict(X0=228.5, X1=251.5),
    'v3_corridor_shift_8': dict(X0=234.5, X1=261.5),
    'v4_thin_wing_54': dict(Yb=430.0),
    'v5_thin_wing_40': dict(Yb=444.0),
    'v6_thick_wing_140': dict(Ya=140.0),
    'v7_corridor_shorter_20': dict(Ya=172.0),
    'v8_bevel_40': dict(thin_inner=(40.0, 440.0)),
    'v9_corridor_longer_22': dict(Ya=130.0),
}


def build_I(**kw):
    p = dict(AL)
    p.update(kw)
    X0, X1, Ya, Yb, Ymin, Ytop, R = p['X0'], p['X1'], p['Ya'], p['Yb'], p['Ymin'], p['Ytop'], p['R']

    def arc(cx, cy, a0, a1, n=6):
        return [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + R * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
    P = [(p['thin_outer'][0], Ytop), (p['thin_inner'][0], Yb)]
    P += arc(X0 - R, Yb - R, 90, 0)                    # upper-left fillet
    P += arc(X0 - R, Ya + R, 0, -90)                   # lower-left fillet
    P += [(p['thick_inner'][0], Ya), (p['thick_outer'][0], Ymin + p['thick_stub']), (p['thick_outer'][0], Ymin), (p['thick_outer'][1], Ymin),
          (p['thick_outer'][1], Ymin + p['thick_stub']), (p['thick_inner'][1], Ya)]
    P += arc(X1 + R, Ya + R, -90, -180)                # lower-right fillet
    P += arc(X1 + R, Yb - R, 180, 90)                  # upper-right fillet
    P += [(p['thin_inner'][1], Yb), (p['thin_outer'][1], Ytop)]
    return P


def dist_outside(Pts, poly):
    """distance of points outside the polygon (0 inside); pure python."""
    def inside(pt):
        x, y, c = pt[0], pt[1], False
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]:
                c = not c
        return c
    def seg(pt):
        best = 1e9
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            abx, aby = b[0] - a[0], b[1] - a[1]
            t = max(0.0, min(1.0, ((pt[0] - a[0]) * abx + (pt[1] - a[1]) * aby) / (abx * abx + aby * aby)))
            best = min(best, math.hypot(pt[0] - a[0] - t * abx, pt[1] - a[1] - t * aby))
        return best
    worst = 0.0
    for pt in Pts:
        if not inside(pt):
            worst = max(worst, seg(pt))
    return worst


def run_variant(name, kw, a):
    import numpy as np
    out = os.path.join(a.outroot, name)
    os.makedirs(out, exist_ok=True)
    P = build_I(**kw)
    stl = os.path.join(out, 'Footprint_%s.stl' % name)
    FA.write_engine_stl(stl, P, 'variant %s of Footprint_261014' % name)
    env = dict(os.environ, KEEP_STL='1', PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, '-u', '-I', os.path.join(HERE, 'engine_capture.py'), a.graph, out, '0=' + stl], capture_output=True, text=True, env=env, encoding='utf-8', errors='replace')
    res = {'variant': name, 'params': kw, 'exit': r.returncode, 'stdout_tail': (r.stdout.strip().splitlines() or [''])[-3:], 'stderr_tail': (r.stderr.strip().splitlines() or [''])[-3:]}
    rj = os.path.join(out, 'MashProject8_v14_result.json')
    if not os.path.isfile(rj):
        return res
    j = json.load(open(rj))
    d = j['data']
    res['status'] = j.get('Status')
    if j.get('status') == 'error':
        res['message'] = d.get('message')
        return res
    res['warnings'] = d.get('input_warnings')
    res['panel_counts'] = d.get('panel_counts')
    q = d.get('panel_quality', {})
    res['panels'] = {k: q.get(k) for k in ('edge_len_mean', 'edge_within_10pct', 'tri_angle_min', 'tri_angle_max', 'rhombus_angle_within_20deg', 'panel_to_shell_dev_max_m', 'coverage_ratio', 'warnings', 'lattice')}
    res['panel_bounds_m'] = d.get('panel_bounds_m')
    v5 = d.get('v5', {})
    res['adapter'] = {k: v5.get(k) for k in ('dx', 'dy', 'inset_m', 'cap_depth_m', 'uc_kesim_payi', 'corridor_width_m', 'thin_wing_depth_m', 'thick_wing_depth_m', 'bridge_width_m', 'wall_x_engine')}
    sp = os.path.join(out, 'AYARLANABILIR_GAUSS_KABUK.stl')
    if os.path.isfile(sp) and not a.no_shell:
        walls = v5['wall_x_engine']
        M.configure(yc=FA.ENGINE_MID_Y, left_wall=walls[0], right_wall=walls[1])
        mesh = M.load(sp)
        V = mesh.vertices
        for w in ('front', 'back'):
            rep = M.mouth_report(mesh, w)
            res['mouth_' + w] = {k: round(rep[k], 3) for k in ('max_dev_m', 'max_dev_pct_B', 'rms_dev_m')}
        lw, rw = walls
        f = M.feet_report(mesh, xs=sorted(set([lw - 14, lw - 8, lw - 2, lw, lw + 2, lw + 8, rw - 12, rw - 6, rw - 2, rw, rw + 3, rw + 6, rw + 10])))
        rows = {int(round(r_['x'])): r_ for r_ in f['rows']}
        res['floor_left'] = round(float(min(r_['bottom_band'] for r_ in f['rows'] if lw - 8 <= r_['x'] <= lw + 2)), 2)
        res['floor_right'] = round(float(min(r_['bottom_band'] for r_ in f['rows'] if rw - 2 <= r_['x'] <= rw + 8)), 2)
        res['wall_plane'] = [round(float(rows[int(round(lw))]['bottom_band']), 2), round(float(rows[int(round(rw))]['bottom_band']), 2)]
        band = (V[:, 0] > lw - 10) & (V[:, 0] < rw + 3) & (np.abs(V[:, 1] - FA.ENGINE_MID_Y) < 40)
        res['bridge_band_min_z'] = round(float(V[band, 2].min()), 2)
        m = v5['map']
        # engine -> variant frame (transpose of the rotation) and plan outside the outline (Y <= top edge only)
        U = [FA.invert_map(m, float(x), float(y)) for x, y in V[::40][:, :2]]
        top = max(p[1] for p in P)
        res['plan_outside_outline_m'] = round(dist_outside([u for u in U if u[1] <= top - 1.0 and u[0] > 31 and u[0] < 449], P), 3)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outroot')
    ap.add_argument('--graph', default=os.path.join(ROOT, 'MashProject8', 'MashProject8_Paylas_V5', 'MashProject8_v14.dyn'))
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--only', default='')
    ap.add_argument('--no-shell', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.outroot, exist_ok=True)
    names = [n for n in VARIANTS if (not a.only or any(n.startswith(o) for o in a.only.split(',')))]
    results = []
    with ThreadPoolExecutor(a.workers) as ex:
        for r in ex.map(lambda n: run_variant(n, VARIANTS[n], a), names):
            results.append(r)
            print(json.dumps(r, default=str)[:1800], flush=True)
    json.dump(results, open(os.path.join(a.outroot, 'variants_results.json'), 'w'), indent=1, default=str)
    return 0


if __name__ == '__main__':
    sys.exit(main())
