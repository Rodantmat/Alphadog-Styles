"""Vectorize every generated pair and assemble the delivery pack + contact sheets.
Usage: python build_pack.py <pack_root>"""
import glob, json, os, subprocess, sys
from PIL import Image, ImageDraw
ROOT = sys.argv[1]
breeds = json.load(open("scripts/breeds25.json"))
THEMES = {"line": ("01_continuous_line", "1"), "geo": ("02_geometric", "0")}
os.makedirs(f"{ROOT}/contact_sheets", exist_ok=True)
for th, (folder, thick) in THEMES.items():
    files = {}
    for f in glob.glob(f"out/sets/{th}_p*/*__*.jpg"):
        files[os.path.basename(f)[:-4]] = f
    for i, (slug, name, _) in enumerate(breeds, 1):
        out = f"{ROOT}/{folder}/{i:02d}_{slug}"; os.makedirs(out, exist_ok=True)
        tiles = []
        for v in ("classic", "cool", "heart"):
            key = f"{slug}__{v}"
            if key not in files: print("MISSING", th, key); continue
            subprocess.run([sys.executable, "scripts/vectorize.py", files[key], f"{out}/{slug}_{v}"], env={**os.environ, "FRONT_THICKEN": thick}, capture_output=True)
            Image.open(files[key]).convert("RGB").save(f"{out}/{slug}_{v}_original.jpg", quality=92)
            tiles.append((v, Image.open(files[key]).convert("RGB")))
        if tiles:
            T = 560; sh = Image.new("RGB", (T * len(tiles), int(T * .667) + 30), "white"); d = ImageDraw.Draw(sh)
            for j, (v, im) in enumerate(tiles):
                im.thumbnail((T, T)); sh.paste(im, (j * T, 30)); d.text((j * T + 8, 8), f"{name} - {v}", fill="black")
            sh.save(f"{ROOT}/contact_sheets/{folder}_{i:02d}_{slug}.jpg", quality=88)
print("done")
