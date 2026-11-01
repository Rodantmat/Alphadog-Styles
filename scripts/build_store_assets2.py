"""Store photos + print-area calibration for tanks, polos and caps from out/blanks2 (Printify mockups)."""
import json,os,re
from PIL import Image
import numpy as np
m=json.load(open("out/blanks2/manifest.json")); meta=m["meta"]
PICK={"tank":{"front":"front","back":"back"},"wtank":{"front":"front","back":"back"},"polo":{"front":"front"},"wpolo":{"front":"left_chest_dtf"},
      "cap_dad":{"front":"front_dtf"},"cap_foam":{"front":"front"},"cap_mesh":{"front":"front"}}
slug=lambda c:re.sub(r"[^a-z0-9]+","-",c.lower()).strip("-")
def magenta(fn):
    a=np.asarray(Image.open(fn).convert("RGB")).astype(int); mk=(a[...,0]>170)&(a[...,2]>150)&(a[...,1]<120)
    if mk.sum()<500: return None
    ys,xs=np.where(mk); return [int(xs.min()),int(ys.min()),int(xs.max()-xs.min()+1),int(ys.max()-ys.min()+1)]
out={}
for prod,sides in PICK.items():
    out[prod]={"cal":{},"colors":{}}
    for side,pos in sides.items():
        cal_imgs=[i for i in m["images"] if i["prod"]==prod and i["kind"]=="calib" and i["position"]==pos]
        bl_imgs=[i for i in m["images"] if i["prod"]==prod and i["kind"]=="blank" and i["position"]==pos]
        for col in sorted({c for i in cal_imgs for c in i["colors"]}):
            ci=[i for i in cal_imgs if col in i["colors"]]; bi=[i for i in bl_imgs if col in i["colors"]]
            if not ci or not bi: continue
            box=magenta(ci[0]["file"])
            if not box: continue
            out[prod]["cal"].setdefault(side,box)  # same geometry for every color; keep first
            im=Image.open(bi[0]["file"]).convert("RGB")
            dst=f"store/img/{prod}_{slug(col)}_{side}.webp"; im.save(dst,"WEBP",quality=82)
            x,y,w,h=box; reg=np.asarray(im.crop((x+w//4,y+h//4,x+3*w//4,y+3*h//4))).reshape(-1,3)
            med=np.median(reg,axis=0).astype(int); out[prod]["colors"].setdefault(col,{"hex":"#%02x%02x%02x"%tuple(med),"slug":slug(col),"sides":[]})["sides"].append(side)
json.dump(out,open("out/blanks2/store_assets.json","w"),indent=1)
for p,v in out.items(): print(p,v["cal"],{c:(x["hex"],x["sides"]) for c,x in v["colors"].items()})
