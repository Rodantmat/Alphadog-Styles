import cv2,numpy as np,glob,os,sys
def whites(rgba,minv=214,sat=0.10):
    a=rgba[...,3]; rgb=rgba[...,:3].astype(int)
    mn=rgb.min(2); mx=rgb.max(2)
    s=(mx-mn)/np.maximum(mx,1)
    w=((mn>=minv)&(s<sat)&(a>40)).astype(np.uint8)
    return w,a
def audit(p):
    im=cv2.imread(p,cv2.IMREAD_UNCHANGED)
    w,a=whites(im)
    trans=(a<40).astype(np.uint8)
    near=cv2.dilate(trans,np.ones((7,7),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(w,connectivity=8)
    tot=0;bad=0
    for i in range(1,n):
        m=lab==i
        if st[i,4]>=40 and (near[m].mean()>0.15): bad+=st[i,4]
    return bad,(a>40).sum()
if __name__=="__main__":
    rows=[]
    for p in sorted(glob.glob(sys.argv[1]+'/*/*.png')):
        b,t=audit(p); rows.append((b/t*1000,b,p))
    for r in sorted(rows,reverse=True)[:40]: print(f"{r[0]:6.1f} {r[1]:7d} {r[2]}")
