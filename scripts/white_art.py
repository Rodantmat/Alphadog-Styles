"""Approved black-card tiles (white lines on black) -> clean white-ink vectors, one SVG per figure.
store/art_w/<theme>_<style>/<breed>_<front|back>.svg  (fill #fff; recoloured at render time).
Cells without a regenerated tile (sunglasses designs untouched) reuse the existing black vector, filled white."""
import sys,os,re,json,glob,numpy as np,cv2,potrace
from scipy import ndimage
from PIL import Image
from concurrent.futures import ProcessPoolExecutor
R="out/black_v2/"
M=json.load(open("/tmp/bv2/match.json")) if os.path.exists("/tmp/bv2/match.json") else json.load(open("scripts/white_art_match.json"))
S=4
def path_d(mask):
    try: pl=potrace.Bitmap(~mask).trace(turdsize=30,alphamax=1.1,opttolerance=0.6)
    except ValueError: pl=potrace.Bitmap(~mask).trace(turdsize=30,alphamax=1.1,opttolerance=0.6,opticurve=False)
    d=[]
    for c in pl:
        s=c.start_point; d.append(f"M{s.x:.1f},{s.y:.1f}")
        for sg in c.segments:
            if sg.is_corner: d.append(f"L{sg.c.x:.1f},{sg.c.y:.1f}L{sg.end_point.x:.1f},{sg.end_point.y:.1f}")
            else: d.append(f"C{sg.c1.x:.1f},{sg.c1.y:.1f} {sg.c2.x:.1f},{sg.c2.y:.1f} {sg.end_point.x:.1f},{sg.end_point.y:.1f}")
        d.append("Z")
    return "".join(d)
def split(ink):
    n,lab,st,cen=cv2.connectedComponentsWithStats(ink.astype(np.uint8),8)
    ids=list(range(1,n)); W=ink.shape[1]
    xs=np.array([cen[i][0] for i in ids]); ar=np.array([st[i,cv2.CC_STAT_AREA] for i in ids],float)
    c=np.array([W*.28,W*.74])
    for _ in range(30):
        asg=(np.abs(xs-c[1])<np.abs(xs-c[0])).astype(int)
        for k in (0,1):
            if (asg==k).any(): c[k]=np.average(xs[asg==k],weights=ar[asg==k])
    F=[i for i,a in zip(ids,asg) if a==0]; B=[i for i,a in zip(ids,asg) if a==1]
    mainF=max(F,key=lambda i:st[i,cv2.CC_STAT_AREA]); mainB=max(B,key=lambda i:st[i,cv2.CC_STAT_AREA])
    dF=cv2.distanceTransform((lab!=mainF).astype(np.uint8),cv2.DIST_L2,5); dB=cv2.distanceTransform((lab!=mainB).astype(np.uint8),cv2.DIST_L2,5)
    nf,nb=[mainF],[mainB]
    for i in ids:
        if i in (mainF,mainB): continue
        mk=lab==i
        (nf if dF[mk].min()<=dB[mk].min() else nb).append(i)
    return {"front":np.isin(lab,nf),"back":np.isin(lab,nb)}
def svg(w,h,d): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><path d="{d}" fill="#fff" fill-rule="evenodd"/></svg>'
def from_tile(path,erase=None):
    g=cv2.imread(path,0)
    if erase: x0,y0,x1,y1=erase; g[y0:y1,x0:x1]=0
    g=cv2.resize(g,None,fx=S,fy=S,interpolation=cv2.INTER_CUBIC); g=cv2.GaussianBlur(g,(0,0),2.2)
    ink=g>115
    ink=cv2.morphologyEx(ink.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8)).astype(bool)
    n,lab,st,_=cv2.connectedComponentsWithStats(ink.astype(np.uint8),8)
    for i in range(1,n):
        if st[i,cv2.CC_STAT_AREA]<400: ink[lab==i]=False
    out={}
    for name,m in split(ink).items():
        ys,xs=np.where(m); m=m[max(ys.min()-20,0):ys.max()+20,max(xs.min()-20,0):xs.max()+20]
        out[name]=svg(m.shape[1],m.shape[0],path_d(m))
    return out
def job(a):
    key,src=a; num,rest=key.split("|")[0],key.split("|")[1]
    breed=re.sub(r"^\d+_","",num); theme_style=rest
    od=f"store/art_w/{theme_style}"; os.makedirs(od,exist_ok=True)
    if src is None:  # reuse black vector, white fill
        for side in ("front","back"):
            s=open(f"store/art/{theme_style}/{breed}_{side}.svg").read()
            s=re.sub(r'fill="#?(000|000000|black)"','fill="#fff"',s)
            if 'fill="#fff"' not in s: s=s.replace("<path ",'<path fill="#fff" ',1)
            open(f"{od}/{breed}_{side}.svg","w").write(s)
        return key,"vec"
    erase=None; path=src
    if key=="19_pomeranian|geo_heart": erase=(771,412,822,463)
    if key=="27_pug|line_cool": path="/tmp/bv2/pug_cool_final.png"
    o=from_tile(path,erase)
    for side,s in o.items(): open(f"{od}/{breed}_{side}.svg","w").write(s)
    return key,"tile"
if __name__=="__main__":
    jobs=[]
    for k,v in M.items():
        err,rel=v[0]
        is_cool=k.endswith("cool")
        use_tile=err<=60 and not rel.startswith("refs/")
        if k=="27_pug|line_cool": use_tile=True
        jobs.append((k,(R+rel) if use_tile else None))
    json.dump(M,open("scripts/white_art_match.json","w"))
    with ProcessPoolExecutor(4) as ex:
        for k,t in ex.map(job,jobs): pass
    print(len(jobs),"done")
