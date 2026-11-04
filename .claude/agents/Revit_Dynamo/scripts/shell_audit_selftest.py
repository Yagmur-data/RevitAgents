#!/usr/bin/env python3
"""shell_audit_selftest.py - offline logic test for a Dynamo mesh-audit Python node (ShellMeshAudit_*.py).

Stubs clr / Autodesk.Revit.DB / RevitServices with tiny fake classes, execs the node source with a synthetic
doc and compares the result against hand-computable expectations (subdivided cube + injected defects).
It proves the ALGORITHM and the JSON/OUT shape only - NOT pythonnet behaviour, NOT Revit's Mesh API, NOT
Dynamo. Usage:  python shell_audit_selftest.py <path-to-node.py> [--big]   (--big = timing run, ~160k tris)
"""
import io
import json
import os
import sys
import tempfile
import time
import types

F2M = 0.3048


# ------------------------------------------------------------ fake Revit API
class XYZ(object):
    def __init__(self, x, y, z):
        self.X, self.Y, self.Z = x, y, z


class GeometryObject(object):
    def GetType(self):
        return types.SimpleNamespace(Name=type(self).__name__)


class Mesh(GeometryObject):
    pass


class Solid(GeometryObject):
    Faces = types.SimpleNamespace(Size=6)


class GeometryInstance(GeometryObject):
    def __init__(self, inner):
        self._inner = inner

    def GetInstanceGeometry(self):
        return self._inner


class Verts(list):
    @property
    def Count(self):
        return len(self)


class Tri(object):
    def __init__(self, idx):
        self._i = idx

    def get_Index(self, k):
        return self._i[k]


class FakeMesh(Mesh):
    def __init__(self, verts, tris):
        self.Vertices = Verts(XYZ(*v) for v in verts)
        self._t = tris
        self.NumTriangles = len(tris)
        self.IsClosed = False

    def get_Triangle(self, i):
        return Tri(self._t[i])


class FakeDS(object):
    def __init__(self, geometry, key="GAUSS_KABUK_01", app="Dynamo.STL.GaussShell", eid=1658697):
        self.ApplicationId, self.ApplicationDataId, self.Name = app, key, key
        self.Id = types.SimpleNamespace(Value=eid)
        self.UniqueId = "fake-unique-id"
        self.Category = types.SimpleNamespace(Name="Generic Models")
        self._g = geometry

    def get_Geometry(self, opts):
        return self._g


def build_stubs(shapes):
    m = {}
    clr = types.ModuleType("clr")
    clr.AddReference = lambda name: None
    m["clr"] = clr
    db = types.ModuleType("Autodesk.Revit.DB")

    class FilteredElementCollector(object):
        def __init__(self, doc):
            pass

        def OfClass(self, cls):
            return list(shapes)

    class DirectShape(object):
        pass

    class Options(object):
        pass

    db.FilteredElementCollector, db.DirectShape, db.Options = FilteredElementCollector, DirectShape, Options
    db.ViewDetailLevel = types.SimpleNamespace(Fine="Fine")
    db.Mesh, db.Solid, db.GeometryInstance = Mesh, Solid, GeometryInstance
    db.UnitUtils = types.SimpleNamespace(ConvertFromInternalUnits=lambda v, u: v * F2M)
    db.UnitTypeId = types.SimpleNamespace(Meters="m")
    for name in ("Autodesk", "Autodesk.Revit"):
        m[name] = types.ModuleType(name)
    m["Autodesk.Revit.DB"] = db
    rs = types.ModuleType("RevitServices")
    rp = types.ModuleType("RevitServices.Persistence")
    doc = types.SimpleNamespace(Title="Fake", PathName="", IsFamilyDocument=False,
                                Application=types.SimpleNamespace(VersionBuild="fake"))
    rp.DocumentManager = types.SimpleNamespace(Instance=types.SimpleNamespace(CurrentDBDocument=doc))
    m["RevitServices"], m["RevitServices.Persistence"] = rs, rp
    return m


# ------------------------------------------------------------ synthetic shapes (feet)
def cube_tris(n, h=100.0):
    """Closed cube, 6 faces, n x n quads per face split in 2 triangles, outward CCW. Returns (points, tris)."""
    pts, idx, tris = [], {}, []

    def vid(p):
        k = tuple(round(c, 6) for c in p)
        if k not in idx:
            idx[k] = len(pts)
            pts.append(k)
        return idx[k]

    faces = [((1, 0, 0), (0, 1, 0), (0, 0, 1)), ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
             ((0, 1, 0), (0, 0, 1), (1, 0, 0)), ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
             ((0, 0, 1), (1, 0, 0), (0, 1, 0)), ((0, 0, -1), (0, 1, 0), (1, 0, 0))]   # (normal, u, v), u x v = normal

    def P(nv, u, v, i, j):
        a = -h + 2 * h * i / n
        b = -h + 2 * h * j / n
        return tuple(nv[k] * h + u[k] * a + v[k] * b for k in range(3))

    for nv, u, v in faces:
        for i in range(n):
            for j in range(n):
                p00, p10, p11, p01 = (vid(P(nv, u, v, i, j)), vid(P(nv, u, v, i + 1, j)),
                                      vid(P(nv, u, v, i + 1, j + 1)), vid(P(nv, u, v, i, j + 1)))
                tris.append((p00, p10, p11))
                tris.append((p00, p11, p01))
    return pts, tris


def unshared(pts, tris):
    """Revit-style 'one vertex per triangle corner' variant of the same triangles."""
    v2, t2 = [], []
    for a, b, c in tris:
        base = len(v2)
        v2 += [pts[a], pts[b], pts[c]]
        t2.append((base, base + 1, base + 2))
    return v2, t2


def two_meshes(pts, tris, split):
    """Split into one indexed mesh + one unshared-vertex mesh to exercise cross-mesh welding."""
    a = FakeMesh(pts, tris[:split])
    v2, t2 = unshared(pts, tris[split:])
    return [a, FakeMesh(v2, t2)]


# ------------------------------------------------------------ run the node under stubs
def run_node(src, shapes, key="GAUSS_KABUK_01", B=10.0):
    out_dir = tempfile.mkdtemp(prefix="shellaudit_")
    saved = {k: sys.modules.get(k) for k in build_stubs(shapes)}
    sys.modules.update(build_stubs(shapes))
    try:
        g = {"IN": [out_dir, key, B], "__name__": "node"}
        t0 = time.time()
        exec(compile(src, "node.py", "exec"), g)
        dt = time.time() - t0
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    path = os.path.join(out_dir, "shell_mesh_audit_result.json")
    res = json.load(io.open(path, encoding="utf-8")) if os.path.isfile(path) else None
    return g["OUT"], res, dt, out_dir


FAILS = []


def check(label, got, want):
    ok = got == want
    print("  %-52s got=%-8s want=%-8s %s" % (label, got, want, "ok" if ok else "FAIL"))
    if not ok:
        FAILS.append(label)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = io.open(sys.argv[1], encoding="utf-8").read()
    pts, tris = cube_tris(4)
    n_tri = len(tris)          # 192
    interior = 2               # a triangle on the +X face that is not on a cube edge? checked via counts below

    print("A  clean cube, 2 meshes (indexed + unshared)")
    out, res, dt, _ = run_node(src, [FakeDS([m for m in two_meshes(pts, tris, 100)])])
    d = res["data"]
    check("status", out["status"], "ok")
    check("triangles", d["counts"]["triangles"], 192)
    check("vertices_welded (6n^2+2)", d["counts"]["vertices_welded"], 98)
    check("unique_edges (3F/2)", d["counts"]["unique_edges"], 288)
    check("open_edges", d["open_edges"]["count"], 0)
    check("non_manifold", d["non_manifold_edges"]["count"], 0)
    check("winding inconsistent", d["winding"]["inconsistent_edges"], 0)
    check("sharp edges >=30deg (12 cube edges x n)", d["dihedral"]["sharp_edges"], 48)
    check("degenerate", d["triangle_quality"]["degenerate"], 0)
    check("sliver", d["triangle_quality"]["sliver_not_degenerate"], 0)
    check("bounds max x (m)", d["bounds_m"]["max"][0], round(100 * F2M, 3))
    check("bin table covers sharp edges", sum(int(r.split(",")[4]) for r in d["bins"]["table_rows_worst_first"]), 48)
    print("   OUT keys:", sorted(out)[:6], "...; json bytes:", os.path.getsize(os.path.join(_, "shell_mesh_audit_result.json")))

    print("B  one triangle removed (hole)")
    tb = list(tris)
    victim = next(i for i, t in enumerate(tb) if all(abs(pts[v][2] - 100) < 1e-6 for v in t) and
                  all(abs(abs(pts[v][0]) - 100) > 1e-6 and abs(abs(pts[v][1]) - 100) > 1e-6 for v in t))
    del tb[victim]
    out, res, dt, _ = run_node(src, [FakeDS(two_meshes(pts, tb, 100))])
    check("open_edges (3 sides of the hole)", res["data"]["open_edges"]["count"], 3)
    check("triangles", res["data"]["counts"]["triangles"], 191)

    print("C  one interior triangle flipped")
    tc = list(tris)
    a, b, c = tc[victim]
    tc[victim] = (a, c, b)
    out, res, dt, _ = run_node(src, [FakeDS(two_meshes(pts, tc, 100))])
    check("winding inconsistent (3 edges)", res["data"]["winding"]["inconsistent_edges"], 3)
    check("sharp edges unchanged (mirror fix)", res["data"]["dihedral"]["sharp_edges"], 48)

    print("D  duplicate triangle")
    td = list(tris) + [tris[victim]]
    out, res, dt, _ = run_node(src, [FakeDS(two_meshes(pts, td, 100))])
    check("duplicate_triangles", res["data"]["counts"]["duplicate_triangles"], 1)
    check("non_manifold edges", res["data"]["non_manifold_edges"]["count"], 3)

    print("E  floating sliver + floating degenerate triangle")
    pe = list(pts) + [(0, 0, 300), (100, 0, 300), (100, 3, 300), (0, 0, 400), (50, 0, 400), (100, 0, 400)]
    te = list(tris) + [(len(pts), len(pts) + 1, len(pts) + 2), (len(pts) + 3, len(pts) + 4, len(pts) + 5)]
    out, res, dt, _ = run_node(src, [FakeDS(two_meshes(pe, te, 100))])
    q = res["data"]["triangle_quality"]
    check("sliver_not_degenerate", q["sliver_not_degenerate"], 1)
    check("degenerate", q["degenerate"], 1)
    check("open edges (2 floating triangles x 3)", res["data"]["open_edges"]["count"], 6)
    check("worst sliver min angle ~1.7 deg", round(q["worst_slivers_by_min_angle"][0]["min_angle_deg"], 1), 1.7)

    print("F  GeometryInstance wrapper + a Solid")
    inner = two_meshes(pts, tris, 100) + [Solid()]
    out, res, dt, _ = run_node(src, [FakeDS([GeometryInstance(inner)])])
    check("instances/solids", (res["data"]["geometry_objects"]["geometry_instances"],
                               res["data"]["geometry_objects"]["solids"]), (1, 1))
    check("triangles via instance", res["data"]["counts"]["triangles"], 192)

    print("G  key not found -> status error, no crash")
    out, res, dt, _ = run_node(src, [FakeDS(two_meshes(pts, tris, 100), key="OTHER")])
    check("status", out["status"], "error")
    check("message names the key", "GAUSS_KABUK_01" in out["message"] and "OTHER" in out["message"], True)
    check("error json written", res is not None and res["status"] == "error", True)

    print("H  two shapes with the same key -> error")
    out, res, dt, _ = run_node(src, [FakeDS(two_meshes(pts, tris, 100), eid=1), FakeDS(two_meshes(pts, tris, 100), eid=2)])
    check("status", out["status"], "error")

    if "--big" in sys.argv:
        print("I  timing, ~160k triangles (smooth wave surface)")
        import math
        nx, ny = 400, 200
        bp = [(i * 3.0, j * 3.0, 20 * math.sin(i / 25.0) * math.cos(j / 20.0)) for i in range(nx + 1) for j in range(ny + 1)]
        bt = []
        for i in range(nx):
            for j in range(ny):
                p00 = i * (ny + 1) + j
                p10 = (i + 1) * (ny + 1) + j
                bt += [(p00, p10, p10 + 1), (p00, p10 + 1, p00 + 1)]
        out, res, dt, _ = run_node(src, [FakeDS([FakeMesh(bp, bt)])])
        print("   triangles=%d seconds=%.1f (stub extraction is cheaper than pythonnet)" % (len(bt), dt))
        print("   stages:", [(s["stage"], s["t_s"]) for s in res["data"]["timings_s"]["stages"]])
        print("   open edges (plane boundary):", res["data"]["open_edges"]["count"], " expected", 2 * (nx + ny))

    print("\nRESULT:", "ALL OK" if not FAILS else "FAILED: " + "; ".join(FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
