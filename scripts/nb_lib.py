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
