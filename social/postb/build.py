#!/usr/bin/env python3
"""Post B builder: Printify mockup carousels (1080x1350) + Reels (1080x1920 mp4). Run from repo root: python3 social/postb/build.py [ids...]"""
import json, os, subprocess, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
MK = "store/mk"; OUT = "out/postb"; LOGO = "store/logo.png"
FB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"; FR = "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf"
def font(p, s): return ImageFont.truetype(p, s)
PAL = {  # name: (top, bottom, ink)
 "cream": ((250,243,230),(231,214,190),(40,34,30)), "sage": ((205,222,205),(150,176,152),(28,40,30)),
 "dusk": ((52,58,92),(24,26,48),(245,240,232)), "clay": ((226,170,140),(176,108,84),(255,248,240)),
 "sky": ((196,220,240),(130,170,205),(24,36,52)), "sand": ((236,224,200),(196,176,140),(44,36,24)),
 "plum": ((92,56,84),(44,26,44),(250,240,246)), "mint": ((214,240,230),(150,200,184),(20,44,40)),
 "slate": ((88,96,108),(36,40,48),(244,244,244)), "rose": ((244,214,214),(206,150,160),(60,30,36)),
 "gold": ((240,214,150),(196,150,70),(50,34,12)), "ink": ((38,40,46),(12,12,16),(246,244,240))}
def bg(w, h, pal, seed=0):
    t, b, _ = PAL[pal]; y = np.linspace(0, 1, h)[:, None, None]
    a = np.array(t)[None, None, :] * (1 - y) + np.array(b)[None, None, :] * y
    a = np.repeat(a, w, axis=1)
    rng = np.random.default_rng(seed); n = rng.normal(0, 3.2, (h, w, 1)); a = np.clip(a + n, 0, 255)
    xx = np.linspace(-1, 1, w)[None, :, None]; yy = np.linspace(-1, 1, h)[:, None, None]
    a = a * (1 - 0.18 * np.clip(xx**2 + yy**2 - 0.3, 0, 1))
    return Image.fromarray(a.astype("uint8"))
def card(path, size):
    im = Image.open(path).convert("RGB").resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], 44, fill=255)
    sh = Image.new("RGBA", (size + 160, size + 160), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([80, 100, size + 80, size + 100], 44, fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(34)); return im, m, sh
def text_c(d, xy, s, f, fill):
    w = d.textlength(s, font=f); d.text((xy[0] - w / 2, xy[1]), s, font=f, fill=fill)
def compose(path, pal, w, h, label, seed, cap=None, cy=None, size=None):
    base = bg(w, h, pal, seed).convert("RGBA"); ink = PAL[pal][2]
    size = size or int(w * 0.88); im, m, sh = card(path, size)
    cx = w // 2; cy = cy or h // 2
    base.alpha_composite(sh, (cx - size // 2 - 80, cy - size // 2 - 80)); base.paste(im, (cx - size // 2, cy - size // 2), m)
    d = ImageDraw.Draw(base)
    # brand: logo top-right, wordmark bottom (never over product)
    if os.path.exists(LOGO):
        lg = Image.open(LOGO).convert("RGBA"); lg.thumbnail((92, 92)); base.alpha_composite(lg, (w - 92 - 44, 40))
    text_c(d, (w / 2, h - 86), "AlphaDog Styles", font(FB, 36), ink)
    if label: text_c(d, (w / 2, 54 if h < 1500 else 120), label, font(FB, 46), ink)
    if cap: text_c(d, (w / 2, h - 150 if h < 1500 else h - 190), cap, font(FR, 32), ink)
    return base.convert("RGB")
def cta(w, h, pal, line1, line2, seed):
    base = bg(w, h, pal, seed); d = ImageDraw.Draw(base); ink = PAL[pal][2]
    if os.path.exists(LOGO):
        lg = Image.open(LOGO).convert("RGBA"); lg.thumbnail((240, 240)); base.paste(lg, (w // 2 - lg.width // 2, h // 2 - 330), lg)
    text_c(d, (w / 2, h // 2 - 40), line1, font(FB, 64), ink); text_c(d, (w / 2, h // 2 + 60), line2, font(FR, 40), ink)
    text_c(d, (w / 2, h // 2 + 170), "alphadogstyles.com", font(FB, 52), ink)
    text_c(d, (w / 2, h // 2 + 250), "33 breeds  -  dark & light colours", font(FR, 32), ink)
    return base
def build(pid, p):
    od = f"{OUT}/{pid}"; os.makedirs(od, exist_ok=True)
    files = [f"{MK}/{f}" for f in p["files"]]; miss = [f for f in files if not os.path.exists(f)]
    if miss: print("MISSING", pid, miss); return
    pal = p["pal"]; L = p.get("labels") or []; n = len(files)
    labels = ([L[0]] + L[2:] if len(L) == n + 1 and False else None)
    labels = [L[0]] + L[2:] if len(L) == n + 1 else (L if len(L) == n else [p["title"]] + [""] * n)
    caps = p.get("caps") or [""] * len(files)
    if p["kind"] == "carousel":
        W, H = 1080, 1350
        for i, f in enumerate(files):
            compose(f, pal, W, H, labels[i], i, caps[i], cy=H // 2 + 10).save(f"{od}/slide{i+1:02d}.jpg", quality=92)
        cta(W, H, pal, p["cta1"], p["cta2"], 99).save(f"{od}/slide{len(files)+1:02d}.jpg", quality=92)
    else:
        W, H = 1080, 1920; fr = []
        for i, f in enumerate(files):
            fn = f"{od}/f{i:02d}.png"; compose(f, pal, W, H, labels[i], i, caps[i], cy=H // 2 - 20).save(fn); fr.append(fn)
        fn = f"{od}/f_cta.png"; cta(W, H, pal, p["cta1"], p["cta2"], 99).save(fn); fr.append(fn)
        fn0 = f"{od}/f_intro.png"; bg(W, H, pal, 5).save(fn0); fr = [fn0] + fr
        D, X = [0.7] + [1.45] * len(files) + [1.5], 0.45  # durations, crossfade
        ins = []; filt = []
        for i, f in enumerate(fr):
            ins += ["-loop", "1", "-t", f"{D[i]+X}", "-i", f]
            filt.append(f"[{i}:v]scale=1188:2112,zoompan=z='min(zoom+0.0007,1.07)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,setsar=1,format=yuv420p[v{i}]")
        cur = "v0"; t = 0
        for i in range(1, len(fr)):
            t += D[i-1]; filt.append(f"[{cur}][v{i}]xfade=transition=fade:duration={X}:offset={t:.2f}[x{i}]"); cur = f"x{i}"
        total = sum(D) + X
        mus = p["music"]; ins += ["-ss", "0", "-i", f"out/music2/{mus}"]
        a = f"[{len(fr)}:a]atrim=0:{total:.2f},afade=t=in:d=0.6,afade=t=out:st={total-1.2:.2f}:d=1.2,volume=0.55[a]"
        cmd = ["ffmpeg", "-y", "-v", "error"] + ins + ["-filter_complex", ";".join(filt + [a]), "-map", f"[{cur}]", "-map", "[a]", "-t", f"{total:.2f}",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", f"{od}/reel.mp4"]
        subprocess.run(cmd, check=True)
        for f in fr: os.remove(f)
    open(f"{od}/caption.txt", "w").write(p["caption"]); print("BUILT", pid, p["kind"])
if __name__ == "__main__":
    plan = json.load(open("social/postb/plan.json")); ids = sys.argv[1:] or list(plan)
    for k in ids: build(k, plan[k])
