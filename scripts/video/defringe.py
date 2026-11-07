# Scrub bright (white leftover) / dark rims on the outer 3px of every cutout: edge colour -> garment colour just inside. usage: defringe.py [files...]
import sys,glob,os,cv2,numpy as np
from multiprocessing import Pool
LIB='/home/claude/alphadog-styles/out/merch_lib/'
W=np.array([0.114,0.587,0.299],np.float32)
def fix(p):
    im=cv2.imread(p,cv2.IMREAD_UNCHANGED)
    if im is None or im.shape[2]<4: return p,0
    rgb=im[...,:3].astype(np.float32);a=im[...,3];hard=(a>127).astype(np.uint8)
    dist=cv2.distanceTransform(hard,cv2.DIST_L2,3)
    inner=((dist>5)&(dist<16)).astype(np.float32)
    if inner.sum()<500: return p,0
    gm=float(np.median(im[...,:3].min(2)[dist>15])) if (dist>15).sum()>200 else 255.
    if gm>=225: return p,0
    # exclude print pixels from the garment colour: use median-like robust field via blur of inner pixels close to the local mode
    num=cv2.GaussianBlur(rgb*inner[...,None],(0,0),7);den=cv2.GaussianBlur(inner,(0,0),7)[...,None]+1e-3;F=num/den
    ring=((a>3)&((dist<=3.5)|(hard==0)))
    dl=rgb@W-F@W
    bad=ring&((dl>22)|(dl<-60))
    n=int(bad.sum())
    if n==0: return p,0
    rgb[bad]=F[bad];im[...,:3]=np.clip(rgb,0,255).astype(np.uint8)
    cv2.imwrite(p,im,[cv2.IMWRITE_WEBP_QUALITY,96]);return p,n
if __name__=='__main__':
    files=sys.argv[1:] or sorted(glob.glob(LIB+'*/*/*.webp'))
    with Pool(2) as P: r=list(P.imap_unordered(fix,files,chunksize=16))
    print(len(r),'files',sum(1 for _,n in r if n),'changed')
