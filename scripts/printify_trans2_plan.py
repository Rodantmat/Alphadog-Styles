#!/usr/bin/env python3
"""Plan for the multi-breed / multi-colour cutout library (fixes the 'one bulldog on grey in every reel' look-alike problem).
Camera ids are valid for every product id + colour of a blueprint (docs/PRINTIFY_TRANSPARENT.md), so for EVERY usable camera of a product type
(person front/back, flat front/back, folded; blocklist applied) we assign K different (breed, design, colour) combos from the real-product catalog
(out/mockidx/catalog.tsv.gz). Back cameras only get combos that have a back print (placement contains 'Back'). Breeds/colours are rotated so the
library spreads over all 33 breeds and all colours. Test/draft products excluded by title slug. Output docs/trans2_plan.json."""
import gzip,csv,json,re,random,collections,sys
K=int(sys.argv[1]) if len(sys.argv)>1 else 6          # combos per person camera
KF=int(sys.argv[2]) if len(sys.argv)>2 else 16         # combos per flat/folded camera (flats are the scarce shot type: only ~2-3 cameras per product)
rows=list(csv.DictReader(gzip.open("out/mockidx/catalog.tsv.gz","rt"),delimiter="\t"))
bad=re.compile(r"test|sample|costtest|neck-label|draft",re.I)
M=json.load(open("docs/printify_cameras.json")); BLOCK=json.load(open("docs/cutout_blocklist.json"))
USE=["Tee A","Tee B","Hoodie","Mesh Trucker Cap","Foam Trucker Hat","Dad Hat","Polo"]
WANT={("person","front"),("person","back"),("flat_front","front"),("flat_back","back"),("folded","other")}
combos=collections.defaultdict(dict)
for r in rows:
    if r["product"] not in USE or bad.search(r["url"]) or not r["breed"]: continue
    pid,var=r["url"].split("/mockup/")[1].split("/")[:2]
    combos[r["product"]][(pid,var)]=dict(pid=pid,var=var,colour=r["colour"] or "none",breed=r["breed"],design=r["design"],style=r["style"],placement=r["placement"],tone=r["tone"])
rnd=random.Random(20261110); plan=[]; usedb=collections.Counter(); usedc=collections.Counter()
for prod in USE:
    cs=list(combos[prod].values()); rnd.shuffle(cs)
    cams=[(c,m) for c,m in M[prod].items() if (m["kind"],m.get("side")) in WANT and c not in BLOCK]
    for cam,m in cams:
        back=m.get("side")=="back"; got=[]
        if back and not any("Back" in c["placement"] for c in cs): continue      # caps/polo: no back print exists
        ncol=len({c["colour"] for c in cs}); kk=K if m["kind"]=="person" else KF
        for _ in range(kk):
            ok=[c for c in cs if (("Back" in c["placement"]) or not back) and c["breed"] not in {g["breed"] for g in got} and (ncol<kk or c["colour"] not in {g["colour"] for g in got})]
            if not ok: break
            ok.sort(key=lambda c:(usedb[c["breed"]],usedc[(prod,c["colour"])],rnd.random())); c=ok[0]; got.append(c)
            usedb[c["breed"]]+=1; usedc[(prod,c["colour"])]+=1
            plan.append(dict(prod=prod,cam=cam,kind=m["kind"],side=m.get("side"),**c))
json.dump(plan,open("docs/trans2_plan.json","w"),indent=0)
print(len(plan),"pictures",collections.Counter(p["prod"] for p in plan)); print("breeds",len({p["breed"] for p in plan}),"colours",collections.Counter(p["colour"] for p in plan).most_common(8))
