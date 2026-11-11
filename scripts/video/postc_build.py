#!/usr/bin/env python3
"""Post B 'C-format': Printify transparent cutouts (scripts/video/ptrans.py technique) composed on the people backgrounds (bg_p_001..300).
usage: postc_build.py ID SEED [MUSIC.mp3]  -> out/postc/ID/{reel.mp4,caption.txt,meta.json}
Rules: 10 frames, one image per frame, 4 different people (2 front/2 back), rest flats/folded of different product types; person cut-outs bottom-anchored;
bg tone chosen for contrast with the garment; each frame a different bg family; text never over merch (title top, brand bottom, small)."""
import json,os,sys,random,glob,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
sys.path.insert(0,"scripts/video"); sys.path.insert(0,"social/postb")
import postb_build as PB, build2 as B2
W,H=1080,1920
DIRS={"Hoodie":"Hoodie","Tee B":"Tee_B","Tee A":"Tee_A","Mesh Trucker Cap":"Mesh","Foam Trucker Hat":"Foam","Polo":"Polo","Dad Hat":"Dad"}
SUB={"Hoodie":"Hoodie","Tee B":"Tee_B","Tee A":"Tee_A","Mesh Trucker Cap":"Mesh_Trucker_Cap","Foam Trucker Hat":"Foam_Trucker_Hat","Polo":"Polo","Dad Hat":"Dad_Hat"}
BLOCK=json.load(open('docs/cutout_blocklist.json'))
def pool():
    M=json.load(open("docs/printify_cameras.json")); out=[]
    for prod,cams in M.items():
        if prod not in DIRS: continue
        for c,m in cams.items():
            if m["kind"] not in("person","flat_front","flat_back","flat_side","folded"): continue
            f=f"out/trans/{DIRS[prod]}/{SUB[prod]}/{c}.png"
            if c in BLOCK: continue
            if os.path.exists(f): out.append(dict(prod=prod,cam=c,kind=m["kind"],side=m.get("side"),file=f))
    ix="out/trans2/index.json"                                                      # multi-breed/colour library (docs/trans2_plan.json); replaces the one-bulldog pool when present
    if os.path.exists(ix):
        out=[]
        for r in json.load(open(ix)):
            if r["file"] in BLOCK or not os.path.exists(r["file"]): continue
            out.append(dict(prod=r["prod"],cam=f"{r['cam']}@{r['pid'][:8]}_{r['colour']}",raw=r["cam"],kind=r["kind"],side=r.get("side"),file=r["file"],breed=r["breed"],colour=r["colour"],design=r["design"],style=r["style"],tone=r["tone"]))
    return out
def load(f):
    im=Image.open(f).convert("RGBA"); a=np.array(im)[:,:,3]; ys,xs=np.where(a>6)
    im=im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1)); return im
def lum(im):
    a=np.array(im).astype("float32"); m=a[:,:,3]>200; return float(a[m][:,:3].mean()) if m.any() else 128
def compose(item,bg,title=None):
    im=load(item["file"]); w,h=im.size; k=item["kind"]; can=Image.open(bg).convert("RGB").resize((W,H)).convert("RGBA")
    if k=="person":
        s=min(1500/h,1020/w); im=im.resize((int(w*s),int(h*s)),Image.LANCZOS); x=(W-im.width)//2; y=H-im.height-70
    else:
        lim=(900,1000) if k!="folded" else (820,760); s=min(lim[0]/w,lim[1]/h); im=im.resize((int(w*s),int(h*s)),Image.LANCZOS); x=(W-im.width)//2; y=int(H*0.50-im.height/2)
        sh=Image.new("RGBA",(W,H),(0,0,0,0)); a=im.split()[3].point(lambda v:int(v*0.35)); blk=Image.new("RGBA",im.size,(0,0,0,255)); blk.putalpha(a); sh.paste(blk,(x+10,y+34),blk); sh=sh.filter(ImageFilter.GaussianBlur(22)); can=Image.alpha_composite(can,sh)
    can.alpha_composite(im,(x,y)); can=can.convert("RGB"); d=ImageDraw.Draw(can)
    if os.path.exists(B2.LOGO):
        lg=Image.open(B2.LOGO).convert("RGBA"); lg.thumbnail((84,84)); can.paste(lg,(W-84-40,56),lg)
    dark=np.array(can.crop((0,H-110,W,H))).mean()<110; col=(250,248,242) if dark else (30,30,34)
    f3=ImageFont.truetype(PB.FB,26); s_="ALPHADOG STYLES"; d.text(((W-d.textlength(s_,font=f3))/2,H-62),s_,font=f3,fill=col)
    if title:
        topdark=np.array(can.crop((0,70,W,190))).mean()<110; c2=(250,248,242) if topdark else (30,30,34); f=ImageFont.truetype(PB.FS,50); d.text(((W-d.textlength(title,font=f))/2,92),title,font=f,fill=c2)
    return can
def main():
    vid,seed=sys.argv[1],int(sys.argv[2]); music=sys.argv[3] if len(sys.argv)>3 else "out/music2/m00.mp3"; r=random.Random(seed)
    P=pool(); cat=json.load(open("docs/backgrounds_people_catalog.json"))
    pf=[p for p in P if p["kind"]=="person" and p["side"]=="front"]; pb=[p for p in P if p["kind"]=="person" and p["side"]=="back"]
    ppl=r.sample(pf,2)+r.sample(pb,2); r.shuffle(ppl)
    flats=[p for p in P if p["kind"]!="person"]; used=set(); prods=[]; rest=[]
    r.shuffle(flats)
    for p in flats:
        if p["prod"] in prods and len(prods)<7: continue
        rest.append(p); prods.append(p["prod"])
        if len(rest)==6: break
    seq=[ppl[0],rest[0],rest[1],ppl[1],rest[2],rest[3],ppl[2],rest[4],rest[5],ppl[3]]
    usedfam=set(); od=f"out/postc/{vid}"; os.makedirs(od,exist_ok=True); frames=[]; meta=[]; last=None
    titles={0:"Find your breed"}
    for i,it in enumerate(seq):
        L=lum(load(it["file"])); want="light" if L<110 else ("dark" if L>200 else r.choice(["mid","dark","light"]))
        if L>=110 and L<=200: want=r.choice(["mid","dark"])
        cands=[c for c in cat if c["tone"]==want and c["family"] not in usedfam and c["family"] not in("brick","neon") ]
        if not cands: cands=[c for c in cat if c["family"] not in usedfam]
        c=r.choice(cands); usedfam.add(c["family"])
        can=compose(it,f"out/bg_people/{c['file']}",titles.get(i)); fn=f"{od}/f{i:02d}.png"; can.save(fn); frames.append(fn); meta.append(dict(i=i,prod=it["prod"],cam=it["cam"],kind=it["kind"],bg=c["file"]))
    p={"format":"reel_rhythm","trans":seed%6,"durs":[0.95]*10}
    PB.ffmpeg_reel(p,od,frames,music)
    for f in frames: os.rename(f,f.replace(".png","_frame.png")) if i==99 else None
    json.dump(meta,open(f"{od}/meta.json","w"),indent=1)
    open(f"{od}/caption.txt","w").write("Which one is yours? Tees, hoodies, polos and caps with our dog line art, front and back.\nTell us your breed in the comments.\nalphadogstyles.com (link in bio)\n#doglover #dogmom #dogdad #dogapparel #alphadogstyles")
    print("BUILT",od)
if __name__=="__main__": main()
