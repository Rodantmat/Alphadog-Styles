import cv2,numpy as np,cut3
def ref_mask(im):
    d=np.abs(im.astype(np.float32)-255).sum(2);m=(cv2.GaussianBlur(d,(0,0),1)>45).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    n,l,st,_=cv2.connectedComponentsWithStats(m);m=(l==1+np.argmax(st[1:,4])).astype(np.uint8)
    from scipy.ndimage import binary_fill_holes
    return binary_fill_holes(m).astype(np.uint8)
def qa(im,r_full,name='',bottom_exempt=0.0,colour_tol=400):
    """r_full: RGBA same size as im (canvas-aligned). returns dict + pass flag"""
    ref=ref_mask(im);a=r_full[...,3]
    refc=cv2.erode(ref,np.ones((9,9),np.uint8))
    # exclude pale/grey backdrop-shadow pockets (they are SUPPOSED to be removed) from what counts as garment
    rf0=im.astype(np.float32);ch0=rf0.max(2)-rf0.min(2);dp0=np.abs(rf0-255).sum(2)
    cr=(cv2.erode(ref,np.ones((15,15),np.uint8))>0)&(rf0.mean(2)>90);chm0=np.median(ch0[cr]) if cr.sum() else 0;dm0=np.median(dp0[cr]) if cr.sum() else 0
    rawpale=(((cv2.GaussianBlur(dp0,(0,0),1.2)<0.72*dm0)&(dm0>45))|((cv2.GaussianBlur(ch0,(0,0),1.2)<0.45*chm0)&(chm0>=12)&(cv2.GaussianBlur(rf0.mean(2),(0,0),1.2)>150))).astype(np.uint8)
    rawpale=cv2.dilate(rawpale,np.ones((5,5),np.uint8));refc=refc*(1-rawpale)
    if bottom_exempt>0:   # cap brim shadow strip is removed on purpose
        ys=np.nonzero(ref.any(1))[0];refc[int(ys.max()-bottom_exempt*(ys.max()-ys.min())):]=0
    cov=((a>230)&(refc>0)).sum()/max(refc.sum(),1)
    # lost pieces: reference-core pixels that are transparent, as connected blobs
    lost=((a<128)&(refc>0)).astype(np.uint8);lost=cv2.morphologyEx(lost,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    lost_px=int(lost.sum())
    # enclosed holes in alpha silhouette
    from scipy.ndimage import binary_fill_holes
    sil=(a>128);hl=(binary_fill_holes(sil)&~sil);holes=int((hl&(np.abs(im.astype(np.float32)-255).sum(2)>60)).sum())   # only holes that were real garment pixels
    # print / colour fidelity inside solid area: composite vs original
    solid=cv2.erode((a>250).astype(np.uint8),np.ones((9,9),np.uint8))>0
    diff=np.abs(r_full[...,:3].astype(np.int16)-im.astype(np.int16)).max(2)
    bad=((diff>40)&solid).sum()
    dark=(im.astype(np.float32).mean(2)<90)&(refc>0);dark_keep=((a>230)&dark).sum()/max(dark.sum(),1) if dark.sum() else 1
    # pale blobs that are lighter than the garment (shadow / backdrop leftovers between arm and body etc.)
    core=(a>250)&(cv2.erode((a>250).astype(np.uint8),np.ones((15,15),np.uint8))>0)
    lum=r_full[...,:3].astype(np.float32).mean(2);lumb=cv2.GaussianBlur(lum,(0,0),2)
    if core.sum()>500:
        med=np.median(lumb[core]);dpix=np.abs(r_full[...,:3].astype(np.float32)-255).sum(2);dmed=np.median(dpix[core]);rf=r_full[...,:3].astype(np.float32);chn=rf.max(2)-rf.min(2);chm=np.median(chn[core])
        pale=(((cv2.GaussianBlur(dpix,(0,0),1.5)<0.72*dmed)&(dmed>45))|((cv2.GaussianBlur(chn,(0,0),1.5)<0.45*chm)&(chm>=12)&(cv2.GaussianBlur(rf.mean(2),(0,0),1.5)>150)))&(a>20);pale=pale.astype(np.uint8);pale=cv2.morphologyEx(pale,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
        pale_px=int(pale.sum())
    else: pale_px=0
    fr=cut3.fringe_report(r_full,name)
    dd=np.abs(im.astype(np.float32)-255).sum(2);over=int(((a>200)&(dd<8)).sum())   # alpha far outside the garment
    ok=cov>0.985 and lost_px<150 and holes<1500 and bad<colour_tol and dark_keep>0.985 and fr['frac_brighter_than_fabric']<0.20 and fr['p95_excess']<30 and over<12 and pale_px<40
    return dict(name=name,cov=round(float(cov),4),lost=lost_px,holes=holes,colour_bad=int(bad),dark_keep=round(float(dark_keep),4),fringe=fr['frac_brighter_than_fabric'],p95=fr['p95_excess'],outside=over,pale=pale_px,PASS=bool(ok))
def full(im,fn,**kw):
    """run matte fn on full image and return canvas-aligned RGBA (matte returns crop with pad -> realign via bbox search)"""
    return fn(im,**kw)

def canvas(r):
    x0,y0,W,H=cut3.LAST;out=np.zeros((H,W,4),np.uint8);out[y0:y0+r.shape[0],x0:x0+r.shape[1]]=r;return out
