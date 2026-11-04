#!/usr/bin/env python3
"""mp9_selftest.py - offline logic test of MashProject9_v11 (ForDynamo/baklava-panels/MashProject9_v11.py + the .dyn) on a FAKE Revit.

  python mp9_selftest.py ENGINE_OUTPUT_DIR [ENGINE_OUTPUT_DIR_WITH_GAP_0.1]

ENGINE_OUTPUT_DIR = folder written by engine_capture.py with panel gap 0 (BAKLAVA_PANELS.bkl + baklava_report.json: REAL engine output at
the user's saved slider values). The optional second folder is the same run with gap 0.1 (negative test: corners are not shared).
The node code and its IN values are read from the .dyn, so the graph that is handed over is the graph that is tested.

Proves: lattice rebuilt from the real panel file == the engine's own vertex/triangle counts (7,889 / 15,482 in the full set), Max-triangles
subset = whole panels, deterministic; WRITE is refused in a project / non-Mass family WITHOUT starting the engine; the dry run creates nothing
anywhere; the V7 block creates points / 3 curves / one Form per triangle in ONE transaction; the DataStorage ownership record round-trips
and a re-run replaces exactly the previous result (REBUILD) and nothing else; rollback keeps the old result; clamp+warn; error paths.
Does NOT prove pythonnet, NewFormByCap, DataStorage or any timing in the real Revit.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import struct
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mp9_stubs as S                      # noqa: E402
from graph_inputs import graph_inputs, load  # noqa: E402

WS = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
WORK = os.path.join(WS, "ForDynamo", "baklava-panels")
ROOT = os.path.join(WS, "MashProject9")
DYN = os.path.join(WORK, "MashProject9_v11.dyn")
PY = os.path.join(WORK, "MashProject9_v11.py")
NAME_RE = re.compile(r'^[A-Za-z0-9_\-]{1,180}$')


def node_code(dyn):
    d = load(dyn)
    return [n for n in d["Nodes"] if "Python" in n.get("ConcreteType", "")][0]["Code"]


def tiny_stl(path):
    tris = [((0, 0, 0), (1, 0, 0), (0, 1, 0)), ((1, 0, 0), (1, 1, 0), (0, 1, 0))]
    with open(path, 'wb') as f:
        f.write(b'\0' * 80)
        f.write(struct.pack('<I', len(tris)))
        for t in tris:
            f.write(struct.pack('<12fH', 0, 0, 1, *t[0], *t[1], *t[2], 0))


class Engine(object):
    calls = 0


def run_code(code, IN, engine_dir, report_patch=None, bad_version=False, captured=None):
    stubs = S.build_stubs()
    saved = {k: sys.modules.get(k) for k in stubs}
    sys.modules.update(stubs)
    real_run = subprocess.run
    rep = json.load(open(os.path.join(engine_dir, 'baklava_report.json')))
    if report_patch:
        rep.update(report_patch)

    def fake_run(cmd, **kw):
        Engine.calls += 1
        out_dir = cmd[cmd.index('--output-dir') + 1]
        if captured is not None:
            captured['settings'] = json.load(open(cmd[cmd.index('--settings') + 1]))
            captured['timeout'] = kw.get('timeout')
        tiny_stl(os.path.join(out_dir, 'AYARLANABILIR_GAUSS_KABUK.stl'))
        shutil.copy(os.path.join(engine_dir, 'BAKLAVA_PANELS.bkl'), os.path.join(out_dir, 'BAKLAVA_PANELS.bkl'))
        j = {'Version': 'WRONG' if bad_version else re.search(r"ENGINE_VERSION = '([^']+)'", code).group(1), 'Triangles': 2, 'Panels': rep}
        return types.SimpleNamespace(returncode=0, stdout='noise\n' + json.dumps(j) + '\n', stderr='')
    subprocess.run = fake_run
    ns = {'IN': IN, '__name__': '__node__'}
    try:
        exec(compile(code, 'node', 'exec'), ns)
    finally:
        subprocess.run = real_run
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return ns['OUT'], ns


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    argv = [a for a in sys.argv[1:] if not a.startswith('--')]
    engine_dir = argv[0]
    engine_gap = argv[1] if len(argv) > 1 else None
    fails = []

    def check(name, cond, info=''):
        print(('PASS ' if cond else 'FAIL ') + name + ('  ' + str(info)[:260] if info != '' else ''))
        if not cond:
            fails.append(name)

    work = tempfile.mkdtemp(prefix='mp9v11_')
    rep = json.load(open(os.path.join(engine_dir, 'baklava_report.json')))
    code = node_code(DYN)
    base_in = graph_inputs(DYN)

    # ---- static -----------------------------------------------------------------------------------------------------
    check('graph embeds the .py (working copy)', code.replace('\r\n', '\n') == open(PY, encoding='utf-8').read().replace('\r\n', '\n'))
    check('root package .dyn == working copy .dyn', open(os.path.join(ROOT, 'MashProject9_v11.dyn'), 'rb').read() == open(DYN, 'rb').read())
    check('57 inputs: IN[0..50] as MashProject8_v10, IN[51] Max triangles, IN[52]/IN[53] patch seed, IN[54] commit every N, IN[55] share edge curves, IN[56] reuse engine result; '
          'WRITE False (dry run), gap 0, speed options OFF by default (0 / False / False)',
          len(base_in) == 57 and base_in[26] is False and base_in[22] == 0.0 and base_in[21] == 4 and base_in[54] == 0 and base_in[55] is False and base_in[56] is False and base_in[52] == 0.0 and base_in[53] == 0.0,
          (len(base_in), base_in[26], base_in[22], base_in[54], base_in[55], base_in[56]))
    dyn_json = load(DYN)
    lnode = [n for n in dyn_json['Nodes'] if n['Id'] in [v['Id'] for v in dyn_json['View']['NodeViews'] if v['Name'].startswith('Baklava Panel Edge L')]][0]
    check('panel edge L slider: step 0.05 (2.75 and 2.7 can be entered), range 0..15', abs(lnode['StepValue'] - 0.05) < 1e-9 and lnode['MinimumValue'] == 0 and lnode['MaximumValue'] == 15, (lnode['StepValue'], lnode['MinimumValue'], lnode['MaximumValue']))
    v10 = graph_inputs(os.path.join(WS, 'MashProject8', 'MashProject8_Paylas_V3', 'MashProject8_v10.dyn'))
    same = [i for i in range(51) if i not in (20, 22, 26, 28) and v10[i] == base_in[i]]
    check('slider panel identical to the user saved MashProject8_v10 (all IN[0..50] except L (the user chose it), gap, WRITE, result folder)', len(same) == 47, (len(same), [i for i in range(51) if i not in same]))
    check('file inputs exist (exe + Footprint.stl of MashProject8_Paylas_V3, result folder = MashProject9)', os.path.isfile(base_in[0]) and os.path.isfile(base_in[1]) and
          os.path.normpath(base_in[28]) == os.path.normpath(ROOT), (base_in[0], base_in[1], base_in[28]))
    stripped = '\n'.join(l for l in code.split('\n') if not l.strip().startswith('#'))
    check('no O2 / family / probe / enum-ToString code left', not any(w in stripped for w in ('NewFamilyDocument', 'LoadFamily', 'SaveAs', '_staging', 'ToString',
                                                                                              'MassDisplay', 'DirectShape', 'enum_text', 'tile')),
          [w for w in ('NewFamilyDocument', 'LoadFamily', 'SaveAs', '_staging', 'ToString', 'MassDisplay', 'DirectShape', 'enum_text', 'tile') if w in stripped])
    items = sorted(os.listdir(ROOT))
    check('root MashProject9 holds only the one graph + START_HERE + archive (+ run outputs)',
          all(i in ('MashProject9_v11.dyn', 'START_HERE_TR.txt', '_arsiv_O2') or i.startswith('MashProject9_v11_') for i in items), items)

    def IN(**kw):
        v = list(base_in)
        v[20], v[26], v[51] = 6.0, False, 1500          # test baseline = the lattice of the engine output used here (L 6); the graph may carry the user's own L / Max triangles
        v[28] = work
        for k, val in kw.items():
            v[int(k[1:])] = val
        return v

    def fresh(kind='mass', mass_category=True):
        for f in os.listdir(work):
            p_ = os.path.join(work, f)
            if os.path.isdir(p_):
                shutil.rmtree(p_, ignore_errors=True)
            else:
                os.remove(p_)
        Engine.calls = 0
        return S.W.reset(kind, mass_category)

    # 1 dry run in a PROJECT ------------------------------------------------------------------------------------------
    doc = fresh('project')
    cap = {}
    t0 = time.time()
    out, ns = run_code(code, IN(i22=0.1), engine_dir, captured=cap)
    print('   dry run python side: %.1f s (engine faked)' % (time.time() - t0))
    d = out.get('data', {})
    lat = d.get('lattice', {})
    sel = d.get('selection', {})
    check('dry run works in a project: status dry-run', out.get('status') == 'dry-run', out.get('Status') or out.get('Message'))
    check('dry run created nothing and opened no transaction', len(doc.elements) == 3 and S.W.transactions == [] and doc.open_tx is None)
    check('engine gap forced to 0 + warning (gap input 0.1 on purpose)', cap['settings'].get('PANEL_GAP') == 0.0 and any('gap' in w.lower() for w in d.get('input_warnings', [])), d.get('input_warnings'))
    check('target document reported: project, not ok, Turkish instruction', d['target_document']['ok'] is False and d['target_document']['kind'] == 'project' and
          'File ▸ New ▸ Conceptual Mass ▸ Metric Mass.rft' in d['target_document']['message'] and any('reddedilir' in w for w in d['warnings']), d['target_document'])
    check('lattice == engine report (7,889 / 15,482), manifold, Euler -1, orientation consistent',
          lat.get('matches_engine_report') is True and lat['vertices'] == rep['vertices'] == 7889 and lat['triangles'] == rep['triangles'] == 15482 and
          lat['non_manifold_edges'] == 0 and lat['euler_characteristic'] == -1 and lat['orientation_conflicts'] == 0, lat)
    q = d['triangle_quality']
    check('quality + equilateral deviation + flat-vs-shell figures present',
          q['angle_deg']['min'] == 32.1 and q['angle_deg']['max'] == 97.2 and 0.93 < q['share_all_angles_within_10deg_of_60'] < 0.96 and 'all' in q['flat_triangle_vs_shell_deviation'],
          (q['angle_deg'], q['share_all_angles_within_10deg_of_60']))
    pc = d['panel_counts']
    check('panel counts 7,669 rhombi + 144 lone = 15,482 triangles, 298 rim', pc['triangles_total'] == 2 * 7669 + 144 and pc['lone_triangles'] == 144 and pc['rim_triangles'] == 298, pc)
    check('Max triangles 1500: whole panels only, 1499..1500 triangles, forms == triangles, curves == 3 x triangles, document RP = nodes + forms',
          1499 <= sel['triangles'] <= 1500 and sel['forms'] == sel['triangles'] and sel['curve_by_points'] == 3 * sel['triangles'] and sel['of_total'] == 15482 and
          sel['rhombus_panels'] * 2 + sel['lone_triangles'] == sel['triangles'] and sel['reference_points_in_document_expected'] == sel['reference_points'] + sel['forms'], sel)
    shp = sel['shape']
    check('PATCH IS COMPACT (the first version was a 22 x 433 x 46 m wall = 9.4): bbox longest/middle < 2, 3 bbox dimensions all >= 40 m, no thin-strip warning',
          shp['longest_to_middle'] < 2.0 and min(shp['bbox_dimensions_m']) >= 40.0 and not any('İNCE ŞERİT' in x for x in d['warnings']), shp)
    check('patch is ONE connected piece (node count) and the report says so', shp['connected_components'] == 1 and sel['seed']['mode'] == 'automatic seed' and sel['seed']['candidates_tested'] > 20, (shp, sel['seed']['mode']))
    print('   AUTO PATCH N=1500: bbox %s m, L/M %.2f, L/S %.1f, boundary edges %d (%.3f per triangle), seed centroid %s, geodesic radius %.0f m' % (
        shp['bbox_dimensions_m'], shp['longest_to_middle'], shp['longest_to_shortest'], shp['boundary_edges'], shp['boundary_edges_per_triangle'],
        sel['seed']['seed_centroid_m'], sel['seed']['geodesic_radius_m']))
    check('estimate = QUADRATIC model of the real runs (1500 Forms: minutes, not the old n^1.31); range text; subset warning',
          100 < d['estimate']['seconds'] < 900 and 'quadratic' in d['estimate']['basis'] and ' - ' in d['estimate']['range_text'] and 'UNMEASURED' in d['estimate']['applies_to'] and any('Yalnız' in w for w in d['warnings']), d['estimate'])
    rp = os.path.join(work, 'MashProject9_v11_result.json')
    mp = os.path.join(work, 'MashProject9_v11_triangle_map.json')
    check('result json + triangle map file written', os.path.isfile(rp) and os.path.isfile(mp))
    full = json.load(open(rp, encoding='utf-8'))
    tm = full.get('triangle_map', {})
    check('triangle_map is a top-level key of the result FILE, not in OUT', 'triangle_map' in full and 'triangle_map' not in out and 'triangle_map' not in d)
    check('map arrays have one entry per lattice triangle', all(len(tm[k]) == 15482 for k in ('tri_nodes', 'tri_panel_index', 'tri_half', 'tri_flags')))
    ok = all(set(tm['tri_nodes'][r[1]]) & set(tm['tri_nodes'][r[2]]) == {r[3], r[4]} and tm['tri_half'][r[1]] == 'a' and tm['tri_half'][r[2]] == 'b' for r in tm['rhombi'])
    check('every rhombus = two triangles sharing exactly the stored diagonal (a, b)', ok and len(tm['rhombi']) == 7669)
    check('lone triangles flagged U, their panel index follows the rhombi', all('U' in tm['tri_flags'][i] for i, h in enumerate(tm['tri_half']) if h == '-') and
          min(tm['tri_panel_index'][i] for i, h in enumerate(tm['tri_half']) if h == '-') == 7670)
    subset = tm['subset']
    inset = set(subset)
    check('subset == whole panels (both halves of every rhombus), sorted, unique, size == selection',
          len(subset) == sel['triangles'] == len(inset) and subset == sorted(subset) and all(((r[1] in inset) == (r[2] in inset)) for r in tm['rhombi']))
    # independent connectivity check from the map (shared node pairs), not from the node's own adjacency
    edges = {}
    for i in subset:
        t = tm['tri_nodes'][i]
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            edges.setdefault((min(a, b), max(a, b)), []).append(i)
    nb = {i: set() for i in subset}
    for pair in edges.values():
        for x in pair:
            for y in pair:
                if x != y:
                    nb[x].add(y)
    seen, stack = {subset[0]}, [subset[0]]
    while stack:
        for y in nb[stack.pop()]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    check('subset is edge-connected (checked independently from tri_nodes of the map file)', len(seen) == len(subset), (len(seen), len(subset)))
    out2, _ = run_code(code, IN(), engine_dir)
    check('subset is deterministic (second run gives the same list)', json.load(open(mp, encoding='utf-8'))['subset'] == subset)
    # seed X,Y, sizes, strip warning ----------------------------------------------------------------------------------------
    for N in (300, 777, 2000):
        o, _ = run_code(code, IN(i51=N), engine_dir)
        sl = o['data']['selection']
        check('Max triangles %d: %d or %d triangles (whole panels), compact, connected' % (N, N, N - 1), N - 1 <= sl['triangles'] <= N and sl['shape']['longest_to_middle'] < 3.0 and sl['shape']['connected_components'] == 1,
              (sl['triangles'], sl['shape']))
    for xy, label in (((237, 250), 'bridge centre'), ((60, 250), 'arm/bridge junction'), ((420, 250), 'right body')):
        o, _ = run_code(code, IN(i52=float(xy[0]), i53=float(xy[1])), engine_dir)
        sl = o['data']['selection']
        c = sl['seed']['seed_centroid_m']
        check('seed X,Y %s (%s): seed triangle within 10 m of the point in plan, mode says so, connected, 1499..1500' % (xy, label),
              sl['seed']['mode'] == 'seed X,Y given' and ((c[0] - xy[0]) ** 2 + (c[1] - xy[1]) ** 2) ** 0.5 < 10.0 and sl['shape']['connected_components'] == 1 and 1499 <= sl['triangles'] <= 1500,
              (sl['seed'], sl['triangles']))
    o, _ = run_code(code, IN(i52=1000.0, i53=1000.0), engine_dir)
    check('seed far outside the shell -> nearest triangle + warning, still a patch', any('yüzeyin dışında' in x for x in o['data']['warnings']) and o['data']['selection']['triangles'] >= 1499, o['data']['warnings'])
    o, ns_ = run_code(code, IN(), engine_dir)
    lat_ = ns_['lattice_from_panels'](*[ns_['read_panels'](os.path.join(engine_dir, 'BAKLAVA_PANELS.bkl'))[i] for i in (1, 0)][::1]) if False else None
    n_sub_, panels_ = ns_['read_panels'](os.path.join(engine_dir, 'BAKLAVA_PANELS.bkl'))
    lat_ = ns_['lattice_from_panels'](panels_, n_sub_)
    ns_['lattice_checks'](lat_)
    ns_['build_adjacency'](lat_)
    old = []
    pk = []
    for pi in range(len(lat_['first_tri'])):
        idx = ns_['panel_triangles'](lat_, pi)
        pts = [lat_['nodes'][g] for i in idx for g in lat_['tris'][i]]
        pk.append((round(sum(p[0] for p in pts) / len(pts), 3), round(sum(p[1] for p in pts) / len(pts), 3), pi, idx))
    pk.sort()
    for cx_, cy_, pi, idx in pk:
        if len(old) + len(idx) > 1500:
            break
        old += idx
    oshape = ns_['patch_shape'](lat_, sorted(old))
    check('the FIRST version (x-sorted strip) measured 22 x 433 x 46 m, L/M 9.4, and the thin-strip warning fires on it; not on the new patch',
          oshape['longest_to_middle'] > 9 and ns_['strip_warning'](oshape) is not None and 'İNCE ŞERİT' in ns_['strip_warning'](oshape) and ns_['strip_warning'](shp) is None, oshape)
    print('   OLD STRIP for comparison: bbox %s m, L/M %.1f, boundary edges %d' % (oshape['bbox_dimensions_m'], oshape['longest_to_middle'], oshape['boundary_edges']))
    # 2 WRITE refused in a project / non-Mass family, engine NOT started -----------------------------------------------
    doc = fresh('project')
    out, ns = run_code(code, IN(i26=True), engine_dir)
    check('WRITE in a project -> ERROR with the Turkish instruction, nothing created, engine not started',
          out.get('Status') == 'ERROR' and 'Önce File ▸ New ▸ Conceptual Mass ▸ Metric Mass.rft aç ve grafiği orada çalıştır.' in out.get('Message', '') and
          len(doc.elements) == 3 and S.W.transactions == [] and Engine.calls == 0, (out.get('Message'), Engine.calls))
    doc = fresh('mass', mass_category=False)
    out, ns = run_code(code, IN(i26=True), engine_dir)
    check('WRITE in a family that is not Mass -> ERROR, nothing created, engine not started',
          out.get('Status') == 'ERROR' and 'Mass kategorisinde değil' in out.get('Message', '') and len(doc.elements) == 3 and Engine.calls == 0, out.get('Message'))
    # 3 dry run in a Mass document -----------------------------------------------------------------------------------------
    doc = fresh('mass')
    out, ns = run_code(code, IN(), engine_dir)
    d = out['data']
    check('dry run in a Mass document: target ok, no previous result, nothing created', d['target_document']['ok'] is True and d['existing_result'] == {'found': False} and
          len(doc.elements) == 3 and S.W.transactions == [] and out.get('status') == 'dry-run', (d['target_document'], d['existing_result']))
    # 4 WRITE in a Mass document ---------------------------------------------------------------------------------------------
    doc = fresh('mass')
    foreign = S.Foreign()
    doc.add(foreign)
    out, ns = run_code(code, IN(i26=True), engine_dir)
    d = out.get('data', {})
    w = d.get('written', {})
    sel = d.get('selection', {})
    check('WRITE status Written', out.get('status') == 'written', out.get('Message') or out.get('Status'))
    check('points == subset nodes, forms == subset triangles, curves == 3 x forms (DynamoOption1V7 method)',
          len(doc.points()) == sel['reference_points'] == w['reference_points'] and len(doc.forms()) == sel['forms'] == w['forms'] and
          len(doc.curves()) == 3 * sel['forms'] == w['curve_by_points'], (len(doc.points()), len(doc.forms()), len(doc.curves())))
    check('every edge curve is a reference line; every Form built from 3 curves', all(c.IsReferenceLine for c in doc.curves()) and all(len(f.depends) == 3 for f in doc.forms()))
    check('ONE transaction committed, none left open', S.W.commits == 1 and S.W.transactions == ['MashProject9 triangle Forms: GAUSS_KABUK_02'] and doc.open_tx is None)
    check('foreign element untouched', foreign.Id.Value in doc.elements)
    names = [s.Name for s in doc.storages()]
    check('ownership record: only DataStorage names <= 180 chars with allowed characters', len(names) == w['record_chunks'] > 0 and all(NAME_RE.match(n) for n in names), (len(names), names[:1]))
    rec = ns['decode_registry'](names, 'GAUSS_KABUK_02')
    owned = set(ns['delta_decode'](rec['owned']))
    created = {e.Id.Value for e in doc.points() + doc.helper_points() + doc.curves() + doc.forms()}
    check('Revit helper points: exactly one per Form, reported (843 + 1,499 style), and part of the ownership record',
          len(doc.helper_points()) == len(doc.forms()) == w['helper_reference_points'] and w['reference_points_added_in_document'] == len(doc.points()) + len(doc.forms()) and
          {h.Id.Value for h in doc.helper_points()} <= owned, (w['helper_reference_points'], len(doc.helper_points())))
    check('record round-trips: owned ids == every created element incl. helper points (and no storage / foreign element)', owned == created and foreign.Id.Value not in owned, (len(owned), len(created)))
    check('record stores the selection (mode, seed, radius)', rec.get('selection', {}).get('mode') == 'automatic seed' and 'seed_triangle' in rec['selection'], rec.get('selection'))
    check('record keeps forms in triangle order + panel/half/flags per triangle',
          ns['delta_decode'](rec['forms']) == json.load(open(os.path.join(work, 'MashProject9_v11_triangle_map.json'), encoding='utf-8'))['form_element_ids'] and
          len(rec['panel']) == len(rec['half']) == len(rec['flags']) == sel['forms'] and set(rec['half']) <= set('ab-') and set(rec['flags']) <= set('.RUB'))
    mf = json.load(open(os.path.join(work, 'MashProject9_v11_triangle_map.json'), encoding='utf-8'))
    check('map file after WRITE: form_element_ids parallel to subset, point ids parallel to nodes', len(mf['form_element_ids']) == len(mf['subset']) == sel['forms'] and
          len(mf['point_element_ids']) == len(mf['point_node_ids']) == sel['reference_points'])
    print('   WRITE: %d points, %d curves, %d Forms, %d record chunks' % (len(doc.points()), len(doc.curves()), len(doc.forms()), len(names)))
    first_forms = {f.Id.Value for f in doc.forms()}
    # 5 re-run = REBUILD of exactly the previous result --------------------------------------------------------------------------
    out, ns = run_code(code, IN(i26=True), engine_dir)
    w2 = out['data']['written']
    check('re-run replaces the previous result: replaced == previous elements (incl. helper points), exactly one new set, foreign element kept, one record',
          out.get('status') == 'written' and w2['replaced_previous_elements'] == len(created) and len(doc.forms()) == sel['forms'] and
          not (first_forms & {f.Id.Value for f in doc.forms()}) and foreign.Id.Value in doc.elements and
          ns['decode_registry']([s.Name for s in doc.storages()], 'GAUSS_KABUK_02')['version'] == 9 and len(doc.storages()) == w2['record_chunks'],
          (w2['replaced_previous_elements'], len(created)))
    check('dry run now reports the previous result', run_code(code, IN(), engine_dir)[0]['data']['existing_result'].get('found') is True)
    # OLD record format (the first run in Family4: no 'selection' key, x-sorted strip): rewrite the stored record that way, then re-run
    old_rec = ns['decode_registry']([s_.Name for s_ in doc.storages()], 'GAUSS_KABUK_02')
    old_rec.pop('selection', None)
    old_names = ns['encode_registry'](old_rec)
    for s_ in doc.storages():
        doc.elements.pop(s_.Id.Value)
    for nm in old_names:
        st = S.Storage(doc)
        st._name = nm
        doc.add(st)
    check('(test setup) old-format record stored in %d chunks' % len(old_names), len(doc.storages()) == len(old_names) > 0)
    before_elems = len(doc.elements)
    out_old, ns = run_code(code, IN(i26=True), engine_dir)
    check('REBUILD reads a record WITHOUT the selection key (as written by the first run) and replaces its result',
          out_old.get('status') == 'written' and out_old['data']['written']['replaced_previous_elements'] > 0 and out_old['data']['existing_result']['found'] is True and
          len(doc.forms()) == out_old['data']['written']['forms'], (out_old.get('Message'), out_old.get('status')))
    out, ns = run_code(code, IN(i26=True, i51=600), engine_dir)
    check('re-run with another Max triangles rebuilds with the new size only', len(doc.forms()) <= 600 and len(doc.forms()) >= 598 and out['data']['written']['forms'] == len(doc.forms()), len(doc.forms()))
    other = run_code(code, IN(i26=True, i18='OTHER_KEY', i51=100), engine_dir)[0]
    check('another Model key creates its own result and leaves the first one alone', other.get('status') == 'written' and len(doc.storages()) > 0 and
          any(n.startswith(ns['registry_prefix']('GAUSS_KABUK_02')) for n in [s.Name for s in doc.storages()]) and
          any(n.startswith(ns['registry_prefix']('OTHER_KEY')) for n in [s.Name for s in doc.storages()]))
    # 6 dependents of the previous result that are NOT in the record -------------------------------------------------------------------
    #   6a: Revit-internal elements (no category, hidden from collectors) = what stopped the first real re-run in Family4 (283 elements that are not part of it)
    doc = fresh('mass')
    run_code(code, IN(i26=True, i51=300), engine_dir)
    pts = doc.points()
    hidden = [S.SketchPlane(pts[i % len(pts)]) for i in range(283)]
    for h in hidden:
        doc.add(h)
    dry, ns = run_code(code, IN(i51=300), engine_dir)
    rc = dry['data']['existing_result']['replace_check']
    check('dry run FORECASTS the replacement: 283 internal dependents, none blocking, document unchanged by the probe',
          rc['dependents'] == 283 and rc['blocking'] == 0 and 'SketchPlane | no category' in rc['by_kind'] and 'engel yok' in rc['verdict'] and all(h.Id.Value in doc.elements for h in hidden) and doc.open_tx is None, rc)
    out, ns = run_code(code, IN(i26=True, i51=300), engine_dir)
    wr = out.get('data', {}).get('written', {})
    check('REBUILD with 283 hidden internal dependents (the real Family4 failure) -> Written, dependents removed and reported by kind',
          out.get('status') == 'written' and wr.get('replaced_dependents_by_kind', {}).get('SketchPlane | no category') == 283 and not any(h.Id.Value in doc.elements for h in hidden), (out.get('Message'), wr.get('replaced_dependents_by_kind')))
    #   6b: the USER's element (a dimension) depends on a point -> blocked, rolled back, listed
    doc = fresh('mass')
    run_code(code, IN(i26=True, i51=300), engine_dir)
    before = set(doc.elements)
    dep = S.Foreign(depends_on=doc.points()[0])
    doc.add(dep)
    before.add(dep.Id.Value)
    dry, ns = run_code(code, IN(i51=300), engine_dir)
    rc = dry['data']['existing_result']['replace_check']
    check('dry run says BLOCKED (a Dimension depends on a point) and warns', rc['blocking'] == 1 and 'ENGEL' in rc['verdict'] and any('senin elemanını' in w for w in dry['data']['warnings']), rc)
    out, ns = run_code(code, IN(i26=True, i51=300), engine_dir)
    check('WRITE with a user dependent -> ERROR naming the class, rolled back, previous result and the dimension intact, diagnostics in the result',
          out.get('Status') == 'ERROR' and 'Foreign' in out.get('Message', '') and 'YOUR work' in out.get('Message', '') and set(doc.elements) == before and
          out['data']['diagnostics']['replace_blocked']['not_allowed'] == 1, (out.get('Message'),))
    #   6c: a Form of the user on one of our points also blocks
    doc = fresh('mass')
    run_code(code, IN(i26=True, i51=300), engine_dir)
    uf = S.Foreign(depends_on=doc.points()[0], category=(S.OST_MASS_FORM, 'Form'))
    doc.add(uf)
    out, ns = run_code(code, IN(i26=True, i51=300), engine_dir)
    check('a Form of the user that sits on one of our points blocks the replacement', out.get('Status') == 'ERROR' and uf.Id.Value in doc.elements, out.get('Message'))
    # 7 failure mid-way ------------------------------------------------------------------------------------------------------------
    doc = fresh('mass')
    S.W.fail_form_at = 50
    out, ns = run_code(code, IN(i26=True), engine_dir)
    check('NewFormByCap failure on a first write -> ERROR, rollback, document empty again (no points, no storages)',
          out.get('Status') == 'ERROR' and S.W.rollbacks == 1 and doc.points() == [] and doc.forms() == [] and doc.storages() == [] and doc.open_tx is None,
          (out.get('Message'), S.W.rollbacks))
    doc = fresh('mass')
    run_code(code, IN(i26=True, i51=300), engine_dir)
    snap = set(doc.elements)
    S.W.fail_form_at = 50
    S.W.rollbacks = 0
    out, ns = run_code(code, IN(i26=True, i51=300), engine_dir)
    check('failure while REBUILDING keeps the previous result (all its elements back)', out.get('Status') == 'ERROR' and set(doc.elements) == snap, (out.get('Message')))
    doc = fresh('mass')
    S.W.fail_form_all_reference = True
    out, ns = run_code(code, IN(i26=True, i51=300), engine_dir)
    wr = out.get('data', {}).get('written', {})
    check('reference-line-only profile rejected -> retry with one visible edge succeeds for every triangle',
          out.get('status') == 'written' and wr.get('visible_edge_fallbacks') == wr.get('forms') and sum(1 for c in doc.curves() if not c.IsReferenceLine) == wr.get('forms'), (out.get('Message'), wr.get('visible_edge_fallbacks')))
    # 8 whole lattice -----------------------------------------------------------------------------------------------------------------
    doc = fresh('mass')
    out, ns = run_code(code, IN(), engine_dir) if False else run_code(code, IN(i51=0), engine_dir)
    d = out['data']
    sel = d['selection']
    check('Max triangles 0 = whole lattice: 15,482 Forms, 7,889 points, 46,446 curves; long-run warning + estimate',
          sel['whole_lattice'] and sel['forms'] == 15482 and sel['reference_points'] == 7889 and sel['curve_by_points'] == 46446 and
          d['estimate']['minutes'] > 300 and ' sa' in d['estimate']['text'] and any('tahmini' in w and 'KARESİYLE' in w for w in d['warnings']) and 'gün' in ns['duration_text'](ns['estimate_seconds'](73833)) and
          ns['estimate_seconds'](73833, 'high') > 3 * 86400, (sel, d['estimate'], ns['duration_text'](ns['estimate_seconds'](73833))))
    doc = fresh('mass')
    out, ns = run_code(code, IN(i26=True, i51=0), engine_dir)
    wr = out['data']['written']
    check('WRITE of the whole lattice (stub): 15,482 Forms / 7,889 points / 46,446 curves, record chunks stay moderate',
          out.get('status') == 'written' and len(doc.forms()) == 15482 and len(doc.points()) == 7889 and len(doc.curves()) == 46446 and wr['record_chunks'] < 800, (out.get('Message'), wr.get('record_chunks')))
    print('   full set record chunks:', wr.get('record_chunks'))
    # 9 inputs / errors ---------------------------------------------------------------------------------------------------------------
    fresh('mass')
    out, ns = run_code(code, IN(i51=10), engine_dir)
    check('Max triangles 10 -> clamped to 50 with a warning (never an error)', out.get('status') == 'dry-run' and any('Max triangles' in x for x in out['data'].get('input_warnings', [])) and
          out['data']['selection']['triangles'] <= 50, out['data'].get('input_warnings'))
    out, ns = run_code(code, IN(i51=99999), engine_dir)
    check('Max triangles above the total -> whole lattice, no error', out.get('status') == 'dry-run' and out['data']['selection']['whole_lattice'])
    out, ns = run_code(code, IN(), engine_dir, report_patch={'vertices': rep['vertices'] + 1})
    check('lattice != engine report -> ERROR (nothing written)', out.get('Status') == 'ERROR' and 'differs from the engine report' in out.get('Message', ''), out.get('Message'))
    out, ns = run_code(code, IN(), engine_dir, bad_version=True)
    check('wrong engine version -> ERROR', out.get('Status') == 'ERROR', out.get('Message'))
    out, ns = run_code(code, IN(i20=0.0), engine_dir)
    check('panel edge 0 -> ERROR', out.get('Status') == 'ERROR', out.get('Message'))
    # 10 L 2.75 + timeout (dry run and WRITE) --------------------------------------------------------------------------------------
    doc = fresh('mass')
    cap = {}
    out, ns = run_code(code, IN(i20=2.75), engine_dir, captured=cap)
    check('L 2.75 accepted in the DRY RUN: PANEL_EDGE 2.75 sent to the engine, engine timeout >= 3600 s', out.get('status') == 'dry-run' and cap['settings']['PANEL_EDGE'] == 2.75 and (cap['timeout'] or 0) >= 3600, (out.get('Message'), cap.get('timeout')))
    doc = fresh('mass')
    cap = {}
    out, ns = run_code(code, IN(i20=2.75, i26=True, i51=300), engine_dir, captured=cap)
    check('L 2.75 accepted in WRITE as well (PANEL_EDGE 2.75, timeout >= 3600 s)', out.get('status') == 'written' and cap['settings']['PANEL_EDGE'] == 2.75 and (cap['timeout'] or 0) >= 3600, (out.get('Message'), cap.get('timeout')))
    check('ENGINE_TIMEOUT_S constant >= 3600', ns['ENGINE_TIMEOUT_S'] >= 3600, ns['ENGINE_TIMEOUT_S'])
    # 11 Commit every N Forms (TransactionGroup) ----------------------------------------------------------------------------------------
    doc = fresh('mass')
    base_out, ns = run_code(code, IN(i26=True, i51=600), engine_dir)
    bw = base_out['data']['written']
    check('default (N 0): ONE transaction, no group, same names as before', bw['transactions'] == 1 and bw['transaction_group'] is False and bw['write_options'] == {'commit_every': 0, 'commit_every_requested': 0, 'share_edge_curves': False} and
          S.W.commits == 1 and S.W.group_assimilated == 0 and not any(t.startswith('GROUP') for t in S.W.transactions), (bw['transactions'], S.W.transactions))
    base_counts = (len(doc.points()), len(doc.curves()), len(doc.forms()), len(doc.helper_points()))
    doc = fresh('mass')
    out, ns = run_code(code, IN(i26=True, i51=600, i54=250), engine_dir)
    w = out['data']['written']
    counts = (len(doc.points()), len(doc.curves()), len(doc.forms()), len(doc.helper_points()))
    check('N 250 over 600 Forms: ONE group, 3 transactions (2 chunk commits + final), group merged, same counts as the single transaction',
          out.get('status') == 'written' and w['transaction_group'] is True and w['transactions'] == 3 and len(w['chunk_commit_seconds']) == 2 and S.W.commits == 3 and S.W.group_assimilated == 1 and
          S.W.group_rollbacks == 0 and counts == base_counts and w['write_options']['commit_every'] == 250, (w['transactions'], counts, base_counts))
    names = [s_.Name for s_ in doc.storages()]
    rec = ns['decode_registry'](names, 'GAUSS_KABUK_02')
    created = {e.Id.Value for e in doc.points() + doc.helper_points() + doc.curves() + doc.forms()}
    check('N 250: the ownership record is complete (owned == every created element of ALL chunks, incl. helper points)', set(ns['delta_decode'](rec['owned'])) == created and len(doc.storages()) > 0, len(created))
    prog = open(os.path.join(work, 'MashProject9_v11_progress.txt'), encoding='utf-8').read()
    check('progress file (every 250 Forms): commit mode + chunk commits, last-250 seconds, per-call cumulative seconds', prog.count('commit mode: every 250 Forms') == 2 and 'last 250:' in prog and 'calls cumulative s: curve' in prog and 'reference' in prog and 'form' in prog, prog[-400:])
    check('result json: call_seconds (4 calls) + progress_series (2 rows with the call timers) + chunk commits', set(w['call_seconds']) == {'NewReferencePoint', 'NewCurveByPoints', 'Reference', 'NewFormByCap'} and len(w['progress_series']) == 2 and
          'NewFormByCap_s' in w['progress_series'][0] and w['progress_series'][1]['commit_chunks'] == 1 and w['progress_series'][0]['commit_chunks'] == 0, w['progress_series'][:1])
    # N larger than the triangle count: single transaction, with a warning in the dry run
    doc = fresh('mass')
    out, ns = run_code(code, IN(i26=True, i51=300, i54=500), engine_dir)
    check('N >= number of Forms: single transaction (no group) and the report says so', out['data']['written']['transaction_group'] is False and out['data']['written']['transactions'] == 1 and any('tek transaction' in x for x in out['data']['warnings']), out['data']['warnings'])
    out, ns = run_code(code, IN(i51=300, i54=20), engine_dir)
    check('N 20 (below the slider minimum 50) -> clamped to 50 with a warning, never an error', out.get('status') == 'dry-run' and any('Commit every N' in x for x in out['data'].get('input_warnings', [])), out['data'].get('input_warnings'))
    # REBUILD over a previous result with chunked commits
    doc = fresh('mass')
    run_code(code, IN(i26=True, i51=300), engine_dir)
    foreign = S.Foreign()
    doc.add(foreign)
    out, ns = run_code(code, IN(i26=True, i51=600, i54=250), engine_dir)
    w = out['data']['written']
    check('chunked write REBUILDS the previous (single-transaction) result: replaced, one record set, foreign element kept, group merged',
          out.get('status') == 'written' and w['replaced_previous_elements'] > 0 and len(doc.forms()) == w['forms'] and foreign.Id.Value in doc.elements and len(doc.storages()) == w['record_chunks'] and S.W.group_rollbacks == 0, (out.get('Message'), w['replaced_previous_elements']))
    # failure inside a LATER chunk: the WHOLE group (earlier committed chunks + the replace of the previous result) is rolled back
    doc = fresh('mass')
    run_code(code, IN(i26=True, i51=300), engine_dir)
    snap = set(doc.elements)
    prev_names = sorted(s_.Name for s_ in doc.storages())
    S.W.fail_form_at = doc._fc.form_calls + 400          # the 400th Form of THIS run = inside the second chunk
    S.W.rollbacks = S.W.group_rollbacks = 0
    out, ns = run_code(code, IN(i26=True, i51=600, i54=250), engine_dir)
    check('N 250: failure at Form ~400 (second chunk) -> ERROR, the group is rolled back (previous result and record intact, nothing leaked)',
          out.get('Status') == 'ERROR' and S.W.group_rollbacks == 1 and set(doc.elements) == snap and sorted(s_.Name for s_ in doc.storages()) == prev_names and doc.open_tx is None and doc.open_group is None and
          'whole transaction group was rolled back' in out.get('Message', ''), (out.get('Message'), S.W.group_rollbacks))
    # failure in the very first chunk of an empty document
    doc = fresh('mass')
    S.W.fail_form_at = 50
    out, ns = run_code(code, IN(i26=True, i51=600, i54=250), engine_dir)
    check('N 250: failure in the first chunk on an empty document -> empty again, group rolled back', out.get('Status') == 'ERROR' and S.W.group_rollbacks == 1 and doc.points() == [] and doc.forms() == [] and doc.storages() == [] and doc.open_group is None, out.get('Message'))
    # Revit rolls back a CHUNK commit by itself (e.g. a failure message): the earlier chunks must go too
    doc = fresh('mass')
    S.W.commit_fail_at = 2
    out, ns = run_code(code, IN(i26=True, i51=600, i54=250), engine_dir)
    check('a chunk commit that Revit refuses (2nd commit) -> ERROR + the earlier committed chunk is rolled back with the group', out.get('Status') == 'ERROR' and S.W.group_rollbacks == 1 and doc.points() == [] and doc.forms() == [] and doc.storages() == [], (out.get('Message'), S.W.group_rollbacks))
    # the FINAL commit (the one that also carries the ownership record) is refused: nothing may remain, no record either
    doc = fresh('mass')
    S.W.commit_fail_at = 3
    out, ns = run_code(code, IN(i26=True, i51=600, i54=250), engine_dir)
    check('the final commit (with the record) refused by Revit -> ERROR, group rolled back: no points, no Forms, no record', out.get('Status') == 'ERROR' and S.W.group_rollbacks == 1 and doc.points() == [] and doc.forms() == [] and doc.storages() == [] and doc.curves() == [], (out.get('Message'), S.W.group_rollbacks))
    # dry run never starts a group
    doc = fresh('mass')
    out, ns = run_code(code, IN(i51=600, i54=250), engine_dir)
    check('dry run with N 250: no transaction, no group, nothing created', out.get('status') == 'dry-run' and S.W.transactions == [] and len(doc.elements) == 3 and out['data']['write_options']['commit_every'] == 250, S.W.transactions)
    # 12 Share edge curves ------------------------------------------------------------------------------------------------------------
    doc = fresh('mass')
    dry, ns = run_code(code, IN(i51=600, i55=True), engine_dir)
    sel = dry['data']['selection']
    check('dry run with sharing: curve_by_points = unique lattice edges (< 3 x Forms), the V7 count and both numbers are reported', sel['curve_by_points'] == sel['curve_by_points_if_shared'] < sel['curve_by_points_v7_method'] == 3 * sel['forms'], sel)
    doc = fresh('mass')
    out, ns = run_code(code, IN(i26=True, i51=600, i55=True), engine_dir)
    w = out['data']['written']
    uses = {}
    for f in doc.forms():
        for c in f.depends:
            uses[c.Id.Value] = uses.get(c.Id.Value, 0) + 1
    check('share True: curves == unique edges, every Form has 3 curves, no curve is used by more than 2 Forms, reused edges == 3 x Forms - curves, no fallback',
          out.get('status') == 'written' and len(doc.curves()) == sel['curve_by_points'] == w['curve_by_points'] and all(len(f.depends) == 3 for f in doc.forms()) and max(uses.values()) <= 2 and
          w['share_edge_curves']['edges_reused'] == 3 * w['forms'] - w['curve_by_points'] and w['share_edge_curves']['fallback_triangles'] == 0 and w['share_edge_curves']['unique_edges'] == w['curve_by_points'] and w['write_options']['share_edge_curves'] is True,
          (len(doc.curves()), sel['curve_by_points'], w['share_edge_curves']))
    names = [s_.Name for s_ in doc.storages()]
    rec = ns['decode_registry'](names, 'GAUSS_KABUK_02')
    check('share True: the ownership record still covers every created element (curves, points, helpers, Forms)', set(ns['delta_decode'](rec['owned'])) == {e.Id.Value for e in doc.points() + doc.helper_points() + doc.curves() + doc.forms()})
    prog = open(os.path.join(work, 'MashProject9_v11_progress.txt'), encoding='utf-8').read()
    check('progress file mentions the shared-edge counters', 'shared edges reused' in prog and 'fallbacks 0' in prog, prog[-300:])
    # Revit refuses a shared reference: per-triangle fallback to the V7 method, counted, every Form still created
    doc = fresh('mass')
    S.W.reject_shared = True
    out, ns = run_code(code, IN(i26=True, i51=600, i55=True), engine_dir)
    w = out['data']['written']
    check('Revit rejects shared curves -> every rejected triangle falls back to its own curves (counted), all Forms created, every Form has 3 curves',
          out.get('status') == 'written' and w['forms'] >= 599 and len(doc.forms()) == w['forms'] and all(len(f.depends) == 3 for f in doc.forms()), (out.get('Message'), w.get('forms')))
    check('fallback numbers: fallback_triangles > 0, curves between the unique-edge count and 3 x Forms, no Form shares a curve with another Form',
          w['share_edge_curves']['fallback_triangles'] > 0 and sel['curve_by_points'] < len(doc.curves()) <= 3 * w['forms'] and
          all(sum(1 for f2 in doc.forms() for c2 in f2.depends if c2 is c) == 1 for f in doc.forms()[:50] for c in f.depends), (w['share_edge_curves'], len(doc.curves())))
    # sharing + chunked commits together
    doc = fresh('mass')
    out, ns = run_code(code, IN(i26=True, i51=600, i55=True, i54=250), engine_dir)
    w = out['data']['written']
    check('share True + commit every 250 together: 3 transactions, curves == unique edges, group merged', out.get('status') == 'written' and w['transactions'] == 3 and w['curve_by_points'] == sel['curve_by_points'] and S.W.group_assimilated == 1, (w['transactions'], w['curve_by_points']))
    # 13 engine result cache -----------------------------------------------------------------------------------------------------------
    tmp = tempfile.mkdtemp(prefix='mp9cache_')
    pkg = os.path.join(tmp, 'pkg')
    os.makedirs(os.path.join(pkg, 'Engine'))
    fp, exe = os.path.join(pkg, 'Footprint.stl'), os.path.join(pkg, 'Engine', 'MashEngine.exe')
    open(fp, 'wb').write(b'footprint-A')
    open(exe, 'wb').write(b'exe-A')
    os.utime(exe, (1700000000, 1700000000))
    cdir = os.path.join(work, 'MashProject9_v11_engine_cache')

    def CIN(**kw):
        v = IN(**kw)
        v[0], v[1] = fp, exe
        return v
    doc = fresh('mass')
    out, ns = run_code(code, CIN(), engine_dir)
    ec = out['data']['engine_cache']
    check('cache: the first run (reuse False) runs the engine once and SAVES the cache (panel file, report, meta)', Engine.calls == 1 and ec['used'] is False and ec['saved'] is True and os.path.isfile(os.path.join(cdir, 'cache.json')) and
          os.path.isfile(os.path.join(cdir, 'BAKLAVA_PANELS.bkl')) and os.path.isfile(os.path.join(cdir, 'engine_report.json')), ec)
    tri_first = out['data']['lattice']['triangles']
    out, ns = run_code(code, CIN(i56=True), engine_dir)
    ec = out['data']['engine_cache']
    check('cache: reuse True + identical settings/STL/exe -> the engine is SKIPPED, same lattice, result says so', Engine.calls == 1 and ec['used'] is True and 'SKIPPED' in ec['reason'] and out['data']['lattice']['triangles'] == tri_first and
          out.get('status') == 'dry-run' and ec.get('engine_seconds_skipped') is not None, ec)
    out, ns = run_code(code, CIN(i56=False), engine_dir)
    check('cache: reuse False always runs the engine (default behaviour unchanged)', Engine.calls == 2 and out['data']['engine_cache']['used'] is False, Engine.calls)
    out, ns = run_code(code, CIN(i56=True, i2=23.0), engine_dir)
    ec = out['data']['engine_cache']
    check('cache: a CHANGED slider (bridge section height) -> mismatch, the engine runs again and the cache is replaced', Engine.calls == 3 and ec['used'] is False and 'changed' in ec['reason'] and ec['saved'] is True, ec)
    out, ns = run_code(code, CIN(i56=True, i2=23.0), engine_dir)
    check('cache: the same changed value again -> hit', Engine.calls == 3 and out['data']['engine_cache']['used'] is True)
    out, ns = run_code(code, CIN(i56=True, i2=23.0, i20=2.75), engine_dir)
    check('cache: panel edge L changed (6 -> 2.75) -> mismatch, engine runs', Engine.calls == 4 and out['data']['engine_cache']['used'] is False)
    out, ns = run_code(code, CIN(i56=True, i2=23.0, i20=2.75), engine_dir)
    check('cache: L 2.75 again -> hit', Engine.calls == 4 and out['data']['engine_cache']['used'] is True)
    open(fp, 'wb').write(b'footprint-B')
    out, ns = run_code(code, CIN(i56=True, i2=23.0, i20=2.75), engine_dir)
    check('cache: the Footprint STL content changed -> mismatch, engine runs', Engine.calls == 5 and out['data']['engine_cache']['used'] is False)
    os.utime(exe, (1700009999, 1700009999))
    out, ns = run_code(code, CIN(i56=True, i2=23.0, i20=2.75), engine_dir)
    check('cache: MashEngine.exe replaced (mtime) -> mismatch, engine runs', Engine.calls == 6 and out['data']['engine_cache']['used'] is False)
    with open(os.path.join(cdir, 'BAKLAVA_PANELS.bkl'), 'r+b') as fh:
        fh.seek(100)
        fh.write(b'\xff\xff\xff\xff')
    out, ns = run_code(code, CIN(i56=True, i2=23.0, i20=2.75), engine_dir)
    check('cache: a damaged cached panel file is detected (hash) -> the engine runs again', Engine.calls == 7 and out['data']['engine_cache']['used'] is False and out['data']['engine_cache']['saved'] is True, out['data']['engine_cache'])
    doc = fresh('mass')
    out, ns = run_code(code, CIN(i56=True, i26=True, i51=300), engine_dir)
    cal = Engine.calls
    out2, ns = run_code(code, CIN(i56=True, i26=True, i51=300), engine_dir)
    check('cache: also works in WRITE mode (first run builds, second run skips the engine and REBUILDS the Forms)', cal == 1 and Engine.calls == 1 and out2.get('status') == 'written' and out2['data']['engine_cache']['used'] is True and out2['data']['written']['replaced_previous_elements'] > 0, (cal, Engine.calls))
    doc = fresh('mass')
    out, ns = run_code(code, CIN(i56=True, i28='C:/does/not/exist'), engine_dir)
    check('cache: unusable result folder -> falls back to the package folder (cache there), no error', out.get('status') == 'dry-run' and Engine.calls == 1 and out['data']['engine_cache'].get('dir') == os.path.join(pkg, 'MashProject9_v11_engine_cache'), out['data']['engine_cache'])
    shutil.rmtree(tmp, ignore_errors=True)
    if engine_gap:
        out, ns = run_code(code, IN(), engine_gap)
        check('panel file written with gap 0.1 (corners not shared) -> ERROR that names the gap', out.get('Status') == 'ERROR' and 'panel gap must be 0' in out.get('Message', ''), out.get('Message'))
    shutil.rmtree(work, ignore_errors=True)
    print('ALL PASS' if not fails else 'FAILED: ' + ', '.join(fails))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
