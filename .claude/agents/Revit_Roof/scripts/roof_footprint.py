"""Roof footprint helper for Revit_Roof.

Turns a closed outline (metres, plan XY) into the `profile` + `edgeSlopesDeg`
arguments for `revit_create_roof`: orders it counter-clockwise, offsets it
outward by the eave overhang (mitred corners), and builds the per-edge slope
list for a roof form.

Usage:
  python roof_footprint.py <input.json>
input.json:
  {"outline": [[x,y], ...],          # wall outer-face corners, metres, no repeat of first point
   "overhang": 0.5,                  # metres, outward; 0 = flush
   "form": "hip|gable|shed|flat",
   "slope": 30,                      # degrees (convert % first: deg = atan(pct/100))
   "ridge": "long|short",            # gable only: ridge parallel to the long or short side (default long)
   "low_edge": 0}                    # shed only: index of the eave edge that slopes (after CCW ordering)

Prints JSON: profile, edgeSlopesDeg, edges (index, length, direction), area, notes.
Gable/shed forms are only offered for 4-sided outlines; anything else is
refused rather than guessed.
"""
import json
import math
import sys


def signed_area(pts):
    return 0.5 * sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                     for i in range(len(pts)))


def offset_polygon(pts, d):
    """Mitred outward offset of a CCW polygon by d (d > 0 grows it)."""
    if d == 0:
        return [list(p) for p in pts]
    n = len(pts)
    lines = []
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        nx, ny = dy / L, -dx / L  # right-hand normal = outward for CCW
        lines.append(((x1 + nx * d, y1 + ny * d), (dx / L, dy / L)))
    out = []
    for i in range(n):
        (p, u), (q, v) = lines[i - 1], lines[i]
        den = u[0] * v[1] - u[1] * v[0]
        if abs(den) < 1e-9:  # collinear edges: just shift the vertex
            out.append([q[0], q[1]])
            continue
        t = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / den
        out.append([round(p[0] + u[0] * t, 6), round(p[1] + u[1] * t, 6)])
    return out


def main(path):
    cfg = json.load(open(path, encoding="utf-8"))
    pts = [list(map(float, p[:2])) for p in cfg["outline"]]
    if len(pts) < 3:
        sys.exit("outline needs at least 3 points")
    notes = []
    if signed_area(pts) < 0:
        pts.reverse()
        notes.append("outline was clockwise; reversed to CCW (edge indices refer to the CCW order)")
    prof = offset_polygon(pts, float(cfg.get("overhang", 0)))
    n = len(prof)
    edges = []
    for i in range(n):
        (x1, y1), (x2, y2) = prof[i], prof[(i + 1) % n]
        edges.append({"i": i, "length": round(math.hypot(x2 - x1, y2 - y1), 4),
                      "dir_deg": round(math.degrees(math.atan2(y2 - y1, x2 - x1)), 2)})

    form, slope = cfg.get("form", "hip"), float(cfg.get("slope", 0))
    if form == "flat":
        slopes = [None] * n
    elif form == "hip":
        slopes = [slope] * n
    elif form in ("gable", "shed"):
        if n != 4:
            sys.exit(f"{form} is only built for 4-sided outlines (got {n}); split the outline or use edgeSlopesDeg by hand")
        if form == "gable":
            long_first = edges[0]["length"] + edges[2]["length"] >= edges[1]["length"] + edges[3]["length"]
            ridge_long = cfg.get("ridge", "long") == "long"
            # eaves (sloping edges) are the edges parallel to the ridge
            eave = (0, 2) if long_first == ridge_long else (1, 3)
            slopes = [slope if i in eave else None for i in range(4)]
        else:
            low = int(cfg.get("low_edge", 0)) % 4
            slopes = [slope if i == low else None for i in range(4)]
    else:
        sys.exit(f"unknown form '{form}'")

    print(json.dumps({
        "profile": [{"x": x, "y": y} for x, y in prof],
        "edgeSlopesDeg": slopes,
        "edges": edges,
        "area_m2": round(signed_area(prof), 3),
        "notes": notes,
    }, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
