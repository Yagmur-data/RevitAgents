#!/usr/bin/env python3
"""mp8v6_adapter_v3.py - PROPOSAL adapter for engine V3 (needs the patched engine of mp8v6_engine_patch.py; NOT used by graph v15, which runs with the V2 exe).

Idea: the shell reaches the footprint outline exactly. The thin wing is extended rectangularly beyond its (slanted) ends so that the engine's 30 m end zone lies outside
the footprint, the engine frame is kept (KEEP_Y_ORIGIN: y' is not re-normalised), and the engine cuts the thin wing with the SLANTED planes of the footprint's own end
bevels (SLANT_CUTS). The thick wing needs no cut at all (its boundary is already the footprint outline).

  python mp8v6_adapter_v3.py FOOTPRINT.stl OUT_DIR      -> OUT_DIR/<stem>.engine3_<md5-8>.stl + .adapter.json (+ prints the engine settings to add)

Reuses footprint_adapter.py (FPAD2) for reading/recognising the outline; the polygon construction below is build_engine_polygon with the end handling replaced.
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import footprint_adapter as FA  # noqa: E402

ADAPTER3 = 'FPAD3'
CUT_FROM_END_V3 = 30.0   # engine V3 proposal: the polygon is extended so that the engine's usual 30 m end zone lies outside the footprint (FPAD2 value; FPAD3 of the node uses 0.6 m + panel clip)
MARGIN = 5.0          # m between the vertical cut line and the extended slanted line (the vertical cut must stay outside the footprint)


def build_polygon_v3(P, lay, jog=20.0):
    m = lay['map']
    Q = [FA.apply_map(m, p[0], p[1]) for p in lay['Pu']]
    ymin = min(q[1] for q in Q)
    Q = [(q[0], q[1] - ymin) for q in Q]
    wall_l, wall_r = lay['thin_depth'], lay['thin_depth'] + lay['corridor_len']
    cc = 0.5 * (lay['corridor_lo'] + lay['corridor_hi'])
    yc = FA.apply_map(m, cc, 0.0)[1] - ymin if lay['axis'] == 'y' else FA.apply_map(m, 0.0, cc)[1] - ymin
    dy = round(FA.ENGINE_MID_Y - yc, 3)
    Q = [(q[0], q[1] + dy) for q in Q]
    w0 = lay['thin_depth']
    inset = round(max((w0 - FA.CAP_LEGACY) / 2.0, 0.0), 3)
    dx_sym = (FA.ENGINE_FOOT_L + FA.ENGINE_FOOT_R - wall_l - wall_r) / 2.0
    dx = round(max(min(dx_sym, FA.REF_X_START - FA.EDGE_MARGIN - inset), 0.0), 3)
    if inset + dx > FA.REF_X_START - 0.5:
        raise FA.AdapterError('The thin wing is too deep (%.1f m) for the engine radius sampling.' % w0)
    lows = [i for i, q in enumerate(Q) if abs(q[0]) < 1e-6]
    if len(lows) != 2:
        raise FA.AdapterError('Expected two outer-edge corners of the thin wing, got %d.' % len(lows))
    n = len(Q)
    i_lo = min(lows, key=lambda i: Q[i][1])
    i_hi = max(lows, key=lambda i: Q[i][1])
    if (i_hi + 1) % n != i_lo:
        raise FA.AdapterError('Outer-edge corners are not consecutive (outline orientation).')
    # true bevel lines in the engine frame (before the anchor tabs): outer corner (dx, y_o), inner corner (wall_l + dx, y_i)
    inner_lo, inner_hi = (i_lo + 1) % n, (i_hi - 1) % n
    A_lo, B_lo = (dx, Q[i_lo][1]), (wall_l + dx, Q[inner_lo][1])
    A_hi, B_hi = (dx, Q[i_hi][1]), (wall_l + dx, Q[inner_hi][1])
    Q = [(q[0] + dx if abs(q[0]) > 1e-6 else 0.0, q[1]) for q in Q]
    tot_inset = inset + dx
    cap = w0 - inset
    x_tip = tot_inset - cap                                  # the shell's cap reaches x' = x_tip (outside the footprint edge)
    slope_lo = (B_lo[1] - A_lo[1]) / (B_lo[0] - A_lo[0])
    slope_hi = (B_hi[1] - A_hi[1]) / (B_hi[0] - A_hi[0])
    y_tip_lo = A_lo[1] + (x_tip - A_lo[0]) * slope_lo       # lowest y' of the slanted line over the shell's x' range
    y_tip_hi = A_hi[1] + (x_tip - A_hi[0]) * slope_hi
    uc = CUT_FROM_END_V3
    y_end_lo = math.floor((min(y_tip_lo, 0.0) - MARGIN - uc) / 5.0) * 5.0
    y_end_hi = math.ceil((max(y_tip_hi, 2 * FA.ENGINE_MID_Y) + MARGIN + uc) / 5.0) * 5.0
    # polygon: replace both bevels by straight ends at y_end_lo / y_end_hi (inner wall line continues, outer corners stay as x' = 0 anchor tabs)
    Q = list(Q)
    Q[i_lo] = (0.0, y_end_lo)
    Q[inner_lo] = (wall_l + dx, y_end_lo)
    Q[i_hi] = (0.0, y_end_hi)
    Q[inner_hi] = (wall_l + dx, y_end_hi)
    new = []
    for i in range(n):
        new.append(Q[i])
        if i == i_hi:
            new += [(0.0, y_end_hi - jog), (tot_inset, y_end_hi - jog), (tot_inset, y_end_lo + jog), (0.0, y_end_lo + jog)]
    Q = new
    if not FA._is_simple(Q):
        raise FA.AdapterError('The engine-frame polygon is not simple.')
    st = min(range(len(Q)), key=lambda i: (-Q[i][0], Q[i][1]))
    Q = Q[st:] + Q[:st]
    full = (m[0], m[1], m[2], m[3], m[4] + dx, m[5] - ymin + dy)

    def cut(A, B, keep_up):
        d = (B[0] - A[0], B[1] - A[1])
        ln = math.hypot(*d)
        nx, ny = (-d[1] / ln, d[0] / ln)
        if (ny > 0) != keep_up:
            nx, ny = -nx, -ny
        return {'origin': [round(A[0], 3), round(A[1], 3)], 'normal': [round(nx, 6), round(ny, 6)]}
    info = {'adapter': ADAPTER3, 'axis': lay['axis'], 'map': list(full), 'dx': dx, 'dy': dy, 'inset_m': inset, 'cap_depth_m': cap, 'uc_kesim_payi': uc,
            'engine_y_range': [y_end_lo, y_end_hi], 'slant_cuts': [cut(A_lo, B_lo, True), cut(A_hi, B_hi, False)], 'slant_split_x': 200.0, 'keep_y_origin': True, 'bridge_foot_wall_x': [wall_l + dx, wall_r + dx],
            'bevel_angle_deg': round(math.degrees(math.atan(abs(slope_lo))), 2), 'bevel_len_m': lay['bevel_len'], 'y_tip': [round(y_tip_lo, 3), round(y_tip_hi, 3)],
            'corridor_width_m': lay['corridor_width'], 'thin_wing_depth_m': lay['thin_depth'], 'thick_wing_depth_m': lay['thick_depth']}
    return Q, info


def derive_v3(path, out_dir):
    md5 = hashlib.md5(open(path, 'rb').read()).hexdigest()
    P, zb, zt = FA.read_outline(path)
    lay = FA.analyze(P)
    Q, info = build_polygon_v3(P, lay)
    stem = os.path.splitext(os.path.basename(path))[0]
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, '%s.engine3_%s.stl' % (stem, md5[:8]))
    cnt = FA.write_engine_stl(out, Q, 'MashProject8 engine-frame footprint V3 of %s (%s, %s)' % (os.path.basename(path), md5[:8], ADAPTER3))
    info.update(source=os.path.basename(path), source_md5=md5, stl_triangles=cnt)
    json.dump(info, open(os.path.splitext(out)[0] + '.adapter.json', 'w'), indent=1)
    return out, info


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    o, i = derive_v3(sys.argv[1], sys.argv[2])
    print('wrote', o)
    print(json.dumps(i, indent=1))
