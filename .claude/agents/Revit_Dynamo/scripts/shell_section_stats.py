import sys, numpy as np, trimesh
m = trimesh.load(sys.argv[1], process=True)
print("triangles", len(m.faces))
for x in (100, 150, 200, 250, 300):
    sec = m.section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0])
    pts = np.vstack([sec.vertices[e.points] for e in sec.entities])
    yc = np.median(pts[:, 1])
    lo, hi = pts[:, 1].min(), pts[:, 1].max()
    ears = pts[(pts[:, 1] < lo + 0.6) | (pts[:, 1] > hi - 0.6)]
    zs = np.median(ears[:, 2])
    top, bot = pts[:, 2].max(), pts[:, 2].min()
    print(f"x={x:3d}  width {hi-lo:5.1f}  seam z {zs:5.1f}  top {top:5.1f} (+{top-zs:4.1f})  bottom {bot:5.1f} (-{zs-bot:4.1f})")
