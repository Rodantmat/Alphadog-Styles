import cv2,numpy as np
def bez(p0,p1,p2,n=60):
    t=np.linspace(0,1,n)[:,None]; return (1-t)**2*np.array(p0)+2*(1-t)*t*np.array(p1)+t**2*np.array(p2)
def close_tail(path,out,x0,yu,yl,tipx,tipy):
    g=cv2.imread(path,0); K=4
    H,W=g.shape; big=cv2.resize(g,(W*K,H*K),interpolation=cv2.INTER_CUBIC)
    m=np.zeros_like(big)
    for (y0,sgn) in((yu,1),(yl,-1)):
        pts=bez((x0,y0),((x0+tipx)/2,y0+sgn*0.5),(tipx,tipy))
        for i in range(len(pts)-1):
            t=i/len(pts); w=max(1,int(round(K*(3.2*(1-t)+0.8*t))))
            a=tuple(int(v*K) for v in pts[i]); b=tuple(int(v*K) for v in pts[i+1])
            cv2.line(m,a,b,255,w,cv2.LINE_AA)
    big=np.minimum(big,255-m)
    o=cv2.resize(big,(W,H),interpolation=cv2.INTER_AREA)
    cv2.imwrite(out,o,[cv2.IMWRITE_JPEG_QUALITY,95]); return o
if __name__=="__main__":
    for th in("line_p1",):
        close_tail(f"out/sets/{th}/dachshund__heart.jpg","/tmp/dh_new.jpg",597,671.5,689.5,546,681)
