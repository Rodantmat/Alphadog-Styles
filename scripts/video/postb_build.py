#!/usr/bin/env python3
"""Build Post B from social/postb/briefs.json + out/pmk3/<id>/NN.jpg  ->  out/postb3/<id>/{reel.mp4|slideNN.jpg, caption.txt}
Formats: reel_slideshow reel_hero reel_flip reel_split reel_grid carousel.  usage: postb_build.py ID [ID...]   (music file via env MUSIC_<ID> or brief['music_file'])"""
import json,os,subprocess,sys,random
sys.path.insert(0,"social/postb")
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import build2 as B2
TRS=[["fade","smoothleft","circleopen"],["zoomin","fadeblack","smoothup"],["wipeleft","slideright","fadewhite"],["radial","smoothdown","dissolve"],["pixelize","fade","wiperight"],["squeezev","circleclose","slideup"]]
FB,FR,FS=B2.FB,B2.FR,B2.FS
def cover(im,W,H):
    w,h=im.size; s=max(W/w,H/h); im=im.resize((int(w*s)+1,int(h*s)+1),Image.LANCZOS); L=(im.width-W)//2; T=(im.height-H)//2; return im.crop((L,T,L+W,T+H))
def tile(path,W,H):
    im=Image.open(path).convert("RGB"); w,h=im.size
    edge=np.array(im.crop((0,h-6,w,h))).astype("float32")
    if edge.mean(axis=2).std()>22: return cover(im,W,H)          # busy photo: true cover
    a=np.array(im).astype("int16"); bgc=np.median(np.concatenate([a[:4,:4].reshape(-1,3),a[:4,-4:].reshape(-1,3),a[-4:,:4].reshape(-1,3),a[-4:,-4:].reshape(-1,3)]),axis=0)
    m=(np.abs(a-bgc).max(axis=2)>22)
    if m.sum()>200:
        ys,xs=np.where(m); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max(); mx=int((x1-x0)*0.06)+4; my=int((y1-y0)*0.06)+4
        im=im.crop((max(0,x0-mx),max(0,y0-my),min(w,x1+mx),min(h,y1+my))); w,h=im.size
    s=min(W*0.96/w,(H-300)/h); im2=im.resize((max(1,int(w*s)),max(1,int(h*s))),Image.LANCZOS)
    top=np.array(im.resize((W,H)).crop((0,0,W,4))).mean(axis=(0,1)); bot=np.array(im.resize((W,H)).crop((0,H-4,W,H))).mean(axis=(0,1))
    a=np.zeros((H,W,3),"float32")
    for y in range(H): t=y/(H-1); a[y]=top*(1-t)+bot*t
    can=Image.fromarray(a.astype("uint8")); can.paste(im2,((W-im2.width)//2,max(0,(H-300-im2.height)//2+30))); return can
def brand(can,title=None,W=1080,H=1920):
    d=ImageDraw.Draw(can)
    if os.path.exists(B2.LOGO):
        lg=Image.open(B2.LOGO).convert("RGBA"); lg.thumbnail((84,84)); can.paste(lg,(W-84-40,56),lg)
    g=np.array(can).astype("float32"); n=300
    for k in range(n): g[H-n+k]*=1-0.72*(k/n)**1.3
    can=Image.fromarray(g.astype("uint8")); d=ImageDraw.Draw(can)
    if title:
        sz=52
        while sz>30 and d.textlength(title,font=ImageFont.truetype(FS,sz))>W-120: sz-=2
        f=ImageFont.truetype(FS,sz); w=d.textlength(title,font=f); d.text(((W-w)/2,H-210),title,font=f,fill=(250,248,242))
    f3=ImageFont.truetype(FB,28); s="ALPHADOG STYLES"; w=d.textlength(s,font=f3); d.text(((W-w)/2,H-92),s,font=f3,fill=(250,248,242)); return can
def frames_for(p,od,files):
    W,H=1080,1920; fmt=p["format"]; out=[]
    title=p.get("title") or f"{p['prod']} · {p['design'][0]} {p['design'][1]}".replace("Tee A","Tee").replace("Tee B","Tee")
    if fmt in("reel_slideshow","reel_hero","reel_flip","reel_rhythm"):
        use=files[:3] if fmt=="reel_hero" else files
        for i,f in enumerate(use):
            can=brand(cover(Image.open(f).convert("RGB"),W,H) if False else tile(f,W,H),title if i==0 else None); fn=f"{od}/f{i:02d}.png"; can.save(fn); out.append(fn)
    elif fmt=="reel_split":
        for k in range(0,len(files)-1,2):
            top=tile(files[k],W,H//2); bot=tile(files[k+1],W,H//2); can=Image.new("RGB",(W,H)); can.paste(top,(0,0)); can.paste(bot,(0,H//2))
            ImageDraw.Draw(can).rectangle([0,H//2-3,W,H//2+3],fill=(250,248,242)); can=brand(can,title if k==0 else None); fn=f"{od}/f{k//2:02d}.png"; can.save(fn); out.append(fn)
    elif fmt=="reel_grid":
        n=min(6,len(files)); tw,th=W//2,(H-300)//3
        for s_ in range(1,n+1):
            can=Image.new("RGB",(W,H),(18,18,20))
            for j in range(s_):
                t=tile(files[j],tw-8,th-8); can.paste(t,((j%2)*tw+4,150+(j//2)*th+4))
            can=brand(can,title if s_==n else None); fn=f"{od}/f{s_-1:02d}.png"; can.save(fn); out.append(fn)
    return out
def ffmpeg_reel(p,od,fr,music):
    fmt=p["format"]; tr=TRS[p["trans"]%len(TRS)]
    D={"reel_rhythm":1.5,"reel_slideshow":1.9,"reel_hero":3.0,"reel_flip":0.75,"reel_split":2.5,"reel_grid":1.1}[fmt]; X={"reel_rhythm":0.4,"reel_slideshow":0.7,"reel_hero":0.9,"reel_flip":0.12,"reel_split":0.6,"reel_grid":0.25}[fmt]
    ins=[];filt=[]; DU=p.get('durs') if fmt=='reel_rhythm' and p.get('durs') else [D]*len(fr)
    for i,f in enumerate(fr):
        ins+=["-framerate","30","-loop","1","-t",f"{DU[i]+X}","-i",f]; D=DU[i]
        zmax={"reel_hero":0.18,"reel_flip":0.10}.get(fmt,0.07); step=zmax/(D*30)
        z=f"min(zoom+{step:.5f},{1+zmax})" if i%2==0 else f"if(eq(on,1),{1+zmax},max(zoom-{step:.5f},1.0))"
        if fmt in("reel_split","reel_grid"): z="1.0"
        filt.append(f"[{i}:v]scale=1700:3022:flags=lanczos,zoompan=z='{z}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,setsar=1,format=yuv420p[v{i}]")
    cur="v0";t=0
    for i in range(1,len(fr)):
        t+=DU[i-1]; filt.append(f"[{cur}][v{i}]xfade=transition={tr[(i-1)%3]}:duration={X}:offset={t:.2f}[x{i}]"); cur=f"x{i}"
    total=sum(DU)+X
    ins+=["-ss","0","-i",music]; filt.append(f"[{len(fr)}:a]atrim=0:{total:.2f},afade=t=in:d=0.6,afade=t=out:st={total-1.4:.2f}:d=1.4,volume=0.6[a]")
    subprocess.run(["ffmpeg","-y","-v","error"]+ins+["-filter_complex",";".join(filt),"-map",f"[{cur}]","-map","[a]","-t",f"{total:.2f}","-c:v","libx264","-preset","veryfast","-crf","16","-c:a","aac","-b:a","160k","-movflags","+faststart",f"{od}/reel.mp4"],check=True)
CAP={
"story":"{lead}\n{body}\nShop the full collection at alphadogstyles.com (link in bio)\n{tags}",
"question":"Which one is yours? {body}\nTell us your breed in the comments.\nalphadogstyles.com (link in bio)\n{tags}",
"list":"{body}\nSwipe through the details.\nalphadogstyles.com (link in bio)\n{tags}",
"benefit":"{lead} {body} Made on demand, designed for dog people.\nalphadogstyles.com (link in bio)\n{tags}",
"gift":"The easiest gift for a dog person: {body}\nalphadogstyles.com (link in bio)\n{tags}",
"seasonal":"{lead} {body}\nalphadogstyles.com (link in bio)\n{tags}"}
def caption(p):
    br=", ".join(p["breeds"][:-1])+" and "+p["breeds"][-1] if len(p["breeds"])>1 else p["breeds"][0]
    prod={"Tee A":"tee","Tee B":"tee"}.get(p["prod"],p["prod"].lower())
    lead={"Hoodie":"Cozy season.","Dad Hat":"Finish the look.","Polo":"Smart, with a tail.","Tank Top":"Warm-weather ready.","Racerback Tank":"Warm-weather ready.","Mesh Trucker Cap":"Cap season.","Foam Trucker Hat":"Cap season."}.get(p["prod"],"New in the shop.")
    if p["prod"]=="Mix": br=", ".join(p["breeds"][:4])+" and "+p["breeds"][4]; body=f"Tees, hoodies, polos and caps for {br} lovers (and 5 more breeds inside)."; lead="Front or back?"
    else: body=f"{p['design'][0]} {p['design'][1]} {prod}: {br}."
    tags="#doglover #dogmom #dogdad #alphadogstyles "+" ".join("#"+b.lower().replace(" ","") for b in p["breeds"][:5])
    return CAP[p["cap"]].format(lead=lead,body=body,tags=tags)
def build(p):
    od=f"out/postb3/{p['id']}"; os.makedirs(od,exist_ok=True); src=f"out/pmk3/{p['id']}"
    files=[f"{src}/{i:02d}.jpg" for i in range(len(p["assets"])) if os.path.exists(f"{src}/{i:02d}.jpg")]
    if len(files)<4: print("SKIP",p["id"],"assets",len(files)); return
    if p["format"]=="carousel":
        W,H=1080,1350
        for i,f in enumerate(files):
            im=tile(f,W,H); d=ImageDraw.Draw(im)
            if os.path.exists(B2.LOGO):
                lg=Image.open(B2.LOGO).convert("RGBA"); lg.thumbnail((76,76)); im.paste(lg,(W-76-32,36),lg)
            im.save(f"{od}/slide{i+1:02d}.jpg",quality=93)
    else:
        fr=frames_for(p,od,files); m=p.get("music_file") or os.environ.get("MUSIC_"+p["id"]) or "out/music2/m00.mp3"
        ffmpeg_reel(p,od,fr,m)
        for f in fr: os.remove(f)
    open(f"{od}/caption.txt","w").write(caption(p)); print("BUILT",p["id"],p["format"],p["prod"])
if __name__=="__main__":
    B=json.load(open("social/postb/briefs.json")); ids=sys.argv[1:] or [p["id"] for p in B]
    for p in B:
        if p["id"] in ids: build(p)
