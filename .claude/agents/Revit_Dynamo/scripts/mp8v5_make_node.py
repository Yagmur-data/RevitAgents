"""mp8v5_make_node.py - rebuilds ForDynamo/baklava-panels/MashProject8_v14.py (the node of graph v14) from MashProject8_v13.py + the adapter block of footprint_adapter.py (copy-first; v13 stays).
Run after EVERY edit of footprint_adapter.py, then mp8v5_make_graph.py (the graph embeds the node code)."""
import re
ROOT = r'C:\Users\user\Desktop\Claude Projects'
src = ROOT + r'\ForDynamo\baklava-panels\MashProject8_v13.py'
dst = ROOT + r'\ForDynamo\baklava-panels\MashProject8_v14.py'
ad = open(ROOT + r'\.claude\agents\Revit_Dynamo\scripts\footprint_adapter.py', encoding='utf-8').read()
b = ad.index('# ==== FOOTPRINT ADAPTER BEGIN ====')
e = ad.index('# ==== FOOTPRINT ADAPTER END ====') + len('# ==== FOOTPRINT ADAPTER END ====')
block = ad[b:e]
s = open(src, encoding='utf-8', newline='').read()


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:90], s.count(old))
    s = s.replace(old, new)


# ---- names / header ------------------------------------------------------------------------------------------------------------
rep("GRAPH = 'MashProject8_v13'", "GRAPH = 'MashProject8_v14'")
rep("SOL_C_DERINLIGI = 35.0  # Sol tarafa dogru eliptik kapanma derinligi (metre). IN[51] 'Left outer cap depth'; 35.0 + the V5 engine-frame Footprint.stl = ONE ellipse at the mouth (old shapes: 24.0 / V4 footprint 35.09)",
    "SOL_C_DERINLIGI = 24.0  # Sol tarafa dogru eliptik kapanma derinligi (metre; eski sabit). IN[51] 'Left outer cap depth': 0 = AUTOMATIC (derived from the footprint outline: (arm width + 24) / 2 = one ellipse at the mouth)")
rep("#   (and the optional shell) BACK into the frame of Footprint_261014.stl before anything reaches Revit. 52 = 'Old model key to delete after writing' (empty = keep); IN[18] default key GAUSS_KABUK_03.",
    """#   (and the optional shell) BACK into the frame of Footprint_261014.stl before anything reaches Revit. 52 = 'Old model key to delete after writing' (empty = keep); IN[18] default key GAUSS_KABUK_03.
#   V5b (this graph = MashProject8_v14, v13 REFUSED Al's own STL - wrong product decision): the user selects HIS OWN footprint STL (Footprint_261014.stl, raw, in his own frame) and the node derives the
#   engine-frame footprint AT RUN TIME (embedded footprint_adapter block: recognises the I layout - corridor, thin wing, thick wing, fillet arcs - from the outline and computes the rotation, dx / dy shifts,
#   cap depth, inset, cut distance, corridor width and foot height compensation from the measures), writes it to <result folder>\\_engine_footprint\\<name>.engine_<md5-8>.stl (+ .adapter.json), runs the engine on
#   it and maps the results back. Known old footprints (md5) pass unchanged; a file with an adapter sidecar (the v13 package files, make_footprint_v5 output) is used as is; anything else that does not fit the
#   I layout stops with the measured values. IN[51] = 0 and IN[3] = 0 mean AUTOMATIC (cap depth / bridge width from the outline); foot heights IN[47] / IN[48] are TRUE heights above ground (0 = touches the ground);
#   the node adds the calibration offset itself.""")

# ---- generate(): bridge width may be 0 (= automatic) ------------------------------------------------------------------------------
rep("    if any(measures[i] <= 0 for i in (0, 1, 3, 4)):", "    if any(measures[i] <= 0 for i in (0, 3, 4)) or measures[1] < 0:")
# ---- generate(): cap depth input 0 = automatic ---------------------------------------------------------------------------------------
rep("    settings['SOL_C_DERINLIGI'] = float(arg(51, SOL_C_DERINLIGI))\n", "    cap_in = float(arg(51, 0.0))\n    settings['SOL_C_DERINLIGI'] = cap_in if cap_in > 0 else SOL_C_DERINLIGI\n")
rep("    clamp_setting(settings, 'SOL_C_DERINLIGI', 5.0, 80.0, 'Left outer cap depth')\n", "")
rep("""    FOOTPRINT_INFO.clear()
    FOOTPRINT_INFO.update(footprint_check(footprint, settings['SOL_C_DERINLIGI']))
    if ADAPTER.get('uc_kesim_payi'):
        settings['UC_KESIM_PAYI'] = float(ADAPTER['uc_kesim_payi'])     # end-cut planes: 30 m from the ends of the user's wings
""", """    derived_dir = os.path.join(result_folder() or temp_dir, '_engine_footprint')
    FOOTPRINT_INFO.clear()
    engine_footprint, _info = prepare_footprint(footprint, derived_dir, settings, cap_in, float(settings['KOPRU_GENISLIGI']))
    FOOTPRINT_INFO.update(_info)
""")
rep("    command = [executable, '--footprint', footprint, '--settings', settings_path, '--output-dir', temp_dir]", "    command = [executable, '--footprint', engine_footprint, '--settings', settings_path, '--output-dir', temp_dir]")
rep("""'v5': dict(FOOTPRINT_INFO, mouth_section='one ellipse when footprint + cap depth + exponents 2 + corner width 27 belong together',""",
    """'v5': dict(FOOTPRINT_INFO, mouth_section='one ellipse when cap depth = (arm width + 24) / 2 (automatic) with exponents 2 + corner width 27',""")

# ---- adapter block + preparation -----------------------------------------------------------------------------------------------
a = s.index("# ---------------------------------------------------------------------------------------------------------------\n# footprint pairing + V5 frame adapter")
b2 = s.index("# ---------------------------------------------------------------------------------------------------------------\n# engine\n")
new_block = '''# ---------------------------------------------------------------------------------------------------------------
# footprint adapter (verbatim copy of the block in Revit_Dynamo/scripts/footprint_adapter.py; the selftest compares both texts)
# ---------------------------------------------------------------------------------------------------------------
''' + block + '''

FOOTPRINT_MD5_ORIGINAL = '0ab5f6f319b67cc3990c0873fa543db2'      # Footprint.stl of MashProject8 .. MashProject8_Paylas_V3 (old 'H', bridge along x)
FOOTPRINT_MD5_V4 = '47bb7ac1ec0eef06bfe96a0c0d0e77aa'            # Footprint.stl of MashProject8_Paylas_V4
FOOTPRINT_INFO = {}
ADAPTER = {}
DEFAULT_BRIDGE_WIDTH = 30.545975490214516                        # the old graphs' Bridge Width


def _normalise_sidecar(d):
    """adapter record -> dict with 'map' = (a, b, c, d, e, f). v13 sidecars (xmin, ymax, dx, dy) are converted: x' = Ymax - Y + dx, y' = X - Xmin + dy."""
    d = dict(d)
    if 'map' not in d:
        for k in ('xmin', 'ymax', 'dx', 'dy'):
            if k not in d:
                raise ValueError('The footprint adapter file is incomplete (' + k + ' missing).')
        d['map'] = [0.0, -1.0, 1.0, 0.0, d['ymax'] + d['dx'], -d['xmin'] + d['dy']]
    return d


def to_user_frame(x, y):
    """engine frame (x', y') -> the frame of the user's footprint STL (X, Y). Rotation + translation, determinant +1: triangle winding is unchanged."""
    return invert_map(ADAPTER['map'], x, y)


def panels_to_user_frame(panels):
    """new list of (kind, array('f')) with every vertex mapped back (z unchanged)."""
    out = []
    for kind, v in panels:
        w = array.array('f', v)
        for k in range(0, len(w), 3):
            w[k], w[k + 1] = to_user_frame(v[k], v[k + 1])
        out.append((kind, w))
    return out


def prepare_footprint(path, derived_dir, settings, cap_in, width_in):
    """Decide how the selected footprint reaches the engine. Returns (engine_footprint_path, info); sets the adapter, the cap depth, the bridge width, UC_KESIM_PAYI and the foot compensation.
    1) an adapter sidecar next to the file (v13 package files / footprint_adapter output): used as is;  2) a known old footprint (md5): unchanged;
    3) anything else: recognised as the I layout and DERIVED here (written to derived_dir); a file that does not fit stops with the measured values."""
    md5 = hashlib.md5(open(path, 'rb').read()).hexdigest()
    ADAPTER.clear()
    side = os.path.splitext(path)[0] + '.adapter.json'
    engine_fp = path
    info = {'md5': md5, 'file': os.path.basename(path)}
    if os.path.isfile(side):
        with io.open(side, encoding='utf-8-sig') as fh:
            ADAPTER.update(_normalise_sidecar(json.load(fh)))
        info['variant'] = 'engine-frame footprint with an adapter record (source: %s)' % ADAPTER.get('source')
    elif md5 in (FOOTPRINT_MD5_ORIGINAL, FOOTPRINT_MD5_V4):
        info['variant'] = 'original old footprint (H layout, used unchanged)' if md5 == FOOTPRINT_MD5_ORIGINAL else 'V4 footprint (H layout, used unchanged)'
    else:
        target = derived_dir
        try:
            if not os.path.isdir(target):
                os.makedirs(target)
        except OSError:
            target = os.path.join(os.path.dirname(derived_dir), 'engine_footprint_tmp')
            os.makedirs(target)
        engine_fp, d = derive(path, target)
        ADAPTER.update(_normalise_sidecar(d))
        info['variant'] = 'derived at run time from %s (I layout recognised)' % os.path.basename(path)
        info['derived_footprint'] = engine_fp
    for w in ADAPTER.get('warnings', []):
        INPUT_WARNINGS.append(w)
    # cap depth: 0 = automatic
    auto_cap = float(ADAPTER['cap_depth_m']) if ADAPTER.get('cap_depth_m') else (35.09 if md5 == FOOTPRINT_MD5_V4 else CAP_LEGACY)
    if cap_in > 0:
        cap = cap_in
        settings['SOL_C_DERINLIGI'] = cap
        clamp_setting(settings, 'SOL_C_DERINLIGI', 5.0, 80.0, 'Left outer cap depth')
        cap = settings['SOL_C_DERINLIGI']
        if md5 == FOOTPRINT_MD5_ORIGINAL and cap > 30.0:
            INPUT_WARNINGS.append('Footprint is the ORIGINAL old one but the cap depth is %.2f m: the mouth is not an ellipse and the arms grow outward (set Left outer cap depth to 0 = automatic or 24).' % cap)
        elif md5 == FOOTPRINT_MD5_V4 and abs(cap - 35.09) > 1.5:
            INPUT_WARNINGS.append('Footprint is the V4 one (arm width 35.09 m at the mouth) but the cap depth is %.2f m: the mouth section is not a single ellipse (0 = automatic).' % cap)
        elif abs(cap - auto_cap) > 1.5:
            INPUT_WARNINGS.append('Left outer cap depth %.2f m differs from the %.2f m derived from this footprint (arm width = cap depth gives ONE ellipse at the mouth).' % (cap, auto_cap))
    else:
        cap = auto_cap
        settings['SOL_C_DERINLIGI'] = cap
    # bridge width: 0 = automatic (the corridor of the footprint)
    corr = ADAPTER.get('corridor_width_m')
    width = float(settings['KOPRU_GENISLIGI'])
    if width <= 0:
        width = float(corr) if corr else DEFAULT_BRIDGE_WIDTH
    elif corr and abs(width - corr) > 1.0:
        INPUT_WARNINGS.append('Bridge Width %.1f m differs from the corridor of the footprint (%.1f m): the bridge is widened / narrowed beyond the STL outline (0 = automatic).' % (width, corr))
    settings['KOPRU_GENISLIGI'] = width
    if ADAPTER.get('uc_kesim_payi'):
        settings['UC_KESIM_PAYI'] = float(ADAPTER['uc_kesim_payi'])         # end-cut planes: 30 m from the ends of the user's wings
    comp = ADAPTER.get('foot_height_comp_m')
    if comp:
        settings['BRIDGE_FOOT_HEIGHT_L'] = min(settings['BRIDGE_FOOT_HEIGHT_L'] + float(comp[0]), 30.0)
        settings['BRIDGE_FOOT_HEIGHT_R'] = min(settings['BRIDGE_FOOT_HEIGHT_R'] + float(comp[1]), 30.0)
        info['foot_height_compensation_m'] = list(comp)
    info.update(cap_depth_m=cap, cap_depth_automatic=cap_in <= 0, bridge_width_m=width, bridge_width_automatic=float(IN[3]) <= 0 if len(IN) > 3 and IN[3] is not None else True)
    if ADAPTER:
        for k in ('source', 'source_md5', 'axis', 'map', 'dx', 'dy', 'inset_m', 'thin_wing_width_at_cut_m', 'uc_kesim_payi', 'corridor_width_m', 'corridor_length_m', 'thin_wing_depth_m',
                  'thick_wing_depth_m', 'wall_x_engine', 'engine_stl_md5', 'adapter'):
            if k in ADAPTER:
                info[k] = ADAPTER[k]
    return engine_fp, info


'''
s = s[:a] + new_block + s[b2:]

rep("' [WARNING: %d slider value(s) clamped, see input_warnings]' % len(INPUT_WARNINGS)", "' [WARNING: %d warning(s), see input_warnings]' % len(INPUT_WARNINGS)")
open(dst, 'w', encoding='utf-8', newline='').write(s)
print('ok', len(s))
