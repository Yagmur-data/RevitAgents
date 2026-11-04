#!/usr/bin/env python3
"""mp8v6_engine_patch.py - builds the PROTOTYPE of engine V3 (tag MASHPROJECT8_BAKLAVA_V3) from MashProject8/Engine_Source.py (V2) by exact text patches.
Nothing is built into an exe by this script; the prototype runs as plain Python (mp8v6_run.py --engine DIR) for offline evidence only.

  python mp8v6_engine_patch.py SRC_Engine_Source.py OUT_Engine_Source.py

Every patch asserts that its anchor text occurs exactly once (the V2 source is untouched). New settings (all default to the V2 behaviour, so the output is
byte-identical when none of them is given):
  KEEP_Y_ORIGIN       true: the footprint is delivered in the engine frame; only x' is normalised (B -= B.min(0) dropped for y'), so the arms may extend below y' = 0
  SLANT_CUTS          list of {"origin":[x',y'], "normal":[nx,ny]}: extra vertical cut planes (kept side = normal direction) applied to the part of the shell with x' < SLANT_SPLIT_X
                      (the thin wing); the usual UC_KESIM_PAYI cuts stay (they move outside the footprint when the polygon is extended)
  SLANT_SPLIT_X       200.0
  BRIDGE_FOOT_PROFILE 0 = quintic S-curve (V2), 1 = constant-angle ramp (BRIDGE_FOOT_ANGLE degrees), 2 = circular arc (feet + crown) in the side view
  BRIDGE_FOOT_ANGLE   30.0 (10..60); only for profile 1
  BRIDGE_FOOT_WALL_X  [x'_left_wall, x'_right_wall]: ramp / arc start (the junction walls of the footprint); default = the foot points 48.3 / 349.7 (10.7 m inside the thick wing: a ramp from there is 4-6 m above the ground at the wall)
"""
import sys

PATCHES = []


def patch(old, new, count=1):
    PATCHES.append((old, new, count))


# 0) tag
patch("# MASHPROJECT8_BAKLAVA_V2 (V8:", "# MASHPROJECT8_BAKLAVA_V3 (V9: slanted end cuts SLANT_CUTS + KEEP_Y_ORIGIN, bridge foot profile BRIDGE_FOOT_PROFILE/ANGLE; V8:")
patch('print(f"MASHPROJECT8_BAKLAVA_V2 | R=', 'print(f"MASHPROJECT8_BAKLAVA_V3 | R=')

# 1) KEEP_Y_ORIGIN
patch("B -= B.min(0)\n",
      "if bool(_settings.get('KEEP_Y_ORIGIN', False)):\n"
      "    B[:, 0] -= B[:, 0].min()      # V3: footprint given in the engine frame; y' is NOT re-normalised (arms may extend to y' < 0)\n"
      "else:\n"
      "    B -= B.min(0)\n")

# 2) slanted cuts (thin wing only) after the vertical cuts
patch("    mesh=trimesh.Trimesh(cut_v,cut_f,process=False)\nmesh.merge_vertices()\n",
      "    mesh=trimesh.Trimesh(cut_v,cut_f,process=False)\n"
      "_slant = _settings.get('SLANT_CUTS')\n"
      "if _slant:\n"
      "    # V3: slanted end cuts of the thin wing: the shell with the slanted planes applied is used for x' < SLANT_SPLIT_X, the vertically cut shell for the rest\n"
      "    _split = float(_settings.get('SLANT_SPLIT_X', 200.0))\n"
      "    _ms = mesh\n"
      "    for _c in _slant:\n"
      "        _v, _f, *_ = trimesh.intersections.slice_faces_plane(_ms.vertices, _ms.faces, [float(_c['normal'][0]), float(_c['normal'][1]), 0.0], [float(_c['origin'][0]), float(_c['origin'][1]), 0.0])\n"
      "        _ms = trimesh.Trimesh(_v, _f, process=False)\n"
      "    _fa = _ms.faces[_ms.vertices[_ms.faces][:, :, 0].mean(1) < _split]\n"
      "    _fb = mesh.faces[mesh.vertices[mesh.faces][:, :, 0].mean(1) >= _split]\n"
      "    mesh = trimesh.Trimesh(np.vstack([_ms.vertices, mesh.vertices]), np.vstack([_fa, _fb + len(_ms.vertices)]), process=False)\n"
      "mesh.merge_vertices()\n")

# 3) foot profile: settings
patch("BRIDGE_FOOT_HEIGHT_L = float(_settings.get('BRIDGE_FOOT_HEIGHT_L', 0.0))\n",
      "BRIDGE_FOOT_HEIGHT_L = float(_settings.get('BRIDGE_FOOT_HEIGHT_L', 0.0))\n"
      "BRIDGE_FOOT_PROFILE = int(round(float(_settings.get('BRIDGE_FOOT_PROFILE', 0))))     # V3: 0 = quintic S-curve, 1 = constant angle, 2 = circular arc\n"
      "BRIDGE_FOOT_ANGLE = float(_settings.get('BRIDGE_FOOT_ANGLE', 30.0))\n")
patch("BRIDGE_FOOT_HEIGHT_R = _clamp('right foot height', BRIDGE_FOOT_HEIGHT_R, 0.0, 30.0)\n",
      "BRIDGE_FOOT_HEIGHT_R = _clamp('right foot height', BRIDGE_FOOT_HEIGHT_R, 0.0, 30.0)\n"
      "BRIDGE_FOOT_PROFILE = BRIDGE_FOOT_PROFILE if BRIDGE_FOOT_PROFILE in (0, 1, 2) else 0\n"
      "BRIDGE_FOOT_ANGLE = _clamp('foot ramp angle', BRIDGE_FOOT_ANGLE, 10.0, 60.0)\n")

# 4) foot profile: windows + targets inside the GECIS block
patch("        _r0L, _m0L = _rc(_xaL), _dr(_xaL) * _L\n",
      "        _winL = _winR = BRIDGE_FOOT_LEN        # blend window length at the left / right foot (profile 0: BRIDGE_FOOT_LEN)\n"
      "        _ut = None\n"
      "        if _foot_on and BRIDGE_FOOT_PROFILE > 0:\n"
      "            def _floor_at(_left_):\n"
      "                _hf_ = BRIDGE_FOOT_HEIGHT_L if _left_ else BRIDGE_FOOT_HEIGHT_R\n"
      "                _xj_ = _xfL if _left_ else _xfR\n"
      "                _mx_ = float(yumusak((_xj_ - LEFT_END) / (RIGHT_START - LEFT_END)))\n"
      "                _ab_ = (_topc(_xj_) - 2. * ((1 - _mx_) * (SOL_C_ACIKLIGI / 2) + _mx_ * (SAG_C_ACIKLIGI / 2))) if BRIDGE_FOOT_FOLLOW_ARM else MERKEZ_Z - ((1 - _mx_) * (SOL_C_ACIKLIGI / 2) + _mx_ * (SAG_C_ACIKLIGI / 2))\n"
      "                return max(_hf_, _ab_)\n"
      "            _flL, _flR = _floor_at(True), _floor_at(False)\n"
      "            _wall = _settings.get('BRIDGE_FOOT_WALL_X')              # [x' left wall, x' right wall]: where the ramp / arc starts (default: the foot points)\n"
      "            _x0L, _x0R = (float(_wall[0]), float(_wall[1])) if _wall else (_xfL, _xfR)\n"
      "            _xmid = 0.5 * (_x0L + _x0R)\n"
      "            _ubf = lambda x_: _topc(x_) - 2. * _rb                  # underside of the plain bridge tube at x\n"
      "            if BRIDGE_FOOT_PROFILE == 1:\n"
      "                _tn = float(np.tan(np.radians(BRIDGE_FOOT_ANGLE)))\n"
      "                def _ut(x_, left_):                                  # constant-angle ramp from the foot (never above the plain tube underside)\n"
      "                    return min((_flL + _tn * max(x_ - _x0L, 0.)) if left_ else (_flR + _tn * max(_x0R - x_, 0.)), _ubf(x_))\n"
      "            else:\n"
      "                _zc = _ubf(_xmid)                                    # crown of the arc = underside of the plain tube at mid span\n"
      "                _c2 = _x0R - _x0L\n"
      "                _sg = max(_zc - 0.5 * (_flL + _flR), 1e-3)           # sagitta over the chord (feet at slightly different heights: mean)\n"
      "                _Rr = (_c2 * _c2 / 4. + _sg * _sg) / (2. * _sg)\n"
      "                def _ut(x_, left_):\n"
      "                    return _zc - (_Rr - float(np.sqrt(max(_Rr * _Rr - (x_ - _xmid) ** 2, 0.))))\n"
      "            if BRIDGE_FOOT_PROFILE == 1:\n"
      "                # window = where the ramp is still below the plain tube underside (+ margin), evaluated on the grid\n"
      "                _okL = [x_ for x_ in _gx[(_gx > _xfL) & (_gx < _xmid)] if _ut(x_, True) < _ubf(x_) - 0.05]\n"
      "                _okR = [x_ for x_ in _gx[(_gx < _xfR) & (_gx > _xmid)] if _ut(x_, False) < _ubf(x_) - 0.05]\n"
      "                _winL = (max(_okL) - _xfL + 12.) if _okL else 12.\n"
      "                _winR = (_xfR - min(_okR) + 12.) if _okR else 12.\n"
      "                _foot_on = _foot_on and (_xfL + _winL < _xfR - _winR)\n"
      "            else:\n"
      "                _winL = _winR = _xmid - _xfL + 1.                    # the arc spans the whole bridge (both halves meet at mid span)\n"
      "        _r0L, _m0L = _rc(_xaL), _dr(_xaL) * _L\n")
patch("            if _foot_on and (_xaL < _x < _xfL + BRIDGE_FOOT_LEN or _xfR - BRIDGE_FOOT_LEN < _x < _xeR):\n",
      "            if _foot_on and (_xaL < _x < _xfL + _winL or _xfR - _winR < _x < _xeR):\n")
patch("                if _left:\n                    _s = float(yumusak((_x - _xfL) / BRIDGE_FOOT_LEN)); _w = float(yumusak((_x - _xaL) / 12.))\n"
      "                else:\n                    _s = float(yumusak((_xfR - _x) / BRIDGE_FOOT_LEN)); _w = float(yumusak((_xeR - _x) / 12.))\n",
      "                if _left:\n                    _s = float(yumusak((_x - _xfL) / BRIDGE_FOOT_LEN)); _w = float(yumusak((_x - _xaL) / 12.))\n"
      "                else:\n                    _s = float(yumusak((_xfR - _x) / BRIDGE_FOOT_LEN)); _w = float(yumusak((_xeR - _x) / 12.))\n"
      "                if _ut is not None:     # V3: explicit underside target: s = (target - floor) / (plain tube underside - floor)\n"
      "                    _fl_ = max(_hf, _arm_bot)\n"
      "                    _den = _topc(_x) - 2. * _rb - _fl_\n"
      "                    _tgt = _ut(_x, _left) if (_x > _x0L if _left else _x < _x0R) else _fl_\n"
      "                    _s = float(np.clip((_tgt - _fl_) / _den, 0., 1.)) if _den > 1e-6 else 1.\n")

# 5) narrowing window follows the profile window
patch("    _sL = 1.-yumusak((_vx-_xfL)/BRIDGE_FOOT_LEN)          # 1 at the left foot -> 0 at the end of the blend\n"
      "    _sR = 1.-yumusak((_xfR-_vx)/BRIDGE_FOOT_LEN)\n",
      "    _sL = 1.-yumusak((_vx-_xfL)/_winL)          # 1 at the left foot -> 0 at the end of the blend\n"
      "    _sR = 1.-yumusak((_xfR-_vx)/_winR)\n")


def build(src_text):
    t = src_text
    for old, new, cnt in PATCHES:
        n = t.count(old)
        if n != cnt:
            raise SystemExit('patch anchor found %d times (expected %d): %r' % (n, cnt, old[:80]))
        t = t.replace(old, new)
    return t


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    src = open(sys.argv[1], encoding='utf-8').read()
    open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(build(src))
    print('wrote', sys.argv[2], '(%d patches)' % len(PATCHES))
