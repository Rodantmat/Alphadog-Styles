"""Download candidate free clips, make contact sheets (committed to out/video_proto/) + pose stats."""
import os,sys,subprocess,json,urllib.request
os.makedirs("out/video_proto/src",exist_ok=True)
IDS=[87,86,49337,36996,16119,43153]
def get(i):
    for res in ("1080","720","360"):
        u=f"https://assets.mixkit.co/videos/{i}/{i}-{res}.mp4"
        p=f"out/video_proto/src/{i}.mp4"
        try:
            req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"})
            open(p,"wb").write(urllib.request.urlopen(req,timeout=90).read()); return p,res
        except Exception as e: print("fail",u,str(e)[:60])
    return None,None
for i in IDS:
    p,res=get(i)
    if not p: continue
    import cv2
    cap=cv2.VideoCapture(p); n=int(cap.get(7)); fps=cap.get(5); w=int(cap.get(3)); h=int(cap.get(4))
    print(i,res,f"{w}x{h} {fps:.1f}fps {n/fps:.1f}s",os.path.getsize(p)//1024,"KB")
    tiles=[]
    for k in range(6):
        cap.set(1,int(n*(k+0.5)/6)); ok,f=cap.read()
        if ok: tiles.append(cv2.resize(f,(240,int(240*h/w))))
    import numpy as np
    if tiles: cv2.imwrite(f"out/video_proto/sheet_{i}.jpg",np.hstack(tiles))
