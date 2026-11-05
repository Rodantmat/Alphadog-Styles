from v5lib import *
import art,math
rs=np.random.RandomState(7)
# ---------- brick wall ----------
def wall():
    img=np.zeros((H,W,3),np.float32);bh,bw=62,172
    for r,y in enumerate(range(-bh,H+bh,bh)):
        off=(bw//2) if r%2 else 0
        for x in range(-bw,W+bw,bw):
            c=np.array([40,36,56],np.float32)+rs.randn()*7+np.array([rs.randn()*3,0,rs.randn()*4])
            img[max(y+3,0):max(y+bh-3,0),max(x+off+3,0):max(x+off+bw-3,0)]=c
    mort=(img.sum(2)==0);img[mort]=(16,14,22)
    n=cv2.GaussianBlur(rs.randn(H,W).astype(np.float32),(0,0),1.3)*6;img+=n[...,None]
    n2=cv2.GaussianBlur(rs.randn(H//8,W//8).astype(np.float32),(0,0),6);n2=cv2.resize(n2,(W,H))*60;img+=n2[...,None]
    return np.clip(img,0,255)
WALL=wall()
# ---------- neon group canvas ----------
CW,CH=1000,900;AH=560
a=art.alpha('labrador_retriever','line_cool','front',h=AH);arr,S=art.arrival(a);AW=a.shape[1]
ax0=(CW-AW)//2;ay0=40
def text_mask(txt,size,sp):
    t=text_img(txt,size,'Bold',(255,255,255,255),sp=sp,shadow=False);m=np.array(t.getchannel('A'),np.float32)/255;return m
tm=text_mask("LABRADOR",78,12)
PINK=np.array([170,70,255],np.float32);PCORE=np.array([235,225,255],np.float32);CY_=np.array([255,230,70],np.float32);CCORE=np.array([255,250,225],np.float32)
def neon_group(cur,tshow,g,tip=True):
    m=np.zeros((CH,CW),np.float32)
    drawn=(arr<=cur).astype(np.float32)*a;m[ay0:ay0+AH,ax0:ax0+AW]=cv2.GaussianBlur(drawn,(0,0),0.7)
    tipm=np.zeros_like(m)
    if tip and cur<S: tipm[ay0:ay0+AH,ax0:ax0+AW]=cv2.GaussianBlur(((arr<=cur)&(arr>cur-30)).astype(np.float32)*a,(0,0),2)
    t=np.zeros_like(m)
    if tshow>0:
        y0=ay0+AH+70;t[y0:y0+tm.shape[0],(CW-tm.shape[1])//2:(CW-tm.shape[1])//2+tm.shape[1]]=tm*tshow
    def lay(mask,col,core):
        glow=(cv2.GaussianBlur(mask,(0,0),5)*0.9+cv2.GaussianBlur(mask,(0,0),16)*0.7+cv2.GaussianBlur(mask,(0,0),44)*0.55)
        return (glow[...,None]*col*1.0+np.clip(mask*1.2,0,1)[...,None]*core)*g
    L=lay(m,PINK,PCORE)+lay(t,CY_,CCORE)+tipm[...,None]*np.array([255,255,255],np.float32)*1.1*g
    return L,np.clip(m+t,0,1)
def place(layer,sc,cx,cy):
    h,w=layer.shape[:2];nw,nh=int(w*sc),int(h*sc);ly=cv2.resize(layer,(nw,nh),interpolation=cv2.INTER_AREA)
    out=np.zeros((H,W,3),np.float32);x0=int(cx-nw/2);y0=int(cy-nh/2)
    xa,xb=max(x0,0),min(x0+nw,W);ya,yb=max(y0,0),min(y0+nh,H);out[ya:yb,xa:xb]=ly[ya-y0:yb-y0,xa-x0:xb-x0];return out
def flicker(f):
    if f<14: return [0,0.9,0.1,0,0.8,0.2,1,0,0.7,0.1,0.9,0,1,0.6][f]*1.0
    g=1.0
    for fk in (60,61,118,119,120,176,200):
        if f==fk: g=0.25
    return g*(0.97+0.03*math.sin(f*1.7))
# ---------- product ----------
prod=apparel('hoodie','labrador_retriever','5LB',(900,840))
def paste_item(bg,s,t,cy,lit):
    p=(0.94+0.06*(1-np.exp(-t*9)))*(1+0.04*min(t,1.5));sw=int(s.shape[1]*p);shh=int(s.shape[0]*p);ss=cut3.rs(s,(sw,shh))
    x0=W//2-sw//2;y0=int(cy-shh//2);A=np.zeros((H,W),np.float32);F=np.zeros((H,W,3),np.float32)
    A[y0:y0+shh,x0:x0+sw]=ss[...,3]/255.;F[y0:y0+shh,x0:x0+sw]=ss[...,:3]
    Fl=F*(0.55+0.45*lit[...,None]/ max(lit.max(),1e-3)) if False else F*0.88+PINK*0.10*np.clip(1-np.abs(np.arange(H)[:,None]-(cy-shh/2))/(shh*0.7),0,1)[...,None]
    sh=np.clip(cv2.GaussianBlur(np.roll(A,(26,0),(0,1)),(0,0),26)*0.6,0,0.75)
    return bg*(1-sh[...,None])*(1-A[...,None])+Fl*A[...,None]
# ---- print bbox on fitted product ----
pa=prod[...,3]>200;lum=prod[...,:3].astype(np.float32).mean(2)
ph_,pw_=prod.shape[:2];dm=(lum<90)&pa
dm[:int(ph_*0.25)]=0;dm[int(ph_*0.62):]=0
ys,xs=np.where(dm);PX0,PX1,PY0,PY1=np.percentile(xs,0.3),np.percentile(xs,99.7),np.percentile(ys,0.3),np.percentile(ys,99.7)
print('print bbox in product',PX0,PX1,PY0,PY1,prod.shape)
PCX,PCY,PW,PHH=(PX0+PX1)/2-pw_/2,(PY0+PY1)/2-ph_/2,PX1-PX0,PY1-PY0   # relative to product centre
HCY=785
def sm(x): x=min(max(x,0),1);return x*x*(3-2*x)
def hood(bg,s,al):
    sw=int(pw_*s);shh=int(ph_*s);ss=cut3.rs(prod,(sw,shh));x0=W//2-sw//2;y0=int(HCY-shh//2)
    A=np.zeros((H,W),np.float32);F=np.zeros((H,W,3),np.float32)
    xa,xb=max(x0,0),min(x0+sw,W);ya,yb=max(y0,0),min(y0+shh,H)
    A[ya:yb,xa:xb]=ss[ya-y0:yb-y0,xa:xb-x0 if False else xb-x0,3]/255. if False else ss[ya-y0:yb-y0,xa-x0:xb-x0,3]/255.
    F[ya:yb,xa:xb]=ss[ya-y0:yb-y0,xa-x0:xb-x0,:3]
    A=A*al;sh=np.clip(cv2.GaussianBlur(np.roll(A,(26,0),(0,1)),(0,0),26)*0.6,0,0.75)
    return bg*(1-sh[...,None])*(1-A[...,None])+F*A[...,None]
artc=np.array([ax0+AW/2-CW/2,ay0+AH/2-CH/2],np.float32)   # art centre offset in group canvas
DRAW0,DRAW1=8,118
T0,T1=150,184
FADE0,FADE1=184,206
TEND=262
p=enc('/tmp/kl/vX3_silent.mp4')
for f in range(TEND):
    g=flicker(f) if f<FADE0 else 1.0
    cur=0 if f<DRAW0 else S*min((f-DRAW0)/(DRAW1-DRAW0),1)**0.9
    tshow=0 if f<124 else min(1,(f-124)/12)*(1.0 if f>136 else (0.3+0.7*((f%3)!=0)))
    u=sm((f-T0)/(T1-T0))
    tshow*=1-sm((f-T0)/10)           # text fades first
    L,mk=neon_group(cur,tshow,g,tip=(f<DRAW1+10))
    if f<DRAW0: L2,_=neon_group(S,0,0.07,False);L=L2*0.5
    hs=0.62+0.38*u                    # hoodie scale
    tsc=min(H,1)*0+ (PHH*hs)/AH       # neon scale landing on print height
    tx,ty=W/2+PCX*hs,HCY+PCY*hs
    sc=1+(tsc-1)*u
    ac=np.array([W/2,800.],np.float32)+artc;ac=ac+(np.array([tx,ty])-ac)*u
    cx,cy=ac[0]-artc[0]*sc,ac[1]-artc[1]*sc
    fo=1-sm((f-FADE0)/(FADE1-FADE0))
    Lp=place(L*fo,sc,cx,cy)
    small=cv2.resize(np.clip(Lp,0,255),(W//6,H//6),interpolation=cv2.INTER_AREA);lt=cv2.GaussianBlur(small,(0,0),16);lt=cv2.resize(lt,(W,H))
    lit=np.clip(0.30+lt/255.*1.5,0,1.5)
    vig=1-0.35*(((np.mgrid[0:W][None,:]-W/2)/(W*0.7))**2+((np.mgrid[0:H][:,None]-H*0.45)/(H*0.7))**2)
    base=WALL*lit*vig[...,None]
    hal=sm((f-T0+6)/18)
    frame=hood(base,hs,hal)
    frame=frame+Lp*(0.55+0.45*(1-hal)) if f>=T0 else frame+Lp
    im=toim(np.clip(frame,0,255));im=lock(im)
    if f>=T1: im=paste_c(im,V.cta("alphadogstyles.com  ·  link in bio"),1212,min(1,(f-T1)/12))
    p.stdin.write(back(im).tobytes())
p.stdin.close();p.wait()
