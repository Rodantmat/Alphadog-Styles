import numpy as np, cv2
from PIL import Image
def load(p,size=(1264,848)):
    g=np.array(Image.open(p).convert("L"))
    return g
def ink(g,th=128): return g<th
def split_x(mask):
    """x of the widest empty gap in the middle 30-70% (front|back boundary)"""
    cols=mask.sum(0); w=mask.shape[1]; lo,hi=int(w*.28),int(w*.72)
    best=None;run=0
    for i,v in enumerate(cols[lo:hi]):
        if v==0:
            run+=1
            if best is None or run>best[1]: best=(i-run+1,run)
        else: run=0
    return lo+best[0]+best[1]//2 if best and best[1]>=6 else w//2

def split_masks(mask):
    """component-based front/back split (k-means on component centres, like white_art.split). returns (front,back) bool masks"""
    n,lab,st,cen=cv2.connectedComponentsWithStats(mask.astype(np.uint8),8)
    ids=[i for i in range(1,n) if st[i,4]>=6]; W=mask.shape[1]
    xs=np.array([cen[i][0] for i in ids]); ar=np.array([st[i,4] for i in ids],float)
    c=np.array([W*.28,W*.74])
    for _ in range(40):
        asg=(np.abs(xs-c[1])<np.abs(xs-c[0])).astype(int)
        for k in(0,1):
            if (asg==k).any(): c[k]=np.average(xs[asg==k],weights=ar[asg==k])
    F=[i for i,a in zip(ids,asg) if a==0]; B=[i for i,a in zip(ids,asg) if a==1]
    mainF=max(F,key=lambda i:st[i,4]); mainB=max(B,key=lambda i:st[i,4])
    dF=cv2.distanceTransform((lab!=mainF).astype(np.uint8),cv2.DIST_L2,5); dB=cv2.distanceTransform((lab!=mainB).astype(np.uint8),cv2.DIST_L2,5)
    nf,nb=[mainF],[mainB]
    for i in ids:
        if i in(mainF,mainB): continue
        mk=lab==i
        (nf if dF[mk].min()<=dB[mk].min() else nb).append(i)
    return np.isin(lab,nf),np.isin(lab,nb)
