"""mp8v6_make_node.py - builds ForDynamo/baklava-panels/MashProject8_v15.py (the node of graph v15) from MashProject8_v14.py (copy-first; v14 stays untouched).

v15 = v14 + (engine exe unchanged, tag MASHPROJECT8_BAKLAVA_V2):
  - adapter FPAD3 (footprint_adapter.py block replaced): the shell is cut 0.6 m beyond the wing ends (was 30 m), the wing ends are squared in the polygon (short 4 m tab), the two bevel lines of the
    thin wing are put into the adapter record (clip_lines)
  - panel_clip.py block: the node clips every panel that crosses a bevel line (exact straight slanted end = the STL 'triangular transitions'; the thick wing corners come back by the shorter cut)
    new input IN[53] 'Clip the thin-wing ends to the STL slanted outline' (default True)
  - bridge foot narrowing default 0 (v14: 0.35 pulled the straight corridor edges up to 4.4 m inward near both feet = Al's 'caves in and comes back'); warning when > 0.05
  - Bridge Section Height 0 = AUTOMATIC = CIRCULAR section (height = bridge width = corridor width, exponent 2)
  - data.v6 block (circle / narrowing / transition switch + the real transition length input / ends clip statistics)
Run after EVERY edit of footprint_adapter.py, panel_clip.py or this script, then mp8v6_make_graph.py (the graph embeds the node code)."""
ROOT = r'C:\Users\user\Desktop\Claude Projects'
src = ROOT + r'\ForDynamo\baklava-panels\MashProject8_v14.py'
dst = ROOT + r'\ForDynamo\baklava-panels\MashProject8_v15.py'
SCRIPTS = ROOT + r'\.claude\agents\Revit_Dynamo\scripts'
s = open(src, encoding='utf-8', newline='').read()
MK0, MK1 = '# ==== FOOTPRINT ADAPTER BEGIN ====', '# ==== FOOTPRINT ADAPTER END ===='
CK0, CK1 = '# ==== PANEL CLIP BEGIN ====', '# ==== PANEL CLIP END ===='


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:90], s.count(old))
    s = s.replace(old, new)


# ---- adapter block (FPAD3) + clip block ------------------------------------------------------------------------------------------
ad = open(SCRIPTS + r'\footprint_adapter.py', encoding='utf-8', newline='').read()
block = ad[ad.index(MK0):ad.index(MK1) + len(MK1)]
cl = open(SCRIPTS + r'\panel_clip.py', encoding='utf-8', newline='').read()
cblock = cl[cl.index(CK0):cl.index(CK1) + len(CK1)]
i0, i1 = s.index(MK0), s.index(MK1) + len(MK1)
s = s[:i0] + block + '\n\n\n# ---------------------------------------------------------------------------------------------------------------\n' \
    '# panel clip (verbatim copy of the block in Revit_Dynamo/scripts/panel_clip.py; the selftest compares both texts)\n' \
    '# ---------------------------------------------------------------------------------------------------------------\n' + cblock + s[i1:]

# ---- names / header ----------------------------------------------------------------------------------------------------------------
rep("GRAPH = 'MashProject8_v14'", "GRAPH = 'MashProject8_v15'")
rep("# The base shell element (ApplicationId Dynamo.STL.GaussShell, key IN[18]) is only touched when IN[26] AND IN[27] are True.",
    """#   V6 (this graph = MashProject8_v15; engine exe unchanged): (1) the thin-wing ends of the STL are SLANTED (30 deg): the adapter (FPAD3) cuts the shell only 0.6 m beyond the wing ends (the engine squares the
#   ends) and the node CLIPS every panel that crosses the two bevel lines (panel_clip block: exact straight slanted edge); IN[53] switches this on / off (default True). The shell element (IN[27]) is not clipped.
#   (2) IN[49] bridge foot narrowing default 0 (0.35 pulled the straight corridor edges up to 4.4 m inward near both feet). (3) IN[2] Bridge Section Height 0 = AUTOMATIC = CIRCULAR section (height = bridge
#   width, exponent 2). (4) IN[19] 'Underside Transition' is only a SWITCH (0 = whole transition block incl. the feet off, > 0 = on); the real length is IN[46]. A constant-angle ramp / circular arc underside
#   needs an engine change (proposal in MashProject8/_motor_v3_onerisi, not built).
# The base shell element (ApplicationId Dynamo.STL.GaussShell, key IN[18]) is only touched when IN[26] AND IN[27] are True.""")

# ---- generate(): section height 0 = automatic circle, narrowing default 0 --------------------------------------------------------------
rep("    if any(measures[i] <= 0 for i in (0, 3, 4)) or measures[1] < 0:", "    if any(measures[i] <= 0 for i in (3, 4)) or measures[0] < 0 or measures[1] < 0:")
rep("    settings['BRIDGE_FOOT_NARROW'] = float(arg(49, 0.35))", "    settings['BRIDGE_FOOT_NARROW'] = float(arg(49, 0.0))")
rep("    FOOTPRINT_INFO.update(_info)\n    clamp_setting(settings, 'END_TAPER_LENGTH'",
    """    FOOTPRINT_INFO.update(_info)
    # V6: Bridge Section Height 0 = automatic = CIRCULAR section (height = bridge width, exponent 2)
    if settings['KOPRU_YUKSEKLIGI'] <= 0:
        settings['KOPRU_YUKSEKLIGI'] = float(settings['KOPRU_GENISLIGI'])
        FOOTPRINT_INFO['bridge_height_automatic'] = True
    FOOTPRINT_INFO['bridge_height_m'] = settings['KOPRU_YUKSEKLIGI']
    if abs(settings['KOPRU_YUKSEKLIGI'] - settings['KOPRU_GENISLIGI']) < 0.05 and abs(settings['BRIDGE_SECTION_EXP'] - 2.0) < 1e-9:
        FOOTPRINT_INFO['bridge_section'] = 'circle: height = width = %.1f m, exponent 2 (at the middle of the bridge; the feet stay tall because the roof is fixed and the underside lands on the ground)' % settings['KOPRU_GENISLIGI']
    else:
        FOOTPRINT_INFO['bridge_section'] = 'NOT a circle: %.1f m wide x %.1f m high, exponent %.1f (Bridge Section Height 0 = automatic circle)' % (settings['KOPRU_GENISLIGI'], settings['KOPRU_YUKSEKLIGI'], settings['BRIDGE_SECTION_EXP'])
    if settings['BRIDGE_FOOT_NARROW'] > 0.05:
        INPUT_WARNINGS.append('Bridge foot narrowing %.2f pulls the corridor edges inward near both feet (up to about %.1f m on each side, over the foot blend length): the model leaves the STL outline there. 0 = straight corridor edges.'
                              % (settings['BRIDGE_FOOT_NARROW'], settings['KOPRU_GENISLIGI'] * settings['BRIDGE_FOOT_NARROW'] / 2.0))
    clamp_setting(settings, 'END_TAPER_LENGTH'""")

# ---- run(): clip the panels ----------------------------------------------------------------------------------------------------------
rep("""        if len(panels) != summary.get('panels_total'):
            raise ValueError('Panel file count %d differs from the engine report %s.' % (len(panels), summary.get('panels_total')))
        groups = group_panels(panels, group_size, panel_edge)""",
    """        if len(panels) != summary.get('panels_total'):
            raise ValueError('Panel file count %d differs from the engine report %s.' % (len(panels), summary.get('panels_total')))
        clip_lines = ADAPTER.get('clip_lines') or []
        if clip_lines and bool(arg(53, True)):
            panels, clip_stats = clip_panels(panels, {0: rhombus_triangles(n_sub or 4), 1: triangle_triangles(n_sub or 4)}, clip_lines)
            clip_stats['lines'] = len(clip_lines)
            clip_stats['note'] = 'panels crossing the two slanted end lines of the thin wing were clipped to them (straight edge on the STL outline); untouched panels are unchanged'
            data['ends_clip'] = clip_stats
            if clip_stats['partial'] + clip_stats['removed'] == 0:
                INPUT_WARNINGS.append('Slanted-end clipping is ON but no panel crossed the bevel lines (check the footprint / Footprint STL selection).')
        elif clip_lines:
            data['ends_clip'] = {'switch': 'OFF (IN[53] = False)', 'lines': len(clip_lines)}
            INPUT_WARNINGS.append('Clipping of the thin-wing ends to the STL slanted outline is OFF: the wing ends are straight cuts and overshoot the STL outline (about %d m2 per end).'
                                  % int(0.5 * float(ADAPTER.get('bevel_len_m') or 0.0) * float(ADAPTER.get('thin_wing_depth_m') or 0.0)))
        groups = group_panels(panels, group_size, panel_edge)""")
rep("""        data['panel_counts'] = {'rhombus': summary['rhombus_panels'], 'triangle': summary['triangle_panels'],
                                'revit_elements': len(groups)}""",
    """        data['panel_counts'] = {'rhombus': summary['rhombus_panels'], 'triangle': summary['triangle_panels'],
                                'revit_elements': len(groups), 'panels_after_end_clip': len(panels)}""")

# ---- geometry builder + element naming for clipped panels (kind 2 / 3 = clipped rhombus / triangle patch: plain triangle list) --------------
rep("""        for (a, b, c) in tri_tables[kind]:
            face = TessellatedFace(Array[XYZ]([xyz[a], xyz[b], xyz[c]]), mats[kind])""",
    """        table = tri_tables[kind] if kind < 2 else [(3 * q, 3 * q + 1, 3 * q + 2) for q in range(len(v) // 9)]
        for (a, b, c) in table:
            face = TessellatedFace(Array[XYZ]([xyz[a], xyz[b], xyz[c]]), mats[kind & 1])""")
rep("                kinds = set(panels[i][0] for i in idxs)", "                kinds = set(panels[i][0] & 1 for i in idxs)")

# ---- data.v6 -----------------------------------------------------------------------------------------------------------------------------
rep("    for _w in (report.get('Warnings') or []):\n        if _w not in INPUT_WARNINGS:",
    """    data['v6'] = {'bridge_section': FOOTPRINT_INFO.get('bridge_section'), 'bridge_foot_narrowing': float(arg(49, 0.0)), 'underside_transition_switch': 'on' if float(arg(19, 100.0)) > 0 else 'OFF (the whole transition block incl. the feet is off)',
                  'underside_transition_real_length_m': float(arg(46, 100.0)) if float(arg(19, 100.0)) > 0 else 0.0,
                  'thin_wing_end_clip': 'ON' if bool(arg(53, True)) and ADAPTER.get('clip_lines') else ('OFF' if ADAPTER.get('clip_lines') else 'not needed (square wing ends / no adapter)'),
                  'note': 'Underside Transition Length (IN[19]) is only an on/off switch; the real transition length is Bridge foot blend length (IN[46]), a smooth S-curve (steepest about 26 deg at 100 m with the circular section, 36 deg at 80 m with the 22 m section).'}
    for _w in (report.get('Warnings') or []):
        if _w not in INPUT_WARNINGS:""")
open(dst, 'w', encoding='utf-8', newline='').write(s)
print('wrote', dst, len(s), 'chars')
