import cv2,numpy as np,glob,os,sys
def blockiness(a):
    m=(a>128).astype(np.uint8)
    e=m-cv2.erode(m,np.ones((3,3),np.uint8))
    sc=0
    for arr in (e,e.T):
        for row in arr[::2]:
            r=np.diff(np.concatenate([[0],row,[0]]))
            st=np.where(r==1)[0]; en=np.where(r==-1)[0]
            sc+=int(((en-st)>=9).sum())
    return sc/max(1,int(e.sum()))*1000
def smooth_contour(a,sig=4.0):
    af=a.astype(np.float32)/255.
    bl=cv2.GaussianBlur(af,(0,0),sig)
    new=np.clip((bl-0.42)/0.16,0,1)
    band=cv2.dilate(((a>20)&(a<235)).astype(np.uint8),np.ones((25,25),np.uint8))>0
    band|=cv2.dilate((a>128).astype(np.uint8)-cv2.erode((a>128).astype(np.uint8),np.ones((3,3),np.uint8)),np.ones((21,21),np.uint8))>0
    out=np.where(band,new,af)
    return (out*255).astype(np.uint8)
def fix(im, minthr=205, smooth=False):
    a=im[...,3].copy(); rgb=im[...,:3].astype(int)
    mn=rgb.min(2); mx=rgb.max(2); s=(mx-mn)/np.maximum(mx,1)
    op=a>128
    lum=rgb.mean(2)
    thr=max(minthr, np.percentile(lum[op],93)+14)
    w=((mn>=thr)&(s<0.16)&(a>0)).astype(np.uint8)
    trans=(a<40).astype(np.uint8)
    near=cv2.dilate(trans,np.ones((11,11),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(w,connectivity=8)
    kill=np.zeros_like(w)
    for i in range(1,n):
        if st[i,4]<20: continue
        m=lab==i
        if near[m].mean()>0.25: kill[m]=1
    # grow removal into the soft halo (near-white-ish edge pixels)
    soft=((mn>=thr-28)&(s<0.18)).astype(np.uint8)
    g=cv2.dilate(kill,np.ones((3,3),np.uint8),iterations=2)&soft
    kill=(kill|g).astype(np.uint8)
    a[kill>0]=0
    # drop small islands
    n,lab,st,_=cv2.connectedComponentsWithStats((a>40).astype(np.uint8),connectivity=8)
    if n>1:
        big=st[1:,4].max()
        for i in range(1,n):
            if st[i,4]<0.003*big: a[lab==i]=0
    if smooth: a=smooth_contour(a)
    # smooth stair-steps on the edge band only
    af=a.astype(np.float32)
    bl=cv2.GaussianBlur(af,(0,0),1.3)
    inner=cv2.erode((a>=250).astype(np.uint8),np.ones((5,5),np.uint8))>0
    out=np.where(inner,af,bl)
    out[a==0]=np.minimum(out[a==0],bl[a==0]*0.0+out[a==0])
    from scipy import ndimage as ndi
    core=(a>=200)
    idx=ndi.distance_transform_edt(~core,return_distances=False,return_indices=True)
    fill=im[...,:3][idx[0],idx[1]]
    im2=im.copy()
    need=(a<200)
    im2[...,:3][need]=fill[need]
    im2[...,3]=np.clip(out,0,255).astype(np.uint8)
    return im2,int(kill.sum())
if __name__=="__main__":
    src,dst=sys.argv[1],sys.argv[2]
    for p in sorted(glob.glob(src+'/*/*.png')):
        im=cv2.imread(p,-1); sm=any(k in p for k in ('Tee_B/102049','Tee_B/92584','Hoodie/102766'))
        if sm: print('smooth',round(blockiness(im[...,3]),1),p)
        o,k=fix(im,smooth=sm)
        q=p.replace(src,dst); os.makedirs(os.path.dirname(q),exist_ok=True); cv2.imwrite(q,o)
        if k>300: print(k,p)
