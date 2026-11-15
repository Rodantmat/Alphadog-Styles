"""Contact sheets for visual QA of the pilot: one sheet per breed, rows = the 10 colours, columns = main + 8 gallery photos (exactly what is uploaded to Amazon).
Also checks every file exists, is >=1000px and that the 9 photos of a colour are all different."""
import os, json, hashlib, collections
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = f"{ROOT}/store/mk/amz/tee"
LD = os.environ.get("LDC", "1"); f = json.load(open(f"{ROOT}/store/data/" + {"1": "amazon_pilot.json", "3": "amazon_listing_tee3.json", "4": "amazon_listing_tee4.json"}[LD]))[0]
COLORS = ["WH", "BK", "NV", "AS", "LB", "HE", "PK", "CR", "NA", "MR"]
breeds = sorted({k["breed"] for k in f["children"]}); T = 150
VD = f"{ROOT}/out/verify" + ("" if LD == "1" else "_d" + LD); os.makedirs(VD, exist_ok=True); problems = []
by = {(k["breed"], k["cc"]): k for k in f["children"]}
for b in breeds:
    sheet = Image.new("RGB", (9 * T + 60, len(COLORS) * T), (255, 255, 255)); d = ImageDraw.Draw(sheet)
    for r, cc in enumerate(COLORS):
        k = by[(b, cc)]; files = [k["img"]] + k["others"]; hs = set()
        if len(files) != 9: problems.append((b, cc, "files %d" % len(files)))
        d.text((2, r * T + T // 2), cc, fill=(200, 0, 0))
        for c, rel in enumerate(files):
            p = f"{ROOT}/store/mk/{rel}"
            if not os.path.exists(p): problems.append((b, cc, "missing " + rel)); continue
            im = Image.open(p).convert("RGB")
            if min(im.size) < 1000: problems.append((b, cc, "small " + rel))
            h = hashlib.md5(im.resize((32, 32)).tobytes()).hexdigest()
            if h in hs: problems.append((b, cc, "duplicate " + rel))
            hs.add(h); im.thumbnail((T, T)); sheet.paste(im, (60 + c * T + (T - im.width) // 2, r * T + (T - im.height) // 2))
    sheet.save(f"{VD}/{b}.jpg", quality=72)
print("verify problems:", len(problems)); [print("  ", p) for p in problems[:30]]
