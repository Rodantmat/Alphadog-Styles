# Restore garment pixels the cutter dropped (found by qa2 'lost_piece'): add source content next to the mask back into the cutout.
import sys,json,cv2,numpy as np
sys.path.insert(0,'/home/claude/alphadog-styles/scripts/video')
import qa2
from merch_lib import largest,fillholes
def repair(rel):
    im=cv2.imread(qa2.LIB+rel,cv2.IMREAD_UNCHANGED);rgb=im[...,:3];a=im[...,3];h,w=a.shape;hard=(a>127).astype(np.uint8)
    ref,skip=qa2.ref_image(rel);x,y=qa2.align(ref,rgb,a);H,W=ref.shape[:2]
    mask=np.zeros((H,W),np.uint8);mask[y:y+h,x:x+w]=hard
    # garment = source pixels clearly darker/more saturated than the white backdrop shadows, within reach of the mask
    sp=ref.max(2).astype(int)-ref.min(2);content=((ref.min(2)<165)|(sp>55)).astype(np.uint8)
    reach=cv2.dilate(mask,np.ones((121,121),np.uint8))
    cand=((content>0)&(reach>0)).astype(np.uint8)|mask
    cand=cv2.morphologyEx(cand,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8));cand=fillholes(largest(cand))
    cand=cv2.morphologyEx(cand,cv2.MORPH_OPEN,np.ones((7,7),np.uint8));cand=fillholes(largest(cand|mask))
    new=cv2.erode(cand,np.ones((3,3),np.uint8))|mask   # keep old edge, pull new edge in 1px
    new=(cv2.GaussianBlur(new.astype(np.float32),(0,0),3)>0.5).astype(np.uint8)|mask
    al=cv2.GaussianBlur(new.astype(np.float32),(0,0),1.0);al=np.clip((al-0.3)/0.5,0,1)
    ys,xs=np.where(al>0.04);y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    col=ref.copy();oy,ox=y,x;col[oy:oy+h,ox:ox+w]=np.where((a>127)[...,None],rgb,col[oy:oy+h,ox:ox+w])
    out=np.dstack([col,(al*255).astype(np.uint8)])[y0:y1+1,x0:x1+1]
    cv2.imwrite(qa2.LIB+rel,out,[cv2.IMWRITE_WEBP_QUALITY,96]);return rel,int(new.sum()-mask.sum())
if __name__=='__main__':
    r=json.load(open(qa2.LIB+'qa2.json'));fl=[k for k,v in r.items() if 'lost_piece' in v['flags']]
    for k in fl:
        if k.endswith('_back.webp'): print(k,'skip back (handled separately)');continue
        print(repair(k))
