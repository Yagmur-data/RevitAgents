#!/usr/bin/env python3
"""mp8v5_make_graph.py - (re)build MashProject8_v14.dyn (the graph of the MashProject8_Paylas_V5 package) copy-first.

  python mp8v5_make_graph.py

Source: ForDynamo/baklava-panels/MashProject8_v12.dyn (the V4 graph, never edited) + the node ForDynamo/baklava-panels/MashProject8_v14.py.
Output: ForDynamo/baklava-panels/MashProject8_v14.dyn and MashProject8/MashProject8_Paylas_V5/MashProject8_v14.dyn (HintPaths -> the V5 package folder).
v14 replaces v13 (which REFUSED Al's own STL): the Filename input points at the RAW footprint .\\Footprint_261014.stl and the node derives the engine-frame footprint itself.
Values: Bridge Width 0 (= automatic: corridor width of the footprint), Left outer cap depth 0 (= automatic), foot heights 0 / 0 (TRUE heights, the node adds the calibration offset),
model key GAUSS_KABUK_03, WRITE False. New input: 'Old model key to delete after writing'. Sliders Bridge Width / cap depth get minimum 0.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, HERE)
from graph_inputs import graph_inputs  # noqa: E402
import dyn_tool  # noqa: E402

SRC = os.path.join(ROOT, 'ForDynamo', 'baklava-panels', 'MashProject8_v12.dyn')
PY = os.path.join(ROOT, 'ForDynamo', 'baklava-panels', 'MashProject8_v14.py')
WORK = os.path.join(ROOT, 'ForDynamo', 'baklava-panels', 'MashProject8_v14.dyn')
PKG = os.path.join(ROOT, 'MashProject8', 'MashProject8_Paylas_V5')
CHANGES = [
    "Bridge Width (m)=0.0",
    "Model key (type GAUSS_KABUK_01 to replace the old shell)=GAUSS_KABUK_03",
    "Bridge foot height at LEFT arm (m above ground, 0 = touches ground)=0.0",
    "Bridge foot height at RIGHT arm (m above ground, 0 = touches ground)=0.0",
    "Left outer cap depth (m; 35.09 = one ellipse with the V4 footprint, 24 = old shape)=0.0",
    "WRITE TO REVIT (False = DRY RUN)=False",
]
NEW_INPUT = "string|Old model key to delete after writing (empty = keep; e.g. GAUSS_KABUK_02)|"
RELABEL = {
    "Select Footprint STL": "Select Footprint STL (YOUR OWN file, e.g. Footprint_261014.stl; the node converts it itself)",
    "Bridge Width (m)": "Bridge Width (m; 0 = automatic: the corridor width of the footprint)",
    "Left outer cap depth (m; 35.09 = one ellipse with the V4 footprint, 24 = old shape)": "Left outer cap depth (m; 0 = automatic: (arm width + 24) / 2 from the footprint = one ellipse)",
    "Left Opening Height (m)": "Left Opening Height (m) [engine LEFT = thin wing]",
    "Right Opening Height (m)": "Right Opening Height (m) [engine RIGHT = thick wing]",
    "Bridge foot height at LEFT arm (m above ground, 0 = touches ground)": "Bridge foot height at the THIN-wing end (true height above ground, 0 = touches the ground)",
    "Bridge foot height at RIGHT arm (m above ground, 0 = touches ground)": "Bridge foot height at the THICK-wing end (true height above ground, 0 = touches the ground)",
}


def main():
    cmd = [sys.executable, '-I', os.path.join(HERE, 'dyn_tool.py'), 'extend', SRC, '--out', WORK, '--py', PY, '--input', NEW_INPUT, '--name', 'MashProject8_v14',
           '--description', 'MashProject8 V5b: select YOUR OWN footprint STL (Footprint_261014.stl); the node derives the engine-frame footprint at run time, maps panels back; elliptical mouth + feet on the ground.']
    for c in CHANGES:
        cmd += ['--set', c]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode:
        print(r.stderr)
        return r.returncode
    d = dyn_tool.load(WORK)
    views = {v['Id']: v for v in d['View']['NodeViews']}
    by_name = {v['Name']: v['Id'] for v in d['View']['NodeViews']}
    nodes = {n['Id']: n for n in d['Nodes']}
    # raw footprint as the default Filename (relative InputValue, absolute HintPath into the package)
    n0 = nodes[by_name['Select Footprint STL']]
    n0['InputValue'] = '.\\Footprint_261014.stl'
    for n in d['Nodes']:
        h = n.get('HintPath')
        if h and h != '.' and 'Paylas' in h:
            tail = n['InputValue'].lstrip('.\\')
            n['HintPath'] = PKG.replace('/', '\\').rstrip('\\') + '\\' + tail
    for label in ("Bridge Width (m)", "Left outer cap depth (m; 35.09 = one ellipse with the V4 footprint, 24 = old shape)"):
        nodes[by_name[label]]['MinimumValue'] = 0.0
    for old, new in RELABEL.items():
        assert old in by_name, old
        views[by_name[old]]['Name'] = new
    dyn_tool.save(WORK, d)
    IN, labels = graph_inputs(WORK, with_labels=True)
    for i in (0, 1, 3, 5, 6, 18, 26, 28, 32, 33, 35, 47, 48, 50, 51, 52):
        print('  IN[%d] %-110s = %r' % (i, labels[i][:110], IN[i]))
    assert len(IN) == 53 and IN[26] is False and IN[3] == 0.0 and IN[18] == 'GAUSS_KABUK_03' and IN[47] == 0.0 and IN[48] == 0.0 and IN[50] == 0.0
    assert IN[32] == 2.0 and IN[33] == 2.0 and IN[35] == 27.0 and IN[51] == 0.0 and IN[52] == '' and IN[0].endswith('Footprint_261014.stl')
    for n in dyn_tool.load(WORK)['Nodes']:
        if 'HintPath' in n and n['HintPath'] != '.':
            assert os.path.normpath(n['HintPath']).startswith(os.path.normpath(PKG)), n['HintPath']
    s = open(WORK, encoding='utf-8').read()
    if os.path.isdir(PKG):
        open(os.path.join(PKG, 'MashProject8_v14.dyn'), 'w', encoding='utf-8', newline='').write(s)
        print('package copy written:', os.path.join(PKG, 'MashProject8_v14.dyn'))
    files = [WORK] + ([os.path.join(PKG, 'MashProject8_v14.dyn')] if os.path.isdir(PKG) else [])
    r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'dyn_tool.py'), 'validate'] + files, capture_output=True, text=True)
    print(r.stdout.strip())
    return r.returncode


if __name__ == '__main__':
    sys.exit(main())
