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
