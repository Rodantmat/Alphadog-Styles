"""Paint eye depth. line: black pupil + white glint into hollow/weak eyes. geo: white glint dot into solid black eyes.
usage: eye_fix.py THEME EYES_JSON DST_DIR  (reads image paths from json keys)"""
import cv2, numpy as np, json, os, sys
theme, EJ, DST = sys.argv[1], sys.argv[2], sys.argv[3]
res = json.load(open(EJ))
os.makedirs(DST, exist_ok=True)
log = {}
def comp_at(black_mask, pt):
    n, lab, st, cen = cv2.connectedComponentsWithStats(black_mask, 8)
    return n, lab, st, cen
def line_eye(m, cx, cy, R, hb):
    """m: black=1. return (cx,cy,r_e,frac_dark) of the eye 'hole' or None"""
    H, W = m.shape
    x0, x1, y0, y1 = max(0, int(cx-R)), min(W, int(cx+R)), max(0, int(cy-R)), min(H, int(cy+R))
    win = m[y0:y1, x0:x1]
    white = (1-win).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(white, 4)
    # ---- solid pupil? (max inscribed black circle near the box centre)
    dtb = cv2.distanceTransform(win, cv2.DIST_L2, 5)
    wy, wx = np.mgrid[0:win.shape[0], 0:win.shape[1]]
    near = ((wx-(cx-x0))**2+(wy-(cy-y0))**2) <= (0.30*R)**2
    if near.any():
        dm = np.where(near, dtb, 0); iy, ix = np.unravel_index(np.argmax(dm), dm.shape); rs = float(dm[iy, ix])
        if rs >= 4.0:
            disc = ((wx-ix)**2+(wy-iy)**2) <= max(1.0, rs-1.3)**2
            nbk, lbk, _, _ = cv2.connectedComponentsWithStats(win, 8)
            cm = (lbk == lbk[iy, ix]).astype(np.uint8)
            cnts, _ = cv2.findContours(cm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            fl = np.zeros_like(cm); cv2.drawContours(fl, cnts, -1, 1, -1)
            dt2 = cv2.distanceTransform(fl, cv2.DIST_L2, 5)
            near2 = ((wx-ix)**2+(wy-iy)**2) <= (0.6*R)**2
            d2 = np.where(near2, dt2, 0); jy, jx = np.unravel_index(np.argmax(d2), d2.shape); rs2 = float(d2[jy, jx])
            holes = (fl > 0) & (cm == 0) & (((wx-jx)**2+(wy-jy)**2) <= (rs2*0.95)**2)
            has_glint = bool(holes.sum() >= 3)
            rs = max(rs, 0.85*rs2); ix, iy = jx, jy
            return ("solid", ix+x0, iy+y0, rs, has_glint)
    best = None
    for k in range(1, n):
        x, y, w, h, a = st[k]
        if x == 0 or y == 0 or x+w >= win.shape[1] or y+h >= win.shape[0]: continue   # touches window border = not enclosed
        if a < 12 or a > (R*R*2.2): continue
        d = np.hypot(cen[k][0]-(cx-x0), cen[k][1]-(cy-y0))
        if best is None or d < best[0]: best = (d, k)
    if best is None: return None
    k = best[1]
    hole = (lab == k).astype(np.uint8)
    # include black blobs fully inside the hole's bbox (existing pupil)
    x, y, w, h, a = st[k]
    filled = hole.copy()
    nb, lb, sb, cb = cv2.connectedComponentsWithStats(win, 8)
    for j in range(1, nb):
        bx, by, bw, bh, ba = sb[j]
        if bx >= x-1 and by >= y-1 and bx+bw <= x+w+1 and by+bh <= y+h+1 and ba < a*3:
            # must be wholly surrounded by the hole -> dilate hole & test
            filled[lb == j] = 1
    ys, xs = np.nonzero(filled)
    area = filled.sum()
    r_e = np.sqrt(area/np.pi)
    ccx, ccy = xs.mean()+x0, ys.mean()+y0
    yy, xx = np.mgrid[0:win.shape[0], 0:win.shape[1]]
    dark = win[((xx-(ccx-x0))**2+(yy-(ccy-y0))**2) <= (0.45*r_e)**2]
    frac = float(dark.mean()) if dark.size else 0
    # catchlight test: if the 'hole' is a small white dot surrounded by solid black, the eye already has a pupil
    ring = ((xx-(ccx-x0))**2+(yy-(ccy-y0))**2)
    ann = win[(ring > (r_e+1.0)**2) & (ring <= (r_e+4.0)**2)]
    ann2 = win[(ring > (r_e+5.0)**2) & (ring <= (r_e+9.0)**2)]
    if r_e <= 6.0 and ann.size and ann.mean() > 0.80 and ann2.size and ann2.mean() > 0.55:
        return ccx, ccy, r_e, 1.0
    return ccx, ccy, r_e, frac
def paint_line(img, m, e):
    if e[0] == "solid":
        _, sx_, sy_, rs, hg = e
        if hg: return "kept(has glint)"
        gr = max(1.4, 0.26*rs)
        cv2.circle(img, (int(round(sx_+0.34*rs)), int(round(sy_-0.34*rs))), int(round(gr)), 255, -1, lineType=cv2.LINE_AA)
        return "glint added"
    ccx, ccy, r_e, frac = e
    if frac >= 0.70: return "kept(has pupil)"
    if r_e < 2.5: return "tiny"
    rp = max(1.6, 0.60*r_e)
    cv2.circle(img, (int(round(ccx)), int(round(ccy))), int(round(rp)), 0, -1, lineType=cv2.LINE_AA)
    if rp >= 3.5:
        gr = max(1.0, 0.24*rp)
        cv2.circle(img, (int(round(ccx+0.32*rp)), int(round(ccy-0.32*rp))), int(round(gr)), 255, -1, lineType=cv2.LINE_AA)
    return "painted"
def geo_eye(m, cx, cy, R):
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    H, W = m.shape
    best = None
    for k in range(1, n):
        x, y, w, h, a = st[k]
        if a < 25 or a > R*R*6: continue
        if w > 3.2*R or h > 3.2*R: continue
        c = cen[k]; d = np.hypot(c[0]-cx, c[1]-cy)
        if d < R*0.9 and (best is None or d < best[0]): best = (d, k)
    if best is None: return None
    k = best[1]; blob = (lab == k).astype(np.uint8)
    cnts, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    hull = cv2.convexHull(cnts[0]); harea = cv2.contourArea(hull)
    solid = blob.sum()/max(1, harea)
    ys, xs = np.nonzero(blob)
    return xs.mean(), ys.mean(), np.sqrt(blob.sum()/np.pi), solid, blob
def paint_geo(img, e):
    bx, by, r_e, solid, blob = e
    if solid < 0.93: return "kept(has detail)"
    if r_e < 3.2: return "tiny"
    gr = max(1.5, 0.17*r_e)
    # glint centre: up-right of centroid, pulled inward until fully inside blob
    for f in (0.42, 0.34, 0.26, 0.18, 0.1):
        gx, gy = bx+f*r_e, by-f*r_e
        yy, xx = np.ogrid[:blob.shape[0], :blob.shape[1]]
        disc = (xx-gx)**2+(yy-gy)**2 <= (gr+1.2)**2
        if blob[disc].all(): break
    cv2.circle(img, (int(round(gx)), int(round(gy))), int(round(gr)), 255, -1, lineType=cv2.LINE_AA)
    return "painted"

def geo_eye2(m, bx0, by0, bx1, by1):
    """solid-eye finder by distance transform inside the (slightly padded) box"""
    H, W = m.shape
    pad = 0.25*max(bx1-bx0, by1-by0)
    x0, x1, y0, y1 = max(0,int(bx0-pad)), min(W,int(bx1+pad)), max(0,int(by0-pad)), min(H,int(by1+pad))
    win = m[y0:y1, x0:x1]
    dt = cv2.distanceTransform(win, cv2.DIST_L2, 5)
    yy, xx = np.mgrid[0:win.shape[0], 0:win.shape[1]]
    inb = (xx+x0 >= bx0) & (xx+x0 <= bx1) & (yy+y0 >= by0) & (yy+y0 <= by1)
    d = np.where(inb, dt, 0)
    iy, ix = np.unravel_index(np.argmax(d), d.shape); rs = float(d[iy, ix])
    if rs < 2.4: return None
    # existing glint: enclosed white component near the centre
    white = (1-win).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(white, 4)
    has = False
    for k in range(1, n):
        x, y, w, h, a = st[k]
        if x == 0 or y == 0 or x+w >= win.shape[1] or y+h >= win.shape[0]: continue
        if a < 3 or a > 0.7*np.pi*rs*rs*1.5 or w < 0.35*rs or h < 0.35*rs: continue
        if np.hypot(cen[k][0]-ix, cen[k][1]-iy) <= 1.6*rs:
            comp = (lab == k).astype(np.uint8)
            ring = cv2.dilate(comp, np.ones((3, 3), np.uint8), iterations=2) - comp
            if win[ring > 0].mean() >= 0.9: has = True
    return ix+x0, iy+y0, rs, has, (win, dt, x0, y0)
def paint_geo2(img, e):
    cx, cy, rs, has, (win, dt, x0, y0) = e
    if has: return "has_glint"
    gr = max(1.6, 0.26*rs)
    ix, iy = int(round(cx-x0)), int(round(cy-y0))
    yy, xx = np.ogrid[:win.shape[0], :win.shape[1]]
    for f in (0.45, 0.35, 0.25, 0.15, 0.0):
        gx, gy = ix+f*rs, iy-f*rs
        disc = (xx-gx)**2+(yy-gy)**2 <= (gr+1.3)**2
        if win[disc].all(): break
    else:
        return "nofit"
    cv2.circle(img, (int(round(gx+x0)), int(round(gy+y0))), int(round(gr)), 255, -1, lineType=cv2.LINE_AA)
    return "painted"
for path, eyes in res.items():
    g = cv2.imread(path, 0)
    H, W = g.shape
    m = (g < 128).astype(np.uint8)
    out = g.copy(); lg = []
    for e in eyes:
        if "box_2d" not in e:
            e = {"box_2d": json.loads(e["box"])}
        y0, x0, y1, x1 = e["box_2d"]
        cx, cy = (x0+x1)/2*W/1000, (y0+y1)/2*H/1000
        R = max((x1-x0)*W/1000, (y1-y0)*H/1000)*0.75
        if theme == "line":
            r = line_eye(m, cx, cy, R, max((x1-x0)*W/1000, (y1-y0)*H/1000)/2)
            lg.append("noeye" if r is None else paint_line(out, m, r))
        else:
            r = geo_eye2(m, x0*W/1000, y0*H/1000, x1*W/1000, y1*H/1000)
            lg.append("noblob" if r is None else paint_geo2(out, r))
    name = os.path.basename(path)
    cv2.imwrite(f"{DST}/{name}", out, [cv2.IMWRITE_JPEG_QUALITY, 95])
    log[name] = lg
json.dump(log, open(f"{DST}/eye_log.json", "w"), indent=0)
from collections import Counter
print(Counter(x for v in log.values() for x in v))
