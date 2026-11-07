import glob,cv2,numpy as np,sys
n=0
for p in glob.glob('/home/claude/alphadog-styles/out/merch_lib/wtank/*/*.webp'):
    im=cv2.imread(p,cv2.IMREAD_UNCHANGED)
    if im is None or im.shape[2]<4: continue
    h,w=im.shape[:2];rgb=im[...,:3];a=im[...,3]
    br=((rgb.min(2)>215)&((rgb.max(2).astype(int)-rgb.min(2))<14)&(a>20)).astype(np.uint8)
    nlab,l,st,cen=cv2.connectedComponentsWithStats(br)
    rm=np.zeros((h,w),np.uint8)
    for i in range(1,nlab):
        x,y,ww,hh,ar=st[i];cy=cen[i][1]
        if cy<0.24*h and ar>150 and ww<0.3*w: rm[l==i]=1
    if rm.any():
        rm=cv2.dilate(rm,np.ones((5,5),np.uint8));im[...,3]=np.where(rm>0,0,a);cv2.imwrite(p,im,[cv2.IMWRITE_WEBP_QUALITY,96]);n+=1
print('fixed',n)
