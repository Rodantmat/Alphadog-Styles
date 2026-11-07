# Independent QA v2 for the trimmed merch library. Re-aligns each cutout to its SOURCE mockup and measures:
#  lost  = real garment/print pixels in the source that the cutout dropped (cut-through / lost pieces)
#  halo  = bright/dark fringe pixels at the edge versus the garment colour just inside (white leftover on black)
#  sym   = left-right symmetry of the silhouette (bites / leftovers) , rough = jagged outline, soft = see-through interior
# usage: qa2.py [limit]  -> out/merch_lib/qa2.json
import os,sys,glob,json,cv2,numpy as np
from multiprocessing import Pool
R='/home/claude/alphadog-styles/';LIB=R+'out/merch_lib/';SRC=R+'store/mk/'
def has_inset(im):
    if im.shape[0]!=1200 or im.shape[1]!=1200: return False
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
    ln=[g[665,690:1150],g[1174,690:1150],g[690:1150,665],g[690:1150,1174]]
    return all(203<x.mean()<216 and x.std()<4 for x in ln)
def ref_image(rel):
    back=rel.endswith('_back.webp');base=rel[:-10] if back else rel[:-5]
    for e in ('.jpg','.webp','.png'):
        p=SRC+base+e
        if os.path.exists(p): break
    else: return None,None
    im=cv2.imread(p)
    if im is None: return None,None
    ins=has_inset(im)
    if back:
        if not ins: return None,None
        c=im[660:1166,660:1172].copy();sp=(c.max(2).astype(int)-c.min(2));nbm=((c.min(2)>=244)&(sp<8)).astype(np.uint8);nl,lab,_,_=cv2.connectedComponentsWithStats(nbm)
        bl=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0};bgm=np.isin(lab,list(bl)).astype(np.uint8)
        grow=(cv2.dilate(bgm,np.ones((13,13),np.uint8))>0)&(c.min(2)>236)&(sp<10);c[(bgm>0)|grow]=255;c=cv2.resize(c,(1064,1056),interpolation=cv2.INTER_CUBIC)
        cv_=np.full((1200,1200,3),255,np.uint8);cv_[72:1128,68:1132]=c;return cv_,None
    return im,(640 if ins else None)
def align(ref,rgb,a):
    h,w=a.shape;s=0.25
    r=cv2.resize(ref,None,fx=s,fy=s,interpolation=cv2.INTER_AREA);t=cv2.resize(rgb,None,fx=s,fy=s,interpolation=cv2.INTER_AREA);m=cv2.resize((a>200).astype(np.uint8)*255,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST)
    if t.shape[0]>=r.shape[0] or t.shape[1]>=r.shape[1]: return None
    res=cv2.matchTemplate(r,t,cv2.TM_SQDIFF,mask=cv2.merge([m,m,m]));_,_,mn,_=cv2.minMaxLoc(res);x0,y0=int(mn[0]/s),int(mn[1]/s)
    best=None
    for dy in range(-5,6):
        for dx in range(-5,6):
            y,x=y0+dy,x0+dx
            if y<0 or x<0 or y+h>ref.shape[0] or x+w>ref.shape[1]: continue
            sub=ref[y:y+h:3,x:x+w:3].astype(np.int16);d=(np.abs(sub-rgb[::3,::3].astype(np.int16)).sum(2)*(a[::3,::3]>250)).sum()
            if best is None or d<best[0]: best=(d,x,y)
    return best[1:] if best else None
def field(rgb,inner):
    f=inner.astype(np.float32);num=cv2.GaussianBlur(rgb.astype(np.float32)*f[...,None],(0,0),7);den=cv2.GaussianBlur(f,(0,0),7)[...,None]+1e-3;return num/den
def analyze(rel):
    out={}
    im=cv2.imread(LIB+rel,cv2.IMREAD_UNCHANGED)
    if im is None or im.ndim<3 or im.shape[2]<4: return rel,{'flags':['noalpha']}
    rgb=im[...,:3];a=im[...,3];hard=(a>127).astype(np.uint8);h,w=a.shape;area=int(hard.sum())
    if area<8000: return rel,{'flags':['tiny']}
    flags=[]
    dist=cv2.distanceTransform(hard,cv2.DIST_L2,3)
    inner=(dist>5)&(dist<16)
    gm=float(np.median(rgb.min(2)[dist>15])) if (dist>15).sum()>200 else 255.
    out['gmed']=round(gm,1)
    # --- halo / edge colour vs garment colour inside
    ring=((cv2.distanceTransform((a>3).astype(np.uint8),cv2.DIST_L2,3)>0)|(a>3))&(dist<=3.5)
    ring=ring&(a>8)
    if inner.sum()>500 and ring.sum()>100:
        F=field(rgb,inner);lum=lambda x:x.astype(np.float32)@np.array([0.114,0.587,0.299],np.float32)
        dl=lum(rgb)-lum(F);wt=(a[ring]/255.)
        bright=float((((dl[ring]>55)*wt).sum())/wt.sum());dark=float((((dl[ring]<-70)*wt).sum())/wt.sum())
        out['bright']=round(bright,4);out['dark']=round(dark,4)
        if bright>0.06 and gm<225: flags.append('halo_bright')
        if dark>0.15 and gm>120: flags.append('halo_dark')
    # --- shape
    cs,_=cv2.findContours(hard,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=cv2.contourArea);per=cv2.arcLength(c,True);hull=cv2.convexHull(c);sol=cv2.contourArea(c)/max(1,cv2.contourArea(hull));out['solidity']=round(sol,4)
    sm=cv2.GaussianBlur(hard.astype(np.float32),(0,0),12);sc,_=cv2.findContours((sm>0.5).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    out['rough']=round(per/max(1,cv2.arcLength(max(sc,key=cv2.contourArea),True)),4) if sc else 1
    n,l,st,_=cv2.connectedComponentsWithStats(hard);out['comps']=int((st[1:,4]>0.002*area).sum())
    if out['comps']>1: flags.append('fragments')
    xs=np.where(hard.any(0))[0];ax=(xs.min()+xs.max())/2;fl=hard[:,::-1];sh=int(round(2*(w/2-ax)));M=np.float32([[1,0,sh],[0,1,0]]);fl=cv2.warpAffine(fl,M,(w,h),flags=cv2.INTER_NEAREST)
    out['sym']=round(float((hard&fl).sum())/max(1,float((hard|fl).sum())),4)
    # interior see-through
    er=cv2.erode(hard,np.ones((15,15),np.uint8));out['soft']=round(float(((a<240)&(er>0)).sum())/max(1,er.sum()),4)
    if out['soft']>0.01: flags.append('seethrough')
    # --- lost pieces vs source
    ref,skip=ref_image(rel)
    if ref is not None:
        pos=align(ref,rgb,a)
        if pos is None: out['align']='fail'
        else:
            x,y=pos;H,W=ref.shape[:2];mask=np.zeros((H,W),np.uint8);mask[y:y+h,x:x+w]=hard
            if skip: mask2=mask.copy()
            sp=ref.max(2).astype(int)-ref.min(2);isw=gm>=225;iscap=rel.startswith('cap_')
            content=((ref.min(2)<165)|(sp>55)) if not isw else ((ref.min(2)<120)|(sp>70))
            if iscap: content=(ref.min(2)<60)|(sp>70)
            valid=np.ones((H,W),bool)
            if skip: valid[skip:,skip:]=False
            near=cv2.dilate(mask,np.ones((7,7),np.uint8))>0
            res=(content&~near&valid).astype(np.uint8)
            res=cv2.morphologyEx(res,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
            # restrict to the neighbourhood of the garment (shadows/props far away are not garment)
            res&=(cv2.dilate(mask,np.ones((61,61),np.uint8))>0).astype(np.uint8)
            n2,l2,st2,_=cv2.connectedComponentsWithStats(res);big=st2[1:,4].max() if n2>1 else 0
            out['lost']=round(float(res.sum())/area,4);out['lostmax']=int(big)
            if big>(2500 if iscap else 600) or res.sum()/area>(0.03 if iscap else 0.012): flags.append('lost_piece')
    out['flags']=flags
    return rel,out
if __name__=='__main__':
    lim=int(sys.argv[1]) if len(sys.argv)>1 else 0
    files=[os.path.relpath(p,LIB) for p in sorted(glob.glob(LIB+'*/*/*.webp'))]
    if lim:
        import random;random.seed(3);files=random.sample(files,lim)
    with Pool(2) as P: res=dict(P.imap_unordered(analyze,files,chunksize=8))
    # robust per-product outliers for shape metrics
    import collections
    g=collections.defaultdict(list)
    for k,v in res.items():
        if 'sym' in v: g[(k.split('/')[0],k.endswith('_back.webp'))].append(k)
    for key,ks in g.items():
        for m,sgn,mn in (('sym',-1,0.07),('solidity',-1,0.03),('rough',1,0.04)):
            vals=np.array([res[k][m] for k in ks]);med=np.median(vals);mad=np.median(np.abs(vals-med))*1.4826+1e-4
            for k in ks:
                z=sgn*(res[k][m]-med)/mad
                if z>5 and abs(res[k][m]-med)>mn: res[k]['flags'].append('out_'+m)
    json.dump(res,open(LIB+('qa2_sample.json' if lim else 'qa2.json'),'w'))
    fc=collections.Counter(f for v in res.values() for f in v['flags']);print(len(res),'checked',sum(1 for v in res.values() if v['flags']),'flagged',dict(fc))
