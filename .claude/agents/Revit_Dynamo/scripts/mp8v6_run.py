#!/usr/bin/env python3
"""mp8v6_run.py - run the MashProject8 engine (frozen exe OR a Python source copy) with a saved settings.json + KEY=VALUE overrides. No Revit, no Dynamo.

  python mp8v6_run.py NAME --base SETTINGS.json --footprint ENGINE_FOOTPRINT.stl [--exe MashEngine.exe | --engine DIR] [--out ROOT] [KEY=VAL ...]

  --base       settings.json captured from a node run (engine_capture.py KEEP_STL=1 or a real run); all keys are sent unchanged except the overrides
  KEY=VAL      engine setting override (JSON value), e.g. BRIDGE_FOOT_NARROW=0  PANEL_EDGE=0 (shell only, much faster)  SIGMA_X_UST=70
  --ovr FILE   JSON file with more overrides (lists/dicts, e.g. SLANT_CUTS)
  --exe        frozen engine (cwd = its folder)          --engine DIR   folder holding Engine_Source.py + baklava_panels.py (python, cwd = DIR)
Output: ROOT/NAME/{settings.json, AYARLANABILIR_GAUSS_KABUK.stl, BAKLAVA_PANELS.bkl, baklava_report.json, log.txt}; prints the engine's last line.
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
DEFAULT_EXE = os.path.join(ROOT, 'MashProject8', 'MashProject8_Paylas_V5', 'Engine', 'MashEngine.exe')
DEFAULT_OUT = os.environ.get('MP8V6_OUT') or os.path.join(os.environ.get('TEMP', '.'), 'mp8v6')


def parse(v):
    try:
        return json.loads(v)
    except Exception:
        return v


def run(name, base, footprint, overrides, exe=None, engine=None, out_root=DEFAULT_OUT):
    s = json.load(open(base))
    s.update(overrides)
    out = os.path.join(out_root, name)
    os.makedirs(out, exist_ok=True)
    sp = os.path.join(out, 'settings.json')
    json.dump(s, open(sp, 'w'), indent=1)
    if engine:
        cmd, cwd, env = [sys.executable, os.path.join(engine, 'Engine_Source.py'), '--footprint', footprint, '--settings', sp, '--output-dir', out], engine, None
    else:
        exe = exe or DEFAULT_EXE
        env = dict(os.environ, MPLBACKEND='Agg', PYTHONIOENCODING='utf-8')
        env.pop('PYTHONHOME', None)
        env.pop('PYTHONPATH', None)
        cmd, cwd = [exe, '--footprint', footprint, '--settings', sp, '--output-dir', out], os.path.dirname(exe)
    if env is None:
        env = dict(os.environ, MPLBACKEND='Agg', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env, encoding='utf-8', errors='replace')
    open(os.path.join(out, 'log.txt'), 'w', encoding='utf-8').write(r.stdout + '\n--- stderr ---\n' + r.stderr)
    last = (r.stdout.strip().splitlines() or [''])[-1][:300]
    print('[%s] exit %d in %.0f s  %s' % (name, r.returncode, time.time() - t0, last))
    if r.returncode:
        print(r.stderr[-1500:])
    return r.returncode, out


def main():
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'):
        print(__doc__)
        return 2
    name = a[0]
    base = fp = exe = engine = None
    out_root = DEFAULT_OUT
    ov = {}
    i = 1
    while i < len(a):
        t = a[i]
        if t == '--base':
            base = os.path.abspath(a[i + 1]); i += 2; continue
        if t == '--footprint':
            fp = os.path.abspath(a[i + 1]); i += 2; continue
        if t == '--exe':
            exe = os.path.abspath(a[i + 1]); i += 2; continue
        if t == '--engine':
            engine = os.path.abspath(a[i + 1]); i += 2; continue
        if t == '--out':
            out_root = os.path.abspath(a[i + 1]); i += 2; continue
        if t == '--ovr':                      # JSON file with a dict of overrides (lists / nested values)
            ov.update(json.load(open(a[i + 1], encoding='utf-8'))); i += 2; continue
        k, v = t.split('=', 1)
        ov[k] = parse(v)
        i += 1
    if not base or not fp:
        print('--base and --footprint are required')
        return 2
    return run(name, base, fp, ov, exe, engine, out_root)[0]


if __name__ == '__main__':
    sys.exit(main())
