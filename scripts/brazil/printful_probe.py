import os, json, sys, requests
T=os.environ.get("PRINTFUL_API_TOKEN","")
OUT="docs/brazil_data/printful"
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
