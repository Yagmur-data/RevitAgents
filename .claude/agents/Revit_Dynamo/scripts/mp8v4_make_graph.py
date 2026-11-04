#!/usr/bin/env python3
"""mp8v4_make_graph.py - (re)build MashProject8_v12.dyn (the graph of the MashProject8_Paylas_V4 package) copy-first.

  python mp8v4_make_graph.py

Source of truth: the USER'S graph MashProject8/MashProject8_v10.dyn (never edited: the new graph is a copy with new node code, one new input and
five changed values) + the node code ForDynamo/baklava-panels/MashProject8_v12.py. Output: ForDynamo/baklava-panels/MashProject8_v12.dyn (working copy) and
MashProject8/MashProject8_Paylas_V4/MashProject8_v12.dyn (package copy, HintPaths retargeted to the package folder). Values carried over from the user's file:
every slider except the ones listed in CHANGES. WRITE is forced False. Runs dyn_tool validate and prints the final input list for the changed values.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, HERE)
from graph_inputs import graph_inputs  # noqa: E402

SRC = os.path.join(ROOT, 'MashProject8', 'MashProject8_v10.dyn')
PY = os.path.join(ROOT, 'ForDynamo', 'baklava-panels', 'MashProject8_v12.py')
WORK = os.path.join(ROOT, 'ForDynamo', 'baklava-panels', 'MashProject8_v12.dyn')
PKG = os.path.join(ROOT, 'MashProject8', 'MashProject8_Paylas_V4')
CHANGES = [
    "Mouth section exponent (2 = ellipse, 3-4 = rounded rectangle)=2.0",
    "Left outer cap exponent (2 = ellipse)=2.0",
    "Section corner width (m; smaller = flatter top, taller side)=27.0",
    "Bridge foot follows arm underside (1 = lands at the arm's own underside level, 0 = lands on true ground)=0",
    "WRITE TO REVIT (False = DRY RUN)=False",
]
NEW_INPUT = "double|Left outer cap depth (m; 35.09 = one ellipse with the V4 footprint, 24 = old shape)|35.09|10|60|0.01"


def main():
    if not os.path.isfile(SRC):
        sys.exit('missing ' + SRC)
    cmd = [sys.executable, '-I', os.path.join(HERE, 'dyn_tool.py'), 'extend', SRC, '--out', WORK, '--py', PY, '--input', NEW_INPUT,
           '--name', 'MashProject8_v12',
           '--description', 'MashProject8 V4: elliptical arm mouth (one ellipse) + bridge feet on the ground. Engine = unchanged MashProject8_Paylas_V3 exe; Footprint.stl = V4 footprint.']
    for c in CHANGES:
        cmd += ['--set', c]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode:
        print(r.stderr)
        return r.returncode
    # HintPaths -> package folder (the InputValue stays relative: .\\Footprint.stl, .\\Engine\\MashEngine.exe)
    s = open(WORK, encoding='utf-8').read()
    d = json.loads(s)
    for n in d['Nodes']:
        h = n.get('HintPath')
        if h and h != '.' and 'Paylas' in h:
            tail = n['InputValue'].lstrip('.\\')
            new = PKG.replace('/', '\\').rstrip('\\') + '\\' + tail
            old_esc, new_esc = json.dumps(h), json.dumps(new)
            assert s.count(old_esc) == 1, (old_esc, s.count(old_esc))
            s = s.replace(old_esc, new_esc)
    open(WORK, 'w', encoding='utf-8', newline='').write(s)
    IN, labels = graph_inputs(WORK, with_labels=True)
    for i in (0, 1, 26, 28, 32, 33, 34, 35, 46, 47, 48, 49, 50, 51):
        print('  IN[%d] %-100s = %r' % (i, labels[i][:100], IN[i]))
    assert IN[26] is False and IN[32] == 2.0 and IN[33] == 2.0 and IN[35] == 27.0 and IN[50] == 0.0 and abs(IN[51] - 35.09) < 1e-9
    d = json.loads(s)
    for n in d['Nodes']:
        if 'HintPath' in n and n['HintPath'] != '.':
            assert os.path.normpath(n['HintPath']).startswith(os.path.normpath(PKG)), n['HintPath']
    if os.path.isdir(PKG):
        open(os.path.join(PKG, 'MashProject8_v12.dyn'), 'w', encoding='utf-8', newline='').write(s)
        print('package copy written:', os.path.join(PKG, 'MashProject8_v12.dyn'))
    r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'dyn_tool.py'), 'validate', WORK] +
                       ([os.path.join(PKG, 'MashProject8_v12.dyn')] if os.path.isdir(PKG) else []), capture_output=True, text=True)
    print(r.stdout.strip())
    return r.returncode


if __name__ == '__main__':
    sys.exit(main())
