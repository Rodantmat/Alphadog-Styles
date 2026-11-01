import json,re,os
import numpy as np
from PIL import Image
man=json.load(open("out/blanks/manifest.json")); cat=json.load(open("store/data/catalog.json"))
slug=lambda s:re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
have={}
for m in man:
    if not m["colors"] or len(m["colors"])!=1 or m["position"] not in("front","back"): continue
    k=(m["prod"],m["colors"][0],m["position"])
    if k in have: continue
    have[k]=m["file"]
for p in cat["products"]:
    keep=[]
    for c in p["colors"]:
        n,hx,ok=c[0],c[1],c[2]
        f,b=have.get((p["id"],n,"front")),have.get((p["id"],n,"back"))
        if ok and not(f and b): print("drop (no photos)",p["id"],n); continue
        if ok:
            for side,src in (("front",f),("back",b)):
                im=Image.open(src).convert("RGB"); im.save(f"store/img/{p['id']}_{slug(n)}_{side}.webp","WEBP",quality=80,method=6)
                if side=="front":
                    a=np.array(im)[620:760,480:720].reshape(-1,3); r,g,bb=np.median(a,axis=0).astype(int); hx="#%02x%02x%02x"%(r,g,bb)
            c=[n,hx,1,slug(n)]
        else: c=[n,hx,0,slug(n)]
        keep.append(c)
    p["colors"]=keep
cat["cal"]={"tee":{"front":[387.6,373.0,424.2,515.4],"back":[403.5,303.2,409.5,497.6]},"hoodie":{"front":[424.5,395.1,334.0,222.7],"back":[441.7,368.9,341.6,284.6]},"photo":1200}
json.dump(cat,open("store/data/catalog.json","w"),indent=1)
print({p["id"]:[(c[0],c[1],c[2]) for c in p["colors"]] for p in cat["products"]})
