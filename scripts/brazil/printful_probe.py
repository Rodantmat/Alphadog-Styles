import os, json, sys, requests
T=os.environ.get("PRINTFUL_API_TOKEN","")
OUT="docs/brazil_data/printful"
os.makedirs(OUT,exist_ok=True)
H={"Authorization":"Bearer "+T,"Content-Type":"application/json"}
def save(name,obj):
    json.dump(obj,open(f"{OUT}/{name}.json","w"),ensure_ascii=False,indent=1)
def get(url,**kw):
    r=requests.get(url,headers=H,timeout=40,**kw)
    try: j=r.json()
    except Exception: j={"raw":r.text[:2000]}
    return r.status_code,j
def post(url,body):
    r=requests.post(url,headers=H,json=body,timeout=40)
    try: j=r.json()
    except Exception: j={"raw":r.text[:2000]}
    return r.status_code,j
print("token length",len(T))
log={}
for n,u in [("stores_v1","https://api.printful.com/stores"),("stores_v2","https://api.printful.com/v2/stores"),("scopes","https://api.printful.com/oauth/scopes")]:
    s,j=get(u); log[n]=s; save(n,j); print(n,s)
# catalog products
s,j=get("https://api.printful.com/v2/catalog-products",params={"limit":100}); log["cat_v2"]=s; print("cat",s)
save("cat_list_p1",j)
# find tee/hoodie candidates by name
prods=j.get("data",[]) if isinstance(j,dict) else []
def find(sub):
    return [(p.get("id"),p.get("name")) for p in prods if sub.lower() in (p.get("name") or "").lower()]
print("tees",find("3001")[:5],"hoodie",find("hoodie")[:5])
save("cat_candidates",{"3001":find("3001"),"hoodie":find("hoodie"),"count":len(prods)})

# paginate catalog
allp=[]
off=0
while off<1000:
    s_,j=get("https://api.printful.com/v2/catalog-products",params={"limit":100,"offset":off})
    d=j.get("data",[]) if isinstance(j,dict) else []
    if s_!=200 or not d: break
    allp+=d; off+=100
print("total catalog products",len(allp))
save("cat_all_names",[{"id":p.get("id"),"name":p.get("name"),"type":p.get("type"),"brand":p.get("brand"),"model":p.get("model")} for p in allp])
def pick(*subs):
    out=[]
    for p in allp:
        n=(p.get("name") or "").lower()
        if all(x in n for x in subs): out.append(p)
    return out
tees=pick("3001")[:2]
hood=(pick("18500")[:1] or pick("hoodie")[:1])
print("tee",[(p["id"],p["name"]) for p in tees],"hood",[(p["id"],p["name"]) for p in hood])
for p in tees+hood:
    i=p["id"]
    for ep in ["", "/availability", "/prices", "/prices?selling_region_name=brazil", "/shipping-rates"]:
        s_,j=get(f"https://api.printful.com/v2/catalog-products/{i}{ep}")
        save(f"prod_{i}_{ep.strip('/').replace('?','_').replace('=','_') or 'main'}",{"status":s_,"body":j})
        print(i,ep,s_)

# round 2: Brazil-region catalog + shipping rates
def paged(url,params):
    out=[];off=0
    while off<1500:
        pr=dict(params);pr.update({"limit":100,"offset":off})
        s_,j=get(url,params=pr)
        d=j.get("data",[]) if isinstance(j,dict) else []
        if s_!=200 or not d:
            if s_!=200: print("page err",s_,str(j)[:200])
            break
        out+=d;off+=100
    return out
br=paged("https://api.printful.com/v2/catalog-products",{"selling_region_name":"brazil"})
print("brazil region products",len(br))
save("cat_brazil_region",[{"id":p.get("id"),"name":p.get("name"),"type":p.get("type"),"brand":p.get("brand")} for p in br])
for reg in ["usa","europe","latin_america","north_america","worldwide"]:
    x=paged("https://api.printful.com/v2/catalog-products",{"selling_region_name":reg})
    print(reg,len(x))
# availability scan for apparel in brazil region
cands=[p for p in br if any(k in (p.get("name") or "").lower() for k in ["tee","t-shirt","shirt","hoodie","sweatshirt","tank"])]
res=[]
for p in cands[:60]:
    s_,j=get(f"https://api.printful.com/v2/catalog-products/{p['id']}/availability",params={"selling_region_name":"brazil"})
    regs=set()
    if s_==200:
        for v in j["data"]:
            for t in v["techniques"]:
                for r in t["selling_regions"]: regs.add((t["technique"],r["name"],r["availability"]))
    res.append({"id":p["id"],"name":p["name"],"status":s_,"regions":sorted(regs)[:12]})
save("brazil_apparel_availability",res)
print("apparel candidates",len(cands))
# shipping rates probe (no order created)
body={"recipient":{"address1":"Av Paulista 1000","city":"Sao Paulo","state_code":"SP","country_code":"BR","zip":"01310100","tax_number":"12345678909"},
      "order_items":[{"source":"catalog","catalog_variant_id":4011,"quantity":1,"placements":[{"placement":"front","technique":"dtg","layers":[{"type":"file","url":"https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"}]}]}],
      "currency":"BRL"}
s_,j=post("https://api.printful.com/v2/shipping-rates",body)
save("ship_rates_try1",{"status":s_,"body":j}); print("ship rates",s_,json.dumps(j)[:500])
