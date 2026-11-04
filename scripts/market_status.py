"""READ-ONLY status of the three marketplace channels (nothing is changed anywhere)."""
import os,sys,json,urllib.request,time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
T=os.environ["PRINTIFY_TOKEN"]
def pf(p):
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=120))
        except Exception as e:
            if a==3: return {"_err":str(e)[:150]}
            time.sleep(10)
out={}
shops=pf("/v1/shops.json"); print("PRINTIFY SHOPS:",json.dumps(shops)[:700])
for s in shops if isinstance(shops,list) else []:
    prods=[];page=1
    while True:
        r=pf(f"/v1/shops/{s['id']}/products.json?limit=50&page={page}")
        if "_err" in r: print("  products error",s["id"],r); break
        prods+=r["data"]
        if page>=r.get("last_page",1): break
        page+=1
    vis=sum(1 for p in prods if p.get("visible")); ext=sum(1 for p in prods if (p.get("external") or {}).get("id")); lock=sum(1 for p in prods if p.get("is_locked"))
    o=pf(f"/v1/shops/{s['id']}/orders.json?limit=20"); od=o.get("data",[]) if isinstance(o,dict) else []
    sts={}
    for x in od: sts[x.get("status")]=sts.get(x.get("status"),0)+1
    out[s["id"]]={"title":s.get("title"),"channel":s.get("sales_channel"),"products":len(prods),"visible":vis,"linked_to_channel":ext,"locked_publishing":lock,"recent_orders":sts}
    print(f"SHOP {s['id']} {s.get('title')} [{s.get('sales_channel')}] products={len(prods)} visible={vis} on_channel(external id)={ext} publishing_locked={lock} recent_order_status={sts}",flush=True)
try:
    import etsy_api as E
    me=E.call("GET","/users/me"); print("ETSY API OK shop_id",me.get("shop_id"))
    for st in ("active","draft","expired","inactive"):
        try: print(f"ETSY listings {st}:",len(E.listings(st)))
        except Exception as e: print("ETSY listings",st,"error",str(e)[:100])
except Exception as e: print("ETSY API problem:",str(e)[:200])
try:
    import etsy_api as E
    S=E.store("GET","/api/internal/orders/all?q=MK-&g=all")
    print("MARKET ORDERS in store:",[(x["id"],x["status"]) for x in S["items"]][:20])
    print("HEALTH",json.dumps(E.store("GET","/api/internal/health")))
except Exception as e: print("store check error",str(e)[:150])
json.dump(out,open("market_status.json","w"),indent=1)
