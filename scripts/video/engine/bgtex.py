import numpy as np,cv2,math
from PIL import Image,ImageDraw,ImageFilter
W,H=1080,1920
def grad(c1,c2,ang=90):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);t=(yy*math.sin(math.radians(ang))+xx*math.cos(math.radians(ang)));t=(t-t.min())/(t.max()-t.min())
    return np.array(c1,np.float32)*(1-t[...,None])+np.array(c2,np.float32)*t[...,None]
def finish(a,seed=0,vig=0.30,grain=3.0):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);r=np.sqrt(((xx-W/2)/(W*0.8))**2+((yy-H*0.45)/(H*0.7))**2)
    a=a*(1-vig*r[...,None]);a=a+np.random.RandomState(seed).randn(H,W,1).astype(np.float32)*grain
    return np.clip(a[...,::-1],0,255)   # RGB -> BGR
def frond_layer(shape,base,ang,L,curve,leaf,n=24,droop=0.5,col=(0,0,0,255),sc=2):
    w,h=shape;im=Image.new("RGBA",(w*sc,h*sc),(0,0,0,0));d=ImageDraw.Draw(im)
    bx,by=base[0]*sc,base[1]*sc;a=math.radians(ang);ux,uy=math.cos(a),math.sin(a);nx,ny=-uy,ux
    def P(t): return (bx+(L*t*ux+curve*t*t*nx)*sc, by+(L*t*uy+curve*t*t*ny)*sc)
    pts=[P(i/60) for i in range(61)];d.line(pts,fill=col,width=int(11*sc))
    for i in range(n):
        t=0.10+0.88*i/(n-1);p=P(t);q=P(min(t+0.01,1));tx,ty=q[0]-p[0],q[1]-p[1];tl=math.hypot(tx,ty)+1e-6;tx/=tl;ty/=tl
        ll=leaf*sc*(math.sin(math.pi*(0.12+0.88*t))**0.7)*(1.05-0.35*t)
        for sgn in (-1,1):
            ph=math.radians(62-34*t)*sgn;dx=tx*math.cos(ph)-ty*math.sin(ph);dy=tx*math.sin(ph)+ty*math.cos(ph)
            dy+=droop*0.55
            m=math.hypot(dx,dy);dx/=m;dy/=m;ex,ey=p[0]+dx*ll,p[1]+dy*ll;mx,my=(p[0]+ex)/2+(-dy)*ll*0.10*sgn,(p[1]+ey)/2+dx*ll*0.10*sgn
            wd=30*sc*(1-0.55*t)
            d.polygon([(p[0]-(-dy)*wd/2,p[1]-dx*wd/2),(mx+(-dy)*wd*0.6,my+dx*wd*0.6),(ex,ey),(mx-(-dy)*wd*0.6,my-dx*wd*0.6),(p[0]+(-dy)*wd/2,p[1]+dx*wd/2)],fill=col)
    return im.resize((w,h),Image.LANCZOS)
def palm(c1,c2,dark,light=None,seed=0):
    bg=grad(c1,c2,90);rs=np.random.RandomState(seed)
    deep=Image.new("RGBA",(W,H),(0,0,0,0));near=Image.new("RGBA",(W,H),(0,0,0,0))
    specs=[((-120,120),22,1050,200,420),((W+120,60),158,1000,-210,410),((-130,1000),-12,900,-160,380),((W+110,1180),192,950,170,390),((-100,1900),-35,1100,-190,420),((W+100,1960),-148,1050,200,420)]
    for k,(b,a,L,cu,lf) in enumerate(specs):
        for layer,blur,al,sc in ((deep,14,0.30,1.12),(near,1.6,0.48,1.0)):
            f=frond_layer((W,H),(b[0]+rs.randint(-30,30),b[1]+rs.randint(-30,30)),a+rs.randint(-6,6),L*sc,cu,lf*sc,droop=0.35);f=f.filter(ImageFilter.GaussianBlur(blur))
            f.putalpha(f.getchannel('A').point(lambda v:int(v*al)));layer.alpha_composite(f)
    out=bg.copy()
    for lay in (deep,near):
        a=np.array(lay.getchannel('A'),np.float32)[...,None]/255.;out=out*(1-a)+np.array(dark,np.float32)*a
    if light is not None:
        L=np.zeros((H,W),np.float32)
        for _ in range(26): cv2.circle(L,(int(rs.randint(0,W)),int(rs.randint(0,H))),int(rs.randint(40,140)),1.0,-1)
        L=cv2.GaussianBlur(L,(0,0),38)*0.22;out=out*(1-L[...,None])+np.array(light,np.float32)*L[...,None]
    return finish(out,seed)
def terrazzo(base,chips,seed=0):
    rs=np.random.RandomState(seed);im=Image.new("RGB",(W,H),tuple(base));d=ImageDraw.Draw(im)
    for _ in range(520):
        cx,cy=rs.randint(0,W),rs.randint(0,H);r=rs.randint(10,34);k=rs.randint(5,8);a0=rs.rand()*6.28
        d.polygon([(cx+r*(0.6+0.5*rs.rand())*math.cos(a0+j*6.28/k),cy+r*(0.6+0.5*rs.rand())*math.sin(a0+j*6.28/k)) for j in range(k)],fill=tuple(chips[rs.randint(len(chips))]))
    a=np.array(im,np.float32);return finish(cv2.GaussianBlur(a,(0,0),0.8),seed,0.25,2.5)
def topo(c1,c2,line,seed=0,k=16,th=0.06):
    rs=np.random.RandomState(seed);f=cv2.resize(rs.rand(10,6).astype(np.float32),(W,H),interpolation=cv2.INTER_CUBIC);f=cv2.GaussianBlur(f,(0,0),60)
    f=(f-f.min())/(f.max()-f.min());fr=(f*k)%1.0;m=np.clip(1-np.abs(fr-0.5)/th,0,1);m=cv2.GaussianBlur(m,(0,0),1.1)[...,None]*0.75
    bg=grad(c1,c2,90);return finish(bg*(1-m)+np.array(line,np.float32)*m,seed)
def halftone(c1,c2,dot,seed=0,step=34):
    bg=grad(c1,c2,90);m=np.zeros((H,W),np.float32)
    for j,y in enumerate(range(0,H+step,step)):
        for i,x in enumerate(range(-step,W+step,step)):
            xx=x+(step//2 if j%2 else 0);r=step*0.46*max(0,min(1,(y/H)**1.4*1.15))
            if r>0.6: cv2.circle(m,(xx,y),int(r),1.0,-1,cv2.LINE_AA)
    m=cv2.GaussianBlur(m,(0,0),0.7)[...,None]*0.5;return finish(bg*(1-m)+np.array(dot,np.float32)*m,seed)
def sunburst(c1,c2,cen=(0.5,0.42),n=28,seed=0):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);a=np.arctan2(yy-H*cen[1],xx-W*cen[0]);s=(np.sin(a*n/2)>0).astype(np.float32)
    s=cv2.GaussianBlur(s,(0,0),1.0)[...,None];return finish(np.array(c1,np.float32)*(1-s)+np.array(c2,np.float32)*s,seed,0.35)
def waves(c1,c2,line,seed=0,k=34):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);ph=yy/H*k+0.35*np.sin(xx/W*6.28*1.5+yy/H*5);m=(np.clip(1-np.abs((ph%1.0)-0.5)/0.11,0,1))[...,None]*0.45
    bg=grad(c1,c2,90);return finish(bg*(1-m)+np.array(line,np.float32)*m,seed)
if __name__=="__main__":
    t=[palm((18,92,96),(8,44,56),(4,26,32),(120,210,190),1),palm((214,120,84),(150,60,50),(86,28,28),(255,200,150),2),terrazzo((232,222,206),[(196,120,96),(70,110,100),(232,176,60),(40,50,70),(240,240,236)],3),
       topo((20,36,74),(10,18,44),(110,150,230),4),halftone((255,170,120),(230,70,110),(255,230,200),5),sunburst((250,200,70),(244,170,40),seed=6),waves((20,110,170),(10,50,100),(180,225,255),7),palm((42,98,60),(18,52,36),(8,28,20),(170,230,150),8)]
    S=np.hstack([cv2.resize(x.astype(np.uint8),(270,480)) for x in t]);cv2.imwrite('/tmp/kl/bgs.jpg',S)
