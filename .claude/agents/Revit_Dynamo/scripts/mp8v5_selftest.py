#!/usr/bin/env python3
"""mp8v5_selftest.py - offline acceptance suite for MashProject8_V5 (Al's new footprint Footprint_261014.stl through the frame adapter). No Revit, no Dynamo.

  python mp8v5_selftest.py OUTROOT --exe MashEngine.exe [--package MashProject8_Paylas_V5] [--workers 6] [--panels] [--only a,b] [--keep]

ADAPTER   the engine-frame footprint DERIVED from the raw Footprint_261014.stl of the package by footprint_adapter.py (the code the node runs) vs Al's STL: mapped back, every vertex except the four un-rounded junction corners and the thin-wing tab/inset lies ON Al's outline;
          the corners sit at the intersection of the extended edges (radius 30 fillets re-created by the engine); polygon simple; min x' = min y' = 0; md5s of sidecar and files agree.
SCENARIOS the REAL exe on the engine-frame footprint with the V5 graph values + overrides (19): mouth ellipse deviation (both mouths), foot floors / no penetration, top kink,
          lobe depth, extent (x_min, y planes). DEFAULT also: the shell mapped back into Al's frame lies INSIDE his outline (Y <= 484) and spans X 30..450, Y 0..508;
          with --panels the panel report (no warnings, deviation <= 0.4 m, edge +-10 % >= 0.93, min angle >= 25, coverage >= 0.95, field-aligned lattice).
Expected floor of a foot = max(foot height, 20 - opening/2, 0) (+- tolerance): the arms hover at 20 - opening/2.
"""
import argparse
import hashlib
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
import make_footprint_v4 as FP4  # noqa: E402
import footprint_adapter as FA  # noqa: E402

SCEN = {
    'default': {},
    'open_30_30': {'SOL_C_ACIKLIGI': 30.0, 'SAG_C_ACIKLIGI': 30.0},
    'open_60_60': {'SOL_C_ACIKLIGI': 60.0, 'SAG_C_ACIKLIGI': 60.0},
    'open_L36_R52': {'SOL_C_ACIKLIGI': 36.0, 'SAG_C_ACIKLIGI': 52.0},
    'sect10': {'KOPRU_YUKSEKLIGI': 10.0},
    'sect40': {'KOPRU_YUKSEKLIGI': 40.0},
    'width20': {'KOPRU_GENISLIGI': 20.0},
    'width34': {'KOPRU_GENISLIGI': 34.0},
    'fillet20': {'KOSE_YUVARLATMA_YARICAPI': 20.0},
    'fillet45': {'KOSE_YUVARLATMA_YARICAPI': 45.0},
    'gauss0': {'TEPE_UST': 0.0, 'TEPE_ALT': 0.0},
    'gauss35': {'TEPE_UST': 35.0, 'TEPE_ALT': 35.0},
    'foot80': {'BRIDGE_FOOT_LEN': 80.0},
    'foot140': {'BRIDGE_FOOT_LEN': 140.0},
    'narrow0': {'BRIDGE_FOOT_NARROW': 0.0},
    'narrow60': {'BRIDGE_FOOT_NARROW': 0.6},
    'feet_5_8': {'BRIDGE_FOOT_HEIGHT_L': 5.0, 'BRIDGE_FOOT_HEIGHT_R': 8.0},
    'follow_arm_1': {'BRIDGE_FOOT_FOLLOW_ARM': 1.0},
    'exp_rounded_rect': {'ARM_SECTION_EXP': 3.0, 'CAP_SECTION_EXP': 3.0, 'ARM_SECTION_WIDTH': 25.0},
}
NO_MOUTH = {'exp_rounded_rect'}
NO_FLOOR = {'follow_arm_1'}


def adapter_checks(user_stl, eng_stl, side):
    fails, info = [], {}
    if hashlib.md5(open(eng_stl, 'rb').read()).hexdigest() != side['engine_stl_md5']:
        fails.append('adapter record engine_stl_md5 does not match the derived footprint')
    if hashlib.md5(open(user_stl, 'rb').read()).hexdigest() != side['source_md5']:
        fails.append('sidecar source_md5 does not match %s' % side['source'])
    E, _, _ = FP4.loop_from_stl(eng_stl)
    U, _, _ = FP4.loop_from_stl(user_stl)
    E, U = E * 0.001, U * 0.001
    if FP4.area2(E) < 0:
        E = E[::-1]
    if not FP4.is_simple(E):
        fails.append('engine-frame polygon is not simple')
    if abs(E[:, 0].min()) > 1e-6 or abs(E[:, 1].min()) > 1e-6:
        fails.append('engine-frame polygon is not min-normalised (the engine would shift it)')
    # back to the user frame
    m_ = side['map']
    Ub = np.c_[m_[0] * (E[:, 0] - m_[4]) + m_[2] * (E[:, 1] - m_[5]), m_[1] * (E[:, 0] - m_[4]) + m_[3] * (E[:, 1] - m_[5])]

    def dist(P, poly):
        d = np.full(len(P), np.inf)
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            ab = b - a
            t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1)
            d = np.minimum(d, np.linalg.norm(P - (a + t[:, None] * ab), axis=1))
        return d
    d = dist(Ub, U)
    far = d > 1e-3
    info['vertices'] = len(E)
    info['off_outline'] = [[round(float(Ub[i, 0]), 2), round(float(Ub[i, 1]), 2), round(float(d[i]), 2)] for i in np.flatnonzero(far)]
    corners = [c for c in info['off_outline'] if abs(c[2] - 30.0 * (2 ** 0.5 - 1.0)) < 0.5]
    if len(corners) != 4:
        fails.append('expected exactly 4 un-rounded corner vertices at distance R(sqrt2-1) = %.2f m from Al outline, got %d' % (30 * (2 ** 0.5 - 1), len(corners)))
    others = [c for c in info['off_outline'] if c not in corners]
    for c in others:      # the only other deviations allowed: the inset / tab / extension of the thin wing (top wing, Y >= 440 or X outside 0..480)
        if not (c[1] >= 430.0 or c[0] < -0.1 or c[0] > 480.1):
            fails.append('unexpected vertex off Al outline: %s' % c)
    # the right (thick) wing and the bridge edges are untouched
    thick = [(round(float(p[0]), 3), round(float(p[1]), 3)) for p in U if p[1] <= 152.0 + 1e-6]
    mapped = set((round(float(p[0]), 3), round(float(p[1]), 3)) for p in Ub)
    miss = [p for p in thick if p not in mapped and not (abs(p[1] - 152.0) < 1e-6 and 190 < p[0] < 290)]
    if miss:
        fails.append('thick-wing vertices of Al outline missing in the engine polygon: %s' % miss[:4])
    info['thin_wing_width_m'] = side.get('thin_wing_width_at_cut_m')
    if abs(side['thin_wing_width_at_cut_m'] - side['inset_m'] - side['cap_depth_m']) > 1e-6:
        fails.append('arm width - inset != cap depth')
    return fails, info, side


def run_scenario(name, over, a, side, outroot, yc0):
    IN = L.graph_inputs(a.graph)
    IN[20] = 6.0 if (name == 'default' and a.panels) else 0.0
    s = L.settings_from_inputs(IN)
    s['UC_KESIM_PAYI'] = float(side['uc_kesim_payi'])
    if s['SOL_C_DERINLIGI'] <= 0:                      # the node's automatic values (graph v14: 0 = automatic)
        s['SOL_C_DERINLIGI'] = float(side['cap_depth_m'])
    if s['KOPRU_GENISLIGI'] <= 0:
        s['KOPRU_GENISLIGI'] = float(side['corridor_width_m'])
    s['BRIDGE_FOOT_HEIGHT_L'] = min(s['BRIDGE_FOOT_HEIGHT_L'] + side['foot_height_comp_m'][0], 30.0)      # the node adds the calibration offset
    s['BRIDGE_FOOT_HEIGHT_R'] = min(s['BRIDGE_FOOT_HEIGHT_R'] + side['foot_height_comp_m'][1], 30.0)
    s.update(over)
    d = os.path.join(outroot, name)
    os.makedirs(d, exist_ok=True)
    sp = os.path.join(d, 'settings.json')
    json.dump(s, open(sp, 'w'), indent=1)
    env = dict(os.environ, MPLBACKEND='Agg', PYTHONIOENCODING='utf-8')
    env.pop('PYTHONHOME', None)
    env.pop('PYTHONPATH', None)
    t0 = time.time()
    r = subprocess.run([a.exe, '--footprint', a.engine_fp, '--settings', sp, '--output-dir', d], capture_output=True, text=True,
                       cwd=os.path.dirname(a.exe), env=env, encoding='utf-8', errors='replace')
    out = {'scenario': name, 'exit': r.returncode, 'secs': round(time.time() - t0)}
    if r.returncode:
        out['err'] = (r.stdout.strip().splitlines() or [''])[0][:160]
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
    lw, rw = M.CFG['left_wall'], M.CFG['right_wall']
    xs = sorted(set([lw - 14, lw - 10, lw - 6, lw - 2, lw, lw + 2, lw + 8, rw - 12, rw - 6, rw - 2, rw, rw + 3, rw + 6, rw + 10, rw + 13]))
    f = M.feet_report(mesh, xs=xs)
    rows = {int(round(r_['x'])): r_ for r_ in f['rows']}
    out['expected_floor'] = [round(max(float(s.get('BRIDGE_FOOT_HEIGHT_L', 0.0)), 20.0 - float(s['SOL_C_ACIKLIGI']) / 2.0, 0.0), 2),
                             round(max(float(s.get('BRIDGE_FOOT_HEIGHT_R', 0.0)), 20.0 - float(s['SAG_C_ACIKLIGI']) / 2.0, 0.0), 2)]
    out['foot_floor_left'] = round(float(min(r_['bottom_band'] for r_ in f['rows'] if lw - 8 <= r_['x'] <= lw + 2)), 2)
    out['foot_floor_right'] = round(float(min(r_['bottom_band'] for r_ in f['rows'] if rw - 2 <= r_['x'] <= rw + 8)), 2)
    out['wall_plane_left'] = round(float(rows[int(round(lw))]['bottom_band']), 2)
    out['wall_plane_right'] = round(float(rows[int(round(rw))]['bottom_band']), 2)
    band = (V[:, 0] > lw - 10) & (V[:, 0] < rw + 10) & (np.abs(V[:, 1] - yc0) < 40)
    out['bridge_band_min_z'] = round(float(V[band, 2].min()), 2)
    tx = np.arange(lw + 10, rw - 9, 3.0)
    top = []
    for x in tx:
        sel = (np.abs(V[:, 0] - x) < 1.2) & (np.abs(V[:, 1] - yc0) < 14)
        top.append(V[sel, 2].max() if sel.any() else np.nan)
    top = np.array(top)
    out['top_kink'] = round(float(np.nanmax(np.abs(np.diff(top, 2)))), 2)
    out['top_max'] = round(float(np.nanmax(top)), 2)
    arm_min = V[(V[:, 0] < lw - 25) | (V[:, 0] > rw + 25)][:, 2].min()
    reg = V[(V[:, 0] > lw - 6) & (V[:, 0] < rw + 6) & (np.abs(V[:, 1] - yc0) < 60)][:, 2]
    out['lobe_depth_m'] = round(float(max(0.0, arm_min - reg.min())), 2)
    if name == 'default':
        m_ = side['map']
        U = np.c_[m_[0] * (V[:, 0] - m_[4]) + m_[2] * (V[:, 1] - m_[5]), m_[1] * (V[:, 0] - m_[4]) + m_[3] * (V[:, 1] - m_[5])]
        out['user_bbox'] = [round(float(U[:, 0].min()), 2), round(float(U[:, 0].max()), 2), round(float(U[:, 1].min()), 2), round(float(U[:, 1].max()), 2)]
        P, _, _ = FP4.loop_from_stl(a.user_stl)
        P = P * 0.001
        from matplotlib.path import Path
        inside = Path(np.vstack([P, P[0]])).contains_points(U, radius=0.0)
        out_pts = ~inside & (U[:, 1] <= 484.0)
        dd = np.full(out_pts.sum(), np.inf)
        Q = U[out_pts]
        n = len(P)
        for i in range(n):
            a_, b_ = P[i], P[(i + 1) % n]
            ab = b_ - a_
            t = np.clip(((Q - a_) @ ab) / (ab @ ab), 0, 1)
            dd = np.minimum(dd, np.linalg.norm(Q - (a_ + t[:, None] * ab), axis=1))
        out['outside_al_outline_max_m'] = round(float(dd.max()) if len(dd) else 0.0, 3)
        if a.panels:
            rp = os.path.join(d, 'baklava_report.json')
            rep = json.load(open(rp)) if os.path.isfile(rp) else {'error': 'no baklava_report.json'}
            out['panels'] = {k: rep.get(k) for k in ('triangles', 'vertices', 'panels_total', 'rhombus_panels', 'triangle_panels', 'edge_len_min', 'edge_len_max', 'edge_within_10pct',
                                                    'tri_angle_min', 'tri_angle_max', 'rhombus_angle_within_20deg', 'irregular_share', 'panel_to_shell_dev_max_m',
                                                    'coverage_ratio', 'warnings', 'lattice', 'error')}
    if not a.keep:
        try:
            os.remove(stl)
        except OSError:
            pass
    return out


def check(name, r, side):
    if r['exit']:
        return ['engine exit %d: %s' % (r['exit'], r.get('err'))]
    fails = []
    strict = name == 'default'
    pct, dm = (1.0, 0.30) if strict else (3.5, 1.2)
    if name not in NO_MOUTH:
        for w in ('front', 'back'):
            m = r['mouth_' + w]
            if m['max_dev_pct_B'] > pct or m['max_dev_m'] > dm:
                fails.append('mouth %s dev %.2f m (%.2f %% B) over the limit %.1f %%' % (w, m['max_dev_m'], m['max_dev_pct_B'], pct))
    tol = 0.35 if strict else 0.75
    if name not in NO_FLOOR:
        for side_, k in (('left', 0), ('right', 1)):
            if abs(r['foot_floor_' + side_] - r['expected_floor'][k]) > tol:
                fails.append('foot floor %s %.2f m, expected %.2f (+-%.2f)' % (side_, r['foot_floor_' + side_], r['expected_floor'][k], tol))
        if r['bridge_band_min_z'] < -0.30 and name not in ('open_60_60',):
            fails.append('shell dips %.2f m below the ground in the bridge band' % r['bridge_band_min_z'])
    else:
        if not (2.0 <= r['foot_floor_left'] <= 6.0 and 2.0 <= r['foot_floor_right'] <= 6.0):
            fails.append('follow-arm floors %.2f / %.2f not the arm underside level' % (r['foot_floor_left'], r['foot_floor_right']))
    if r['top_kink'] > (0.3 if strict else 0.8):
        fails.append('top kink %.2f' % r['top_kink'])
    if r['lobe_depth_m'] > (0.15 if strict else 0.30):      # 0.2 m = the engine's built-in bridge centre line is 3.7 m off the corridor centre (compensated by foot heights 0.2 / 0.05 in the default)
        fails.append('lobe depth %.2f' % r['lobe_depth_m'])
    if strict:
        xe = side['dx'] + side['inset_m'] - side['cap_depth_m']
        if abs(r['x_min'] - xe) > 0.7:
            fails.append('x extent moved: x_min %.2f expected %.2f' % (r['x_min'], xe))
        if abs(r['y_range'][0] - side['uc_kesim_payi']) > 0.1 or abs(r['y_range'][1] - (side['engine_y_range'][1] - side['uc_kesim_payi'])) > 0.1:
            fails.append('mouth planes moved: y %s' % r['y_range'])
        ub = r['user_bbox']
        if not (abs(ub[0] - 30.0) < 0.1 and abs(ub[1] - 450.0) < 0.1 and abs(ub[2] - 0.0) < 0.1 and abs(ub[3] - 508.0) < 0.2):
            fails.append('shell in the footprint frame spans %s, expected X 30..450, Y 0..508' % ub)
        if r['outside_al_outline_max_m'] > 0.05:
            fails.append('shell plan leaves Al outline by %.3f m' % r['outside_al_outline_max_m'])
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outroot')
    ap.add_argument('--package', default=os.path.join(ROOT, 'MashProject8', 'MashProject8_Paylas_V5'))
    ap.add_argument('--graph', default=os.path.join(ROOT, 'ForDynamo', 'baklava-panels', 'MashProject8_v14.dyn'))
    ap.add_argument('--exe', default=None)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--panels', action='store_true')
    ap.add_argument('--only', default='')
    ap.add_argument('--keep', action='store_true')
    a = ap.parse_args()
    a.exe = a.exe or os.path.join(a.package, 'Engine', 'MashEngine.exe')
    os.makedirs(a.outroot, exist_ok=True)
    total = 0
    a.user_stl = os.path.join(a.package, 'Footprint_261014.stl')
    a.engine_fp, side = FA.derive(a.user_stl, os.path.join(a.outroot, '_engine_footprint'))     # the very code the node runs at run time
    fa, info, side = adapter_checks(a.user_stl, a.engine_fp, side)
    print('ADAPTER %s  %s' % ('PASS' if not fa else 'FAIL ' + '; '.join(fa), json.dumps(info)[:600]))
    total += len(fa)
    yc0 = 249.4
    M.configure(yc=yc0, left_wall=side['wall_x_engine'][0], right_wall=side['wall_x_engine'][1])
    names = [n for n in SCEN if (not a.only or n in a.only.split(','))]
    results = []
    with ThreadPoolExecutor(a.workers) as ex:
        for r in ex.map(lambda n: run_scenario(n, SCEN[n], a, side, a.outroot, yc0), names):
            fails = check(r['scenario'], r, side)
            r['fails'] = fails
            results.append(r)
            total += len(fails)
            if r['exit']:
                print('%-18s ENGINE FAIL %s' % (r['scenario'], r.get('err')))
                continue
            print('%-18s %s | mouth dev front %.2f m (%.2f%% B) back %.2f m (%.2f%% B) | floors L %.2f R %.2f (exp %s; wall L %.2f R %.2f) min z band %.2f | kink %.2f lobe %.2f | x_min %.1f | %ds' %
                  (r['scenario'], 'PASS' if not fails else 'FAIL', r['mouth_front']['max_dev_m'], r['mouth_front']['max_dev_pct_B'], r['mouth_back']['max_dev_m'],
                   r['mouth_back']['max_dev_pct_B'], r['foot_floor_left'], r['foot_floor_right'], r['expected_floor'], r['wall_plane_left'], r['wall_plane_right'],
                   r['bridge_band_min_z'], r['top_kink'], r['lobe_depth_m'], r['x_min'], r['secs']))
            for f_ in fails:
                print('      - ' + f_)
            if r['scenario'] == 'default':
                print('      user frame: bbox %s, outside Al outline max %.3f m' % (r['user_bbox'], r['outside_al_outline_max_m']))
                if r.get('panels'):
                    print('      panels', json.dumps(r['panels']))
    json.dump({'adapter': {'fails': fa, 'info': info}, 'scenarios': results}, open(os.path.join(a.outroot, 'selftest_v5_results.json'), 'w'), indent=1)
    print('TOTAL FAILS %d' % total)
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
