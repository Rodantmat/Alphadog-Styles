"""Layer A: objective technical checks for POD art. Usage: python analyze_tech.py <dir> -> <dir>/tech.json"""
import json, sys, glob, os
import numpy as np
from PIL import Image
from scipy import ndimage

GARMENTS = {"white": (245, 245, 245), "black": (20, 20, 22), "heather_gray": (150, 150, 152),
            "navy": (30, 40, 70), "sand": (215, 195, 160)}
NEEDS = {"full_front": (4500, 5400), "left_chest_4in": (1200, 1200), "cap_front": (1200, 720)}

def lab(rgb):
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)

def analyze(path):
    im = Image.open(path).convert("RGBA"); W, H = im.size
    a = np.asarray(im).astype(float); rgb = a[..., :3]
    has_alpha = (a[..., 3] < 250).any()
    # background = border-connected pixels close to the dominant border color
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bgc = np.median(border, 0)
    dist = np.linalg.norm(rgb - bgc, axis=-1)
    near = dist < 18
    lbl, _ = ndimage.label(near)
    edge_labels = set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))) - {0}
    bg = np.isin(lbl, list(edge_labels))
    subj = ~bg
    subj = ndimage.binary_opening(subj, iterations=2)
    filled_all = ndimage.binary_fill_holes(subj)
    comp, n = ndimage.label(filled_all)
    if n == 0:
        return {"file": os.path.basename(path), "error": "no subject found"}
    sizes = ndimage.sum(filled_all, comp, range(1, n + 1))
    main = int(np.argmax(sizes)) + 1
    filled = comp == main
    # stray marks: other components >= 20 px not overlapping main subject
    stray = [int(z) for z in sizes if z >= 20][1:] if n > 1 else []
    stray_px = int(sum(z for i, z in enumerate(sizes) if i + 1 != main and z >= 20))
    if filled.sum() < 100:
        return {"file": os.path.basename(path), "error": "no subject found"}
    ys, xs = np.where(filled)
    bbox = (xs.min(), ys.min(), xs.max(), ys.max())
    touches = bool(xs.min() <= 2 or ys.min() <= 2 or xs.max() >= W - 3 or ys.max() >= H - 3)
    # T2/T3: boundary analysis
    boundary = filled & ~ndimage.binary_erosion(filled, iterations=2)
    bdist = dist[boundary]
    soft = float(((bdist >= 18) & (bdist < 70)).mean())          # mid-tone halo risk
    lowcontrast_edge = float((bdist < 40).mean())                 # edge barely differs from bg
    # interior holes that are background-colored (white fur gaps that would print as holes)
    inner_bgcolored = float((near & filled & ~bg).sum() / filled.sum())
    S = rgb[filled]; L = lab(S.reshape(-1, 1, 3)).reshape(-1, 3)
    # T4 gradient load: low but nonzero local gradient
    g = np.zeros((H, W))
    for ch in range(3):
        gx = ndimage.sobel(rgb[..., ch], 1); gy = ndimage.sobel(rgb[..., ch], 0)
        g = np.maximum(g, np.hypot(gx, gy))
    gs = g[filled]
    gradient_share = float(((gs > 6) & (gs < 40)).mean())
    # T5 palette size covering 95%
    q = (S // 24).astype(int); keys = q[:, 0] * 10000 + q[:, 1] * 100 + q[:, 2]
    _, counts = np.unique(keys, return_counts=True)
    c = np.sort(counts)[::-1].cumsum() / counts.sum()
    palette95 = int(np.searchsorted(c, 0.95) + 1)
    # embroidery-ish: merge into perceptual clusters via coarse Lab bins
    lq = np.round(L / [12, 18, 18]).astype(int); lk = lq[:, 0] * 1e6 + lq[:, 1] * 1e3 + lq[:, 2]
    _, lc = np.unique(lk, return_counts=True); lcs = np.sort(lc)[::-1].cumsum() / lc.sum()
    thread_colors_est = int(np.searchsorted(lcs, 0.90) + 1)
    # T6 detail survival at small sizes
    crop = im.crop(bbox).convert("L"); cw, ch_ = crop.size
    def survival(target_px):
        s = target_px / max(cw, ch_)
        small = crop.resize((max(1, int(cw * s)), max(1, int(ch_ * s))), Image.LANCZOS).resize((cw, ch_), Image.LANCZOS)
        o = np.asarray(crop, float); r = np.asarray(small, float)
        eo = np.hypot(ndimage.sobel(o, 0), ndimage.sobel(o, 1)); er = np.hypot(ndimage.sobel(r, 0), ndimage.sobel(r, 1))
        return float(np.minimum(eo, er).sum() / max(eo.sum(), 1))
    chest_survival = survival(4 * 100)   # 4in viewed on screen ~100ppi
    thumb_survival = survival(150)       # marketplace grid thumbnail
    # T7/T8 garment contrast: share of subject pixels with deltaE < 15 vs garment
    near_white = float((L[:, 0] > 88).mean())
    garments = {}
    for name, col in GARMENTS.items():
        gl = lab(np.array(col, float).reshape(1, 1, 3)).reshape(3)
        de = np.linalg.norm(L - gl, axis=1)
        lost = float((de < 15).mean())
        bd = np.linalg.norm(lab(rgb[boundary].reshape(-1, 1, 3)).reshape(-1, 3) - gl, axis=1)
        sil = float((bd > 25).mean())   # silhouette edge visibility against garment
        garments[name] = {"pixels_lost": round(lost, 3), "edge_visible": round(sil, 3),
                          "usable": bool(lost < 0.12 and sil > 0.6)}
    # T9 composition
    fill = float(filled.sum() / ((bbox[2] - bbox[0] + 1) * (bbox[3] - bbox[1] + 1)))
    cx = (bbox[0] + bbox[2]) / 2 / W; cy = (bbox[1] + bbox[3]) / 2 / H
    sub = np.asarray(im.crop(bbox).convert("L"), float)
    asym = float(np.abs(sub - sub[:, ::-1]).mean() / 255)
    up = {k: round(max(v[0] / (bbox[2] - bbox[0] + 1), v[1] / (bbox[3] - bbox[1] + 1)), 2) for k, v in NEEDS.items()}
    gates = []
    if up["full_front"] > 4: gates.append("T1 upscale >4x for full front")
    if lowcontrast_edge > 0.20: gates.append("T2 background hard to separate (edge ~ background color)")
    if soft > 0.25: gates.append("T3 soft/semi-transparent edge risk -> underbase halo")
    if gradient_share > 0.40: gates.append("T4 heavy gradients -> needs halftone for dark DTG")
    if thread_colors_est > 6: gates.append("T5 >6 colors -> cap needs separate simplified art")
    if stray_px > 0: gates.append(f"T11 stray marks/specks outside the art ({stray_px}px) -> must be cleaned")
    if chest_survival < 0.6 or thumb_survival < 0.33: gates.append("T6 detail lost at chest/thumbnail size")
    usable = [k for k, v in garments.items() if v["usable"]]
    if len(usable) < 2: gates.append("T7 usable on fewer than 2 garment colors")
    if asym > 0.25: gates.append("T9 asymmetry high")
    if touches: gates.append("T10 art touches canvas edge (cropped)")
    if has_alpha is False: gates.append("T2 no transparency (background must be removed)")
    return {"file": os.path.basename(path), "size": [W, H],
            "subject_bbox_px": [int(bbox[2] - bbox[0] + 1), int(bbox[3] - bbox[1] + 1)],
            "upscale_needed": up, "bg_low_contrast_edge": round(lowcontrast_edge, 3),
            "soft_edge_share": round(soft, 3), "interior_bg_colored": round(inner_bgcolored, 3),
            "gradient_share": round(gradient_share, 3), "palette95": palette95,
            "thread_colors_est": thread_colors_est, "chest_detail_survival": round(chest_survival, 3),
            "thumb_detail_survival": round(thumb_survival, 3), "near_white_share": round(near_white, 3),
            "garments": garments, "usable_garments": usable, "fill_ratio": round(fill, 3),
            "center": [round(cx, 3), round(cy, 3)], "asymmetry": round(asym, 3),
            "touches_edge": touches, "stray_marks_px": stray_px, "tech_flags": gates}

if __name__ == "__main__":
    d = sys.argv[1]
    res = [analyze(f) for f in sorted(glob.glob(os.path.join(d, "*.png")))]
    json.dump(res, open(os.path.join(d, "tech.json"), "w"), indent=1)
    for r in res: print(r["file"], len(r.get("tech_flags", [])), r.get("tech_flags"))
