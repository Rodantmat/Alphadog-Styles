"""Pilot listing images: for the pilot (tee x design 1) render, from the SAME Printify product and colour as the main photo, the back view and the collar close-up on pure white.
Writes store/mk/amz/tee/<breed>/1<CC>.jpg (main), 1<CC>_b.jpg (back), 1<CC>_c.jpg (collar) and store/data/amazon_extras.json (which exist) + out/amazon_pilot_sheet.png.
Everything comes from ONE Printify product per breed+colour, so no other design/product can leak into the gallery."""
import json, os, sys, io, collections
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "amazon_mains.py")).read().split("jobs = {}")[0]
sys.argv = sys.argv[:1]
exec(src)
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
PK, DC = "tee", "1"
COLORS = ["WH", "BK", "NV", "AS", "LB", "HE", "PK", "CR", "NA", "MR"]      # every tee colour that has real Printify photos for all 33 breeds
D = {d["code"]: d for d in plan["products"][PK]["designs"]}; C = {c["code"]: c for c in plan["products"][PK]["colors"]}
def product(b, cc):
    d = D[DC]; c = C[cc]; want = {norm(c["name"]), norm(c.get("color", c["name"]))}
    for bp in BP[PK]:
        for r in BY[bp]:
            if M.BR[b] not in r["title"] or not title_ok(PK, d["art"], d["front"], d["back"], r["title"]): continue
            vids = {v for v, lab in r["variants"].items() if variant_color(lab) in want}
            if not vids: continue
            def pick(cams):
                for cam in cams:
                    for im in r["imgs"]:
                        if im["cam"] == cam and img_color_ok(im, r, want): return im["src"]
            f = pick(("front", "front-2"))
            if f: return r["pid"], r["title"], {"": f, "_b": pick(("back", "back-2")), "_c": pick(("front-collar-closeup",)), "_f": pick(("folded",)), "_h": pick(("hanging-1", "hanging-2")), "_s": pick(("size-chart",))}
    return None, None, {}
def work(key):
    b, cc = key; pid, title, ims = product(b, cc); res = {"pid": pid, "title": title}
    for suf, u in ims.items():
        if not u: res[suf or "main"] = "none"; continue
        path = f"{OUT}/{PK}/{b}/{DC}{cc}{suf}.jpg"
        if os.path.exists(path): res[suf or "main"] = "ok"; continue
        try: data, st = render(get(u))
        except Exception as e: res[suf or "main"] = "err"; continue
        if st != "ok": res[suf or "main"] = st; continue
        os.makedirs(os.path.dirname(path), exist_ok=True); open(path, "wb").write(data); res[suf or "main"] = "ok"
    return key, res
keys = [(b, cc) for b in M.BR for cc in COLORS]
out = {}; st = collections.Counter()
with ThreadPoolExecutor(12) as ex:
    for key, res in ex.map(work, keys):
        out[f"{key[0]}|{key[1]}"] = res
        for k in ("main", "_b", "_c", "_f", "_h", "_s"): st[(k, res.get(k))] += 1
print("pilot images:", dict(st))
json.dump(out, open(f"{ROOT}/store/data/amazon_extras.json", "w"), indent=0)
# detail crops of the print itself (front emblem / back design), taken from the SAME rendered mockups
import numpy as np
from scipy import ndimage as ndi
def detail(path, min_frac=0.22):
    im = Image.open(path).convert("RGB"); a = np.asarray(im).astype(int)
    garment = (255 - a.min(axis=2)) > 12                               # everything that is not the white backdrop
    garment = ndi.binary_fill_holes(garment); inner = ndi.binary_erosion(garment, iterations=45)
    ys, xs = np.where(inner)
    if len(xs) < 5000: return None
    med = np.median(a[inner], axis=0); dev = np.abs(a - med).max(axis=2)
    pm = (dev > 38) & inner; pm = ndi.binary_opening(pm, iterations=1)
    ys, xs = np.where(pm)
    if len(xs) < 60: return None
    x0, x1, y0, y1 = np.percentile(xs, 1), np.percentile(xs, 99), np.percentile(ys, 1), np.percentile(ys, 99)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; side = max(x1 - x0, y1 - y0) * 1.35
    side = max(side, SZ * min_frac); half = side / 2
    box = (int(max(0, cx - half)), int(max(0, cy - half)), int(min(SZ, cx + half)), int(min(SZ, cy + half)))
    c = im.crop(box); k = SZ / max(c.size)
    c = c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS)
    cv = Image.new("RGB", (SZ, SZ), (255, 255, 255)); cv.paste(c, ((SZ - c.width) // 2, (SZ - c.height) // 2))
    b = io.BytesIO(); cv.save(b, "JPEG", quality=88, optimize=True); return b.getvalue()
dstat = collections.Counter()
for key, res in out.items():
    b, cc = key.split("|")
    for src_s, dst_s, frac in (("", "_z1", 0.22), ("_b", "_z2", 0.45)):
        sp = f"{OUT}/{PK}/{b}/{DC}{cc}{src_s}.jpg"; dp = f"{OUT}/{PK}/{b}/{DC}{cc}{dst_s}.jpg"
        if not os.path.exists(sp): res[dst_s] = "nosrc"; continue
        data = detail(sp, frac)
        if data is None: res[dst_s] = "none"
        else: open(dp, "wb").write(data); res[dst_s] = "ok"
        dstat[(dst_s, res[dst_s])] += 1
print("detail crops:", dict(dstat))
json.dump(out, open(f"{ROOT}/store/data/amazon_extras.json", "w"), indent=0)
# contact sheets: sheet 1 = main+back for every breed x colour; sheet 2 = every extra view for 3 breeds
rows = list(M.BR); TH = 110; cols = [(c, s_) for c in COLORS for s_ in ("", "_b")]
sheet = Image.new("RGB", (TH * len(cols), TH * len(rows)), (230, 230, 230))
for i, b in enumerate(rows):
    for j, (cc, suf) in enumerate(cols):
        p = f"{OUT}/{PK}/{b}/{DC}{cc}{suf}.jpg"
        if os.path.exists(p): sheet.paste(Image.open(p).resize((TH - 4, TH - 4)), (j * TH, i * TH))
os.makedirs(f"{ROOT}/out", exist_ok=True); sheet.save(f"{ROOT}/out/amazon_pilot_sheet.png")
views = ("", "_b", "_z1", "_z2", "_f", "_h", "_c", "_s"); sub = list(M.BR)[:3]; TH2 = 150
s2 = Image.new("RGB", (TH2 * len(views) * 3, TH2 * len(COLORS)), (230, 230, 230))
for bi, b in enumerate(sub):
    for ci, cc in enumerate(COLORS):
        for vi, v in enumerate(views):
            p = f"{OUT}/{PK}/{b}/{DC}{cc}{v}.jpg"
            if os.path.exists(p): s2.paste(Image.open(p).resize((TH2 - 4, TH2 - 4)), ((bi * len(views) + vi) * TH2, ci * TH2))
s2.save(f"{ROOT}/out/amazon_pilot_views.png")
