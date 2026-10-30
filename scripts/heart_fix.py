"""Replace the heart around the front head of every 01 (line) heart design with the poodle (01-06) heart.
usage: heart_fix.py SRC_BASE DST_BASE   (SRC_BASE contains line_p1/line_p2 dirs)"""
import cv2, numpy as np, json, os, sys
SRC, DST = sys.argv[1], sys.argv[2]
b = json.load(open("scripts/breeds25.json"))
def find(base, slug, v):
    for p in ("p1", "p2"):
        f = f"{base}/line_{p}/{slug}__{v}.jpg"
        if os.path.exists(f): return f, p
def split_x(m):
    H, W = m.shape
    prof = m[:, int(W*.40):int(W*.58)].sum(0).astype(float)
    prof = np.convolve(prof, np.ones(9)/9, 'same')
    return int(W*.40) + int(np.argmin(prof))
def heart_comp(m, sx):
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    cands = [(st[k, 2]*st[k, 3], k) for k in range(1, n) if st[k, 4] > 300 and cen[k][0] < sx]
    cands.sort(reverse=True)
    return n, lab, st, cands[0][1]
# ---- template from poodle
pf, _ = find(SRC, "poodle", "heart")
pg = cv2.imread(pf, 0); pm = (pg < 128).astype(np.uint8); psx = split_x(pm)
n, lab, st, hk = heart_comp(pm, psx)
tx, ty, tw, th = st[hk, :4]
T = (lab[ty:ty+th, tx:tx+tw] == hk).astype(np.uint8)
dt = cv2.distanceTransform(T, cv2.DIST_L2, 3)
sk = cv2.ximgproc.thinning(T*255) if hasattr(cv2, "ximgproc") else None
t0 = float(np.median(dt[T > 0]) * 2)
print("template", tw, th, "thickness~", round(t0, 1))
report = {}
TEDGE = 6
TEDGE_OVR = {'doberman_pinscher': 44}
EXTRA = {'golden_retriever': [(335,240,362,249)], 'beagle': [(305,216,387,266)], 'doberman_pinscher': [], 'havanese': [(330,207,376,266)]}
for i, (slug, name, _) in enumerate(b):
    f, p = find(SRC, slug, "heart")
    g = cv2.imread(f, 0); m = (g < 128).astype(np.uint8); H, W = m.shape
    sx = split_x(m)
    if slug == "poodle":
        out = g
        report[slug] = "template"
    else:
        n, lab, st, hk = heart_comp(m, sx)
        x, y, w, h, area = st[hk]
        comp = (lab == hk).astype(np.uint8)
        k21 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
        pad = cv2.copyMakeBorder(comp, 30, 30, 30, 30, cv2.BORDER_CONSTANT, value=0)
        cl = cv2.morphologyEx(pad, cv2.MORPH_CLOSE, k21)
        inv = (1-cl).astype(np.uint8)
        fl = np.zeros((cl.shape[0]+2, cl.shape[1]+2), np.uint8)
        cv2.floodFill(inv, fl, (0, 0), 2)
        filled = (inv != 2).astype(np.uint8)
        dist = cv2.distanceTransform(filled, cv2.DIST_L2, 5)[30:-30, 30:-30]
        sub = m.copy()
        edge = (comp > 0) & (dist <= TEDGE)
        xc = x + w/2
        yy, xx = np.mgrid[0:comp.shape[0], 0:comp.shape[1]]
        zone = (yy < y + 0.135*h) & (np.abs(xx - xc) < 0.10*w) & (comp > 0)
        sub[edge | zone] = 0
        TE2 = TEDGE_OVR.get(slug)
        if TE2: sub[(comp > 0) & (dist <= TE2)] = 0
        # separate small fragments of the old top heart
        for k in range(1, n):
            if k == hk: continue
            if st[k, 1] + st[k, 3] < y + 0.14*h and abs(st[k, 0] + st[k, 2]/2 - xc) < 0.12*w and st[k, 4] > 15:
                sub[lab == k] = 0
        mm = sub
        if True:
            # fit template to old heart bbox
            Tr = cv2.resize(T*255, (w, h), interpolation=cv2.INTER_AREA).astype(np.uint8)
            sc = ((w/tw) + (h/th)) / 2
            d = int(round(abs(1-sc)*t0/2))
            if d > 0:
                ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*d+1, 2*d+1))
                Tr = cv2.dilate(Tr, ker) if sc < 1 else cv2.erode(Tr, ker)
            Tr = (Tr > 110).astype(np.uint8)
            # --- cleanup of old-heart residue BEFORE pasting the new heart
            Tfull = np.zeros_like(mm); Tfull[y:y+h, x:x+w] = Tr
            padT = cv2.copyMakeBorder(Tfull, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=0)
            clT = cv2.morphologyEx(padT, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
            invT = (1-clT).astype(np.uint8); flT = np.zeros((clT.shape[0]+2, clT.shape[1]+2), np.uint8)
            cv2.floodFill(invT, flT, (0, 0), 2)
            silT = (invT != 2).astype(np.uint8)[5:-5, 5:-5]
            silT = cv2.dilate(silT, np.ones((5, 5), np.uint8))
            n2, lab2, st2, cen2 = cv2.connectedComponentsWithStats(mm, 8)
            for k in range(1, n2):
                if cen2[k][0] >= sx and st2[k,0] > sx: continue
                reg = lab2 == k
                outside = (reg & (silT == 0)).sum() / max(1, reg.sum())
                cx = st2[k, 0] + st2[k, 2]/2; cy = st2[k, 1] + st2[k, 3]/2
                small_top = st2[k, 4] < 900 and st2[k, 3] < 0.13*h and st2[k, 2] < 0.09*w and abs(cx - xc) < 0.07*w and cy < y + 0.30*h
                if outside > 0.5 or small_top:
                    mm[reg] = 0
            for (ex0,ey0,ex1,ey1) in EXTRA.get(slug,[]): mm[ey0:ey1, ex0:ex1] = 0
            mm[y:y+h, x:x+w] = np.maximum(mm[y:y+h, x:x+w], Tr)
            out = np.where(mm > 0, 0, 255).astype(np.uint8)
            report[slug] = f"ok scale {sc:.2f}"
    for pp in ("p1", "p2"):
        os.makedirs(f"{DST}/line_{pp}", exist_ok=True)
    cv2.imwrite(f"{DST}/line_{p}/{slug}__heart.jpg", out, [cv2.IMWRITE_JPEG_QUALITY, 95])
print(json.dumps(report, indent=0))
