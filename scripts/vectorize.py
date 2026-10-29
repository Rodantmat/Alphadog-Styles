"""Raster pair sheet -> clean production vectors. Usage: python vectorize.py <pair.png> <out_prefix>
Splits front emblem / back print, upscales, smooths, thresholds, traces with potrace -> SVG (hard edges, no semi-transparent pixels),
renders transparent PNGs (black ink and white ink) at print size."""
import sys, io, os, numpy as np, cv2, potrace, cairosvg
from PIL import Image
src, pre = sys.argv[1], sys.argv[2]
g = cv2.imread(src, 0); S = 4
g = cv2.resize(g, None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC)
g = cv2.GaussianBlur(g, (0, 0), 2.2)
ink = g < 140
ink = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(bool)
n, lab, st, _ = cv2.connectedComponentsWithStats(ink.astype(np.uint8), 8)
for i in range(1, n):                       # despeckle
    if st[i, cv2.CC_STAT_AREA] < 400: ink[lab == i] = False
cols = ink.any(0); W = len(cols); lo, hi = int(W * .3), int(W * .7)
gap, best, run = lo, 0, 0
for x in range(lo, hi):                     # widest empty column run between front and back
    run = run + 1 if not cols[x] else 0
    if run > best: best, gap = run, x - run // 2
parts = {"front": ink[:, :gap], "back": ink[:, gap:]}
def path_d(mask):
    plist = potrace.Bitmap(~mask).trace(turdsize=30, alphamax=1.1, opttolerance=0.6)
    d = []
    for c in plist:
        s = c.start_point; d.append(f"M{s.x:.1f},{s.y:.1f}")
        for sg in c.segments:
            if sg.is_corner: d.append(f"L{sg.c.x:.1f},{sg.c.y:.1f}L{sg.end_point.x:.1f},{sg.end_point.y:.1f}")
            else: d.append(f"C{sg.c1.x:.1f},{sg.c1.y:.1f} {sg.c2.x:.1f},{sg.c2.y:.1f} {sg.end_point.x:.1f},{sg.end_point.y:.1f}")
        d.append("Z")
    return "".join(d)
for name, m in parts.items():
    if name == "front" and int(os.environ.get("FRONT_THICKEN", "0")) > 0:
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=int(os.environ["FRONT_THICKEN"])).astype(bool)
    ys, xs = np.where(m); m = m[max(ys.min() - 20, 0):ys.max() + 20, max(xs.min() - 20, 0):xs.max() + 20]
    h, w = m.shape; d = path_d(m)
    svg = lambda col: f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><path d="{d}" fill="{col}" fill-rule="evenodd"/></svg>'
    open(f"{pre}_{name}.svg", "w").write(svg("#000"))
    tall = 5400 if name == "back" else 1200
    for col, tag in (("#000", "black"), ("#fff", "white")):
        png = cairosvg.svg2png(bytestring=svg(col).encode(), output_height=tall)
        im = Image.open(io.BytesIO(png)).convert("RGBA")
        a = np.asarray(im).copy(); a[..., 3] = np.where(a[..., 3] > 127, 255, 0)   # hard alpha
        Image.fromarray(a).save(f"{pre}_{name}_{tag}ink.png")
    print(name, w, h, len(d) // 1000, "KB path")
