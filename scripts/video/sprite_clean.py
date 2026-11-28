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
    # 2) enclosed / edge-hugging white slivers when the garment itself is not white (armholes, gaps between sleeve and body)
    lum=bgr@W; core=dist>22
    gm=float(np.median(lum[core])) if core.sum()>800 else 255.0
    if gm<185 and not person:
        sat=bgr.max(2)-bgr.min(2)
        wh=((bgr.min(2)>200)&(sat<26)&(al>0.1)&(dist<70)).astype(np.uint8)
        wh=cv2.dilate(wh,np.ones((5,5),np.uint8))
        # never delete the print itself: keep white pixels that sit inside the garment body (far from the outline, surrounded by solid garment)
        body=cv2.erode(keep,np.ones((1,1),np.uint8)); body=(cv2.distanceTransform(body,cv2.DIST_L2,3)>34)
        wh=np.where(body,0,wh); al=np.where(wh>0,0,al)
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
        bad=rim&(((L0-LF)>18)|((L0-LF)<-55))
        bgr=np.where(bad[...,None],F,bgr)
    # soft outline: 1.2px feather from the trimmed mask, intersected with the old alpha
    soft=cv2.GaussianBlur(keep2.astype(np.float32),(0,0),0.9)
    al=np.minimum(al,np.where(cv2.dilate(keep2,np.ones((5,5),np.uint8))>0,np.maximum(soft,0),0))
    # interior stays opaque
    al=np.where(d2>2.5,np.maximum(al,np.where(keep2>0,1.0,0)),al)
    out=np.dstack([cv2.cvtColor(np.clip(bgr,0,255).astype(np.uint8),cv2.COLOR_BGR2RGB),np.clip(al*255,0,255).astype(np.uint8)])
    return Image.fromarray(out,"RGBA")
