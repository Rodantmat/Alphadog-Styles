import cv2,numpy as np,io,cairosvg
from PIL import Image
AD='/home/claude/alphadog-styles/store/art/'
def alpha(breed,style='line_classic',view='front',h=1400,pad=0):
    png=cairosvg.svg2png(url=f'{AD}{style}/{breed}_{view}.svg',output_height=h*2)
    a=np.array(Image.open(io.BytesIO(png)).convert('RGBA'))[...,3]
    ys,xs=np.nonzero(a>40);a=a[ys.min():ys.max()+1,xs.min():xs.max()+1]
    s=h/a.shape[0];a=cv2.resize(a,(int(a.shape[1]*s),h),interpolation=cv2.INTER_AREA).astype(np.float32)/255
    return a
def arrival(a,seed_stagger=900,thr=0.2):
    """geodesic arrival times along the ink (like a pen drawing it); components start staggered top to bottom"""
    ink=(a>thr).astype(np.uint8);n,lab,st,_=cv2.connectedComponentsWithStats(ink,connectivity=8)
    arr=np.full(ink.shape,1e9,np.float32);reached=np.zeros_like(ink);pend=[];AH=a.shape[0]
    for k,c in enumerate(sorted(range(1,n),key=lambda c:-st[c,4])):
        ys,xs=np.nonzero(lab==c);i=np.argmin(ys);pend.append((0 if k==0 else int(60+(ys[i]/AH)*seed_stagger),xs[i],ys[i]))
    ker=np.ones((3,3),np.uint8);s=0;mx=max(d for d,_,_ in pend)
    while True:
        for d,x,y in pend:
            if d==s: reached[y,x]=1;arr[y,x]=s
        new=cv2.dilate(reached,ker)&ink&(1-reached);arr[new>0]=s;reached|=new;s+=1
        if s>mx and new.sum()==0: break
    return arr,s
