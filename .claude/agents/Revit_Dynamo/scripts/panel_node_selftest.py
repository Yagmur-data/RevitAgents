#!/usr/bin/env python3
"""panel_node_selftest.py - offline logic test of the MashProject6 Dynamo Python node (ForDynamo/baklava-panels/
MashProject7_v6.py): stubs clr / Autodesk.Revit.DB / RevitServices / System, fakes the engine subprocess with a REAL engine
output folder (BAKLAVA_PANELS.bkl + baklava_report.json from MashProject6/run_panels.py) and checks dry run, write,
idempotent re-run, grouping, shell toggle, rollback and the error path.

  python panel_node_selftest.py NODE.py ENGINE_OUTPUT_DIR [OLDER_ENGINE_OUTPUT_DIR]   (3rd arg: also test a re-run whose panel count CHANGED)

Proves the node's algorithm, counts, keys and JSON shape only. It does NOT prove pythonnet, Revit's TessellatedShapeBuilder,
DirectShape.SetShape, Material.Create or Dynamo transactions - those stay unverified until a real Dynamo run.
"""
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import types

F2M = 0.3048


# ------------------------------------------------------------ fake Revit API
class XYZ(object):
    def __init__(self, x, y, z):
        self.X, self.Y, self.Z = x, y, z

    @staticmethod
    def IsWithinLengthLimits(p):
        return True


class ElementIdC(object):
    InvalidElementId = None

    def __init__(self, v):
        self.Value = v

    def __str__(self):
        return str(self.Value)


ElementIdC.InvalidElementId = ElementIdC(-1)


class GeometryObject(object):
    pass


class MeshC(GeometryObject):
    def __init__(self, n):
        self.NumTriangles = n


class TessellatedFace(object):
    def __init__(self, pts, mat):
        self.pts, self.mat = pts, mat


class TSB(object):
    Fail_at = None

    def __init__(self):
        self.n = 0
        self.sets = 0
        self.Target = self.Fallback = None

    def OpenConnectedFaceSet(self, solid):
        self.sets += 1

    def CloseConnectedFaceSet(self):
        pass

    def DoesFaceHaveEnoughLoopsAndVertices(self, f):
        return len(f.pts) == 3

    def AddFace(self, f):
        self.n += 1

    def Build(self):
        pass

    def GetBuildResult(self):
        n = self.n
        return types.SimpleNamespace(GetGeometricalObjects=lambda: [MeshC(n)])


class World(object):
    def __init__(self):
        self.elements = []
        self.materials = {}
        self.deleted = 0
        self.rollbacks = 0
        self.commits = 0
        self.next_id = 1000
        self.create_fail_at = None


W = World()


class FakeEl(object):
    def __init__(self, cat):
        W.next_id += 1
        self.Id = ElementIdC(W.next_id)
        self.ApplicationId = self.ApplicationDataId = self.Name = None
        self.shape_tris = None
        self.params = {}
        self.cat = cat

    def SetShape(self, geo):
        self.shape_tris = sum(g.NumTriangles for g in geo)

    def get_Parameter(self, bip):
        el = self

        class P(object):
            IsReadOnly = False

            def Set(self_, text):
                el.params[bip] = text
        return P()


class DirectShapeC(object):
    @staticmethod
    def CreateElement(doc, cat):
        if W.create_fail_at is not None and len([e for e in W.elements if e.ApplicationId]) >= W.create_fail_at:
            raise RuntimeError('simulated Revit failure')
        el = FakeEl(cat)
        W.elements.append(el)
        return el


class Collector(object):
    def __init__(self, doc):
        self.kind = None

    def OfClass(self, cls):
        if cls is DirectShapeC:
            return list(W.elements)
        return list(W.materials.values())


class MaterialC(object):
    def __init__(self, name):
        self.Name = name
        self.Id = ElementIdC(len(W.materials) + 1)
        self.Color = None
        self.Transparency = 0

    @staticmethod
    def Create(doc, name):
        m = MaterialC(name)
        W.materials[name] = m
        return m.Id


class Sub(object):
    def __init__(self, doc):
        self.started = False

    def Start(self):
        self.started = True
        self.snap = list(W.elements)         # a real rollback restores the state at Start (created elements vanish, deleted ones come back)

    def HasStarted(self):
        return self.started

    def Commit(self):
        W.commits += 1
        self.started = False

    def RollBack(self):
        W.rollbacks += 1
        self.started = False
        W.elements[:] = list(getattr(self, 'snap', []))


def build_stubs():
    m = {}
    clr = types.ModuleType('clr')
    clr.AddReference = lambda n: None
    m['clr'] = clr
    db = types.ModuleType('Autodesk.Revit.DB')
    db.XYZ, db.ElementId, db.DirectShape = XYZ, ElementIdC, DirectShapeC
    db.BuiltInCategory = types.SimpleNamespace(OST_GenericModel='OST_GenericModel')
    db.BuiltInParameter = types.SimpleNamespace(ALL_MODEL_MARK='MARK', ALL_MODEL_INSTANCE_COMMENTS='COMMENTS')
    db.FilteredElementCollector = Collector
    db.TessellatedShapeBuilder = TSB
    db.TessellatedShapeBuilderTarget = types.SimpleNamespace(Mesh='Mesh')
    db.TessellatedShapeBuilderFallback = types.SimpleNamespace(Salvage='Salvage')
    db.TessellatedFace = TessellatedFace
    db.UnitUtils = types.SimpleNamespace(ConvertToInternalUnits=lambda v, u: v / F2M)
    db.UnitTypeId = types.SimpleNamespace(Meters='m')
    db.Mesh, db.SubTransaction, db.GeometryObject = MeshC, Sub, GeometryObject
    db.Material, db.Color = MaterialC, lambda r, g, b: (r, g, b)
    for name in ('Autodesk', 'Autodesk.Revit'):
        m[name] = types.ModuleType(name)
    m['Autodesk.Revit.DB'] = db
    rs = types.ModuleType('RevitServices')
    rp = types.ModuleType('RevitServices.Persistence')
    rt = types.ModuleType('RevitServices.Transactions')
    doc = types.SimpleNamespace(Title='Fake', IsFamilyDocument=False)
    doc.GetElement = lambda eid: [x for x in W.materials.values() if x.Id is eid][0]

    def delete(eid):
        W.elements[:] = [e for e in W.elements if e.Id is not eid]
        W.deleted += 1
    doc.Delete = delete
    rp.DocumentManager = types.SimpleNamespace(Instance=types.SimpleNamespace(CurrentDBDocument=doc))
    rt.TransactionManager = types.SimpleNamespace(Instance=types.SimpleNamespace(
        EnsureInTransaction=lambda d: None, TransactionTaskDone=lambda: None))
    m['RevitServices'], m['RevitServices.Persistence'], m['RevitServices.Transactions'] = rs, rp, rt
    sysm = types.ModuleType('System')

    class _Arr(object):
        def __class_getitem__(cls, t):
            return lambda items: list(items)
    sysm.Array = _Arr
    m['System'] = sysm
    return m


def tiny_stl(path):
    tris = [((0, 0, 0), (1, 0, 0), (0, 1, 0)), ((1, 0, 0), (1, 1, 0), (0, 1, 0))]
    with open(path, 'wb') as f:
        f.write(b'\0' * 80)
        f.write(struct.pack('<I', len(tris)))
        for t in tris:
            f.write(struct.pack('<12fH', 0, 0, 1, *t[0], *t[1], *t[2], 0))


LAST_SETTINGS = {}
LAST_NS = {}
LAST_CMD = []


def run_node(code, IN, engine_dir, report_patch=None, bad_version=False):
    stubs = build_stubs()
    saved = {k: sys.modules.get(k) for k in stubs}
    sys.modules.update(stubs)
    real_run = subprocess.run
    rep = json.load(open(os.path.join(engine_dir, 'baklava_report.json')))
    if report_patch:
        rep.update(report_patch)

    def fake_run(cmd, **kw):
        out_dir = cmd[cmd.index('--output-dir') + 1]
        LAST_CMD[:] = list(cmd)
        try:
            LAST_SETTINGS.clear()
            LAST_SETTINGS.update(json.load(open(cmd[cmd.index('--settings') + 1])))
        except Exception:
            pass
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
    LAST_NS['ns'] = ns
    return ns['OUT']


def main():
    node, engine_dir = sys.argv[1], sys.argv[2]
    code = open(node, encoding='utf-8').read()
    work = tempfile.mkdtemp(prefix='nodetest_')
    fp = os.path.join(work, 'Footprint.stl')
    ex = os.path.join(work, 'MashEngine.exe')
    _orig = os.environ.get('FP_ORIGINAL') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'MashProject8', 'Footprint.stl')
    if os.path.isfile(_orig):
        shutil.copy(_orig, fp)           # a real (known, old H) footprint: passes the node unchanged
    else:
        open(fp, 'wb').write(b'x')
    open(ex, 'wb').write(b'x')
    rep = json.load(open(os.path.join(engine_dir, 'baklava_report.json')))
    nr, nt = rep['rhombus_panels'], rep['triangle_panels']
    ntri_expected = nr * 32 + nt * 16          # n=4 -> 2*n*n per rhombus, n*n per triangle
    def IN(write=False, shell=False, group=1, edge=6.0, folder=None, cap=None, footprint=None, key=None, oldkey=None, section=None, narrow=None, switch=None, clip=None):
        v = [footprint or fp, ex] + [None] * 30
        if key is not None:
            v[18] = key
        if 'prepare_footprint' in code:
            v[3] = 0.0                      # v14: Bridge Width 0 = automatic (corridor width of the footprint)
        v[20], v[21], v[22], v[23], v[24], v[25], v[26], v[27], v[28] = edge, 4, 0.1, 0.05, 0, group, write, shell, folder or work
        v[29], v[30] = True, 3.0
        if len(v) > 31:
            v[31] = True
        if 'IN[45]' in code or 'arg(45' in code:          # MashProject7 graph: section/taper/spine/variation inputs 32..45
            v += [3.0, 3.0, 2.0, 25.0, 60.0, 0.0, 0.0, 12.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
            if 'arg(49' in code:                              # MashProject8 graph: bridge foot inputs 46..48
                v += [100.0, 0.0, 0.0]
                if 'arg(49' in code:
                    v += [0.35, 1.0]
                    if (cap is not None or oldkey is not None) and 'arg(51' in code:     # MashProject8_v12 (V4): input 51 = left outer cap depth
                        v += [35.0 if cap is None else cap]
                        if oldkey is not None and 'arg(52' in code:                      # MashProject8_v13 (V5): input 52 = old model key to delete
                            v += [oldkey]
        if 'arg(53' in code:                                                              # MashProject8_v15 (V6): 2 section height (0 = circle), 19 transition switch, 49 narrowing (0), 53 end clip switch
            while len(v) < 54:
                v.append(None)
            v[2] = 0.0 if section is None else section
            v[19] = 100.0 if switch is None else switch
            v[49] = 0.0 if narrow is None else narrow
            v[53] = True if clip is None else clip
        return v
    fails = []

    def check(name, cond, info=''):
        print(('PASS ' if cond else 'FAIL ') + name + ('  ' + str(info) if info else ''))
        if not cond:
            fails.append(name)

    # 1 dry run
    W.__init__()
    out = run_node(code, IN(write=False), engine_dir)
    d = out.get('data', {})
    check('dry-run status', out.get('status') == 'dry-run', out.get('Status'))
    check('dry-run wrote nothing', len(W.elements) == 0 and W.commits == 0 and not W.materials)
    check('dry-run counts', d.get('panel_counts', {}).get('revit_elements') == nr + nt, d.get('panel_counts'))
    check('dry-run geometry test covers every panel', d.get('geometry_test', {}).get('triangles') == ntri_expected,
          (d.get('geometry_test', {}).get('triangles'), ntri_expected))
    check('dry-run plan', d.get('plan', {}).get('would_create') == nr + nt and d['plan']['shell_element'] == 'not touched')
    check('result json written', os.path.isfile(os.path.join(work, re.search(r"GRAPH = '([^']+)'", code).group(1) + '_result.json')))
    # 2 write
    W.__init__()
    out = run_node(code, IN(write=True), engine_dir)
    d = out.get('data', {})
    keys = [e.ApplicationDataId for e in W.elements]
    check('write status', out.get('status') == 'written', out.get('Status') or d)
    check('write created all', d.get('written', {}).get('created') == nr + nt and len(W.elements) == nr + nt, len(W.elements))
    check('keys unique + format', len(set(keys)) == len(keys) and keys[0] == 'BAKLAVA_GAUSS_KABUK_02_00001', keys[:1])
    check('app id', all(e.ApplicationId == 'Dynamo.Baklava.Panel' for e in W.elements))
    check('triangles per element', sum(e.shape_tris for e in W.elements) == ntri_expected)
    check('materials created', set(W.materials) == {'BAKLAVA_Rhombus', 'BAKLAVA_Triangle'})
    check('mark/comments set', W.elements[0].params.get('MARK') == 'BKL-00001' and 'BAKLAVA' in W.elements[0].params.get('COMMENTS', ''))
    check('shell untouched by default', 'shell' not in d)
    first_ids = [e.Id.Value for e in W.elements]
    # 3 idempotent re-run
    out = run_node(code, IN(write=True), engine_dir)
    d = out.get('data', {})
    check('re-run updates, creates nothing', d.get('written', {}).get('created') == 0 and d['written']['updated'] == nr + nt
          and len(W.elements) == nr + nt, d.get('written'))
    check('re-run keeps element ids', [e.Id.Value for e in W.elements] == first_ids)
    # 4 grouped re-run deletes the surplus keys of the same model key
    out = run_node(code, IN(write=True, group=25), engine_dir)
    d = out.get('data', {})
    groups = d.get('panel_counts', {}).get('revit_elements')
    check('grouping reduces elements', groups is not None and groups < (nr + nt) / 5, groups)
    check('surplus panels deleted, total == groups', len(W.elements) == groups and d.get('written', {}).get('deleted') == nr + nt - groups,
          (len(W.elements), d.get('written')))
    check('grouped triangles preserved', sum(e.shape_tris for e in W.elements) == ntri_expected)
    # 5 shell toggle
    W.__init__()
    out = run_node(code, IN(write=True, shell=True), engine_dir)
    d = out.get('data', {})
    shell = [e for e in W.elements if e.ApplicationId == 'Dynamo.STL.GaussShell']
    check('shell created only with both toggles', len(shell) == 1 and d.get('shell', {}).get('action') == 'created', d.get('shell'))
    # 6 errors / rollback
    W.__init__()
    out = run_node(code, IN(write=True), engine_dir, bad_version=True)
    check('wrong engine version -> ERROR, model untouched', out.get('Status') == 'ERROR' and len(W.elements) == 0, out.get('Message'))
    W.__init__()
    W.create_fail_at = 100
    out = run_node(code, IN(write=True), engine_dir)
    check('failure mid-write -> rollback, no elements', out.get('Status') == 'ERROR' and W.rollbacks == 1 and len(W.elements) == 0,
          (out.get('Message'), W.rollbacks, len(W.elements)))
    W.__init__()
    out = run_node(code, IN(write=False, edge=1.0), engine_dir)
    check('edge < 2 m refused', out.get('Status') == 'ERROR', out.get('Message'))
    # 6b slider values outside the engine range must be CLAMPED with a warning, never an error (V8 fix: blend length 60, panel size 1.0)
    if 'arg(49' in code:
        W.__init__()
        v = IN(write=False)
        v[-5] = 60.0                      # bridge foot blend length (accepted: 0 or 80..140)
        out = run_node(code, v, engine_dir)
        ws = out.get('data', {}).get('input_warnings', [])
        check('slider out of range -> clamped + warning, no error', out.get('status') == 'dry-run' and any('blend length' in w for w in ws), (out.get('Status'), ws))
        W.__init__()
        v = IN(write=False)
        v[40] = 1.0                       # panel size at bridge centre 1.0 m (accepted 0 or 2..60)
        out = run_node(code, v, engine_dir)
        ws = out.get('data', {}).get('input_warnings', [])
        check('panel size 1.0 -> clamped to 2 + warning', out.get('status') == 'dry-run' and any('bridge centre' in w for w in ws), (out.get('Status'), ws))
    # 6c V4 (graph MashProject8_v12): cap depth input 51 + footprint pairing warnings (never errors)
    if 'arg(51' in code:
        orig_fp = os.environ.get('V4_FOOTPRINT_ORIGINAL', '')
        v4_fp = os.environ.get('V4_FOOTPRINT_V4', '')
        W.__init__()
        out = run_node(code, IN(write=False), engine_dir)
        m_ = re.search(r"^SOL_C_DERINLIGI = ([0-9.]+)", code, re.M)
        dflt = float(m_.group(1)) if m_ else 35.09           # v14: IN[51] = 0 / absent = automatic: 24 for the original old footprint (the fake footprint here)
        check('V4: IN[51] absent -> the node default cap depth (%.2f) reaches the engine' % dflt, abs(LAST_SETTINGS.get('SOL_C_DERINLIGI', 0) - dflt) < 1e-9, LAST_SETTINGS.get('SOL_C_DERINLIGI'))
        out = run_node(code, IN(write=False, cap=24.0), engine_dir)
        check('V4: cap depth 24 (old shape) is sent as 24', LAST_SETTINGS.get('SOL_C_DERINLIGI') == 24.0 and out.get('status') == 'dry-run', LAST_SETTINGS.get('SOL_C_DERINLIGI'))
        out = run_node(code, IN(write=False, cap=3.0), engine_dir)
        ws = out.get('data', {}).get('input_warnings', [])
        check('V4: cap depth 3 -> clamped to 5 + warning, no error', LAST_SETTINGS.get('SOL_C_DERINLIGI') == 5.0 and any('cap depth' in w for w in ws) and out.get('status') == 'dry-run', (LAST_SETTINGS.get('SOL_C_DERINLIGI'), ws))
        out = run_node(code, IN(write=False, cap=500.0), engine_dir)
        check('V4: cap depth 500 -> clamped to 80', LAST_SETTINGS.get('SOL_C_DERINLIGI') == 80.0)
        d = out.get('data', {})
        blk = d.get('v5') or d.get('v4')
        check('V4/V5: result carries the footprint block with the variant', isinstance(blk, dict) and 'variant' in blk and blk.get('cap_depth_m') == 80.0, blk)
        if os.path.isfile(orig_fp) and os.path.isfile(v4_fp):
            out = run_node(code, IN(write=False, cap=35.09, footprint=orig_fp), engine_dir)
            ws = out.get('data', {}).get('input_warnings', [])
            check('V4: ORIGINAL footprint + cap 35.09 -> warning (not an error)', out.get('status') == 'dry-run' and any('ORIGINAL' in w for w in ws), ws)
            check('V4: footprint variant reported as original', (out['data'].get('v5') or out['data'].get('v4'))['variant'].startswith('original'), (out['data'].get('v5') or out['data'].get('v4')))
            out = run_node(code, IN(write=False, cap=24.0, footprint=v4_fp), engine_dir)
            ws = out.get('data', {}).get('input_warnings', [])
            check('V4: V4 footprint + cap 24 -> warning (not an error)', out.get('status') == 'dry-run' and any('V4 one' in w for w in ws), ws)
            out = run_node(code, IN(write=False, cap=35.09, footprint=v4_fp), engine_dir)
            ws = out.get('data', {}).get('input_warnings', [])
            check('V4: V4 footprint + cap 35.09 -> no footprint warning', not any('Footprint' in w for w in ws) and (out['data'].get('v5') or out['data'].get('v4'))['variant'].startswith('V4'), (ws, (out['data'].get('v5') or out['data'].get('v4'))))
        else:
            print('SKIP footprint pairing tests (set V4_FOOTPRINT_ORIGINAL / V4_FOOTPRINT_V4 to the two footprint files)')
    # 6d V5/V5b (graphs MashProject8_v13 / v14): footprint adapter. v14 = the user selects his OWN raw STL and the node derives + maps back.
    if 'prepare_footprint' in code or 'load_adapter' in code:
        usr = os.environ.get('V5_USER_STL', '')
        legacy = os.environ.get('V5_LEGACY_DIR', '')
        ad_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'footprint_adapter.py')
        if os.path.isfile(usr) and 'prepare_footprint' in code:
            import importlib.util
            spec = importlib.util.spec_from_file_location('footprint_adapter_t', ad_py)
            FA = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(FA)
            # kit-block guard: the adapter text inside the node is the text of footprint_adapter.py
            mk0, mk1 = '# ==== FOOTPRINT ADAPTER BEGIN ====', '# ==== FOOTPRINT ADAPTER END ===='
            t_node = code[code.index(mk0):code.index(mk1)]
            t_file = open(ad_py, encoding='utf-8').read()
            t_file = t_file[t_file.index(mk0):t_file.index(mk1)]
            check('V5b: adapter block in the node == footprint_adapter.py (kit-block guard)', t_node.replace('\r\n', '\n') == t_file.replace('\r\n', '\n'))
            raw = os.path.join(work, 'Footprint_261014.stl')
            shutil.copy(usr, raw)
            res_dir = os.path.join(work, 'res')
            os.makedirs(res_dir)
            W.__init__()
            out = run_node(code, IN(write=False, folder=res_dir, footprint=raw, cap=0.0), engine_dir)
            d = out.get('data', {})
            efp = LAST_CMD[LAST_CMD.index('--footprint') + 1]
            ref_dir = os.path.join(work, 'ref')
            ref_stl, ref_info = FA.derive(raw, ref_dir)
            import hashlib as _h
            md = lambda q: _h.md5(open(q, 'rb').read()).hexdigest()      # noqa: E731
            d0_counts = d.get('panel_counts', {}).get('revit_elements', nr + nt)       # v15: the slanted-end clip removes panels, the written count is the clipped count
            check('V5b: raw STL selected -> dry run succeeds with no warnings', out.get('status') == 'dry-run' and not d.get('input_warnings'), (out.get('Status'), d.get('input_warnings'), out.get('Message')))
            check('V5b: the footprint sent to the engine is the DERIVED file under <result>/_engine_footprint (not the raw STL)', os.path.basename(os.path.dirname(efp)) == '_engine_footprint' and efp != raw, efp)
            check('V5b: derived file == footprint_adapter output / make_footprint_v5 (md5)', md(efp) == md(ref_stl), (md(efp), md(ref_stl)))
            side = json.load(open(os.path.splitext(efp)[0] + '.adapter.json'))
            check('V5b: runtime adapter record written next to it and equal to the reference record', side.get('engine_stl_md5') == md(efp) and side.get('map') == ref_info.get('map') and side.get('source_md5') == md(raw), side.get('map'))
            check('V5b: automatic values reach the engine (cap = arm width + 24 over 2, bridge width = corridor, cut distance, foot offset, bridge feet default)',
                  abs(LAST_SETTINGS['SOL_C_DERINLIGI'] - ref_info['cap_depth_m']) < 1e-9 and abs(LAST_SETTINGS['KOPRU_GENISLIGI'] - ref_info['corridor_width_m']) < 1e-9 and
                  abs(LAST_SETTINGS['UC_KESIM_PAYI'] - ref_info['uc_kesim_payi']) < 1e-9 and abs(LAST_SETTINGS['BRIDGE_FOOT_HEIGHT_L'] - 0.2) < 1e-9 and abs(LAST_SETTINGS['BRIDGE_FOOT_HEIGHT_R'] - 0.05) < 1e-9,
                  {k: LAST_SETTINGS.get(k) for k in ('SOL_C_DERINLIGI', 'KOPRU_GENISLIGI', 'UC_KESIM_PAYI', 'BRIDGE_FOOT_HEIGHT_L', 'BRIDGE_FOOT_HEIGHT_R')})
            rawb = open(os.path.join(engine_dir, 'BAKLAVA_PANELS.bkl'), 'rb').read()
            fl = struct.unpack_from('<%df' % ((len(rawb) - 20) // 4), rawb, 20)
            mm = ref_info['map']
            ux, uy, uz = [], [], []
            for k in range(0, len(fl), 3):
                u_, v_ = fl[k] - mm[4], fl[k + 1] - mm[5]
                ux.append(mm[0] * u_ + mm[2] * v_)
                uy.append(mm[1] * u_ + mm[3] * v_)
                uz.append(fl[k + 2])
            b_ = d.get('panel_bounds_m', {})
            check('V5b: panels come back in Als own frame (bounds = the engine panels through the inverse of the derived map)',
                  abs(b_['min'][0] - min(ux)) < 1e-3 and abs(b_['max'][0] - max(ux)) < 1e-3 and abs(b_['min'][1] - min(uy)) < 1e-3 and abs(b_['max'][1] - max(uy)) < 1e-3, (b_, (min(ux), max(ux), min(uy), max(uy))))
            check('V5b: v5 block says derived at run time + names the source', 'derived at run time' in d.get('v5', {}).get('variant', '') and d['v5'].get('source') == 'Footprint_261014.stl', d.get('v5', {}).get('variant'))
            f2 = LAST_NS['ns']['to_user_frame']
            pts = [(0.0, 0.0), (100.0, 0.0), (0.0, 100.0), (123.4, 250.5)]
            back = [FA.apply_map(mm, *f2(x, y)) for x, y in pts]
            check('V5b: forward / inverse round trip of the frame map', all(abs(b2[0] - p2[0]) < 1e-6 and abs(b2[1] - p2[1]) < 1e-6 for b2, p2 in zip(back, pts)), back)
            a0, a1, a2 = f2(*pts[0]), f2(*pts[1]), f2(*pts[2])
            det = (a1[0] - a0[0]) * (a2[1] - a0[1]) - (a1[1] - a0[1]) * (a2[0] - a0[0])
            check('V5b: the map is a pure rotation (det +1, no scaling)', abs(det - 100.0 * 100.0) < 1e-6, det)
            out = run_node(code, IN(write=False, folder=res_dir, footprint=raw, cap=24.0), engine_dir)
            ws = out.get('data', {}).get('input_warnings', [])
            check('V5b: explicit cap depth different from the derived one -> warning, not an error', out.get('status') == 'dry-run' and any('differs from' in w for w in ws), ws)
            # the original old footprint passes unchanged
            W.__init__()
            run_node(code, IN(write=False, folder=res_dir), engine_dir)
            check('V5b: the known old footprint reaches the engine unchanged and cap 0 = 24', LAST_CMD[LAST_CMD.index('--footprint') + 1] == fp and abs(LAST_SETTINGS['SOL_C_DERINLIGI'] - 24.0) < 1e-9, LAST_SETTINGS.get('SOL_C_DERINLIGI'))
            # a footprint that does not fit the I layout stops with the measures; garbage stops with a clear message
            rect = os.path.join(work, 'rect.stl')
            FA.write_engine_stl(rect, [(0.0, 0.0), (300.0, 0.0), (300.0, 100.0), (0.0, 100.0)], 'rectangle')
            W.__init__()
            out = run_node(code, IN(write=False, folder=res_dir, footprint=rect), engine_dir)
            check('V5b: a rectangle is refused with the measures (nothing written)', out.get('Status') == 'ERROR' and 'does not fit the I layout' in str(out.get('Message')) and 'bbox' in str(out.get('Message')) and len(W.elements) == 0, out.get('Message'))
            junk = os.path.join(work, 'junk.stl')
            open(junk, 'wb').write(b'not an stl')
            out = run_node(code, IN(write=False, folder=res_dir, footprint=junk), engine_dir)
            check('V5b: a file that is not an STL stops with a clear message', out.get('Status') == 'ERROR' and 'STL' in str(out.get('Message')), out.get('Message'))
            n_exp = d0_counts if 'd0_counts' in dir() else nr + nt
            # old set deletion / panel sets / plan summary
            W.__init__()
            out = run_node(code, IN(write=True, folder=res_dir, footprint=raw, key='SET_A'), engine_dir)
            n_a = len(W.elements)
            check('V5b: set A written from the raw STL', out.get('status') == 'written' and n_a == n_exp, n_a)
            out = run_node(code, IN(write=False, folder=res_dir, footprint=raw, key='SET_B', oldkey='SET_A'), engine_dir)
            d = out.get('data', {})
            check('V5b: dry run reports old set / new count / create / delete and deletes nothing', d['plan']['old_set']['elements'] == n_a and d['plan']['would_create'] == n_exp and len(W.elements) == n_a and 'SET_A' in d['plan']['summary'], d.get('plan'))
            check('V5b: panel sets in the document are listed', d.get('panel_sets_in_document') == {'SET_A': n_a}, d.get('panel_sets_in_document'))
            out = run_node(code, IN(write=True, folder=res_dir, footprint=raw, key='SET_B', oldkey='SET_A'), engine_dir)
            d = out.get('data', {})
            check('V5b: write creates set B and deletes set A in the same run', d.get('written', {}).get('old_set_deleted') == n_a and len(W.elements) == n_exp and all(e.ApplicationDataId.startswith('BAKLAVA_SET_B_') for e in W.elements), d.get('written'))
            out = run_node(code, IN(write=True, folder=res_dir, footprint=raw, key='SET_B', oldkey='SET_B'), engine_dir)
            ws = out.get('data', {}).get('input_warnings', [])
            check('V5b: old key equal to the key is ignored with a warning', len(W.elements) == n_exp and any('Old model key equals' in w for w in ws), ws)
            W.__init__()
            run_node(code, IN(write=True, folder=res_dir, footprint=raw, key='SET_A'), engine_dir)
            W.create_fail_at = 100
            out = run_node(code, IN(write=True, folder=res_dir, footprint=raw, key='SET_B', oldkey='SET_A'), engine_dir)
            check('V5b: failure while writing set B -> rollback, the old set A is NOT deleted', out.get('Status') == 'ERROR' and len([e for e in W.elements if e.ApplicationDataId.startswith('BAKLAVA_SET_A_')]) == n_exp, (out.get('Message'), len(W.elements)))
            # the file derived by the v13 package (Footprint.stl + Footprint.adapter.json) still works when selected
            if os.path.isfile(os.path.join(legacy, 'Footprint.stl')) and os.path.isfile(os.path.join(legacy, 'Footprint.adapter.json')):
                lg = os.path.join(work, 'Footprint.stl')
                shutil.copy(os.path.join(legacy, 'Footprint.stl'), lg)
                shutil.copy(os.path.join(legacy, 'Footprint.adapter.json'), os.path.join(work, 'Footprint.adapter.json'))
                W.__init__()
                out = run_node(code, IN(write=False, folder=res_dir, footprint=lg, cap=35.0), engine_dir)
                d = out.get('data', {})
                lside = json.load(open(os.path.join(work, 'Footprint.adapter.json')))
                lm = [0.0, -1.0, 1.0, 0.0, lside['ymax'] + lside['dx'], -lside['xmin'] + lside['dy']]
                ux = [lm[0] * (fl[k] - lm[4]) + lm[2] * (fl[k + 1] - lm[5]) for k in range(0, len(fl), 3)]
                check('V5b: the derived v13 package Footprint.stl (adapter sidecar) is accepted unchanged (backward compatible), frame mapped back',
                      out.get('status') == 'dry-run' and LAST_CMD[LAST_CMD.index('--footprint') + 1] == lg and abs(d['panel_bounds_m']['min'][0] - min(ux)) < 1e-3, (out.get('Status'), d.get('input_warnings')))
            else:
                print('SKIP legacy sidecar test (set V5_LEGACY_DIR to the folder with the v13 Footprint.stl + Footprint.adapter.json)')
        else:
            print('SKIP V5b tests (set V5_USER_STL to Footprint_261014.stl; V5_LEGACY_DIR optional)')
    # 6e V6 (graph MashProject8_v15): slanted wing ends by panel clipping, circular bridge section, foot narrowing 0, transition switch. Needs the engine output of the V6 package (ENGINE_OUTPUT_DIR = a v15 capture).
    if 'arg(53' in code:
        usr = os.environ.get('V5_USER_STL', '')
        if os.path.isfile(usr):
            import importlib.util
            sd = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, sd)
            pcm = importlib.util.spec_from_file_location('panel_clip_t', os.path.join(sd, 'panel_clip.py'))
            PCT = importlib.util.module_from_spec(pcm)
            pcm.loader.exec_module(PCT)
            ck0, ck1 = '# ==== PANEL CLIP BEGIN ====', '# ==== PANEL CLIP END ===='
            t_node = code[code.index(ck0):code.index(ck1)]
            t_file = open(os.path.join(sd, 'panel_clip.py'), encoding='utf-8').read()
            t_file = t_file[t_file.index(ck0):t_file.index(ck1)]
            check('V6: panel clip block in the node == panel_clip.py (kit-block guard)', t_node.replace('\r\n', '\n') == t_file.replace('\r\n', '\n'))
            raw6 = os.path.join(work, 'Footprint_261014.stl')
            if not os.path.isfile(raw6):
                shutil.copy(usr, raw6)
            res6 = os.path.join(work, 'res6')
            os.makedirs(res6, exist_ok=True)
            W.__init__()
            out = run_node(code, IN(write=False, folder=res6, footprint=raw6, cap=0.0), engine_dir)
            d = out.get('data', {})
            ec = d.get('ends_clip', {})
            check('V6: dry run with the raw STL: status ok, no warnings, clip ON', out.get('status') == 'dry-run' and not d.get('input_warnings') and d.get('v6', {}).get('thin_wing_end_clip') == 'ON', (out.get('Status'), d.get('input_warnings'), out.get('Message')))
            check('V6: slanted-end clip acted on both ends (partial >= 10, removed >= 10)', ec.get('partial', 0) >= 10 and ec.get('removed', 0) >= 10 and ec.get('lines') == 2, ec)
            check('V6: panel_counts.revit_elements = engine panels - removed, panels_after_end_clip agrees', d['panel_counts']['revit_elements'] == nr + nt - ec['removed'] and d['panel_counts']['panels_after_end_clip'] == nr + nt - ec['removed'], d.get('panel_counts'))
            # expected triangle count: untouched panels 32 / 16, clipped panels = number of kept sub-triangles
            ad6 = json.load(open(os.path.splitext(LAST_CMD[LAST_CMD.index('--footprint') + 1])[0] + '.adapter.json'))
            import mp8v6_previews3 as P36
            n6, pan6, tabs6, st6 = P36.user_panels(os.path.join(engine_dir, 'BAKLAVA_PANELS.bkl'), os.path.splitext(LAST_CMD[LAST_CMD.index('--footprint') + 1])[0] + '.adapter.json', clip=True)
            exp_tris = sum((len(tabs6[k]) if k < 2 else len(v) // 9) for k, v in pan6)
            check('V6: geometry test builds exactly the clipped triangle set', d.get('geometry_test', {}).get('triangles') == exp_tris and not d.get('geometry_test', {}).get('failures'), (d.get('geometry_test', {}).get('triangles'), exp_tris))
            check('V6: node clip statistics == the standalone clip of the same panels', st6['partial'] == ec['partial'] and st6['removed'] == ec['removed'] and st6['panels_out'] == ec['panels_out'], (st6, ec))
            check('V6: circular section by default (Bridge Section Height 0): height = width = corridor 27 m, exponent 2', abs(LAST_SETTINGS['KOPRU_YUKSEKLIGI'] - 27.0) < 1e-9 and abs(LAST_SETTINGS['KOPRU_GENISLIGI'] - 27.0) < 1e-9 and d['v6']['bridge_section'].startswith('circle'), d['v6']['bridge_section'])
            check('V6: foot narrowing default 0, transition switch on, real length 100, shell cut 0.6 m beyond the wing ends (UC = 10)', LAST_SETTINGS['BRIDGE_FOOT_NARROW'] == 0.0 and LAST_SETTINGS['GECIS_UZUNLUGU'] == 100.0 and abs(LAST_SETTINGS['UC_KESIM_PAYI'] - 10.0) < 1e-9 and d['v6']['underside_transition_real_length_m'] == 100.0,
                  {k: LAST_SETTINGS.get(k) for k in ('BRIDGE_FOOT_NARROW', 'GECIS_UZUNLUGU', 'UC_KESIM_PAYI')})
            # section height explicit -> kept, 'not a circle' says so
            out = run_node(code, IN(write=False, folder=res6, footprint=raw6, cap=0.0, section=22.0), engine_dir)
            d2 = out.get('data', {})
            check('V6: Bridge Section Height 22 is kept and reported as NOT a circle', abs(LAST_SETTINGS['KOPRU_YUKSEKLIGI'] - 22.0) < 1e-9 and d2['v6']['bridge_section'].startswith('NOT a circle'), d2['v6']['bridge_section'])
            out = run_node(code, IN(write=False, folder=res6, footprint=raw6, cap=0.0, section=-1.0), engine_dir)
            check('V6: negative Bridge Section Height is refused with a clear message', out.get('Status') == 'ERROR' and 'must be positive' in str(out.get('Message')), out.get('Message'))
            out = run_node(code, IN(write=False, folder=res6, footprint=raw6, cap=0.0, narrow=0.35), engine_dir)
            ws = out.get('data', {}).get('input_warnings', [])
            check('V6: foot narrowing 0.35 -> warning that names the price (about 4.7 m)', out.get('status') == 'dry-run' and any('pulls the corridor edges inward' in w and '4.7' in w for w in ws), ws)
            out = run_node(code, IN(write=False, folder=res6, footprint=raw6, cap=0.0, switch=0.0), engine_dir)
            d3 = out.get('data', {})
            check('V6: transition switch 0 -> the data block says OFF (whole block incl. feet) and the engine gets 0', LAST_SETTINGS['GECIS_UZUNLUGU'] == 0.0 and d3['v6']['underside_transition_switch'].startswith('OFF') and d3['v6']['underside_transition_real_length_m'] == 0.0, d3['v6'])
            out = run_node(code, IN(write=False, folder=res6, footprint=raw6, cap=0.0, clip=False), engine_dir)
            d4 = out.get('data', {})
            ws = d4.get('input_warnings', [])
            check('V6: clip OFF -> panels untouched (count = engine count), warning about the overshoot', d4['panel_counts']['revit_elements'] == nr + nt and d4['ends_clip'].get('switch', '').startswith('OFF') and any('clipping' in w.lower() and 'OFF' in w for w in ws), (d4.get('panel_counts'), ws))
            W.__init__()
            out = run_node(code, IN(write=True, folder=res6, footprint=raw6, cap=0.0, key='SET_V6'), engine_dir)
            check('V6: WRITE creates one element per clipped panel set entry and its triangles match', out.get('status') == 'written' and len(W.elements) == nr + nt - ec['removed'] and sum(e.shape_tris for e in W.elements) == exp_tris,
                  (out.get('Status'), len(W.elements), sum(e.shape_tris for e in W.elements), exp_tris))
            out = run_node(code, IN(write=True, folder=res6, footprint=raw6, cap=0.0, key='SET_V6'), engine_dir)
            check('V6: re-run is idempotent (same count, updates in place)', len(W.elements) == nr + nt - ec['removed'] and out.get('data', {}).get('written', {}).get('created') == 0, out.get('data', {}).get('written'))
        else:
            print('SKIP V6 tests (set V5_USER_STL to Footprint_261014.stl and pass a v15 engine capture as ENGINE_OUTPUT_DIR)')
    # 7 CHANGED panel count on re-run (older run in OTHER_ENGINE_DIR, newer run in ENGINE_DIR): in-place update + surplus delete / extra create
    if len(sys.argv) > 3:
        other = sys.argv[3]
        orep = json.load(open(os.path.join(other, 'baklava_report.json')))
        n_old, n_new = orep['panels_total'], rep['panels_total']
        W.__init__()
        run_node(code, IN(write=True), other)
        ids_old = [e.Id.Value for e in W.elements]
        check('older run created %d panels' % n_old, len(W.elements) == n_old, len(W.elements))
        out = run_node(code, IN(write=True), engine_dir)
        d = out.get('data', {})
        w = d.get('written', {})
        keys = sorted(e.ApplicationDataId for e in W.elements)
        exp_keys = sorted('BAKLAVA_GAUSS_KABUK_02_%05d' % (i + 1) for i in range(n_new))
        check('changed count: updated=min, created=max(0,new-old), deleted=max(0,old-new)',
              w.get('updated') == min(n_old, n_new) and w.get('created') == max(0, n_new - n_old) and w.get('deleted') == max(0, n_old - n_new), (n_old, n_new, w))
        check('changed count: element total == new count, keys 00001..N', len(W.elements) == n_new and keys == exp_keys)
        check('changed count: surviving elements keep their ids', set(e.Id.Value for e in W.elements if e.Id.Value in ids_old) == set(ids_old[:min(n_old, n_new)]))
        check('changed count: triangle count of new geometry', sum(e.shape_tris for e in W.elements) == rep['rhombus_panels'] * 32 + rep['triangle_panels'] * 16)
        print('   old run %d panels -> new run %d panels: %s' % (n_old, n_new, w))
    shutil.rmtree(work, ignore_errors=True)
    print('ALL PASS' if not fails else 'FAILED: ' + ', '.join(fails))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
