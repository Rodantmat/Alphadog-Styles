import json,urllib.request,re,time
def g(u):
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"alphadog"}),timeout=60))
        except Exception as e: err=e; time.sleep(2)
    print("ERR",u,err); return None
prods=[];off=0
while True:
    r=g(f"https://api.printful.com/v2/catalog-products?limit=100&offset={off}")
    if not r: break
    prods+=r["data"]; off+=100
    if off>=r["paging"]["total"]: break
print("products",len(prods))
hats=[p for p in prods if re.search(r"hat|cap|beanie|snapback|trucker|visor|headwear",(p.get("type","")+" "+p.get("name","")),re.I)]
print("hats",len(hats))
allpl={};out=[]
for p in hats:
    pls=[(t.get("placement"),t.get("technique")) for t in p.get("placements",[])]
    for x in pls: allpl[str(x)]=allpl.get(str(x),0)+1
    out.append({"id":p["id"],"name":p["name"],"placements":pls})
    if any(re.search("label|inside|inner|sweat",str(x),re.I) for x in pls): print("INSIDE?",p["id"],p["name"],pls)
print(json.dumps(allpl,indent=0))
json.dump(out,open("out/printful_v2_hats.json","w"),indent=1)
