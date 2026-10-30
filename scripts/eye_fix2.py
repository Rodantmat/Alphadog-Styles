"""Pass 2 (line theme): any eye whose iris is hollow / has only a tiny dot gets a proper black pupil + glint.
usage: eye_fix2.py SRC_BASE DST_DIR   (uses out/eyes/merged_line.json boxes; SRC_BASE contains line_p1/line_p2)"""
import cv2, numpy as np, json, os, sys
SRC, DST = sys.argv[1], sys.argv[2]
res = json.load(open("out/eyes/merged_line.json"))
os.makedirs(DST, exist_ok=True); log = {}
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
        win = m[Y0:Y1, X0:X1]; white = (1-win).astype(np.uint8)
        n, lab, st, cen = cv2.connectedComponentsWithStats(white, 4)
        best = None
        for k in range(1, n):
            x, y, w, h, a = st[k]
            if x == 0 or y == 0 or x+w >= win.shape[1] or y+h >= win.shape[0]: continue
            if a < 10 or a > 1.6*bw*bw: continue
            if max(w, h) > 1.7*max(1, min(w, h)): continue          # iris is roundish
            dd = np.hypot(cen[k][0]-(cx-X0), cen[k][1]-(cy-Y0))
            if dd > 0.38*R: continue
            if best is None or dd < best[0]: best = (dd, k)
        if best is None:
            # fallback for tiny eyes: tight box, biggest enclosed white pocket
            tx0, tx1, ty0, ty1 = max(0,int(bx0)-3), min(W,int(bx1)+4), max(0,int(by0)-3), min(H,int(by1)+4)
            tw = m[ty0:ty1, tx0:tx1]; tn, tl, ts, tc = cv2.connectedComponentsWithStats((1-tw).astype(np.uint8), 4)
            cand = [(ts[k,4], k) for k in range(1,tn) if ts[k,0]>0 and ts[k,1]>0 and ts[k,0]+ts[k,2]<tw.shape[1] and ts[k,1]+ts[k,3]<tw.shape[0] and 4<=ts[k,4]<=250]
            if not cand: lg.append("nohole"); continue
            a_, k_ = max(cand); req = np.sqrt(a_/np.pi)
            dtb = cv2.distanceTransform(tw, cv2.DIST_L2, 5)
            px, py = tc[k_]
            if float(np.where(((np.arange(tw.shape[1])[None,:]-px)**2+(np.arange(tw.shape[0])[:,None]-py)**2)<=(req+1)**2, dtb, 0).max()) >= 1.8: lg.append("ok(small)"); continue
            cv2.circle(out, (int(round(px+tx0)), int(round(py+ty0))), max(1,int(round(0.62*req))), 0, -1, lineType=cv2.LINE_AA)
            lg.append("painted small"); continue
        k = best[1]; hole = (lab == k).astype(np.uint8); bx, by, bw_, bh_, a = st[k]
        filled = hole.copy()
        nb, lb, sb, _ = cv2.connectedComponentsWithStats(win, 8)
        for j in range(1, nb):
            ix, iy, iw, ih, ia = sb[j]
            if ix >= bx-1 and iy >= by-1 and ix+iw <= bx+bw_+1 and iy+ih <= by+bh_+1 and ia < a*2: filled[lb == j] = 1
        area = int(filled.sum()); r_e = np.sqrt(area/np.pi)
        ys, xs = np.nonzero(filled); ccx, ccy = xs.mean(), ys.mean()
        dark = float(win[filled > 0].mean())
        # catchlight inside solid pupil -> fine
        yy, xx = np.mgrid[0:win.shape[0], 0:win.shape[1]]; rr2 = (xx-ccx)**2+(yy-ccy)**2
        if r_e <= 6 and win[(rr2 > (r_e+1)**2) & (rr2 <= (r_e+4)**2)].mean() > .8: lg.append("ok(catchlight)"); continue
        if r_e < 2.2: lg.append("tiny"); continue
        dtb = cv2.distanceTransform(win, cv2.DIST_L2, 5)
        near = rr2 <= (0.5*r_e + 1.5)**2
        rs_c = float(np.where(near, dtb, 0).max())
        if rs_c >= max(2.2, 0.62*r_e): lg.append("ok"); continue
        bm = (xx+X0 >= bx0) & (xx+X0 <= bx1) & (yy+Y0 >= by0) & (yy+Y0 <= by1)
        if float(np.where(bm, dtb, 0).max()) >= 0.28*bw: lg.append("ok(solid elsewhere)"); continue   # already a big solid pupil in the box
        if r_e < 6.5 or r_e < 0.2*bw or bw_/max(1, bh_) > 1.6 or bh_/max(1, bw_) > 1.6: lg.append("skip(small/odd)"); continue
        rp = max(1.5, 0.80*r_e)
        cv2.circle(out, (int(round(ccx+X0)), int(round(ccy+Y0))), int(round(rp)), 0, -1, lineType=cv2.LINE_AA)
        if rp >= 3.4:
            gr = max(1.0, 0.24*rp)
            cv2.circle(out, (int(round(ccx+X0+0.32*rp)), int(round(ccy+Y0-0.32*rp))), int(round(gr)), 255, -1, lineType=cv2.LINE_AA)
        lg.append(f"painted r={rp:.1f} dark={dark:.2f}")
    cv2.imwrite(f"{DST}/{nm}", out, [cv2.IMWRITE_JPEG_QUALITY, 95]); log[nm] = lg
json.dump(log, open(f"{DST}/eye_log.json", "w"), indent=0)
from collections import Counter
print(Counter(x.split()[0] for v in log.values() for x in v))
