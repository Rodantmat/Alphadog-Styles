import sys,os,numpy as np,cv2
from rembg import remove,new_session
from PIL import Image
from pymatting import estimate_alpha_cf,estimate_foreground_ml
_s={}
def sess(m):
    if m not in _s: _s[m]=new_session(m)
    return _s[m]
def cutout(path,model="isnet-general-use",white_bg=None,caps=False):
    im=Image.open(path).convert("RGB"); a=np.asarray(im)
    m=np.asarray(remove(im,session=sess(model),only_mask=True)).astype(np.float32)/255
    h,w=m.shape
    border=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]])
    wb=(border.min(axis=1)>=250).mean()>=0.5 if white_bg is None else white_bg
    mh=m.copy(); forced=np.zeros(m.shape,bool)
    if wb:
        # pure-white regions the model says are background -> hard bg (arm/body gaps etc)
        near=(a.min(axis=2)>=(252 if caps else 234)).astype(np.uint8)
        n,lab,st,_=cv2.connectedComponentsWithStats(near,connectivity=4)
        edge=set(lab[0])|set(lab[-1])|set(lab[:,0])|set(lab[:,-1]); edge.discard(0)
        for c in range(1,n):
            if st[c,4]<60: continue
            reg=lab==c
            if c in edge or (caps and m[reg].mean()<0.5) or (not caps and st[c,4]>=150): mh[reg]=0; forced|=reg
    if wb:
        nonwhite=(a.min(axis=2)<(210 if caps else 238)).astype(np.float32)
        nonwhite[forced]=0
        # drop tiny specks of nonwhite
        n2,l2,s2,_=cv2.connectedComponentsWithStats(nonwhite.astype(np.uint8),connectivity=8)
        kp=np.zeros(n2,bool)
        if n2>1: kp[1:]=s2[1:,4]>=0.01*s2[1:,4].max()
        nonwhite=nonwhite*kp[l2]
        # white-on-white: keep nonwhite only if inside model blob dilated (avoid floor shadows), else keep as is for dark garments
        if caps: mh=np.maximum(mh,nonwhite)
        else:
            nonwhite=(~forced).astype(np.float32); nonwhite=cv2.morphologyEx(nonwhite,cv2.MORPH_OPEN,np.ones((3,3),np.uint8)); mh=nonwhite
    k=lambda r:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
    fg=cv2.erode((mh>0.95).astype(np.uint8),k(6))
    bg=cv2.erode((mh<0.05).astype(np.uint8),k(6))
    tri=np.full((h,w),0.5,np.float32); tri[fg>0]=1; tri[bg>0]=0
    img=a.astype(np.float64)/255
    if not (tri>=0.9).any() or not (tri<=0.1).any():
        if (tri>=0.9).any() or mh.mean()>0.5:
            return Image.fromarray(np.dstack([a,np.full((h,w),255,np.uint8)]),"RGBA")
        tri[mh>0.5]=1
    al=estimate_alpha_cf(img,tri.astype(np.float64))
    F=estimate_foreground_ml(img,al)
    al=np.clip(al,0,1)
    # tiny speck cleanup
    mm=(al>0.5).astype(np.uint8); n,l,stt,_=cv2.connectedComponentsWithStats(mm,connectivity=8)
    if n>1:
        keep=np.zeros(n,bool); keep[1:]=stt[1:,4]>=0.02*stt[1:,4].max(); al=al*keep[l]
    rgba=np.dstack([(np.clip(F,0,1)*255).astype(np.uint8),(al*255).astype(np.uint8)])
    return Image.fromarray(rgba,"RGBA")
if __name__=="__main__":
    model=sys.argv[1]
    for f in sys.argv[2:]:
        r=cutout(f,model); n="/tmp/cut/m_"+f.split('/')[-2]+"_"+os.path.basename(f)[:-4]
        bg=Image.new("RGB",r.size,(0,0,0));bg.paste(r,mask=r.split()[3]);bg.save(n+".jpg")

from scipy import ndimage as ndi
def cutout_flat(path,tol=21,sat_mode=False):
    """flat product on pure white: exact blend-with-white matting, no ML."""
    im=Image.open(path).convert("RGB"); a=np.asarray(im).astype(np.float32)
    h,w=a.shape[:2]
    border=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]]); bgc=np.median(border,axis=0)
    if sat_mode:
        mx=a.max(axis=2);mn=a.min(axis=2); sat=(mx-mn)/np.maximum(mx,1)
        near=((sat<0.09)&(mn>80)).astype(np.uint8)
    else: near=(np.abs(a-bgc).max(axis=2)<=tol).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(near,connectivity=4)
    edge=set(lab[0])|set(lab[-1])|set(lab[:,0])|set(lab[:,-1]); edge.discard(0)
    bg=np.zeros(n,bool)
    for c in range(1,n):
        if c in edge or (st[c,4]>=150 and not sat_mode): bg[c]=True
    bgm=bg[lab]
    fg=~bgm
    fg=cv2.morphologyEx(fg.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8)).astype(bool)
    core=cv2.erode(fg.astype(np.uint8),np.ones((9,9),np.uint8)).astype(bool)
    # nearest core colour for every pixel
    idx=ndi.distance_transform_edt(~core,return_distances=False,return_indices=True)
    F=a[idx[0],idx[1]]
    band=fg&~core
    d=bgc-F; num=bgc-a
    dm=d.mean(axis=2); alpha=np.where(dm>25,np.clip(num.mean(axis=2)/np.maximum(dm,1),0,1),1.0)
    al=np.where(core,1.0,np.where(band,alpha,0.0))
    # soften fringes: pixels in band keep own colour only partially -> use F colour for band (decontaminate)
    out=np.where(band[...,None],F,a)
    # remove specks
    mm=(al>0.5).astype(np.uint8); n2,l2,s2,_=cv2.connectedComponentsWithStats(mm,connectivity=8)
    if n2>1:
        k=np.zeros(n2,bool); k[1:]=s2[1:,4]>=0.02*s2[1:,4].max(); al=al*k[l2]
    return Image.fromarray(np.dstack([out.clip(0,255).astype(np.uint8),(al*255).astype(np.uint8)]),"RGBA")
