# Trim every product mockup in store/mk to a transparent cutout -> out/merch_lib/<cat>/<breed>/<code>.webp  (resumable)
# usage: merch_lib.py [shard n_shards] [cat ...]
import sys,os,glob,json,cv2,numpy as np
from rembg import new_session,remove
R='/home/claude/alphadog-styles/';SRC=R+'store/mk/';OUT=R+'out/merch_lib/'
S=None
def sess():
    global S
    if S is None: S=new_session('u2netp')
    return S
def has_inset(im):
    if im.shape[0]!=1200 or im.shape[1]!=1200: return False
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
    ln=[g[665,690:1150],g[1174,690:1150],g[690:1150,665],g[690:1150,1174]]
    return all(203<x.mean()<216 and x.std()<4 for x in ln)
def rmask(im,contrast=True):
    d=np.abs(im.astype(np.float32)-255).sum(2)
    if contrast:
        a0=np.clip(cv2.GaussianBlur(d,(0,0),1.0)/55.,0,1)[...,None];im=(im*a0+np.array([70,40,30],np.float32)*(1-a0)).astype(np.uint8)
    a=np.array(remove(cv2.cvtColor(im,cv2.COLOR_BGR2RGB),session=sess(),only_mask=True)).astype(np.float32)/255
    return a
def mirror_fill(im):
    t=im.copy();t[640:1190,640:1190]=255;m=(rmask(t)>0.5).astype(np.uint8)
    ax=[]
    for y in range(400,630,5):
        xs=np.where(m[y]>0)[0]
        if len(xs)>80: ax.append((xs.min()+xs.max())/2)
    if not ax: return im
    ax=float(np.median(ax));out=im.copy()
    try:   # seam continuity: align the mirrored sleeve edge with the real sleeve edge at the inset's top border
        xr=np.mean([np.where(m[y]>0)[0].max() for y in range(624,637)]);xl=np.mean([np.where(m[y]>0)[0].min() for y in range(644,657)])
        a2=(xr+xl)/2
        if abs(a2-ax)<45: ax=float(a2)
    except Exception: pass
    ys,xs=np.mgrid[640:1190,640:1190];xm=np.round(2*ax-xs).astype(int);ok=(xm>=0)&(xm<640)
    w=np.clip((np.minimum(ys-640,xs-640)-2)/14.0,0,1)[...,None]
    src=im[ys.clip(0,1199),np.clip(xm,0,1199)].astype(np.float32);cur=im[ys,xs].astype(np.float32)
    mix=np.where(ok[...,None],cur*(1-w)+src*w,255.0);out[ys,xs]=mix.astype(np.uint8);return out
def largest(m):
    n,l,st,_=cv2.connectedComponentsWithStats(m);return (l==1+np.argmax(st[1:,4])).astype(np.uint8) if n>1 else m
def fillholes(m):
    inv=(1-m).astype(np.uint8);n,l,st,_=cv2.connectedComponentsWithStats(inv);return (l!=l[0,0]).astype(np.uint8)
def fringe(im,alpha_hard):
    """fraction of boundary-ring pixels that are near white while the garment is not (white halo)"""
    k=cv2.distanceTransform(alpha_hard,cv2.DIST_L2,3);ring=(k>0)&(k<=3);inner=k>12
    if inner.sum()<500 or ring.sum()<200: return 0.0,0
    mc=im.min(2).astype(np.float32);gmed=np.median(mc[inner])
    if gmed>110: return 0.0,gmed   # light garment: cannot separate by colour
    return float((mc[ring]>232).mean()),gmed
def cut(path):
    iscap='/cap_' in path
    im=cv2.imread(path)
    if im is None: return None
    inset=has_inset(im)
    if inset: im=mirror_fill(im)
    a=rmask(im);d=cv2.GaussianBlur(np.abs(im.astype(np.float32)-255).sum(2),(0,0),1.0)
    rem=(a>0.5).astype(np.uint8)
    # classical: white backdrop connected to the border
    cm=min(int(im[0,0].min()),int(im[0,-1].min()),int(im[-1,0].min()),int(im[-1,-1].min()))
    nb=(((255-im.min(2))<8)|((im.min(2)>226)&((im.max(2).astype(int)-im.min(2))<8)&(cm<250))).astype(np.uint8);n,l,st,_=cv2.connectedComponentsWithStats(nb)
    bgl={l[0,0],l[0,-1],l[-1,0],l[-1,-1]}-{0};bg=np.isin(l,list(bgl)).astype(np.uint8);C=(1-bg).astype(np.uint8)
    C=cv2.morphologyEx(C,cv2.MORPH_OPEN,np.ones((3,3),np.uint8));C=fillholes(largest(C))
    gm=np.median(im.min(2)[rem>0]) if rem.sum() else 255
    if gm<110 and rem.sum()>=0.6*C.sum():
        hard=((rem>0)&(d>45)).astype(np.uint8)
    elif rem.sum()>=0.6*C.sum():
        neutral=((im.max(2).astype(int)-im.min(2))<12)&(im.min(2)>150)
        shadow=(C>0)&(cv2.dilate(rem,np.ones((5,5),np.uint8))==0)&neutral
        hard=((C>0)&~shadow).astype(np.uint8)
    else: hard=C   # rembg lost a pale garment -> trust the white-background cut
    if iscap and gm<200:   # soft grey floor shadow is bright + neutral; white print lines are enclosed and get refilled
        nb2=((im.max(2).astype(int)-im.min(2))<14)&(im.min(2)>140)
        hard=fillholes(largest(((hard>0)&~nb2).astype(np.uint8)))
    if iscap and rem.sum()>=0.5*C.sum(): hard=(hard&cv2.dilate(rem,np.ones((13,13),np.uint8))).astype(np.uint8)
    if gm<200 and not iscap:   # dark garment: strip bright backdrop remnants that touch the outline (printed art is enclosed)
        br=((im.min(2)>max(120,gm+55))&(hard>0)).astype(np.uint8)
        out_d=cv2.distanceTransform(hard,cv2.DIST_L2,3);nbr=(out_d<=3)&(hard>0)
        n,l,_,_=cv2.connectedComponentsWithStats(br);seed=np.unique(l[(nbr)&(br>0)])
        bad=np.isin(l,seed[seed>0])|((br>0)&(out_d<=60));hard=((hard>0)&~cv2.dilate(bad.astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)).astype(np.uint8)
    hard=cv2.morphologyEx(hard,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8));hard=fillholes(largest(hard))
    if gm<200 and not iscap: hard=fillholes(largest((hard>0)&~(cv2.dilate(bg,np.ones((3,3),np.uint8))>0))).astype(np.uint8) if False else (((hard>0)&~(cv2.dilate(bg,np.ones((3,3),np.uint8))>0)).astype(np.uint8))
    # drop thin slivers (soft shadow edges): opening then geodesic regrow by 3 px
    op=cv2.morphologyEx(hard,cv2.MORPH_OPEN,np.ones((9,9),np.uint8));hard=(hard&cv2.dilate(largest(op),np.ones((7,7),np.uint8))).astype(np.uint8)
    hard=fillholes(largest(hard))
    er=1;tries=0
    while True:
        h2=cv2.erode(hard,np.ones((2*er+1,2*er+1),np.uint8));f,g=fringe(im,h2);tries+=1
        if f<0.012 or er>=5: break
        er+=1
    if gm<200 and not iscap:   # final pass AFTER hole filling: enclosed slivers of backdrop (armpit slits)
        dd=cv2.distanceTransform(h2,cv2.DIST_L2,3);brt=((im.min(2)>max(120,gm+38))&(dd>0)&(dd<=60)).astype(np.uint8)
        h2=(h2&~cv2.dilate(brt,np.ones((3,3),np.uint8))).astype(np.uint8)
    if inset:   # smooth the seam where the mirrored sleeve meets the real one
        h2=(cv2.GaussianBlur(h2.astype(np.float32),(0,0),5)>0.5).astype(np.uint8)
    al=cv2.GaussianBlur(h2.astype(np.float32),(0,0),1.0);al=np.clip((al-0.3)/0.5,0,1)
    col=im.astype(np.float32);aa=np.maximum(al[...,None],0.4);edge=((al>0)&(al<0.98))[...,None]
    dec=np.clip((col-(1-aa)*255)/aa,0,255);col=np.where(edge,dec,col)
    ys,xs=np.where(al>0.04);y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    out=np.dstack([col.astype(np.uint8),(al*255).astype(np.uint8)])[y0:y1+1,x0:x1+1]
    return out,dict(inset=bool(inset),erode=er,fringe=round(f,4),gmed=float(g))
def save(out,p):
    os.makedirs(os.path.dirname(p),exist_ok=True)
    # lossless-quality webp with alpha (RGBA); keep colours exact under alpha
    cv2.imwrite(p,out,[cv2.IMWRITE_WEBP_QUALITY,96])
if __name__=='__main__':
    args=sys.argv[1:];shard,ns=0,1
    if len(args)>=2 and args[0].isdigit() and args[1].isdigit(): shard,ns=int(args[0]),int(args[1]);args=args[2:]
    cats=args or ['tee','hoodie','tank','wtank','polo','cap_dad','cap_foam','cap_mesh']
    files=[]
    for c in cats: files+=sorted(glob.glob(f'{SRC}{c}/*/*.jpg')+glob.glob(f'{SRC}{c}/*/*.webp')+glob.glob(f'{SRC}{c}/*/*.png'))
    files=files[shard::ns];log=open(OUT+f'log_{shard}.jsonl','a');n=0
    for f in files:
        rel=os.path.relpath(f,SRC);o=OUT+os.path.splitext(rel)[0]+'.webp'
        if os.path.exists(o): continue
        try:
            r=cut(f)
            if r is None: continue
            out,meta=r;save(out,o);meta['f']=rel;log.write(json.dumps(meta)+'\n');log.flush();n+=1
        except Exception as e: log.write(json.dumps({'f':rel,'err':repr(e)[:120]})+'\n');log.flush()
    print('done',shard,n)
