# Background styles for the laugh videos. bg(style, seed, c1, c2, c3) -> float32 HxWx3 (1920x1080). Styles are structurally different, not recolours.
import numpy as np,cv2
W,H=1080,1920
def _noise(seed,amp=5):
    r=np.random.RandomState(seed);n=r.randn(H,W).astype(np.float32);n=cv2.GaussianBlur(n,(0,0),1.1);return n[...,None]*amp
def _vig(img):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);d=np.sqrt(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.7))**2);return img*(1-0.18*np.clip(d,0,1.2)**2)[...,None]
def sunburst(seed,c1,c2,c3=None,rays=24):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);cx,cy=W/2,H*0.42;a=np.arctan2(yy-cy,xx-cx);m=(np.floor((a+np.pi)/(2*np.pi)*rays)%2)[...,None]
    r=np.sqrt((xx-cx)**2+(yy-cy)**2)/1200;img=np.where(m>0,np.array(c1,np.float32),np.array(c2,np.float32))*(1-0.35*np.clip(r,0,1))[...,None]
    return img
def checker(seed,c1,c2,c3=None,s=135):
    yy,xx=np.mgrid[0:H,0:W];m=(((xx//s)+(yy//s))%2)[...,None];img=np.where(m>0,np.array(c1,np.float32),np.array(c2,np.float32)).astype(np.float32)
    yy2=np.linspace(0,1,H)[:,None,None];return img*(1-0.15*yy2)
def dots(seed,c1,c2,c3=None,s=54):   # comic halftone, dots grow downward
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);u=(xx+((yy//s)%2)*s/2)%s-s/2;v=yy%s-s/2;rad=s*(0.18+0.30*yy/H);m=(np.sqrt(u*u+v*v)<rad)[...,None]
    return np.where(m,np.array(c2,np.float32),np.array(c1,np.float32)).astype(np.float32)
def stripes(seed,c1,c2,c3=None,w=110):  # diagonal candy stripes
    yy,xx=np.mgrid[0:H,0:W];m=((((xx+yy)//w))%2)[...,None];return np.where(m>0,np.array(c1,np.float32),np.array(c2,np.float32)).astype(np.float32)
def chevron(seed,c1,c2,c3=None,w=120,amp=70):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);z=np.abs(((xx/ (2*amp)) % 2)-1)*amp*2;m=(((yy+z)//w)%2)[...,None];return np.where(m>0,np.array(c1,np.float32),np.array(c2,np.float32)).astype(np.float32)
def stars(seed,c1,c2,c3=None):
    c3=c3 or (255,255,255)  # night sky with stars/confetti
    rs=np.random.RandomState(seed);yy=np.linspace(0,1,H)[:,None,None];img=np.array(c1,np.float32)*(1-yy)+np.array(c2,np.float32)*yy;img=np.repeat(img,W,1).copy()
    for _ in range(190):
        x,y=rs.randint(0,W),rs.randint(0,H);r=rs.randint(4,17);col=tuple(int(v) for v in c3) if rs.rand()<0.7 else (255,220,90)
        pts=np.array([[x+r*np.cos(a),y+r*np.sin(a)*1.0] if i%2==0 else [x+r*0.42*np.cos(a),y+r*0.42*np.sin(a)] for i,a in enumerate(np.linspace(-np.pi/2,np.pi*1.5,11)[:10])],np.int32)
        cv2.fillPoly(img,[pts],col)
    return img
def hexes(seed,c1,c2,c3=None,s=90):
    img=np.full((H,W,3),np.array(c1,np.float32),np.float32);dx,dy=s*1.732,s*1.5
    for row in range(-1,int(H/dy)+2):
        for col in range(-1,int(W/dx)+2):
            cx=col*dx+(dx/2 if row%2 else 0);cy=row*dy;pts=np.array([[cx+s*0.9*np.cos(np.pi/6+i*np.pi/3),cy+s*0.9*np.sin(np.pi/6+i*np.pi/3)] for i in range(6)],np.int32)
            k=(row*3+col*7+seed)%5;cv2.fillPoly(img,[pts],tuple(int(v) for v in (np.array(c2)*(0.82+0.07*k))))
    return img
STY=dict(sunburst=sunburst,checker=checker,dots=dots,stripes=stripes,chevron=chevron,stars=stars,hexes=hexes)
def make(style,seed,c1,c2,c3=None):
    img=STY[style](seed,c1,c2,c3);img=_vig(img)+_noise(seed);return np.clip(img,0,255).astype(np.float32)
