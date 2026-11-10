#!/usr/bin/env python3
"""Compositor v2: Printify transparent cutout on a real-photo background, following docs/research/11 (shadows, haze, depth, grain, safe zones)."""
import numpy as np, random
from PIL import Image,ImageFilter,ImageDraw
W,H=1080,1920
def load(f):
    im=Image.open(f).convert("RGBA"); a=np.array(im)[:,:,3]; ys,xs=np.where(a>6); return im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
def garment_rgb(im,kind):
    a=np.array(im); h,w=a.shape[:2]
    if kind=="person": a=a[int(h*.28):int(h*.58),int(w*.28):int(w*.72)]
    m=a[:,:,3]>230
    return tuple(int(x) for x in np.median(a[m][:,:3],axis=0)) if m.sum()>50 else (128,128,128)
def cropped_bottom(im):
    a=np.array(im)[:,:,3]; return (a[-3:,:]>200).mean()>0.12
def edge_bad(im,kind):
    a=np.array(im)[:,:,3]>200
    e=lambda x:x.mean()>0.02
    if e(a[0,:]) or e(a[:,0]) or e(a[:,-1]): return True
    return kind!="person" and e(a[-1,:])
def prep_bg(bg,kind,rnd,blur=None):
    a=np.asarray(bg.convert("RGB").resize((W,H),Image.LANCZOS),"float32")
    a=a*(0.88)+ (a.mean()*0.12)                      # -12% local contrast
    a=a+6.0                                            # lift blacks (haze)
    g=a.mean(axis=2,keepdims=True); a=a*0.91+g*0.09    # desaturate 9%
    im=Image.fromarray(np.clip(a,0,255).astype("uint8"))
    s=blur if blur is not None else (rnd.uniform(5,9) if kind in("person","closeup") else 0)
    if s: im=im.filter(ImageFilter.GaussianBlur(s))
    return im
def shadow_layer(im,x,y,kind,bgc,cropped):
    """returns RGBA layer with tinted shadows"""
    layer=Image.new("RGBA",(W,H),(0,0,0,0)); a=im.split()[3]; col=tuple(int(c*0.45) for c in bgc)
    def put(alpha,off,blur,op):
        s=Image.new("RGBA",im.size,col+(255,)); s.putalpha(alpha.point(lambda v:int(v*op))); l=Image.new("RGBA",(W,H),(0,0,0,0)); l.paste(s,(x+off[0],y+off[1]),s); return l.filter(ImageFilter.GaussianBlur(blur))
    if kind=="person" and not cropped:
        w=im.width; el=Image.new("L",(W,H),0); d=ImageDraw.Draw(el); cx=x+w//2; by=y+im.height-6
        d.ellipse([cx-int(w*.30),by-14,cx+int(w*.30),by+22],fill=int(255*0.5)); el=el.filter(ImageFilter.GaussianBlur(9))
        s=Image.new("RGBA",(W,H),col+(255,)); s.putalpha(el); layer=Image.alpha_composite(layer,s)
        sq=a.resize((im.width,max(8,int(im.height*0.22))),Image.BILINEAR).transpose(Image.FLIP_TOP_BOTTOM)
        layer=Image.alpha_composite(layer,put_squash(sq,x+28,by-6,col,0.22,30))
    elif kind in("flat","folded","closeup"):
        layer=Image.alpha_composite(layer,put(a,(11,22),18,0.22)); layer=Image.alpha_composite(layer,put(a,(3,5),4,0.34))
    return layer
def put_squash(sq,x,y,col,op,blur):
    s=Image.new("RGBA",sq.size,col+(255,)); s.putalpha(sq.point(lambda v:int(v*op))); l=Image.new("RGBA",(W,H),(0,0,0,0)); l.paste(s,(x,y),s); return l.filter(ImageFilter.GaussianBlur(blur))
def compose(cut_file,kind,bgfile,seed=0,kb=False):
    rnd=random.Random(seed); im=load(cut_file); bg=prep_bg(Image.open(bgfile),kind,rnd); bgc=tuple(int(v) for v in np.array(bg.resize((16,16))).reshape(-1,3).mean(axis=0)); cropped=cropped_bottom(im); w,h=im.size
    if kind=="person":
        th=1480 if cropped else 1180; s=min(th/h,1000/w); im=im.resize((int(w*s),int(h*s)),Image.LANCZOS); x=(W-im.width)//2+rnd.randint(-40,40); y=H-im.height+ (6 if cropped else -(rnd.randint(480,520)))
        if not cropped: y=min(y,1440-im.height+0)
    elif kind=="closeup":
        s=min(1100/h,980/w); im=im.resize((int(w*s),int(h*s)),Image.LANCZOS); x=(W-im.width)//2; y=H-im.height+6 if cropped else 560
    else:
        lim=(820,980) if kind=="flat" else (640,700); s=min(lim[0]/w,lim[1]/h); im=im.resize((int(w*s),int(h*s)),Image.LANCZOS); x=(W-im.width)//2+rnd.randint(-30,30); cy=840 if kind=="flat" else 930; y=cy-im.height//2
    # colour: <=6% tint toward bg mean (never re-grade hue)
    arr=np.array(im).astype("float32"); arr[:,:,:3]=arr[:,:,:3]*0.94+np.array(bgc,"float32")*0.06; im=Image.fromarray(arr.astype("uint8"),"RGBA")
    can=bg.convert("RGBA"); can=Image.alpha_composite(can,shadow_layer(im,x,y,kind,bgc,cropped)); can.alpha_composite(im,(x,y))
    a=np.array(can.convert("RGB")).astype("float32")
    yy,xx=np.mgrid[0:H,0:W].astype("float32"); d=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H*0.5)/(H/2))**2); a*= (1-0.13*np.clip(d-0.45,0,1)**2.4/0.55**2.4)[...,None]   # vignette ~13%
    lumw=1.0+0.6*(1-a.mean(axis=2,keepdims=True)/255); a+=np.random.default_rng(seed).normal(0,5.5,(H,W,1))*lumw    # grain on the whole frame
    return Image.fromarray(np.clip(a,0,255).astype("uint8")),dict(x=x,y=y,w=im.width,h=im.height,cropped=bool(cropped))
