#!/usr/bin/env python3
"""mp8v6_rims.py - open boundary loops (mouth rims) of an engine shell STL in Al's footprint frame + least-squares ellipse fit. Library of mp8v6_selftest.py / the previews."""
import os
import sys

import numpy as np
import trimesh
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mp8v6_measure as M        # noqa: E402
import mp8v4_measure as M4       # noqa: E402


def loops(stl, adapter_json):
    """list of (n, 3) arrays: the open boundary loops of the shell in the footprint frame (vertices welded at 0.1 mm)."""
    U, ad = M.load_user_mesh(stl, adapter_json)
    V = U.reshape(-1, 3)
    key = np.round(V / 1e-4).astype(np.int64)
    uk, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.ravel()
    mesh = trimesh.Trimesh(V[first], inv.reshape(-1, 3), process=False)
    return M4.boundary_loops(mesh)


def fit(P):
    """axis-aligned ellipse fit of 2D points -> (centre x, centre y, A, B), residuals (m)."""
    f = lambda p: (np.hypot((P[:, 0] - p[0]) / p[2], (P[:, 1] - p[1]) / p[3]) - 1.0) * np.sqrt(p[2] * p[3])
    s = least_squares(f, [P[:, 0].mean(), P[:, 1].mean(), np.ptp(P[:, 0]) / 2, np.ptp(P[:, 1]) / 2])
    return s.x, f(s.x)
