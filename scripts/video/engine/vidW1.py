#!/usr/bin/env python3
"""d7 'Which one is yours?' re-creation from the trimmed merch library + 300 backgrounds.
usage: python3 vidW1.py cfg.json   cfg: {out, music, ss, scenes:[{head, item:'product/breed/code', bg:id}], cta_head}
Layout (phone-safe): logo pill y~276, heading y~436, merch centred y~1010 (top >= 650), CTA pill y~1330 (final scene)."""
import sys, json, subprocess, glob
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
R = '/home/claude/alphadog-styles/'
W, H, FPS = 1080, 1920, 30
FB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
cfg = json.load(open(sys.argv[1]))

def font(s): return ImageFont.truetype(FB, s)
def bg(i):
    f = glob.glob(R + f'out/backgrounds/bg_{i:03d}_*.jpg')[0]
    return Image.open(f).convert('RGB').resize((W, H))
def pill(txt, size, logo=True, fill=(18, 20, 26, 215)):
    f = font(size); d0 = ImageDraw.Draw(Image.new('L', (1, 1))); tw = int(d0.textlength(txt, font=f)) + (size + 18 if logo else 0)
    h = int(size * 1.9); im = Image.new('RGBA', (tw + 70, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, h - 1], radius=h // 2, fill=fill, outline=(255, 255, 255, 70), width=2)
    x = 32
    if logo:
        lg = Image.open(R + 'store/logo.png').convert('RGBA'); lg.thumbnail((int(h * .72), int(h * .72))); d.ellipse([x - 8, (h - lg.height) // 2 - 2, x - 6 + lg.width + 2, (h + lg.height) // 2 + 2], fill=(255, 255, 255, 255)); im.paste(lg, (x - 6, (h - lg.height) // 2), lg); x += lg.width + 14
    d.text((x, h // 2), txt, font=f, fill=(255, 255, 255, 255), anchor='lm'); return im
def head(txt, size):
    f = font(size); d0 = ImageDraw.Draw(Image.new('L', (1, 1))); sp = 6
    tw = int(sum(d0.textlength(c, font=f) + sp for c in txt)); im = Image.new('RGBA', (tw + 40, size * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 20
    for c in txt:
        d.text((x + 2, size + 3), c, font=f, fill=(0, 0, 0, 140), anchor='lm'); d.text((x, size), c, font=f, fill=(255, 255, 255, 255), anchor='lm'); x += d.textlength(c, font=f) + sp
    return im
def merch(code, box=(800, 720)):
    p, b, c = code.split('/'); im = Image.open(R + f'out/merch_lib/{p}/{b}/{c}.webp').convert('RGBA')
    bb = im.getchannel('A').getbbox(); im = im.crop(bb); s = min(box[0] / im.width, box[1] / im.height); return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
def shadow(m):
    a = np.array(m.getchannel('A')).astype(np.float32) / 255; s = cv2.GaussianBlur(a, (0, 0), 22) * 0.55
    sh = Image.new('RGBA', m.size, (0, 0, 0, 0)); sh.putalpha(Image.fromarray((s * 255).astype(np.uint8))); return sh
def scene(sc, t, final=False, cta=None, cta_on=False):
    im = bg(sc['bg']).convert('RGBA');
    # soft top/bottom darkening for legibility (never on merch)
    ov = np.zeros((H, W, 4), np.uint8); yy = np.arange(H)[:, None]; a = (np.clip((620 - yy) / 400, 0, 1) * 110).astype(np.uint8); ov[..., 3] = np.repeat(a, W, 1); im.alpha_composite(Image.fromarray(ov))
    pop = 0.94 + 0.06 * (1 - np.exp(-t * 9)); m = merch(sc['item'], (800, 600) if cta_on else (800, 720)); m = m.resize((int(m.width * pop * (1 + 0.04 * min(t, 2.5) / 2.5)), int(m.height * pop * (1 + 0.04 * min(t, 2.5) / 2.5))), Image.LANCZOS)
    cy = 940 if cta_on else 1010; x = (W - m.width) // 2; y = cy - m.height // 2
    sh = shadow(m); im.alpha_composite(sh, (x + 14, y + 22)); im.alpha_composite(m, (x, y))
    pl = pill('ALPHADOG STYLES', 30); im.alpha_composite(pl, ((W - pl.width) // 2, 276 - pl.height // 2))
    hd = sc['head']; lines = hd if isinstance(hd, list) else [hd]
    for i, l in enumerate(lines):
        h = head(l, sc.get('hs', 80)); im.alpha_composite(h, ((W - h.width) // 2, 436 + i * 96 - h.height // 2))
    if cta:
        c = pill(cta, 36, logo=False, fill=(255, 255, 255, 235)); d = ImageDraw.Draw(c)
        c2 = Image.new('RGBA', c.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(c2); d2.rounded_rectangle([0, 0, c.width - 1, c.height - 1], radius=c.height // 2, fill=(255, 255, 255, 240))
        d2.text((c.width // 2, c.height // 2), cta, font=font(36), fill=(20, 20, 26, 255), anchor='mm'); im.alpha_composite(c2, ((W - c.width) // 2, 1390))
    return np.array(im.convert('RGB'))[:, :, ::-1]

sc = cfg['scenes']; D = cfg.get('dur', [2.3, 2.3, 2.3, 3.1]); X = 0.18
frames_per = [int(d * FPS) for d in D]; total = sum(frames_per)
p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '/tmp/s/_w1_silent.mp4'], stdin=subprocess.PIPE)
last = None
for si, s in enumerate(sc):
    fin = si == len(sc) - 1
    for f in range(frames_per[si]):
        fr = scene(s, f / FPS, fin, cfg['cta'] if (fin and f > 8) else None, fin)
        if last is not None and f < int(X * FPS):
            a = (f + 1) / (X * FPS + 1); fr = cv2.addWeighted(last, 1 - a, fr, a, 0)
        p.stdin.write(fr.tobytes())
    last = scene(s, 99, fin, cfg['cta'] if fin else None, fin)
p.stdin.close(); p.wait()
T = total / FPS
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', '/tmp/s/_w1_silent.mp4', '-ss', str(cfg.get('ss', 0)), '-i', R + 'out/music2/' + cfg['music'] if not cfg['music'].startswith('t') else R + 'out/music/' + cfg['music'],
    '-filter_complex', f'[1:a]atrim=0:{T:.2f},afade=t=in:d=0.4,afade=t=out:st={T-1.2:.2f}:d=1.2,volume=0.7[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{T:.2f}', '-movflags', '+faststart', cfg['out']], check=True)
print('BUILT', cfg['out'], T)
