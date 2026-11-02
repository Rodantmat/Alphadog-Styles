"""eBay Revise file: replace the gallery photos of our 100 live eBay listings (rotated main-photo colors)."""
import csv,json,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
items=json.load(open(f"{ROOT}/store/data/ebay_items.json")); imgs=json.load(open(f"{ROOT}/store/data/market_images.json")); SITE="https://alphadogstyles.com/mk/"
os.makedirs(f"{ROOT}/store/mk/feeds",exist_ok=True)
with open(f"{ROOT}/store/mk/feeds/ebay_revise_pics.csv","w",newline="",encoding="utf-8") as fh:
    w=csv.writer(fh); w.writerow(["*Action(SiteID=US|Country=US|Currency=USD|Version=1193|CC=UTF-8)","ItemID","PicURL"])
    for lab,iid in items.items():
        m=imgs[lab.lower()]; w.writerow(["Revise",iid,"|".join(SITE+f for f in (m["hero"][:10]+[m["lineup"]])[:12])])
print("revise rows",len(items))
