"""Stair run calculator for Revit_Stair.

Floor-to-floor height + limits -> riser count, equal riser height, tread,
step formula value, flight split with landings, and (optionally) the
walking-line start/end points per flight for revit_create_stair plus the
landing outline for a Floor stand-in.

No code figures are built in: every limit comes from the command line
(stair-code-check skill values, or the stair type's own limits).

revit_create_stair lays treads along the walking line, so a flight with
n risers needs a line of (n - 1) x tread. That is the length printed here.

Two ways to size it:
  - design (preferred): --target-riser 0.170 --blondel 0.630 [--min-tread]
    n = round(H / target), raised until H/n <= max riser; tread =
    blondel - 2r rounded to the mm, raised to --min-tread if below.
  - fixed: --tread 0.28 and n = ceil(H / max riser) (fewest risers).

Usage (metres):
  python -I stair_run.py --height 2.75 --max-riser 0.1778 --target-riser 0.17
      --blondel 0.63 --min-tread 0.2794
  python -I stair_run.py --height 4.2 --max-riser 0.175 --tread 0.275
      [--max-risers-per-flight 12] [--max-flight-rise 3.658]
      [--step-min 0.60 --step-max 0.64] [--pitch-max 42]
      [--landing-depth 1.2]
      [--start 10,5 --dir 1,0 --layout straight|U --turn left|right
       --width 1.2 --gap 0.1]
Prints JSON.
"""
import argparse
import json
import math


def split_flights(n_risers, max_per_flight):
    if not max_per_flight or n_risers <= max_per_flight:
        return [n_risers]
    k = math.ceil(n_risers / max_per_flight)
    base, extra = divmod(n_risers, k)
    # Longer flights first, so 25 / 2 -> [13, 12].
    return [base + 1 if i < extra else base for i in range(k)]


def pt(x, y):
    return {"x": round(x, 4), "y": round(y, 4)}


def rect(x, y, dx, dy, px, py, depth, width):
    """Rectangle starting on the line through (x, y) across the walking
    direction, `depth` along (dx, dy), `width` centred on the walking line."""
    hw = width / 2
    a = (x - px * hw, y - py * hw)
    return [pt(*a),
            pt(a[0] + dx * depth, a[1] + dy * depth),
            pt(a[0] + dx * depth + px * width, a[1] + dy * depth + py * width),
            pt(a[0] + px * width, a[1] + py * width)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--height", type=float, required=True, help="floor-to-floor, m")
    ap.add_argument("--max-riser", type=float, required=True, help="m")
    ap.add_argument("--tread", type=float, help="fixed going for the run, m")
    ap.add_argument("--target-riser", type=float, help="design riser, m (design mode)")
    ap.add_argument("--blondel", type=float, help="target 2R+G, m; tread = blondel - 2R")
    ap.add_argument("--min-tread", type=float, help="code minimum going, m")
    ap.add_argument("--min-riser", type=float, help="m, optional lower bound")
    ap.add_argument("--max-risers-per-flight", type=int)
    ap.add_argument("--max-flight-rise", type=float, help="max vertical rise between landings, m")
    ap.add_argument("--step-min", type=float, help="lower bound of 2R+G, m")
    ap.add_argument("--step-max", type=float, help="upper bound of 2R+G, m")
    ap.add_argument("--pitch-min", type=float, help="degrees")
    ap.add_argument("--pitch-max", type=float, help="degrees")
    ap.add_argument("--landing-depth", type=float, help="intermediate landing depth, m")
    ap.add_argument("--floor-landing-depth", type=float,
                    help="clear depth required at the bottom and top floor landings, m")
    ap.add_argument("--advise-risers-per-flight", type=int,
                    help="comfort limit: warn (ÖNERİ) above this many risers per flight")
    ap.add_argument("--start", help="x,y of the first flight's walking-line start")
    ap.add_argument("--dir", default="1,0", help="dx,dy of the first flight; write --dir=-1,0 for a negative x")
    ap.add_argument("--layout", choices=["straight", "U"], default="straight")
    ap.add_argument("--turn", choices=["left", "right"], default="left")
    ap.add_argument("--width", type=float, help="run width, m (U layout)")
    ap.add_argument("--gap", type=float, default=0.0, help="well between U flights, m")
    a = ap.parse_args()

    if a.height <= 0 or a.max_riser <= 0:
        raise SystemExit("height and max-riser must be > 0")
    if a.tread is None and a.blondel is None:
        raise SystemExit("pass --tread, or --blondel (with --target-riser)")

    warnings = []
    if a.target_riser:
        n = max(1, round(a.height / a.target_riser))
    else:
        n = math.ceil(a.height / a.max_riser - 1e-9)
    while a.height / n > a.max_riser + 1e-9:
        n += 1
    riser = a.height / n

    if a.tread is None:
        a.tread = round(a.blondel - 2 * riser, 3)
    if a.min_tread and a.tread < a.min_tread - 1e-9:
        warnings.append(f"tread {a.tread*1000:.0f} mm raised to min {a.min_tread*1000:.1f} mm")
        a.tread = math.ceil(a.min_tread * 1000 - 1e-6) / 1000
    if a.tread <= 0:
        raise SystemExit("tread must be > 0")

    out = {
        "height_m": a.height,
        "risers": n,
        "riser_m": round(riser, 5),
        "riser_mm": round(riser * 1000, 1),
        "tread_m": a.tread,
        "step_2R_plus_G_m": round(2 * riser + a.tread, 4),
        "pitch_deg": round(math.degrees(math.atan(riser / a.tread)), 2),
        "warnings": warnings,
    }
    pitch = out["pitch_deg"]
    if (a.pitch_min is not None and pitch < a.pitch_min) or \
       (a.pitch_max is not None and pitch > a.pitch_max):
        out["warnings"].append(f"pitch {pitch} deg outside [{a.pitch_min}, {a.pitch_max}]")
    if a.min_riser and riser < a.min_riser:
        out["warnings"].append(
            f"riser {riser*1000:.1f} mm < min {a.min_riser*1000:.0f} mm")
    if a.step_min is not None or a.step_max is not None:
        v = 2 * riser + a.tread
        ok = (a.step_min is None or v >= a.step_min - 1e-9) and \
             (a.step_max is None or v <= a.step_max + 1e-9)
        out["step_ok"] = ok
        if not ok:
            out["warnings"].append(
                f"2R+G = {v:.3f} m outside [{a.step_min}, {a.step_max}]")

    per_flight = a.max_risers_per_flight
    if a.max_flight_rise:
        by_rise = math.floor(a.max_flight_rise / riser + 1e-9)
        per_flight = min(per_flight, by_rise) if per_flight else by_rise
    flights = split_flights(n, per_flight)
    elev, fl = 0.0, []
    for i, k in enumerate(flights):
        f = {"flight": i + 1, "risers": k,
             "base_offset_m": round(elev, 4),
             "top_offset_m": round(elev + k * riser, 4),
             "run_length_m": round((k - 1) * a.tread, 4)}
        elev += k * riser
        fl.append(f)
    out["flights"] = fl
    if a.advise_risers_per_flight:
        long_ = [f["flight"] for f in fl if f["risers"] > a.advise_risers_per_flight]
        if long_:
            out["warnings"].append(
                f"ÖNERİ: flight(s) {long_} over {a.advise_risers_per_flight} risers — "
                "consider an intermediate landing")
    if len(fl) > 1:
        out["landing_offsets_m"] = [f["top_offset_m"] for f in fl[:-1]]
        if a.landing_depth is None:
            out["warnings"].append("multi-flight: pass --landing-depth for geometry")

    if a.start:
        sx, sy = map(float, a.start.split(","))
        dx, dy = map(float, a.dir.split(","))
        L = math.hypot(dx, dy)
        dx, dy = dx / L, dy / L
        # Left-hand perpendicular of the walking direction.
        px, py = (-dy, dx) if a.turn == "left" else (dy, -dx)
        D = a.landing_depth or 0.0
        landings = []
        last_dir = (dx, dy)
        if a.layout == "straight":
            x, y = sx, sy
            for i, f in enumerate(fl):
                ex, ey = x + dx * f["run_length_m"], y + dy * f["run_length_m"]
                f["start"], f["end"] = pt(x, y), pt(ex, ey)
                if i < len(fl) - 1 and D and a.width:
                    landings.append({"offset_m": f["top_offset_m"],
                                     "outline": rect(ex, ey, dx, dy, px, py, D, a.width)})
                x, y = ex + dx * D, ey + dy * D
        else:
            if len(fl) != 2:
                raise SystemExit("U layout needs exactly 2 flights (set --max-risers-per-flight)")
            if not a.width or not D:
                raise SystemExit("U layout needs --width and --landing-depth")
            f1, f2 = fl
            e1x, e1y = sx + dx * f1["run_length_m"], sy + dy * f1["run_length_m"]
            f1["start"], f1["end"] = pt(sx, sy), pt(e1x, e1y)
            off = a.width + a.gap
            s2x, s2y = e1x + px * off, e1y + py * off
            f2["start"] = pt(s2x, s2y)
            f2["end"] = pt(s2x - dx * f2["run_length_m"], s2y - dy * f2["run_length_m"])
            # Landing: from flight 1's last riser line forward by D, across
            # both flights' outer edges.
            hw = a.width / 2
            a0x, a0y = e1x - px * hw, e1y - py * hw
            corners = [(a0x, a0y),
                       (a0x + dx * D, a0y + dy * D),
                       (a0x + dx * D + px * (off + a.width), a0y + dy * D + py * (off + a.width)),
                       (a0x + px * (off + a.width), a0y + py * (off + a.width))]
            landings.append({"offset_m": f1["top_offset_m"],
                             "outline": [pt(*c) for c in corners]})
            span = max(f1["run_length_m"], f2["run_length_m"]) + D
            out["footprint_m"] = {"along": round(span, 3),
                                  "across": round(2 * a.width + a.gap, 3)}
            last_dir = (-dx, -dy)
        if landings:
            out["landings"] = landings
        # Floor landings: the clear zone that must stay free (walls, door
        # swings, other stairs) in front of the first riser and past the
        # last nosing line, as deep as --floor-landing-depth.
        if a.floor_landing_depth and a.width:
            FD = a.floor_landing_depth
            first, last = fl[0], fl[-1]
            bx, by = first["start"]["x"], first["start"]["y"]
            tx, ty = last["end"]["x"], last["end"]["y"]
            ldx, ldy = last_dir
            lpx, lpy = (-ldy, ldx) if a.turn == "left" else (ldy, -ldx)
            out["floor_landing_zones"] = [
                {"where": "bottom", "offset_m": 0.0,
                 "outline": rect(bx, by, -dx, -dy, px, py, FD, a.width)},
                {"where": "top", "offset_m": last["top_offset_m"],
                 "outline": rect(tx, ty, ldx, ldy, lpx, lpy, FD, a.width)},
            ]

    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
