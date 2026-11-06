import os,json,urllib.request,collections
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(p): return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
for pid in os.environ["PIDS"].split(","):
    p=call(f"/v1/shops/{os.environ['SHOP']}/products/{pid}.json")
    print("PROD",pid,p["title"][:50],"images",len(p["images"]))
    c=collections.Counter(im["position"] for im in p["images"]); print("POS",dict(c))
    for im in p["images"][:60]:
        if im["position"] not in ("front","back"): print("IMG",im["position"],len(im.get("variant_ids",[])),im["src"].split("/")[-3:])
