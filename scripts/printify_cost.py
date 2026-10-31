import os,json,urllib.request
T=os.environ["PRINTIFY_TOKEN"]
def g(p):
    r=urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}); return json.load(urllib.request.urlopen(r))
out={}
for name,shop,pid in [("tee_pair",29544854,"6ae56ab79404229b2d0c3626"),("hoodie_pair",29544854,"6ae56abab3e56e7b5f092b0d"),("tee_pocket",29545924,"6ae57d451db256d3020eb326"),("hoodie_pocket",29545924,"6ae57d4890e00e273b088c24"),("tee_portrait",29545924,"6ae572475d127aa2b30aef55"),("hoodie_portrait",29545924,"6ae5724a55e86fafe60ad39a")]:
    p=g(f"/v1/shops/{shop}/products/{pid}.json")
    rows={}
    for v in p["variants"]:
        if not v.get("is_enabled"): continue
        c,s=v["title"].split(" / ") if " / " in v["title"] else (v["title"],"")
        rows[v["title"]]={"cost":v["cost"],"price":v["price"]}
    out[name]=rows
for name,bp in []:
    try: out[name+"_ship"]=g(f"/v1/catalog/blueprints/{bp}/print_providers/99/shipping.json")
    except Exception as e: out[name+"_ship"]=str(e)
json.dump(out,open("out/costs.json","w"),indent=1)
print("ok")
