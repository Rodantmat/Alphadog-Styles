import os,json,urllib.request,urllib.error
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(m,p,b=None):
    r=urllib.request.Request("https://api.printify.com"+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+T,"User-Agent":"a","Content-Type":"application/json"})
    try: return json.load(urllib.request.urlopen(r,timeout=60))
    except urllib.error.HTTPError as e: return {"ERR":e.code,"msg":e.read().decode()[:300]}
SHOP=29545924
for pid in ["6ae588ecc0e74489cc070b2a","6ae588ea90e00e273b0894da","6ae581c7197e2a80420272ab","6ae581c455e86fafe60ae18c","6ae57c8f499964581706fe21","6ae57c8c90e00e273b088bba"]:
    p=call("GET",f"/v1/shops/{SHOP}/products/{pid}.json")
    print(pid,p.get("title"),"visible",p.get("visible"),"external",bool(p.get("external")),"locked",p.get("is_locked"))
    if p.get("external"):
        r=call("POST",f"/v1/shops/{SHOP}/products/{pid}/publish.json",{"title":False,"description":False,"images":True,"variants":False,"tags":False,"keyFeatures":False,"shipping_template":False})
        print("  publish ->",json.dumps(r)[:200])
