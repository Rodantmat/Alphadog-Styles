#!/usr/bin/env python3
"""Post B v2: FULL-SCREEN Printify mockups (people wearing, views) -> 1080x1920 Reels (varied elegant transitions + music) and 1080x1350 carousels.
plan2.json: {id:{kind,music,title,images:[path],texts:[str],caption}}"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FB="/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"; FR="/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf"; FS="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
LOGO="store/logo.png"
TR=["fade","smoothleft","dissolve","fadewhite","smoothright","fade","circleopen","dissolve"]
def fullscreen(path,W,H):
    im=Image.open(path).convert("RGB"); w,h=im.size
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
    od=f"out/postb2/{pid}"; os.makedirs(od,exist_ok=True); imgs=p["images"]; txt=p.get("texts") or [""]*len(imgs)
    if p["kind"]=="carousel":
        W,H=1080,1350
        for i,f in enumerate(imgs):
            im=Image.open(f).convert("RGB"); w,h=im.size; s=max(W/w,H/h); im=im.resize((int(w*s),int(h*s)),Image.LANCZOS)
            L=(im.width-W)//2; im=im.crop((L,(im.height-H)//2,L+W,(im.height-H)//2+H))
            d=ImageDraw.Draw(im)
            if os.path.exists(LOGO):
                lg=Image.open(LOGO).convert("RGBA"); lg.thumbnail((76,76)); im.paste(lg,(W-76-32,36),lg)
            if txt[i]:
                f2=ImageFont.truetype(FS,46); w2=d.textlength(txt[i],font=f2); d.text(((W-w2)/2,H-110),txt[i],font=f2,fill=(24,24,28) if lum(im,(0,H-140,W,H))>140 else (248,246,240))
            im.save(f"{od}/slide{i+1:02d}.jpg",quality=93)
    else:
        W,H=1080,1920; fr=[]
        for i,f in enumerate(imgs):
            can,y0,ih=fullscreen(f,W,H); can=dress(can,y0,ih,p.get("title") if i==0 else "",txt[i],W,H,i); fn=f"{od}/f{i:02d}.png"; can.save(fn); fr.append(fn)
        D=[1.7]*len(fr); X=0.5; ins=[]; filt=[]
        for i,f in enumerate(fr):
            ins+=["-loop","1","-t",f"{D[i]+X}","-i",f]
            z="min(zoom+0.0006,1.06)" if i%2==0 else "if(eq(on,1),1.06,max(zoom-0.0006,1.0))"
            filt.append(f"[{i}:v]scale=1188:2112,zoompan=z='{z}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,setsar=1,format=yuv420p[v{i}]")
        cur="v0"; t=0
        for i in range(1,len(fr)):
            t+=D[i-1]-0.0; filt.append(f"[{cur}][v{i}]xfade=transition={TR[(i-1)%len(TR)]}:duration={X}:offset={t-X*(i-0)+X*(i-1) if False else t-(i)*0:.2f}[x{i}]"); cur=f"x{i}"
        total=sum(D)+X
        ins+=["-ss","0","-i",f"out/music2/{p['music']}"]
        filt.append(f"[{len(fr)}:a]atrim=0:{total:.2f},afade=t=in:d=0.6,afade=t=out:st={total-1.4:.2f}:d=1.4,volume=0.6[a]")
        subprocess.run(["ffmpeg","-y","-v","error"]+ins+["-filter_complex",";".join(filt),"-map",f"[{cur}]","-map","[a]","-t",f"{total:.2f}","-c:v","libx264","-preset","veryfast","-crf","19","-c:a","aac","-b:a","160k","-movflags","+faststart",f"{od}/reel.mp4"],check=True)
        for f in fr: os.remove(f)
    open(f"{od}/caption.txt","w").write(p["caption"]); print("BUILT",pid,p["kind"])
if __name__=="__main__":
    plan=json.load(open("social/postb/plan2.json"))
    for k in (sys.argv[1:] or plan): build(k,plan[k])
