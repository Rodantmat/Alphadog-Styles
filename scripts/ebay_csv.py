"""eBay Seller Hub Reports upload file (classic File Exchange columns) for the consolidated eBay listings in market_plan.json.
One parent row per listing + one row per variation (Dog Breed / Design / Color / Size). Variation pictures by Dog Breed
(multi-breed listings) or Design (single-breed). Writes store/mk/feeds/ebay_listings.csv (served at alphadogstyles.com/mk/feeds/).
Usage: python3 scripts/ebay_csv.py [--only LISTING_ID] [--limit N]"""
import csv,io,json,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import market_text as T
from market_plan import sku,price,short
ROOT=T.ROOT; plan=T.plan; imgs=json.load(open(f"{ROOT}/store/data/market_images.json"))
SITE="https://alphadogstyles.com/mk/"
CAT={"tee":15687,"hoodie":155183,"wtank":53159,"tank":15687,"polo":185101,"cap":52365}
DEPT={"tee":"Unisex Adults","hoodie":"Unisex Adults","wtank":"Women","tank":"Unisex Adults","polo":"Men","cap":"Unisex Adults"}
TYPE={"tee":"T-Shirt","hoodie":"Hoodie","wtank":"Tank Top","tank":"Tank Top","polo":"Polo","cap":"Baseball Cap"}
POL={"ShippingProfileName":'Printify "Printify Choice" "standard" policy #18542',"ReturnProfileName":"Return policy by Printify","PaymentProfileName":"Payment policy by Printify"}
HDR=["*Action(SiteID=US|Country=US|Currency=USD|Version=1193|CC=UTF-8)","CustomLabel","*Category","*Title","Relationship","RelationshipDetails",
     "*ConditionID","PicURL","*Description","*Format","*Duration","*StartPrice","*Quantity","*Location","ShippingProfileName","ReturnProfileName","PaymentProfileName",
     "C:Brand","C:Department","C:Type","C:Style","C:Size Type","C:Theme","C:Material","C:Sleeve Length","C:Neckline","C:Features","C:Vintage","C:Handmade","C:Country/Region of Manufacture",
     "C:Dog Breed","C:Design","C:Color","C:Size"]
def html(L):
    txt=T.description(L); out=[]
    for para in txt.split("\n\n"):
        lines=para.split("\n")
        if lines[0].isupper() and len(lines)>1: out.append(f"<h3>{lines[0].title()}</h3>"+"<br>".join(lines[1:]))
        else: out.append("<p>"+"<br>".join(lines)+"</p>")
    return "<div style='font-family:Arial,sans-serif;font-size:15px;max-width:800px'>"+"".join(out)+"</div>"
def rows(L):
    P=plan["products"][L["prod"]]; D={d["code"]:d for d in P["designs"]}; C={c["code"]:c for c in P["colors"]}; cap=L["prod"]=="cap"
    multi=len(L["breeds"])>1; m=imgs[L["id"]]
    bname=lambda b: T.BR[b] if len(T.BR[b])<=30 else short(b)
    dname=lambda d: d["name"].replace("·","-")
    specs=[("Dog Breed",[bname(b) for b in L["breeds"]])] if multi else []
    specs+=[("Design",[dname(D[d]) for d in L["designs"]]),("Hat" if cap else "Color",[C[c]["name"] for c in L["colors"]])]
    if not cap: specs.append(("Size",L["sizes"]))
    parent={h:"" for h in HDR}
    parent.update({HDR[0]:"Add","CustomLabel":L["id"].upper(),"*Category":CAT[L["prod"]],"*Title":L["title"][:80],
      "RelationshipDetails":"|".join(f"{n}="+";".join(v) for n,v in specs),"*ConditionID":1000,
      "PicURL":"|".join(SITE+f for f in (m["hero"][:10]+[m["lineup"]])[:12]),"*Description":html(L),"*Format":"FixedPrice","*Duration":"GTC",
      "*Location":"San Diego, CA",**POL,"C:Brand":"AlphaDog Styles","C:Department":DEPT[L["prod"]],"C:Type":TYPE[L["prod"]],
      "C:Style":"Graphic Tee" if L["prod"]=="tee" else ("Pullover" if L["prod"]=="hoodie" else ""),"C:Size Type":"" if cap else "Regular","C:Theme":"Animals, Dogs",
      "C:Material":"Cotton" if L["prod"] in("tee","tank") else ("Cotton Blend" if L["prod"]!="cap" else "Cotton"),
      "C:Sleeve Length":{"tee":"Short Sleeve","hoodie":"Long Sleeve","wtank":"Sleeveless","tank":"Sleeveless","polo":"Short Sleeve"}.get(L["prod"],""),
      "C:Neckline":{"tee":"Crew Neck","tank":"Scoop Neck","wtank":"Scoop Neck","polo":"Collared"}.get(L["prod"],""),
      "C:Features":"Graphic Print","C:Vintage":"No","C:Handmade":"No","C:Country/Region of Manufacture":"United States"})
    out=[parent]; pic_spec="Dog Breed" if multi else "Design"; seen=set()
    for b in L["breeds"]:
        for dc in L["designs"]:
            for cc in L["colors"]:
                for s in L["sizes"]:
                    r={h:"" for h in HDR}; det=[]
                    if multi: det.append(f"Dog Breed={bname(b)}")
                    det.append(f"Design={dname(D[dc])}"); det.append(("Hat=" if cap else "Color=")+C[cc]["name"])
                    if not cap: det.append(f"Size={s}")
                    r.update({"CustomLabel":sku(L["prod"],b,dc,cc,s),"Relationship":"Variation","RelationshipDetails":"|".join(det),
                              "*StartPrice":f"{price(C[cc]['prod'],s):.2f}","*Quantity":10})
                    key=bname(b) if multi else dname(D[dc]); f=m["bd"].get(f"{b}|{dc}") if not multi else m["bd"].get(f"{b}|{L['designs'][0]}")
                    if key not in seen and f: r["PicURL"]=f"{key}={SITE}{f}"; seen.add(key)
                    out.append(r)
    return out
if __name__=="__main__":
    only=sys.argv[sys.argv.index("--only")+1] if "--only" in sys.argv else None
    lim=int(sys.argv[sys.argv.index("--limit")+1]) if "--limit" in sys.argv else None
    Ls=[l for l in plan["listings"] if l["plat"]=="ebay" and (not only or l["id"]==only)][:lim]
    os.makedirs(f"{ROOT}/store/mk/feeds",exist_ok=True)
    name="ebay_listings.csv" if not (only or lim) else f"ebay_listings_{only or lim}.csv"
    with open(f"{ROOT}/store/mk/feeds/{name}","w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=HDR); w.writeheader(); n=0
        for L in Ls:
            for r in rows(L): w.writerow(r); n+=1
    print(name,len(Ls),"listings",n,"rows")
