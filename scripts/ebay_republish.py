"""Re-publish eBay products that never reached eBay (no external id), N at a time, then check which went live."""
import os,json,time,urllib.request,urllib.error
T=os.environ["PRINTIFY_TOKEN"]; SHOP=29545924; N=int(os.environ.get("N","3")); WAIT=int(os.environ.get("WAIT","300"))
def call(m,p,b=None):
    for a in range(5):
        r=urllib.request.Request("https://api.printify.com"+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try:
            x=urllib.request.urlopen(r,timeout=120).read(); return json.loads(x) if x else {}
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:300]
            if e.code==429: time.sleep(60); continue
            return {"_err":e.code,"msg":msg}
st=json.load(open("out/state_light_ebay.json")); todo=[]
for k,v in st.items():
    if "#old" in k: continue
    p=call("GET",f"/v1/shops/{SHOP}/products/{v['id']}.json")
    if not (p.get("external") or {}).get("id"): todo.append((k,v["id"]))
    if len(todo)>=N: break
print("republishing",len(todo))
for k,pid in todo:
    print(k,call("POST",f"/v1/shops/{SHOP}/products/{pid}/publish.json",{"title":True,"description":True,"images":True,"variants":True,"tags":True,"keyfeatures":True,"shipping_template":True}))
    time.sleep(3)
time.sleep(WAIT)
for k,pid in todo:
    p=call("GET",f"/v1/shops/{SHOP}/products/{pid}.json"); print("AFTER",k,"external:",p.get("external"),"locked:",p.get("is_locked"))
