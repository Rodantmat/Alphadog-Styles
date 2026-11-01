"""Light-only launch helper. env: MODE (probe|hoodies|tees|publish), SHOP, CHANNEL, PRINTIFY_TOKEN, plus per-mode vars."""
import os, json, time, urllib.request, urllib.error
T=os.environ["PRINTIFY_TOKEN"]; MODE=os.environ.get("MODE","probe")
def call(m,p,b=None,retry=4):
    for a in range(retry):
        d=json.dumps(b).encode() if b is not None else None
        r=urllib.request.Request("https://api.printify.com"+p,data=d,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:600]
            if e.code in (429,500,502,503,504) and a<retry-1: time.sleep(10*(a+1)); continue
            print("HTTP",e.code,p,msg,flush=True); raise
if MODE=="probe":
    r=call("GET","/v1/catalog/blueprints/12/print_providers/99/variants.json")
    vs=r["variants"]; print("n variants",len(vs))
    print("colors",sorted({v["options"]["color"] for v in vs}))
    print("sizes",sorted({v["options"]["size"] for v in vs}))
    print("placeholders",json.dumps(vs[0]["placeholders"]))
    json.dump(vs,open("out/bella_variants.json","w"))
    # hoodie sample product light/dark info
    SHOP=int(os.environ["SHOP"]); st=json.load(open(f"out/state_{os.environ['CHANNEL']}.json"))
    k=next(k for k in st if k.endswith("hoodie|pair") or k.endswith("hoodie|portrait"))
    p=call("GET",f"/v1/shops/{SHOP}/products/{st[k]['id']}.json")
    print("hoodie",k,p["blueprint_id"],p.get("visible"),p.get("is_locked"),len(p["variants"]),"enabled",sum(v["is_enabled"] for v in p["variants"]))
    print(json.dumps({kk:p[kk] for kk in p if kk not in("variants","images","print_areas","options","description")})[:700])
    print("external",p.get("external"))
