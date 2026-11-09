"""nb_export.py COMPDIR OUTDIR -> per breed transparent PNG exports (2400px) + light/dark contact sheets."""
import sys, os, glob, numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/claude/alphadog-styles/scripts'); from nb_lib import split_x, split_masks
import cv2
comp, out = sys.argv[1:3]
BREEDS = ["lhasa_apso", "miniature_pinscher", "vira_lata"]
ORDER = [("line","classic"),("line","cool"),("line","heart"),("geo","classic"),("geo","cool"),("geo","heart")]
TH={"line":"Linha","geo":"Geom."}; VA={"classic":"Classico","cool":"Oculos","heart":"Coracao"}
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
def parts(n, mode):
    a = np.array(Image.open(f"{comp}/{mode}/{n}.png")); m = a > 128; fm, bm = split_masks(m); res = {}
    for side, mm in (("front", fm), ("back", bm)):
        d = cv2.dilate(mm.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        other = bm if side == "front" else fm
        keep = d & ~(cv2.dilate(other.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0 & ~d)
        sub = np.where(d, a, 0).astype(np.uint8); mk = mm; ys, xs = np.where(mk)
        pad = 20; y0, y1 = max(ys.min()-pad, 0), min(ys.max()+pad, mk.shape[0]); x0, x1 = max(xs.min()-pad, 0), min(xs.max()+pad, mk.shape[1])
        sub = sub[y0:y1, x0:x1]; h, w = sub.shape; t = 2400/max(h, w)
        res[side] = Image.fromarray(sub).resize((round(w*t), round(h*t)), Image.LANCZOS)
    return res
for b in BREEDS:
    sheets = {}
    for mode, bg, fg in (("light", 255, 0), ("dark", 0, 255)):
        sh = Image.new("RGB", (2000, 1560), (bg,)*3); d = ImageDraw.Draw(sh)
        d.text((12, 8), f"{b.replace('_',' ').title()} - {mode.upper()} card ({'black' if mode=='light' else 'white'} lines)", fill=(200,0,0), font=F)
        sheets[mode] = (sh, d)
    for i, (th, v) in enumerate(ORDER):
        n = f"{th}_{b}_{v}"
        for mode, bg, fg in (("light", 255, 0), ("dark", 0, 255)):
            p = parts(n, mode)
            for side, al in p.items():
                for ink, col in (("black", 0), ("white", 255)):
                    if (ink == "black") != (mode == "light") and False: pass
                ink, col = ("black", 0) if mode == "light" else ("white", 255)
                o = Image.new("RGBA", al.size, (col, col, col, 0)); o.putalpha(al)
                dd = f"{out}/{b}/{ink}_ink"; os.makedirs(dd, exist_ok=True); o.save(f"{dd}/{b}_{th}_{v}_{side}_{ink}ink.png")
            sh, d = sheets[mode]
            r, c = divmod(i, 2)
            for j, side in enumerate(("front", "back")):
                im = p[side]; W, H = 470, 440; t = min(W/im.width, H/im.height); im2 = im.resize((max(1,round(im.width*t)), max(1,round(im.height*t))), Image.LANCZOS)
                tile = Image.new("L", im2.size, bg); 
                x = (c*2+j)*500+15+(W-im2.width)//2; y = 40+r*500+(H-im2.height)//2
                if mode == "light": sh.paste(Image.new("RGB", im2.size, (0,0,0)), (x, y), im2)
                else: sh.paste(Image.new("RGB", im2.size, (255,255,255)), (x, y), im2)
                d.text(((c*2+j)*500+15, 40+r*500+455), f"{TH[th]} {VA[v]} {side}", fill=(200,0,0), font=F)
    for mode in ("light", "dark"):
        os.makedirs(out, exist_ok=True); sheets[mode][0].save(f"{out}/{b}_{mode}_card.jpg", quality=90)
print("ok")
