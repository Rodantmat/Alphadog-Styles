# Read-only, no token: Printful public catalog checks for Brazil production
import json,urllib.request
def g(u):
    try:
        r=urllib.request.Request(u,headers={"User-Agent":"a"}); return json.load(urllib.request.urlopen(r,timeout=30))
    except Exception as e: return {"error":str(e)}
out={}
for pid,name in [(71,"bella_3001"),(146,"gildan_18500"),(248,"bella_3480_tank"),(206,"yupoong_6245_cap")]:
    out[name]={
      "v2_prices_brazil":g(f"https://api.printful.com/v2/catalog-products/{pid}/prices?selling_region_name=brazil&currency=BRL"),
      "v2_availability":g(f"https://api.printful.com/v2/catalog-products/{pid}/availability?selling_region_name=brazil"),
      "v1_product":(lambda d:{"title":d.get("result",{}).get("product",{}).get("title"),"err":d.get("error")})(g(f"https://api.printful.com/products/{pid}")),
    }
json.dump(out,open("out/printful_brazil.json","w"),indent=1)
