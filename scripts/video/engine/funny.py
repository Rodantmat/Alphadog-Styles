import sys,math,random
from v5lib import *
FG='/home/claude/alphadog-styles/out/footage/'
CTA_TXT=sys.argv[2] if len(sys.argv)>2 else "alphadogstyles.com  ·  link in bio"
def sm(x): x=min(max(x,0),1);return x*x*(3-2*x)
def bounce(t): # 0..1 pop with overshoot
    if t<=0: return 0.0
    if t>=1: return 1.0
    return 1+1.7*math.pow(t-1,3)+0.7*math.pow(t-1,2)
# ---------- paw-print backdrop (new, brand-fit) ----------
def paws(seed=5,c1=(40,178,246),c2=(24,120,226),ink=(18,92,205)):
    rs=np.random.RandomState(seed);yy=np.linspace(0,1,H)[:,None,None]
    base=np.array(c1,np.float32)*(1-yy)+np.array(c2,np.float32)*yy;base=np.repeat(base,W,1)
    lay=np.zeros((H,W),np.float32)
    def paw(cx,cy,s,a):
        m=np.zeros((H,W),np.uint8)
        R=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
        def el(dx,dy,ax,ay,ang=0):
            p=R@np.array([dx,dy])*s;cv2.ellipse(m,(int(cx+p[0]),int(cy+p[1])),(int(ax*s),int(ay*s)),math.degrees(a)+ang,0,360,255,-1)
        el(0,12,34,28);
        for dx,dy,ang in((-38,-16,-20),(-14,-40,-6),(14,-40,6),(38,-16,20)): el(dx,dy,13,18,ang)
        return m.astype(np.float32)/255
    for r in range(-1,13):
        for c in range(-1,7):
            x=c*190+(95 if r%2 else 0)+rs.randint(-14,14);y=r*170+rs.randint(-14,14)
            lay=np.maximum(lay,paw(x,y,0.95,rs.uniform(-0.6,0.6))*1.0)
    lay=cv2.GaussianBlur(lay,(0,0),1.1)
    img=base*(1-0.30*lay[...,None])+np.array(ink,np.float32)*0.30*lay[...,None]
    n=cv2.GaussianBlur(rs.randn(H,W).astype(np.float32),(0,0),1.1)*5;img+=n[...,None]
    n2=cv2.resize(cv2.GaussianBlur(rs.randn(H//8,W//8).astype(np.float32),(0,0),5),(W,H))*26;img+=n2[...,None]
    vig=1-0.30*(((np.mgrid[0:W][None,:]-W/2)/(W*0.75))**2+((np.mgrid[0:H][:,None]-H*0.5)/(H*0.75))**2)
    return np.clip(img*vig[...,None],0,255)
# ---------- clip window ----------
WW,WH=960,800
RR=44
def rmask(w,h,r):
    m=np.zeros((h,w),np.uint8);cv2.rectangle(m,(r,0),(w-r,h),255,-1);cv2.rectangle(m,(0,r),(w,h-r),255,-1)
    for x,y in((r,r),(w-r,r),(r,h-r),(w-r,h-r)): cv2.circle(m,(x,y),r,255,-1)
    return cv2.GaussianBlur(m,(0,0),0.8).astype(np.float32)/255
WM=rmask(WW,WH,RR);ring=WM-cv2.erode(WM,np.ones((13,13),np.uint8))
class Clip:
    def __init__(s,id_,t0,cx=0.5,zoom=1.0): s.cap=cv2.VideoCapture(f'{FG}{id_}.mp4');s.t0=t0;s.cx=cx;s.z=zoom
    def win(s,t,punch=0.0):
        s.cap.set(cv2.CAP_PROP_POS_MSEC,(s.t0+t)*1000);ok,im=s.cap.read()
        if not ok: s.cap.set(cv2.CAP_PROP_POS_MSEC,s.t0*1000);ok,im=s.cap.read()
        h,w=im.shape[:2];z=s.z*(1+punch);ch=h/z;cw=ch*WW/WH;x0=min(max(s.cx*w-cw/2,0),w-cw);y0=(h-ch)/2
        c=im[int(y0):int(y0+ch),int(x0):int(x0+cw)];return cv2.resize(c,(WW,WH),interpolation=cv2.INTER_CUBIC).astype(np.float32)
def put_window(frame,win,cx,cy,s=1.0,al=1.0):
    w,h=int(WW*s),int(WH*s)
    if w<8: return frame
    ww=cv2.resize(win,(w,h),interpolation=cv2.INTER_AREA);m=cv2.resize(WM,(w,h));rg=cv2.resize(ring,(w,h))
    x0,y0=int(cx-w/2),int(cy-h/2)
    ya,yb,xa,xb=max(y0,0),min(y0+h,H),max(x0,0),min(x0+w,W)
    sh=np.zeros((H,W),np.float32);sh[ya:yb,xa:xb]=m[ya-y0:yb-y0,xa-x0:xb-x0];sh=np.clip(cv2.GaussianBlur(np.roll(sh,(30,0),(0,1)),(0,0),28)*0.55,0,0.6)*al
    frame=frame*(1-sh[...,None])
    A=m[ya-y0:yb-y0,xa-x0:xb-x0]*al;R=rg[ya-y0:yb-y0,xa-x0:xb-x0]*al
    reg=frame[ya:yb,xa:xb];src=ww[ya-y0:yb-y0,xa-x0:xb-x0]
    src=src*(1-R[...,None])+255*R[...,None]
    frame[ya:yb,xa:xb]=reg*(1-A[...,None])+src*A[...,None];return frame
# ---------- merch ----------
def blit(frame,rgba,cx,cy,s=1.0,al=1.0,rot=0.0):
    if s<=0.02 or al<=0: return frame
    sw,shh=int(rgba.shape[1]*s),int(rgba.shape[0]*s);ss=cut3.rs(rgba,(sw,shh))
    if rot:
        M=cv2.getRotationMatrix2D((sw/2,shh/2),rot,1.0);ss=cv2.warpAffine(ss,M,(sw,shh),flags=cv2.INTER_LINEAR,borderValue=0)
    x0,y0=int(cx-sw/2),int(cy-shh/2);xa,xb,ya,yb=max(x0,0),min(x0+sw,W),max(y0,0),min(y0+shh,H)
    A=np.zeros((H,W),np.float32);A[ya:yb,xa:xb]=ss[ya-y0:yb-y0,xa-x0:xb-x0,3]/255.
    F=np.zeros((H,W,3),np.float32);F[ya:yb,xa:xb]=ss[ya-y0:yb-y0,xa-x0:xb-x0,:3]
    A*=al;sh=np.clip(cv2.GaussianBlur(np.roll(A,(22,0),(0,1)),(0,0),22)*0.55,0,0.6)
    return frame*(1-sh[...,None])*(1-A[...,None])+F*A[...,None]
# ---------- text chips ----------
def chip(txt,size,fg=(20,20,20,255),bg=(255,255,255,255),padx=34,pady=16,w='Bold'):
    t=text_img(txt,size,w,fg,sp=1,shadow=False);W_,H_=t.size
    c=Image.new('RGBA',(W_+2*padx,H_+2*pady),(0,0,0,0));d=ImageDraw.Draw(c)
    d.rounded_rectangle([0,0,c.width-1,c.height-1],radius=(H_+2*pady)//2 if (H_+2*pady)<130 else 30,fill=bg);c.alpha_composite(t,(padx,pady));return c
def overlay(im,ov,cx,cy,al=1.0,scale=1.0):
    if al<=0: return im
    if scale!=1.0: ov=ov.resize((max(int(ov.width*scale),2),max(int(ov.height*scale),2)),Image.LANCZOS)
    if al<1: ov=ov.copy();ov.putalpha(ov.getchannel('A').point(lambda v:int(v*al)))
    im.alpha_composite(ov,(int(cx-ov.width/2),int(cy-ov.height/2)));return im
def wipe(frame,p):   # diagonal white fan-wipe, p 0..1
    if p<=0 or p>=1: return frame
    X=np.mgrid[0:W][None,:]+0.5*np.mgrid[0:H][:,None];pos=-200+p*(W+0.5*H+400)
    a=np.clip(1-np.abs(X-pos)/130,0,1)[...,None];return frame*(1-a)+255*a
def finish(out,silent,music,mid,dur):
    pass
