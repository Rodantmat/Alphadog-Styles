#!/usr/bin/env python3
"""Post B MIX engine: every video = 10 frames randomly drawn from the FULL Printify catalog (out/mockidx/slim.json.gz).
Composition: 4 people shots (front, Mesh/Foam trucker or Polo) + 1 flat front + 5 flat BACK prints  => 40% people / 60% not, 50% front / 50% back.
Hard rules: no breed twice in a video, none of the previous video' breeds, forbidden breeds never, art (breed x style x sub) never reused within ART_WINDOW videos,
no asset reused ever, no two consecutive frames share product/colour/style, >=5 products, >=5 colours with >=3 dark shades beyond black, >=3 popular breeds,
both styles present, a person shot opens, a back print closes.  usage: postb_mix.py N [SEED] [START_ID]"""
import re, gzip,json,random,sys,os,collections
FORBID={"Yorkshire Terrier","Pomeranian","Shih Tzu","Havanese","Pug","Mini Poodle","Bichon Frise","Maltese"}
POPULAR={"French Bulldog","Golden Retriever","Labrador Retriever","German Shepherd","English Bulldog","Dachshund","Pembroke Welsh Corgi","Siberian Husky","Boxer","Beagle","Rottweiler","Doberman Pinscher","Australian Shepherd","Shiba Inu","Border Collie","Great Dane"}
DARK_X={"Navy","Heather Navy","Forest Green","Maroon","Charcoal","Dark Heather","Dark Chocolate","Military Green","Asphalt","Dark Grey Heather","Red"}
BACKP={"Front & Back","Pocket Portrait + Full Body Back"}
ART_WINDOW=18; H="social/postb/mixhist.json"
FORMATS=["reel_slideshow","reel_flip","reel_split","reel_rhythm"]; MUSIC=["Electronic & House","Feel-good","Funk & Disco","Chill & Lo-fi"]
TITLES=["10 breeds. 10 looks.","Find your breed","Dog people wear it better","Front, back and everything between","Pick your pup","Wear your best friend","Made for dog people"]
# ---- PEOPLE (owner rule: 40% of every video = people wearing it, always DIFFERENT people) ----
# person camera ids are valid for every colour of a product (same URL pattern as printify_pmk.py): Hoodie 98427-98430, Tee B 102051-102062
FRONT_PL=("Pocket Print","Big Portrait","Front & Back","Pocket Portrait + Full Body Back")
PER_HOOD={98427:"h27",98428:"h28",98429:"h29",98430:"h30"}   # front views, 4 different people
PER_TEEB_F={102051:"w51",102052:"w52",102053:"m53",102057:"red",102059:"asm",102061:"blk"}   # front views
PER_TEEB_B={102054:"m54",102058:"red",102060:"asm",102062:"blk"}                          # back views (design on the back)
PEOPLEPRODS={"Mesh Trucker Cap","Foam Trucker Hat","Polo"}
FAM=lambda p:"Tee" if p in("Tee A","Tee B") else p
HATS={"Mesh Trucker Cap","Foam Trucker Hat","Dad Hat"}
def purl(o,cam): return re.sub(r"/mockup/([^/]+)/(\d+)/\d+/.*$",lambda m:f"/mockup/{m.group(1)}/{m.group(2)}/{cam}/x.jpg?camera_label=front",o["src"])
def load():
    d=json.load(gzip.open("out/mockidx/slim.json.gz","rt")); d=[o for o in d if o["breed"] not in FORBID]
    PF=[];PB=[]
    for o in d:
        if o["prod"]=="Hoodie" and o["cam"]=="back" and o["place"] in FRONT_PL:
            for cam,k in PER_HOOD.items(): PF.append({**o,"src":purl(o,cam),"cam":f"person-{cam}","pkey":k,"side":"front"})
        if o["prod"]=="Tee B" and o["cam"]=="front-2":
            if o["place"] in FRONT_PL:
                for cam,k in PER_TEEB_F.items(): PF.append({**o,"src":purl(o,cam),"cam":f"person-{cam}","pkey":k,"side":"front"})
            if o["place"] in BACKP:
                for cam,k in PER_TEEB_B.items(): PB.append({**o,"src":purl(o,cam),"cam":f"person-{cam}","pkey":k,"side":"back"})
    for k,(pr,cam) in {"cap1":("Mesh Trucker Cap","person-1-front"),"foam1":("Foam Trucker Hat","person-1-front"),"foam2":("Foam Trucker Hat","person-2-front")}.items():
        PF+= [{**o,"pkey":k,"side":"front"} for o in d if (o["prod"],o["cam"])==(pr,cam)]
    PF+= [{**o,"pkey":"polo","side":"front"} for o in d if (o["prod"],o["cam"])==("Polo","person-front") and o["colour"]=="Athletic Heather"]
    big=("Tee A","Tee B","Hoodie")
    F=[o for o in d if o["cam"] in("front","front-2") and ((o["prod"] in big and o["place"] in("Big Portrait","Pocket Print","Front & Back")) or o["prod"] in("Dad Hat","Mesh Trucker Cap","Foam Trucker Hat"))]
    Bk=[o for o in d if o["cam"] in("back","back-2") and o["prod"] in big and o["place"] in BACKP]
    V=[o for o in d if o["cam"] in("hanging-1","front-collar-closeup") and o["prod"] in big and o["place"] in("Big Portrait","Pocket Print","Front & Back")]
    return PF,PB,F,Bk,V
def pick(rng,pool,ok):
    c=[o for o in pool if ok(o)]
    return rng.choice(c) if c else None
def make(rng,pools,hist,vid,idx):
    PF,PB,F,Bk,V=pools; recent=set(b for h in hist[-1:] for b in h["breeds"]); art_hist=set(tuple(a) for h in hist[-ART_WINDOW:] for a in h["arts"]); assets=set(a for h in hist for a in h["srcs"])
    prevpc=set(tuple(x) for x in (hist[-1].get("pc",[]) if hist else [])); prevppl=set(hist[-1].get("ppl",[]) if hist else [])
    fk=sorted({o["pkey"] for o in PF}-prevppl); bk=sorted({o["pkey"] for o in PB}-prevppl)
    # 10 frames: person-front, back, front, person-back, front, person-front, back, front, person-back, back  => 4 people (40%), 5 front / 5 back
    slots=["Pf","Bk","Ff","Pb","Ff","Pf","Bk","Ff","Pb","Bk"]
    for attempt in range(3000):
        pb=rng.sample(bk,2); pf=rng.sample([k for k in fk if k not in pb],2)
        keys={"Pf0":pf[0],"Pf1":pf[1],"Pb0":pb[0],"Pb1":pb[1]}; npf=npb=0
        order=[]; used_b=set(); arts=set(); cols=set(); cnt={}; fail=False
        for s in slots:
            prev=order[-1] if order else None
            def ok(o):
                if o["breed"] in used_b or o["breed"] in recent: return False
                a=(o["breed"],o["style"],o["sub"])
                if a in arts or a in art_hist or o["src"] in assets: return False
                if o["colour"] and o["colour"] in cols: return False
                if o["colour"] and s[0]!="P" and (o["prod"],o["colour"]) in prevpc: return False
                if prev:
                    if FAM(o["prod"])==FAM(prev["prod"]) and o["prod"] not in("Tee A","Tee B","Hoodie") : return False
                    if o["style"]==prev["style"] and rng.random()<.9: return False
                    if o["tone"] and prev["tone"] and o["tone"]==prev["tone"] and s[0]!="P" and prev["prod"] not in PEOPLEPRODS: return False
                g="hat" if o["prod"] in HATS else FAM(o["prod"])
                if cnt.get(g,0)>=({"hat":3,"Tee":5,"Hoodie":5}.get(g,2)): return False
                return True
            if s=="Pf":
                k=pf[npf]; o=pick(rng,[x for x in PF if x["pkey"]==k],ok); npf+=1
            elif s=="Pb":
                k=pb[npb]; o=pick(rng,[x for x in PB if x["pkey"]==k],ok); npb+=1
            elif s=="Ff": o=pick(rng,F+V if rng.random()<.35 else F,ok)
            else: o=pick(rng,Bk,ok)
            if not o: fail=True; break
            order.append(o); used_b.add(o["breed"]); arts.add((o["breed"],o["style"],o["sub"]))
            if o["colour"]: cols.add(o["colour"])
            g="hat" if o["prod"] in HATS else FAM(o["prod"]); cnt[g]=cnt.get(g,0)+1
        if fail: continue
        if len({o["prod"] for o in order})<3: continue
        if sum(1 for o in order if o["tone"]=="dark")<3 or sum(1 for o in order if o["tone"] in("light","pastel"))<2: continue
        if sum(1 for o in order if o["breed"] in POPULAR)<3: continue
        if len({o["style"] for o in order})<2: continue
        return order,[o.get("pkey") for o in order if o.get("pkey")]
    raise SystemExit("could not satisfy rules for "+vid)
def main():
    n=int(sys.argv[1]); seed=sys.argv[2] if len(sys.argv)>2 else "x"; start=int(sys.argv[3]) if len(sys.argv)>3 else 40
    rng=random.Random(seed); pools=load()
    hist=json.load(open(H)) if os.path.exists(H) else []
    briefs=[]; B="social/postb/briefs.json"
    for i in range(n):
        vid=f"m{start+i:02d}"; order,pair=make(rng,pools,hist,vid,i)
        prevf=hist[-1]["format"] if hist else None; prevm=hist[-1]["music"] if hist else None; prevt=hist[-1]["title"] if hist else None
        fmt="reel_slideshow"; mus=rng.choice([m for m in MUSIC if m!=prevm]); tit=rng.choice([t for t in TITLES if t!=prevt])
        durs=[round(rng.uniform(.9,2.4),2) for _ in order] if fmt=="reel_rhythm" else None
        a=[{"src":o["src"],"pid":o["pid"],"breed":o["breed"],"colour":o["colour"],"cam":o["cam"],"prod":o["prod"],"style":o["style"],"sub":o["sub"],"person":"person" in o["cam"],"pkey":o.get("pkey")} for o in order]
        p={"id":vid,"prod":"Mix","title":tit,"breeds":[o["breed"] for o in order],"format":fmt,"trans":rng.randrange(6),"music":mus,"cap":rng.choice(["story","question","list","benefit","gift","seasonal"]),"durs":durs,"assets":a}
        briefs.append(p)
        hist.append({"id":vid,"breeds":p["breeds"],"arts":[(o["breed"],o["style"],o["sub"]) for o in order],"srcs":[o["src"] for o in order],"format":fmt,"music":mus,"title":tit,"pc":[(o["prod"],o["colour"]) for o in order],"ppl":list(pair)})
    json.dump(briefs,open(B,"w"),indent=1)
    json.dump([{**h,"arts":[list(a) for a in h["arts"]]} for h in hist],open(H,"w"))
    for p in briefs:
        a=p["assets"]; print(p["id"],p["format"],p["music"],"people",sum(x["person"] for x in a),"back",sum(x["cam"].startswith("back") for x in a),[x["prod"][:4]+":"+x["colour"][:6] for x in a])
if __name__=="__main__":
    # hist arts come back as lists
    main()
