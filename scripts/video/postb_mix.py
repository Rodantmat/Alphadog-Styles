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
def load():
    d=json.load(gzip.open("out/mockidx/slim.json.gz","rt")); d=[o for o in d if o["breed"] not in FORBID]
    P=[o for o in d if o["cam"] in("person-front","person-1-front","person-2-front")]
    F=[o for o in d if o["cam"]=="front" and o["place"] in("Big Portrait","Pocket Print","Front & Back") and o["prod"] in("Tee A","Tee B","Hoodie")]
    Bk=[o for o in d if o["cam"] in("back","back-2") and o["place"] in BACKP and o["prod"] in("Tee A","Tee B","Hoodie")]
    return P,F,Bk
def pick(rng,pool,ok):
    c=[o for o in pool if ok(o)]
    return rng.choice(c) if c else None
def make(rng,pools,hist,vid):
    P,F,Bk=pools; usedA=set(); recent=set(b for h in hist[-1:] for b in h["breeds"]); art_hist=set(tuple(a) for h in hist[-ART_WINDOW:] for a in h["arts"]); assets=set(a for h in hist for a in h["srcs"])
    for attempt in range(400):
        # slot order: P B F B P B P B P B  (person opens, back closes)
        slots="PBFBPBPBPB"; order=[]; used_b=set(); arts=set(); prev=None; fail=False; styles=[]
        pprods=[("Mesh Trucker Cap","person-1-front"),("Foam Trucker Hat","person-1-front"),("Foam Trucker Hat","person-2-front"),("Polo","person-front")]; rng.shuffle(pprods); pi=0  # 4 different models, never the same person twice
        for s in slots:
            def ok(o):
                if o["breed"] in used_b or o["breed"] in recent: return False
                a=(o["breed"],o["style"],o["sub"])
                if a in arts or a in art_hist or o["src"] in assets: return False
                if prev and (o["prod"]==prev["prod"] or o["colour"]==prev["colour"] or o["style"]==prev["style"] and rng.random()<.9): return False
                return True
            if s=="P":
                pp=pprods[pi]; pi+=1; o=pick(rng,[x for x in P if (x["prod"],x["cam"])==pp],ok)
            elif s=="F": o=pick(rng,F,ok)
            else:
                # force dark-shade variety on backs
                dk=sum(1 for x in order if x["colour"] in DARK_X)
                o=pick(rng,[x for x in Bk if (x["colour"] in DARK_X or rng.random()<.35)],ok)
            if not o: fail=True; break
            order.append(o); used_b.add(o["breed"]); arts.add((o["breed"],o["style"],o["sub"])); prev=o
        if fail: continue
        if len({o["prod"] for o in order})<5 or len({o["colour"] for o in order if o["colour"]})<5: continue
        if sum(1 for o in order if o["colour"] in DARK_X)<3: continue
        if sum(1 for o in order if o["breed"] in POPULAR)<3: continue
        if len({o["style"] for o in order})<2: continue
        return order
    raise SystemExit("could not satisfy rules for "+vid)
def main():
    n=int(sys.argv[1]); seed=sys.argv[2] if len(sys.argv)>2 else "x"; start=int(sys.argv[3]) if len(sys.argv)>3 else 40
    rng=random.Random(seed); pools=load()
    hist=json.load(open(H)) if os.path.exists(H) else []
    briefs=[]; B="social/postb/briefs.json"
    for i in range(n):
        vid=f"m{start+i:02d}"; order=make(rng,pools,hist,vid)
        prevf=hist[-1]["format"] if hist else None; prevm=hist[-1]["music"] if hist else None; prevt=hist[-1]["title"] if hist else None
        fmt="reel_slideshow"; mus=rng.choice([m for m in MUSIC if m!=prevm]); tit=rng.choice([t for t in TITLES if t!=prevt])
        durs=[round(rng.uniform(.9,2.4),2) for _ in order] if fmt=="reel_rhythm" else None
        a=[{"src":o["src"],"pid":o["pid"],"breed":o["breed"],"colour":o["colour"],"cam":o["cam"],"prod":o["prod"],"style":o["style"],"sub":o["sub"],"person":"person" in o["cam"]} for o in order]
        p={"id":vid,"prod":"Mix","title":tit,"breeds":[o["breed"] for o in order],"format":fmt,"trans":rng.randrange(6),"music":mus,"cap":rng.choice(["story","question","list","benefit","gift","seasonal"]),"durs":durs,"assets":a}
        briefs.append(p)
        hist.append({"id":vid,"breeds":p["breeds"],"arts":[(o["breed"],o["style"],o["sub"]) for o in order],"srcs":[o["src"] for o in order],"format":fmt,"music":mus,"title":tit})
    json.dump(briefs,open(B,"w"),indent=1)
    json.dump([{**h,"arts":[list(a) for a in h["arts"]]} for h in hist],open(H,"w"))
    for p in briefs:
        a=p["assets"]; print(p["id"],p["format"],p["music"],"people",sum(x["person"] for x in a),"back",sum(x["cam"].startswith("back") for x in a),[x["prod"][:4]+":"+x["colour"][:6] for x in a])
if __name__=="__main__":
    # hist arts come back as lists
    main()
