#!/usr/bin/env python3
"""mp8v5_previews.py - preview PNGs for MashProject8_V5 (Al's new footprint Footprint_261014.stl), everything in the frame of THAT STL (offline; no Revit).

  python mp8v5_previews.py OUTDIR --after-stl A.stl --after-bkl A.bkl --after-adapter A.adapter.json --footprint Footprint_261014.stl
                           [--before-stl B.stl --before-dxdy DX DY] [--tmp DIR]

Writes OUTDIR/V5_plan_footprint_kabuk.png (plan: Al's outline + shell height, mouths, feet), V5_yan_gorunus_1.png (elevation along +Y, x-z), V5_uctan_gorunus_agiz.png (end view along +X into the
mouth at X = 30, y-z), V5_yan_gorunus_2_kopru.png (bridge profile along +X), V5_oblik.png, V5_agiz_kesiti_elips.png (both mouth loops + best-fit ellipse + deviation, before/after), V5_ayak_profili.png (underside along the bridge, ground z = 0, sections at both
junction walls, before/after). 'before' = the old V3/V4 default values on the same footprint (no inset, cap 24, exponents 3 / W 25, follow-arm 1).
Engine frame -> footprint frame: inverse of the adapter record's affine map (a, b, c, d, e, f) (see footprint_adapter.py).
"""
import argparse
import json
import os
import struct
import subprocess
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, HERE)
import mp8v4_measure as M          # noqa: E402
import make_footprint_v4 as FP4    # noqa: E402


def inv_xy(ad, x, y):
    """engine (x', y') -> footprint frame (X, Y) with the adapter record's affine map (a, b, c, d, e, f): transpose of the rotation."""
    m = ad['map']
    u, v = x - m[4], y - m[5]
    return m[0] * u + m[2] * v, m[1] * u + m[3] * v


def to_user(V, ad):
    W = V.copy()
    W[:, 0], W[:, 1] = inv_xy(ad, V[:, 0], V[:, 1])
    return W


def bkl_to_user(src, dst, ad):
    data = bytearray(open(src, 'rb').read())
    a = np.frombuffer(bytes(data[20:]), dtype='<f4').reshape(-1, 3).astype(np.float64)
    b = to_user(a, ad).astype('<f4')
    open(dst, 'wb').write(bytes(data[:20]) + b.tobytes())


def plan_figure(V, P, ad, out):
    U = to_user(V, ad)
    g = 1.0
    ix, iy = (U[:, 0] / g).astype(int), (U[:, 1] / g).astype(int)
    Z = np.full((iy.max() + 1, ix.max() + 1), np.nan)
    o = np.argsort(U[:, 2])
    Z[iy[o], ix[o]] = U[o, 2]
    fig, ax = plt.subplots(figsize=(10, 9.4))
    im = ax.imshow(Z, origin='lower', extent=[0, ix.max() + 1, 0, iy.max() + 1], cmap='viridis')
    ax.plot(np.r_[P[:, 0], P[0, 0]], np.r_[P[:, 1], P[0, 1]], 'k-', lw=1.6, label='Footprint_261014.stl outline')
    for xm, t in ((30.0, 'mouth X=30'), (450.0, 'mouth X=450')):
        ax.axvline(xm, color='r', ls='--', lw=1.0)
        ax.text(xm + 3, 8, t, color='r', rotation=90, fontsize=8)
    ax.annotate('thin wing (engine LEFT) foot Y~438', (240, 438), (300, 470), arrowprops=dict(arrowstyle='->', color='w'), color='w', fontsize=8)
    ax.annotate('thick wing (engine RIGHT) foot Y~152', (240, 152), (300, 120), arrowprops=dict(arrowstyle='->', color='w'), color='w', fontsize=8)
    ax.annotate('cap: shell extends beyond the STL edge (Y up to 508)', (120, 496), (130, 520), color='k', fontsize=8)
    ax.set_xlim(-10, 495)
    ax.set_ylim(-10, 530)
    ax.set_aspect('equal')
    ax.set_xlabel('X (m, Footprint_261014 frame)')
    ax.set_ylabel('Y (m)')
    ax.set_title('V5 shell on Al footprint: plan, colour = height z (m)')
    ax.legend(loc='lower right', fontsize=8)
    plt.colorbar(im, ax=ax, shrink=0.6, label='z (m)')
    fig.tight_layout()
    fig.savefig(out, dpi=75)
    plt.close(fig)


def render(bkl, out, args, title, size='1300 560'):
    rp = os.path.join(ROOT, 'MashProject8', 'render_panels.py')
    cmd = [sys.executable, '-I', rp, bkl, out] + args + ['--size'] + size.split() + ['--title', title]
    subprocess.run(cmd, check=True, capture_output=True)


def mouth_figure(after, before, ad_a, ad_b, out):
    fig, axs = plt.subplots(2, 2, figsize=(12.5, 8.2))
    for j, (m, ad, lab) in enumerate(((before, ad_b, 'BEFORE (V3/V4 defaults on the same footprint)'), (after, ad_a, 'AFTER (V5)'))):
        for i, w in enumerate(('front', 'back')):
            ax = axs[i, j]
            lp = M.mouth_loop(m, w)
            r = M.mouth_report(m, w)
            Yc = inv_xy(ad, lp[:, 0], lp[:, 1])[1]
            e = M._ell_pts([r['xc'], r['zc'], r['A'], r['B'], 0.0])
            Ye = inv_xy(ad, e[:, 0], np.full(len(e), r['y_plane']))[1]
            Xplane = inv_xy(ad, 0.0, r['y_plane'])[0]
            ax.plot(Ye, e[:, 1], '--', color='#d02020', lw=1.4, label='best-fit ellipse (A %.1f x B %.1f m)' % (r['A'], r['B']))
            ax.plot(Yc, lp[:, 2], 'k-', lw=2.0, label='shell mouth loop (X = %.1f)' % Xplane)
            ax.axhline(0, color='g', lw=0.8)
            ax.text(0.5, 0.04, 'max deviation %.2f m = %.1f %% of B   (rms %.2f m)' % (r['max_dev_m'], r['max_dev_pct_B'], r['rms_dev_m']), transform=ax.transAxes,
                    ha='center', fontsize=10, bbox=dict(fc='w', ec='0.6'))
            ax.set_aspect('equal')
            ax.set_xlim(430, 535)
            ax.set_ylim(-6, 50)
            ax.set_title('%s - mouth at X = %.0f' % (lab, Xplane), fontsize=10)
            ax.legend(loc='upper right', fontsize=7)
            ax.set_xlabel('Y (m)   [STL top edge = 484]')
            ax.set_ylabel('z (m)')
            ax.axvline(484.0, color='0.7', ls=':', lw=0.8)
    fig.tight_layout()
    fig.savefig(out, dpi=80)
    plt.close(fig)


def feet_figure(after, before, ad_a, ad_b, yc0, out):
    cols = ['0.45', '#c02020']
    fig = plt.figure(figsize=(13.5, 9.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.15])
    axl, axr = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    for k, (m, ad, lab) in enumerate(((before, ad_b, 'BEFORE'), (after, ad_a, 'AFTER (V5)'))):
        V = m.vertices
        xs = np.arange(20, 460, 2.0)
        bot = []
        for x in xs:
            sel = (np.abs(V[:, 0] - x) < 0.6) & (np.abs(V[:, 1] - yc0) < 1.0)
            bot.append(V[sel, 2].min() if sel.any() else np.nan)
        Y = inv_xy(ad, xs, np.full(len(xs), yc0))[1]
        bot = np.array(bot)
        for ax, lo, hi in ((axl, 380, 520), (axr, 60, 200)):
            s = (Y >= lo) & (Y <= hi)
            ax.plot(Y[s], bot[s], color=cols[k], lw=2.2, label=lab + ' - lowest z on the bridge centre line')
    for ax, yw, ttl, lo, hi in ((axl, 438.0, 'THIN-wing foot (engine LEFT): wall plane Y = 438', 380, 520), (axr, 152.0, 'THICK-wing foot (engine RIGHT): wall plane Y = 152', 60, 200)):
        ax.axhline(0, color='g', lw=1.2)
        ax.axvline(yw, color='0.7', ls=':')
        ax.set_ylim(-4, 36)
        ax.set_xlim(lo, hi)
        ax.set_title(ttl)
        ax.set_xlabel('Y (m)')
        ax.set_ylabel('underside z (m)   (ground = 0)')
        ax.legend(fontsize=7, loc='upper left')
    walls = ((438.0, 'section at the thin-wing wall plane Y = 438 (x-z plane)'), (152.0, 'section at the thick-wing wall plane Y = 152 (x-z plane)'))
    for j, (yw, ttl) in enumerate(walls):
        ax = fig.add_subplot(gs[1, j])
        for k, (m, ad, lab) in enumerate(((before, ad_b, 'BEFORE'), (after, ad_a, 'AFTER (V5)'))):
            V = m.vertices
            xw = ad['map'][4] - yw        # x' of the plane Y = yw (rotation +90: Y = e - x')
            s = V[np.abs(V[:, 0] - xw) < 0.5]
            X = inv_xy(ad, s[:, 0], s[:, 1])[0]
            ax.plot(X, s[:, 2], '.', ms=2.0, color=cols[k], label='%s (lowest z %.2f m)' % (lab, s[:, 2].min()))
        ax.axhline(0, color='g', lw=1.2)
        ax.set_aspect('equal')
        ax.set_xlim(150, 330)
        ax.set_ylim(-4, 56)
        ax.set_title(ttl)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('z (m)')
        ax.legend(fontsize=7, loc='upper right')
    fig.tight_layout()
    fig.savefig(out, dpi=75)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outdir')
    ap.add_argument('--after-stl', required=True)
    ap.add_argument('--after-bkl', required=True)
    ap.add_argument('--after-adapter', required=True)
    ap.add_argument('--footprint', required=True)
    ap.add_argument('--before-stl', required=True)
    ap.add_argument('--before-dxdy', nargs=2, type=float, default=[0.0, 9.4])
    ap.add_argument('--yc', type=float, default=249.4)
    ap.add_argument('--tmp', default=os.environ.get('TEMP', '.'))
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    ad = json.load(open(a.after_adapter))
    mb = list(ad['map'])
    mb[4] -= ad['dx'] - a.before_dxdy[0]
    mb[5] -= ad['dy'] - a.before_dxdy[1]
    ad_b = dict(ad, map=mb, dx=a.before_dxdy[0], dy=a.before_dxdy[1])
    M.configure(yc=a.yc, left_wall=ad['wall_x_engine'][0], right_wall=ad['wall_x_engine'][1])
    after, before = M.load(a.after_stl), M.load(a.before_stl)
    P, _, _ = FP4.loop_from_stl(a.footprint)
    P = P * 0.001
    plan_figure(after.vertices, P, ad, os.path.join(a.outdir, 'V5_plan_footprint_kabuk.png'))
    mouth_figure(after, before, ad, ad_b, os.path.join(a.outdir, 'V5_agiz_kesiti_elips.png'))
    feet_figure(after, before, ad, ad_b, a.yc, os.path.join(a.outdir, 'V5_ayak_profili.png'))
    ub = os.path.join(a.tmp, 'v5_user_frame.bkl')
    bkl_to_user(a.after_bkl, ub, ad)
    render(ub, os.path.join(a.outdir, 'V5_yan_gorunus_1.png'), ['--dir', '0', '1', '0', '--up', '0', '0', '1'], 'V5 side view 1: looking along +Y (x-z plane), panels', '1300 460')
    render(ub, os.path.join(a.outdir, 'V5_uctan_gorunus_agiz.png'), ['--dir', '1', '0', '0', '--up', '0', '0', '1', '--box', '0', '120', '-10', '520', '-10', '70'],
           'V5 end view into the mouth at X = 30: looking along +X (y-z plane), panels X<120', '1300 560')
    render(ub, os.path.join(a.outdir, 'V5_yan_gorunus_2_kopru.png'), ['--dir', '1', '0', '0', '--up', '0', '0', '1', '--box', '0', '480', '140', '450', '-10', '70'],
           'V5 side view 2: bridge profile, looking along +X (y-z plane), panels with Y 140..450 (both feet at the ends)', '1300 420')
    render(ub, os.path.join(a.outdir, 'V5_oblik.png'), ['--dir', '-0.45', '0.75', '-0.5', '--up', '0', '0', '1'], 'V5 oblique view (panels)', '1300 900')
    print('previews written to', a.outdir)


if __name__ == '__main__':
    main()
