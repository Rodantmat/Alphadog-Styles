"""nb3_compose.py SELDIR EYES.json OUTDIR
KEEP the Gemini-drawn eyes of the approved style (lid outline + big solid pupil + white glint) in LIGHT art.
DARK art = same drawing inverted, but each solid pupil is converted to the approved dark eye: white lid outline (kept),
black interior, ONE thin white iris ring (the pupil outline) + ONE white highlight dot."""
import sys, os, json, glob, numpy as np, cv2
from PIL import Image
sys.path.insert(0, '/home/claude/alphadog-styles/scripts')
from nb_lib import split_masks
from nb_compose import stroke_med, circ
S = 2
IRIS = {"geo_vira_lata": ("ring", "iris"), "line_minpin": ("ring", "iris"), "line_vira_lata": ("iris", "iris")}   # (front, back): eye already has a thin iris ring around the pupil
for k_ in ("geo_lhasa_apso", "geo_miniature_pinscher", "line_lhasa_apso"): IRIS[k_] = ("ring", "ring")
IRIS["line_miniature_pinscher"] = ("iris", "iris")
NORMALIZE = set(json.loads(os.environ.get("NORM", "[]")))   # "name:idx" eyes to rebuild as standard round pupil
def find_pupil(ink, bx0, bx1, by0, by1):
    bs = max(bx1-bx0, by1-by0); cx, cy = (bx0+bx1)/2, (by0+by1)/2
    H, W = ink.shape; pad = int(1.2*bs)
    X0, X1, Y0, Y1 = max(0, int(cx-pad)), min(W, int(cx+pad)), max(0, int(cy-pad)), min(H, int(cy+pad))
    win = ink[Y0:Y1, X0:X1].astype(np.uint8)
    # fill glint holes (small enclosed white components)
    nw, lw, sw_, cw = cv2.connectedComponentsWithStats((1-win).astype(np.uint8), 4)
    w2 = win.copy(); holes = []
    for j in range(1, nw):
        x, y, w, h, ar = sw_[j]
        if x == 0 or y == 0 or x+w >= win.shape[1] or y+h >= win.shape[0]: continue
        if ar <= 0.16*bs*bs*0.5 and ar >= 0.6*np.pi*(w/2)*(h/2) and max(w, h) <= 1.5*min(w, h):
            w2[lw == j] = 1; holes.append((j, cw[j][0], cw[j][1], ar))
    dt = cv2.distanceTransform(w2, cv2.DIST_L2, 5)
    yy, xx = np.mgrid[0:win.shape[0], 0:win.shape[1]]
    near = (xx-(cx-X0))**2+(yy-(cy-Y0))**2 <= (0.5*bs)**2
    d = np.where(near, dt, 0); iy, ix = np.unravel_index(np.argmax(d), d.shape); rs = float(d[iy, ix])
    if rs < max(5.0, 0.09*bs): return None
    # refine centre: centroid of pixels with dt >= 0.9 rs connected to peak
    core = (dt >= 0.88*rs).astype(np.uint8); n, lab = cv2.connectedComponents(core, connectivity=8)
    ys, xs = np.nonzero(lab == lab[iy, ix]); pcx, pcy = xs.mean(), ys.mean()
    disc = (xx-pcx)**2+(yy-pcy)**2 <= (rs+0.5)**2
    g = None
    cand = [(ar, hx, hy) for (j, hx, hy, ar) in holes if (hx-pcx)**2+(hy-pcy)**2 <= (1.05*rs)**2 and ar >= 6]
    if cand:
        ar, hx, hy = max(cand); g = (hx+X0, hy+Y0, float(np.sqrt(ar/np.pi)))
    # existing thin iris ring tightly around the pupil? (enclosed small white gap bounded by a THIN line, not the lid)
    ring = cv2.dilate(disc.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=3) > 0
    ids = set(np.unique(lw[ring & (win == 0)])) - {0}
    hid = set(h_[0] for h_ in holes); iris = False
    dtw = cv2.distanceTransform(win, cv2.DIST_L2, 5)
    for j in ids:
        if j in hid: continue
        x, y, w, h, ar = sw_[j]
        if x == 0 or y == 0 or x+w >= win.shape[1] or y+h >= win.shape[0]: continue
        if not (0.3*np.pi*rs*rs < ar <= 1.5*np.pi*rs*rs): continue
        gm = (lw == j).astype(np.uint8); outer = (cv2.dilate(gm, np.ones((3, 3), np.uint8), iterations=2) > 0) & (win == 1) & ~disc
        if outer.sum() < 10: continue
        th = 2*float(np.percentile(dtw[outer], 90))
        if th <= 0.27*rs: iris = True
    fl = disc.astype(np.uint8)
    return dict(cx=pcx+X0, cy=pcy+Y0, r=rs, glint=g, X0=X0, Y0=Y0, fill=fl, iris=iris)
def build(path, boxes, name):
    g = np.array(Image.open(path).convert("L"))
    g2 = cv2.resize(g, None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC).astype(np.float32)
    a = (np.clip(((255-g2)/255.0-0.25)/0.5, 0, 1)*255).astype(np.uint8)
    H, W = a.shape; binm = a > 128
    fm, bm = split_masks(binm)
    cut = (np.where(fm)[1].max()+np.where(bm)[1].min())/2 if np.where(fm)[1].max() < np.where(bm)[1].min() else W/2
    sm = {"front": stroke_med(fm), "back": stroke_med(bm)}
    L = a.copy(); D = a.copy(); info = []
    for i, e in enumerate(boxes):
        y0, x0, y1, x1 = e["box_2d"]; bx0, bx1, by0, by1 = x0*W/1000, x1*W/1000, y0*H/1000, y1*H/1000
        side = "front" if (bx0+bx1)/2 < cut else "back"
        p = find_pupil(binm, bx0, bx1, by0, by1)
        if p is None: info.append((round((bx0+bx1)/2), round((by0+by1)/2), "nopupil")); continue
        r = p["r"]; cx, cy = p["cx"], p["cy"]; sw = sm[side]
        kk = [k_ for k_ in IRIS if name.startswith(k_)]
        if kk: p["iris"] = IRIS[kk[0]][0 if side == "front" else 1] == "iris"
        if f"{name}:{i}" in NORMALIZE:                       # rebuild as standard round pupil + glint (same gaze as approved)
            X0, Y0, fl = p["X0"], p["Y0"], p["fill"]
            sub = L[Y0:Y0+fl.shape[0], X0:X0+fl.shape[1]]; sub[fl > 0] = 0
            circ(L, cx, cy, r, 255, -1); circ(L, cx+0.36*r, cy-0.36*r, 0.24*r, 0, -1)
            g_ = (cx+0.36*r, cy-0.36*r, 0.24*r); p["glint"] = g_
            D[Y0:Y0+fl.shape[0], X0:X0+fl.shape[1]][fl > 0] = 0
        # ---- DARK: clear the filled pupil, draw ring + highlight
        X0, Y0, fl = p["X0"], p["Y0"], p["fill"]
        if p["iris"]:
            yy_, xx_ = np.mgrid[0:fl.shape[0], 0:fl.shape[1]]
            fl = ((xx_-(cx-X0))**2+(yy_-(cy-Y0))**2 <= (0.88*r)**2).astype(np.uint8)
        D[Y0:Y0+fl.shape[0], X0:X0+fl.shape[1]][(fl > 0)] = 0
        ro = 0.88*r; t = max(0.2*r, min(0.62*sw, 0.38*r)); t = max(t, 3.2)
        if not p["iris"]: circ(D, cx, cy, ro-t/2, 255, t)
        gx, gy, gr = p["glint"] if p["glint"] else (cx+0.36*r, cy-0.36*r, 0.24*r)
        ri = ro-t                                               # inner radius of ring
        gr = max(2.6, min(gr*0.95, 0.30*ri)) if not p['iris'] else max(3.0, 0.26*r); dx, dy = gx-cx, gy-cy; dd = np.hypot(dx, dy)
        lim = max(0.0, ri-gr-1.5) if not p['iris'] else max(0.0, 0.86*r-gr)
        if dd > lim and dd > 0: dx, dy = dx/dd*lim, dy/dd*lim
        circ(D, cx+dx, cy+dy, gr, 255, -1)
        info.append((round(cx), round(cy), round(r, 1), round(t, 1), 'iris' if p['iris'] else 'ring'))
    return L, D, info, cut
if __name__ == "__main__":
    sel, ej, out = sys.argv[1:4]
    eyes = json.load(open(ej)); os.makedirs(out+"/light", exist_ok=True); os.makedirs(out+"/dark", exist_ok=True); rep = {}
    for p in sorted(glob.glob(sel+"/*.png")):
        n = os.path.basename(p); key = [k for k in eyes if k.endswith("/"+n)]
        boxes = eyes[key[0]] if key else []
        L, D, info, cut = build(p, boxes, n[:-4])
        Image.fromarray(L).save(f"{out}/light/{n}"); Image.fromarray(D).save(f"{out}/dark/{n}"); rep[n] = (info, cut)
    json.dump(rep, open(out+"/compose_log.json", "w")); print({k: v[0] for k, v in rep.items()})
