"""eBay Revise file for the LIVE eBay listings (ItemID from store/data/ebay_items.json).
The live listings carry the OLD color sets (scripts/ebay_live_plan.json = snapshot of what was uploaded). The new plan swaps/adds colors, so:
 parent row  = Revise + ItemID, RelationshipDetails = union(old, new values)
 variation rows in old but not in new = Action 'Delete'; new ones = added; unchanged ones kept (blank action).
Usage: python3 scripts/ebay_revise.py [--only ebay-tee-01] [--skip N] [--limit N] [--out DIR]"""
import csv,json,os,sys,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ebay_csv as X
HERE=os.path.dirname(os.path.abspath(__file__))
items=json.load(open(f"{X.ROOT}/store/data/ebay_items.json")); old=json.load(open(f"{HERE}/ebay_live_plan.json")); new=X.plan
HDR=[X.HDR[0],"ItemID"]+X.HDR[1:]; ACT=X.HDR[0]
class AnyImgs(dict):
    def __getitem__(s,k): return {"hero":[],"lineup":"","bd":{}}
def union(a,b):
    def parse(s):
        d=collections.OrderedDict()
        for part in s.split("|"):
            n,v=part.split("=",1); d[n]=v.split(";")
        return d
    A,B=parse(a),parse(b)
    for n,v in B.items():
        A.setdefault(n,[]); A[n]+= [x for x in v if x not in A[n]]
    return "|".join(f"{n}="+";".join(v) for n,v in A.items())
def build(lid):
    Ln=[l for l in new["listings"] if l["id"]==lid][0]; Lo=[l for l in old["listings"] if l["id"]==lid][0]
    rn=X.rows(Ln)
    X.plan=old; X.imgs=AnyImgs()
    try: ro=X.rows(Lo)
    finally: X.plan=new; X.imgs=json.load(open(f"{X.ROOT}/store/data/market_images.json"))
    parent=rn[0]; parent[ACT]="Revise"; parent["ItemID"]=items[lid.upper()]
    parent["RelationshipDetails"]=union(parent["RelationshipDetails"],ro[0]["RelationshipDetails"])
    nk={r["CustomLabel"] for r in rn[1:]}; ok={r["CustomLabel"] for r in ro[1:]}
    out=[parent]+rn[1:]
    for r in ro[1:]:
        if r["CustomLabel"] not in nk: r[ACT]="Delete"; r["PicURL"]=""; out.append(r)
    return out,len(nk-ok),len(ok-nk),len(nk&ok)
def main():
    only=sys.argv[sys.argv.index("--only")+1] if "--only" in sys.argv else None
    lim=int(sys.argv[sys.argv.index("--limit")+1]) if "--limit" in sys.argv else None
    out=sys.argv[sys.argv.index("--out")+1] if "--out" in sys.argv else f"{X.ROOT}/store/mk/feeds"
    skip=int(sys.argv[sys.argv.index("--skip")+1]) if "--skip" in sys.argv else 0
    Ls=[l for l in new["listings"] if l["plat"]=="ebay" and (not only or l["id"]==only)][skip:][:lim]; os.makedirs(out,exist_ok=True)
    name=f"ebay_revise_{only or (str(skip)+'_'+str(lim))}.csv"; n=0; st=[0,0,0]
    with open(f"{out}/{name}","w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=HDR); w.writeheader()
        for L in Ls:
            rs,a,d,k=build(L["id"]); st[0]+=a; st[1]+=d; st[2]+=k
            for r in rs: r.setdefault("ItemID",""); w.writerow(r); n+=1
    print(name,len(Ls),"listings",n,"rows | added",st[0],"deleted",st[1],"kept",st[2])
if __name__=="__main__": main()
