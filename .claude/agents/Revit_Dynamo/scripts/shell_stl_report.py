# Offline report on an engine-produced shell STL: bbox, mesh quality, hot spots, cross-sections.
import sys, json, os
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

stl, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
m = trimesh.load(stl, process=True)  # merge duplicate vertices so face adjacency works
V, F = np.asarray(m.vertices), np.asarray(m.faces)
print("triangles", len(F), "vertices", len(V))
print("bbox min", V.min(0).round(2), "max", V.max(0).round(2))

# --- triangle quality
p = V[F]
e = np.stack([p[:, 1] - p[:, 0], p[:, 2] - p[:, 1], p[:, 0] - p[:, 2]], 1)
el = np.linalg.norm(e, axis=2)
area = 0.5 * np.linalg.norm(np.cross(e[:, 0], -e[:, 2]), axis=1)
ratio = el.max(1) / np.maximum(el.min(1), 1e-12)
print("area<1e-6:", int((area < 1e-6).sum()), "| edge ratio>10:", int((ratio > 10).sum()),
      "| edge ratio>30:", int((ratio > 30).sum()), "| edge len median/p99/max:",
      np.median(el).round(3), np.percentile(el, 99).round(3), el.max().round(3))

sl = ratio > 30
c = p[sl].mean(1)
if len(c):
    H2, xe2, ye2 = np.histogram2d(c[:,0], c[:,1], bins=[np.arange(-30,510,30), np.arange(20,480,30)])
    idx2 = np.dstack(np.unravel_index(np.argsort(-H2.ravel())[:8], H2.shape))[0]
    print("sliver(ratio>30) hot cells (x,y centre,count):", [(int(xe2[i]+15), int(ye2[j]+15), int(H2[i,j])) for i,j in idx2 if H2[i,j]>0])
    print("sliver z-range:", c[:,2].min().round(1), c[:,2].max().round(1))
# --- dihedral angles on shared edges (use face adjacency)
adj = m.face_adjacency
ang = np.degrees(m.face_adjacency_angles)
for t in (10, 20, 30, 45, 90):
    print(f"adjacent-face angle >= {t} deg:", int((ang >= t).sum()))
sharp = ang >= 30
mid = m.vertices[m.face_adjacency_edges].mean(1)[sharp]
print("sharp(>=30deg) edges:", int(sharp.sum()))
if sharp.sum():
    H, xe, ye = np.histogram2d(mid[:, 0], mid[:, 1], bins=[np.arange(-30, 510, 30), np.arange(20, 480, 30)])
    idx = np.dstack(np.unravel_index(np.argsort(-H.ravel())[:10], H.shape))[0]
    print("top 30 m cells with sharp edges (x,y centre, count):",
          [(int(xe[i] + 15), int(ye[j] + 15), int(H[i, j])) for i, j in idx if H[i, j] > 0])

# --- cross sections perpendicular to X (end-on view of the arms/bridge)
fig, axs = plt.subplots(2, 3, figsize=(15, 8))
xs = [20, 60, 100, 200, 300, 380]
for ax, x in zip(axs.ravel(), xs):
    sec = m.section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0])
    if sec is None:
        ax.set_title(f"x={x}: no section"); continue
    for ent in sec.entities:
        pts = sec.vertices[ent.points]
        ax.plot(pts[:, 1], pts[:, 2], "k-", lw=0.6)
    ax.set_aspect("equal"); ax.set_title(f"section x={x} m (Y horizontal, Z vertical)")
plt.tight_layout(); plt.savefig(os.path.join(outdir, "sections_x.png"), dpi=110); plt.close(fig)

# --- bridge centre-line section along Y direction through the middle (z extent upper vs lower)
for x in (150, 200, 250):
    sec = m.section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0])
    if sec is None: continue
    pts = np.vstack([sec.vertices[e.points] for e in sec.entities])
    # take the central bridge band by y near bridge centre line
    yc = np.median(pts[:, 1])
    band = pts[np.abs(pts[:, 1] - yc) < 2]
    print(f"x={x}: central band y~{yc:.1f}: z min {band[:,2].min():.2f}  z max {band[:,2].max():.2f}  "
          f"thickness {band[:,2].max()-band[:,2].min():.2f}  centre z {(band[:,2].max()+band[:,2].min())/2:.2f}")

# --- top-view and side-view silhouettes (cheap: scatter of subsampled vertices)
sub = V[np.random.default_rng(0).choice(len(V), min(len(V), 120000), replace=False)]
fig, axs = plt.subplots(1, 2, figsize=(15, 6))
axs[0].scatter(sub[:, 0], sub[:, 1], s=0.2, c=sub[:, 2], cmap="viridis"); axs[0].set_aspect("equal"); axs[0].set_title("top view (colour=Z)")
axs[1].scatter(sub[:, 0], sub[:, 2], s=0.2, c=sub[:, 1], cmap="viridis"); axs[1].set_aspect("equal"); axs[1].set_title("side view X-Z")
plt.tight_layout(); plt.savefig(os.path.join(outdir, "top_side.png"), dpi=100); plt.close(fig)
print("wrote", outdir)
