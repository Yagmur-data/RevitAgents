#!/usr/bin/env python3
"""mp8v4_selftest.py - offline acceptance suite for MashProject8_V4 (no Revit, no Dynamo).

  python mp8v4_selftest.py OUTROOT [--graph FILE.dyn] [--footprint FILE] [--engine DIR | --exe FILE] [--workers N] [--panels]
                                    [--only name,name] [--keep]

What it proves (numbers from the shell STL the ENGINE writes, nothing else):
  FOOTPRINT  the V4 Footprint.stl keeps the outer extent (min x = 0 anchor corner kept, y range, inset 11.1 m, simple polygon)
  MOUTH      both left-arm mouth loops (y = 30 and y = 463) vs their best-fit ellipse: max deviation in m and % of the semi-minor axis
  FEET       lowest shell z at the LEFT foot (x 45..60) and RIGHT foot (x 335..352) = gap to the ground z = 0; at the arm-wall planes x = 58 / 337
  SHELL      top surface kink / dip (no pit between the arm tops), 'lobe depth' (bridge region lower than the arm's own lowest point), extent,
             mouth planes y = 30.0 / 462.97
  PANELS     (--panels) one default run with the panel stage: warnings empty, deviation <= 0.4 m, edge +-10 % >= 0.93, min triangle angle >= 25,
             coverage >= 0.95 (the same panel stage the Dynamo node runs)
Scenario values are engine settings on top of the SAVED values of the graph (default MashProject8_v12.dyn in ForDynamo/baklava-panels).
DEFAULT scenario thresholds are strict; other scenarios (other measures) use looser limits - they show where the V4 defaults stop being a true ellipse.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, HERE)
import mp8v4_lab as L            # noqa: E402
import mp8v4_measure as M        # noqa: E402
import make_footprint_v4 as FP   # noqa: E402

SCEN = {
    'default': {},
    'open_30_30': {'SOL_C_ACIKLIGI': 30.0, 'SAG_C_ACIKLIGI': 30.0},
    'open_60_60': {'SOL_C_ACIKLIGI': 60.0, 'SAG_C_ACIKLIGI': 60.0},
    'open_L36_R52': {'SOL_C_ACIKLIGI': 36.0, 'SAG_C_ACIKLIGI': 52.0},
    'sect10': {'KOPRU_YUKSEKLIGI': 10.0},
    'sect40': {'KOPRU_YUKSEKLIGI': 40.0},
    'width15': {'KOPRU_GENISLIGI': 15.0},
    'width45': {'KOPRU_GENISLIGI': 45.0},
    'fillet0': {'KOSE_YUVARLATMA_YARICAPI': 0.0},
    'fillet60': {'KOSE_YUVARLATMA_YARICAPI': 60.0},
    'gauss0': {'TEPE_UST': 0.0, 'TEPE_ALT': 0.0},
    'gauss35': {'TEPE_UST': 35.0, 'TEPE_ALT': 35.0},
    'foot80': {'BRIDGE_FOOT_LEN': 80.0},
    'foot140': {'BRIDGE_FOOT_LEN': 140.0},
    'narrow0': {'BRIDGE_FOOT_NARROW': 0.0},
    'narrow60': {'BRIDGE_FOOT_NARROW': 0.6},
    'feet_5_8': {'BRIDGE_FOOT_HEIGHT_L': 5.0, 'BRIDGE_FOOT_HEIGHT_R': 8.0},
    'follow_arm_1': {'BRIDGE_FOOT_FOLLOW_ARM': 1.0},
    'exp_rounded_rect': {'ARM_SECTION_EXP': 3.0, 'CAP_SECTION_EXP': 3.0, 'ARM_SECTION_WIDTH': 25.0},      # documents: exponents 3 with the V4 footprint is NOT an ellipse
}
# per-scenario limits: (mouth max dev % of B, mouth max dev m, foot floor max m or None)
LIMITS = {'default': (1.0, 0.30, 0.35)}
LOOSE = (3.5, 1.2, 0.60)
NO_MOUTH = {'exp_rounded_rect'}                    # documents the old look - mouth is NOT an ellipse there (expected)
NO_FLOOR = {'follow_arm_1'}                         # follow-arm 1 is the old behaviour (floor ~3 m): its own check below


def lim(name):
    return LIMITS.get(name, LOOSE)


def run_scenario(name, over, a, outroot):
    IN = L.graph_inputs(a.graph)
    IN[20] = 6.0 if (name == 'default' and a.panels) else 0.0
    s = L.settings_from_inputs(IN)
    s.update(over)
    d = os.path.join(outroot, name)
    os.makedirs(d, exist_ok=True)
    sp = os.path.join(d, 'settings.json')
    json.dump(s, open(sp, 'w'), indent=1)
    t0 = time.time()
    if a.exe:
        env = dict(os.environ, MPLBACKEND='Agg', PYTHONIOENCODING='utf-8')
        env.pop('PYTHONHOME', None)
        env.pop('PYTHONPATH', None)
        cmd, cwd = [a.exe, '--footprint', a.footprint, '--settings', sp, '--output-dir', d], os.path.dirname(a.exe)
    else:
        env = None
        cmd, cwd = [sys.executable, os.path.join(a.engine, 'Engine_Source.py'), '--footprint', a.footprint, '--settings', sp, '--output-dir', d], a.engine
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env, encoding='utf-8', errors='replace')
    out = {'scenario': name, 'exit': r.returncode, 'secs': round(time.time() - t0)}
    if r.returncode:
        out['err'] = (r.stderr.strip().splitlines() or [''])[-1][:160]
        return out
    stl = os.path.join(d, 'AYARLANABILIR_GAUSS_KABUK.stl')
    mesh = M.load(stl)
    V = mesh.vertices
    out['tri'] = len(mesh.faces)
    out['x_min'] = round(float(V[:, 0].min()), 2)
    out['y_range'] = [round(float(V[:, 1].min()), 2), round(float(V[:, 1].max()), 2)]
    for w in ('front', 'back'):
        rep = M.mouth_report(mesh, w)
        out['mouth_' + w] = {k: round(rep[k], 3) for k in ('max_dev_m', 'max_dev_pct_B', 'rms_dev_m', 'A', 'B', 'width', 'height')}
    f = M.feet_report(mesh, xs=(40, 46, 48, 50, 54, 58, 60, 66, 337, 335, 340, 345, 349, 352))
    out['expected_floor'] = [round(max(float(s.get('BRIDGE_FOOT_HEIGHT_L', 0.0)), 20.0 - float(s['SOL_C_ACIKLIGI']) / 2.0, 0.0), 2),
                             round(max(float(s.get('BRIDGE_FOOT_HEIGHT_R', 0.0)), 20.0 - float(s['SAG_C_ACIKLIGI']) / 2.0, 0.0), 2)]
    rows = {int(r_['x']): r_ for r_ in f['rows']}
    left = [r_['bottom_band'] for r_ in f['rows'] if 46 <= r_['x'] <= 60]        # bridge side of the left junction (the arm itself ends at x ~ 58)
    right = [r_['bottom_band'] for r_ in f['rows'] if 335 <= r_['x'] <= 349]     # bridge side of the right junction (the right body starts at x ~ 350)
    out['foot_floor_left'] = round(float(min(left)), 2)
    out['foot_floor_right'] = round(float(min(right)), 2)
    out['wall_plane_left_x58'] = round(float(rows[58]['bottom_band']), 2)
    out['wall_plane_right_x337'] = round(float(rows[337]['bottom_band']), 2)
    # top surface (same measure as ShellFix/generality_tests.py)
    xs = np.arange(40, 381, 3.0)
    top = []
    for x in xs:
        band = (np.abs(V[:, 0] - x) < 1.2) & ((np.abs(V[:, 1] - 250) < 14) if 60 < x < 335 else (np.abs(V[:, 1] - 250) < 999))
        z = V[band, 2]
        top.append(z.max() if len(z) else np.nan)
    top = np.array(top)
    br = (xs >= 60) & (xs <= 335)
    out['top_dip'] = round(float(np.nanmin(top[br]) - min(top[0], top[-1])), 2)
    out['top_kink'] = round(float(np.nanmax(np.abs(np.diff(top[br], 2)))), 2)
    arm_min = V[(V[:, 0] < 30) | (V[:, 0] > 370)][:, 2].min()
    reg = V[(V[:, 0] > 40) & (V[:, 0] < 350) & (np.abs(V[:, 1] - 250) < 60)][:, 2]
    out['lobe_depth_m'] = round(float(max(0.0, arm_min - reg.min())), 2)
    out['min_z'] = round(float(V[:, 2].min()), 2)
    if a.panels and name == 'default':
        rp = os.path.join(d, 'baklava_report.json')
        if os.path.isfile(rp):
            rep = json.load(open(rp))
            out['panels'] = {k: rep.get(k) for k in ('triangles', 'vertices', 'panels_total', 'rhombus_panels', 'triangle_panels', 'edge_len_min', 'edge_len_max',
                                                    'edge_within_10pct', 'tri_angle_min', 'tri_angle_max', 'rhombus_angle_within_20deg', 'irregular_share',
                                                    'panel_to_shell_dev_max_m', 'coverage_ratio', 'warnings', 'method', 'lattice')}
        else:
            out['panels'] = {'error': 'no baklava_report.json'}
    if not a.keep:
        try:
            os.remove(stl)
        except OSError:
            pass
    return out


def check(name, r):
    fails = []
    if r['exit']:
        return ['engine exit %d: %s' % (r['exit'], r.get('err'))]
    pct, dm, fl = lim(name)
    if name not in NO_MOUTH:
        for w in ('front', 'back'):
            m = r['mouth_' + w]
            if m['max_dev_pct_B'] > pct or m['max_dev_m'] > dm * (1.0 if name == 'default' else 3.0):
                fails.append('mouth %s dev %.2f m (%.2f %% B) > limit %.1f %%' % (w, m['max_dev_m'], m['max_dev_pct_B'], pct))
    if name not in NO_FLOOR:
        # FOLLOW_ARM = 0: the foot lands at max(requested foot height, the arm's own underside level 20 - opening/2 without the Gauss lift, ground)
        for side, k in (('left', 0), ('right', 1)):
            if abs(r['foot_floor_' + side] - r['expected_floor'][k]) > fl:
                fails.append('foot floor %s %.2f m, expected %.2f m (+-%.2f)' % (side, r['foot_floor_' + side], r['expected_floor'][k], fl))
    if name == 'follow_arm_1':
        if not (2.0 <= r['foot_floor_left'] <= 5.0 and 2.0 <= r['foot_floor_right'] <= 5.0):
            fails.append('follow-arm floors %.2f / %.2f not the expected arm-underside level (2..5 m)' % (r['foot_floor_left'], r['foot_floor_right']))
    if r['top_kink'] > (0.2 if name == 'default' else 0.5):
        fails.append('top kink %.2f' % r['top_kink'])
    if r['lobe_depth_m'] > 0.1:
        fails.append('lobe depth %.2f' % r['lobe_depth_m'])
    if name == 'default':
        if not (-24.0 <= r['x_min'] <= -22.5):
            fails.append('x extent moved: x_min %.2f (expected about -23.3)' % r['x_min'])
        if abs(r['y_range'][0] - 30.0) > 0.1 or abs(r['y_range'][1] - 462.97) > 0.1:
            fails.append('mouth planes moved: y %s' % r['y_range'])
        pn = r.get('panels')
        if pn is not None:
            if pn.get('error') or pn.get('warnings'):
                fails.append('panel stage: %s' % (pn.get('error') or pn.get('warnings')))
            else:
                if pn['panel_to_shell_dev_max_m'] > 0.4:
                    fails.append('panel deviation %.2f m' % pn['panel_to_shell_dev_max_m'])
                if pn['edge_within_10pct'] < 0.93:
                    fails.append('edge +-10 %% = %.3f' % pn['edge_within_10pct'])
                if pn['tri_angle_min'] < 25.0:
                    fails.append('min triangle angle %.1f' % pn['tri_angle_min'])
                if pn['coverage_ratio'] < 0.95:
                    fails.append('coverage %.3f' % pn['coverage_ratio'])
                if pn.get('lattice') != 'field-aligned':
                    fails.append('lattice %s' % pn.get('lattice'))
    return fails


def footprint_checks(path, original):
    """structure of the V4 footprint against the original (kept anchor corner, inset, simple polygon, same right body)."""
    fails = []
    P, _, _ = FP.loop_from_stl(path)
    O, _, _ = FP.loop_from_stl(original)
    Q = P * 0.001
    Q = Q - Q.min(0)
    Oq = O * 0.001
    Oq = Oq - Oq.min(0)
    if not FP.is_simple(Q):
        fails.append('footprint polygon is not simple')
    if abs(Q[:, 0].min()) > 1e-6 or abs(Q[:, 1].min()) > 1e-6:
        fails.append('footprint minimum is not the origin')
    # the min corner must still sit at the same absolute place: both polygons share the original's min x / min y in mm
    if abs(P[:, 0].min() - O[:, 0].min()) > 1e-3 or abs(P[:, 1].min() - O[:, 1].min()) > 1e-3:
        fails.append('anchor corner moved: the whole shell would shift in x/y')
    right_o = sorted(map(tuple, np.round(Oq[Oq[:, 0] > 100], 3)))
    right_n = sorted(map(tuple, np.round(Q[Q[:, 0] > 100], 3)))
    if right_o != right_n:
        fails.append('right part of the footprint (x > 100) differs from the original')
    # left arm width at y = 30 (seam x - left edge x)
    def width_at(poly, y0):
        xs = []
        n = len(poly)
        for i in range(n):
            a_, b_ = poly[i], poly[(i + 1) % n]
            if (a_[1] - y0) * (b_[1] - y0) < 0 and min(a_[0], b_[0]) < 100:
                xs.append(a_[0] + (y0 - a_[1]) * (b_[0] - a_[0]) / (b_[1] - a_[1]))
        xs = sorted(xs)
        return (xs[1] - xs[0]) if len(xs) >= 2 else float('nan')
    w_o, w_n = width_at(Oq, 30.04), width_at(Q, 30.04)
    if not (abs((w_o - w_n) - 11.1) < 0.1):
        fails.append('arm width at y=30 changed by %.2f m, expected 11.1' % (w_o - w_n))
    return fails, dict(width_original=round(w_o, 2), width_v4=round(w_n, 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outroot')
    ap.add_argument('--graph', default=os.path.join(ROOT, 'ForDynamo', 'baklava-panels', 'MashProject8_v12.dyn'))
    ap.add_argument('--footprint', default=os.path.join(ROOT, 'MashProject8', 'MashProject8_Paylas_V4', 'Footprint.stl'))
    ap.add_argument('--original-footprint', default=os.path.join(ROOT, 'MashProject8', 'Footprint.stl'))
    ap.add_argument('--engine', default=os.path.join(ROOT, 'MashProject8'))
    ap.add_argument('--exe', default=None)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--panels', action='store_true')
    ap.add_argument('--only', default='')
    ap.add_argument('--keep', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.outroot, exist_ok=True)
    names = [n for n in SCEN if (not a.only or n in a.only.split(','))]
    total_fail = 0
    ff, info = footprint_checks(a.footprint, a.original_footprint)
    print('FOOTPRINT %s  %s' % ('PASS' if not ff else 'FAIL ' + '; '.join(ff), info))
    total_fail += len(ff)
    results = []
    with ThreadPoolExecutor(a.workers) as ex:
        for r in ex.map(lambda n: run_scenario(n, SCEN[n], a, a.outroot), names):
            fails = check(r['scenario'], r)
            r['fails'] = fails
            results.append(r)
            total_fail += len(fails)
            if r['exit']:
                print('%-18s ENGINE FAIL %s' % (r['scenario'], r.get('err')))
                continue
            print('%-18s %s | mouth dev front %.2f m (%.2f%% B) back %.2f m (%.2f%% B) | floors L %.2f R %.2f (x58 %.2f, x337 %.2f) | top_kink %.2f dip %.1f lobe %.2f | x_min %.1f | %ds' %
                  (r['scenario'], 'PASS' if not fails else 'FAIL', r['mouth_front']['max_dev_m'], r['mouth_front']['max_dev_pct_B'], r['mouth_back']['max_dev_m'],
                   r['mouth_back']['max_dev_pct_B'], r['foot_floor_left'], r['foot_floor_right'], r['wall_plane_left_x58'], r['wall_plane_right_x337'],
                   r['top_kink'], r['top_dip'], r['lobe_depth_m'], r['x_min'], r['secs']))
            for f_ in fails:
                print('      - ' + f_)
            if r.get('panels'):
                print('      panels', json.dumps(r['panels']))
    json.dump({'footprint': {'fails': ff, 'info': info}, 'scenarios': results}, open(os.path.join(a.outroot, 'selftest_results.json'), 'w'), indent=1)
    print('TOTAL FAILS %d' % total_fail)
    return 1 if total_fail else 0


if __name__ == '__main__':
    sys.exit(main())
