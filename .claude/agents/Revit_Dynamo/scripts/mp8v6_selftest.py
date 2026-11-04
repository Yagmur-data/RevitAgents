#!/usr/bin/env python3
"""mp8v6_selftest.py - offline acceptance suite for the v15 round (Al's 4 notes of 2026-10-14). No Revit, no Dynamo.

  python mp8v6_selftest.py adapter FOOTPRINT_261014.stl                     FPAD3 adapter: squared ends, short tab, cut 0.6 m beyond the end, clip lines (angle, side, box); no-bevel footprint -> no clip lines
  python mp8v6_selftest.py v15 CAP_DIR FOOTPRINT_261014.stl                 results of engine_capture.py on graph v15 (KEEP_STL=1): settings, shell plan vs the STL, corridor edges, bridge circle, feet, mouth ellipses,
                                                                            panels after the node's clip (inside the STL outline, slanted end straight, no gap), panel report (no warnings)
  python mp8v6_selftest.py engine3 OUTROOT --engine ENGINE_DIR --exe EXE    PROTOTYPE engine V3 (python, mp8v6_engine_patch.py): regression (no new setting -> byte-identical STL), slanted cut
                                                                            (3 open loops, no missing area, planar rims), foot ramp 25 / 30 / 35 deg (measured angle +-3 deg, walls on the ground), arc
Exit code 0 = all pass.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, HERE)
import footprint_adapter as FA   # noqa: E402
import mp8v6_measure as M        # noqa: E402
import mp8v6_run as RUN          # noqa: E402

FAILS = []


def check(name, cond, info=''):
    print(('PASS ' if cond else 'FAIL ') + name + ('  ' + str(info) if info else ''))
    if not cond:
        FAILS.append(name)


# ------------------------------------------------------------------------------------------------------------------------------------------
def t_adapter(fp, work):
    P, zb, zt = FA.read_outline(fp)
    lay = FA.analyze(P)
    Q, info = FA.build_engine_polygon(P, lay)
    check('FPAD3 version', info['adapter'] == 'FPAD3', info['adapter'])
    check('cut is 0.6 m beyond the wing ends: UC = 0.6 + dy', abs(info['uc_kesim_payi'] - (0.6 + info['dy'])) < 1e-9, info['uc_kesim_payi'])
    check('anchor tab is short (4 m) and lies behind the cut (cut y\' >= 10 > tab 4)', abs(info['jog_y_m'] - 4.0) < 1e-9 and info['uc_kesim_payi'] > info['jog_y_m'] + 5.0, info['jog_y_m'])
    check('polygon simple', FA._is_simple(Q))
    xs = sorted(set(round(q[0], 3) for q in Q))
    low_end = [q for q in Q if abs(q[1]) < 1e-6]
    check('lower wing end is SQUARE: two vertices on y\' = 0 (x\' = 0 and the inner wall)', sorted(round(q[0], 3) for q in low_end) == [0.0, round(lay['thin_depth'] + info['dx'], 3)], low_end)
    hi_end = [q for q in Q if abs(q[1] - max(p[1] for p in Q)) < 1e-6]
    check('upper wing end is SQUARE (inner wall corner on the outer corner\'s y\')', len(hi_end) == 2, hi_end)
    cl = info['clip_lines']
    check('two clip lines for the two slanted ends', len(cl) == 2, cl)
    if len(cl) == 2:
        ang = [abs(np.degrees(np.arctan2(c['normal'][1], c['normal'][0]))) for c in cl]
        check('clip normals 30 deg from the corridor-perpendicular axis (bevel 30 deg) and point INTO the footprint',
              abs(cl[0]['normal'][0] - 0.866025) < 1e-5 and abs(cl[0]['normal'][1] - 0.5) < 1e-5 and abs(cl[1]['normal'][0] + 0.866025) < 1e-5 and abs(cl[1]['normal'][1] - 0.5) < 1e-5, [c['normal'] for c in cl])
        check('clip lines pass through the outer corners (0, 484) and (480, 484) of the thin wing and the inner ends (26.558, 438) / (453.442, 438)',
              all(abs((q[0] - c['point'][0]) * c['normal'][0] + (q[1] - c['point'][1]) * c['normal'][1]) < 1e-3 for c, q in ((cl[0], (26.558, 438.0)), (cl[1], (453.442, 438.0)))) and cl[0]['point'] == [0.0, 484.0] and cl[1]['point'] == [480.0, 484.0], cl)
        check('clip box covers the end region only (X -5..87 / 393..485, Y 426..529)', cl[0]['box'][1] < 100 and cl[1]['box'][0] > 380 and cl[0]['box'][2] < 430 and cl[0]['box'][3] > 515, cl[0]['box'])
    check('no warnings for Al\'s footprint', not info['warnings'], info['warnings'])
    # derived file == write_engine_stl of the polygon (the node writes the same bytes)
    os.makedirs(work, exist_ok=True)
    out, info2 = FA.derive(fp, work)
    check('derive() record has clip_lines and the same map', info2['clip_lines'] == cl and info2['map'] == info['map'])
    # footprint WITHOUT bevel: no clip lines, still works
    sq = [(0.0, 0.0), (480.0, 0.0), (480.0, 484.0), (0.0, 484.0)]
    # build an I with square ends from the bevel one: replace the two bevel vertices by the square corners
    P2 = list(P)
    iA = [i for i, p in enumerate(P2) if abs(p[0] - 453.442) < 1e-3 and abs(p[1] - 438.0) < 1e-3][0]
    iB = [i for i, p in enumerate(P2) if abs(p[0] - 26.558) < 1e-3 and abs(p[1] - 438.0) < 1e-3][0]
    P2[iA] = (480.0, 438.0)
    P2[iB] = (0.0, 438.0)
    lay2 = FA.analyze(P2)
    Q2, info3 = FA.build_engine_polygon(P2, lay2)
    check('square-ended footprint: no clip lines, polygon simple, no warnings', info3['clip_lines'] == [] and FA._is_simple(Q2) and not info3['warnings'], (info3['clip_lines'], info3['warnings']))

    # corridor shifted 8 m (dy 1.4): the cut must stay behind the tab (UC >= 10) and the node is told that the wing end is cut straight over the outer part
    import mp8v5_variants as V5
    P3 = V5.build_I(X0=234.5, X1=261.5)
    lay3 = FA.analyze(list(P3))
    Q3, info4 = FA.build_engine_polygon(list(P3), lay3)
    check('shifted corridor (dy %.1f): UC >= 10 (cut behind the 4 m tab) and a warning names the straight outer part' % info4['dy'], info4['uc_kesim_payi'] >= 10.0 - 1e-9 and any('can only be cut' in w for w in info4['warnings']), (info4['uc_kesim_payi'], info4['warnings']))


# ------------------------------------------------------------------------------------------------------------------------------------------
def t_v15(cap, fp):
    sys.path.insert(0, HERE)
    import panel_clip as PC
    import mp8v6_previews3 as P3
    settings = json.load(open(os.path.join(cap, 'settings.json')))
    check('node sends foot narrowing 0', settings['BRIDGE_FOOT_NARROW'] == 0.0, settings['BRIDGE_FOOT_NARROW'])
    check('node sends a circular bridge section (height = width = 27)', abs(settings['KOPRU_YUKSEKLIGI'] - 27.0) < 1e-9 and abs(settings['KOPRU_GENISLIGI'] - 27.0) < 1e-9 and settings['BRIDGE_SECTION_EXP'] == 2.0,
          (settings['KOPRU_YUKSEKLIGI'], settings['KOPRU_GENISLIGI']))
    check('node sends the FPAD3 cut (UC 10.0), transition switch 100, foot blend 100', abs(settings['UC_KESIM_PAYI'] - 10.0) < 1e-9 and settings['GECIS_UZUNLUGU'] == 100.0 and settings['BRIDGE_FOOT_LEN'] == 100.0)
    der = [f for f in os.listdir(os.path.join(cap, '_engine_footprint')) if f.endswith('.adapter.json')][0]
    ad_json = os.path.join(cap, '_engine_footprint', der)
    ad = json.load(open(ad_json))
    check('derived footprint record is FPAD3 with 2 clip lines', ad['adapter'] == 'FPAD3' and len(ad['clip_lines']) == 2)
    stl = os.path.join(cap, 'AYARLANABILIR_GAUSS_KABUK.stl')
    check('shell STL kept (KEEP_STL=1)', os.path.isfile(stl))
    U, _ = M.load_user_mesh(stl, ad_json)
    P = M.footprint_outline(fp)
    pc = M.plan_compare(U, P)
    unders = [c for c in pc['comps'] if c['kind'] == 'under']
    check('shell covers the whole STL outline (nothing missing > 0.5 m, wing ends and thick wing corners included)', pc['area_under'] < 5.0 and not unders, (pc['area_under'], unders[:2]))
    overs = [c for c in pc['comps'] if c['kind'] == 'over' and c['area'] >= 20 and not (c['cy'] > 484.0)]
    check('shell overshoot is only the two end wedges (clipped by the node) and the cap', all(c['cx'] < 40 or c['cx'] > 440 for c in overs) and len(overs) <= 2, [(c['cx'], c['cy'], c['area']) for c in overs])
    ce = M.corridor_edges(pc, ys=range(190, 411, 10))
    gaps = [max(abs(l - 226.5), abs(r - 253.5)) for (_, l, r) in ce if l is not None]
    check('corridor edges straight: shell within 0.5 m of the STL lines for Y 190..410', max(gaps) <= 0.5, max(gaps))
    for y in (260.0, 290.0, 330.0):
        se = M.section_ellipse(U, y)
        check('bridge section at Y = %d is a circle (|A - B| <= 0.15 m, deviation <= 0.1 m)' % y, abs(se['A'] - se['B']) <= 0.15 and se['max_dev'] <= 0.1 and abs(se['A'] - 13.5) <= 0.1, se)
    prof = M.underside_profile(U, [438.0, 152.0, 300.0])
    check('feet touch the ground at both walls (|z| <= 0.35)', abs(prof[0][1]) <= 0.35 and abs(prof[1][1]) <= 0.35, [round(p[1], 2) for p in prof])
    check('no shell vertex below the ground in the bridge band (min z >= -0.35 for X 226..254, Y 160..430)',
          float(U.reshape(-1, 3)[(np.abs(U.reshape(-1, 3)[:, 0] - 240.0) < 13.5) & (U.reshape(-1, 3)[:, 1] > 160) & (U.reshape(-1, 3)[:, 1] < 430), 2].min()) >= -0.35)
    # mouth rim ellipses (end-on)
    sys.path.insert(0, os.path.join(HERE, '..'))
    from scipy.optimize import least_squares

    def fit(Pxy):
        f = lambda p: (np.hypot((Pxy[:, 0] - p[0]) / p[2], (Pxy[:, 1] - p[1]) / p[3]) - 1.0) * np.sqrt(p[2] * p[3])
        s = least_squares(f, [Pxy[:, 0].mean(), Pxy[:, 1].mean(), np.ptp(Pxy[:, 0]) / 2, np.ptp(Pxy[:, 1]) / 2])
        return s.x, f(s.x)
    for x0, nm in ((1.0, 'left'), (479.0, 'right')):
        T = U.reshape(-1, 3)
        S = M.slice_plane_x(U, x0)
        S = S[S[:, 0] > 437]
        p, r = fit(S)
        check('%s mouth (section 0.4 m inside the cut, X = %.1f) is an ellipse: deviation <= 0.45 m (<= 2 %% of B)' % (nm, x0), np.abs(r).max() <= 0.45, round(float(np.abs(r).max()), 3))
    # panels
    n, panels, tabs, st = P3.user_panels(os.path.join(cap, 'BAKLAVA_PANELS.bkl'), ad_json, clip=True)
    rep = json.load(open(os.path.join(cap, 'baklava_report.json')))
    check('engine panel report: no warnings, field-aligned lattice', not rep['warnings'] and rep['lattice'] == 'field-aligned', rep['warnings'])
    check('panel quality: edges 10 % >= 0.93, min triangle angle >= 25, coverage >= 0.95, deviation <= 0.4 m', rep['edge_within_10pct'] >= 0.93 and rep['tri_angle_min'] >= 25.0 and rep['coverage_ratio'] >= 0.95 and rep['panel_to_shell_dev_max_m'] <= 0.4,
          (rep['edge_within_10pct'], rep['tri_angle_min'], rep['coverage_ratio'], rep['panel_to_shell_dev_max_m']))
    check('clip statistics: both ends clipped (partial >= 10, removed >= 10, remaining fraction min >= 0.03)', st['partial'] >= 10 and st['removed'] >= 10 and (st['remaining_fraction_min'] or 0) >= 0.03, st)
    worst = 0.0
    allp = []
    for kind, v in panels:
        a = np.frombuffer(v, dtype=np.float32).reshape(-1, 3).astype(float)
        allp.append(a)
    A = np.vstack(allp)
    for c in ad['clip_lines']:
        b = c['box']
        sel = (A[:, 0] >= b[0]) & (A[:, 0] <= b[1]) & (A[:, 1] >= b[2]) & (A[:, 1] <= b[3])
        s = (A[sel, 0] - c['point'][0]) * c['normal'][0] + (A[sel, 1] - c['point'][1]) * c['normal'][1]
        worst = min(worst, float(s.min()))
        check('all panel vertices lie on the kept side of the slanted end line (>= -5 mm: vertices within the 4 mm snap stay)', float(s.min()) >= -0.005, round(float(s.min()), 5))
        check('panel vertices lie ON the slanted line (>= 20 within 5 mm)', int((np.abs(s) < 0.005).sum()) >= 20, int((np.abs(s) < 0.005).sum()))
    # panel plan coverage vs the STL outline (panels incl. clipped): missing / overshoot
    from PIL import Image, ImageDraw
    from scipy import ndimage
    res = 0.25
    x0, y0, W, H = -30.0, -20.0, int(570 / res), int(580 / res)
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    for kind, v in panels:
        a = np.frombuffer(v, dtype=np.float32).reshape(-1, 3)
        if kind >= 2:
            for t in a.reshape(-1, 3, 3):
                d.polygon([((q[0] - x0) / res, (q[1] - y0) / res) for q in t], fill=1)
        else:
            tri = tabs[kind]
            for (i, j, k) in tri:
                d.polygon([((a[q, 0] - x0) / res, (a[q, 1] - y0) / res) for q in (i, j, k)], fill=1)
    Sm = ndimage.binary_closing(np.asarray(im).astype(bool), iterations=3)
    Tm = M.raster_polys([P], res, x0, y0, W, H)
    dT = ndimage.distance_transform_edt(~Tm) * res
    dS = ndimage.distance_transform_edt(~Sm) * res
    over = Sm & ~Tm & (dT > 0.6)
    under = Tm & ~Sm & (dS > 0.6)
    lab, nn = ndimage.label(over)
    comps = []
    for k in range(1, nn + 1):
        yy, xx = np.nonzero(lab == k)
        if len(yy) * res * res >= 20:
            comps.append((round(x0 + xx.mean() * res, 1), round(y0 + yy.mean() * res, 1), round(len(yy) * res * res, 1)))
    check('panels: overshoot beyond the STL outline only at the cap (Y > 484) - the slanted ends are straight on the STL line', all(c[1] > 484.0 for c in comps), comps)
    check('panels: STL area without panels (> 0.6 m from any panel) <= 60 m2 (gaps between panels excluded)', float(under.sum() * res * res) <= 60.0, round(float(under.sum() * res * res), 1))
    json.dump(dict(clip=st, report={k: rep[k] for k in ('panels_total', 'rhombus_panels', 'triangle_panels', 'edge_len_min', 'edge_len_max', 'tri_angle_min', 'tri_angle_max', 'irregular_share', 'panel_to_shell_dev_max_m', 'coverage_ratio')},
                   corridor_gap_max=max(gaps), plan_under=pc['area_under'], plan_over=[(c['cx'], c['cy'], c['area']) for c in pc['comps'] if c['kind'] == 'over']), open(os.path.join(cap, 'selftest_v15_numbers.json'), 'w'), indent=1)


# ------------------------------------------------------------------------------------------------------------------------------------------
def t_engine3(root, engine, exe, fp, base):
    from concurrent.futures import ThreadPoolExecutor
    import mp8v6_adapter_v3 as A3
    os.makedirs(root, exist_ok=True)
    out3, info3 = A3.derive_v3(fp, os.path.join(root, 'fp3'))
    ovr = {'KEEP_Y_ORIGIN': True, 'UC_KESIM_PAYI': info3['uc_kesim_payi'], 'SLANT_CUTS': info3['slant_cuts'], 'SLANT_SPLIT_X': info3['slant_split_x'], 'BRIDGE_FOOT_NARROW': 0.0,
           'BRIDGE_FOOT_WALL_X': info3['bridge_foot_wall_x'], 'PANEL_EDGE': 0.0}
    fp_v2 = os.path.join(root, 'fpv2')
    outv2, infov2 = FA.derive(fp, fp_v2)
    jobs = {
        'reg_exe': dict(footprint=outv2, exe=exe, ov={'PANEL_EDGE': 0.0, 'UC_KESIM_PAYI': infov2['uc_kesim_payi']}),
        'reg_py': dict(footprint=outv2, engine=engine, ov={'PANEL_EDGE': 0.0, 'UC_KESIM_PAYI': infov2['uc_kesim_payi']}),
        'slant': dict(footprint=out3, engine=engine, ov=dict(ovr, KOPRU_YUKSEKLIGI=27.0)),
        'ramp25': dict(footprint=out3, engine=engine, ov=dict(ovr, KOPRU_YUKSEKLIGI=27.0, BRIDGE_FOOT_PROFILE=1, BRIDGE_FOOT_ANGLE=25.0)),
        'ramp30': dict(footprint=out3, engine=engine, ov=dict(ovr, KOPRU_YUKSEKLIGI=27.0, BRIDGE_FOOT_PROFILE=1, BRIDGE_FOOT_ANGLE=30.0)),
        'ramp35': dict(footprint=out3, engine=engine, ov=dict(ovr, KOPRU_YUKSEKLIGI=27.0, BRIDGE_FOOT_PROFILE=1, BRIDGE_FOOT_ANGLE=35.0)),
        'arc': dict(footprint=out3, engine=engine, ov=dict(ovr, KOPRU_YUKSEKLIGI=27.0, BRIDGE_FOOT_PROFILE=2)),
    }

    def run(name):
        j = jobs[name]
        rc, d = RUN.run(name, base, j['footprint'], j['ov'], exe=j.get('exe'), engine=j.get('engine'), out_root=root)
        return name, rc, d
    with ThreadPoolExecutor(max_workers=4) as ex:
        res = {n: (rc, d) for n, rc, d in ex.map(run, list(jobs))}
    for n, (rc, d) in res.items():
        check('engine run %s exits 0' % n, rc == 0)
    stl = lambda n: os.path.join(res[n][1], 'AYARLANABILIR_GAUSS_KABUK.stl')       # noqa: E731
    md = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()                    # noqa: E731
    check('REGRESSION: prototype engine without the new settings == frozen exe (byte-identical shell STL)', md(stl('reg_exe')) == md(stl('reg_py')), (md(stl('reg_exe')), md(stl('reg_py'))))
    ad3 = os.path.join(root, 'fp3', [f for f in os.listdir(os.path.join(root, 'fp3')) if f.endswith('.adapter.json')][0])
    P = M.footprint_outline(fp)
    U, _ = M.load_user_mesh(stl('slant'), ad3)
    pc = M.plan_compare(U, P)
    check('slanted cut: nothing missing > 0.5 m (thin-wing ends and thick-wing corners covered)', pc['area_under'] < 2.0, pc['area_under'])
    import mp8v6_rims as RH
    loops = RH.loops(stl('slant'), ad3)
    check('slanted cut: exactly 3 open boundary loops (two mouths + thick wing)', len(loops) == 3, [len(l) for l in loops])
    L = [l for l in loops if len(l) < 1500 and l.mean(0)[0] < 240][0]
    d = (L[:, 0] - 0.0) * 0.866025 + (L[:, 1] - 484.0) * 0.5
    check('slanted cut: the left rim lies in ONE vertical plane (max distance <= 1 mm)', float(np.abs(d).max()) <= 0.001, float(np.abs(d).max()))
    s = (L[:, 0] - 0.0) * 0.5 + (L[:, 1] - 484.0) * (-0.866025)
    p, r = RH.fit(np.c_[s, L[:, 2]])
    check('slanted cut: the left rim is an ellipse in its plane (A = 35 / cos 30 = 40.4 +- 0.3, deviation <= 0.4 m)', abs(p[2] - 40.41) <= 0.3 and np.abs(r).max() <= 0.4, (round(float(p[2]), 2), round(float(np.abs(r).max()), 3)))
    for nm, ang in (('ramp25', 25.0), ('ramp30', 30.0), ('ramp35', 35.0)):
        U2, _ = M.load_user_mesh(stl(nm), ad3)
        fa = M.foot_angles(U2, y_lo=300.0, y_hi=446.0)
        Y, z, a = fa['Y'], fa['z'], np.abs(fa['angle'])
        ramp = (Y > 380) & (a >= ang - 3.0)
        am = float(np.median(a[ramp])) if ramp.any() else -1.0
        check('%s: median angle of the thin-foot ramp %.1f deg is within +-3 deg of the setting %.0f' % (nm, am, ang), abs(am - ang) <= 3.0, am)
        zt = lambda yy: float(z[list(Y).index(yy)])            # noqa: E731
        check('%s: the underside touches the ground at the thin wall Y = 438 (|z| <= 0.35)' % nm, abs(zt(438.0)) <= 0.35, round(zt(438.0), 2))
        U3, _ = M.load_user_mesh(stl(nm), ad3)
        fb = M.foot_angles(U3, y_lo=140.0, y_hi=300.0)
        zb = float(fb['z'][list(fb['Y']).index(152.0)])
        check('%s: the underside touches the ground at the thick wall Y = 152 (|z| <= 0.35; the right foot needs +0.2 m calibration)' % nm, abs(zb) <= 0.35, round(zb, 2))
    Ua, _ = M.load_user_mesh(stl('arc'), ad3)
    fa = M.foot_angles(Ua, y_lo=140.0, y_hi=446.0)
    check('arc: foot angle 15..26 deg, crown 28..30 m, walls on the ground', 15.0 <= fa['thin_foot']['max_angle'] <= 26.0 and 28.0 <= float(fa['z'][list(fa['Y']).index(290.0)]) <= 30.0 and abs(float(fa['z'][list(fa['Y']).index(438.0)])) <= 0.35, (fa['thin_foot'], fa['thick_foot']))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=('adapter', 'v15', 'engine3'))
    ap.add_argument('a')
    ap.add_argument('b', nargs='?')
    ap.add_argument('--engine')
    ap.add_argument('--exe')
    ap.add_argument('--base')
    a = ap.parse_args()
    if a.cmd == 'adapter':
        import tempfile
        t_adapter(a.a, tempfile.mkdtemp(prefix='mp8v6_ad_'))
    elif a.cmd == 'v15':
        t_v15(a.a, a.b)
    else:
        t_engine3(a.a, a.engine, a.exe, a.b, a.base)
    print('ALL PASS' if not FAILS else 'FAILED: ' + ', '.join(FAILS))
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
