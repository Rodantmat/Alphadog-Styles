"""TikTok Shop has a product limit for this shop (Printify shows "Product limit reached" at ~100 live listings).
Keep the BEST listings live: breadth across the most popular breeds first (people search their own breed), a mix of products per breed.
Priority: 20 most popular breeds x 5 listings (tee front+back, tee big portrait, hoodie front+back, women's racerback tank, dad hat),
then the remaining breeds, then the other designs. MODE=curate: unpublish live listings outside the top LIMIT, publish missing top ones.
Env: PRINTIFY_TOKEN, LIMIT (default 100), DRY (1 = only print the plan)."""
import os,json,time,urllib.request,urllib.error
T=os.environ["PRINTIFY_TOKEN"]; SHOP=29546485; LIMIT=int(os.environ.get("LIMIT","100")); DRY=os.environ.get("DRY")=="1"
def call(m,p,b=None):
    for a in range(6):
        r=urllib.request.Request("https://api.printify.com"+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try:
            x=urllib.request.urlopen(r,timeout=120).read(); return json.loads(x) if x else {}
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:300]
            if e.code==429 or e.code>=500: time.sleep(45*(a+1)); continue
            return {"_err":e.code,"msg":msg}
    return {"_err":"retries"}
BREEDS=[b[0] for b in json.load(open("scripts/breeds25.json"))]
light=json.load(open("out/state_light_tiktok.json")); extras=json.load(open("out/state_extras_tiktok.json"))
lab=json.load(open("out/state_extras_tiktok_label.json")) if os.path.exists("out/state_extras_tiktok_label.json") else {}
def pid(key):
    if key in light: return light[key]["id"]
    if key in extras and (lab.get(key) or extras[key]["prod"] in ("cap_foam","cap_mesh")): return extras[key]["id"]
    return None
SLOTS=[("{b}|line_classic|tee|pair"),("{b}|geo_cool|tee|portrait"),("{b}|line_heart|hoodie|pair"),("{b}|line_heart|wtank"),("{b}|line_classic|cap_dad")]
MORE=[("{b}|geo_classic|tee|pair"),("{b}|line_cool|tee|portrait"),("{b}|geo_heart|hoodie|portrait"),("{b}|line_classic|tank"),("{b}|geo_cool|cap_foam"),("{b}|line_classic|polo"),("{b}|geo_heart|tee|pocket"),("{b}|line_cool|cap_mesh")]
order=[]
for tier in (SLOTS,MORE):
    for b in BREEDS:
        for s in tier:
            k=s.format(b=b)
            if pid(k) and k not in order: order.append(k)
top=order[:LIMIT]; topids={pid(k) for k in top}
# which products are live on TikTok right now
live=set(); page=1
while True:
    r=call("GET",f"/v1/shops/{SHOP}/products.json?limit=50&page={page}")
    for p in r.get("data",[]):
        if (p.get("external") or {}).get("id") or p.get("is_locked"): live.add(p["id"])
    if page>=r.get("last_page",1): break
    page+=1
drop=[x for x in live if x not in topids]; add=[pid(k) for k in top if pid(k) not in live]
print(f"live {len(live)}, keep {len(live)-len(drop)}, unpublish {len(drop)}, publish {len(add)} (limit {LIMIT})")
print("top breeds:",BREEDS[:20])
if DRY: raise SystemExit
for x in drop:
    print("unpublish",x,call("POST",f"/v1/shops/{SHOP}/products/{x}/unpublish.json",{})); time.sleep(2)
if drop: time.sleep(120)   # let TikTok free the slots
n=0
for x in add:
    r=call("POST",f"/v1/shops/{SHOP}/products/{x}/publish.json",{"title":True,"description":True,"images":True,"variants":True,"tags":True,"keyfeatures":True,"shipping_template":True})
    print("publish",x,r if r.get("_err") else "ok"); n+=1; time.sleep(3)
json.dump({"limit":LIMIT,"top":top},open("out/tiktok_curated.json","w"),indent=1)
print("CURATE DONE published",n,"unpublished",len(drop))
