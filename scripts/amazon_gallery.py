"""Pilot gallery = REAL Printify photos (people wearing it, on the hanger, folded, lifestyle) for every breed x colour, 8 per child (Amazon allows main + 8).
Same Printify product + colour variant as the main photo, camera ids from docs/printify_cameras.json. Writes store/mk/amz/tee/<breed>/1<CC>_g1..g8.jpg + store/data/amazon_gallery.json."""
import json, os, sys, io, collections, time, urllib.request
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "amazon_mains.py")).read().split("jobs = {}")[0]
sys.argv = sys.argv[:1]
exec(src)
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
PK, DC = "tee", "1"
COLORS = ["WH", "BK", "NV", "AS", "LB", "HE", "PK", "CR", "NA", "MR"]
CAMS = {145: [97993, 100619, 100620, 100616, 100617, 100621, 100615, 127673],        # Tee A: back, man front, man back, woman front, woman back, seated, folded, lifestyle on couch
        12:  [102045, 102047, 102057, 102058, 102059, 102060, 102046, 92584]}         # Tee B: back, on hanger, woman front/back, man front/back, folded, lifestyle
D = {d["code"]: d for d in plan["products"][PK]["designs"]}; C = {c["code"]: c for c in plan["products"][PK]["colors"]}
def product(b, cc):
    d = D[DC]; c = C[cc]; want = {norm(c["name"]), norm(c.get("color", c["name"]))}
    for bp in BP[PK]:
        for r in BY[bp]:
            if M.BR[b] not in r["title"] or not title_ok(PK, d["art"], d["front"], d["back"], r["title"]): continue
            for cam in ("front", "front-2"):
                for im in r["imgs"]:
                    if im["cam"] == cam and img_color_ok(im, r, want): return r["pid"], bp, im["src"].split("/")[-3], im["src"]
    return None, None, None, None
def fetch(pid, v, cam):
    u = f"https://images.printify.com/mockup/{pid}/{v}/{cam}/x.jpg?camera_label=front&s=1600&use_cache=false&t={int(time.time()*1000)}"
    for k in range(6):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=90).read()
        except Exception as e: err = e; time.sleep(2 * (k + 1))
    raise err
def work(key):
    b, cc = key; pid, bp, v, fsrc = product(b, cc); res = {"pid": pid, "g": [], "main": "none"}
    if not pid: return key, res
    mp = f"{OUT}/{PK}/{b}/{DC}{cc}.jpg"          # the white-background MAIN photo (same Printify product + colour)
    if os.path.exists(mp): res["main"] = "ok"
    else:
        try:
            data, st_ = render(get(fsrc))
            if st_ == "ok": os.makedirs(os.path.dirname(mp), exist_ok=True); open(mp, "wb").write(data); res["main"] = "ok"
            else: res["main"] = st_
        except Exception as e: res["main"] = "err"
    for i, cam in enumerate(CAMS[bp], 1):
        path = f"{OUT}/{PK}/{b}/{DC}{cc}_g{i}.jpg"
        if not os.path.exists(path):
            try:
                im = Image.open(io.BytesIO(fetch(pid, v, cam))).convert("RGB")
                if min(im.size) < 1000: res["g"].append("small"); continue
                os.makedirs(os.path.dirname(path), exist_ok=True); im.save(path, "JPEG", quality=90, optimize=True)
            except Exception as e: res["g"].append("err"); continue
        res["g"].append("ok")
    return key, res
keys = [(b, cc) for b in M.BR for cc in COLORS]; out = {}; st = collections.Counter()
with ThreadPoolExecutor(8) as ex:
    for key, res in ex.map(work, keys):
        out[f"{key[0]}|{key[1]}"] = res
        for s in res["g"]: st[s] += 1
print("mains:", dict(collections.Counter(r["main"] for r in out.values())), "gallery:", dict(st), "products missing:", sum(1 for r in out.values() if not r["pid"]))
json.dump(out, open(f"{ROOT}/store/data/amazon_gallery.json", "w"), indent=0)
