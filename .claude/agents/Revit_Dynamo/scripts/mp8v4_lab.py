#!/usr/bin/env python3
"""mp8v4_lab.py - offline lab driver for the MashProject8 engine family (shell STL, optional panels). No Revit, no Dynamo.

  python mp8v4_lab.py run NAME [--engine DIR] [--graph FILE.dyn] [--out ROOT] [--panels L] [IDX=VAL ...] [KEY=VAL ...]

  IDX=VAL   overrides graph input IN[IDX] (integer key, e.g. 32=2.0 = Mouth section exponent)
  KEY=VAL   overrides an engine setting directly (e.g. SOL_C_DERINLIGI=30, BRIDGE_FOOT_FOLLOW_ARM=0)
  --engine  folder holding Engine_Source.py + baklava_panels.py + Footprint.stl (default: MashProject8)
  --graph   graph whose SAVED slider values are used (default MashProject8/MashProject8_v10.dyn)
  --footprint FILE  footprint STL to use instead of <engine>/Footprint.stl
  --exe FILE        run the frozen MashEngine.exe instead of <engine>/Engine_Source.py (cwd = the exe folder)
  --panels  panel edge L in metres (default: 0 = shell only, about 40 s)
  --out     output root (default $MP8V4_OUT or the scratchpad); files: ROOT/NAME/{settings.json, AYARLANABILIR_GAUSS_KABUK.stl, log.txt}

The slider -> engine-setting mapping is a copy of `generate()` in ForDynamo/baklava-panels/MashProject8_v10.py (checked against the
shell triangle count of a real Dynamo run). Prints the engine's last line (version, triangles).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, HERE)
from graph_inputs import graph_inputs  # noqa: E402

DEFAULT_OUT = os.environ.get('MP8V4_OUT') or os.path.join(os.environ.get('TEMP', '.'), 'mp8v4')

BASE = {  # constants of the node (not sliders)
    'SOL_DIS_KENARI_KAPAT': True, 'SOL_C_DERINLIGI': 24.0,
    'Dx_SOL_UST': 1.0, 'Dy_SOL_UST': 3.0, 'Q_SOL_UST': 8.6, 'G_SOL_UST': 0.8,
    'Dx_KOPRU_UST': 3.0, 'Dy_KOPRU_UST': 5.0, 'Q_KOPRU_UST': 8.6, 'G_KOPRU_UST': 0.8,
    'Dx_SAG_UST': 1.0, 'Dy_SAG_UST': 3.0, 'Q_SAG_UST': 8.6, 'G_SAG_UST': 0.8,
    'Dx_SOL_ALT': 1.0, 'Dy_SOL_ALT': 3.0, 'Q_SOL_ALT': -8.6, 'G_SOL_ALT': 0.8,
    'Dx_KOPRU_ALT': 3.0, 'Dy_KOPRU_ALT': 5.0, 'Q_KOPRU_ALT': 2.5, 'G_KOPRU_ALT': 0.8,
    'Dx_SAG_ALT': 1.0, 'Dy_SAG_ALT': 3.0, 'Q_SAG_ALT': -8.6, 'G_SAG_ALT': 0.8,
}


def settings_from_inputs(IN):
    def arg(i, d):
        return IN[i] if len(IN) > i and IN[i] is not None else d
    s = dict(BASE)
    s.update({
        'h': float(arg(8, 1.0)), 'SOL_C_PARCA_SAYISI': int(round(float(arg(9, 104)))),
        'GAUSS_X_UST': float(arg(10, 200.0)), 'GAUSS_Y_UST': float(arg(11, 250.0)),
        'SIGMA_X_UST': float(arg(12, 105.0)), 'SIGMA_Y_UST': float(arg(13, 85.0)),
        'GAUSS_X_ALT': float(arg(14, 200.0)), 'GAUSS_Y_ALT': float(arg(15, 250.0)),
        'SIGMA_X_ALT': float(arg(16, 105.0)), 'SIGMA_Y_ALT': float(arg(17, 85.0)),
        'KOPRU_YUKSEKLIGI': float(arg(2, 18.0)), 'KOPRU_GENISLIGI': float(arg(3, 30.545975490214516)),
        'TEPE_UST': float(arg(4, 18.0)), 'TEPE_ALT': float(arg(4, 18.0)),
        'SOL_C_ACIKLIGI': float(arg(5, 44.0)), 'SAG_C_ACIKLIGI': float(arg(6, 44.0)),
        'KOSE_YUVARLATMA_YARICAPI': float(arg(7, 30.0)), 'GECIS_UZUNLUGU': float(arg(19, 100.0)),
        'PANEL_EDGE': float(arg(20, 0.0)), 'PANEL_SUBDIV': int(arg(21, 4)), 'PANEL_GAP': float(arg(22, 0.0)),
        'PANEL_OFFSET': float(arg(23, 0.05)), 'PANEL_FAMILY': int(arg(24, 0)),
        'PANEL_FIELD': bool(arg(29, True)), 'PANEL_FILL_ZONE': float(arg(30, 3.0)),
        'PANEL_ALIGN_MIN': 10.0 if bool(arg(31, True)) else 0.0,
        'ARM_SECTION_EXP': float(arg(32, 3.0)), 'CAP_SECTION_EXP': float(arg(33, 3.0)),
        'BRIDGE_SECTION_EXP': float(arg(34, 2.0)), 'ARM_SECTION_WIDTH': float(arg(35, 25.0)),
        'END_TAPER_LENGTH': float(arg(36, 60.0)), 'END_TAPER_STRENGTH': float(arg(37, 0.0)),
        'SPINE_HEIGHT': float(arg(38, 0.0)), 'SPINE_WIDTH': float(arg(39, 12.0)),
        'PANEL_SIZE_BRIDGE': float(arg(40, 0.0)), 'PANEL_SIZE_PIER': float(arg(41, 0.0)), 'PANEL_SIZE_TIP': float(arg(42, 0.0)),
        'PANEL_VAR_STRENGTH': float(arg(43, 1.0)), 'PANEL_ELONG_BRIDGE': float(arg(44, 1.0)), 'PANEL_ELONG_PIER': float(arg(45, 1.0)),
        'BRIDGE_FOOT_LEN': float(arg(46, 100.0)), 'BRIDGE_FOOT_HEIGHT_L': float(arg(47, 0.0)), 'BRIDGE_FOOT_HEIGHT_R': float(arg(48, 0.0)),
        'BRIDGE_FOOT_NARROW': float(arg(49, 0.35)), 'BRIDGE_FOOT_FOLLOW_ARM': 1.0 if float(arg(50, 1.0)) >= 0.5 else 0.0,
        'SOL_C_DERINLIGI': float(arg(51, 24.0)),      # IN[51] exists only in the V4 graph (MashProject8_v12); older graphs keep the constant 24
    })
    return s


def parse(v):
    try:
        return json.loads(v)
    except Exception:
        return v


def main():
    a = sys.argv[1:]
    if len(a) < 2 or a[0] != 'run':
        print(__doc__)
        return 2
    name = a[1]
    engine = os.path.join(ROOT, 'MashProject8')
    graph = os.path.join(ROOT, 'MashProject8', 'MashProject8_v10.dyn')
    out_root = DEFAULT_OUT
    panels = 0.0
    footprint = None
    exe = None
    idx_over, key_over = {}, {}
    i = 2
    while i < len(a):
        t = a[i]
        if t == '--engine':
            engine = os.path.abspath(a[i + 1]); i += 2; continue
        if t == '--graph':
            graph = os.path.abspath(a[i + 1]); i += 2; continue
        if t == '--out':
            out_root = os.path.abspath(a[i + 1]); i += 2; continue
        if t == '--exe':
            exe = os.path.abspath(a[i + 1]); i += 2; continue
        if t == '--footprint':
            footprint = os.path.abspath(a[i + 1]); i += 2; continue
        if t == '--panels':
            panels = float(a[i + 1]); i += 2; continue
        k, v = t.split('=', 1)
        if k.isdigit():
            idx_over[int(k)] = parse(v)
        else:
            key_over[k] = parse(v)
        i += 1
    IN = graph_inputs(graph)
    IN[20] = panels
    for k, v in idx_over.items():
        IN[k] = v
    s = settings_from_inputs(IN)
    s.update(key_over)
    out = os.path.join(out_root, name)
    os.makedirs(out, exist_ok=True)
    sp = os.path.join(out, 'settings.json')
    with open(sp, 'w') as fh:
        json.dump(s, fh, indent=1)
    t0 = time.time()
    fp = footprint or os.path.join(engine, 'Footprint.stl')
    if exe:
        env = dict(os.environ, MPLBACKEND='Agg', PYTHONIOENCODING='utf-8')
        env.pop('PYTHONHOME', None)
        env.pop('PYTHONPATH', None)
        cmd, cwd = [exe, '--footprint', fp, '--settings', sp, '--output-dir', out], os.path.dirname(exe)
    else:
        env = None
        cmd, cwd = [sys.executable, os.path.join(engine, 'Engine_Source.py'), '--footprint', fp, '--settings', sp, '--output-dir', out], engine
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env, encoding='utf-8', errors='replace')
    with open(os.path.join(out, 'log.txt'), 'w', encoding='utf-8') as fh:
        fh.write(r.stdout + '\n--- stderr ---\n' + r.stderr)
    print('[%s] engine exit %d in %.0f s' % (name, r.returncode, time.time() - t0))
    if r.returncode:
        print(r.stderr[-1500:])
        return r.returncode
    print((r.stdout.strip().splitlines() or [''])[-1][:200])
    return 0


if __name__ == '__main__':
    sys.exit(main())
