"""wall_line.py - a straight, axis-aligned wall's location line from its bbox.

The bridge has no tool that returns a wall's location curve:
revit_get_element_info gives only the bounding box (in FEET), `Length` and
`Location Line`. For a wall parallel to X or Y this script rebuilds the
location line (start/end in metres) that opening_layout.py needs.

- Thin side of the bbox = wall thickness -> the line is its midpoint
  (valid for Location Line = Wall Centerline; other location lines are
  reported, not guessed).
- Long side of the bbox can be longer than `Length` because Revit extends
  the wall body into its joins. The extra is put at the end(s) that meet a
  perpendicular wall's centreline given with --joins; without --joins the
  candidates are printed and `ok` is false.
- A slanted wall (thin side != thickness) is refused: ask the user to
  select points on it in Revit, or it is a developer job (location-curve tool).

Write coordinate args as --opt=x,y (a leading minus is otherwise read as an option).

Example (Аэровокзал wall 1658711, bbox in feet as the tool returns it;
result 0,16 -> 25,16):
  python -I wall_line.py --bbox-min=-0.4708,52.0226 --bbox-max=82.0210,52.9642 \
      --feet --length 25.0 --thickness 0.287 --joins 0
"""
import argparse
import json
import sys

FT = 0.3048


def pair(s):
    a, b = (float(v) for v in s.split(","))
    return a, b


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bbox-min", type=pair, required=True, help="x,y of bbox min")
    ap.add_argument("--bbox-max", type=pair, required=True, help="x,y of bbox max")
    ap.add_argument("--feet", action="store_true", help="bbox values are in feet (raw get_element_info)")
    ap.add_argument("--length", type=float, required=True, help="wall `Length` parameter, m (its valueString /1000)")
    ap.add_argument("--thickness", type=float, required=True, help="wall type Width (thickness), m")
    ap.add_argument("--location-line", default="Wall Centerline", help="wall `Location Line` valueString")
    ap.add_argument("--joins", default="", help="centreline coords (m) of perpendicular walls along the long axis, ';' separated")
    ap.add_argument("--tol", type=float, default=0.005, help="tolerance, m")
    a = ap.parse_args(argv)

    k = FT if a.feet else 1.0
    (x0, y0), (x1, y1) = a.bbox_min, a.bbox_max
    x0, y0, x1, y1 = x0 * k, y0 * k, x1 * k, y1 * k
    dx, dy = x1 - x0, y1 - y0
    problems = []

    if dx >= dy:
        axis, lo, hi, thin, mid = "x", x0, x1, dy, (y0 + y1) / 2
    else:
        axis, lo, hi, thin, mid = "y", y0, y1, dx, (x0 + x1) / 2
    if abs(thin - a.thickness) > a.tol:
        problems.append(f"bbox thin side {thin:.4f} m != thickness {a.thickness:.4f} m: wall is slanted, curved "
                        "or has sweeps/reveals - don't derive its line from the bbox")
    if a.location_line != "Wall Centerline":
        problems.append(f"Location Line is '{a.location_line}': the bbox midpoint is the wall centre, not the "
                        "location line - opening_layout works on the centre, say so when reporting offsets")

    extra = (hi - lo) - a.length
    if extra < -a.tol:
        problems.append(f"bbox long side {hi - lo:.4f} m is shorter than Length {a.length:.4f} m")
    joins = [float(v) for v in a.joins.split(";") if v.strip()]
    candidates = {"extra_at_min": (lo + extra, hi), "extra_at_max": (lo, hi - extra),
                  "split": (lo + extra / 2, hi - extra / 2)}
    chosen = None
    if extra <= a.tol:
        chosen = "none"
        s, e = lo, hi
    else:
        for name, (s, e) in candidates.items():
            if joins and all(any(abs(j - v) <= a.tol for v in (s, e)) for j in joins):
                chosen = name
                break
        if chosen:
            s, e = candidates[chosen]
        else:
            problems.append(f"bbox is {extra:.4f} m longer than Length (wall joins); pass --joins with the "
                            "perpendicular walls' centrelines to decide which end, or ask the user")
            s, e = candidates["split"]

    def xy(v):
        return {"x": round(v, 4), "y": round(mid, 4)} if axis == "x" else {"x": round(mid, 4), "y": round(v, 4)}

    print(json.dumps({
        "axis": axis,
        "start": xy(s), "end": xy(e),
        "length_check": round(e - s, 4),
        "join_extension": round(extra, 4), "resolved_by": chosen,
        "candidates": {n: [xy(c[0]), xy(c[1])] for n, c in candidates.items()} if extra > a.tol else None,
        "ok": not problems, "problems": problems,
    }, indent=2, ensure_ascii=False))
    return 0 if not problems else 2


if __name__ == "__main__":
    sys.exit(main())
