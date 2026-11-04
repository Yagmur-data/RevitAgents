#!/usr/bin/env python3
"""mp8v6_previews2.py - bridge section / underside profile and the 'Underside Transition Length' schematic for the v15 round (library of mp8v6_previews.py)."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import mp8v6_measure as M


def smooth_step(t):
    t = np.clip(t, 0, 1)
    return t ** 3 * (10 - 15 * t + 6 * t * t)


def fig_bridge(cfg, out, load):
    fig = plt.figure(figsize=(17, 10.5))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.15])
    res = {}
    # ---- top: bridge section at the middle (Y = 290): v14 ellipse vs v15 circle; foot sections
    for k, (key, ttl) in enumerate((('before', 'graf v14: kopru kesiti 27 x 22 m (elips)'), ('v15', 'graf v15: Bridge Section Height 0 = otomatik: 27 x 27 m (DAIRE)'))):
        ax = fig.add_subplot(gs[0, k])
        U, ad = load(cfg[key])
        P = M.slice_plane_y(U, 290.0)
        P = P[(P[:, 0] > 200) & (P[:, 0] < 280)]
        se = M.section_ellipse(U, 290.0)
        ax.plot(P[:, 0], P[:, 1], 'k.', ms=2.5)
        a_, b_ = se['A'], se['B']
        t_ = np.linspace(0, 2 * np.pi, 200)
        ax.plot(se['centre'][0] + a_ * np.cos(t_), se['centre'][1] + b_ * np.sin(t_), 'r--', lw=1.1)
        ax.set_aspect('equal')
        ax.set_title(ttl, fontsize=10)
        ax.set_xlabel('X (m)   Y = 290 kesiti\nen iyi elips: genislik %.2f m x yukseklik %.2f m, sapma %.2f m' % (2 * a_, 2 * b_, se['max_dev']), fontsize=9)
        res['section_' + key] = se
    ax = fig.add_subplot(gs[0, 2])
    U, ad = load(cfg['v15'])
    for y, col in zip((300, 400, 420), ('#1f77b4', '#2ca02c', '#d62728')):
        P = M.slice_plane_y(U, float(y))
        P = P[(P[:, 0] > 200) & (P[:, 0] < 280)]
        ax.plot(P[:, 0], P[:, 1], '.', color=col, ms=2, label='Y = %d' % y)
    ax.axhline(0, color='g', lw=1.2)
    ax.set_aspect('equal')
    ax.set_title('graf v15: ayaga dogru kesitler (tavan sabit, alt yuz yere iner: uzun elips)', fontsize=9.5)
    ax.legend(fontsize=8, loc='upper right')
    ax.set_xlabel('X (m)   yesil cizgi = zemin (z = 0)')
    # ---- bottom: underside profile along the bridge
    ax = fig.add_subplot(gs[1, :])
    curves = (('before', 'graf v14: S-egrisi 100 m, kesit 27 x 22', '0.35'), ('v15', 'graf v15 (exe ayni): S-egrisi 100 m, daire kesit', '#1f77b4'),
              ('ramp30', 'ONERI motor V3: sabit 30 derece rampa', '#d62728'), ('arc', 'ONERI motor V3: dairesel yay (kopru alt yuzu)', '#2ca02c'))
    for key, lab, col in curves:
        if key not in cfg:
            continue
        U, ad = load(cfg[key])
        r = M.foot_angles(U, y_lo=140.0, y_hi=446.0)
        ax.plot(r['Y'], r['z'], '-', color=col, lw=2.0, label=lab)
        Y = list(r['Y'])
        res['foot_' + key] = dict(thin=r['thin_foot'], thick=r['thick_foot'], z_wall_thin=round(float(r['z'][Y.index(438.0)]), 2), z_wall_thick=round(float(r['z'][Y.index(152.0)]), 2), crown=round(float(r['z'][Y.index(290.0)]), 2))
    ax.axhline(0, color='g', lw=1.5)
    for yw, nm in ((438, 'ince kanat duvari Y=438'), (152, 'kalin kanat duvari Y=152')):
        ax.axvline(yw, color='0.6', ls=':')
        ax.text(yw, 36, nm, rotation=90, va='top', ha='right', fontsize=8, color='0.4')
    ax.set_xlim(446, 140)
    ax.set_ylim(-2, 38)
    ax.set_xlabel('Y (m)  [kopru ekseni, ince kanattan (solda) kalin kanada (sagda)]')
    ax.set_ylabel('kopru alt yuzunun yuksekligi (m), X = 240 hatti')
    ax.legend(loc='lower center', fontsize=9, ncol=2)
    sub = res.get('foot_v15')
    if sub:
        ax.set_title('Alt yuz profili: ayaklar yere degiyor (z = 0). S-egrisinde egim 0 dan baslar (en dik %.0f derece), rampada her yerde ayni aci.' % sub['thin']['max_angle'], fontsize=10)
    fig.tight_layout()
    fig.savefig(out, dpi=70)
    plt.close(fig)
    return res


def fig_schema(cfg, out, measured=None):
    measured = measured or {}
    fig, axs = plt.subplots(1, 2, figsize=(17, 6.8), gridspec_kw=dict(width_ratios=[1.55, 1.0]))
    ax = axs[0]
    D = 29.0
    x = np.linspace(0, 160, 800)
    for L, col in ((80, '#d62728'), (100, '#1f77b4'), (140, '#2ca02c')):
        z = D * smooth_step(x / L)
        sl = np.degrees(np.arctan(np.gradient(z, x)))
        mt = measured.get(str(L))
        ax.plot(x, z, color=col, lw=2.2, label='Bridge foot blend length = %d m -> en dik %.0f derece (formul)%s' % (L, sl.max(), (', kabukta olculen %.0f' % mt) if mt else ''))
    ramp = np.minimum(np.tan(np.radians(30)) * x, 23.3)
    ramp = np.where(x > 23.3 / np.tan(np.radians(30)), np.minimum(23.3 + np.tan(np.radians(5)) * (x - 23.3 / np.tan(np.radians(30))), D), ramp)
    ax.plot(x, ramp, 'k--', lw=1.5, label='ONERI motor V3: sabit 30 derece rampa (%.0f m), sonra kopru alt yuzu' % (23.3 / np.tan(np.radians(30))))
    ax.axhline(0, color='g', lw=1.5)
    ax.axhline(D, color='0.5', ls=':')
    ax.text(158, D + 0.8, 'kopru alt yuzu (orta kisim)', fontsize=9, color='0.4', ha='right')
    ax.text(2, 1.2, 'ayak noktasi (zemin)', fontsize=9, color='g')
    ax.annotate('', xy=(100, -3.0), xytext=(0, -3.0), arrowprops=dict(arrowstyle='<->', color='#1f77b4'))
    ax.text(50, -5.6, 'GERCEK gecis uzunlugu = IN[46] "Bridge foot blend length" (80-140 m)', ha='center', fontsize=9.5, color='#1f77b4')
    ax.set_ylim(-7, 40)
    ax.set_xlim(-3, 160)
    ax.set_xlabel('ayaktan olculen mesafe (m)')
    ax.set_ylabel('alt yuz yuksekligi (m)')
    ax.legend(loc='center right', fontsize=8.5)
    ax.set_title('Alt yuz gecisi (yan gorunum): S-egrisi, baslangic ve bitiste egim 0 (kuintik)', fontsize=10.5)
    ax = axs[1]
    ax.axis('off')
    txt = ('"Underside Transition Length" (IN[19]) NEDIR?\n\n'
           '- Sadece bir ANAHTAR: 0 = alt yuz gecisi + KOPRU AYAKLARI tamamen kapali,\n'
           '  0 dan buyuk herhangi bir deger = acik. 100, 120 veya 160 yazmak sonucu DEGISTIRMEZ.\n\n'
           '- Gercek uzunluk: IN[46] "Bridge foot blend length" = 100 m (80-140).\n'
           '  Gecis S-seklinde: ayak noktasinda egim 0, ortada en dik, kopru altinda yine 0.\n'
           '  Daire kesitli kopruda alt yuz 29 m yukselir: ortalama egim 29 m / 100 m = 16 derece,\n'
           '  en dik yer 26 derece (80 m de 31, 140 m de 21). Eski 22 m kesitte 30 / 36 derece idi.\n\n'
           '- "Tam bir aci" ve "tam dairesel kopru" icin motor degisikligi gerekir (onerildi, derlenmedi):\n'
           '  * sabit aci rampasi (BRIDGE_FOOT_ANGLE, ornek 30 derece),\n'
           '  * ya da dairesel yay (kopru alt yuzu yaricapi ~370-400 m, ayakta ~20 derece).\n'
           '- Kesit: Bridge Section Height 0 = otomatik = genislik (27 m) -> orta kesit DAIRE\n'
           '  (graf v15, exe ayni).')
    ax.text(0.0, 1.0, txt, va='top', fontsize=10.5)
    fig.tight_layout()
    fig.savefig(out, dpi=70)
    plt.close(fig)
