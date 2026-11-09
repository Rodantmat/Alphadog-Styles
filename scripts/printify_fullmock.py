"""FULL mockup index: every product x every variant x every camera/view Printify holds for AlphaDog (all shops). Index only (no image downloads).
Writes out/mockidx/index.json  rows: {shop,pid,title,bp,prov,tags,variants:{id:title},imgs:[{src,cam,pos,vids}]} and out/mockidx/summary.txt"""
import os,json,urllib.request,time,re,collections
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(p):
    for t in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=90))
        except Exception as e:
            err=e; time.sleep(4+4*t)
    raise err
os.makedirs("out/mockidx",exist_ok=True); rows=[]
for s in call("/v1/shops.json"):
    sid=s["id"]; pg=1
    while True:
        d=call(f"/v1/shops/{sid}/products.json?limit=50&page={pg}")
        for p in d["data"]:
            imgs=[]
            for i in p.get("images",[]):
                m=re.search(r"camera_label=([^&]+)",i["src"]); imgs.append({"src":i["src"].split("?")[0],"cam":m.group(1) if m else "","pos":i.get("position"),"vids":i.get("variant_ids",[]),"def":i.get("is_default")})
            rows.append({"shop":sid,"pid":p["id"],"title":p["title"],"bp":p.get("blueprint_id"),"prov":p.get("print_provider_id"),"tags":p.get("tags",[]),"vis":p.get("visible"),
              "variants":{v["id"]:v["title"] for v in p["variants"] if v.get("is_enabled")},"imgs":imgs})
        print("shop",sid,"page",pg,len(d["data"]),flush=True)
        if pg>=d.get("last_page",1): break
        pg+=1; time.sleep(1)
json.dump(rows,open("out/mockidx/index.json","w"))
bp=collections.Counter(r["bp"] for r in rows); cam=collections.Counter(i["cam"] for r in rows for i in r["imgs"])
L=[f"products {len(rows)}  images {sum(len(r['imgs']) for r in rows)}","blueprints "+str(dict(bp)),"cameras "+str(dict(cam))]
for b in bp:
    r=[x for x in rows if x["bp"]==b]; L.append(f"bp {b}: {len(r)} prods, e.g. {r[0]['title'][:70]} | variants {len(r[0]['variants'])} | imgs {len(r[0]['imgs'])}")
open("out/mockidx/summary.txt","w").write("\n".join(L)); print("\n".join(L))
