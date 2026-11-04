#!/usr/bin/env python3
"""mp8v6_variants.py - robustness test of adapter FPAD3 + the node's slanted-end clip: the 10 synthetic variants of Al's 'I' footprint (mp8v5_variants.VARIANTS) go through the REAL node
(MashProject8_v15.dyn via engine_capture.py: adapter -> real MashEngine.exe -> panels -> clip) and are measured against THEIR OWN outline. No Revit.

  python mp8v6_variants.py OUTROOT [--workers 4] [--only v0,v1,...] [--graph MashProject8_v15.dyn]

Per variant: node status / warnings / clip statistics, panels (count, quality), shell plan vs the variant outline (missing > 0.5 m, overshoot components), corridor edge straightness, mouth ellipses
(section 1 m inside the shell ends), bridge circle at the middle, feet at the walls, panel vertices on the kept side of the clip lines.
"""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, HERE)
import footprint_adapter as FA   # noqa: E402
import mp8v5_variants as V5      # noqa: E402
import mp8v6_measure as M        # noqa: E402
import mp8v6_rims as RH          # noqa: E402


def run_variant(name, kw, a):
    out = os.path.join(a.outroot, name)
    os.makedirs(out, exist_ok=True)
    P = V5.build_I(**kw)
    stl = os.path.join(out, 'Footprint_%s.stl' % name)
    FA.write_engine_stl(stl, P, 'variant %s of Footprint_261014' % name)
    env = dict(os.environ, KEEP_STL='1', PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, '-u', '-I', os.path.join(HERE, 'engine_capture.py'), a.graph, out, '0=' + stl], capture_output=True, text=True, env=env, encoding='utf-8', errors='replace')
    res = {'variant': name, 'params': kw, 'exit': r.returncode, 'stdout_tail': (r.stdout.strip().splitlines() or [''])[-3:], 'stderr_tail': (r.stderr.strip().splitlines() or [''])[-3:]}
    rj = [f for f in os.listdir(out) if f.endswith('_result.json')]
    if not rj:
        return res
    j = json.load(open(os.path.join(out, rj[0])))
    d = j['data']
    res['status'] = j.get('Status')
    if j.get('status') == 'error':
        res['message'] = d.get('message')
        return res
    res['warnings'] = d.get('input_warnings')
    res['panel_counts'] = d.get('panel_counts')
    res['ends_clip'] = d.get('ends_clip')
    q = d.get('panel_quality', {})
    res['panels'] = {k: q.get(k) for k in ('edge_within_10pct', 'tri_angle_min', 'tri_angle_max', 'panel_to_shell_dev_max_m', 'coverage_ratio', 'warnings', 'lattice')}
    ad_json = os.path.join(out, '_engine_footprint', [f for f in os.listdir(os.path.join(out, '_engine_footprint')) if f.endswith('.adapter.json')][0])
    ad = json.load(open(ad_json))
    res['adapter'] = {k: ad.get(k) for k in ('dx', 'dy', 'inset_m', 'cap_depth_m', 'uc_kesim_payi', 'corridor_width_m', 'thin_wing_depth_m', 'thick_wing_depth_m', 'bevel_len_m', 'wall_x_engine')}
    res['clip_lines'] = ad.get('clip_lines')
    sp = os.path.join(out, 'AYARLANABILIR_GAUSS_KABUK.stl')
    if os.path.isfile(sp):
        Pa = np.array(P)
        U, _ = M.load_user_mesh(sp, ad_json)
        pc = M.plan_compare(U, Pa)
        res['plan_missing_m2'] = round(pc['area_under'], 1)
        res['plan_over'] = [(round(float(c['cx']), 1), round(float(c['cy']), 1), c['area']) for c in pc['comps'] if c['kind'] == 'over' and c['area'] >= 20]
        res['plan_under'] = [(round(float(c['cx']), 1), round(float(c['cy']), 1), c['area']) for c in pc['comps'] if c['kind'] == 'under' and c['area'] >= 20]
        X0, X1 = float(Pa[:, 0].min()), float(Pa[:, 0].max())
        for nm, x0 in (('left', X0 + 1.0), ('right', X1 - 1.0)):
            S = M.slice_plane_x(U, x0)
            S = S[S[:, 0] > float(Pa[:, 1].max()) - 60.0]
            try:
                p, r_ = RH.fit(S)
                res['mouth_' + nm] = dict(A=round(float(p[2]), 2), B=round(float(p[3]), 2), max_dev=round(float(np.abs(r_).max()), 3), pct_B=round(float(np.abs(r_).max() / p[3] * 100), 2))
            except Exception as exc:
                res['mouth_' + nm] = str(exc)[:80]
        lay = FA.analyze(list(P))
        ylo, yhi = lay['corridor_lo'], lay['corridor_hi']
        ym = 0.5 * (ylo + yhi)
        pp = dict(V5.AL)
        pp.update(kw)
        ce = M.corridor_edges(pc, ys=range(int(pp['Ya'] + 45), int(pp['Yb'] - 45), 10))
        gaps = [max(abs(l - ylo), abs(r - yhi)) for (_, l, r) in ce if l is not None]
        res['corridor_edges_gap_max_m'] = round(max(gaps), 2) if gaps else None
        res['bridge_section_mid'] = M.section_ellipse(U, 0.5 * (pp['Ya'] + pp['Yb']), x_lo=ym - 40, x_hi=ym + 40)
    # panels on the kept side of the clip lines
    try:
        import mp8v6_previews3 as P3
        n, panels, tabs, st = P3.user_panels(os.path.join(out, 'BAKLAVA_PANELS.bkl'), ad_json, clip=True)
        A = np.vstack([np.frombuffer(v, dtype=np.float32).reshape(-1, 3).astype(float) for k, v in panels])
        worst = 0.0
        for c in ad.get('clip_lines') or []:
            b = c['box']
            sel = (A[:, 0] >= b[0]) & (A[:, 0] <= b[1]) & (A[:, 1] >= b[2]) & (A[:, 1] <= b[3])
            s = (A[sel, 0] - c['point'][0]) * c['normal'][0] + (A[sel, 1] - c['point'][1]) * c['normal'][1]
            worst = min(worst, float(s.min()))
        res['panel_min_side_distance_m'] = round(worst, 5)
        res['clip_stats_check'] = st
    except Exception as exc:
        res['clip_check_error'] = str(exc)[:200]
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outroot')
    ap.add_argument('--graph', default=os.path.join(ROOT, 'MashProject8', 'MashProject8_Paylas_V5', 'MashProject8_v15.dyn'))
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--only', default='')
    a = ap.parse_args()
    os.makedirs(a.outroot, exist_ok=True)
    names = [n for n in V5.VARIANTS if (not a.only or any(n.startswith(o) for o in a.only.split(',')))]
    results = []
    with ThreadPoolExecutor(a.workers) as ex:
        for r in ex.map(lambda n: run_variant(n, V5.VARIANTS[n], a), names):
            results.append(r)
            print(json.dumps(r, default=str)[:2500], flush=True)
    json.dump(results, open(os.path.join(a.outroot, 'variants_results.json'), 'w'), indent=1, default=str)
    return 0


if __name__ == '__main__':
    sys.exit(main())
