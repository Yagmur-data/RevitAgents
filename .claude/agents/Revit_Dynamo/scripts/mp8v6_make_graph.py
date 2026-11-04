#!/usr/bin/env python3
"""mp8v6_make_graph.py - builds MashProject8_v15.dyn (graph of the MashProject8_Paylas_V5 package, next to v14) copy-first.

  python mp8v6_make_graph.py

Source: ForDynamo/baklava-panels/MashProject8_v14.dyn (never edited) + the node ForDynamo/baklava-panels/MashProject8_v15.py (build it first with mp8v6_make_node.py).
Output: ForDynamo/baklava-panels/MashProject8_v15.dyn and MashProject8/MashProject8_Paylas_V5/MashProject8_v15.dyn (HintPaths unchanged: the same package folder).
Changes vs v14 (the engine exe is NOT changed): Bridge foot narrowing 0.35 -> 0.0 (straight corridor edges), Bridge Section Height 22 -> 0 (= automatic = circular section, slider minimum 0),
Underside Transition Length relabelled as what it is (a SWITCH), Bridge foot blend length relabelled as the real transition length. Model key stays GAUSS_KABUK_03 (in-place update of the
panel set Al's last run wrote), WRITE False.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, HERE)
from graph_inputs import graph_inputs  # noqa: E402
import dyn_tool  # noqa: E402

SRC = os.path.join(ROOT, 'ForDynamo', 'baklava-panels', 'MashProject8_v14.dyn')
PY = os.path.join(ROOT, 'ForDynamo', 'baklava-panels', 'MashProject8_v15.py')
WORK = os.path.join(ROOT, 'ForDynamo', 'baklava-panels', 'MashProject8_v15.dyn')
PKG = os.path.join(ROOT, 'MashProject8', 'MashProject8_Paylas_V5')
CHANGES = [
    "Bridge Section Height (m)=0.0",
    "Bridge foot narrowing (0 = none; narrows the landing section, avoids the 'ear')=0.0",
]
NEW_INPUT = "bool|Clip the thin-wing ends to the STL slanted outline (True = slanted like the STL, False = straight cut)|true"
RELABEL = {
    "Bridge Section Height (m)": "Bridge Section Height (m; 0 = automatic: equal to the bridge width = CIRCULAR section)",
    "Underside Transition Length (m)": "Underside Transition SWITCH (0 = whole transition + feet OFF; > 0 = ON; the real length is 'Bridge foot blend length')",
    "Bridge foot narrowing (0 = none; narrows the landing section, avoids the 'ear')": "Bridge foot narrowing (0 = straight corridor edges as in the STL; > 0 caves the edges in near the feet)",
    "Bridge foot blend length (m; 0 = off, else 80-140)": "Bridge foot blend length (m) = the REAL underside transition length (0 = off, else 80-140; smooth S-curve, steepest about 30 deg at 100)",
}


def main():
    cmd = [sys.executable, '-I', os.path.join(HERE, 'dyn_tool.py'), 'extend', SRC, '--out', WORK, '--py', PY, '--input', NEW_INPUT, '--name', 'MashProject8_v15',
           '--description', 'MashProject8 v15: v14 + slanted thin-wing ends (panel clip) + straight corridor edges (foot narrowing 0) + circular bridge section (height = width, automatic); engine exe unchanged.']
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
    nodes[by_name['Bridge Section Height (m)']]['MinimumValue'] = 0.0
    for old, new in RELABEL.items():
        assert old in by_name, old
        views[by_name[old]]['Name'] = new
    dyn_tool.save(WORK, d)
    IN, labels = graph_inputs(WORK, with_labels=True)
    for i in (0, 1, 2, 3, 18, 19, 26, 46, 49, 50, 51, 52, 53):
        print('  IN[%d] %-120s = %r' % (i, labels[i][:120], IN[i]))
    assert len(IN) == 54 and IN[53] is True and IN[26] is False and IN[2] == 0.0 and IN[3] == 0.0 and IN[49] == 0.0 and IN[19] == 100.0 and IN[46] == 100.0
    assert IN[18] == 'GAUSS_KABUK_03' and IN[50] == 0.0 and IN[51] == 0.0 and IN[52] == '' and IN[0].endswith('Footprint_261014.stl')
    for n in dyn_tool.load(WORK)['Nodes']:
        if 'HintPath' in n and n['HintPath'] != '.':
            assert os.path.normpath(n['HintPath']).startswith(os.path.normpath(PKG)), n['HintPath']
    s = open(WORK, encoding='utf-8').read()
    if os.path.isdir(PKG):
        open(os.path.join(PKG, 'MashProject8_v15.dyn'), 'w', encoding='utf-8', newline='').write(s)
        print('package copy written:', os.path.join(PKG, 'MashProject8_v15.dyn'))
    files = [WORK] + ([os.path.join(PKG, 'MashProject8_v15.dyn')] if os.path.isdir(PKG) else [])
    r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'dyn_tool.py'), 'validate'] + files, capture_output=True, text=True)
    print(r.stdout.strip())
    return r.returncode


if __name__ == '__main__':
    sys.exit(main())
