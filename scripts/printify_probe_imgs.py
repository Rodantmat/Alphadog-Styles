import os,json,urllib.request,urllib.error,collections
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(m,p):
    r=urllib.request.Request("https://api.printify.com"+p,method=m,headers={"Authorization":"Bearer "+T,"User-Agent":"a"})
    return json.load(urllib.request.urlopen(r,timeout=60))
old="6ae638b642ccd775a0a50e47"
agg=collections.Counter();ex={}
for s in call("GET","/v1/shops.json"):
    pg=1
    while True:
        r=call("GET",f"/v1/shops/{s['id']}/products.json?limit=50&page={pg}")
        for p in r["data"]:
            pos=sorted({ph["position"] for a in p["print_areas"] for ph in a["placeholders"] for im in ph["images"] if im["id"]==old})
            if pos:
                k=(s["title"],p["blueprint_id"],p["print_provider_id"],tuple(pos),bool(p.get("external")))
                agg[k]+=1; ex.setdefault(k,(p["id"],p["title"][:60],sorted({v["cost"] for v in p["variants"] if v["is_enabled"]})[:3]))
        if pg>=r["last_page"]: break
        pg+=1
for k,v in agg.items(): print("OLDLOGO",k,v,ex[k])
