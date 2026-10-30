"""Line eyes pass 4: every eye gets a white iris interior, a smaller pupil offset by ONE shared gaze, and a glint.
usage: eye_fix3.py SRC_BASE DST_DIR"""
import cv2, numpy as np, json, os, sys
SRC, DST = sys.argv[1], sys.argv[2]
res = json.load(open("out/eyes/merged_line.json"))
os.makedirs(DST, exist_ok=True); log = {}
GX, GY = 0.40, -0.15; PR = 0.58
def disc(sub, x, y, r, col):
    cv2.circle(sub, (int(round(x*16)), int(round(y*16))), int(round(r*16)), col, -1, lineType=cv2.LINE_AA, shift=4)
def draw_pupil(sub, ccx, ccy, r_iris, inside):
    """inside: bool mask of iris interior (or None)"""
    rp = max(1.5, PR*r_iris); room = max(0.0, r_iris - rp - 1.2)
    px, py = ccx+GX*room, ccy+GY*room
    if inside is not None:
        yy, xx = np.mgrid[0:sub.shape[0], 0:sub.shape[1]]
        for _ in range(12):
            if inside[((xx-px)**2+(yy-py)**2) <= (rp+0.6)**2].all(): break
            px += (ccx-px)*0.3; py += (ccy-py)*0.3
    disc(sub, px, py, rp, 0)
    if rp >= 3.0: disc(sub, px+0.36*rp, py-0.36*rp, max(1.2, 0.24*rp), 255)
for key, eyes in res.items():
    nm = os.path.basename(key); d = key.split('/')[2]
    if nm.endswith("__cool.jpg"): continue
    g = cv2.imread(f"{SRC}/{d}/{nm}", 0); H, W = g.shape; m = (g < 128).astype(np.uint8); out = g.copy(); lg = []
    for e in eyes:
        if "box_2d" not in e: e = {"box_2d": json.loads(e["box"])}
        y0, x0, y1, x1 = e["box_2d"]
        bx0, bx1, by0, by1 = x0*W/1000, x1*W/1000, y0*H/1000, y1*H/1000
        cx, cy = (bx0+bx1)/2, (by0+by1)/2; bw = max(bx1-bx0, by1-by0); R = max(bw, 14)
        X0, X1, Y0, Y1 = max(0, int(cx-R)), min(W, int(cx+R)), max(0, int(cy-R)), min(H, int(cy+R))
        win = m[Y0:Y1, X0:X1]; sub = out[Y0:Y1, X0:X1]
        n, lab, st, cen = cv2.connectedComponentsWithStats((1-win).astype(np.uint8), 4)
        best = None
        for k in range(1, n):
            x, y, w, h, a = st[k]
            if x == 0 or y == 0 or x+w >= win.shape[1] or y+h >= win.shape[0]: continue
            if a < 8 or a > 1.6*bw*bw or max(w, h) > 1.7*max(1, min(w, h)) or w > 1.3*bw or h > 1.3*bw: continue
            if np.hypot(cen[k][0]-(cx-X0), cen[k][1]-(cy-Y0)) > 0.4*R: continue
            if best is None or w*h > best[0]: best = (w*h, k)
        done = False
        dtb = cv2.distanceTransform(win, cv2.DIST_L2, 5)
        yy, xx = np.mgrid[0:win.shape[0], 0:win.shape[1]]
        near = (xx-(cx-X0))**2+(yy-(cy-Y0))**2 <= (0.45*R)**2
        dm = np.where(near, dtb, 0); iy, ix = np.unravel_index(np.argmax(dm), dm.shape); rs = float(dm[iy, ix])
        if rs >= max(2.6, 0.13*bw):                              # route B: solid pupil present -> erase exactly that disc
            # refine centre/radius: centroid of the black pixels with dt >= 0.7*rs connected to the peak
            core = (dtb >= 0.72*rs).astype(np.uint8); nb, lb = cv2.connectedComponents(core, connectivity=8)
            cm = lb == lb[iy, ix]; ys, xs = np.nonzero(cm); ccx, ccy = xs.mean(), ys.mean()
            r_p = rs
            sub[((xx-ccx)**2+(yy-ccy)**2) <= (r_p+0.6)**2] = 255
            draw_pupil(sub, ccx, ccy, r_p*1.12+0.8, None); lg.append(f"B r={r_p:.1f}"); done = True
        elif best is not None:                                   # route A: hollow iris ring
            hole = (lab == best[1]).astype(np.uint8)
            cnts, _ = cv2.findContours(hole, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            filled = np.zeros_like(hole); cv2.drawContours(filled, cnts, -1, 1, -1)
            filled = cv2.morphologyEx(filled, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))
            dt = cv2.distanceTransform(filled, cv2.DIST_L2, 5); r_in = float(dt.max())
            if r_in >= 0.15*bw and r_in >= 2.4:
                ys, xs = np.nonzero(filled); ccx, ccy = xs.mean(), ys.mean()
                sub[filled > 0] = 255
                draw_pupil(sub, ccx, ccy, r_in, filled > 0); lg.append(f"A r={r_in:.1f}"); done = True
        if not done: lg.append("skip"); continue
        out[Y0:Y1, X0:X1] = sub
    cv2.imwrite(f"{DST}/{nm}", out, [cv2.IMWRITE_JPEG_QUALITY, 95]); log[nm] = lg
json.dump(log, open(f"{DST}/eye_log.json", "w"), indent=0)
from collections import Counter
print(Counter(x.split()[0] for v in log.values() for x in v))
