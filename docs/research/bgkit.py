import numpy as np
from PIL import Image, ImageFilter, ImageDraw
W,H=1080,1920
rng=np.random.default_rng(7)

def fbm(h,w,octaves=6,base=4,persist=.5,seed=0):
    """multi-octave value noise, 0..1. Core of plaster/concrete/paper/marble."""
    r=np.random.default_rng(seed); out=np.zeros((h,w),np.float32); amp=1; tot=0
    for o in range(octaves):
        n=base*2**o
        g=r.random((n+1,int(n*w/h)+2)).astype(np.float32)
        im=Image.fromarray(g).resize((w,h),Image.BICUBIC)
        out+=amp*np.asarray(im); tot+=amp; amp*=persist
    out/=tot; return (out-out.min())/(out.max()-out.min()+1e-9)

def tint(gray,dark,light):
    d=np.array(dark,np.float32); l=np.array(light,np.float32)
    return d+(l-d)*gray[...,None]

def plaster(dark=(176,164,148),light=(214,204,190),seed=1):
    a=fbm(H,W,6,3,.55,seed); b=fbm(H,W,3,2,.5,seed+9)
    g=.65*a+.35*b                     # cloudy trowel marks
    return tint(g,dark,light)

def concrete(dark=(120,120,118),light=(176,176,172),seed=2,pores=900):
    g=.6*fbm(H,W,7,3,.6,seed)+.4*fbm(H,W,3,2,.5,seed+3)
    im=tint(g,dark,light)
    p=np.zeros((H,W),np.float32); r=np.random.default_rng(seed)
    ys,xs=r.integers(0,H,pores),r.integers(0,W,pores); p[ys,xs]=1
    p=np.asarray(Image.fromarray((p*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6)),np.float32)/255
    return np.clip(im-p[...,None]*90,0,255)   # blown pores

def linen(base=(214,205,188),seed=3,pitch=5):
    y,x=np.mgrid[0:H,0:W]
    warp=.5+.5*np.sin(2*np.pi*x/pitch+fbm(H,W,4,6,.5,seed)*4)
    weft=.5+.5*np.sin(2*np.pi*y/pitch+fbm(H,W,4,6,.5,seed+1)*4)
    slub=fbm(H,W,5,20,.5,seed+2)
    g=.35*warp+.35*weft+.3*slub
    return np.array(base,np.float32)*(0.88+.24*g)[...,None]

def paper(base=(232,226,212),seed=4):
    g=fbm(H,W,5,60,.55,seed)         # fibres: high base freq
    return np.array(base,np.float32)*(0.95+.07*g)[...,None]

def wood(dark=(70,48,32),light=(120,86,58),seed=5):
    y,x=np.mgrid[0:H,0:W].astype(np.float32)
    n=fbm(H,W,5,3,.5,seed)
    rings=.5+.5*np.sin((y*.045+n*18))
    fine=fbm(H,W,6,40,.6,seed+1)
    g=.6*rings+.4*fine
    return tint(g,dark,light)

def marble(base=(236,234,230),vein=(110,112,118),seed=6):
    n=fbm(H,W,6,3,.5,seed); n2=fbm(H,W,6,3,.5,seed+5)
    y,x=np.mgrid[0:H,0:W].astype(np.float32)
    v=np.abs(np.sin((x/W*3+y/H*1.4+n*2.2+n2*1.2)*np.pi))
    v=np.clip(1-v*9,0,1)**2           # thin veins
    cloud=fbm(H,W,4,2,.5,seed+9)
    im=np.array(base,np.float32)*(0.96+.05*cloud)[...,None]
    return im*(1-v[...,None])+np.array(vein,np.float32)*v[...,None]*.9

def terrazzo(base=(226,218,204),chips=((150,120,100),(110,118,108),(190,170,140),(80,80,84)),n=420,seed=7):
    r=np.random.default_rng(seed); im=Image.fromarray(paper(base,seed).astype(np.uint8)); d=ImageDraw.Draw(im)
    for _ in range(n):
        cx,cy=r.integers(0,W),r.integers(0,H); R=r.integers(6,34); k=r.integers(5,9)
        a=np.sort(r.random(k))*2*np.pi; rad=R*(.6+.4*r.random(k))
        d.polygon([(cx+np.cos(t)*q,cy+np.sin(t)*q) for t,q in zip(a,rad)],fill=chips[r.integers(len(chips))])
    return np.asarray(im,np.float32)

def sweep(top=(205,196,183),floor=(176,166,152),horizon=.62,soft=.18,seed=8):
    """seamless studio sweep: wall->floor curve, light pool upper-left"""
    y=np.linspace(0,1,H)[:,None]; t=np.clip((y-(horizon-soft))/(2*soft),0,1); t=t*t*(3-2*t)
    col=np.array(top)*(1-t[...,None])+np.array(floor)*t[...,None]
    col=np.broadcast_to(col,(H,W,3)).copy()
    yy,xx=np.mgrid[0:H,0:W]; pool=np.exp(-(((xx-W*.3)/(W*.9))**2+((yy-H*.3)/(H*.55))**2))
    return col*(0.82+.28*pool[...,None])

def gobo(img,kind='window',angle=-14,strength=.38,blur=26,seed=0):
    """multiply a blurred shadow pattern: window panes / blinds / leaves"""
    m=Image.new('L',(W*2,H*2),255); d=ImageDraw.Draw(m)
    if kind=='window':
        for i in range(2):
            for j in range(3):
                x0=int(W*.25+i*W*.55); y0=int(H*.15+j*H*.42)
                d.rectangle([x0,y0,x0+int(W*.48),y0+int(H*.36)],fill=0)
        # lit panes are 0 => invert later; here lit=white
    elif kind=='blinds':
        for k in range(0,H*2,130): d.rectangle([0,k,W*2,k+70],fill=0)
    elif kind=='leaves':
        r=np.random.default_rng(seed)
        for _ in range(55):
            cx,cy=r.integers(0,W*2),r.integers(0,H*2); a=r.random()*6.28
            L=r.integers(90,260); wd=r.integers(25,60)
            pts=[(cx+np.cos(a)*L*s,cy+np.sin(a)*L*s+np.sin(s*3.14)*wd*c) for s in np.linspace(0,1,12) for c in (1,)]
            pts+=[(cx+np.cos(a)*L*s,cy+np.sin(a)*L*s-np.sin(s*3.14)*wd) for s in np.linspace(1,0,12)]
            d.polygon(pts,fill=0)
    if kind=='window': m=Image.eval(m,lambda v:255-v)  # panes = shadow-free light
    m=m.rotate(angle,resample=Image.BICUBIC,fillcolor=255).resize((W,H)).filter(ImageFilter.GaussianBlur(blur))
    a=np.asarray(m,np.float32)/255
    return img*(1-strength*(1-a))[...,None]

def vignette(img,amt=.14,power=2.4):
    yy,xx=np.mgrid[0:H,0:W]; r=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)/1.414
    return img*(1-amt*np.clip(r,0,1)**power)[...,None]

def grain(img,sigma=6,seed=None,shadow_boost=1.0):
    r=np.random.default_rng(seed)
    n=r.normal(0,sigma,(H,W)).astype(np.float32)
    n=np.asarray(Image.fromarray(np.clip(n*4+128,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.5)),np.float32)
    n=(n-n.mean())/4
    lum=img.mean(2,keepdims=True)/255; w=1+shadow_boost*(1-lum)*.6
    return np.clip(img+n[...,None]*w,0,255)

def shadow_layer(alpha,offset=(8,16),sigma=18,opacity=.3,color=(30,24,20),squash=1.0,base_y=0):
    """alpha: HxW float 0..1 of the cutout placed on canvas. returns RGBA-ish (color, a)"""
    a=Image.fromarray((alpha*255).astype(np.uint8))
    a=a.transform(a.size,Image.AFFINE,(1,0,-offset[0],0,1/squash,base_y-base_y/squash-offset[1]))  # squash about the ground line
    a=a.filter(ImageFilter.GaussianBlur(sigma))
    return np.asarray(a,np.float32)/255*opacity

def composite(bg,cut_rgba,anchor_xy,scale_h,bg_tint=None,light_xy=(-1,-1),
              contact=True,ambient=True,reflect=0.0,shadow_col=None):
    """cut_rgba: PIL RGBA (transparent cutout). anchor_xy=(cx,bottom_y) in canvas px,
    scale_h = target height px. Subject colour is NOT altered except <=6% ambient tint."""
    cw,ch=cut_rgba.size; s=scale_h/ch
    c=cut_rgba.resize((max(1,int(cw*s)),scale_h),Image.LANCZOS)
    arr=np.asarray(c,np.float32); a=arr[...,3]/255
    # defringe: erode alpha 1px then 0.8px feather
    am=Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.8))
    a=np.asarray(am,np.float32)/255
    rgb=arr[...,:3]
    if bg_tint is not None: rgb=rgb*(1-.06)+np.array(bg_tint,np.float32)*.06
    x0=int(anchor_xy[0]-c.size[0]/2); y0=int(anchor_xy[1]-c.size[1])
    full=np.zeros((H,W),np.float32)
    ys0,xs0=max(0,y0),max(0,x0); ys1,xs1=min(H,y0+c.size[1]),min(W,x0+c.size[0])
    full[ys0:ys1,xs0:xs1]=a[ys0-y0:ys1-y0,xs0-x0:xs1-x0]
    out=bg.copy()
    dark=np.array(shadow_col if shadow_col is not None else np.percentile(bg.reshape(-1,3),5,axis=0)*.45,np.float32)
    ox=-light_xy[0]; oy=-light_xy[1]
    if ambient:
        sh=shadow_layer(full,(ox*14,abs(oy)*30),sigma=38,opacity=.28,squash=.35,base_y=anchor_xy[1])
        out=out*(1-sh[...,None])+dark*sh[...,None]
    if reflect>0:
        flip=full[::-1]; fade=np.clip(1-(np.arange(H)[:,None]-anchor_xy[1])/320,0,1)
        # (flat reflection recipe: shift flipped alpha so it starts at bottom_y; omitted for brevity)
    if contact:
        sh=shadow_layer(full,(ox*3,5),sigma=6,opacity=.5,squash=.97,base_y=anchor_xy[1])
        out=out*(1-sh[...,None])+dark*sh[...,None]
    fr=np.zeros((H,W,3),np.float32); fr[ys0:ys1,xs0:xs1]=rgb[ys0-y0:ys1-y0,xs0-x0:xs1-x0]
    out=out*(1-full[...,None])+fr*full[...,None]
    return out

def finish(img,vig=.14,gr=5):
    return Image.fromarray(np.clip(grain(vignette(img,vig),gr),0,255).astype(np.uint8))

def zoom_crop(im,z,dx=0.0,dy=0.0):
    """sub-pixel zoom about canvas centre (+drift dx,dy px) -> W x H frame. im is a PIL image >= W x H.
    Uses AFFINE+BICUBIC (float coords) -> no integer-rounding jitter."""
    w,h=im.size; sx=w/W
    a=1/z*sx; cx=w/2+dx*sx; cy=h/2+dy*sx
    return im.transform((W,H),Image.AFFINE,(a,0,cx-a*W/2,0,a,cy-a*H/2),resample=Image.BICUBIC)

def parallax_frame(bg,sub_layer,fg_layer,t,T=10.0):
    """bg/sub/fg: RGB/RGBA PIL layers at canvas size (bg ideally 1.2x). Subject moves less than fg, more than bg.
    bg 1.00->1.05, subject 1.00->1.025, fg blur elements 1.00->1.12 (my engineering values)."""
    k=t/T; e=k*k*(3-2*k)                         # smoothstep ease
    f=zoom_crop(bg,1+.05*e,dx=-10*e)
    f=f.convert('RGBA'); f.alpha_composite(zoom_crop(sub_layer,1+.025*e,dx=-5*e))
    if fg_layer is not None: f.alpha_composite(zoom_crop(fg_layer,1+.12*e,dx=14*e))
    return f.convert('RGB')
