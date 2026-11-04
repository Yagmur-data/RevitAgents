#!/usr/bin/env python3
"""mp8v6_render.py - small shaded-shell renderer for the v15 previews (matplotlib, orthographic, painter's algorithm, no GPU). Library only.

  render_shell(ax, U, view=(dx, dy, dz), bbox=None, cell=1.0, color=(...))   U = triangles (n,3,3) in the footprint frame; draws into a matplotlib axis
"""
import numpy as np
from matplotlib.collections import PolyCollection


def decimate(T, cell):
    """vertex clustering of a triangle soup (n,3,3) -> (V, F)."""
    V = T.reshape(-1, 3)
    key = np.round(V / cell).astype(np.int64)
    uk, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.ravel()
    cnt = np.bincount(inv, minlength=len(uk)).astype(float)
    Vn = np.zeros((len(uk), 3))
    for ax in range(3):
        Vn[:, ax] = np.bincount(inv, weights=V[:, ax], minlength=len(uk)) / cnt
    F = inv.reshape(-1, 3)
    ok = (F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2])
    F = F[ok]
    s = np.sort(F, axis=1)
    _, first = np.unique(s, axis=0, return_index=True)
    return Vn, F[first]


def basis(view, up=(0, 0, 1.0)):
    d = np.array(view, float)
    d /= np.linalg.norm(d)
    up = np.array(up, float)
    r = np.cross(d, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, d)
    return r, u, d


def render_shell(ax, U, view=(0.45, 0.75, -0.55), bbox=None, cell=1.0, base=(0.62, 0.70, 0.78), light=(-0.4, -0.5, 0.8), lw=0.0, alpha=1.0, edge=None):
    T = U
    if bbox is not None:
        c = T.mean(axis=1)
        sel = (c[:, 0] >= bbox[0]) & (c[:, 0] <= bbox[1]) & (c[:, 1] >= bbox[2]) & (c[:, 1] <= bbox[3])
        T = T[sel]
    V, F = decimate(T, cell)
    r, u, d = basis(view)
    P = V[F]
    n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1
    n = n / ln[:, None]
    # two-sided shading
    L = np.array(light, float)
    L /= np.linalg.norm(L)
    sh = np.abs(n @ L)
    col = np.array(base)[None, :] * (0.35 + 0.65 * sh[:, None])
    col = np.clip(col, 0, 1)
    X = P @ r
    Y = P @ u
    depth = (P @ d).mean(axis=1)
    order = np.argsort(-depth)            # far first
    polys = np.stack([X, Y], axis=2)[order]
    pc = PolyCollection(polys, facecolors=col[order], edgecolors=edge if edge else 'face', linewidths=lw, alpha=alpha)
    ax.add_collection(pc)
    ax.set_xlim(X.min(), X.max())
    ax.set_ylim(Y.min(), Y.max())
    ax.set_aspect('equal')
    ax.axis('off')
    return r, u, d
