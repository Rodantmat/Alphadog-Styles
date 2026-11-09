#!/usr/bin/env python3
"""Post B engine: picks each next Post B from the FULL Printify asset catalog (out/mockidx/slim.json.gz) so that consecutive posts share NOTHING.
Dimensions kept apart between neighbours: product, breeds, colours (and tone), design style+sub, placement, photo-style (camera group), format, transitions, music theme, palette, caption template.
usage: postb_engine.py START_ID N [--after prev1,prev2]   writes social/postb/briefs.json (+history in social/postb/history.json) and prints the variety matrix."""
import gzip,json,random,sys,os,collections,re
CAT=None
def cat():
    global CAT
    if CAT is None: CAT=json.load(gzip.open("out/mockidx/slim.json.gz","rt"))
    return CAT
GROUP={"person-1-front":"person","person-2-front":"person","person-front":"person","person-1-back":"person","person-back":"person",
 "front":"flat-front","front-2":"flat-front","back":"flat-back","back-2":"flat-back","folded":"folded","hanging-1":"hanging","front-collar-closeup":"closeup",
 "side":"closeup","left":"closeup","right":"closeup","left-chest":"closeup","right-chest":"closeup","left-sleeve":"closeup"}
FORMATS=["reel_slideshow","carousel","reel_split","reel_grid","reel_flip","reel_hero"]
TRANS=[["fade","smoothleft","circleopen"],["zoomin","fadeblack","smoothup"],["wipeleft","slideright","fadewhite"],["radial","smoothdown","dissolve"],["pixelize","fade","wiperight"],["squeezev","circleclose","slideup"]]
MUSIC=["Hip-hop & Trap","Pop & Party","Funk & Disco","Feel-good","Chill & Lo-fi","Acoustic","Latin","Rock & Indie"]
PAL=["cream","dusk","ink","sage","terracotta","ocean","blush","charcoal"]
ONE_TONE={"Polo","Tank Top","Mesh Trucker Cap","Foam Trucker Hat","Racerback Tank"}
CAP=["story","question","list","benefit","gift","seasonal"]
def tonef(c): 
    return c
def build_index():
    X=collections.defaultdict(list)
    for o in cat():
        if o["prod"]!="Women's Polo": X[o["prod"]].append(o)
    return X
def pick_post(pid,hist,X,rnd):
    last=hist[-1] if hist else {}
    recent=hist[-4:]
    def lru(key,vals,n=None):
        # least-recently-used first, never equal to the previous post's value
        use={v:-1 for v in vals}
        for i,h in enumerate(hist):
            vv=h.get(key); vv=vv if isinstance(vv,list) else [vv]
            for v in vv:
                if v in use: use[v]=i
        ok=[v for v in vals if v not in (last.get(key) if isinstance(last.get(key),list) else [last.get(key)])]
        ok.sort(key=lambda v:(use[v],rnd.random()))
        return ok
    prod=lru("prod",list(X))[0]
    pool=X[prod]
    # colour family differs from last post's tone; colours disjoint from the previous 2 posts
    prevcols={c for h in hist[-2:] for c in h["colours"]}
    prevtone=last.get("tone")
    cols=sorted({o["colour"] for o in pool if o["colour"]})
    tones={o["colour"]:o["tone"] for o in pool if o["colour"]}
    cand=[c for c in cols if c not in prevcols and tones[c]!=prevtone] or [c for c in cols if c not in prevcols] or cols
    rnd.shuffle(cand)
    t0=tones.get(cand[0]) if cand else ""
    same=[c for c in cand if tones.get(c)==t0]
    cand=same[:4] if len(same)>=1 else cand[:4]
    # design/placement: different from last
    ds=sorted({(o["style"],o["sub"]) for o in pool if o["style"]!="Other"})
    d_ok=[d for d in ds if d!=tuple(last.get("design",[]))]; 
    d_ok.sort(key=lambda d:(max([i for i,h in enumerate(hist) if tuple(h.get("design",[]))==d] or [-1]),rnd.random()))
    design=d_ok[0] if d_ok else ds[0]
    pls=sorted({o["place"] for o in pool if o["place"]})
    place=(lru("place",pls) or pls or [""])[0] if pls else ""
    cams=collections.Counter(GROUP.get(o["cam"],"other") for o in pool)
    groups=[g for g in cams if g!="other"]
    grp=lru("grp",groups)[0] if groups else "flat-front"
    # breeds: not in last 20 posts' breeds, up to 6, different from last post
    usedb=collections.Counter(b for h in hist[-8:] for b in h["breeds"])
    allb=sorted({o["breed"] for o in pool})
    lastb=set(last.get("breeds",[]))
    bl=sorted([b for b in allb if b not in lastb],key=lambda b:(usedb[b],rnd.random()))
    nimg=6
    # choose assets: for each of nimg distinct breeds pick one asset matching design/place/colour/group
    chosen=[];used=set()
    for b in bl:
        if len(chosen)>=nimg: break
        m=[o for o in pool if o["breed"]==b and (o["style"],o["sub"])==design and (not place or o["place"]==place or o["place"]=="") and GROUP.get(o["cam"])==grp and (o["colour"] in cand or not o["colour"])]
        if not m: m=[o for o in pool if o["breed"]==b and (o["style"],o["sub"])==design and GROUP.get(o["cam"])==grp and (o["colour"] in cand or not o["colour"])]
        if not m: m=[o for o in pool if o["breed"]==b and GROUP.get(o["cam"])==grp and (o["colour"] in cand or not o["colour"])]
        if not m: m=[o for o in pool if o["breed"]==b and GROUP.get(o["cam"])==grp]
        if not m: continue
        o=rnd.choice(m)
        if o["src"] in used: continue
        used.add(o["src"]); chosen.append(o)
    fmt=lru("format",FORMATS)[0]; tr=lru("trans",list(range(len(TRANS))))[0]; mu=lru("music",MUSIC)[0]; pal=lru("pal",PAL)[0]; cp=lru("cap",CAP)[0]
    ctone=collections.Counter(o["tone"] for o in chosen).most_common(1)[0][0] if chosen else ""
    return dict(id=pid,prod=prod,breeds=[o["breed"] for o in chosen],colours=sorted({o["colour"] for o in chosen if o["colour"]}),tone=ctone,design=list(design),place=place,grp=grp,format=fmt,trans=tr,music=mu,pal=pal,cap=cp,assets=[{k:o[k] for k in("src","breed","colour","cam","pid")} for o in chosen])
def neighbour_ok(a,b):
    bad=[]
    for k in ("prod","grp","format","trans","music","pal","cap"):
        if a.get(k)==b.get(k): bad.append(k)
    if set(a["breeds"])&set(b["breeds"]): bad.append("breeds")
    if set(a["colours"])&set(b["colours"]): bad.append("colours")
    if a["design"]==b["design"]: bad.append("design")
    if a["place"] and a["place"]==b["place"]: bad.append("place")
    if a["tone"]==b["tone"] and a["tone"] and a["prod"] not in ONE_TONE and b["prod"] not in ONE_TONE: bad.append("tone")
    return bad
def main():
    start=sys.argv[1]; n=int(sys.argv[2]); X=build_index(); rnd=random.Random(20261109)
    hf="social/postb/history.json"; hist=json.load(open(hf)) if os.path.exists(hf) else []
    num=int(re.sub(r"\D","",start)); out=[]
    while len(out)<n:
        pid=f"b{num+len(out):02d}"; best=None
        for _ in range(60):
            p=pick_post(pid,hist+out,X,random.Random(rnd.random()))
            if len(p["assets"])<4: continue
            if best is None: best=p
            bad=neighbour_ok(hist[-1],p) if (hist or out) and (out or hist) and not out else (neighbour_ok(out[-1],p) if out else [])
            if not bad: best=p;break
        out.append(best)
    json.dump(out,open("social/postb/briefs.json","w"),indent=1)
    print("id   prod              grp        format        design            place                     tone   breeds / colours")
    prev=hist[-1] if hist else None
    for p in out:
        bad=neighbour_ok(prev,p) if prev else []
        print(f"{p['id']} {p['prod'][:16]:16} {p['grp']:10} {p['format']:13} {'/'.join(p['design']):17} {p['place'][:24]:24} {p['tone']:6} {','.join(b[:10] for b in p['breeds'])} | {','.join(p['colours'])}  {'CLASH:'+','.join(bad) if bad else ''}")
        prev=p
if __name__=="__main__": main()
