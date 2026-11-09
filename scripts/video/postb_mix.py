#!/usr/bin/env python3
"""Post B MIX engine: every video = 10 frames randomly drawn from the FULL Printify catalog (out/mockidx/slim.json.gz).
Composition: 4 people shots (front, Mesh/Foam trucker or Polo) + 1 flat front + 5 flat BACK prints  => 40% people / 60% not, 50% front / 50% back.
Hard rules: no breed twice in a video, none of the previous video' breeds, forbidden breeds never, art (breed x style x sub) never reused within ART_WINDOW videos,
no asset reused ever, no two consecutive frames share product/colour/style, >=5 products, >=5 colours with >=3 dark shades beyond black, >=3 popular breeds,
both styles present, a person shot opens, a back print closes.  usage: postb_mix.py N [SEED] [START_ID]"""
import gzip,json,random,sys,os,collections
FORBID={"Yorkshire Terrier","Pomeranian","Shih Tzu","Havanese","Pug","Mini Poodle","Bichon Frise","Maltese"}
POPULAR={"French Bulldog","Golden Retriever","Labrador Retriever","German Shepherd","English Bulldog","Dachshund","Pembroke Welsh Corgi","Siberian Husky","Boxer","Beagle","Rottweiler","Doberman Pinscher","Australian Shepherd","Shiba Inu","Border Collie","Great Dane"}
DARK_X={"Navy","Heather Navy","Forest Green","Maroon","Charcoal","Dark Heather","Dark Chocolate","Military Green","Asphalt","Dark Grey Heather","Red"}
BACKP={"Front & Back","Pocket Portrait + Full Body Back"}
ART_WINDOW=18; H="social/postb/mixhist.json"
FORMATS=["reel_slideshow","reel_flip","reel_split","reel_rhythm"]; MUSIC=["Electronic & House","Feel-good","Funk & Disco","Chill & Lo-fi"]
TITLES=["10 breeds. 10 looks.","Find your breed","Dog people wear it better","Front, back and everything between","Pick your pup","Wear your best friend","Made for dog people"]
PEOPLE={"mesh":("Mesh Trucker Cap","person-1-front"),"foam1":("Foam Trucker Hat","person-1-front"),"foam2":("Foam Trucker Hat","person-2-front"),"polo":("Polo","person-front")}
PAIRS=[("polo","mesh"),("foam1","foam2"),("polo","foam1"),("mesh","foam2")]   # 2 people per video, 4 different models; neighbours never share a person
PEOPLEPRODS={"Mesh Trucker Cap","Foam Trucker Hat","Polo"}
HATS={"Mesh Trucker Cap","Foam Trucker Hat","Dad Hat"}
def load():
    d=json.load(gzip.open("out/mockidx/slim.json.gz","rt")); d=[o for o in d if o["breed"] not in FORBID]
    P={k:[o for o in d if (o["prod"],o["cam"])==v] for k,v in PEOPLE.items()}
    big=("Tee A","Tee B","Hoodie")
    F=[o for o in d if o["cam"] in("front","front-2") and ((o["prod"] in big and o["place"] in("Big Portrait","Pocket Print","Front & Back")) or o["prod"] in("Racerback Tank","Tank Top","Dad Hat","Polo","Mesh Trucker Cap","Foam Trucker Hat"))]
    Bk=[o for o in d if o["cam"] in("back","back-2") and ((o["prod"] in big and o["place"] in BACKP) or o["prod"] in("Racerback Tank","Tank Top","Dad Hat","Polo","Mesh Trucker Cap"))]
    return P,F,Bk
def pick(rng,pool,ok):
    c=[o for o in pool if ok(o)]
    return rng.choice(c) if c else None
def make(rng,pools,hist,vid,idx):
    P,F,Bk=pools; recent=set(b for h in hist[-1:] for b in h["breeds"]); art_hist=set(tuple(a) for h in hist[-ART_WINDOW:] for a in h["arts"]); assets=set(a for h in hist for a in h["srcs"])
    prevpc=set(tuple(x) for x in (hist[-1].get("pc",[]) if hist else [])); prevprods=set(x[0] for x in prevpc)
    pair=PAIRS[idx%len(PAIRS)]
    # 10 frames: person, back, front, back, front, person, back, front, back, back
    slots=["P0","B","F","B","F","P1","B","F","B","B"]
    for attempt in range(1500):
        order=[]; used_b=set(); arts=set(); cols=set(); cnt={}; fail=False
        for s in slots:
            prev=order[-1] if order else None
            def ok(o):
                if o["breed"] in used_b or o["breed"] in recent: return False
                a=(o["breed"],o["style"],o["sub"])
                if a in arts or a in art_hist or o["src"] in assets: return False
                if o["colour"] and o["colour"] in cols and not s[0]=="P": return False
                if o["colour"] and s[0]!="P" and (o["prod"],o["colour"]) in prevpc: return False
                if prev:
                    if o["prod"]==prev["prod"] or o["style"]==prev["style"] and rng.random()<.9: return False
                    if s[0]!="P" and prev["prod"] not in PEOPLEPRODS and o["tone"] and prev["tone"] and o["tone"]==prev["tone"] and rng.random()<.85: return False
                g="hat" if o["prod"] in HATS else ("tee" if o["prod"] in("Tee A","Tee B") else o["prod"])
                lim={"hat":3,"tee":3,"Hoodie":3}.get(g,2)
                if cnt.get(g,0)>=lim: return False
                return True
            if s[0]=="P": o=pick(rng,P[pair[int(s[1])]],ok)
            elif s=="F": o=pick(rng,F,ok)
            else: o=pick(rng,Bk,ok)
            if not o: fail=True; break
            order.append(o); used_b.add(o["breed"]); arts.add((o["breed"],o["style"],o["sub"]))
            if o["colour"]: cols.add(o["colour"])
            g="hat" if o["prod"] in HATS else ("tee" if o["prod"] in("Tee A","Tee B") else o["prod"]); cnt[g]=cnt.get(g,0)+1
        if fail: continue
        prods={o["prod"] for o in order}
        if len(prods)<6 or len(prods-{"Tee A","Tee B","Hoodie"})<3: continue
        if len(prods&prevprods)>4: continue
        if sum(1 for o in order if o["tone"]=="dark")<3 or sum(1 for o in order if o["tone"] in("light","pastel"))<3: continue
        if sum(1 for o in order if o["breed"] in POPULAR)<3: continue
        if len({o["style"] for o in order})<2: continue
        return order,pair
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
        a=[{"src":o["src"],"pid":o["pid"],"breed":o["breed"],"colour":o["colour"],"cam":o["cam"],"prod":o["prod"],"style":o["style"],"sub":o["sub"],"person":"person" in o["cam"]} for o in order]
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
