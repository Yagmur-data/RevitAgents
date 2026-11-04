"""wall_floor_audit.py - model-integrity audit of walls and floors (no code figures).

The bridge has no location-curve tool and no per-warning element ids, and
revit_create_wall / revit_create_floor accept duplicates without a warning.
This script rebuilds every axis-aligned wall's centreline from what the
tools do return (bbox, Length, type width) and finds the drawing defects the
skill's M rows name:

  M1 overlapping / duplicate walls   (same level, same line, ranges overlap)
  M2 open ends                       (a wall end stops short of / runs past
                                      another wall's line by more than --tol
                                      but less than --gap-max)
  M3 wall top not tied to a level    (Unconnected, top != next level or the
                                      roof level; parapets are reported, not
                                      flagged, when --parapet-max covers them)
  M4 uneven exterior heights         (same level, same type, heights differ)
  F1 foundation-slab type used above the lowest level
  F2 floor edge vs the exterior wall outline (centreline / inner face /
                                      outer face / outside) - reported, the
                                      convention is the user's choice
  F3 overlapping floors on one level (possible duplicate)
  H  storey clear height per level  (next level - this level - upper slab)

Input: one JSON file
{
  "units": "feet" | "meters",            # bbox units (raw get_element_info = feet)
  "levels": [{"name": "L1", "elevation": 0.0}],          # metres; optional
                                         # "storey": false for stair-landing levels
  "walls":  [{"id": 1, "level": "L1", "type": "...", "kind": "Basic",
              "bbox_min": [x, y, z], "bbox_max": [x, y, z],
              "length": 26.0, "thickness": 0.287, "height": 9.0,   # metres
              "base_offset": 0.0, "top_constraint": "Unconnected",
              "location_line": "Wall Centerline"}],
  "floors": [{"id": 2, "level": "L1", "type": "...", "family": "Floor",
              "bbox_min": [x, y, z], "bbox_max": [x, y, z],
              "thickness": 0.25, "offset": 0.0}]
}
Slanted, curved and curtain walls whose bbox thin side != thickness are
listed under `skipped` - never guessed.

Usage: python -I wall_floor_audit.py model.json [--tol 0.005] [--gap-max 0.5]
Exit 0 = no M/F defects, 2 = defects listed (the report is JSON either way).
"""
import argparse
import json
import sys

FT = 0.3048


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def box(e, k):
    (x0, y0, *_), (x1, y1, *_) = e["bbox_min"], e["bbox_max"]
    return x0 * k, y0 * k, x1 * k, y1 * k


def centrelines(walls, k, tol):
    """First pass: axis, cross coordinate and bbox range of every straight wall."""
    lines, skipped = [], []
    for w in walls:
        x0, y0, x1, y1 = box(w, k)
        dx, dy = x1 - x0, y1 - y0
        axis, lo, hi, thin, mid = ("x", x0, x1, dy, (y0 + y1) / 2) if dx >= dy else ("y", y0, y1, dx, (x0 + x1) / 2)
        if abs(thin - w["thickness"]) > tol:
            skipped.append({"id": w["id"], "why": f"bbox thin side {thin:.3f} m != thickness {w['thickness']:.3f} m "
                                                   "(slanted, curved, curtain or has sweeps)"})
            continue
        lines.append({"w": w, "axis": axis, "mid": mid, "lo": lo, "hi": hi, "extra": (hi - lo) - w["length"]})
    return lines, skipped


def zrange(w, elev):
    """Base/top elevation (m) of a wall, or None when its level is not in the input."""
    if w["level"] not in elev:
        return None
    b = elev[w["level"]] + w.get("base_offset", 0.0)
    return b, b + w["height"]


def together(A, B, elev, tol):
    """Walls that share height: a wall based on L1 running up through L2 meets the L2 partitions
    (2026-10-30: Project1's 9 m facade walls are based on L1 and enclose L2 too). Same level when
    elevations are unknown."""
    za, zb = zrange(A["w"], elev), zrange(B["w"], elev)
    if za is None or zb is None:
        return A["w"]["level"] == B["w"]["level"]
    return min(za[1], zb[1]) - max(za[0], zb[0]) > tol


def resolve(lines, tol, elev=None):
    """Put each wall's join extension at the end(s) that meet a perpendicular centreline."""
    elev = elev or {}
    for L in lines:
        perp = [P["mid"] for P in lines if P is not L and P["axis"] != L["axis"]
                and together(P, L, elev, tol) and P["lo"] - tol <= L["mid"] <= P["hi"] + tol]
        e = L["extra"]
        if e <= tol:
            L["s"], L["e"], L["sure"] = L["lo"], L["hi"], True
            continue
        cands = [(L["lo"] + e, L["hi"]), (L["lo"], L["hi"] - e), (L["lo"] + e / 2, L["hi"] - e / 2)]
        score = [sum(any(abs(p - v) <= tol for p in perp) for v in c) for c in cands]
        best = max(range(3), key=lambda i: (score[i], i == 2))
        L["s"], L["e"] = cands[best]
        L["sure"] = score[best] > 0
    return lines


def pt(L, v):
    return (round(v, 4), round(L["mid"], 4)) if L["axis"] == "x" else (round(L["mid"], 4), round(v, 4))


def audit(m, tol, gap_max, parapet_max):
    k = FT if m.get("units", "feet") == "feet" else 1.0
    levels = sorted(m.get("levels", []), key=lambda l: l["elevation"])
    elev = {l["name"]: l["elevation"] for l in levels}
    lines, skipped = centrelines(m.get("walls", []), k, tol)
    resolve(lines, tol, elev)
    defects, notes = [], []

    for i, A in enumerate(lines):
        for B in lines[i + 1:]:
            if not together(A, B, elev, tol) or A["axis"] != B["axis"]:
                continue
            if abs(A["mid"] - B["mid"]) > (A["w"]["thickness"] + B["w"]["thickness"]) / 2 - tol:
                continue
            ov = min(A["e"], B["e"]) - max(A["s"], B["s"])
            if ov > tol:
                defects.append({"rule": "M1", "ids": [A["w"]["id"], B["w"]["id"]], "overlap_m": round(ov, 3),
                                "offset_m": round(abs(A["mid"] - B["mid"]), 3),
                                "what": "walls overlap on one line (duplicate or double-drawn)"})

    for A in lines:
        for end in ("s", "e"):
            v = A[end]
            best = None
            for B in lines:
                if B is A or not together(A, B, elev, tol):
                    continue
                if B["axis"] != A["axis"]:
                    if not (B["s"] - tol <= A["mid"] <= B["e"] + tol):
                        continue
                    d = abs(v - B["mid"])
                else:
                    if abs(A["mid"] - B["mid"]) > tol:
                        continue
                    d = min(abs(v - B["s"]), abs(v - B["e"]))
                if best is None or d < best[0]:
                    best = (d, B["w"]["id"])
            if best and tol < best[0] <= gap_max:
                defects.append({"rule": "M2", "id": A["w"]["id"], "end": pt(A, v), "near": best[1],
                                "gap_m": round(best[0], 3), "sure": A["sure"],
                                "what": "wall end misses the other wall's centreline (open/overrun join)"})
            elif best is None or best[0] > gap_max:
                notes.append({"rule": "M2", "id": A["w"]["id"], "end": pt(A, v), "what": "free end (nothing within gap-max)"})

    # Storey levels: a level some wall stands on, unless the input says "storey": true/false
    # (stair-landing levels such as "+2.100" carry floors but no walls and are not storeys).
    based = {w["level"] for w in m.get("walls", [])}
    storeys = [l for l in levels if l.get("storey", l["name"] in based or l is levels[-1])]
    floors = m.get("floors", [])
    slab = {l["name"]: max((f["thickness"] for f in floors if f["level"] == l["name"]), default=0.0) for l in levels}
    for A in lines:
        w = A["w"]
        if w.get("top_constraint", "Unconnected") != "Unconnected" or w["level"] not in elev:
            continue
        base = elev[w["level"]] + w.get("base_offset", 0.0)
        top = base + w["height"]
        targets = []
        for l in storeys:
            if l["elevation"] > base + tol:
                targets.append((abs(top - l["elevation"]), l["name"], 0.0))
                if slab[l["name"]]:
                    targets.append((abs(top - l["elevation"] + slab[l["name"]]), l["name"], -slab[l["name"]]))
        exact = [t for t in targets if t[0] <= tol]
        if w["height"] <= parapet_max and not exact:
            notes.append({"rule": "M3", "id": w["id"], "top_m": round(top, 3), "what": "low unconnected wall - parapet/upstand?"})
            continue
        if exact:
            _, name, off = exact[0]
            defects.append({"rule": "M3", "id": w["id"], "top_m": round(top, 3), "tie_to": name, "top_offset_m": off,
                            "what": "Top Constraint = Unconnected; top already sits at " +
                                    (f"{name}" if not off else f"the underside of the {name} slab") +
                                    " - tie it (Top Constraint + Top Offset) so it follows level changes"})
        else:
            near = sorted((top - elev[l["name"]], l["name"]) for l in storeys if l["elevation"] > base + tol)
            near = min(near, key=lambda t: abs(t[0]), default=None)
            defects.append({"rule": "M3", "id": w["id"], "top_m": round(top, 3),
                            "nearest_storey": {"level": near[1], "delta_m": round(near[0], 3)} if near else None,
                            "what": "Top Constraint = Unconnected and the top matches no storey level or slab "
                                    "underside (built-in parapet? ask before changing)"})

    groups = {}
    for A in lines:
        groups.setdefault((A["w"]["level"], A["w"]["type"]), []).append(A["w"])
    for (lvl, typ), ws in groups.items():
        hs = sorted({round(w["height"], 3) for w in ws})
        if len(hs) > 1 and len(ws) <= 8:
            defects.append({"rule": "M4", "level": lvl, "type": typ, "heights_m": hs,
                            "ids": {str(h): [w["id"] for w in ws if round(w["height"], 3) == h] for h in hs},
                            "what": "same wall type on one level with different heights - intended?"})

    lowest = levels[0]["name"] if levels else None
    for f in floors:
        if "foundation" in (f.get("family", "") + f.get("type", "")).lower() and f["level"] != lowest:
            defects.append({"rule": "F1", "id": f["id"], "type": f["type"], "what": "foundation-slab type above the lowest level"})

    for f in floors:
        fz = elev.get(f["level"], 0.0) + f.get("offset", 0.0)
        # "outline": false = site wall / barrier / kerb outside the building - not part of the exterior outline
        ext = [A for A in lines if A["w"].get("kind", "Basic") != "Curtain" and A["w"].get("outline", True) and (
               A["w"]["level"] == f["level"] if zrange(A["w"], elev) is None
               else zrange(A["w"], elev)[0] <= fz + tol and zrange(A["w"], elev)[1] > fz + tol)]
        if not ext:
            continue
        x0, y0, x1, y1 = box(f, k)
        xs = [A["mid"] for A in ext if A["axis"] == "y"]
        ys = [A["mid"] for A in ext if A["axis"] == "x"]
        if not xs or not ys:
            continue
        inside = (max(0, min(x1, max(xs)) - max(x0, min(xs))) * max(0, min(y1, max(ys)) - max(y0, min(ys))))
        share = inside / max((x1 - x0) * (y1 - y0), 1e-9)
        if share < 0.5:
            notes.append({"rule": "F2", "id": f["id"], "level": f["level"], "inside_outline_share": round(share, 2),
                          "what": "mostly outside the exterior wall outline (apron, external landing, canopy?)"})
            continue
        sides = {}
        for side, v, ref, outward in (("min_x", x0, min(xs), -1), ("max_x", x1, max(xs), 1),
                                      ("min_y", y0, min(ys), -1), ("max_y", y1, max(ys), 1)):
            t = max(A["w"]["thickness"] for A in ext if A["mid"] == ref) / 2
            d = (v - ref) * outward
            sides[side] = ("centreline" if abs(d) <= tol else "outer face" if abs(d - t) <= tol
                           else "inner face" if abs(d + t) <= tol else
                           f"outside by {d - t:.3f} m" if d > t else f"inside by {-d:.3f} m")
        notes.append({"rule": "F2", "id": f["id"], "level": f["level"], "edges_vs_outermost_walls": sides})

    for i, a in enumerate(floors):
        for b in floors[i + 1:]:
            if a["level"] != b["level"]:
                continue
            ax0, ay0, ax1, ay1 = box(a, k)
            bx0, by0, bx1, by1 = box(b, k)
            ov = max(0, min(ax1, bx1) - max(ax0, bx0)) * max(0, min(ay1, by1) - max(ay0, by0))
            if ov > 0.01:
                defects.append({"rule": "F3", "ids": [a["id"], b["id"]], "bbox_overlap_m2": round(ov, 2),
                                "what": "floor bboxes overlap on one level - duplicate or stepped slab?"})

    heights = []
    for lo_l, hi_l in zip(storeys, storeys[1:]):
        storey = hi_l["elevation"] - lo_l["elevation"]
        s = slab[hi_l["name"]] or None
        heights.append({"from": lo_l["name"], "to": hi_l["name"], "storey_m": round(storey, 3),
                        "upper_slab_m": s, "clear_to_slab_m": round(storey - s, 3) if s else None,
                        "note": "clear to the slab underside; a suspended ceiling lowers the room height further"})

    return {"walls_checked": len(lines), "floors_checked": len(floors), "defects": defects,
            "notes": notes, "storey_heights": heights, "skipped": skipped,
            "uncertain_lines": [A["w"]["id"] for A in lines if not A["sure"]],
            "centrelines": {str(A["w"]["id"]): [pt(A, A["s"]), pt(A, A["e"])] for A in lines}}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("model", help="JSON file (see module docstring)")
    ap.add_argument("--tol", type=float, default=0.005, help="tolerance, m")
    ap.add_argument("--gap-max", type=float, default=0.5, help="largest miss still reported as an open join, m")
    ap.add_argument("--parapet-max", type=float, default=1.5, help="unconnected walls up to this height = parapet note, m")
    a = ap.parse_args(argv)
    r = audit(load(a.model), a.tol, a.gap_max, a.parapet_max)
    sys.stdout.reconfigure(encoding="utf-8")  # Cyrillic level names on a cp1254 console
    print(json.dumps(r, indent=2, ensure_ascii=False))
    return 2 if r["defects"] else 0


if __name__ == "__main__":
    sys.exit(main())
