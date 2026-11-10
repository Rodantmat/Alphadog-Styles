#!/usr/bin/env python3
"""Design-presence check for Printify cutouts: measures the printed-design ink area (excluding the tiny neck/brand tag) and rejects cutouts whose
visible design is missing or only a logo (e.g. polo back with just the neck tag)."""
import numpy as np, cv2
from PIL import Image
def ink(file):
    a=np.array(Image.open(file).convert("RGBA")); al=a[:,:,3]>240
    ys,xs=np.where(al); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    rgb=a[y0:y1,x0:x1,:3].astype("float32"); m=al[y0:y1,x0:x1].astype("uint8")
    m=cv2.erode(m,np.ones((15,15),np.uint8)); g=rgb.mean(axis=2)
    # remove folds/shading: compare against a heavy blur of the garment (masked)
    gm=g*m; bl=cv2.GaussianBlur(gm,(0,0),25)/np.maximum(cv2.GaussianBlur(m.astype("float32"),(0,0),25),1e-3)
    d=np.abs(g-bl)*m; ib=(d>38)&(m>0)
    n,lab,st,_=cv2.connectedComponentsWithStats(ib.astype("uint8"),8)
    h,w=g.shape; big=0; 
    for i in range(1,n):
        x,y,ww,hh,ar=st[i]
        if ar>=0.00035*h*w: big+=ar          # drop specks
    return big/max(m.sum(),1), (w,h)
if __name__=="__main__":
    import sys,json,glob,os
    sys.path.insert(0,"scripts/video"); import postc_build as P
    M=json.load(open("docs/printify_cameras.json")); rows=[]
    for it in P.pool():
        f,_=ink(it["file"]); rows.append((f,it["prod"],it["cam"],it["kind"],it.get("side")))
    rows.sort()
    for r in rows: print("%.4f %-18s %s %-10s %s"%r)
