"""Pilot gallery = REAL Printify photos (people wearing it, on the hanger, folded, lifestyle) for every breed x colour, 8 per child (Amazon allows main + 8).
Same Printify product + colour variant as the main photo, camera ids from docs/printify_cameras.json. Writes store/mk/amz/tee/<breed>/1<CC>_g1..g8.jpg + store/data/amazon_gallery.json."""
import json, os, sys, io, collections, time, urllib.request
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "amazon_mains.py")).read().split("jobs = {}")[0]
sys.argv = sys.argv[:1]
exec(src)
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
PK = os.environ.get("PK", "tee")              # tee (default) | polo | tank | wtank
DCS = os.environ.get("DCS", "1").split(",")      # design codes to render, e.g. "1,4"
# colours that have REAL Printify mockups per product (others are not published)
COLORS = {"tee": ["WH", "BK", "NV", "AS", "LB", "HE", "PK", "CR", "NA", "MR"], "polo": ["WH", "HE"], "tank": ["WH", "HE"], "wtank": ["WH", "HG", "TB", "MI", "LO"],
          "hoodie": ["WH", "GR", "SA", "LB", "PK", "AS"],                                      # light colours first (dark-art versions are added later)
          "cap": ["DW", "DS", "DK", "DB", "DP", "FW", "FP", "FB", "MW"]}[PK]
CAMS = {77:   [98425, 98427, 111848, 111847, 100682, 98428, 98432, 98429],             # Hoodie: back, person front, person back, person front, person back, person front, folded, person front
        1447: [135043, 135044, 135046, 135047, 135048],                               # Dad Hat: back, side, person front, person back, person front
        1735: [127559, 110282, 110280, 110281, 110570],                               # Foam Trucker: back, side, 3 x person
        1734: [109529, 110007, 110013, 110020, 110021],                               # Mesh Trucker: back, person front/back x 2
        1402: [101910, 102926, 103301, 103302],                                       # Polo: back, person front, person back, person close-up
        39:   [101892, 119051],                                                       # Tank Top: back, size chart
        18:   [49, 111806, 111807, 119048],                                           # Racerback Tank: back, alt front, alt back, size chart
        145: [97993, 100619, 100620, 100616, 100617, 100621, 100615, 127673],        # Tee A: back, man front, man back, woman front, woman back, seated, folded, lifestyle on couch
        12:  [102045, 102047, 102057, 102058, 102059, 102060, 102046, 92584]}         # Tee B: back, on hanger, woman front/back, man front/back, folded, lifestyle
D = {d["code"]: d for d in plan["products"][PK]["designs"]}; C = {c["code"]: c for c in plan["products"][PK]["colors"]}
def product(b, cc, DC):
    d = D[DC]; c = C[cc]; want = {norm(c["name"]), norm(c.get("color", c["name"]))}
    for bp in BP[c["prod"] if PK == "cap" else PK]:
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
    DC, b, cc = key; pid, bp, v, fsrc = product(b, cc, DC); res = {"pid": pid, "g": [], "main": "none"}
    if not pid: return key, res
    mp = f"{OUT}/{PK}/{b}/{DC}{cc}.jpg"          # the white-background MAIN photo (same Printify product + colour)
    if os.path.exists(mp): res["main"] = "ok"
    else:
        res["main"] = "err"
        for k in range(5):                                   # transient Printify/network errors: retry
            try:
                data, st_ = render(get(fsrc))
                if st_ == "ok": os.makedirs(os.path.dirname(mp), exist_ok=True); open(mp, "wb").write(data); res["main"] = "ok"; break
                else: res["main"] = st_
            except Exception as e: res["main"] = "err"
            time.sleep(2 * (k + 1))
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
NG = len(next(iter(CAMS[bp] for bp in BP["cap_dad" if PK == "cap" else PK])))          # gallery photos per colour for this product (8 for tees)
for DC in DCS:
    keys = [(DC, b, cc) for b in M.BR for cc in COLORS]; out = {}; st = collections.Counter()
    todo = keys
    for ps in range(5):                       # pass 1 = everything; later passes retry only what is still missing (files already on disk are skipped), gentler
        with ThreadPoolExecutor(8 if ps == 0 else 3) as ex:
            for key, res in ex.map(work, todo): out[f"{key[1]}|{key[2]}"] = res
        todo = [k for k in keys if out[f"{k[1]}|{k[2]}"]["main"] != "ok" and out[f"{k[1]}|{k[2]}"]["pid"] or any(g != "ok" for g in out[f"{k[1]}|{k[2]}"]["g"]) or len(out[f"{k[1]}|{k[2]}"]["g"]) < NG and out[f"{k[1]}|{k[2]}"]["pid"]]
        print("  pass", ps + 1, "still incomplete:", len(todo), file=sys.stderr, flush=True)
        if not todo: break
        time.sleep(20)
    for res in out.values():
        for s_ in res["g"]: st[s_] += 1
    print(PK, "design", DC, "mains:", dict(collections.Counter(r["main"] for r in out.values())), "gallery:", dict(st), "products missing:", sum(1 for r in out.values() if not r["pid"]))
    json.dump(out, open(f"{ROOT}/store/data/amazon_gallery{('' if DC == '1' else '_d' + DC) if PK == 'tee' else '_' + PK + '_d' + DC}.json", "w"), indent=0)
