#!/usr/bin/env python3
"""make_footprint_v5.py - thin command line wrapper around footprint_adapter.py (the SAME code the Dynamo node v14 runs at run time).

  python make_footprint_v5.py Footprint_261014.stl OUT_DIR

Reads Al's footprint (his own frame), recognises the 'I' layout (corridor, thin wing, thick wing, fillet arcs), derives every adapter value from the outline measures and writes
OUT_DIR/<stem>.engine_<md5-8>.stl (the ENGINE-FRAME footprint) + OUT_DIR/<stem>.engine_<md5-8>.adapter.json (affine map, dx, dy, inset, cap depth, cut distance, corridor width, foot offset ...).
The node derives the identical file itself when the user selects the raw STL; this tool exists for tests, previews and to inspect the values. See footprint_adapter.py for the rules.
(History: v13 of the node REFUSED Al's own file and needed a pre-converted Footprint.stl made by an earlier numpy version of this script - a wrong product decision, replaced 2026-10-14.)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import footprint_adapter as FA   # noqa: E402


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    try:
        out, info = FA.derive(sys.argv[1], sys.argv[2])
    except FA.AdapterError as exc:
        print('NOT RECOGNISED: %s' % exc)
        return 1
    print('wrote %s (%d STL triangles) + adapter.json' % (out, info['stl_triangles']))
    print(json.dumps({k: info[k] for k in info if k not in ('unrounded_corners', 'frame')}, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
