# 300 very different 1080x1920 backgrounds: 36 procedural families x many palettes/params. usage: bg300.py [outdir] [only_family]
import numpy as np,cv2,sys,os,json,math,random
from scipy.spatial import cKDTree,Delaunay
W,H=1080,1920
PALS=['0b132b 1c2541 3a506b 5bc0be 6fffe9','264653 2a9d8f e9c46a f4a261 e76f51','ffbe0b fb5607 ff006e 8338ec 3a86ff','03045e 0077b6 00b4d8 90e0ef caf0f8','2b2d42 8d99ae edf2f4 ef233c d90429',
'606c38 283618 fefae0 dda15e bc6c25','f72585 b5179e 7209b7 560bad 3a0ca3','ffcdb2 ffb4a2 e5989b b5838d 6d6875','0d1b2a 1b263b 415a77 778da9 e0e1dd','ff9f1c ffbf69 ffffff cbf3f0 2ec4b6',
'390099 9e0059 ff0054 ff5400 ffbd00','010101 1a1a1a d4af37 f6e27a 8a6d1d','dad7cd a3b18a 588157 3a5a40 344e41','ff595e ffca3a 8ac926 1982c4 6a4c93','e63946 f1faee a8dadc 457b9d 1d3557',
'fdf0d5 c6d8d3 d81e5b 331832 f0544f','5f0f40 9a031e fb8b24 e36414 0f4c5c','cdb4db ffc8dd ffafcc bde0fe a2d2ff','003049 d62828 f77f00 fcbf49 eae2b7','1b4332 2d6a4f 40916c 74c69d b7e4c7',
'7400b8 6930c3 5e60ce 4ea8de 48bfe3','ef476f ffd166 06d6a0 118ab2 073b4c','2d00f7 8900f5 e500a4 ff0069 ff8500','f4f1de e07a5f 3d405b 81b29a f2cc8f','0a0908 22333b eae0d5 c6ac8f 5e503f',
'f94144 f3722c f8961e f9c74f 90be6d','10002b 240046 3c096c 5a189a 9d4edd','fefae0 faedcd e9edc9 ccd5ae d4a373','001219 005f73 0a9396 94d2bd e9d8a6','ff7b00 ff8800 ffa200 ffb700 ffd000',
'6d597a b56576 e56b6f eaac8b 355070','e0fbfc c2dfe3 9db4c0 5c6b73 253237','ff0a54 ff477e ff7096 ff85a1 fbb1bd','132a13 31572c 4f772d 90a955 ecf39e','8ecae6 219ebc 023047 ffb703 fb8500',
'ffffff 000000 ff0000 ffff00 0000ff','1a1423 372549 774c60 b75d69 eacdc2','06d6a0 1b9aaa ef476f ffc43d 2b2d42','d8e2dc ffe5d9 ffcad4 f4acb7 9d8189','233d4d fe7f2d fcca46 a1c181 619b8a',
'0f0e17 ff8906 f25f4c e53170 a7a9be','a8dadc f1faee e63946 457b9d 1d3557','3d5a80 98c1d9 e0fbfc ee6c4d 293241','f0ead2 dde5b6 adc178 a98467 6c584c','4a0e4e 81007f c200fb ec0868 fc2f00',
'ffe74c ff5964 ffffff 38a3a5 4b88a2','2e1f27 854d27 dd7230 f4c95d e7e393','14213d fca311 e5e5e5 ffffff 000000','9b5de5 f15bb5 fee440 00bbf9 00f5d4','582f0e 7f4f24 936639 b6ad90 c2c5aa',
'0081a7 00afb9 fdfcdc fed9b7 f07167','231942 5e548e 9f86c0 be95c4 e0b1cb','f6bd60 f7ede2 f5cac3 84a59d f28482','11001c 220135 32013f 4d0f6b ff2e63','eaf4f4 cce3de a4c3b2 6b9080 3a5a40',
'ff4d6d c9184a 800f2f 590d22 fff0f3','184e77 1e6091 1a759f 168aad 34a0a4','fcf6bd d0f4de a9def9 e4c1f9 ff99c8','2c3e50 e74c3c ecf0f1 3498db 2980b9','ffd6ff e7c6ff c8b6ff b8c0ff bbd0ff',
'1d1d1d f2c14e f78154 4d9078 b4436c','001d3d 003566 ffc300 ffd60a ffffff','e9ecef adb5bd 6c757d 343a40 ff6b6b','f2e9e4 c9ada7 9a8c98 4a4e69 22223b','00f5d4 00bbf9 9b5de5 f15bb5 fee440',
'3a0ca3 4361ee 4cc9f0 f72585 fff3b0','7f5539 9c6644 b08968 ddb892 e6ccb2','0b3954 087e8b bfd7ea ff5a5f c81d25','ffb5a7 fcd5ce f8edeb f9e5d8 f9dcc4','212529 495057 ced4da f8f9fa e03131',
'ff6d00 ff9e00 240046 5a189a 9d4edd','0e6ba8 0a2472 a6e1fa dff6ff 001c55']
NP=len(PALS)
def hx(s): return np.array([int(s[i:i+2],16) for i in (0,2,4)],np.float32)
def pal(i):
    c=[hx(x) for x in PALS[i%NP].split()];c.sort(key=lambda v:v@np.array([.3,.59,.11]));return c   # dark..light
def noise(rng,scale,oct=5,pers=.5,hh=H,ww=W):
    out=np.zeros((hh,ww),np.float32);amp=1.;tot=0.
    for o in range(oct):
        s=max(2.,scale/(2**o));g=rng.random((max(2,int(hh/s))+3,max(2,int(ww/s))+3)).astype(np.float32)
        out+=amp*cv2.resize(g,(ww,hh),interpolation=cv2.INTER_CUBIC);tot+=amp;amp*=pers
    n=out/tot;return (n-n.min())/(n.max()-n.min()+1e-6)
def cmap(t,cols):
    k=len(cols);t=np.clip(t,0,1)*(k-1);i0=np.clip(np.floor(t).astype(int),0,k-2);f=(t-i0)[...,None];C=np.array(cols,np.float32);return C[i0]*(1-f)+C[i0+1]*f
def ss(a,b,x): t=np.clip((x-a)/(b-a+1e-9),0,1);return t*t*(3-2*t)
YY,XX=np.mgrid[0:H,0:W].astype(np.float32)
def grad(c1,c2,ang=90):
    a=math.radians(ang);t=((XX-W/2)*math.cos(a)+(YY-H/2)*math.sin(a));t=(t-t.min())/(t.max()-t.min());return cmap(t,[c1,c2])
def full(c): return np.ones((H,W,3),np.float32)*np.array(c,np.float32)
def u8(a): return np.clip(a,0,255).astype(np.uint8)
def fl(a): return a.astype(np.float32)
def rc(rng,cols): return cols[rng.integers(len(cols))]
def tc(c): return tuple(int(x) for x in c)
def screen(a,b): return 255-(255-a)*(255-b)/255.
def gl(img,r,k): return cv2.GaussianBlur(img,(0,0),r)*k
def fam_mesh(r,P):
    n=int(r.integers(5,9));pts=r.random((n,2))*[W,H];cols=[rc(r,P) for _ in range(n)];sw,sh=W//6,H//6
    ys,xs=np.mgrid[0:sh,0:sw].astype(np.float32);ys*=6;xs*=6;acc=np.zeros((sh,sw,3),np.float32);ws=0
    for p,c in zip(pts,cols):
        d=((xs-p[0])**2+(ys-p[1])**2)+3000;w=1/d**1.6;acc+=w[...,None]*c;ws=ws+w
    return cv2.resize(acc/ws[...,None],(W,H),interpolation=cv2.INTER_CUBIC)
def fam_aurora(r,P):
    img=grad(P[0]*.35,P[1]*.55,r.integers(60,120));
    for k in range(int(r.integers(3,6))):
        y0=r.uniform(.15,.85)*H;a1=r.uniform(60,260);f1=r.uniform(.002,.007);p1=r.uniform(0,6);a2=r.uniform(20,90);f2=r.uniform(.006,.02);p2=r.uniform(0,6);th=r.uniform(50,170)
        cy=y0+a1*np.sin(XX*f1+p1)+a2*np.sin(XX*f2+p2);m=np.exp(-((YY-cy)/th)**2);m*=0.55+0.45*noise(r,200,3,hh=H,ww=W)
        img=screen(img,m[...,None]*rc(r,P[2:])*0.95)
    st=np.zeros((H,W),np.float32);ys=r.integers(0,H,int(r.integers(80,220)));xs=r.integers(0,W,len(ys));st[ys,xs]=r.uniform(.5,1,len(ys));st=cv2.GaussianBlur(st,(0,0),1.3)*14
    return screen(img,st[...,None]*255)
def fam_terrazzo(r,P):
    base=P[r.integers(0,5)] if r.random()<.5 else P[-1];cv=np.zeros((H,W,3),np.uint8);cv[:]=u8(base);cols=[c for c in P if not np.allclose(c,base)]
    for _ in range(int(r.integers(160,300))):
        cx,cy=r.random()*W,r.random()*H;R=r.uniform(14,70);k=int(r.integers(5,8));ang=np.sort(r.random(k))*2*np.pi;rad=R*r.uniform(.5,1.1,k)
        pts=np.stack([cx+rad*np.cos(ang),cy+rad*np.sin(ang)],1).astype(np.int32);cv2.fillPoly(cv,[pts],tc(rc(r,cols)),cv2.LINE_AA)
    img=fl(cv);return img*(0.94+0.12*noise(r,6,2)[...,None])
def fam_memphis(r,P):
    img=full(P[r.integers(0,2)] if r.random()<.6 else P[-1]);cv=u8(img);cols=[c for c in P if not np.allclose(c,img[0,0])]
    for _ in range(int(r.integers(55,95))):
        x,y=int(r.random()*W),int(r.random()*H);s=int(r.uniform(35,120));c=tc(rc(r,cols));t=int(r.integers(0,7));th=int(r.integers(5,12))
        if t==0: cv2.circle(cv,(x,y),s//2,c,th,cv2.LINE_AA)
        elif t==1: cv2.circle(cv,(x,y),s//2,c,-1,cv2.LINE_AA)
        elif t==2:
            a=r.uniform(0,6.28);pts=np.array([[x+s*np.cos(a+k*2.094),y+s*np.sin(a+k*2.094)] for k in range(3)],np.int32);cv2.polylines(cv,[pts],True,c,th,cv2.LINE_AA)
        elif t==3:
            pts=np.array([[x+i*s/8,y+(s/5)*math.sin(i*1.2)] for i in range(-8,9)],np.int32);cv2.polylines(cv,[pts],False,c,th,cv2.LINE_AA)
        elif t==4: cv2.line(cv,(x-s//3,y),(x+s//3,y),c,th,cv2.LINE_AA);cv2.line(cv,(x,y-s//3),(x,y+s//3),c,th,cv2.LINE_AA)
        elif t==5:
            for i in range(4):
                for j in range(4): cv2.circle(cv,(x+i*18,y+j*18),4,c,-1,cv2.LINE_AA)
        else:
            pts=np.array([[x+i*s/6,y+(s/5)*(i%2)] for i in range(-6,7)],np.int32);cv2.polylines(cv,[pts],False,c,th,cv2.LINE_AA)
    return fl(cv)
def dots(img,field,c1,sp,ang,mx=.7,col=None):
    cv=u8(img);a=math.radians(ang);ca,sa=math.cos(a),math.sin(a);R=int(math.hypot(W,H)/sp)+2
    for i in range(-R,R):
        for j in range(-R,R):
            x=W/2+(i*ca-j*sa)*sp;y=H/2+(i*sa+j*ca)*sp
            if -sp<x<W+sp and -sp<y<H+sp:
                t=field[int(np.clip(y,0,H-1)),int(np.clip(x,0,W-1))];rr=t*sp*mx
                if rr>.8: cv2.circle(cv,(int(x),int(y)),int(rr),tc(c1 if col is None else col),-1,cv2.LINE_AA)
    return fl(cv)
def fam_halftone(r,P):
    ang=r.uniform(0,180);a=math.radians(ang)
    f=((XX-W/2)*math.cos(a)+(YY-H/2)*math.sin(a));f=(f-f.min())/(f.max()-f.min()) if r.random()<.5 else np.clip(np.hypot(XX-r.uniform(0,W),YY-r.uniform(0,H))/1500,0,1)
    img=grad(P[1],P[0],ang) if r.random()<.5 else full(P[0]);img=dots(img,f,P[-1],r.uniform(20,40),45,.62)
    return dots(img,1-f,P[-2],r.uniform(20,40),15,.4) if r.random()<.5 else img
def fam_topo(r,P):
    n=noise(r,r.uniform(400,800),4);lv=int(r.integers(5,10));band=np.floor(n*lv)/lv;base=cmap(band,[P[0],P[1],P[2],P[3]] if r.random()<.5 else list(P))
    f=r.uniform(14,34);v=np.abs(np.sin(n*f*math.pi));line=1-ss(.0,.16,v);lc=P[-1] if r.random()<.6 else P[0]
    return base*(1-line[...,None])+lc*line[...,None]
def fam_marble(r,P):
    n=noise(r,r.uniform(350,650),5);a=r.uniform(0,6.28);u=(XX*math.cos(a)+YY*math.sin(a))/W*r.uniform(2,5)+n*r.uniform(2,6)
    v=np.abs(np.sin(u*math.pi));vein=v**r.uniform(.15,.4)
    img=cmap(vein,[P[-1],P[2],P[0]] if r.random()<.5 else [P[0],P[1],P[-1]])
    return img*(.95+.1*noise(r,4,2)[...,None])
def fam_watercolor(r,P):
    img=full([245,240,230]);
    for k in range(int(r.integers(5,9))):
        n=noise(r,r.uniform(250,500),4);th=r.uniform(.45,.62);m=ss(th,th+.05,n);edge=np.clip(m-cv2.GaussianBlur(m,(0,0),6),0,1)*3
        c=rc(r,P);al=r.uniform(.35,.65);col=255-(255-c)*(al*(.7+.3*noise(r,60,3)))[...,None]
        img=img*(1-m[...,None]*.9)+(img*col/255.)*m[...,None]*.9;img-=edge[...,None]*18
    return img*(.93+.1*noise(r,3,2)[...,None])
def fam_concrete(r,P):
    c=P[r.integers(1,4)];n=noise(r,r.uniform(120,320),6);f=noise(r,7,2);sp=(r.random((H,W))<.0025).astype(np.float32);sp=cv2.GaussianBlur(sp,(0,0),1.2)*5
    t=.55+.7*(n-.5)+.18*(f-.5)-sp;img=c*t[...,None]
    if r.random()<.5:
        cr=np.zeros((H,W),np.uint8)
        for _ in range(3):
            x,y=r.integers(0,W),r.integers(0,H);pts=[(x,y)]
            for i in range(40): x+=int(r.normal(0,25));y+=int(r.normal(35,25));pts.append((x,y))
            cv2.polylines(cr,[np.array(pts,np.int32)],False,255,2,cv2.LINE_AA)
        img*=(1-0.45*cv2.GaussianBlur(cr.astype(np.float32)/255,(0,0),1.5))[...,None]
    return img
def fam_weave(r,P):
    p=int(r.integers(6,11));A=np.sin(2*np.pi*XX/p)*.5+.5;B=np.sin(2*np.pi*YY/p)*.5+.5;chk=(((XX//p)+(YY//p))%2).astype(bool);t=np.where(chk,A,B)
    tv=noise(r,3,2,hh=H,ww=W);c=rc(r,P[1:4]);img=c*(.62+.5*t*(.8+.4*tv))[...,None]
    if r.random()<.5: img=img*(.9+.2*noise(r,300,3)[...,None])
    c2=rc(r,P[2:]);st=((XX//(p*8))%2==0)&(r.random()<2);img=np.where((((YY//(p*14))%3)==0)[...,None],img*.6+c2*.5*(.6+.5*t[...,None]),img);return img
def fam_wood(r,P):
    pw=int(r.integers(110,200));img=np.zeros((H,W,3),np.float32);n=noise(r,500,4);fn=noise(r,5,2,hh=H,ww=W);cols=[P[0],P[1],P[2]] if r.random()<.5 else [P[1],P[2],P[3]]
    for k in range(W//pw+2):
        x0=k*pw;off=r.uniform(0,40);sh=r.uniform(.8,1.15);d=(XX-x0)*r.uniform(.06,.14)+n*r.uniform(4,9)+off;v=np.abs(np.sin(d))**.7*.75+fn*.35
        m=((XX>=x0)&(XX<x0+pw))[...,None];img=np.where(m,cmap(v*sh,cols),img)
    gap=(np.minimum(XX%pw,pw-XX%pw)<2.5).astype(np.float32);return img*(1-.55*gap[...,None])
def fam_bauhaus(r,P):
    T=int(r.choice([135,180,216,270]));cv=np.zeros((H,W,3),np.uint8);bgc=P[-1] if r.random()<.5 else P[0]
    for y in range(0,H,T):
        for x in range(0,W,T):
            bg=rc(r,P);fg=rc(r,[c for c in P if not np.allclose(c,bg)]);cv[y:y+T,x:x+T]=u8(bg);t=int(r.integers(0,5));cx,cy=x+T//2,y+T//2;fgc=tc(fg)
            if t==0: cv2.circle(cv,(cx,cy),T//2-6,fgc,-1,cv2.LINE_AA)
            elif t==1: cv2.ellipse(cv,(x+(T if r.random()<.5 else 0),y+(T if r.random()<.5 else 0)),(T,T),0,0,360,fgc,-1,cv2.LINE_AA);cv[y:y+T,x:x+T]=np.where(cv[y:y+T,x:x+T]==0,u8(bg),cv[y:y+T,x:x+T])
            elif t==2: cv2.ellipse(cv,(cx,y+T),(T//2-6,T//2-6),0,180,360,fgc,-1,cv2.LINE_AA) if r.random()<.5 else cv2.ellipse(cv,(cx,y),(T//2-6,T//2-6),0,0,180,fgc,-1,cv2.LINE_AA)
            elif t==3: cv2.fillPoly(cv,[np.array([[x,y],[x+T,y],[x,y+T]] if r.random()<.5 else [[x+T,y],[x+T,y+T],[x,y+T]],np.int32)],fgc,cv2.LINE_AA)
            else: cv2.rectangle(cv,(x+T//4,y+T//4),(x+3*T//4,y+3*T//4),fgc,-1,cv2.LINE_AA)
    return fl(cv)
def fam_seigaiha(r,P):
    R=int(r.integers(55,95));cols=[rc(r,P) for _ in range(3)];cv=np.zeros((H,W,3),np.uint8);cv[:]=u8(P[0]);rows=int(H/(R/2))+3
    for j in range(rows):
        y=int(j*R/2)
        for i in range(-1,int(W/R)+2):
            x=int(i*R+(R/2 if j%2 else 0))
            for k,rr in enumerate([R,int(R*.8),int(R*.6),int(R*.4),int(R*.2)]):
                cv2.circle(cv,(x,y),rr,tc(cols[k%3] if k%2==0 else P[-1]),-1,cv2.LINE_AA)
            cv2.circle(cv,(x,y),R,tc(P[0]*.5),2,cv2.LINE_AA)
    return fl(cv)
def fam_isocubes(r,P):
    s=int(r.integers(70,120));cv=np.zeros((H,W,3),np.uint8);h=s*math.sqrt(3)/2;mono=r.random()<.45;base=rc(r,P[1:4])
    for j in range(-1,int(H/(1.5*s))+3):
        for i in range(-1,int(W/(2*h))+3):
            cx=i*2*h+(h if j%2 else 0);cy=j*1.5*s;c=base if mono else rc(r,P)
            t=[(cx,cy-s),(cx+h,cy-s/2),(cx,cy),(cx-h,cy-s/2)];l=[(cx-h,cy-s/2),(cx,cy),(cx,cy+s),(cx-h,cy+s/2)];rr=[(cx+h,cy-s/2),(cx,cy),(cx,cy+s),(cx+h,cy+s/2)]
            for poly,k in ((t,1.15),(l,.8),(rr,.55)): cv2.fillPoly(cv,[np.array(poly,np.int32)],tc(np.clip(c*k,0,255)),cv2.LINE_AA)
    return fl(cv)
def fam_plaid(r,P):
    def stripes(n,total):
        seq=[];c=0
        while c<total:
            w=int(r.choice([8,14,30,60,90]));seq.append((rc(r,P),w));c+=w
        return seq
    def build(seq,size,axis):
        out=np.zeros((size,3),np.float32);o=0
        for c,w in seq: out[o:o+w]=c;o+=w
        return out[:size]
    pat=stripes(8,320);ph=build(pat,320,0);pv=build(stripes(8,320),320,1)
    Hc=np.tile(ph,(H//320+1,1))[:H][:,None,:];Vc=np.tile(pv,(W//320+1,1))[:W][None,:,:]
    img=(Hc+Vc)/2*1.0;tw=np.sin((XX+YY)*.9)*.5+.5;return img*(.82+.28*tw[...,None])
def fam_rays(r,P):
    cx,cy=r.uniform(-.2,1.2)*W,r.uniform(.1,.9)*H;n=int(r.integers(12,40));ang=np.arctan2(YY-cy,XX-cx)+math.pi;ang+=.08*np.sin(np.hypot(XX-cx,YY-cy)*.004*r.uniform(0,3))
    k=np.floor(ang/(2*math.pi)*n)%2;img=np.where(k[...,None]==0,rc(r,P[1:3]),rc(r,P[3:]));d=np.hypot(XX-cx,YY-cy);img=img*(1.15-.4*np.clip(d/1800,0,1))[...,None]
    if r.random()<.5: img=dots(img,np.clip(d/1500,0,1)*0.9,P[-1],r.uniform(28,44),30,.5)
    return img
def fam_synthwave(r,P):
    hz=int(H*r.uniform(.5,.62));sky=cmap(np.clip(YY/hz,0,1),[P[0]*.5,P[1],P[2]]);img=sky.copy()
    cx=W//2;cy=int(hz-r.uniform(120,300));R=int(r.uniform(190,320));sun=np.hypot(XX-cx,YY-cy)<R;sc=cmap(np.clip((YY-(cy-R))/(2*R),0,1),[P[-1],P[-2]]);sl=((YY-(cy-R))%40>(np.clip((YY-(cy-R))/(2*R),0,1)*30))&(YY>cy);img=np.where((sun&~sl)[...,None],sc,img)
    fl_=np.where((YY>=hz)[...,None],np.ones_like(img)*P[0]*.3,img);img=fl_;g=np.zeros((H,W,3),np.uint8);gc=tc(P[-1]*.8+np.array([40,40,40]))
    for i in range(-30,31): cv2.line(g,(cx+i*60,hz),(cx+i*900,H),gc,3,cv2.LINE_AA)
    y=hz;dy=8
    while y<H: cv2.line(g,(0,int(y)),(W,int(y)),gc,3,cv2.LINE_AA);y+=dy;dy*=1.22
    g=fl(g);g[:hz]=0;img=screen(img,g*.85+gl(g,8,1.4));st=(r.random((H,W))<.0007)*(YY<hz);return screen(img,cv2.GaussianBlur(st.astype(np.float32),(0,0),1.1)[...,None]*255*6)
def fam_nebula(r,P):
    img=full(P[0]*.25)
    for k in range(3):
        n=noise(r,r.uniform(250,550),5);m=ss(.35,.85,n)**1.6;img=screen(img,m[...,None]*rc(r,P[1:])*.95)
    st=(r.random((H,W))<.0016).astype(np.float32);st=cv2.GaussianBlur(st,(0,0),1.2)*10;img=screen(img,st[...,None]*255)
    for _ in range(4):
        x,y=int(r.integers(0,W)),int(r.integers(0,H));l=np.zeros((H,W),np.float32);cv2.line(l,(x-40,y),(x+40,y),1,1);cv2.line(l,(x,y-40),(x,y+40),1,1);img=screen(img,cv2.GaussianBlur(l,(0,0),2.2)[...,None]*255*2.5)
    return img
def fam_bokeh(r,P):
    img=grad(P[0]*.6,P[1],r.integers(0,180));
    for lay,(lo,hi,al) in enumerate([(70,150,.28),(35,80,.35),(14,40,.45)]):
        cv=np.zeros((H,W,3),np.uint8)
        for _ in range(int(r.integers(14,30))*(lay+1)):
            c=tc(rc(r,P[2:]));x,y,rr=int(r.random()*W),int(r.random()*H),int(r.uniform(lo,hi));cv2.circle(cv,(x,y),rr,c,-1,cv2.LINE_AA);cv2.circle(cv,(x,y),rr,tc(np.clip(np.array(c)*1.4,0,255)),3,cv2.LINE_AA)
        cv=cv2.GaussianBlur(cv,(0,0),2+lay*0.5);img=screen(img,fl(cv)*al*1.6)
    return img
def fam_confetti(r,P):
    cv=np.zeros((H,W,3),np.uint8);cv[:]=u8(P[0] if r.random()<.5 else P[-1]);cols=[c for c in P if not np.allclose(c,cv[0,0])]
    for _ in range(int(r.integers(220,380))):
        x,y=r.random()*W,r.random()*H;s=r.uniform(10,32);c=tc(rc(r,cols));t=int(r.integers(0,3));a=r.uniform(0,6.28)
        if t==0: pts=np.array([[x+(i[0]*math.cos(a)-i[1]*math.sin(a)),y+(i[0]*math.sin(a)+i[1]*math.cos(a))] for i in [(-s,-s/3),(s,-s/3),(s,s/3),(-s,s/3)]],np.int32);cv2.fillConvexPoly(cv,pts,c,cv2.LINE_AA)
        elif t==1: cv2.circle(cv,(int(x),int(y)),int(s/2),c,-1,cv2.LINE_AA)
        else: pts=np.array([[x+s*math.cos(a+k*2.094),y+s*math.sin(a+k*2.094)] for k in range(3)],np.int32);cv2.fillConvexPoly(cv,pts,c,cv2.LINE_AA)
    return fl(cv)
def fam_papercut(r,P):
    img=grad(P[-1],P[-2],90);L=int(r.integers(6,9))
    for i in range(L):
        yb=H*(.15+.85*i/L);y=yb+r.uniform(50,120)*np.sin(XX*r.uniform(.002,.006)+r.uniform(0,6))+r.uniform(20,60)*np.sin(XX*r.uniform(.007,.016)+r.uniform(0,6));m=(YY>y).astype(np.float32)
        sh=np.roll(cv2.GaussianBlur(m,(0,0),16),-12,axis=0);img*=(1-.42*sh)[...,None];c=cmap(i/max(1,L-1),[P[1],P[2],P[3]]) if r.random()<.5 else cmap(i/max(1,L-1),[P[3],P[2],P[0]])
        img=np.where((m>0)[...,None],c*np.ones((H,W,3),np.float32),img)
    return img
def fam_voronoi(r,P):
    n=int(r.integers(55,150));pts=r.random((n,2))*[W,H];sw,sh=W//3,H//3;ys,xs=np.mgrid[0:sh,0:sw];tree=cKDTree(pts);d,lab=tree.query(np.stack([xs.ravel()*3,ys.ravel()*3],1));lab=lab.reshape(sh,sw);d=d.reshape(sh,sw)
    cc=[rc(r,P)*r.uniform(.8,1.15) for _ in range(n)];img=np.array(cc,np.float32)[lab];img*=(1-np.clip(d/260,0,.5))[...,None]*.9+.1
    img=cv2.resize(img,(W,H),interpolation=cv2.INTER_LINEAR);lb=cv2.resize(lab.astype(np.float32),(W,H),interpolation=cv2.INTER_NEAREST);e=((lb!=np.roll(lb,1,0))|(lb!=np.roll(lb,1,1))).astype(np.float32);e=cv2.dilate(e,np.ones((4,4),np.uint8))
    lc=P[0]*.25 if r.random()<.6 else P[-1];return img*(1-e[...,None])+lc*e[...,None]
def fam_moire(r,P):
    cs=[(r.uniform(-.3,1.3)*W,r.uniform(-.1,1.1)*H) for _ in range(int(r.integers(2,4)))];t=0
    for c in cs: t=t+np.sin(np.hypot(XX-c[0],YY-c[1])*r.uniform(.05,.14))
    t=(t/len(cs))*.5+.5;return cmap(ss(.25,.75,t) if r.random()<.5 else t,list(P))
def fam_mosaic(r,P):
    B=int(r.choice([36,54,72,108]));g=noise(r,r.uniform(5,12),3,hh=H//B+1,ww=W//B+1);g=(g-g.min())/(g.max()-g.min());q=np.floor(g*r.integers(4,8))/6
    img=cv2.resize(cmap(q,list(P)),(W,H),interpolation=cv2.INTER_NEAREST)
    for _ in range(int(r.integers(4,12))):
        y=int(r.integers(0,H-60));h=int(r.integers(8,60));img[y:y+h]=np.roll(img[y:y+h],int(r.integers(-200,200)),axis=1)
    return img
def fam_graingrad(r,P):
    img=grad(rc(r,P),rc(r,P),r.uniform(0,180))
    for _ in range(2):
        c=rc(r,P);d=np.hypot(XX-r.uniform(0,W),YY-r.uniform(0,H));m=np.exp(-(d/r.uniform(400,800))**2);img=img*(1-m[...,None]*.85)+c*m[...,None]*.85
    return img+r.normal(0,26,(H,W,1)).astype(np.float32)
def fam_spots(r,P):
    n=noise(r,r.uniform(70,130),3);base=P[r.integers(1,4)];fill=P[r.integers(2,5)];ring=P[0] if r.random()<.7 else P[-1];t=r.uniform(.56,.64);img=full(base);m=(n>t).astype(np.float32);rg=(n>t-.04).astype(np.float32)-m
    img=img*(1-rg[...,None])+ring*rg[...,None];img=img*(1-m[...,None])+fill*m[...,None];return img*(.95+.1*noise(r,5,2)[...,None])
def fam_blueprint(r,P):
    v=int(r.integers(0,3));
    if v==0: bg=full([20,70,130]);lc=np.array([220,235,255.])
    elif v==1: bg=full([245,240,215]);lc=np.array([90,150,120.])
    else: bg=full([28,50,44]);lc=np.array([230,235,230.])
    bg=bg*0.25+P[1+int(r.integers(0,3))]*0.75;lc=lc*0.3+P[-1]*0.7
    cv=np.zeros((H,W),np.float32);s=int(r.choice([24,30,36,45,60]))
    for x in range(0,W,s): cv[:,x:x+1]=.35 if (x//s)%5 else .9
    for y in range(0,H,s): cv[y:y+1,:]=np.maximum(cv[y:y+1,:],.35 if (y//s)%5 else .9)
    cv=cv2.GaussianBlur(cv,(0,0),.7);dd=np.zeros((H,W),np.uint8)
    for _ in range(int(r.integers(3,8))):
        t=int(r.integers(0,3));x,y=int(r.integers(100,W-100)),int(r.integers(100,H-100))
        if t==0: cv2.circle(dd,(x,y),int(r.integers(40,200)),255,2,cv2.LINE_AA)
        elif t==1: cv2.rectangle(dd,(x,y),(x+int(r.integers(80,300)),y+int(r.integers(80,300))),255,2,cv2.LINE_AA)
        else: cv2.arrowedLine(dd,(x,y),(x+int(r.integers(-250,250)),y+int(r.integers(-250,250))),255,2,cv2.LINE_AA,tipLength=.1)
    m=np.clip(cv*.95+fl(dd)/255,0,1)*(.75+.25*noise(r,100,3));img=bg*(1-m[...,None])+lc*m[...,None]
    if v==2: img*=(.85+.3*noise(r,40,4)[...,None])
    return img
def fam_lattice(r,P):
    R=int(r.integers(60,130));cv=np.zeros((H,W,3),np.uint8);bg=grad(P[0],P[1],r.uniform(0,180));cv[:]=u8(bg);lc=tc(rc(r,P[2:]));lc2=tc(rc(r,P[2:]));hh=R*math.sqrt(3)/2
    for j in range(-1,int(H/hh)+2):
        for i in range(-1,int(W/R)+2):
            x=int(i*R+(R/2 if j%2 else 0));y=int(j*hh)
            cv2.circle(cv,(x,y),R,lc,3 if r.random()<.9 else 5,cv2.LINE_AA)
    if r.random()<.5:
        ov=cv.copy()
        for j in range(-1,int(H/hh)+2,2):
            for i in range(-1,int(W/R)+2,2): cv2.circle(ov,(int(i*R+(R/2 if j%2 else 0)),int(j*hh)),R//2,lc2,-1,cv2.LINE_AA)
        cv=cv2.addWeighted(cv,.55,ov,.45,0)
    return fl(cv)
def fam_liquid(r,P):
    a=r.uniform(0,6.28);u=(XX*math.cos(a)+YY*math.sin(a));w=noise(r,r.uniform(300,600),4)*r.uniform(300,700)+noise(r,150,3)*120;t=((u+w)/r.uniform(140,300))%1.0
    cols=list(P)+[P[0]];img=cmap(np.abs(t*2-1),cols);return img*(.88+.25*noise(r,500,3)[...,None])
def fam_neon(r,P):
    img=grad(P[0]*.18,P[1]*.22,r.integers(0,180));l=np.zeros((H,W,3),np.uint8);t=int(r.integers(0,4));cols=[tc(np.clip(c*1.25,0,255)) for c in P[2:]]
    if t==0:
        for k in range(12): m=k*38;cv2.rectangle(l,(60+m,150+m*1.6 if False else 150+int(m*1.6)),(W-60-m,H-150-int(m*1.6)),cols[k%3],4,cv2.LINE_AA)
    elif t==1:
        for k in range(14): cv2.circle(l,(W//2,H//2),70+k*55,cols[k%3],4,cv2.LINE_AA)
    elif t==2:
        for k in range(10): s=k*48;cv2.polylines(l,[np.array([[W//2,260+s],[W-120-s//2,H-300-s//2],[120+s//2,H-300-s//2]],np.int32)],True,cols[k%3],4,cv2.LINE_AA)
    else:
        for k in range(16): y=int(H*(k+.5)/16);cv2.polylines(l,[np.array([[x,y+(40 if (x//90)%2 else -40)] for x in range(0,W+90,90)],np.int32)],False,cols[k%3],4,cv2.LINE_AA)
    l=fl(l);return screen(img,l*.8+gl(l,5,.8)+gl(l,16,1.6)+gl(l,40,1.8))
def fam_ripples(r,P):
    t=0;n=int(r.integers(5,12))
    for _ in range(n):
        cx,cy=r.random()*W,r.random()*H;d=np.hypot(XX-cx,YY-cy);t=t+np.sin(d*r.uniform(.04,.09)-r.uniform(0,6))*np.exp(-d/r.uniform(250,600))
    t=np.clip(t/max(1e-3,np.abs(t).max())*.5+.5,0,1);return cmap(t,[P[0],P[1],P[2],P[3]])*(.9+.15*noise(r,6,2)[...,None])
def fam_fabric(r,P):
    c=rc(r,P[1:4]);d=((XX+YY)//2)%4;t=np.where(d<2,1.0,.62);tv=cv2.resize(r.random((H//2+2,W//2+2)).astype(np.float32),(W,H),interpolation=cv2.INTER_NEAREST)
    rows=np.repeat(r.random(H//2+2),2)[:H][:,None];cols_=np.repeat(r.random(W//2+2),2)[:W][None,:];img=c*(t*(.78+.3*tv)*(.9+.2*rows)*(.9+.2*cols_))[...,None]
    c2=rc(r,P[3:]);bands=(((YY//r.integers(60,140))%2)==0)[...,None];img=np.where(bands,img*.8,img*.55+c2*.5);return img*(.8+.4*noise(r,200,3)[...,None])
def fam_zigzag(r,P):
    per=r.uniform(120,260);amp=r.uniform(50,130);bw=r.uniform(60,130);tri=r.random()<.55;x=XX/per;wave=(np.abs((x%1)*2-1)*2-1) if tri else np.sin(x*2*np.pi);t=(YY-amp*wave)/bw
    idx=np.floor(t).astype(int)%len(P);C=np.array(P,np.float32);img=C[idx]
    return img.reshape(H,W,3) if r.random()<.5 else np.rot90(img,1).copy()[:H,:W] if False else img
def fam_popart(r,P):
    cx,cy=r.uniform(.2,.8)*W,r.uniform(.2,.8)*H;n=int(r.integers(18,34));ang=np.arctan2(YY-cy,XX-cx)+math.pi;k=np.floor(ang/(2*math.pi)*n)%2;img=np.where(k[...,None]==0,P[-1],P[-2])
    f=np.clip(YY/H,0,1);return dots(img,f,P[1],r.uniform(24,40),45,.6)
def fam_lowpoly(r,P):
    c=int(r.integers(110,200));gx=np.arange(-c,W+2*c,c);gy=np.arange(-c,H+2*c,c);pts=np.array([[x+r.uniform(-.4,.4)*c,y+r.uniform(-.4,.4)*c] for y in gy for x in gx]);tri=Delaunay(pts).simplices
    a=r.uniform(0,6.28);cv=np.zeros((H,W,3),np.uint8);n=noise(r,300,3)
    for s in tri:
        p=pts[s];ctr=p.mean(0);t=((ctr[0]-W/2)*math.cos(a)+(ctr[1]-H/2)*math.sin(a))/(math.hypot(W,H)/1.3)+.5+r.normal(0,.09);col=tc(cmap(np.array([np.clip(t,0,1)]),list(P))[0]);cv2.fillConvexPoly(cv,p.astype(np.int32),col,cv2.LINE_AA);cv2.polylines(cv,[p.astype(np.int32)],True,col,1,cv2.LINE_AA)
    return fl(cv)
def fam_argyle(r,P):
    sw,sh=int(r.integers(110,200)),int(r.integers(180,320));cv=np.zeros((H,W,3),np.uint8);cv[:]=u8(P[0]);c1,c2=rc(r,P[1:]),rc(r,P[1:])
    for j in range(-1,H//sh+2):
        for i in range(-1,W//sw+2):
            cx=i*sw+(sw/2 if j%2 else 0);cy=j*sh/2;c=c1 if (i+j)%2==0 else c2
            cv2.fillConvexPoly(cv,np.array([[cx,cy-sh/2],[cx+sw/2,cy],[cx,cy+sh/2],[cx-sw/2,cy]],np.int32),tc(c),cv2.LINE_AA)
    img=fl(cv);lines=np.zeros((H,W),np.uint8)
    for k in range(-H,W,int(sw)): cv2.line(lines,(k,0),(k+int(H*sw/sh),H),255,2,cv2.LINE_AA)
    return np.where(cv2.GaussianBlur(lines,(0,0),.6)[...,None]>90,P[-1]*.9,img)
FAMS=[('mesh',fam_mesh),('aurora',fam_aurora),('terrazzo',fam_terrazzo),('memphis',fam_memphis),('halftone',fam_halftone),('topo',fam_topo),('marble',fam_marble),('watercolor',fam_watercolor),('concrete',fam_concrete),('weave',fam_weave),('wood',fam_wood),('bauhaus',fam_bauhaus),('seigaiha',fam_seigaiha),('isocubes',fam_isocubes),('plaid',fam_plaid),('rays',fam_rays),('synthwave',fam_synthwave),('nebula',fam_nebula),('bokeh',fam_bokeh),('confetti',fam_confetti),('papercut',fam_papercut),('voronoi',fam_voronoi),('moire',fam_moire),('mosaic',fam_mosaic),('graingrad',fam_graingrad),('spots',fam_spots),('blueprint',fam_blueprint),('lattice',fam_lattice),('liquid',fam_liquid),('neon',fam_neon),('ripples',fam_ripples),('fabric',fam_fabric),('zigzag',fam_zigzag),('popart',fam_popart),('lowpoly',fam_lowpoly),('argyle',fam_argyle)]
def finish(img,r):
    img=np.clip(img,0,255).astype(np.float32);lum=img@np.array([.114*0+.299,.587,.114],np.float32)
    # phone readability: lift pure-black floors, tame extreme local busyness
    mean=float(lum.mean())
    if mean<48: img=img*(1+(48-mean)/60)+ (48-mean)*.6
    img=img+r.normal(0,3.0,(H,W,1)).astype(np.float32)   # fine paper grain on every background
    return np.clip(img,0,255).astype(np.uint8)
def make(fi,k,seed):
    name,fn=FAMS[fi];r=np.random.default_rng(seed);P=pal(fi*11+k*13+seed%7*0);img=fn(r,P);return finish(img,r),name,P
if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else 'bgs';only=sys.argv[2] if len(sys.argv)>2 else None;os.makedirs(out,exist_ok=True);F=len(FAMS);base,extra=300//F,300%F;cat=[];idx=0
    for fi,(name,fn) in enumerate(FAMS):
        cnt=base+(1 if fi<extra else 0)
        for k in range(cnt):
            idx+=1
            if only and only!=name: continue
            seed=1000+fi*100+k;img,nm,P=make(fi,k,seed);fn_=f'bg_{idx:03d}_{name}.jpg';cv2.imwrite(os.path.join(out,fn_),cv2.cvtColor(img,cv2.COLOR_RGB2BGR),[cv2.IMWRITE_JPEG_QUALITY,90])
            cat.append({'id':idx,'file':fn_,'family':name,'seed':seed,'palette':PALS[(fi*11+k*13)%NP],'mean_lum':round(float(img.mean()),1)});print(fn_,flush=True)
    json.dump(cat,open(os.path.join(out,'catalog.json'),'w'),indent=1)
