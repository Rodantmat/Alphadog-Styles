"""Amazon MAIN images: the real Printify front mockup of each breed/design/colour, trimmed and centred on pure white (RGB 255), product ~90% of frame.
Writes store/mk/amz/<prod>/<breed>/<design><colour>.jpg (deploy-time, not committed) and out/amazon_mains_report.json (+ contact sheet).
usage: python3 scripts/amazon_mains.py [--limit N]"""
import json, os, sys, io, re, urllib.request, collections
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import market_plan as M
ROOT = M.ROOT; OUT = f"{ROOT}/store/mk/amz"; SZ = 1200; FILL = 0.90
BP = {"tee": [12, 145], "hoodie": [77], "wtank": [18], "tank": [39], "polo": [1402], "cap_dad": [1447], "cap_foam": [1735], "cap_mesh": [1734]}
JUNK = re.compile(r"BRAND TEST|NECK LABEL|COST PROBE|COSTTEST|BLANK|draft", re.I)
I = [r for r in json.load(open(f"{ROOT}/out/mockidx/index.json")) if not JUNK.search(r["title"])]
BY = collections.defaultdict(list)
for r in I: BY[r["bp"]].append(r)
F = json.load(open(f"{ROOT}/store/data/amazon_feed.json")); plan = json.load(open(f"{ROOT}/store/data/market_plan.json"))
SIZES = {"xs", "s", "m", "l", "xl", "2xl", "3xl", "4xl", "5xl", "one size", "s/m", "l/xl"}
def norm(x): return re.sub(r"^solid\s+", "", x.lower().strip())
def variant_color(label):
    parts = [p.strip() for p in label.split(" / ")]
    cs = [p for p in parts if p.lower() not in SIZES]
    return norm(" / ".join(cs))
def title_ok(pk, art, front, back, t):
    th, st = art.split("_"); stl = st.capitalize()
    theme = "Continuous Line Art" if th == "line" else "Geometric"; theme2 = "Line Art" if th == "line" else "Geometric"
    if pk in ("tee", "hoodie"):
        place = ("Big Portrait" if front == "head_l" and not back else "Pocket Print" if not back else "Front & Back")
        if " | " in t: return th == "line" and bool(back) and f"{theme} {stl} " in t
        return f"{theme2} {stl} {place}" in t
    return bool(re.search(rf"{theme2} {stl}$", t))
def find(pk, breed, dc, cc, D, C):
    c = C[cc]; sub = c["prod"] if pk == "cap" else pk
    d = D[dc]; art, front, back = d["art"], d["front"], d["back"]
    want = {norm(c["name"]), norm(c.get("color", c["name"]))}
    for bp in BP[sub]:
        for r in BY[bp]:
            if M.BR[breed] not in r["title"] or not title_ok(pk, art, front, back, r["title"]): continue
            vids = {v for v, lab in r["variants"].items() if variant_color(lab) in want}
            if not vids: continue
            for cam in ("front", "front-2"):
                for im in r["imgs"]:
                    if im["cam"] == cam and img_color_ok(im, r, want): return im["src"], r["pid"]
    return None, None
def img_color_ok(im, r, want):
    """the variant id in the mockup URL (mockup/<pid>/<variant>/<camera>/...) is the colour this picture really shows; the index 'vids' list is NOT reliable (often every variant)"""
    try: lab = r["variants"].get(str(int(im["src"].split("/")[-3])))
    except Exception: return False
    return bool(lab) and variant_color(lab) in want
def get(u):
    for t in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
        except Exception as e: err = e
    raise err
def render(raw):
    im = Image.open(io.BytesIO(raw)).convert("RGB"); a = np.asarray(im).astype(int)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    if (border.min(axis=1) < 235).mean() > 0.02: return None, "nonwhite-border"
    m = (255 - a.min(axis=2)) > 12; ys, xs = np.where(m)
    if len(xs) == 0: return None, "empty"
    c = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)); k = SZ * FILL / max(c.size)
    c = c.resize((max(1, round(c.width * k)), max(1, round(c.height * k))), Image.LANCZOS)
    cv = Image.new("RGB", (SZ, SZ), (255, 255, 255)); cv.paste(c, ((SZ - c.width) // 2, (SZ - c.height) // 2))
    b = io.BytesIO(); cv.save(b, "JPEG", quality=85, optimize=True); return b.getvalue(), "ok"
jobs = {}
for x in F:
    pk = x["prod"]; PP = plan["products"][pk]; D = {d["code"]: d for d in PP["designs"]}; C = {c["code"]: c for c in PP["colors"]}
    for k in x["children"]:
        jobs.setdefault((pk, k["breed"], k["design"], k["cc"]), (D, C))
keys = sorted(jobs)
if "--limit" in sys.argv: keys = keys[:int(sys.argv[sys.argv.index("--limit") + 1])]
stat = collections.Counter(); bad = []
def work(key):
    pk, b, dc, cc = key; path = f"{OUT}/{pk}/{b}/{dc}{cc}.jpg"
    if os.path.exists(path): return key, "cached", None
    D, C = jobs[key]; src, pid = find(pk, b, dc, cc, D, C)
    if not src: return key, "no-printify-mockup", None
    try: data, st = render(get(src))
    except Exception as e: return key, "fetch-error", str(e)[:80]
    if st != "ok": return key, st, src
    os.makedirs(os.path.dirname(path), exist_ok=True); open(path, "wb").write(data); return key, "ok", None
with ThreadPoolExecutor(12) as ex:
    for key, st, info in ex.map(work, keys):
        stat[st] += 1
        if st not in ("ok", "cached") and len(bad) < 400: bad.append([list(key), st, info])
print("images needed:", len(keys), dict(stat))
for b in bad[:25]: print(" ", b)
os.makedirs(f"{ROOT}/out", exist_ok=True)
json.dump({"needed": len(keys), "stat": stat, "bad": bad}, open(f"{ROOT}/out/amazon_mains_report.json", "w"))
# contact sheet of a spread of results
import glob, random
fs = sorted(glob.glob(f"{OUT}/*/*/*.jpg")); random.seed(3); S = random.sample(fs, min(24, len(fs)))
if S:
    sheet = Image.new("RGB", (6 * 240, 4 * 240), (255, 255, 255))
    for i, f in enumerate(S): sheet.paste(Image.open(f).resize((236, 236)), ((i % 6) * 240, (i // 6) * 240))
    sheet.save(f"{ROOT}/out/amazon_mains_sheet.png")
