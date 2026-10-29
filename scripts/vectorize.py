"""Raster pair sheet -> clean production vectors. Usage: python vectorize.py <pair.png> <out_prefix>
Splits front emblem / back print, upscales, smooths, thresholds, traces with potrace -> SVG (hard edges, no semi-transparent pixels),
renders transparent PNGs (black ink and white ink) at print size."""
import sys, io, os, numpy as np, cv2, potrace, cairosvg
from scipy import ndimage
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
# split front emblem / back print: 2-means on component x-centres (weighted by area), robust when the two touch in x
n, lab, st, cen = cv2.connectedComponentsWithStats(ink.astype(np.uint8), 8)
W = ink.shape[1]; ids = [i for i in range(1, n)]
xs_ = np.array([cen[i][0] for i in ids]); ar_ = np.array([st[i, cv2.CC_STAT_AREA] for i in ids], float)
c = np.array([W * .22, W * .72])
for _ in range(20):
    asg = (np.abs(xs_ - c[1]) < np.abs(xs_ - c[0])).astype(int)
    for k in (0, 1):
        if (asg == k).any(): c[k] = np.average(xs_[asg == k], weights=ar_[asg == k])
front_ids = [i for i, a_ in zip(ids, asg) if a_ == 0]; back_ids = [i for i, a_ in zip(ids, asg) if a_ == 1]
parts = {"front": np.isin(lab, front_ids), "back": np.isin(lab, back_ids)}
def dark_garment_mask(m):
    """Naive inversion turns black eyes/noses/lenses into glowing white blobs. For dark shirts: solid blobs become
    white ring + dark pupil (shirt shows through) + white catchlight, so eyes keep their focal contrast."""
    ink = m.astype(np.uint8)
    dt = cv2.distanceTransform(ink, cv2.DIST_L2, 5)
    ridge = (dt >= cv2.dilate(dt, np.ones((3, 3), np.uint8)) * 0.999) & (dt > 1.5)
    w = float(np.median(dt[ridge])) if ridge.any() else 4.0        # line half-width
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * int(r) + 1, 2 * int(r) + 1))
    blobs = cv2.morphologyEx(ink, cv2.MORPH_OPEN, k(max(2.0 * w, 3)))
    n, lab = cv2.connectedComponents(blobs)
    out = ink.copy()
    for i in range(1, n):
        b = (lab == i).astype(np.uint8)
        filled = ndimage.binary_fill_holes(b).astype(np.uint8)
        inner = cv2.erode(filled, k(max(2.0 * w, 3)))                # ring thickness = one line width
        if inner.sum() < 30: continue                                 # too small to hollow: stays solid white
        out[inner > 0] = 0                                            # dark pupil / lens
        holes = (filled > 0) & (b == 0) & (inner > 0)                 # catchlights / glints become white
        out[holes] = 1
    return out.astype(bool)
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
    h, w = m.shape; d = path_d(m); dw = path_d(dark_garment_mask(m))
    svg = lambda col, dd=None: f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><path d="{dd or d}" fill="{col}" fill-rule="evenodd"/></svg>'
    open(f"{pre}_{name}.svg", "w").write(svg("#000"))
    tall = 5400 if name == "back" else 1200
    for col, tag in (("#000", "black"), ("#fff", "white")):
        png = cairosvg.svg2png(bytestring=(svg(col, dw) if tag == "white" else svg(col)).encode(), output_height=tall)
        im = Image.open(io.BytesIO(png)).convert("RGBA")
        a = np.asarray(im).copy(); a[..., 3] = np.where(a[..., 3] > 127, 255, 0)   # hard alpha
        Image.fromarray(a).save(f"{pre}_{name}_{tag}ink.png")
    print(name, w, h, len(d) // 1000, "KB path")
