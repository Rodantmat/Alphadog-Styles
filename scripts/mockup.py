"""Flat tee mockups: front (left-chest emblem) + back (full print). Usage: python mockup.py <pairs.json> <out.jpg>"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops

def cutout(path, ink=(15, 15, 15)):
    im = Image.open(path).convert("L")
    a = np.asarray(im, float)
    alpha = np.clip((235 - a) / 140, 0, 1)          # dark = ink, white = transparent
    alpha = (alpha > 0.5).astype(float)               # hard alpha, no semi-transparent pixels
    rgba = np.zeros(a.shape + (4,), np.uint8); rgba[..., :3] = ink; rgba[..., 3] = (alpha * 255).astype(np.uint8)
    out = Image.fromarray(rgba); bb = out.getbbox(); return out.crop(bb) if bb else out

def tee(color, w=520, h=600):
    im = Image.new("RGB", (w, h), (238, 238, 235)); d = ImageDraw.Draw(im)
    body = [(130, 70), (205, 40), (260, 60), (315, 40), (390, 70), (500, 170), (440, 225), (400, 195), (400, 580), (120, 580), (120, 195), (80, 225), (20, 170)]
    d.polygon(body, fill=color, outline=(120, 120, 120)); return im

def place(base, art, box):
    x0, y0, x1, y1 = box; art = art.copy(); art.thumbnail((x1 - x0, y1 - y0), Image.LANCZOS)
    base.paste(art, (x0 + (x1 - x0 - art.width) // 2, y0), art)

pairs = json.load(open(sys.argv[1])); out = sys.argv[2]
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
cols = [((250, 250, 248), (15, 15, 15)), ((28, 28, 30), (245, 245, 240))]   # white tee/black ink, black tee/white ink
rows = []
for p in pairs:
    row = Image.new("RGB", (4 * 530 + 20, 650), "white"); dr = ImageDraw.Draw(row)
    for j, (tc, ink) in enumerate(cols):
        f = tee(tc); place(f, cutout(p["front"], ink), (290, 110, 370, 190))    # ~4in left chest (wearer's left)
        b = tee(tc); place(b, cutout(p["back"], ink), (170, 120, 350, 420))     # ~12in back
        row.paste(f, (10 + j * 1060, 40)); row.paste(b, (540 + j * 1060, 40))
    dr.text((12, 8), p["name"] + "   (front | back | front | back)", fill="black", font=font); rows.append(row)
sheet = Image.new("RGB", (rows[0].width, 650 * len(rows)), "white")
for i, r in enumerate(rows): sheet.paste(r, (0, i * 650))
sheet.save(out, quality=85)
