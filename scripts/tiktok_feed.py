"""TikTok Shop listing data for the consolidated listings (plat=tiktok): 2 variation tiers, <=100 SKUs per product.
Tier 1 "Style" = breed · design · color (<=35 chars), tier 2 = Size (hats: tier 1 = breed · design, tier 2 = Hat).
Writes out/tiktok_feed.json; tiktok_xlsx.py maps it onto TikTok's bulk template."""
import json,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import market_text as T
from market_plan import sku,price,short
ROOT=T.ROOT; plan=T.plan; imgs=json.load(open(f"{ROOT}/store/data/market_images.json")); SITE="https://alphadogstyles.com/mk/"
DS={"1":"Line+Back","2":"Geo Shades","3":"Heart+Back","4":"Geo+Back","5":"Line Shades","6":"Geo Heart"}
CS={"Soft Cream":"Cream","Athletic Heather":"Heather","Light Blue":"Lt Blue","Soft Pink":"Pink","Sport Grey":"Grey","Light Pink":"Pink",
    "Heather Grey":"Grey","Solid Tahiti Blue":"Blue","Solid Mint":"Mint","Solid Light Orange":"Peach","Solid White":"White"}
WEIGHT={"tee":0.4,"hoodie":1.3,"wtank":0.3,"tank":0.35,"polo":0.6,"cap":0.4}   # lb, packed
DIM={"tee":(10,8,1),"hoodie":(12,10,3),"wtank":(10,8,1),"tank":(10,8,1),"polo":(11,9,2),"cap":(10,8,5)}  # inches
def tier1(L,b,dc,cc,cap):
    P=plan["products"][L["prod"]]; C={c["code"]:c for c in P["colors"]}
    nm=short(b) if len(short(b))<=14 else short(b)[:14]
    v=f"{nm} · {DS.get(dc,dc)}" if cap else f"{nm} · {DS.get(dc,dc)} · {CS.get(C[cc]['color'],C[cc]['color'])}"
    return v[:35]
def build():
    out=[]
    for L in [l for l in plan["listings"] if l["plat"]=="tiktok"]:
        P=plan["products"][L["prod"]]; C={c["code"]:c for c in P["colors"]}; cap=L["prod"]=="cap"; m=imgs[L["id"]]
        skus=[]
        for b in L["breeds"]:
            for dc in L["designs"]:
                for cc in L["colors"]:
                    for s in L["sizes"]:
                        v1=tier1(L,b,dc,cc,cap); v2=C[cc]["name"] if cap else s
                        img=m["bdc"].get(f"{b}|{dc}|{cc}") or m["bd"].get(f"{b}|{dc}")
                        skus.append({"sku":sku(L["prod"],b,dc,cc,s),"v1":v1,"v2":v2,"price":price(C[cc]["prod"],s),"qty":999,"img":SITE+img if img else ""})
        # tier-1 values must be unique per (breed,design,color) - guard against truncation collisions
        assert len({(x["v1"],x["v2"]) for x in skus})==len(skus),L["id"]
        out.append({"id":L["id"],"prod":L["prod"],"title":L["title"],"desc":T.description(L).replace("\n","<br>"),
                    "images":[SITE+f for f in (m["hero"][:8]+[m["lineup"]])[:9]],"v1name":"Style","v2name":"Hat" if cap else "Size",
                    "weight_lb":WEIGHT[L["prod"]],"dims_in":DIM[L["prod"]],"brand":"AlphaDog Styles","skus":skus})
    return out
if __name__=="__main__":
    f=build(); os.makedirs(f"{ROOT}/out",exist_ok=True); json.dump(f,open(f"{ROOT}/out/tiktok_feed.json","w"),indent=0)
    print(len(f),"products",sum(len(x["skus"]) for x in f),"skus; max",max(len(x["skus"]) for x in f),"; longest v1",max(len(s["v1"]) for x in f for s in x["skus"]))
    print(f[0]["skus"][0])
