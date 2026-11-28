"""Independent edge audit for composed-ready sprites (run on the CLEANED sprite). Returns dict of defect scores and a verdict.
Does not share code with sprite_clean: measures what a viewer sees on a dark and a light backdrop.
fringe: share of outline pixels brighter/whiter than the garment just inside | sliver: bright non-garment area near outline (armholes/gaps)
ghost: translucent alpha mass away from the body (box shadow) | verdict ok only if all under limits."""
import numpy as np, cv2
W=np.array([0.114,0.587,0.299],np.float32)
LIM=dict(fringe=0.10,sliver=0.0035,ghost=0.004,blob=0.0015)
def audit(im,kind="flat_front"):
    a=np.array(im.convert("RGBA")); al=a[...,3]/255.; bgr=cv2.cvtColor(a[...,:3],cv2.COLOR_RGB2BGR).astype(np.float32)
    solid=(al>0.5).astype(np.uint8); n,l,st,_=cv2.connectedComponentsWithStats(solid)
    if n<2: return dict(fringe=1,sliver=1,ghost=1,ok=False)
    big=1+int(np.argmax(st[1:,4])); keep=np.isin(l,[i for i in range(1,n) if st[i,4]>=0.02*st[big,4]]).astype(np.uint8)
    area=float(keep.sum()); dist=cv2.distanceTransform(keep,cv2.DIST_L2,3)
    lum=bgr@W
    rim=(dist>0)&(dist<=3); inn=(dist>7)&(dist<20)
    fr=0.0
    if rim.sum()>50 and inn.sum()>200:
        # local inner colour per rim pixel via blur
        m=inn.astype(np.float32); F=cv2.GaussianBlur(lum*m,(0,0),8)/(cv2.GaussianBlur(m,(0,0),8)+1e-3)
        sat=bgr.max(2)-bgr.min(2)
        bad=rim&((lum-F)>28)&(bgr.min(2)>175)
        fr=float(bad.sum())/float(rim.sum())
    core=dist>22; gm=float(np.median(lum[core])) if core.sum()>800 else 255.
    sl=0.0
    if gm<185 and kind!="person":
        sat=bgr.max(2)-bgr.min(2); wh=((bgr.min(2)>195)&(sat<30)&(al>0.3)&(dist<70)&(dist>0)).astype(np.uint8)
        wh=wh*(dist<34)   # print lives deeper inside; slivers hug the outline
        sl=float(wh.sum())/area
    gh=0.0
    if kind!="person":
        near=cv2.dilate(keep,np.ones((15,15),np.uint8))
        gh=float(((al>0.04)&(al<0.9)&(near==0)).sum())/area
    # blob: leftover photo-backdrop pieces (neutral grey/white) glued to the outline that contrast with the garment beside them: armhole slivers, cast shadow under caps/hems
    bl=0.0
    if kind!="person":
        sat=bgr.max(2)-bgr.min(2); neu=((sat<24)&(al>0.1)&(lum>95)&(dist<120)&(dist>0)).astype(np.uint8)
        nn,nl,nst,_=cv2.connectedComponentsWithStats(neu)
        for i in range(1,nn):
            if nst[i,4]<12 or nst[i,4]>0.12*area: continue
            c=nl==i; dd=dist[c]
            if dd.min()>8: continue
            ys=np.where(c.any(1))[0]
            if dd.max()>(85 if ys.min()>0.80*al.shape[0] else 62): continue
            ring=(cv2.dilate(c.astype(np.uint8),np.ones((9,9),np.uint8))>0)&(~c)&(keep>0)
            if ring.sum()<20: continue
            if np.median(sat[ring])>40 or abs(np.median(lum[c])-np.median(lum[ring]))>55: bl+=nst[i,4]
        bl=bl/area
    r=dict(fringe=round(fr,4),sliver=round(sl,5),ghost=round(gh,5),blob=round(bl,5)); r["ok"]=all(r[k]<=LIM[k] for k in LIM); return r
