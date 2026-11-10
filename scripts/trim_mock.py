import json,glob,os,hashlib
from PIL import Image,ImageChops
import numpy as np
R=json.load(open("out/mockexact/result.json"))
rep=[]
for prod,r in R.items():
    d="out/mockexact/"+prod.replace(" ","_").replace("'","")
    o="out/mockexact_trim/"+os.path.basename(d); os.makedirs(o,exist_ok=True)
    dup={i for i,h,dd in r["ok"] if dd}
    for i,h,dd in r["ok"]:
        if dd: continue
        im=Image.open(f"{d}/{i}.jpg").convert("RGB"); a=np.asarray(im).astype(int)
        mask=(255-a.min(axis=2))>14
        ys,xs=np.where(mask)
        if len(xs)==0: rep.append((prod,i,"EMPTY")); im.save(f"{o}/{i}.png"); continue
        x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
        frac=(x1-x0)*(y1-y0)/(im.width*im.height)
        edge=mask[0].any() or mask[-1].any() or mask[:,0].any() or mask[:,-1].any()
        if edge or frac>0.9: out=im; kind="kept-full(scene)"
        else:
            p=int(0.03*max(x1-x0,y1-y0)); out=im.crop((max(0,x0-p),max(0,y0-p),min(im.width,x1+p),min(im.height,y1+p))); kind="trimmed"
        out.save(f"{o}/{i}.png"); rep.append((prod,i,kind,im.size,out.size))
json.dump(rep,open("out/mockexact_trim/report.json","w"))
from collections import Counter
print(Counter((p,k[0] if False else k) for p,i,k,*_ in rep))
for x in rep: print(x)
