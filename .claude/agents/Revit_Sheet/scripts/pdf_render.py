"""Render PDF pages (and optional crops) to PNG + dump text/vector stats.
Usage: python pdf_render.py <pdf> <outdir> [dpi]
       python pdf_render.py --crop <pdf> <out.png> x0 y0 x1 y1 [dpi]   (fractions 0-1 of page)
"""
import sys, os, collections
import warnings; warnings.filterwarnings("ignore")
import pymupdf

def main():
    if sys.argv[1] == "--crop":
        pdf, out = sys.argv[2], sys.argv[3]
        x0, y0, x1, y1 = map(float, sys.argv[4:8])
        dpi = int(sys.argv[8]) if len(sys.argv) > 8 else 200
        d = pymupdf.open(pdf); p = d[0]; r = p.rect
        clip = pymupdf.Rect(r.x0 + x0*r.width, r.y0 + y0*r.height, r.x0 + x1*r.width, r.y0 + y1*r.height)
        p.get_pixmap(dpi=dpi, clip=clip).save(out); return
    pdf, outdir = sys.argv[1], sys.argv[2]
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    os.makedirs(outdir, exist_ok=True)
    d = pymupdf.open(pdf)
    stem = os.path.splitext(os.path.basename(pdf))[0]
    for i, p in enumerate(d):
        r = p.rect
        print(f"page {i+1}: {r.width:.1f}x{r.height:.1f} pt = {r.width/72*25.4:.0f}x{r.height/72*25.4:.0f} mm")
        p.get_pixmap(dpi=dpi).save(os.path.join(outdir, f"{stem}_p{i+1}.png"))
        w = collections.Counter(round(dr.get("width") or 0, 2) for dr in p.get_drawings())
        print("line widths (pt->count):", sorted(w.items())[:25])
        print("line widths mm:", sorted((round(k*25.4/72,2), v) for k, v in w.items())[:25])
        print("fonts:", d.get_page_fonts(i)[:6])

main()
