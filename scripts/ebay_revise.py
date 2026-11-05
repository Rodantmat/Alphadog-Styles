"""eBay Revise file for the LIVE eBay listings (ItemID from store/data/ebay_items.json): new color sets, photos, variations.
Usage: python3 scripts/ebay_revise.py [--only ebay-tee-01] [--limit N] [--out DIR]"""
import csv,json,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ebay_csv as X
items=json.load(open(f"{X.ROOT}/store/data/ebay_items.json"))
HDR=[X.HDR[0],"ItemID"]+X.HDR[1:]
def main():
    only=sys.argv[sys.argv.index("--only")+1] if "--only" in sys.argv else None
    lim=int(sys.argv[sys.argv.index("--limit")+1]) if "--limit" in sys.argv else None
    out=sys.argv[sys.argv.index("--out")+1] if "--out" in sys.argv else f"{X.ROOT}/store/mk/feeds"
    skip=int(sys.argv[sys.argv.index("--skip")+1]) if "--skip" in sys.argv else 0
    Ls=[l for l in X.plan["listings"] if l["plat"]=="ebay" and (not only or l["id"]==only)][skip:]
    Ls=Ls[:lim]; os.makedirs(out,exist_ok=True)
    name=f"ebay_revise_{only or (str(skip)+'_'+str(lim))}.csv"; n=0
    with open(f"{out}/{name}","w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=HDR); w.writeheader()
        for L in Ls:
            rs=X.rows(L); rs[0][X.HDR[0]]="Revise"; rs[0]["ItemID"]=items[L["id"].upper()]
            for r in rs: r.setdefault("ItemID",""); w.writerow(r); n+=1
    print(name,len(Ls),"listings",n,"rows")
if __name__=="__main__": main()
