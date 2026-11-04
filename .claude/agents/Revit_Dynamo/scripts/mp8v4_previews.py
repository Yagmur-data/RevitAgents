#!/usr/bin/env python3
"""mp8v4_previews.py - before / after preview PNGs for MashProject8_V4 (offline; no Revit).

  python mp8v4_previews.py OUTDIR --before-stl A.stl --after-stl B.stl [--before-bkl A.bkl --after-bkl B.bkl] [--label-before TXT --label-after TXT]

Writes into OUTDIR:
  V4_agiz_kesiti_elips.png          mouth loops (y = 30 front, y = 463 back) before / after with their best-fit ellipse and the deviation numbers
  V4_uctan_gorunum_once_sonra.png   end-on view along +y (like the user's screenshot) of the PANELS before / after   (needs --before-bkl/--after-bkl)
  V4_ayak_once_sonra.png            bridge underside along its centre line (left and right foot) + y-z sections at the arm walls x = 58 / 337, ground z = 0
Needs numpy / trimesh / matplotlib / Pillow and (for the end-on view) MashProject8/render_panels.py.
"""
import argparse
import os
import subprocess
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, HERE)
import mp8v4_measure as M   # noqa: E402


def mouth_figure(meshes, labels, out):
    fig, axs = plt.subplots(2, 2, figsize=(12.5, 8.2))
    for j, (m, lab) in enumerate(zip(meshes, labels)):
        for i, w in enumerate(('front', 'back')):
            ax = axs[i, j]
            lp = M.mouth_loop(m, w)
            r = M.mouth_report(m, w)
            e = M._ell_pts([r['xc'], r['zc'], r['A'], r['B'], 0.0])
            ax.plot(e[:, 0], e[:, 1], '--', color='#d02020', lw=1.4, label='best-fit ellipse (A %.1f x B %.1f m)' % (r['A'], r['B']))
            ax.plot(lp[:, 0], lp[:, 2], color='k', lw=2.0, label='shell mouth loop (y = %.1f)' % r['y_plane'])
            ax.axhline(0, color='g', lw=0.8)
            ax.text(0.5, 0.04, 'max deviation %.2f m = %.1f %% of B   (rms %.2f m)' % (r['max_dev_m'], r['max_dev_pct_B'], r['rms_dev_m']),
                    transform=ax.transAxes, ha='center', fontsize=10, bbox=dict(fc='w', ec='0.6'))
            ax.set_aspect('equal')
            ax.set_xlim(-30, 65)
            ax.set_ylim(-6, 50)
            ax.set_title('%s - %s mouth' % (lab, 'front (y 30)' if w == 'front' else 'back (y 463)'), fontsize=11)
            ax.legend(loc='upper right', fontsize=7)
            ax.set_xlabel('x (m)')
            ax.set_ylabel('z (m)')
    fig.tight_layout()
    fig.savefig(out, dpi=80)
    plt.close(fig)


def feet_figure(meshes, labels, out):
    cols = ['0.45', '#c02020']
    fig = plt.figure(figsize=(13, 9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.15])
    axl, axr = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    for k, (m, lab) in enumerate(zip(meshes, labels)):
        V = m.vertices
        for ax, xs in ((axl, np.arange(0, 150.1, 2.0)), (axr, np.arange(250, 400.1, 2.0))):
            bot = []
            for x in xs:
                y0 = float(M.yc(x)) if 60 < x < 337 else 250.0
                sel = (np.abs(V[:, 0] - x) < 0.6) & (np.abs(V[:, 1] - y0) < (0.6 if 60 < x < 337 else 4.0))
                bot.append(V[sel, 2].min() if sel.any() else np.nan)
            ax.plot(xs, bot, color=cols[k], lw=2.2, label=lab + ' - lowest z on the bridge centre line')
    for ax, xw, ttl in ((axl, 58.0, 'LEFT foot (arm wall x = 58)'), (axr, 337.0, 'RIGHT foot (arm wall x = 337)')):
        ax.axhline(0, color='g', lw=1.2)
        ax.axvline(xw, color='0.7', lw=0.8, ls=':')
        ax.set_ylim(-4, 36)
        ax.set_title(ttl)
        ax.set_xlabel('x (m)')
        ax.set_ylabel('underside z (m)   (ground = 0)')
        ax.legend(fontsize=7, loc='upper right' if xw < 100 else 'upper left')
    for j, (x0, ttl) in enumerate(((58.0, 'section at the LEFT arm wall x = 58'), (337.0, 'section at the RIGHT arm wall x = 337'))):
        ax = fig.add_subplot(gs[1, j])
        for k, (m, lab) in enumerate(zip(meshes, labels)):
            V = m.vertices
            s = V[np.abs(V[:, 0] - x0) < 0.5]
            ax.plot(s[:, 1], s[:, 2], '.', ms=2.0, color=cols[k], label='%s (lowest z %.2f m)' % (lab, s[:, 2].min()))
        ax.axhline(0, color='g', lw=1.2)
        ax.set_aspect('equal')
        ax.set_xlim(190, 310)
        ax.set_ylim(-4, 56)
        ax.set_title(ttl + '   (y-z plane)')
        ax.set_xlabel('y (m)')
        ax.set_ylabel('z (m)')
        ax.legend(fontsize=7, loc='upper right')
    fig.tight_layout()
    fig.savefig(out, dpi=75)
    plt.close(fig)


def endon_figure(bkls, labels, out_png, tmp):
    from PIL import Image, ImageDraw
    rp = os.path.join(ROOT, 'MashProject8', 'render_panels.py')
    ims = []
    for b, lab in zip(bkls, labels):
        t = os.path.join(tmp, 'endon_%s.png' % lab.split()[0])
        subprocess.run([sys.executable, '-I', rp, b, t, '--dir', '0', '1', '0', '--up', '0', '0', '1', '--box', '-30', '200', '0', '500', '-10', '70',
                        '--size', '1200', '640', '--title', lab], check=True, capture_output=True)
        ims.append(Image.open(t).convert('RGB'))
    w = max(i.width for i in ims)
    h = sum(i.height for i in ims)
    canvas = Image.new('RGB', (w, h), 'white')
    y = 0
    for i in ims:
        canvas.paste(i, (0, y))
        y += i.height
    canvas.save(out_png)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outdir')
    ap.add_argument('--before-stl', required=True)
    ap.add_argument('--after-stl', required=True)
    ap.add_argument('--before-bkl')
    ap.add_argument('--after-bkl')
    ap.add_argument('--label-before', default='BEFORE (MashProject8 saved values)')
    ap.add_argument('--label-after', default='AFTER (V4)')
    ap.add_argument('--tmp', default=os.environ.get('TEMP', '.'))
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    meshes = [M.load(a.before_stl), M.load(a.after_stl)]
    labels = [a.label_before, a.label_after]
    mouth_figure(meshes, labels, os.path.join(a.outdir, 'V4_agiz_kesiti_elips.png'))
    feet_figure(meshes, labels, os.path.join(a.outdir, 'V4_ayak_once_sonra.png'))
    if a.before_bkl and a.after_bkl:
        endon_figure([a.before_bkl, a.after_bkl], labels, os.path.join(a.outdir, 'V4_uctan_gorunum_once_sonra.png'), a.tmp)
    print('previews written to', a.outdir)


if __name__ == '__main__':
    main()
