#!/usr/bin/env python3
"""FEED-CROP CONTACT SHEET (owner 2026-11-19). Instagram/Facebook show a reel in the scrolling FEED as a centred 4:5 crop of the 1080x1920 frame
(rows 285-1635) with the account/audio bar over the top ~125 px of that crop (rows 285-410). Anything outside rows 430-1580 is cut or covered.
usage: feedcrop.py video.mp4 out.jpg [fps=2]   -> tiles the feed view of every frame; the red band marks the covered bar, the green lines the safe zone.
LOOK at it: every word of text and every garment must be fully inside the green lines in EVERY tile."""
import subprocess, sys, os, tempfile, glob
from PIL import Image, ImageDraw
v, out = sys.argv[1], sys.argv[2]; fps = sys.argv[3] if len(sys.argv) > 3 else "2"
d = tempfile.mkdtemp()
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", v, "-vf", f"fps={fps},crop=1080:1350:0:285,scale=270:338", f"{d}/f%04d.png"], check=True)
fr = sorted(glob.glob(f"{d}/f*.png")); cols = 8; rows = (len(fr) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 274, rows * 342), (30, 30, 30))
for i, p in enumerate(fr):
    im = Image.open(p).convert("RGB"); dr = ImageDraw.Draw(im, "RGBA")
    dr.rectangle([0, 0, 270, 31], fill=(255, 0, 0, 90))                      # account/audio bar (crop rows 285-410)
    dr.line([0, 36, 270, 36], fill=(0, 255, 0, 255)); dr.line([0, 338 - 8, 270, 338 - 8], fill=(0, 255, 0, 255))   # safe zone: frame rows 430 / 1580 -> 36 / 330 in the tile... (bottom 1580 = 330)
    sheet.paste(im, ((i % cols) * 274, (i // cols) * 342))
sheet.save(out, quality=88); print(out, len(fr), "tiles")
