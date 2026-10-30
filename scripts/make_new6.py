import json,os
B="out/sets"
def P(th,s,v):
    for p in("p1","p2"):
        f=f"{B}/{th}_{p}/{s}__{v}.jpg"
        if os.path.exists(f): return f
    raise SystemExit((th,s,v))
BREEDS=[ # slug, name, base slug (existing approved design to clone style from), traits
("siberian_husky","Siberian Husky","german_shepherd","erect triangular ears set high, thick double coat with fluffy cheek ruff, almond-shaped eyes, facial mask markings drawn only with lines, medium muzzle, full bushy tail carried low or curled"),
("pug","Pug","french_bulldog","round head with deeply wrinkled forehead, flat short muzzle, small folded rose-shaped ears, big round eyes, stocky compact body, short legs, tightly curled tail over the hip"),
("american_pit_bull_terrier","American Pit Bull Terrier","boxer","muscular athletic body, broad blocky head with strong cheeks, short smooth coat, small half-folded rose ears, wide chest, thin tapering tail"),
("border_collie","Border Collie","australian_shepherd","medium athletic body, feathered medium-length coat with a ruff on the chest, semi-erect ears with tipped-over tops, narrow white blaze line down the face, alert intelligent eyes, long feathered bushy tail"),
("shiba_inu","Shiba Inu","pomeranian","fox-like face, small erect triangular ears, compact sturdy body, cream cheek markings drawn with lines, thick fur ruff, tail tightly curled over the back"),
]
ACC={"classic":"Plain classic version, no accessories.",
 "cool":"Both the front head and the back dog wear the same aviator sunglasses as in image 1 (nothing else added).",
 "heart":"Keep the heart element of image 1 around the front head and the collar with a small heart tag on the back dog, exactly as in image 1."}
DESC={"line":"single flowing continuous hand-drawn line","geo":"bold geometric polygon lines"}
KEEP=(" KEEP IDENTICAL to image 1: the exact same drawing style, line weight, level of detail, eye style (white iris with one off-centre black pupil and a small highlight, both eyes looking the same direction), layout (small front head emblem on the left, matching full-body sitting dog on the right), pose type, size and positions. "
 "The front head AND the full-body dog must both be complete and clearly the same breed: all ears fully drawn and continuous, the tail fully drawn and clearly visible (closed, tapered), chest and body contour lines drawn on the back dog just like the base dog in image 1, "
 "legs and paws complete. Pure black on flat white, no gray, no shading, no text, nothing cut off at the canvas or between the two drawings.")
jobs=[]
for slug,name,base,tr in BREEDS:
  for th in("line","geo"):
    for v in("classic","cool","heart"):
      pr=(f"Image 1 is an APPROVED finished design set of a {base.replace('_',' ')} in {DESC[th]} style. Redraw it as a {name}: {tr}. Change ONLY the dog's identity (head shape, ears, coat, body proportions, tail) so it is instantly recognizable as a {name}, not a {base.replace('_',' ')}. "+KEEP+" "+ACC[v])
      for k in "abcd":
        jobs.append({"id":f"N_{th}_{slug}_{v}__{k}","theme":th,"slug":slug,"variant":v,"side":"both","refs":[P(th,base,v)],"aspect":"3:2","prompt":pr})
for i in range(0,len(jobs),60):
    json.dump({"base":"","styles":jobs[i:i+60]},open(f"scripts/new6_{i//60}.json","w"),indent=1)
print(len(jobs))
