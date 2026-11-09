#!/usr/bin/env python3
"""Slim the full Printify index into the Post B asset catalog (every product x breed x design x placement x colour x view).
in: out/mockidx/index.json   out: out/mockidx/slim.json.gz  rows: {pid,prod,breed,style,tone,place,colour,cam,src}"""
import json,re,gzip,collections
BAD=re.compile(r'TEST|BLANK|PROBE|COST|PILOT|draft|do not publish',re.I)
PROD={77:"Hoodie",145:"Tee A",12:"Tee B",1734:"Mesh Trucker Cap",1735:"Foam Trucker Hat",1447:"Dad Hat",1402:"Polo",18:"Racerback Tank",39:"Tank Top",6488:"Women's Polo"}
DARK={"Black","Navy","Maroon","Forest Green","Dark Heather","Charcoal","Heather Navy","Military Green","Dark Chocolate","Asphalt","Forest","Red","Dark Grey Heather","Heather Military Green","Graphite Heather","Gravel"}
PASTEL={"Light Blue","Light Pink","Soft Pink","Pink","Yellow Haze","Antique Orange"}
def tone(c): return "dark" if c in DARK else "pastel" if c in PASTEL else "light"
def parse(t):
    head=t.split("|")[0].strip(); place=t.split("|")[-1].strip() if "|" in t else ""
    breed=re.split(r" (?:Continuous Line Art|Shirt|Hoodie|T-Shirt|Mesh Trucker|Foam Trucker|Dad Hat|Polo Shirt|Women's|Racerback|Tank Top)",head)[0]
    style="Line Art" if "Line Art" in head else "Geometric" if "Geometric" in head else "Other"
    sub=next((s for s in ("Classic","Cool","Heart") if s in head),"")
    pl=next((p for p in ("Big Portrait","Pocket Print","Front & Back") if p in head),"")
    if not pl and "Pocket Portrait" in place: pl="Pocket Portrait + Full Body Back"
    return breed,style,sub,pl
def main():
    R=json.load(open("out/mockidx/index.json")); out=[]; seen=set()
    for r in R:
        if BAD.search(r["title"]) or r["bp"] not in PROD: continue
        breed,style,sub,pl=parse(r["title"])
        vt={str(k):v for k,v in r["variants"].items()}
        for im in r["imgs"]:
            cols=collections.Counter(vt[str(v)].split(" /")[0] if "/" in vt.get(str(v),"") and not vt[str(v)].split(" /")[0] in("S","M","L","XL","2XL","3XL","XS") else (vt[str(v)].split(" / ")[-1] if str(v) in vt else "") for v in im["vids"])
            col=cols.most_common(1)[0][0] if cols else ""
            col=col.replace("One size","")
            k=(r["pid"],im["cam"],col)
            if im["cam"]=="size-chart" or k in seen: continue
            seen.add(k)
            out.append(dict(pid=r["pid"],prod=PROD[r["bp"]],breed=breed,style=style,sub=sub,place=pl,colour=col,tone=tone(col) if col else "",cam=im["cam"],src=im["src"]))
    with gzip.open("out/mockidx/slim.json.gz","wt") as f: json.dump(out,f)
    c=collections.Counter((o["prod"]) for o in out); print(len(out),dict(c))
    print("breeds",len({o['breed'] for o in out}),"cams",len({o['cam'] for o in out}),"colours",len({o['colour'] for o in out}))
if __name__=="__main__": main()
