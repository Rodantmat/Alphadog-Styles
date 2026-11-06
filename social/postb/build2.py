#!/usr/bin/env python3
"""Post B v2: FULL-SCREEN Printify mockups (people wearing, views) -> 1080x1920 Reels (varied elegant transitions + music) and 1080x1350 carousels.
plan2.json: {id:{kind,music,title,images:[path],texts:[str],caption}}"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FB="/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"; FR="/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf"; FS="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
LOGO="store/logo.png"
TR=["fade","smoothleft","fadeblack","zoomin","smoothup","fade","fadewhite","circleopen","smoothright"]
def fullscreen(path,W,H):
    im=Image.open(path).convert("RGB"); w,h=im.size
    edge=np.array(im.crop((0,h-6,w,h))).astype("float32")
    if edge.mean(axis=2).std()>22:  # busy edge (person/studio): true full-bleed cover crop
        s=H/h; im2=im.resize((int(w*s),H),Image.LANCZOS); L=(im2.width-W)//2
        return im2.crop((L,0,L+W,H)), 0, H
    s=W/w; im2=im.resize((W,int(h*s)),Image.LANCZOS)
    top=np.array(im2.crop((0,0,W,6))).mean(axis=(0,1)); bot=np.array(im2.crop((0,im2.height-6,W,im2.height))).mean(axis=(0,1))
    can=Image.new("RGB",(W,H)); a=np.zeros((H,W,3),dtype="float32")
    y0=(H-im2.height)//2
    for y in range(H):
        t=y/(H-1); a[y,:,:]=top*(1-t)+bot*t
    can=Image.fromarray(a.astype("uint8")); can.paste(im2,(0,y0))
    # soften the seams
    m=Image.new("L",(W,H),0); ImageDraw.Draw(m).rectangle([0,y0+40,W,y0+im2.height-40],fill=255); m=m.filter(ImageFilter.GaussianBlur(30))
    base=Image.fromarray(a.astype("uint8")); base.paste(im2,(0,y0)); 
    return Image.composite(can,base,m) if False else can, y0, im2.height
def lum(img,box):
    return np.array(img.crop(box).convert("L")).mean()
def dress(can,y0,ih,title,sub,W,H,i):
    if y0==0 and ih==H:  # full-bleed photo: bottom shade, light text at bottom only
        g=np.array(can).astype("float32"); n=420
        for k in range(n): g[H-n+k]*=1-0.62*(k/n)**1.4
        can=Image.fromarray(g.astype("uint8")); d=ImageDraw.Draw(can); wh=(250,248,242)
        if os.path.exists(LOGO):
            lg=Image.open(LOGO).convert("RGBA"); lg.thumbnail((84,84)); can.paste(lg,(W-84-40,56),lg)
        t=(title if i==0 and title else sub)
        if t:
            f=ImageFont.truetype(FS if i==0 and title else FR,56 if i==0 and title else 38); w=d.textlength(t,font=f); d.text(((W-w)/2,H-200),t,font=f,fill=wh)
        f3=ImageFont.truetype(FB,30); s_="ALPHADOG STYLES"; w=d.textlength(s_,font=f3); d.text(((W-w)/2,H-96),s_,font=f3,fill=wh)
        return can
    d=ImageDraw.Draw(can)
    topc=lum(can,(0,0,W,200)); botc=lum(can,(0,H-260,W,H)); 
    ink=lambda l:(24,24,28) if l>140 else (248,246,240)
    if os.path.exists(LOGO):
        lg=Image.open(LOGO).convert("RGBA"); lg.thumbnail((84,84)); can.paste(lg,(W-84-40,56),lg)
    f=ImageFont.truetype(FS,52); 
    if title:
        w=d.textlength(title,font=f); d.text(((W-w)/2,y0-110 if y0>150 else 70),title,font=f,fill=ink(topc))
    if sub:
        f2=ImageFont.truetype(FR,34); w=d.textlength(sub,font=f2); d.text(((W-w)/2,y0+ih+40 if H-(y0+ih)>200 else H-170),sub,font=f2,fill=ink(botc))
    f3=ImageFont.truetype(FB,30); s="ALPHADOG STYLES"; w=d.textlength(s,font=f3); d.text(((W-w)/2,H-86),s,font=f3,fill=ink(botc))
    return can
def build(pid,p):
    od=f"out/postb2/{pid}"; os.makedirs(od,exist_ok=True); imgs=p["images"]; txt=[""]*len(imgs)  # no per-frame labels
    if p["kind"]=="carousel":
        W,H=1080,1350
        for i,f in enumerate(imgs):
            im=Image.open(f).convert("RGB"); w,h=im.size; s=max(W/w,H/h); im=im.resize((int(w*s),int(h*s)),Image.LANCZOS)
            L=(im.width-W)//2; im=im.crop((L,(im.height-H)//2,L+W,(im.height-H)//2+H))
            g=np.array(im).astype("float32")
            for k in range(280): g[H-280+k]*=1-0.6*(k/280)**1.4
            im=Image.fromarray(g.astype("uint8")); d=ImageDraw.Draw(im)
            if os.path.exists(LOGO):
                lg=Image.open(LOGO).convert("RGBA"); lg.thumbnail((76,76)); im.paste(lg,(W-76-32,36),lg)
            if txt[i]:
                f2=ImageFont.truetype(FS,46); w2=d.textlength(txt[i],font=f2); d.text(((W-w2)/2,H-110),txt[i],font=f2,fill=(250,248,242))
            im.save(f"{od}/slide{i+1:02d}.jpg",quality=93)
    else:
        W,H=1080,1920; fr=[]
        for i,f in enumerate(imgs):
            can,y0,ih=fullscreen(f,W,H); can=can.filter(ImageFilter.UnsharpMask(2,60,2)); can=dress(can,y0,ih,p.get("title") if i==0 else "",txt[i],W,H,i); fn=f"{od}/f{i:02d}.png"; can.save(fn); fr.append(fn)
        D=[1.85]*len(fr); X=0.7; ins=[]; filt=[]
        for i,f in enumerate(fr):
            ins+=["-loop","1","-t",f"{D[i]+X}","-i",f]
            z="min(zoom+0.0005,1.07)" if i%2==0 else "if(eq(on,1),1.07,max(zoom-0.0005,1.0))"
            filt.append(f"[{i}:v]scale=1700:3022:flags=lanczos,zoompan=z='{z}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,setsar=1,unsharp=5:5:0.7:3:3:0.0,eq=contrast=1.05:saturation=1.1,format=yuv420p[v{i}]")
        cur="v0"; t=0
        for i in range(1,len(fr)):
            t+=D[i-1]-0.0; filt.append(f"[{cur}][v{i}]xfade=transition={TR[(i-1)%len(TR)]}:duration={X}:offset={t-X*(i-0)+X*(i-1) if False else t-(i)*0:.2f}[x{i}]"); cur=f"x{i}"
        total=sum(D)+X
        ins+=["-ss","0","-i",f"out/music2/{p['music']}"]
        filt.append(f"[{len(fr)}:a]atrim=0:{total:.2f},afade=t=in:d=0.6,afade=t=out:st={total-1.4:.2f}:d=1.4,volume=0.6[a]")
        subprocess.run(["ffmpeg","-y","-v","error"]+ins+["-filter_complex",";".join(filt),"-map",f"[{cur}]","-map","[a]","-t",f"{total:.2f}","-c:v","libx264","-preset","veryfast","-crf","15","-c:a","aac","-b:a","160k","-movflags","+faststart",f"{od}/reel.mp4"],check=True)
        for f in fr: os.remove(f)
    open(f"{od}/caption.txt","w").write(p["caption"]); print("BUILT",pid,p["kind"])
if __name__=="__main__":
    plan=json.load(open("social/postb/plan2.json"))
    for k in (sys.argv[1:] or plan): build(k,plan[k])
