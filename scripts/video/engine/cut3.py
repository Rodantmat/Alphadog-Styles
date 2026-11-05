import cv2,numpy as np,time
from pymatting import estimate_alpha_cf,estimate_foreground_ml
def hard_mask(im,wthr=14):
    f=im.astype(np.float32);d=np.abs(f-255).sum(2)
    m=(d>30).astype(np.uint8);m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV);S,V=hsv[...,1].astype(np.float32),hsv[...,2].astype(np.float32)
    core=hsv[(hsv[...,2]<225)&(m>0)];ms=np.median(core[...,1]) if len(core) else 0
    vthr=226 if ms>38 else 243
    bgpix=((V>vthr)&(S<(16 if ms>38 else 6)))|((ms>38)&(S<ms*0.5)&(V>195))
    bgpix=cv2.dilate(bgpix.astype(np.uint8),np.ones((3,3),np.uint8))>0
    m[bgpix]=0
    m[cv2.GaussianBlur(d,(0,0),1.5)<wthr]=0;m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((4,4),np.uint8))
    n,l,st,_=cv2.connectedComponentsWithStats(m);m=(l==1+np.argmax(st[1:,4])).astype(np.uint8)
    inv=(1-m).astype(np.uint8);nn,ll,ss,_=cv2.connectedComponentsWithStats(inv,connectivity=4);h,w=m.shape
    for i in range(1,nn):
        x,y,ww,hh,ar=ss[i]
        if ar<500 and x>0 and y>0 and x+ww<w and y+hh<h and (np.abs(im.astype(np.float32)-255).sum(2)[ll==i].mean()>70): m[ll==i]=1
    return m
def desat_clean(c,k=0.5):
    hsv=cv2.cvtColor(c,cv2.COLOR_BGR2HSV);core=hsv[(hsv[...,2]<235)&(hsv[...,1]>12)]
    ms=np.median(core[...,1]);c=c.copy();c[(hsv[...,1]<ms*k)&(hsv[...,2]>120)]=255;return c
def matte(im,wthr=14,sat=False,band=(4,4),er=3):
    """closed-form alpha matting + multilevel foreground estimation (removes white contamination)"""
    if sat: im=desat_clean(im)
    m=hard_mask(im,wthr);x,y,w,h=cv2.boundingRect(m);pad=16
    x0,y0=max(x-pad,0),max(y-pad,0);x1,y1=min(x+w+pad,im.shape[1]),min(y+h+pad,im.shape[0])
    c=im[y0:y1,x0:x1];mm=m[y0:y1,x0:x1];global LAST;LAST=(x0,y0,im.shape[1],im.shape[0])
    fg=cv2.erode(mm,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*band[0]+1,)*2))
    bgm=1-cv2.dilate(mm,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*band[1]+1,)*2))
    tri=np.full(mm.shape,0.5,np.float64);tri[fg>0]=1;tri[bgm>0]=0
    rgb=c[...,::-1].astype(np.float64)/255
    a=estimate_alpha_cf(rgb,tri)
    F=estimate_foreground_ml(rgb,a)
    a=np.clip(a,0,1)
    rgb8=np.clip(F[...,::-1]*255,0,255).astype(np.uint8)
    solid=cv2.erode((a>0.9).astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*er+1,2*er+1)))
    dist,lab=cv2.distanceTransformWithLabels(1-solid,cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_PIXEL)
    ys,xs=np.nonzero(solid);near=rgb8[ys[lab-1],xs[lab-1]]
    nb=cv2.GaussianBlur(near,(0,0),1.2)
    rgb8=np.where((solid>0)[...,None],rgb8,nb)
    pure=(a>0.97)&(cv2.erode((a>0.97).astype(np.uint8),np.ones((5,5),np.uint8))>0)   # fully-opaque pixels keep their ORIGINAL colour (foreground estimator can drift them)
    rgb8=np.where(pure[...,None],c,rgb8)
    a=np.clip((a-0.18)/0.72,0,1);a[a<0.02]=0
    return np.dstack([rgb8,(a*255).astype(np.uint8)])
def fringe_report(rgba,name=""):
    """numeric QA: composite on black & measure brightness of edge pixels vs the interior just inside the edge"""
    a=rgba[...,3].astype(np.float32)/255;rgb=rgba[...,:3].astype(np.float32)
    m=(a>0.5).astype(np.uint8);inner=cv2.erode(m,np.ones((9,9),np.uint8))>0
    ring=(cv2.dilate(m,np.ones((5,5),np.uint8))>0)&(~(cv2.erode(m,np.ones((5,5),np.uint8))>0))
    lum=rgb.mean(2);ref=cv2.blur(np.where(inner,lum,0),(31,31))/(cv2.blur(inner.astype(np.float32),(31,31))+1e-6)
    ex=(lum-ref)[ring&(a>0.1)];bright=(ex>12).mean();p95=np.percentile(ex,95)
    return dict(name=name,edge_px=int(ring.sum()),frac_brighter_than_fabric=round(float(bright),3),p95_excess=round(float(p95),1))
if __name__=="__main__":
    import sys
    M='/home/claude/alphadog-styles/store/mk/'
    for kind,b,c,kw in [("tee","labrador_retriever","2LB",{}),("cap_dad","poodle","2DP",dict(wthr=60,sat=True))]:
        im=cv2.imread(f'{M}{kind}/{b}/{c}.jpg');t=time.time();r=matte(im,**kw);print(kind,b,c,time.time()-t,fringe_report(r,kind))
        cv2.imwrite(f'/tmp/kl/m3_{kind}.png',r)

def rs(rgba,size=None,fx=None,fy=None,interp=cv2.INTER_AREA):
    """resize RGBA with PREMULTIPLIED alpha so transparent-pixel colour never bleeds into edges"""
    a=rgba[...,3:].astype(np.float32)/255;pm=rgba[...,:3].astype(np.float32)*a
    kw=dict(dsize=size,fx=fx or 0,fy=fy or 0,interpolation=interp) if size else dict(dsize=None,fx=fx,fy=fy,interpolation=interp)
    pm2=cv2.resize(pm,**kw);a2=cv2.resize(a[...,0],**kw)
    rgb=np.where(a2[...,None]>1e-4,pm2/np.maximum(a2[...,None],1e-4),0)
    return np.dstack([np.clip(rgb,0,255),np.clip(a2*255,0,255)]).astype(np.uint8)
def fit(r,bw,bh):
    s=min(bw/r.shape[1],bh/r.shape[0]);return rs(r,(int(r.shape[1]*s),int(r.shape[0]*s)))
