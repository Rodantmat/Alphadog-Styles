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
# 2026-11-20 (owner "do them all", engagement research): v5 = breed-led reel. The breed of the OPENING shot is named in the first-frame hook, the share CTA, the caption (front-loaded) and 3-5 descriptive hashtags; the end dissolves back to frame 0 so a replay loops cleanly (replays + shares + watch-through are the top ranking signals). Rule 9 still holds: the other frames keep their own distinct breeds.
def breed_slug(b): return "".join(ch for ch in b.lower() if ch.isalnum())
HOOKS=["For {b} lovers","Every {b} owner needs this","Calling all {b} owners","{b} people, this is you"]   # 2026-11-22: call-out hooks (Virlo 2026: call-out/bold-claim hooks lead for pet products); picked per video, id stored in meta.json for the 24 h/72 h comparison
def art(b): return 'an' if b[:1].upper() in 'AEIOU' else 'a'                         # 'an English Bulldog' (the on-screen CTA of c39 says 'a English Bulldog' and is already burned in)
def v5_hook_id(vid): return sum(ord(ch) for ch in str(vid))%len(HOOKS)
def v5_texts(b,hid=0):
    h=HOOKS[hid].format(b=b)
    if len(h)>31: h=HOOKS[0].format(b=b)                                                  # chosen hook would overflow the 860 px pill: use the short one ("For <breed> lovers" fitted up to 31 chars before)
    if len(b)>20: return "Your breed is here", "Send this to a dog person"   # long breed names would overflow the 860 px pill
    return h, f"Send this to {art(b)} {b} owner"
def season_gift(today=None):
    import datetime as D; t=today or D.date.today(); return D.date(t.year,11,15)<=t<=D.date(t.year,12,24)   # holiday gifting window (Pinterest holiday guide: gifting searches start early, keep going to Dec 24)
def v5_caption(b,today=None):
    sl=breed_slug(b); g=season_gift(today)
    l2=(f"Gift idea for dog dads and dog moms: {b} line art tees, hoodies, polos and caps, front and back." if g
        else "Dog line art tees, hoodies, polos and caps, front and back.")
    tags=f"#{sl} #doggifts #dogapparel" if g else f"#{sl} #dogtshirt #dogapparel"          # 3 descriptive tags (Mosseri: tags do not add reach; IG caps at 5; Metricool 2026: tagged posts got fewer views) - sources conflict, so 3 not 0
    return (f"{b} lovers, this one is yours. \U0001F43E Send it to {art(b)} {b} owner.\n{l2}\n"
            f"What is your {b}'s name? \U0001F447\nalphadogstyles.com (link in bio)\n{tags}")
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
    y=max(y,448)            # VIDEO_RULES 15: pill (y-18) must sit below row 430, clear of the feed account bar
    y=min(y,1580-sz-26)     # and above row 1580
    d.rounded_rectangle([x-30,y-18,x+w+30,y+sz+26],radius=28,fill=(12,12,14,150)); d.text((x,y),text,font=f,fill=(255,255,255,255),stroke_width=2,stroke_fill=(0,0,0,200))
    return Image.alpha_composite(im,ov).convert("RGB")
def push(PL,A,B): pass
PLN=lambda p,x,y:f"if(eq(PLANE,0),{p}0({x},{y}),if(eq(PLANE,1),{p}1({x},{y}),{p}2({x},{y})))"
EXPR_PUSH="st(1,1-P);st(0,if(lt(ld(1),0.5),4*ld(1)*ld(1)*ld(1),1-pow(-2*ld(1)+2,3)/2));if(lt(X,W*(1-ld(0))),"+PLN("a","X+W*ld(0)","Y")+","+PLN("b","X-W*(1-ld(0))","Y")+")"
def pick_trans(a,b,used,rnd):
    if a["k"]=="person" and b["k"]!="person" and used.get("push",0)<3: return "push",0.8
    if a["k"]!="person" and b["k"]=="person": return "smoothleft",0.8
    # owner rule (2026-11-13 gate): transitions slow, >=0.7 s; no hard cuts
    if abs(a["lum"]-b["lum"])>0.25: return "fadeblack",0.8
    return ("fade",0.8) if rnd.random()<0.5 else ("dissolve",0.8)
N=8; NF=4
BANNED_BREEDS={"Yorkshire Terrier","Pomeranian","Shih Tzu","Havanese","Pug","Mini Poodle","Bichon Frise","Maltese"}  # owner: never in Post B (enforced Nov 12)
def pin_json(b,variant,prods,vid=None):
    # Pinterest = keyword search (docs/WORDING_PLAYBOOK.md 3): title keyword-first, first 40 chars visible; description ~220 chars, <=5 related keywords
    if variant=="v5" and b!="dog":
        t=f"{b} Line Art Hoodie, Tee and Cap, Dog Dad and Dog Mom Gift"[:100]
        d=(f"{b} line art tees, hoodies, polos and caps for {b} lovers: a front print or chest emblem, plus a full-body back print. "
           f"A gift for dog dads, dog moms and every {b} owner. Shop alphadogstyles.com. #{breed_slug(b)} #doggift #dogapparel")[:500]
    else:
        t="Dog Line Art Hoodie, Tee and Cap, Dog Lover Gift"; d="Dog line art tees, hoodies, polos and caps in 33 breeds. A gift for dog dads and dog moms. Shop alphadogstyles.com. #doggift #dogmom #dogdad #dogapparel #doglover"
    url="https://alphadogstyles.com"
    if variant=="v5" and b!="dog": url=f"https://alphadogstyles.com/?utm_source=pinterest&utm_medium=social&utm_campaign={vid or 'pin'}#/design?breed={'_'.join(b.lower().split())}"   # unique URL per pin (Pinterest fresh-pin guidance) that opens the shop on THAT breed; the store reads #/design?breed=<slug>
    return dict(title=t,description=d,url=url)
def build(vid,seed,music,variant="v5"):
    if variant in ("v1","v2","v3","v4") and not os.environ.get("C2_KEEP_VARIANT"): variant="v5"   # 2026-11-20: the generator prompt still passes v2; every Post B is now the breed-led v5 unless C2_KEEP_VARIANT=1 (A/B tests)
    rnd=random.Random(seed); od=f"out/postc/{vid}"; os.makedirs(od,exist_ok=True)
    pool=P1.pool(); cat=BM.Catalog()
    _ok={}
    def okc(p):
        if p["file"] not in _ok: _ok[p["file"]]=not C.edge_bad(C.load(p["file"],kind_of(p)),kind_of(p))
        return _ok[p["file"]]
    pool=[p for p in pool if okc(p)]
    ex=[x for x in os.environ.get("C2_EXCL","").split(",") if x]                     # V9: never reuse a cutout camera or background from these reels
    exc=set(); exb=set()
    for x in ex:
        mm=json.load(open(f"out/postc/{x}/meta.json")); mm=mm["meta"] if isinstance(mm,dict) else mm; exc|={m["cam"] for m in mm}; exb|={m["bg"] for m in mm}
    pool=[p for p in pool if str(p["cam"]) not in exc]
    for x in [y for y in os.environ.get("C2_EXCLBG","").split(",") if y]:             # backgrounds only (60-day rule): reels built in this run are not yet in docs/bg_used.json, so list them here (added 2026-11-21)
        mm=json.load(open(f"out/postc/{x}/meta.json")); mm=mm["meta"] if isinstance(mm,dict) else mm; exb|={m["bg"] for m in mm}
    exb|={y for y in os.environ.get("C2_TAKENBG","").split(",") if y}                # explicit bg files (e.g. the same-day Post A)
    taken0=set(exb)
    nob=set(x for x in os.environ.get("C2_NOBREED","").split(",") if x)               # breeds already shown in other reels
    nob|=BANNED_BREEDS                                                                 # owner rule (runbook/RULES_LEDGER V13): never show these breeds in Post B
    exr=set()                                                                          # people/cameras (raw ids) and breeds of the other reels
    exp=[x for x in os.environ.get("C2_EXCLP",os.environ.get("C2_EXCL","")).split(",") if x]   # window for people + breeds (only 33 breeds / ~40 people exist, so a rolling window of recent reels)
    for x in exp:
        mm=json.load(open(f"out/postc/{x}/meta.json")); mm=mm["meta"] if isinstance(mm,dict) else mm
        exr|={m.get("raw") for m in mm if m.get("raw")}; nob|={m["breed"] for m in mm if m.get("breed")}
    for x in [y for y in os.environ.get("C2_EXCLR","").split(",") if y]:               # people only (wider window than breeds)
        mm=json.load(open(f"out/postc/{x}/meta.json")); mm=mm["meta"] if isinstance(mm,dict) else mm; exr|={m.get("raw") for m in mm if m.get("raw")}
    pool=[p for p in pool if p.get("breed") not in nob and not (p["kind"]=="person" and p.get("raw") in exr)]
    exq=set()                                                                          # V1: never the same product+colour as the previous reel (C2_EXCLC=<previous reel ids>)
    for x in [y for y in os.environ.get("C2_EXCLC","").split(",") if y]:
        mm=json.load(open(f"out/postc/{x}/meta.json")); mm=mm["meta"] if isinstance(mm,dict) else mm; exq|={(m["prod"],m.get("colour")) for m in mm}
    pool=[p for p in pool if (p["prod"],p.get("colour")) not in exq]
    exa=set()                                                                          # VIDEO_RULES 9: art (breed x style x design) never reused within 18 videos (C2_EXCLART=<reel ids>); added 2026-11-21 so the builder can no longer produce art the scheduler blocks
    for x in [y for y in os.environ.get("C2_EXCLART","").split(",") if y]:
        mm=json.load(open(f"out/postc/{x}/meta.json")); mm=mm["meta"] if isinstance(mm,dict) else mm; exa|={(m.get("breed"),m.get("style"),m.get("design")) for m in mm}
    pool=[p for p in pool if (p.get("breed"),p.get("style"),p.get("design")) not in exa]
    nocol=set(x for x in os.environ.get("C2_NOCOL","").split(",") if x)               # colours worn in the same-day / neighbouring Post A (owner V1)
    pool=[p for p in pool if p.get("colour") not in nocol]
    pf=[p for p in pool if p["kind"]=="person" and p["side"]=="front"]; pb=[p for p in pool if p["kind"]=="person" and p["side"]=="back"]
    ub=set(); uc=set(); ur=set()
    def take(cands):                                                                   # distinct breed, colour and person inside the reel
        c=[x for x in cands if x.get("breed") not in ub and x.get("colour") not in uc and x.get("raw",x["cam"]) not in ur] or [x for x in cands if x.get("breed") not in ub]
        x=rnd.choice(c); ub.add(x.get("breed")); uc.add(x.get("colour")); ur.add(x.get("raw",x["cam"])); return x
    ppl=[take(pf),take(pb),take(pf),take(pb)]; flats=[p for p in pool if p["kind"]!="person"]; rnd.shuffle(flats); rest=[]; seen=set()
    for p in flats:
        if p["prod"] in seen and len(seen)<NF: continue
        if p.get("breed") in ub or p.get("colour") in uc: continue
        seen.add(p["prod"]); rest.append(p); ub.add(p.get("breed")); uc.add(p.get("colour"))
        if len(rest)==NF: break
    for p in flats:                                                                    # fallback: relax colour/product spread, never the breed
        if len(rest)==NF: break
        if p not in rest and p.get("breed") not in ub: rest.append(p); ub.add(p.get("breed"))
    fr=[]
    for it in ppl+rest:
        im=k=kind_of(it); im=C.load(it["file"],k); g=C.garment_rgb(im,k)
        fr.append(dict(it=it,k=k,view=it.get("side"),prod=it["prod"],lum=BM.relL(g),rgb=g))
    seq=order(fr,rnd); taken=set(taken0); fams=[]; shots=[]; meta=[]
    if os.environ.get("C2_DRY"):                                                       # selection-only dry run (2026-11-21): print the pick so seeds can be scored before the 3-minute render
        import collections
        cs=[f['it'].get('colour') for f in seq if f['it'].get('colour')!='none']; pr=[f['prod'] for f in seq]
        print("DRY",json.dumps(dict(breeds=[f['it'].get('breed') for f in seq],prods=pr,colours=cs,nprod=len(set(pr)),dupcol=len(cs)-len(set(cs)),art=[(f['it'].get('breed'),f['it'].get('style'),f['it'].get('design')) for f in seq]))); return None
    lead=seq[0]["it"].get("breed") or "dog"
    for i,f in enumerate(seq):
        b=None
        for att in range(3):
            b=cat.pick(f["rgb"],"person" if f["k"]=="person" else f["k"],avoid_fam=fams[-2:],taken=taken,rnd=rnd,only=None if f['k']=='person' else (lambda r:str(BM.family(r)).startswith('texture') or r['file'].startswith('pa_')))
            if b: break
        if not b: raise SystemExit(f"no background for {f['k']} {f['rgb']}")
        taken.add(b["file"]); fams.append(BM.family(b))
        img,pos=C.compose(f["it"]["file"],f["k"],f"out/bg/{b['file']}",seed=seed*100+i)
        if variant=="v5":
            if i==0: img=add_text(img,v5_texts(lead,v5_hook_id(vid))[0],310,66)
            if i==len(seq)-1: img=add_text(img,v5_texts(lead,v5_hook_id(vid))[1],1400,60)
        else:
            if variant!="v0" and i==0: img=add_text(img,HOOKS.get(variant,HOOKS["v1"]),310,66)
            if variant in CTAS and i==len(seq)-1: img=add_text(img,CTAS[variant],1400,60)
        fn=f"{od}/s{i:02d}.png"; img.save(fn); shots.append(fn); meta.append(dict(i=i,prod=f["prod"],cam=f["it"]["cam"],raw=f["it"].get("raw"),breed=f["it"].get("breed"),colour=f["it"].get("colour"),design=f["it"].get("design"),style=f["it"].get("style"),kind=f["k"],bg=b["file"],bgname=b.get("name"),fam=fams[-1],ratio=round(BM.ratio(BM.relL(f["rgb"]),BM.bgL(b)),1)))
    phase,L=beat_grid(music); T_used={}; trs=[pick_trans(seq[i],seq[i+1],T_used,rnd) for i in range(N-1)]
    sT=sum(t for _,t in trs); Ls=[(10.0+sT)/N]*N          # fill to exactly ~10 s
    FPS=30; ins=[]; filt=[]
    LOOP=0.6; shots_all=shots+[shots[0]]; Ls=Ls+[LOOP+0.1]                 # shot N = frame 0 again: the last LOOP s dissolve into the opening frame (clean replay loop)
    for i,fn in enumerate(shots_all):
        fr_n=int((Ls[i]+0.5)*FPS)+2; z0,z1=1.0,1.05
        p=f"(on/{fr_n-1})"; ease=f"({p}*{p}*(3-2*{p}))"; z=f"{z0}+({z1}-{z0})*{ease}"
        ins+=["-i",fn]
        filt.append(f"[{i}:v]scale=2160:3840:flags=lanczos,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr_n}:s=1080x1920:fps={FPS},setsar=1,format=gbrp[v{i}]")
    cur="v0"; off=0.0
    for i in range(1,N+1):
        name,T=(trs[i-1] if i<N else ("fade",LOOP)); off+=Ls[i-1]-T
        if name=="push": filt.append(f"[{cur}][v{i}]xfade=transition=custom:duration={T}:offset={off:.3f}:expr='{EXPR_PUSH}'[x{i}]"); T_used["push"]=T_used.get("push",0)+1
        elif name=="cut": filt.append(f"[{cur}][v{i}]xfade=transition=fade:duration=0.033:offset={off:.3f}[x{i}]")
        else: filt.append(f"[{cur}][v{i}]xfade=transition={name}:duration={T}:offset={off:.3f}[x{i}]")
        cur=f"x{i}"
    total=10.1; ins+=["-ss",f"{phase:.3f}","-i",music]
    filt.append(f"[{N+1}:a]atrim=0:{total:.2f},afade=t=in:d=0.2,afade=t=out:st={total-1.2:.2f}:d=1.2,volume=0.7[a]")
    filt.append(f"[{cur}]format=yuv420p[vout]")
    subprocess.run(["ffmpeg","-y","-v","error"]+ins+["-filter_complex",";".join(filt),"-map","[vout]","-map","[a]","-t","10.1","-c:v","libx264","-preset","medium","-crf","20","-c:a","aac","-b:a","160k","-movflags","+faststart",f"{od}/reel.mp4"],check=True)
    for fn in shots: os.remove(fn)
    cap=open(f"{od}/caption.txt","w"); cap.write(v5_caption(lead) if variant=="v5" else "Which one is yours? Tell us your breed in the comments.\nTees, hoodies, polos and caps with our dog line art, front and back.\nalphadogstyles.com (link in bio)\n#doglover #dogmom #dogdad #alphadogstyles"); cap.close()
    json.dump(pin_json(lead,variant,[m["prod"] for m in meta],vid),open(f"{od}/pin.json","w"),indent=1)
    json.dump(dict(meta=meta,trans=[t for t in trs],beat_phase=phase,shot_len=L,variant=variant,hook_id=v5_hook_id(vid) if variant=="v5" else None),open(f"{od}/meta.json","w"),indent=1); print("lead breed",lead,"BUILT",od,"transitions",[t[0] for t in trs])
    return [m["bg"] for m in meta]
if __name__=="__main__": build(sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4] if len(sys.argv)>4 else "v5")
