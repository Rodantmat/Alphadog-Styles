# Use the trimmed merch library (RGBA webp, tight bbox) in the engine. key = 'product/breed/code' (code may end _back)
import cv2,numpy as np
from v5lib import fit
LIB='/home/claude/alphadog-styles/out/merch_lib/'
def apparel_lib(key,box=(700,640)):
    im=cv2.imread(LIB+key+'.webp',cv2.IMREAD_UNCHANGED)
    ys,xs=np.where(im[...,3]>8);im=im[ys.min():ys.max()+1,xs.min():xs.max()+1]
    return fit(im,*box)
