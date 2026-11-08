"""nb_compose.py: sel pngs + eye boxes -> light/dark alpha (2x) with ONE consistent eye style.
usage: nb_compose.py SELDIR EYES.json OUTDIR   -> OUTDIR/light/<name>.png, OUTDIR/dark/<name>.png (L, white=ink)"""
import sys, os, json, glob, numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from nb_lib import split_x, split_masks
S = 2
GX, GY = 0.42, -0.14           # shared gaze (same for every eye)
def ss(img, k=8):               # draw helper with sub-pixel accuracy
    return k
def circ(a, x, y, r, col, th=-1):
    k = 16; cv2.circle(a, (int(round(x*k)), int(round(y*k))), int(round(r*k)), col, -1 if th < 0 else max(1, int(round(th))), cv2.LINE_AA, 4)
def stroke_med(alpha_bin):
    sk = cv2.ximgproc.thinning(alpha_bin.astype(np.uint8)*255) if hasattr(cv2, "ximgproc") else None
    dt = cv2.distanceTransform(alpha_bin.astype(np.uint8), cv2.DIST_L2, 5)
    if sk is None:
        # approx: local maxima of dt
        mx = cv2.dilate(dt, np.ones((5, 5), np.float32)); pts = (dt >= mx-1e-3) & (dt > 0.8)
    else: pts = sk > 0
    v = dt[pts]; v = v[(v > 0.8) & (v < 12)]
    return float(np.median(v)*2) if len(v) else 4.0
def fill_lenses(a, boxes):
    """make sunglasses lenses fully solid: close glare slashes, keep only big solid blobs near the eye positions, fill their hulls"""
    H, W = a.shape; out = a.copy(); m = (a > 128).astype(np.uint8)
    for e in boxes:
        y0, x0, y1, x1 = e["box_2d"]; cx, cy = (x0+x1)/2*W/1000, (y0+y1)/2*H/1000; r = 0.5*min((x1-x0)*W/1000, (y1-y0)*H/1000)
        zr = int(1.9*r); k = max(5, int(0.36*r)//2*2+1); ko = max(5, int(0.5*r)//2*2+1)
        X0, X1, Y0, Y1 = max(0, int(cx-zr)), min(W, int(cx+zr)), max(0, int(cy-zr)), min(H, int(cy+zr))
        sub = m[Y0:Y1, X0:X1]
        c = cv2.morphologyEx(sub, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
        o = cv2.morphologyEx(c, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ko, ko)))
        n, lab, st, cen = cv2.connectedComponentsWithStats(o, 8)
        best = None
        for i in range(1, n):
            d = np.hypot(cen[i][0]-(cx-X0), cen[i][1]-(cy-Y0))
            if st[i, 4] > 0.6*r*r and d < 1.3*r and (best is None or st[i, 4] > st[best, 4]): best = i
        if best is None: continue
        cnt, _ = cv2.findContours((lab == best).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hull = cv2.convexHull(np.vstack(cnt)); fill = np.zeros_like(sub); cv2.fillConvexPoly(fill, hull, 1)
        # only fill pixels that are enclosed by lens: hull shrunk slightly to keep the frame shape
        fill = cv2.erode(fill, np.ones((3, 3), np.uint8))
        region = out[Y0:Y1, X0:X1]; region[fill > 0] = 255
    return out
def build(path, boxes, lens_boxes=None):
    g = np.array(Image.open(path).convert("L"))
    H0, W0 = g.shape
    g2 = cv2.resize(g, None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC).astype(np.float32)
    a = np.clip(((255-g2)/255.0-0.25)/0.5, 0, 1)*255            # soft-threshold alpha
    a = a.astype(np.uint8)
    H, W = a.shape
    if lens_boxes: a = fill_lenses(a, lens_boxes)
    binm = a > 128
    fm, bm = split_masks(binm)
    cut = (np.where(fm)[1].max() + np.where(bm)[1].min())/2 if np.where(fm)[1].max() < np.where(bm)[1].min() else W/2
    sm = {"front": stroke_med(fm), "back": stroke_med(bm)}
    eyes = []
    for e in boxes:
        y0, x0, y1, x1 = e["box_2d"]; bx0, bx1, by0, by1 = x0*W/1000, x1*W/1000, y0*H/1000, y1*H/1000
        cx, cy = (bx0+bx1)/2, (by0+by1)/2; r = 0.5*min(bx1-bx0, by1-by0)
        eyes.append(dict(cx=cx, cy=cy, r=r, side="front" if cx < cut else "back"))
    # one radius per (dog, pair) : mean of its eyes -> both eyes of a dog identical
    for side in ("front", "back"):
        es = [e for e in eyes if e["side"] == side]
        if es:
            R = float(np.mean([e["r"] for e in es]))
            # make the pair horizontally level
            cyv = float(np.mean([e["cy"] for e in es]))
            for e in es: e["r"] = R; e["cy"] = cyv if len(es) == 2 else e["cy"]
    # remove small stray specks/ticks left next to old eyes (isolated blobs only)
    nn, lab, st, cen = cv2.connectedComponentsWithStats((a > 128).astype(np.uint8), 8)
    for e in eyes:
        for i in range(1, nn):
            if st[i, 4] < 0.9*e["r"]**2 and np.hypot(cen[i][0]-e["cx"], cen[i][1]-e["cy"]) < 2.1*e["r"]:
                a[cv2.dilate((lab == i).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0] = 0
    L = a.copy(); D = a.copy(); info = []
    for e in eyes:
        R = e["r"]; s = max(3.0, min(sm[e['side']]*0.85, 0.34*R*0.70)); s = max(s, 0.16*R*0.70)
        for arr in (L, D):
            circ(arr, e["cx"], e["cy"], R*1.05+s*0.5, 0, -1)         # erase old eye area
        ro = R*0.70                                                   # outer eye ring radius
        # LIGHT: ring + solid pupil (offset by shared gaze) + glint
        circ(L, e["cx"], e["cy"], ro, 255, s)
        rp = 0.50*ro; room = ro-s/2-rp-s*0.5
        px, py = e["cx"]+GX*room, e["cy"]+GY*room
        circ(L, px, py, rp, 255, -1); circ(L, px+0.38*rp, py-0.38*rp, max(1.6, 0.26*rp), 0, -1)
        # DARK: ring + small iris ring + highlight dot, inside black
        circ(D, e["cx"], e["cy"], ro, 255, s)
        ri = 0.40*ro; ix, iy = e["cx"]+GX*(ro*0.36), e["cy"]+GY*(ro*0.36)
        circ(D, ix, iy, ri, 255, max(s*0.75, 2.4))
        circ(D, ix+0.30*ri, iy-0.30*ri, max(2.0, 0.17*ri), 255, -1)
        info.append((round(e["cx"]), round(e["cy"]), round(ro, 1), round(s, 1)))
    return L, D, info, cut
if __name__ == "__main__":
    sel, ej, out = sys.argv[1:4]
    eyes = json.load(open(ej)); os.makedirs(out+"/light", exist_ok=True); os.makedirs(out+"/dark", exist_ok=True); rep = {}
    for p in sorted(glob.glob(sel+"/*.png")):
        n = os.path.basename(p); key = [k for k in eyes if k.endswith("/"+n)]
        boxes = eyes[key[0]] if key else []
        lb = None
        if False:
            ck = [k for k in eyes if k.endswith("/"+n.replace("_cool","_classic"))]; lb = eyes[ck[0]] if ck else None
        L, D, info, cut = build(p, boxes, lb)
        Image.fromarray(L).save(f"{out}/light/{n}"); Image.fromarray(D).save(f"{out}/dark/{n}"); rep[n] = (info, cut)
    json.dump(rep, open(out+"/compose_log.json", "w"))
    print(len(rep))
