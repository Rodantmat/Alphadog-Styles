import os,json,urllib.request,collections
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(p):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
out={}
for s in call("/v1/shops.json"):
    pg=1
    while True:
        r=call(f"/v1/shops/{s['id']}/products.json?limit=50&page={pg}")
        for p in r["data"]:
            c=collections.Counter((im.get("position"),bool(im.get("is_default"))) for im in p["images"])
            out[p["id"]]=dict(shop=s["title"],bp=p["blueprint_id"],title=p["title"][:60],n=len(p["images"]),pos=dict((f"{k[0]}",v) for k,v in c.items()),src=[im["src"].split("/")[-1] for im in p["images"][:3]])
        if pg>=r["last_page"]: break
        pg+=1
print("TOTAL",len(out))
tot=collections.Counter()
for k,v in out.items(): tot[(v["bp"],v["n"],tuple(sorted(v["pos"])))]+=1
for k,v in tot.most_common(25): print("GROUP",k,v)
for i,(k,v) in enumerate(out.items()):
    if i<4: print("EX",k,json.dumps(v))
json.dump(out,open("out/printify_imglist.json","w"))
