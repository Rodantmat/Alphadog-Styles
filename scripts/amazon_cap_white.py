"""Cap MAIN photos on pure white. The Printify cap mockup carries a wide soft grey glow around the hat; Amazon rejects it for HAT (error 100588
"MAIN image has non-pure white background" - seen Nov 18 2026 on Dad Hat Pink). For the coloured dad hats the glow is removed: every light neutral
pixel connected to the picture border becomes RGB 255 (the dark contact shadow under the brim stays). White / foam / mesh hats are left untouched -
a neutral hat cannot be told apart from the glow, so the fill is refused whenever it reaches the middle of the hat.
Runs in the store deploy after amazon_gallery.py; same input always gives the same output. usage: python3 scripts/amazon_cap_white.py"""
import glob, os, re, sys, collections
from PIL import Image
import numpy as np
from scipy import ndimage
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLORS = ("DS", "DK", "DB", "DP")            # keep in step with CAP_WHITE in amazon_merch_feed.py
st = collections.Counter()
for p in sorted(glob.glob(f"{ROOT}/store/mk/amz/cap/*/*.jpg")):
    m = re.fullmatch(r"\d+([A-Z]{2})\.jpg", os.path.basename(p))
    if not m or m.group(1) not in COLORS: continue
    im = Image.open(p).convert("RGB"); a = np.asarray(im).astype(int); H, W = a.shape[:2]
    mn, mx = a.min(axis=2), a.max(axis=2)
    lab, n = ndimage.label((mx - mn <= 16) & (mn >= 120))
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])); edge = edge[edge > 0]
    bg = np.isin(lab, edge)
    if bg[H * 3 // 8: H * 5 // 8, W * 3 // 8: W * 5 // 8].mean() > 0.001 or not 0.30 < bg.mean() < 0.70: st["refused"] += 1; print("  refused", p[len(ROOT) + 1:], round(float(bg.mean()), 3)); continue
    if (bg & (mn < 255)).sum() < 500: st["already-white"] += 1; continue
    out = a.copy(); out[bg] = 255
    Image.fromarray(out.astype("uint8")).save(p, "JPEG", quality=90, optimize=True); st["whitened"] += 1
print("cap mains on pure white:", dict(st))
