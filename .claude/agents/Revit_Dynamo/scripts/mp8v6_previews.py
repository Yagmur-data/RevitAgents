#!/usr/bin/env python3
"""mp8v6_previews.py - preview PNGs of the v15 round (Al's 4 notes of 2026-10-14), written to ForDynamo/baklava-panels/V6_*.png. Offline, no Revit.

  python mp8v6_previews.py OUTDIR --cfg CFG.json [--only plan,mouth,bridge,schema,ends]

CFG.json (paths; all STL/bkl in the ENGINE frame, each with the adapter record that maps them back to Al's footprint frame):
  footprint            Footprint_261014.stl (Al's)
  before               {stl, adapter, bkl}      graph v14 run (narrowing 0.35, section 22)
  v15                  {stl, adapter, bkl}      graph v15 defaults with the real exe (narrowing 0, circular section)
  proposal             {stl, adapter, bkl}      engine V3 prototype (slanted ends) - not built into an exe
  ramp30, arc, s_curve {stl, adapter}           proposal foot profiles (angle ramp / arc / S-curve with the circular section)
  sigma70              {stl, adapter}           v15 with Gauss Sigma X 70
Images: V6_plan_once_sonra.png, V6_agiz_elips_apertur.png, V6_kopru_kesit_alt_profil.png, V6_gecis_uzunlugu_semasi.png, V6_uc_ucgen_paneller.png
"""
import argparse
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Polygon as MPoly

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mp8v6_measure as M        # noqa: E402

RED, ORG, BLU, GRN = '#d62728', '#ff9f1c', '#1f77b4', '#2ca02c'


def load(entry):
    U, ad = M.load_user_mesh(entry['stl'], entry['adapter'])
    return U, ad


def plan_panel(ax, pc, P, title, notes):
    res, x0, y0 = pc['res'], pc['x0'], pc['y0']
    H, W = pc['S'].shape
    ext = [x0, x0 + W * res, y0, y0 + H * res]
    img = np.ones((H, W, 3))
    img[pc['S']] = (0.80, 0.86, 0.93)
    img[pc['over']] = (1.0, 0.85, 0.55)
    img[pc['under']] = (0.95, 0.45, 0.45)
    ax.imshow(img, origin='lower', extent=ext, interpolation='nearest')
    ax.plot(np.r_[P[:, 0], P[0, 0]], np.r_[P[:, 1], P[0, 1]], 'k-', lw=1.1)
    ax.set_xlim(-25, 505)
    ax.set_ylim(-15, 525)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=10)
    ax.tick_params(labelsize=7)
    for (x, y, t, col) in notes:
        ax.text(x, y, t, fontsize=7.5, color=col, ha='center', va='center', bbox=dict(fc='w', ec=col, lw=0.6, alpha=0.85, boxstyle='round,pad=0.2'))


def classify_notes(pc, cut=(35.0, 445.0)):
    notes = []
    for c in pc['comps']:
        if c['area'] < 40:
            continue
        if c['kind'] == 'over':
            notes.append((240, 496, 'kapak tasmasi (tasarim): Y 484 -> 508, %d m2' % round(c['area']) if c['area'] > 3000 else 'STL disina tasma: %d m2' % round(c['area']), '#b36b00'))
            continue
        ends = c['cx'] < cut[0] or c['cx'] > cut[1]
        if ends:
            lab = ('ince kanat ucu: ucgen YOK\n%d m2' if c['cy'] > 300 else 'kalin kanat kosesi YOK\n%d m2') % round(c['area'])
        else:
            lab = 'coken kenar\n%.1f m, %d m2' % (c['depth'], round(c['area']))
        notes.append((c['cx'] + (0 if ends else (-48 if c['cx'] < 240 else 48)), c['cy'] + (16 if ends else 0), lab, RED))
    return notes


def fig_plan(cfg, out):
    P = M.footprint_outline(cfg['footprint'])
    items = (('before', 'ONCE (graf v14: ayak daralmasi 0.35, uc dik kesim)'), ('v15', 'SONRA - graf v15 (exe ayni): ayak daralmasi 0'), ('proposal', 'ONERI - motor V3 (egik uc kesimi; exe yeniden derlenmeli)'))
    fig, axs = plt.subplots(1, 3, figsize=(19.5, 8.4))
    stats = {}
    for ax, (k, ttl) in zip(axs, items):
        U, ad = load(cfg[k])
        pc = M.plan_compare(U, P)
        plan_panel(ax, pc, P, ttl, classify_notes(pc))
        ce = M.corridor_edges(pc, ys=range(190, 411, 10))
        gaps = [max(abs(l - 226.5), abs(r - 253.5)) for (_, l, r) in ce if l is not None]
        stats[k] = dict(area_under=pc['area_under'], area_over=pc['area_over'], corridor_gap_max=max(gaps), comps=[c for c in pc['comps'] if c['area'] >= 40])
        ax.text(0.5, -0.07, 'koridor kenari - STL farki (en fazla): %.1f m   |   eksik alan (>0.5 m): %d m2' % (max(gaps), round(pc['area_under'])), transform=ax.transAxes, ha='center', fontsize=9)
    fig.suptitle('Plan: kabuk (mavi) ve Footprint_261014.stl cizgisi (siyah); kirmizi = STL icinde kabuk yok, turuncu = kabuk STL disina tasiyor (kapak, tasarim geregi)', fontsize=11)
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    fig.savefig(out, dpi=70)
    plt.close(fig)
    return stats


def ell_xy(p, n=240):
    t = np.linspace(0, 2 * np.pi, n)
    return p[0] + p[2] * np.cos(t), p[1] + p[3] * np.sin(t)


def rim_fit_panels(bkl, adapter, origin, normal, slant=None):
    n, rh, tr = M.bkl_to_user(bkl, adapter)
    P = M.rim_points(n, rh, tr, origin, normal, 0.06)
    P = P[(P[:, 1] > 430) if origin[0] < 100 or origin[0] > 400 else (P[:, 1] > -1e9)]
    if slant is None:
        xy = np.c_[P[:, 1], P[:, 2]]
    else:
        u = slant
        xy = np.c_[(P[:, 0] - origin[0]) * u[0] + (P[:, 1] - origin[1]) * u[1], P[:, 2]]
    p, r = M.fit_ellipse_pts(xy)
    return xy, p, r


def fig_mouth(cfg, out):
    fig, axs = plt.subplots(2, 3, figsize=(18, 10.5))
    res = {}
    # ---- row 0: mouth rims from the PANELS (v14 graph: vertical cut; proposal: slanted cut)
    for ax, (o, nv, ttl) in zip(axs[0, :2], (((30.0, 0.0), (1.0, 0.0), 'SOL agiz (X = 30): panel noktalari'), ((450.0, 0.0), (-1.0, 0.0), 'SAG agiz (X = 450): panel noktalari'))):
        xy, p, r = rim_fit_panels(cfg['before']['bkl'], cfg['before']['adapter'], o, nv)
        ax.plot(xy[:, 0], xy[:, 1], 'k.', ms=4)
        ax.plot(*ell_xy(p), 'r--', lw=1.2)
        ax.set_aspect('equal')
        ax.set_title(ttl, fontsize=10)
        ax.set_ylim(-5, 46)
        ax.set_xlabel('Y (m)\nelips A %.2f x B %.2f m | en buyuk sapma %.2f m = %%%.1f B (rms %.2f)' %(p[2], p[3], np.abs(r).max(), np.abs(r).max() / p[3] * 100, np.sqrt((r ** 2).mean())), fontsize=9)
        ax.set_ylabel('Z (m)')
        res[ttl] = dict(A=round(float(p[2]), 2), B=round(float(p[3]), 2), max_dev=round(float(np.abs(r).max()), 3), pct=round(float(np.abs(r).max() / p[3] * 100), 2))
    if 'v15' in cfg and cfg['v15'].get('bkl'):
        import json as _json
        import mp8v6_previews3 as _P3
        n15, pan15, tabs15, st15 = _P3.user_panels(cfg['v15']['bkl'], cfg['v15']['adapter'], clip=True)
        A15 = np.vstack([np.frombuffer(v, dtype=np.float32).reshape(-1, 3).astype(float) for k, v in pan15])
        cl = _json.load(open(cfg['v15']['adapter']))['clip_lines'][0]
        s15 = (A15[:, 0] - cl['point'][0]) * cl['normal'][0] + (A15[:, 1] - cl['point'][1]) * cl['normal'][1]
        on = A15[(np.abs(s15) < 0.005) & (A15[:, 1] > 437) & (A15[:, 0] < 90)]
        vert = A15[(np.abs(A15[:, 0] - A15[:, 0].min()) < 0.006) & (A15[:, 1] > 437) & (A15[:, 0] < 10)]
        Pr = np.vstack([on, vert])
        xy = np.c_[Pr[:, 1], Pr[:, 2]]
        p, r = M.fit_ellipse_pts(xy)
        ax = axs[0, 2]
        ax.plot(on[:, 1], on[:, 2], 'k.', ms=4, label='egik kenar (kirpilmis panel koseleri)')
        ax.plot(vert[:, 1], vert[:, 2], '.', color='#1f77b4', ms=4, label='kapak: dik kenar (X = 0.65)')
        ax.plot(*ell_xy(p), 'r--', lw=1.2)
        ax.set_aspect('equal')
        ax.set_title('graf v15: SOL agiz, kirpilmis panel kenari (uctan gorunum)', fontsize=10)
        ax.set_ylim(-5, 46)
        ax.legend(fontsize=7, loc='lower center')
        ax.set_xlabel('Y (m)\nelips A %.2f x B %.2f m | en buyuk sapma %.2f m = %%%.1f B (rms %.2f)' % (p[2], p[3], np.abs(r).max(), np.abs(r).max() / p[3] * 100, np.sqrt((r ** 2).mean())), fontsize=9)
        res['v15_clipped_rim'] = dict(A=round(float(p[2]), 2), B=round(float(p[3]), 2), max_dev=round(float(np.abs(r).max()), 3), pct=round(float(np.abs(r).max() / p[3] * 100), 2), points_on_slanted_line=int(len(on)))
    # ---- row 1: see-through aperture (end-on)
    c = (473.0, 21.5)
    img = None
    if cfg.get('image5') and os.path.isfile(cfg['image5']):
        img = M.image_contour(cfg['image5'])
    for ax, key, ttl in ((axs[1, 0], 'before', 'GORUNEN DELIK (aperture) - graf v14: Gauss kubbesi kolu 2.9 m kaldiriyor'), (axs[1, 1], 'sigma70', 'SECENEK: Gauss Sigma X ust+alt = 70 (kopru kemeri daralir)')):
        if key not in cfg:
            ax.axis('off')
            continue
        U, ad = load(cfg[key])
        th, R, used = M.aperture_curves(U)
        rim_o, rimP = M.describe_curve(th, R[0], c)
        ap_o, apP = M.describe_curve(th, R.min(axis=0), c)
        pe, _ = M.fit_ellipse_pts(apP)
        ax.fill(rimP[:, 0], rimP[:, 1], color='0.90', label='agiz kesiti (X = 30)')
        ax.fill(apP[:, 0], apP[:, 1], color='#bcd7f2', label='gorunen delik')
        ax.plot(*ell_xy(pe), 'r--', lw=1.2, label='delige en iyi uyan elips')
        ax.plot(rimP[:, 0], rimP[:, 1], 'k-', lw=0.8)
        ax.set_aspect('equal')
        ax.set_title(ttl, fontsize=9.5)
        zb = [c[1] - R[i][int(np.argmin(np.abs(th + np.pi / 2)))] for i in range(len(used))]
        ax.set_ylim(-5, 46)
        ax.legend(loc='lower center', fontsize=7)
        ax.set_xlabel('Y (m)\ndelik yuksekligi %.1f m (agiz %.1f) | taban en fazla %.1f m yukselmis\nelipse sapma %.2f m = %%%.1f B (agiz kenari: %.2f m = %%%.1f B)' %(ap_o['height'], rim_o['height'], max(zb) - zb[0], ap_o['max_dev'], ap_o['max_dev_pct_B'], rim_o['max_dev'], rim_o['max_dev_pct_B']), fontsize=8.5)
        ax.set_ylabel('Z (m)')
        res['aperture_' + key] = dict(height=ap_o['height'], rim_height=rim_o['height'], bottom_lift=round(max(zb) - zb[0], 2), max_dev=ap_o['max_dev'], pct=ap_o['max_dev_pct_B'], rim_max_dev=rim_o['max_dev'], rim_pct=rim_o['max_dev_pct_B'], bottomB=ap_o['bottom']['B'], topB=ap_o['top']['B'])
        if key == 'before':
            res['aperture_before']['rms'] = ap_o['rms']
            res['aperture_before']['rim_rms'] = rim_o['rms']
    ax = axs[1, 2]
    if img is not None:
        pi = np.c_[-img[:, 0], -img[:, 1]]
        pe, r = M.fit_ellipse_pts(pi)
        s = 69.8 / (2 * pe[2])
        ax.plot((pi[:, 0] - pe[0]) * s, (pi[:, 1] - pe[1]) * s, 'k.', ms=3)
        ax.plot(*ell_xy((0, 0, pe[2] * s, pe[3] * s)), 'r--', lw=1.2)
        ax.set_aspect('equal')
        ax.set_title("Al'in ekran goruntusu (5.png): kontur", fontsize=9.5)
        top = pi[pi[:, 1] > pe[1]]
        bot = pi[pi[:, 1] <= pe[1]]
        qt, rt = M.fit_ellipse_pts(top)
        qb, rb = M.fit_ellipse_pts(bot)
        ax.set_xlabel('sol yari = kapak tarafi (tam elips), sag yari = birlesim tarafi; olcek: genislik 69.8 m\nelips sapmasi %.2f m = %%%.1f B, rms %.2f m | ust yari B %.1f m, alt yari B %.1f m' % (np.abs(r).max() * s, np.abs(r).max() / pe[3] * 100, np.sqrt((r ** 2).mean()) * s, qt[3] * s, qb[3] * s), fontsize=8.5)
        res['image5'] = dict(max_dev_m=round(float(np.abs(r).max() * s), 2), pct=round(float(np.abs(r).max() / pe[3] * 100), 1), rms_m=round(float(np.sqrt((r ** 2).mean()) * s), 2), top_B=round(float(qt[3] * s), 2), bottom_B=round(float(qb[3] * s), 2))
    else:
        ax.axis('off')
    fig.suptitle('Agiz elipsi: panel kenarlarindan olculen agiz (ust sira) ve ucta gorunen delik (alt sira)', fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out, dpi=70)
    plt.close(fig)
    return res


def panel_polys_plan(n, rh, tr):
    rc, tc = M.panel_corner_sets(n, rh, tr)
    polys = [c[:, :2] for c in rc] + [c[:, :2] for c in tc]
    kind = [0] * len(rc) + [1] * len(tc)
    return polys, kind


def fig_ends(cfg, out):
    P = M.footprint_outline(cfg['footprint'])
    fig, axs = plt.subplots(2, 2, figsize=(15, 11))
    stats = {}
    wins = (((-25, 100, 425, 515), 'sol uc - ince kanat'), ((-5, 105, 100, 170), 'sol kose - kalin kanat'))
    for j, (key, ttl) in enumerate((('before', 'ONCE (graf v14): X = 30 dik kesim'), ('proposal', 'ONERI (motor V3): STL egik cizgisinde kesim'))):
        n, rh, tr = M.bkl_to_user(cfg[key]['bkl'], cfg[key]['adapter'])
        polys, kind = panel_polys_plan(n, rh, tr)
        cen = np.array([p.mean(0) for p in polys])
        for i, (win, wname) in enumerate(wins):
            ax = axs[i, j]
            sel = [k for k in range(len(polys)) if win[0] - 8 <= cen[k, 0] <= win[1] + 8 and win[2] - 8 <= cen[k, 1] <= win[3] + 8]
            col = [(0.80, 0.86, 0.94) if kind[k] == 0 else (0.98, 0.78, 0.55) for k in sel]
            pc = PolyCollection([polys[k] for k in sel], facecolors=col, edgecolors='0.25', linewidths=0.6)
            ax.add_collection(pc)
            ax.plot(np.r_[P[:, 0], P[0, 0]], np.r_[P[:, 1], P[0, 1]], '-', color=RED, lw=2.0)
            ax.set_xlim(win[0], win[1])
            ax.set_ylim(win[2], win[3])
            ax.set_aspect('equal')
            ax.set_title('%s - %s' % (ttl, wname), fontsize=10)
            ax.set_xlabel('X (m)   kirmizi cizgi = Footprint_261014.stl')
            ntri = sum(1 for k in sel if kind[k] == 1)
            ax.text(0.02, 0.97, '%d panel, %d ucgen' % (len(sel), ntri), transform=ax.transAxes, va='top', fontsize=9, bbox=dict(fc='w', ec='0.6'))
            stats['%s_%s' % (key, 'thin' if i == 0 else 'thick')] = dict(panels=len(sel), triangles=ntri)
    fig.suptitle('Uc bolgesi: paneller (mavi = baklava, turuncu = ucgen) ve STL cizgisi; solda dik kesim (STL ucgeni boş), sagda egik kesim (STL cizgisine kadar)', fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out, dpi=70)
    plt.close(fig)
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outdir')
    ap.add_argument('--cfg', required=True)
    ap.add_argument('--only', default='plan,mouth,bridge,schema,ends')
    a = ap.parse_args()
    cfg = json.load(open(a.cfg))
    os.makedirs(a.outdir, exist_ok=True)
    res = {}
    only = a.only.split(',')
    if 'plan' in only:
        import mp8v6_previews3 as P3
        res['plan'] = P3.fig_plan_panels(cfg, os.path.join(a.outdir, 'V6_plan_once_sonra.png'))
    if 'bridge' in only:
        import mp8v6_previews2 as P2
        res['bridge'] = P2.fig_bridge(cfg, os.path.join(a.outdir, 'V6_kopru_kesit_alt_profil.png'), load)
    if 'schema' in only:
        import mp8v6_previews2 as P2
        P2.fig_schema(cfg, os.path.join(a.outdir, 'V6_gecis_uzunlugu_semasi.png'), cfg.get('measured_max_angle'))
    if 'ends' in only:
        import mp8v6_previews3 as P3
        res['ends'] = P3.fig_ends(cfg, os.path.join(a.outdir, 'V6_uc_ucgen_paneller.png'))
    if 'mouth' in only:
        res['mouth'] = fig_mouth(cfg, os.path.join(a.outdir, 'V6_agiz_elips_apertur.png'))
    json.dump(res, open(os.path.join(a.outdir, 'V6_numbers.json'), 'w'), indent=1, default=str)
    print(json.dumps(res, indent=1, default=str)[:4000])


if __name__ == '__main__':
    main()
