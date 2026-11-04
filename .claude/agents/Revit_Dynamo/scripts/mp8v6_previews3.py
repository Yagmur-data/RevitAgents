#!/usr/bin/env python3
"""mp8v6_previews3.py - wing end preview with the panel clip (graph v15) next to the old vertical cut (v14) and the engine-V3 slanted-cut proposal. Library of mp8v6_previews.py."""
import array
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mp8v6_measure as M        # noqa: E402
import panel_clip as PC          # noqa: E402

RED = '#d62728'


def rhombus_tris(n):
    t = []
    for i in range(n):
        for j in range(n):
            v00, v10, v11, v01 = i * (n + 1) + j, (i + 1) * (n + 1) + j, (i + 1) * (n + 1) + j + 1, i * (n + 1) + j + 1
            t += [(v00, v10, v11), (v00, v11, v01)]
    return t


def triangle_tris(n):
    bary = [(i, j) for i in range(n + 1) for j in range(n + 1 - i)]
    bi = dict((ij, k) for k, ij in enumerate(bary))
    t = []
    for i in range(n):
        for j in range(n - i):
            t.append((bi[(i, j)], bi[(i + 1, j)], bi[(i, j + 1)]))
            if i + j < n - 1:
                t.append((bi[(i + 1, j)], bi[(i + 1, j + 1)], bi[(i, j + 1)]))
    return t


def user_panels(bkl, adapter_json, clip=False):
    """node-style panels (kind, array('f')) in Al's frame; with clip=True the node's clip_panels is applied with the adapter record's clip_lines."""
    n, rh, tr = M.bkl_to_user(bkl, adapter_json)
    panels = [(0, array.array('f', a.ravel().tolist())) for a in rh] + [(1, array.array('f', a.ravel().tolist())) for a in tr]
    tabs = {0: rhombus_tris(n), 1: triangle_tris(n)}
    stats = None
    if clip:
        lines = json.load(open(adapter_json)).get('clip_lines') or []
        panels, stats = PC.clip_panels(panels, tabs, lines)
    return n, panels, tabs, stats


def outline_of(kind, v, n, tabs):
    pts = np.frombuffer(v, dtype=np.float32).reshape(-1, 3).astype(float)
    if kind == 0:
        ring = [0, n, (n + 1) * (n + 1) - 1, n * (n + 1)]
        return [pts[ring, :2]], []
    if kind == 1:
        ring = [0, n, (n + 1) * (n + 2) // 2 - 1]
        return [pts[ring, :2]], []
    tris = pts.reshape(-1, 3, 3)
    edges = {}
    for t in tris:
        for a in range(3):
            p, q = t[a, :2], t[(a + 1) % 3, :2]
            k = (tuple(np.round(p, 4)), tuple(np.round(q, 4)))
            kr = (k[1], k[0])
            if kr in edges:
                edges[kr] = None
            else:
                edges[k] = (p, q)
    segs = [e for e in edges.values() if e is not None]
    return [t[:, :2] for t in tris], segs


def fig_ends(cfg, out):
    P = M.footprint_outline(cfg['footprint'])
    cols = (('before', False, 'ONCE (graf v14): dik kesim X = 30, STL ucgeni bos'), ('v15', True, 'SONRA (graf v15, exe ayni): 0.6 m otesinde kes + paneli STL egik cizgisine KIRP'),
            ('proposal', False, 'ONERI (motor V3, derlenmedi): kabuk egik duzlemde kesilir'))
    wins = (((-25, 100, 425, 515), 'sol uc - ince kanat'), ((-5, 105, 100, 170), 'sol kose - kalin kanat'))
    fig, axs = plt.subplots(2, 3, figsize=(21, 11.5))
    stats = {}
    for j, (key, clip, ttl) in enumerate(cols):
        if key not in cfg or not cfg[key].get('bkl'):
            for i in range(2):
                axs[i, j].axis('off')
            continue
        n, panels, tabs, cs = user_panels(cfg[key]['bkl'], cfg[key]['adapter'], clip=clip)
        cen, cz = [], []
        for kind, v in panels:
            a = np.frombuffer(v, dtype=np.float32).reshape(-1, 3)
            cen.append(a[:, :2].mean(0))
            cz.append(a[:, 2].mean())
        cen, cz = np.array(cen), np.array(cz)
        for i, (win, wname) in enumerate(wins):
            ax = axs[i, j]
            sel = [k for k in range(len(panels)) if win[0] - 8 <= cen[k, 0] <= win[1] + 8 and win[2] - 8 <= cen[k, 1] <= win[3] + 8 and cz[k] > 21.0]   # upper surface only
            polys, colors, segs = [], [], []
            ntri = nclip = 0
            for k in sel:
                kind, v = panels[k]
                pl, sg = outline_of(kind, v, n, tabs)
                if kind >= 2:
                    nclip += 1
                    ntri += 0
                    polys += pl
                    colors += [(1.0, 0.86, 0.55)] * len(pl)
                    segs += sg
                else:
                    ntri += 1 if kind == 1 else 0
                    polys += pl
                    colors += [(0.80, 0.86, 0.94) if kind == 0 else (0.98, 0.78, 0.55)] * len(pl)
            ax.add_collection(PolyCollection(polys, facecolors=colors, edgecolors='0.45', linewidths=0.35))
            if segs:
                ax.add_collection(LineCollection(segs, colors='k', linewidths=0.9))
            ax.plot(np.r_[P[:, 0], P[0, 0]], np.r_[P[:, 1], P[0, 1]], '-', color=RED, lw=1.8)
            ax.set_xlim(win[0], win[1])
            ax.set_ylim(win[2], win[3])
            ax.set_aspect('equal')
            ax.set_title('%s\n%s' % (ttl, wname), fontsize=9.5)
            ax.set_xlabel('X (m)   kirmizi cizgi = Footprint_261014.stl')
            ax.text(0.02, 0.97, '%d panel%s%s' % (len(sel), (', %d kirpilmis (turuncu)' % nclip) if nclip else '', (', %d ucgen' % ntri) if ntri else ''), transform=ax.transAxes, va='top', fontsize=8.5, bbox=dict(fc='w', ec='0.6'))
            stats['%s_%s' % (key, 'thin' if i == 0 else 'thick')] = dict(panels=len(sel), clipped=nclip, triangles=ntri)
        if cs:
            stats['%s_clip' % key] = cs
    fig.suptitle('Uc bolgesi (plan): paneller ve STL cizgisi (kirmizi); turuncu = STL cizgisine kirpilan paneller (siyah = yeni kenar)', fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out, dpi=65)
    plt.close(fig)
    return stats


def fig_plan_panels(cfg, out):
    """plan of the PANELS (what Revit shows) vs Al's footprint outline: before (v14) / v15 (cut 0.6 m beyond the ends + clip) / proposal (engine V3)."""
    import mp8v6_previews as PV
    P = M.footprint_outline(cfg['footprint'])
    items = (('before', False, 'ONCE (graf v14): dik kesim X = 30, ayak daralmasi 0.35'),
             ('v15', True, 'SONRA (graf v15, exe ayni): kabuk uc 0.6 m otesinde kesilir,\npaneller STL egik cizgisine kirpilir, ayak daralmasi 0'),
             ('proposal', False, 'ONERI (motor V3, derlenmedi): egik kesim,\nsabit aci rampasi / yay secenekleri'))
    fig, axs = plt.subplots(1, 3, figsize=(21, 10.5))
    stats = {}
    for ax, (k, clip, ttl) in zip(axs, items):
        n, panels, tabs, cs = user_panels(cfg[k]['bkl'], cfg[k]['adapter'], clip=clip)
        S = panel_plan_mask(panels, tabs)
        pc = M.plan_compare_mask(S, P)
        PV.plan_panel(ax, pc, P, ttl, PV.classify_notes(pc))
        ce = M.corridor_edges(pc, ys=range(190, 411, 10))
        gaps = [max(abs(l - 226.5), abs(r - 253.5)) for (_, l, r) in ce if l is not None]
        ax.set_xlabel('koridor kenari - STL farki (en fazla): %.2f m\nSTL icinde panelsiz alan (>0.5 m): %d m2   |   %d panel' % (max(gaps), round(pc['area_under']), len(panels)), fontsize=9.5)
        stats[k] = dict(area_under=round(pc['area_under'], 1), area_over=round(pc['area_over'], 1), corridor_gap_max=round(max(gaps), 2), panels=len(panels),
                        comps=[dict(kind=c['kind'], area=c['area'], depth=c['depth'], cx=c['cx'], cy=c['cy']) for c in pc['comps'] if c['area'] >= 40], clip=cs)
    fig.suptitle('Plan (paneller): mavi = panellerin kapladigi alan, siyah cizgi = Footprint_261014.stl, kirmizi = STL icinde panel YOK, turuncu = STL disina tasan', fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out, dpi=75)
    plt.close(fig)
    return stats


def panel_plan_mask(panels, tabs, res=0.25, x0=-30.0, y0=-20.0, W=None, H=None):
    from PIL import Image, ImageDraw
    from scipy import ndimage
    W = W or int((540.0 - x0) / res)
    H = H or int((560.0 - y0) / res)
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    for kind, v in panels:
        a = np.frombuffer(v, dtype=np.float32).reshape(-1, 3)
        if kind >= 2:
            for t in a.reshape(-1, 3, 3):
                d.polygon([((q[0] - x0) / res, (q[1] - y0) / res) for q in t], fill=1)
        else:
            for (i, j, k) in tabs[kind]:
                d.polygon([((a[q, 0] - x0) / res, (a[q, 1] - y0) / res) for q in (i, j, k)], fill=1)
    return ndimage.binary_closing(np.asarray(im).astype(bool), iterations=3)
