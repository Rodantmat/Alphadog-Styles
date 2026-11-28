"""Edge repair for Printify transparent sprites (out/trans, out/trans2) before they are composed into a reel.
Fixes, at the source, what the owner keeps seeing: white fringe/halo on the outline, white slivers in armholes/gaps,
frayed mesh edges and hard box shadows baked into the sprite alpha. usage: sprite_clean.clean(PIL_RGBA, kind) -> PIL_RGBA
kind: person | flat_front | flat_back | folded | closeup (anything else is treated as a flat product)."""
import numpy as np, cv2
from PIL import Image
W=np.array([0.114,0.587,0.299],np.float32)
def clean(im,kind="flat_front"):
    a0=np.array(im.convert("RGBA")); bgr=cv2.cvtColor(a0[...,:3],cv2.COLOR_RGB2BGR).astype(np.float32); al=a0[...,3].astype(np.float32)/255
    person=(kind=="person")
    solid=(al>0.78).astype(np.uint8)
    n,l,st,_=cv2.connectedComponentsWithStats(solid)
    if n<2: return im
    # keep every sizeable component (a person has hair/arm islands); drop specks
    keep=np.zeros_like(solid)
    big=st[1:,4].max()
    for i in range(1,n):
        if st[i,4]>=0.02*big: keep[l==i]=1
    dist=cv2.distanceTransform(keep,cv2.DIST_L2,3)
    # 1) box shadows / ghost alpha: anything translucent that is not hugging the solid body goes (flat products only; hair needs its fringe)
    if not person:
        near=cv2.dilate(keep,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
        al=np.where((near==0)&(al<0.95),0,al)
    # 2) leftover photo-backdrop pieces: neutral (grey/white) blobs that hug the outline and contrast with the garment next to them
    #    = armhole slivers, white fringe pockets, grey cast-shadow under caps. Prints never touch the outline and are deeper than 62 px, so they are safe.
    if not person:
        sat=bgr.max(2)-bgr.min(2); lum0=bgr@W
        neu=((sat<24)&(al>0.1)&(lum0>95)&(dist<120)).astype(np.uint8)
        nn,nl,nst,_=cv2.connectedComponentsWithStats(neu); A=float(keep.sum()); rm=np.zeros_like(neu)
        for i in range(1,nn):
            comp=(nl==i)
            if nst[i,4]<12 or nst[i,4]>0.12*A: continue
            dd=dist[comp]
            ysb=np.where(comp.any(1))[0]; low=ysb.min()>0.80*al.shape[0]                      # grey cast shadow under a cap/hem sits in the bottom 20 %
            if dd.min()>8 or dd.max()>(85 if low else 62): continue
            ring=(cv2.dilate(comp.astype(np.uint8),np.ones((9,9),np.uint8))>0)&(~comp)&(keep>0)&(dist>0)
            if ring.sum()<20: continue
            rs=float(np.median(sat[ring])); rl=float(np.median(lum0[ring])); cl=float(np.median(lum0[comp]))
            if rs>40 or abs(cl-rl)>55: rm|=comp.astype(np.uint8)
        if rm.any(): rm=cv2.dilate(rm,np.ones((5,5),np.uint8)); al=np.where(rm>0,0,al)
    # 3) trim 1.5px from the outline, then re-feather: kills the white mixed-in rim
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    hard=(al>0.5).astype(np.uint8); hard=cv2.erode(hard,k,iterations=1 if person else 2)
    keep2=hard
    d2=cv2.distanceTransform(keep2,cv2.DIST_L2,3)
    # 4) colour bleed: rim pixels (<5px from the new edge) take the colour of the garment just inside, never the leftover backdrop
    inner=((d2>6)&(d2<22)).astype(np.float32)
    if inner.sum()>400:
        num=cv2.GaussianBlur(bgr*inner[...,None],(0,0),6); den=cv2.GaussianBlur(inner,(0,0),6)[...,None]+1e-3; F=num/den
        rim=(d2<=5)&(al>0.02)
        L0=bgr@W; LF=F@W
        sat0=bgr.max(2)-bgr.min(2); satF=F.max(2)-F.min(2)
        rim9=(d2<=9)&(al>0.02)&(sat0<32)&(satF>38)&((L0-LF)>22)      # neutral-white pixels on a coloured garment's edge (foam-cap visor rim, mesh edge)
        bad=(rim&(((L0-LF)>18)|((L0-LF)<-55)))|rim9
        bgr=np.where(bad[...,None],F,bgr)
    # soft outline: 1.2px feather from the trimmed mask, intersected with the old alpha
    soft=cv2.GaussianBlur(keep2.astype(np.float32),(0,0),0.9)
    al=np.minimum(al,np.where(cv2.dilate(keep2,np.ones((5,5),np.uint8))>0,np.maximum(soft,0),0))
    # interior stays opaque
    al=np.where(d2>2.5,np.maximum(al,np.where(keep2>0,1.0,0)),al)
    out=np.dstack([cv2.cvtColor(np.clip(bgr,0,255).astype(np.uint8),cv2.COLOR_BGR2RGB),np.clip(al*255,0,255).astype(np.uint8)])
    return Image.fromarray(out,"RGBA")
