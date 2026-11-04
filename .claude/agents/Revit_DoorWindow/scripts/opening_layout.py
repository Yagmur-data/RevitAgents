"""opening_layout.py - door/window positions along a straight wall.

Turns "put the door 1 m in from the start of the wall" or "3 equally spaced
windows in this wall" into the insertion points revit_place_family_instance needs
(the centre of each opening, on the wall's location line), and checks that
every opening stays inside the wall and does not overlap an existing one.

No code figures are built in: minimum jamb/end clearances come from the args.
Pure Python, metres.

Write coordinate args as --opt=x,y (a leading minus is otherwise read as an option).

Examples
  # one door, near edge 1.0 m from the wall start
  python -I opening_layout.py --wall-start 0,0 --wall-end 6,0 --width 0.9 --offset 1.0
  # one window centred on the wall
  python -I opening_layout.py --wall-start 0,0 --wall-end 6,0 --width 1.2 --center
  # 3 windows, equal piers (wall ends count as piers)
  python -I opening_layout.py --wall-start 0,0 --wall-end 6,0 --width 1.2 --count 3
  # check against openings already in the wall (centre x,y + width, ';' separated)
  python -I opening_layout.py ... --existing "2.5,0,0.9;4.8,0,1.2" --min-end 0.1 --min-gap 0.2
"""
import argparse
import json
import math
import sys


def pt(s):
    x, y = (float(v) for v in s.split(","))
    return x, y


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--wall-start", type=pt, required=True, help="x,y of the wall location line start")
    ap.add_argument("--wall-end", type=pt, required=True, help="x,y of the wall location line end")
    ap.add_argument("--width", type=float, required=True, help="opening width (family Width / rough width), m")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--offset", type=float, help="distance from the reference end to the NEAR edge of the opening")
    g.add_argument("--center-offset", type=float, help="distance from the reference end to the opening CENTRE")
    g.add_argument("--center", action="store_true", help="one opening centred on the wall")
    g.add_argument("--count", type=int, help="N openings with equal piers between them and at both ends")
    ap.add_argument("--from-end", action="store_true", help="measure --offset/--center-offset from the wall END instead of the start")
    ap.add_argument("--existing", default="", help="openings already in the wall: 'x,y,width;x,y,width' (centres)")
    ap.add_argument("--min-end", type=float, default=0.0, help="minimum distance opening edge -> wall end, m")
    ap.add_argument("--min-gap", type=float, default=0.0, help="minimum distance between two openings' edges, m")
    a = ap.parse_args(argv)

    (x0, y0), (x1, y1) = a.wall_start, a.wall_end
    L = math.hypot(x1 - x0, y1 - y0)
    if L <= 0:
        sys.exit("wall start and end are the same point")
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    w = a.width

    # centres as distance along the wall from its start
    if a.count:
        pier = (L - a.count * w) / (a.count + 1)
        centres = [pier * (i + 1) + w * i + w / 2 for i in range(a.count)]
        mode = {"count": a.count, "pier": round(pier, 4)}
    elif a.center or (a.offset is None and a.center_offset is None):
        centres = [L / 2]
        mode = {"center": True}
    else:
        c = a.center_offset if a.center_offset is not None else a.offset + w / 2
        centres = [L - c if a.from_end else c]
        mode = {"offset_from": "end" if a.from_end else "start",
                "center_offset": round(c, 4)}

    existing = []
    for item in filter(None, (s.strip() for s in a.existing.split(";"))):
        ex, ey, ew = (float(v) for v in item.split(","))
        s = (ex - x0) * ux + (ey - y0) * uy          # along the wall
        d = -(ex - x0) * uy + (ey - y0) * ux         # off the line
        existing.append({"s": s, "width": ew, "off_line": d})

    problems = []
    out = []
    for i, c in enumerate(centres):
        lo, hi = c - w / 2, c + w / 2
        if lo < a.min_end - 1e-9 or hi > L - a.min_end + 1e-9:
            problems.append(f"opening {i + 1}: edge {min(lo, L - hi):.3f} m from a wall end (< {a.min_end})")
        for j, e in enumerate(existing):
            gap = abs(c - e["s"]) - (w + e["width"]) / 2
            if gap < a.min_gap - 1e-9:
                problems.append(f"opening {i + 1}: {'overlaps' if gap < 0 else f'{gap:.3f} m from'} existing opening {j + 1}")
        for k in range(i):
            gap = abs(c - centres[k]) - w
            if gap < a.min_gap - 1e-9:
                problems.append(f"opening {i + 1}: {'overlaps' if gap < 0 else f'{gap:.3f} m from'} opening {k + 1}")
        out.append({
            "location": {"x": round(x0 + ux * c, 4), "y": round(y0 + uy * c, 4)},
            "center_along_wall": round(c, 4),
            "edges_along_wall": [round(lo, 4), round(hi, 4)],
        })
    if a.count and mode["pier"] < 0:
        problems.append(f"{a.count} openings of {w} m don't fit in a {L:.3f} m wall")

    print(json.dumps({
        "wall_length": round(L, 4),
        "wall_direction": [round(ux, 6), round(uy, 6)],
        "mode": mode,
        "openings": out,
        "existing_along_wall": [{k: round(v, 4) for k, v in e.items()} for e in existing],
        "ok": not problems,
        "problems": problems,
    }, indent=2, ensure_ascii=False))
    return 0 if not problems else 2


if __name__ == "__main__":
    sys.exit(main())
