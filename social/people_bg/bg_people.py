#!/usr/bin/env python3
"""300 people-friendly 1080x1920 backgrounds (bg_p_001..300): 30 structural families x 10 palettes/variants.
Built for bottom-anchored person cut-outs and flat garments: calm centre, interesting edges, floor/horizon hidden behind the subject,
light/mid/dark tags for garment contrast. usage: bg_people.py [OUTDIR]  -> OUTDIR/bg_p_NNN_<family>.jpg + docs/backgrounds_people_catalog.json"""
import numpy as np, json, os, sys, math, random
from PIL import Image, ImageFilter, ImageDraw
W,H=1080,1920
yy,xx=np.mgrid[0:H,0:W].astype("float32"); Y=yy/H; X=xx/W
def hx(s): return np.array([int(s[i:i+2],16) for i in (0,2,4)],"float32")
def lerp(a,b,t): return a+(b-a)*t[...,None]
def vgrad(a,b,t0=0,t1=1): return lerp(hx(a),hx(b),np.clip((Y-t0)/(t1-t0),0,1))
def noise(rng,sc,amp):
    if not hasattr(rng,"normal"): rng=np.random.default_rng(rng.randrange(1<<30))
    n=rng.random((H//sc+2,W//sc+2)).astype("float32"); im=Image.fromarray((n*255).astype("uint8")).resize((W,H),Image.BICUBIC); return (np.array(im,"float32")/255-.5)*amp
def grain(img,rng,a=5):
    if not hasattr(rng,"normal"): rng=np.random.default_rng(rng.randrange(1<<30))
    return img+rng.normal(0,a,(H,W,1)).astype("float32")
def vign(img,s=.30): d=np.sqrt((X-.5)**2*1.2+(Y-.55)**2); return img*(1-s*np.clip(d-.28,0,1)[...,None]*1.6)
def blur(img,r): return np.array(Image.fromarray(np.clip(img,0,255).astype("uint8")).filter(ImageFilter.GaussianBlur(r)),"float32")
def draw(fn,base):
    im=Image.fromarray(np.clip(base,0,255).astype("uint8")); d=ImageDraw.Draw(im,"RGBA"); fn(d); return np.array(im,"float32")
P=[ # (light/mid/dark, [c1..c5]) curated
("light",["f5efe6","e8d9c5","d9c2a7","fbf7f0","c9b08f"]),("light",["eef3f7","d6e2ee","bcd0e4","f8fbfd","9db8d3"]),("light",["f7eaea","efd0d0","e3b0b0","fdf6f6","d48f8f"]),("light",["eef5ee","d3e5d3","b4d0b4","f7fbf7","8fb88f"]),
("light",["fdf3dc","f8e0a6","f2c96b","fffaf0","e9aa3c"]),("light",["f1ecf7","ddd0ee","c3aee0","faf7fd","a78bd0"]),("light",["f3f0ed","dcd6d0","c4bcb4","fbfaf9","a89f95"]),("light",["e9f6f5","c8e8e5","9fd4cf","f6fcfb","6fb9b2"]),
("mid",["c9a27e","a9825d","8a6747","e1c3a1","6b4e35"]),("mid",["7fa3b8","5f869d","476d84","a5c3d4","325669"]),("mid",["b5838d","9a6670","7e4d58","d4a5ae","613a44"]),("mid",["8fae8d","6f9370","557856","b0c9ae","3f5e40"]),
("mid",["d98e5f","c2703f","a85a2f","eaae85","85431f"]),("mid",["9b8fc4","7d70ad","625494","bdb3dc","483b78"]),("mid",["c4a35a","a8863d","8c6c2a","dbc283","6e5319"]),("mid",["6fa8a0","4f8d85","38746c","95c4bd","255a53"]),
("dark",["1b2a41","324a6b","0c1424","4d6a94","060b14"]),("dark",["2b1b2e","4a2d4f","170d19","6e4575","0b060c"]),("dark",["1c2b24","2f4a3e","0f1a15","4b7461","070d0a"]),("dark",["2e2418","4d3c27","1a140c","7a6140","0d0a06"]),
("dark",["301414","542424","1a0a0a","824040","0c0404"]),("dark",["1a1f2e","2e3652","0e111a","4a5785","06080c"]),("dark",["222222","3a3a3a","101010","5a5a5a","080808"]),("dark",["12303a","1e5260","081a20","2f7d90","040e11"]),
("mid",["e08e9b","c96f7e","ad5565","f1b2bc","8c3e4d"]),("mid",["5b8db8","3f72a0","2c5882","86b0d4","1c3f63"]),("light",["fff1e6","ffdcc2","ffc79e","fffaf5","ffae78"]),("light",["f0f4e8","dde8c8","c5d8a4","f9fbf4","a9c27d"]),
("dark",["2a1a3d","4a2f6b","160c24","7a55a8","0a0512"]),("mid",["d7b98e","bf9a68","a37b48","ebd6b5","7e5c30"]),
]
def rp(rng,tone=None):
    c=[(t,p) for t,p in P if tone is None or t==tone]; t,p=rng.choice(c); p=[hx(x) for x in p]; rng.shuffle(p); return t,p
def F_seamless(r,p,tone): b=lerp(p[0],p[3],Y); b=b*(1-.0)+0; floor=np.clip((Y-.80)/.2,0,1); b=lerp(b,p[2]*.9,floor*.5); b=vign(b,.35); return b
def F_wallfloor(r,p,tone): y0=r.uniform(.72,.84); wall=lerp(p[0],p[3],Y/y0); floor=lerp(p[2],p[4],np.clip((Y-y0)/(1-y0),0,1)); m=(Y>y0)[...,None]; b=np.where(m,floor,wall); sh=np.clip(1-abs(Y-y0)*40,0,1)[...,None]*.15; return vign(b*(1-sh),.3)
def F_spot(r,p,tone): d=np.sqrt((X-.5)**2*1.4+(Y-.45)**2); t=np.clip(d/.75,0,1); return lerp(p[3],p[4],t**.9)
def F_arch(r,p,tone):
    b=vgrad("%02x%02x%02x"%tuple(p[0].astype(int)),"%02x%02x%02x"%tuple(p[2].astype(int))); im=Image.fromarray(b.astype("uint8")); d=ImageDraw.Draw(im,"RGBA"); c=tuple(p[3].astype(int))+(235,)
    d.rounded_rectangle([140,260,W-140,H+200],radius=420,fill=c); d.rounded_rectangle([140,260,W-140,H+200],radius=420,outline=tuple(p[4].astype(int))+(160,),width=10); return vign(np.array(im,"float32"),.25)
def F_blocks(r,p,tone):
    b=np.zeros((H,W,3),"float32"); n=r.randint(3,5); cuts=sorted([0]+[r.random() for _ in range(n-1)]+[1])
    for i in range(n): m=((X>=cuts[i])&(X<cuts[i+1])); b[m]=p[i%len(p)]*(0.92+0.1*(Y[m])[...,None]) if False else p[i%len(p)]
    return vign(b+noise(r,160,14)[...,None],.2)
def F_diag(r,p,tone): t=np.clip((X*.55+Y*.45-r.uniform(.35,.65))*1.0,-1,1); m=(t>0)[...,None]; return vign(np.where(m,lerp(p[0],p[3],Y),lerp(p[2],p[4],Y)),.3)
def F_bokeh(r,p,tone):
    b=lerp(p[2],p[4],Y)
    def f(d):
        for _ in range(r.randint(35,60)):
            x,y,rad=r.randint(-50,W+50),r.randint(0,H),r.randint(40,150); c=tuple(r.choice(p).astype(int))+(r.randint(40,110),); d.ellipse([x-rad,y-rad,x+rad,y+rad],fill=c)
    o=draw(f,b); return blur(o,14)
def F_sunset(r,p,tone): b=vgrad("%02x%02x%02x"%tuple(p[4].astype(int)),"%02x%02x%02x"%tuple(p[0].astype(int)),0,.85); d=np.sqrt((X-.5)**2+(Y-.6)**2*.8); b=b+np.clip(.35-d,0,1)[...,None]*hx("ffe8b0")*.7; hill=(Y>.78+.04*np.sin(X*6+r.random()*6))[...,None]; return vign(np.where(hill,p[2]*.5,b),.25)
def F_foliage(r,p,tone):
    b=lerp(p[1],p[2],Y)
    def f(d):
        for _ in range(110): x,y=r.randint(-80,W+80),r.randint(-80,H+80); rad=r.randint(60,220); c=tuple((r.choice(p)).astype(int))+(r.randint(60,150),); d.ellipse([x-rad,y-rad,x+rad*.8,y+rad],fill=c)
    return blur(draw(f,b),24)
def F_brick(r,p,tone):
    b=np.zeros((H,W,3),"float32")+p[1]; bh,bw=60,150
    def f(d):
        for row in range(H//bh+1):
            off=(row%2)*bw//2
            for col in range(-1,W//bw+2):
                x=col*bw+off; c=p[r.randrange(len(p))]*(.9+r.random()*.2); d.rectangle([x+3,row*bh+3,x+bw-3,row*bh+bh-3],fill=tuple(np.clip(c,0,255).astype(int))+(255,))
    o=draw(f,b); return vign(blur(o,1.2)*(1-.12*np.clip(Y-.7,0,1)[...,None]),.3)
def F_slats(r,p,tone):
    n=r.randint(14,26); w=W/n; b=np.zeros((H,W,3),"float32")
    for i in range(n):
        m=(X*W>=i*w)&(X*W<(i+1)*w); c=p[r.randrange(len(p))]; b[m]=c*(.92+.16*r.random())
    b=b*(1-.25*(((X*W)%w)/w<.06)[...,None]); return vign(b+noise(r,3,10)[...,None],.3)
def F_tile(r,p,tone):
    s=r.choice([90,120,160]); b=np.zeros((H,W,3),"float32")+p[3]; gx=((xx%s)<4)|((yy%s)<4); b[gx]=p[2]*.85
    cb=(((xx//s).astype(int)+(yy//s).astype(int))%2==0); b[cb&~gx]=p[0]; return vign(blur(b,.8),.3)
def F_concrete(r,p,tone): b=lerp(p[0],p[2],Y)+noise(r,40,18)[...,None]+noise(r,6,10)[...,None]; return vign(grain(b,r,4),.35)
def F_curtain(r,p,tone): f=r.uniform(14,26); t=.5+.5*np.sin(X*f*math.pi*2+np.sin(Y*3)*.5); b=lerp(p[2],p[0],t)*(1-.25*Y[...,None]*0); return vign(b,.3)
def F_blinds(r,p,tone):
    b=lerp(p[0],p[3],Y); ang=r.uniform(.25,.5); s=r.randint(50,90); m=(((xx*ang+yy)%s)<s*.45)
    o=b.copy(); o[m]=b[m]*0.82; o=blur(o,3); return vign(o,.25)
def F_plaster(r,p,tone): b=lerp(p[0],p[3],X*.5+Y*.5)+noise(r,30,16)[...,None]; sh=blur(np.dstack([np.clip(1-abs(Y-.14)*30,0,1)*60]*3),20); return vign(b-sh*.5,.3)
def F_neon(r,p,tone):
    b=np.zeros((H,W,3),"float32")+p[4]*.6; im=Image.fromarray(b.astype("uint8")); d=ImageDraw.Draw(im); c=tuple(p[r.randrange(3)].astype(int)); 
    for k in range(3): d.rounded_rectangle([90+k*14,170+k*14,W-90-k*14,H-170-k*14],radius=60,outline=c,width=8)
    g=np.array(im.filter(ImageFilter.GaussianBlur(18)),"float32"); s=np.array(im,"float32"); return vign(np.maximum(s,g*1.6)*.9+b*.2,.35)
def F_circles(r,p,tone):
    b=np.zeros((H,W,3),"float32")+p[0]
    def f(d):
        for _ in range(r.randint(4,7)): x,y,rad=r.randint(-100,W+100),r.randint(100,H-100),r.randint(200,520); c=tuple(r.choice(p[1:]).astype(int))+(r.randint(110,220),); d.ellipse([x-rad,y-rad,x+rad,y+rad],fill=c)
    return vign(draw(f,b),.2)
def F_sea(r,p,tone): hz=r.uniform(.40,.52); sky=vgrad("%02x%02x%02x"%tuple(p[3].astype(int)),"%02x%02x%02x"%tuple(p[0].astype(int)),0,hz); sea=lerp(p[2],p[4],np.clip((Y-hz)/(1-hz),0,1)); m=(Y>hz)[...,None]; b=np.where(m,sea+ (np.sin(Y*140+X*8)*5)[...,None],sky); return vign(b,.25)
def F_city(r,p,tone):
    b=vgrad("%02x%02x%02x"%tuple(p[0].astype(int)),"%02x%02x%02x"%tuple(p[2].astype(int)))
    def f(d):
        x=-20
        while x<W: w=r.randint(70,170); h=r.randint(260,820); c=tuple((p[4]*(.35+.4*r.random())).astype(int))+(255,); d.rectangle([x,H-h-250,x+w,H],fill=c); x+=w+r.randint(0,20)
    return vign(draw(f,b),.3)
def F_mount(r,p,tone):
    b=vgrad("%02x%02x%02x"%tuple(p[3].astype(int)),"%02x%02x%02x"%tuple(p[0].astype(int)),0,.8)
    def f(d):
        for k,l in enumerate([.58,.68,.78]):
            pts=[(0,H)]; 
            for i in range(0,W+90,90): pts.append((i,int(H*(l+.07*math.sin(i/170+k*2+r.random()))-r.randint(0,80))))
            pts.append((W,H)); d.polygon(pts,fill=tuple((p[(k+1)%5]*(.55+.15*k)).astype(int))+(255,))
    return vign(draw(f,b),.25)
def F_confetti(r,p,tone):
    b=lerp(p[3],p[0],Y)
    def f(d):
        for _ in range(260): x,y=r.randint(0,W),r.randint(0,H); s=r.randint(8,26); c=tuple(r.choice(p).astype(int))+(r.randint(120,220),); d.rectangle([x,y,x+s,y+s//2],fill=c)
    return blur(draw(f,b),1.2)
def F_stars(r,p,tone):
    b=vgrad("%02x%02x%02x"%tuple((p[2]*.5).astype(int)),"%02x%02x%02x"%tuple((p[4]*.5+30).astype(int)))
    def f(d):
        for _ in range(240): x,y=r.randint(0,W),r.randint(0,int(H*.85)); s=r.choice([2,2,3,4]); d.ellipse([x,y,x+s,y+s],fill=(255,255,255,r.randint(110,255)))
    return vign(draw(f,b),.3)
def F_sunpaper(r,p,tone): b=np.zeros((H,W,3),"float32")+p[0]+noise(r,3,8)[...,None]; d=np.sqrt((X-r.uniform(.3,.7))**2+(Y-r.uniform(.2,.4))**2); m=(d<.2)[...,None]; return vign(np.where(m,p[1],b),.2)
def F_mist(r,p,tone): b=lerp(p[3],p[1],Y)+noise(r,200,40)[...,None]+noise(r,60,14)[...,None]; return vign(b,.25)
def F_stage(r,p,tone): b=np.where((Y>.74)[...,None],lerp(p[2],p[4],np.clip((Y-.74)/.26,0,1)),lerp(p[0],p[3],Y)); d=np.sqrt((X-.5)**2*1.1+(Y-.55)**2); return vign(b+np.clip(.45-d,0,1)[...,None]*60,.45)
def F_terrazzo(r,p,tone):
    b=np.zeros((H,W,3),"float32")+p[3]
    def f(d):
        for _ in range(900): x,y=r.randint(0,W),r.randint(0,H); a=r.randint(6,22); c=tuple(r.choice(p).astype(int))+(255,); d.polygon([(x,y),(x+a,y+r.randint(0,a)),(x+r.randint(0,a),y+a)],fill=c)
    return vign(blur(draw(f,b),.8),.25)
def F_rays(r,p,tone): ang=np.arctan2(Y-.9,X-.5); n=r.randint(10,18); t=(np.sin(ang*n)>0)[...,None]; return vign(np.where(t,lerp(p[0],p[3],Y),lerp(p[2],p[0],Y)),.35)
def F_waves(r,p,tone): t=.5+.5*np.sin(Y*r.uniform(10,18)+np.sin(X*5+r.random()*6)*1.6); return vign(lerp(p[1],p[3],t),.3)
def F_dapple(r,p,tone):
    b=lerp(p[0],p[3],Y); m=blur(draw(lambda d:[d.ellipse([x-rd,y-rd*1.5,x+rd,y+rd*1.5],fill=(0,0,0,70)) for x,y,rd in [(r.randint(-50,W),r.randint(-50,H),r.randint(60,200)) for _ in range(40)]],np.zeros((H,W,3),"float32")),30)
    return vign(b*(1-(m.mean(axis=2,keepdims=True)/255)*1.0),.25)
FAM=[("seamless",F_seamless),("wallfloor",F_wallfloor),("spot",F_spot),("arch",F_arch),("blocks",F_blocks),("diag",F_diag),("bokeh",F_bokeh),("sunset",F_sunset),("foliage",F_foliage),("brick",F_brick),
("slats",F_slats),("tile",F_tile),("concrete",F_concrete),("curtain",F_curtain),("blinds",F_blinds),("plaster",F_plaster),("neon",F_neon),("circles",F_circles),("sea",F_sea),("city",F_city),
("mount",F_mount),("confetti",F_confetti),("stars",F_stars),("sunpaper",F_sunpaper),("mist",F_mist),("stage",F_stage),("terrazzo",F_terrazzo),("rays",F_rays),("waves",F_waves),("dapple",F_dapple)]
TONES=["light","light","light","mid","mid","mid","dark","dark","mid","light"]  # per variant: ensures tone spread
def main(out="out/bg_people"):
    os.makedirs(out,exist_ok=True); cat=[]; n=0
    for fi,(name,fn) in enumerate(FAM):
        for v in range(10):
            n+=1; r=random.Random(7000+fi*37+v); tone_want=TONES[(v+fi)%10]
            if name in("stars","neon") : tone_want="dark"
            if name in("confetti","sunpaper","blocks"): tone_want=r.choice(["light","mid"])
            tone,p=rp(r,tone_want); rn=np.random.default_rng(900+n)
            img=fn(r,p,tone); img=grain(img,rn,3.5); img=np.clip(img,0,255)
            Image.fromarray(img.astype("uint8")).save(f"{out}/bg_p_{n:03d}_{name}.jpg",quality=90)
            sm=img[::40,::40]; cat.append({"id":n,"file":f"bg_p_{n:03d}_{name}.jpg","family":name,"tone":tone,"mean_lum":round(float(sm.mean()),1),"centre_lum":round(float(img[600:1500,250:830].mean()),1),"palette":" ".join("%02x%02x%02x"%tuple(c.astype(int)) for c in p[:5])})
    json.dump(cat,open("docs/backgrounds_people_catalog.json","w"),indent=0); print(n,"backgrounds")
if __name__=="__main__": main(*(sys.argv[1:2]))
