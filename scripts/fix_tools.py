import cv2, numpy as np, json, os, sys, glob
def split_x(g):
    m = (g < 128).astype(np.uint8); H, W = m.shape
    prof = m[:, int(W*.40):int(W*.58)].sum(0).astype(float)
    prof = np.convolve(prof, np.ones(9)/9, 'same')
    return int(W*.40) + int(np.argmin(prof))
def load_gray(p): return cv2.imread(p, 0)
def clean(g):
    g = g.astype(np.float32)
    g = np.clip((g - 40) * (255.0/(215-40)), 0, 255)   # push near-white to white, near-black to black
    return g.astype(np.uint8)
def composite(orig_path, cand_path, side):
    o = load_gray(orig_path); c = load_gray(cand_path)
    c = cv2.resize(c, (o.shape[1], o.shape[0]), interpolation=cv2.INTER_AREA); c = clean(c)
    sx = front_right(o) + 6
    if side == "both": return c
    out = o.copy()
    if side == "back": out[:, sx:] = c[:, sx:]
    else: out[:, :sx] = c[:, :sx]
    return out

def front_right(g):
    m = (g < 128).astype(np.uint8); sx = split_x(g)
    cols = np.where(m[:, :sx].any(0))[0]
    return int(cols.max()) if len(cols) else sx
def composite_tail(orig_path, cand_path, grow=3):
    o = load_gray(orig_path); c = load_gray(cand_path)
    c = cv2.resize(c, (o.shape[1], o.shape[0]), interpolation=cv2.INTER_AREA); c = clean(c)
    O = (o < 128).astype(np.uint8); C = (c < 128).astype(np.uint8)
    fr = front_right(o)
    O[:, :fr+3] = np.where(np.arange(O.shape[1])[None, :fr+3] < 0, 0, O[:, :fr+3])
    back = np.zeros_like(O); back[:, fr+3:] = 1
    near = cv2.dilate(O, np.ones((11, 11), np.uint8))
    new = (C & (1-near) & back).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(new, 8)
    ys, xs = np.nonzero(O * back)
    bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    keep = np.zeros_like(O)
    for k in range(1, n):
        x, y, w, h, a = st[k]
        if a < 30: continue
        if x < bx0-3 or x+w > bx1+3 or y+h > by1+3 or y < by0-3: keep[lab == k] = 1
        elif a > 180 and (x+w > bx1-25):   # tail overlapping the body edge region
            keep[lab == k] = 1
    zone = cv2.dilate(keep, np.ones((19, 19), np.uint8))
    outink = np.maximum((o < 128).astype(np.uint8), C * zone)
    return np.where(outink > 0, 0, 255).astype(np.uint8)
