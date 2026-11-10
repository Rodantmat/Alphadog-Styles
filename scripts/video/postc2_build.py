#!/usr/bin/env python3
"""Post B 'C2' builder: real-photo backgrounds (bgmatch) + compose2 + ordering + beat-synced cuts/transitions (docs/research/12) + hook/CTA text variants (docs/WORDING_PLAYBOOK.md).
usage: postc2_build.py ID SEED MUSIC.mp3 [VARIANT v0|v1|v2|v3|v4]   -> out/postc/ID/{reel.mp4,caption.txt,meta.json}
Needs out/bg (jpgs from bg-fetch release zips) and out/bgcat/catalog_*.json, out/trans (transparent cutouts)."""
import sys,os,json,random,subprocess,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,"scripts/video"); sys.path.insert(0,"social/postb")
import compose2 as C, bgmatch as BM, postc_build as P1
import postb_build as PB
W,H=1080,1920
HOOKS={"v1":"Which breed is yours?","v2":"Find your breed","v3":"POV: your dog has merch","v4":"Find your dog's shirt"}
CTAS={"v2":"Send this to a dog person","v3":"Save for your next gift","v4":"Tag your dog's biggest fan"}
def kind_of(it):
    k=it["kind"]; return "person" if k=="person" else ("folded" if k=="folded" else "flat")
def order(frames,rnd,tries=300):
    def cost(a,b):
        c=3.0*(a["k"]==b["k"])+2.0*(a["view"]==b["view"])+2.0*(a["prod"]==b["prod"])*1.5+2.0*(1-min(1,abs(a["lum"]-b["lum"])/0.35))
        return c
    best=None
    for _ in range(tries):
        pool=frames[:]; rnd.shuffle(pool); seq=[pool.pop(0)]
        while pool:
            ok=[f for f in pool if f["prod"]!=seq[-1]["prod"] and not(len(seq)>=2 and seq[-1]["k"]==f["k"]==seq[-2]["k"])] or pool
            ok.sort(key=lambda f:cost(seq[-1],f)+rnd.uniform(0,0.8)); n=ok[0]; seq.append(n); pool.remove(n)
        c=sum(cost(a,b) for a,b in zip(seq,seq[1:]))
        c+=sum(2.0 for i,f in enumerate(seq) if (f["k"]=="person")!=(i%2==0))          # P O P O rhythm
        if seq[0]["k"]=="folded": c+=5
        if seq[-1]["k"]!="flat": c+=4                                                    # clean flat last (CTA space)
        if best is None or c<best[0]: best=(c,seq)
    return best[1]
def beat_grid(music,target=1.0):
    import librosa
    y,sr=librosa.load(music,sr=22050,mono=True,duration=60); o=librosa.onset.onset_strength(y=y,sr=sr); t=float(librosa.feature.tempo(onset_envelope=o,sr=sr)[0])
    while t<80: t*=2
    while t>160: t/=2
    _,b=librosa.beat.beat_track(onset_envelope=o,sr=sr,units="time",tightness=100); ib=60/t
    if len(b)<6: return 0.0,1.0
    phase=float(np.median(np.array(b)%ib)); k=max(1,round(target/ib)); return phase,ib*k
def font(sz): return ImageFont.truetype(PB.FB,sz)
def add_text(img,text,y,sz=64):
    im=img.convert("RGBA"); ov=Image.new("RGBA",im.size,(0,0,0,0)); d=ImageDraw.Draw(ov); f=font(sz)
    while d.textlength(text,font=f)>W-220 and sz>40: sz-=2; f=font(sz)
    w=d.textlength(text,font=f); x=(W-w)/2
    d.rounded_rectangle([x-30,y-18,x+w+30,y+sz+26],radius=28,fill=(12,12,14,150)); d.text((x,y),text,font=f,fill=(255,255,255,255),stroke_width=2,stroke_fill=(0,0,0,200))
    return Image.alpha_composite(im,ov).convert("RGB")
def push(PL,A,B): pass
PLN=lambda p,x,y:f"if(eq(PLANE,0),{p}0({x},{y}),if(eq(PLANE,1),{p}1({x},{y}),{p}2({x},{y})))"
EXPR_PUSH="st(1,1-P);st(0,if(lt(ld(1),0.5),4*ld(1)*ld(1)*ld(1),1-pow(-2*ld(1)+2,3)/2));if(lt(X,W*(1-ld(0))),"+PLN("a","X+W*ld(0)","Y")+","+PLN("b","X-W*(1-ld(0))","Y")+")"
def pick_trans(a,b,used,rnd):
    if a["k"]=="person" and b["k"]!="person" and used.get("push",0)<3: return "push",0.8
    if a["k"]!="person" and b["k"]=="person": return "smoothleft",0.8
    if abs(a["lum"]-b["lum"])>0.25: return "cut",0.033
    return ("fade",0.7) if rnd.random()<0.5 else ("cut",0.033)
N=8; NF=4
def build(vid,seed,music,variant="v0"):
    rnd=random.Random(seed); od=f"out/postc/{vid}"; os.makedirs(od,exist_ok=True)
    pool=P1.pool(); cat=BM.Catalog()
    _ok={}
    def okc(p):
        if p["file"] not in _ok: _ok[p["file"]]=not C.edge_bad(C.load(p["file"]),kind_of(p))
        return _ok[p["file"]]
    pool=[p for p in pool if okc(p)]
    pf=[p for p in pool if p["kind"]=="person" and p["side"]=="front"]; pb=[p for p in pool if p["kind"]=="person" and p["side"]=="back"]
    ppl=rnd.sample(pf,2)+rnd.sample(pb,2); flats=[p for p in pool if p["kind"]!="person"]; rnd.shuffle(flats); rest=[]; seen=set()
    for p in flats:
        if p["prod"] in seen and len(seen)<NF: continue
        seen.add(p["prod"]); rest.append(p)
        if len(rest)==NF: break
    fr=[]
    for it in ppl+rest:
        im=C.load(it["file"]); k=kind_of(it); g=C.garment_rgb(im,k)
        fr.append(dict(it=it,k=k,view=it.get("side"),prod=it["prod"],lum=BM.relL(g),rgb=g))
    seq=order(fr,rnd); taken=set(); fams=[]; shots=[]; meta=[]
    for i,f in enumerate(seq):
        b=None
        for att in range(3):
            b=cat.pick(f["rgb"],"person" if f["k"]=="person" else f["k"],avoid_fam=fams[-2:],taken=taken,rnd=rnd,only=None if f['k']=='person' else (lambda r:str(BM.family(r)).startswith('texture') or r['file'].startswith('pa_')))
            if b: break
        if not b: raise SystemExit(f"no background for {f['k']} {f['rgb']}")
        taken.add(b["file"]); fams.append(BM.family(b))
        img,pos=C.compose(f["it"]["file"],f["k"],f"out/bg/{b['file']}",seed=seed*100+i)
        if variant!="v0" and i==0: img=add_text(img,HOOKS.get(variant,HOOKS["v1"]),310,66)
        if variant in CTAS and i==len(seq)-1: img=add_text(img,CTAS[variant],1400,60)
        fn=f"{od}/s{i:02d}.png"; img.save(fn); shots.append(fn); meta.append(dict(i=i,prod=f["prod"],cam=f["it"]["cam"],kind=f["k"],bg=b["file"],bgname=b.get("name"),fam=fams[-1],ratio=round(BM.ratio(BM.relL(f["rgb"]),BM.bgL(b)),1)))
    phase,L=beat_grid(music); T_used={}; trs=[pick_trans(seq[i],seq[i+1],T_used,rnd) for i in range(N-1)]
    sT=sum(t for _,t in trs); Ls=[(10.0+sT)/N]*N          # fill to exactly ~10 s
    FPS=30; ins=[]; filt=[]
    for i,fn in enumerate(shots):
        fr_n=int((Ls[i]+0.5)*FPS)+2; z0,z1=1.0,1.05
        p=f"(on/{fr_n-1})"; ease=f"({p}*{p}*(3-2*{p}))"; z=f"{z0}+({z1}-{z0})*{ease}"
        ins+=["-i",fn]
        filt.append(f"[{i}:v]scale=2160:3840:flags=lanczos,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr_n}:s=1080x1920:fps={FPS},setsar=1,format=gbrp[v{i}]")
    cur="v0"; off=0.0
    for i in range(1,N):
        name,T=trs[i-1]; off+=Ls[i-1]-T
        if name=="push": filt.append(f"[{cur}][v{i}]xfade=transition=custom:duration={T}:offset={off:.3f}:expr='{EXPR_PUSH}'[x{i}]"); T_used["push"]=T_used.get("push",0)+1
        elif name=="cut": filt.append(f"[{cur}][v{i}]xfade=transition=fade:duration=0.033:offset={off:.3f}[x{i}]")
        else: filt.append(f"[{cur}][v{i}]xfade=transition={name}:duration={T}:offset={off:.3f}[x{i}]")
        cur=f"x{i}"
    total=10.0; ins+=["-ss",f"{phase:.3f}","-i",music]
    filt.append(f"[{N}:a]atrim=0:{total:.2f},afade=t=in:d=0.2,afade=t=out:st={total-1.2:.2f}:d=1.2,volume=0.7[a]")
    filt.append(f"[{cur}]format=yuv420p[vout]")
    subprocess.run(["ffmpeg","-y","-v","error"]+ins+["-filter_complex",";".join(filt),"-map","[vout]","-map","[a]","-t","10","-c:v","libx264","-preset","medium","-crf","20","-c:a","aac","-b:a","160k","-movflags","+faststart",f"{od}/reel.mp4"],check=True)
    for fn in shots: os.remove(fn)
    cap=open(f"{od}/caption.txt","w"); cap.write("Which one is yours? Tell us your breed in the comments.\nTees, hoodies, polos and caps with our dog line art, front and back.\nalphadogstyles.com (link in bio)\n#doglover #dogmom #dogdad #alphadogstyles"); cap.close()
    json.dump(dict(meta=meta,trans=[t for t in trs],beat_phase=phase,shot_len=L,variant=variant),open(f"{od}/meta.json","w"),indent=1); print("BUILT",od,"transitions",[t[0] for t in trs])
    return [m["bg"] for m in meta]
if __name__=="__main__": build(sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4] if len(sys.argv)>4 else "v0")
