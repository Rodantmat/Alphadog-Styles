import cv2,numpy as np,cut3
from rembg import new_session,remove
_S=None
def rmask(im,contrast=False):
    global _S
    if _S is None: _S=new_session('isnet-general-use')
    if contrast:   # replace the white backdrop by a dark one so pale garments get contrast for the model
        d=np.abs(im.astype(np.float32)-255).sum(2);a=np.clip(cv2.GaussianBlur(d,(0,0),1.0)/55.,0,1)[...,None]
        im=(im*a+np.array([70,40,30],np.float32)*(1-a)).astype(np.uint8)
    rgb=cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
    a=remove(rgb,session=_S,only_mask=True)
    m=(np.array(a)>127).astype(np.uint8)
    n,l,st,_=cv2.connectedComponentsWithStats(m);m=(l==1+np.argmax(st[1:,4])).astype(np.uint8)
    return m
def matte(im,wthr=14,sat=False,**kw):
    orig=cut3.hard_mask
    def hm(i,w=14):
        base=orig(i,w);rm=rmask(i)
        # model silhouette limited to pixels that differ from white (drops soft shadow), fill with base interior
        d=np.abs(i.astype(np.float32)-255).sum(2)
        m=((rm>0)&(cv2.GaussianBlur(d,(0,0),1.0)>w)).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,l,st,_=cv2.connectedComponentsWithStats(m);m=(l==1+np.argmax(st[1:,4])).astype(np.uint8)
        return m
    cut3.hard_mask=hm
    try: return cut3.matte(im,wthr=wthr,sat=sat,**kw)
    finally: cut3.hard_mask=orig

def cap(im,**kw):
    r=matte(im,wthr=60,sat=True,**kw);rgb=r[...,:3];a=r[...,3].copy()
    hsv=cv2.cvtColor(rgb,cv2.COLOR_BGR2HSV);S=hsv[...,1].astype(np.float32)
    core=(a>250)&(hsv[...,2]>150);ms=np.median(S[core]) if core.sum() else 0
    # grey shadow = low saturation AND darker than fabric (not the black print: print is enclosed)
    sh=((S<ms*0.45)&(hsv[...,2]<215)).astype(np.uint8)
    sh=cv2.morphologyEx(sh,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,l,st,_=cv2.connectedComponentsWithStats(sh)
    h=a.shape[0];out=np.zeros_like(sh)
    for i in range(1,n):
        x,y,w,hh,ar=st[i]
        if ar>400 and y+hh>h*0.8: out[l==i]=1   # touches bottom edge region -> shadow strip
    out=cv2.dilate(out,np.ones((5,5),np.uint8))
    a[out>0]=0
    m=(a>0).astype(np.uint8);n,l,st,_=cv2.connectedComponentsWithStats(m);m=(l==1+np.argmax(st[1:,4]))
    a=np.where(m,a,0);a=cv2.GaussianBlur(a,(0,0),0.8)
    ys=np.nonzero((a>128).any(1))[0];yb=int(ys.max()-0.18*(ys.max()-ys.min()))
    er=cv2.erode(a,np.ones((3,3),np.uint8),iterations=2);a2=a.copy();a2[yb:]=er[yb:];a=cv2.GaussianBlur(a2,(0,0),0.8)   # tidy brim underside edge
    r=r.copy();r[...,3]=a;return r

import qa
def peel(r):
    """remove backdrop/shadow slivers: pixels much closer to white than the fabric, near the silhouette edge"""
    a=r[...,3].astype(np.float32)/255;core=cv2.erode((a>0.99).astype(np.uint8),np.ones((15,15),np.uint8))>0
    if core.sum()<500: return r
    dp=np.abs(r[...,:3].astype(np.float32)-255).sum(2);dmed=np.median(dp[core])
    rgbf=r[...,:3].astype(np.float32);ch=rgbf.max(2)-rgbf.min(2);chm=np.median(ch[core])
    gray=(cv2.GaussianBlur(ch,(0,0),1.2)<0.45*chm)&(a>0.02)&(chm>=12)&(cv2.GaussianBlur(rgbf.mean(2),(0,0),1.2)>150)     # neutral-grey shadow on a coloured garment
    if dmed<45 and chm<12: return r
    pale=((cv2.GaussianBlur(dp,(0,0),1.2)<0.72*dmed)&(dmed>=45)|gray)&(a>0.02)
    dist=cv2.distanceTransform((a>0.5).astype(np.uint8),cv2.DIST_L2,5)
    pale&=(dist<40)
    pale=cv2.morphologyEx(pale.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,l,st,_=cv2.connectedComponentsWithStats(pale)
    kill=np.zeros_like(pale)
    for i in range(1,n):
        if st[i,4]>=12: kill[l==i]=1
    kill=cv2.dilate(kill,np.ones((3,3),np.uint8))
    a2=a.copy();a2[kill>0]=0
    m=(a2>0.02).astype(np.uint8);n,l,st,_=cv2.connectedComponentsWithStats(m);m=(l==1+np.argmax(st[1:,4]))
    a2=np.where(m,a2,0);a2=cv2.GaussianBlur(a2,(0,0),0.7)*(a2>0).astype(np.float32)*0+cv2.GaussianBlur(a2,(0,0),0.7)
    out=r.copy();out[...,3]=np.clip(a2*255,0,255).astype(np.uint8);return out
def safe_matte(im,name='',cap=False,verbose=True):
    """try masks in order, accept first that passes the QA analyzer; raise if none does"""
    orig=cut3.hard_mask
    def mk_hm(kind):
        def hm(i,w=14):
            if kind=='orig': return orig(i,w)
            if kind.startswith('flood'):
                d0=np.abs(i.astype(np.float32)-255).sum(2)
                t=float(np.clip(0.55*np.median(d0[d0>40]),24,70)) if kind=='floodauto' else float(kind[5:])
                d=cv2.GaussianBlur(np.abs(i.astype(np.float32)-255).sum(2),(0,0),0.8)
                bgc=(d<t).astype(np.uint8);n,l,st,_=cv2.connectedComponentsWithStats(bgc,connectivity=4)
                border=set(np.unique(np.concatenate([l[0],l[-1],l[:,0],l[:,-1]])))-{0}
                big=set(i for i in range(1,n) if st[i,4]>150)   # enclosed backdrop pockets (between arm and body) count as background too
                bg=np.isin(l,list(border|big));m=(~bg).astype(np.uint8)
                m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
                n,l,st,_=cv2.connectedComponentsWithStats(m);return (l==1+np.argmax(st[1:,4])).astype(np.uint8)
            rm=rmask(i,contrast=(kind=='rembgc'));d=np.abs(i.astype(np.float32)-255).sum(2)
            if kind in('rembg','rembgc'): m=((rm>0)&(cv2.GaussianBlur(d,(0,0),1.0)>w)).astype(np.uint8)
            else:  # rembg union reference-core (fills what the model dropped), edges from reference
                ref=qa.ref_mask(i);m=(((rm>0)&(cv2.GaussianBlur(d,(0,0),1.0)>w))|(ref>0)).astype(np.uint8)
            m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
            n,l,st,_=cv2.connectedComponentsWithStats(m);return (l==1+np.argmax(st[1:,4])).astype(np.uint8)
        return hm
    last=None
    for kind in ('rembg','floodauto','flood24','flood34','flood50','flood70','flood16','union','orig'):
        cut3.hard_mask=mk_hm(kind)
        try:
            kw=dict(wthr=60,sat=True) if cap else {}
            r=cut3.matte(im,**kw)
        finally: cut3.hard_mask=orig
        r=peel(r);rc=qa.canvas(r);res=qa.qa(im,rc,name)
        if verbose: print(kind,res)
        if res['PASS']: return r
        last=res
    raise RuntimeError(f'matte QA failed for {name}: {last}')
