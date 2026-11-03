"""Remove the old logo-only back embroidery from dad hats (blueprint 1447, position back_hat_embroidery). Front art untouched."""
import os,json,urllib.request,urllib.error,time
T=os.environ["PRINTIFY_TOKEN"].strip();DRY=os.environ.get("DRY")=="1";LIMIT=int(os.environ.get("LIMIT","100000"))
OLD="6ae638b642ccd775a0a50e47"
def call(m,p,b=None,retry=9):
    for a in range(retry):
        d=json.dumps(b).encode() if b is not None else None
        r=urllib.request.Request("https://api.printify.com"+p,data=d,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:400]
            if e.code in (429,500,502,503,504) and a<retry-1: time.sleep(20*(a+1)); continue
            print("HTTP",e.code,p,msg,flush=True); raise
st={"changed":0,"none":0,"failed":0,"locked":0};done=0
for s in call("GET","/v1/shops.json"):
    SHOP=s["id"];page=1
    while True:
        r=call("GET",f"/v1/shops/{SHOP}/products.json?limit=50&page={page}")
        for p in r["data"]:
            if p["blueprint_id"]!=1447: continue
            has=any(ph["position"]=="back_hat_embroidery" and any(im["id"]==OLD for im in ph["images"]) for a in p["print_areas"] for ph in a["placeholders"])
            if not has: st["none"]+=1; continue
            if done>=LIMIT: break
            new=[{"variant_ids":a["variant_ids"],"placeholders":[{"position":q["position"],"images":[{k:v for k,v in im.items() if k in("id","x","y","scale","angle")} for im in q["images"] if im.get("type")!="text/plain"]} for q in a["placeholders"] if q["images"] and q["position"]!="back_hat_embroidery"]} for a in p["print_areas"]]
            new=[a for a in new if a["placeholders"]]
            if DRY: st["changed"]+=1;done+=1; print("would",SHOP,p["id"],p["title"][:50],flush=True); continue
            try:
                if p.get("is_locked"): call("POST",f"/v1/shops/{SHOP}/products/{p['id']}/publishing_failed.json",{"reason":"unlock"}); st["locked"]+=1
                call("PUT",f"/v1/shops/{SHOP}/products/{p['id']}.json",{"print_areas":new}); st["changed"]+=1;done+=1
            except Exception: st["failed"]+=1
            time.sleep(0.3)
        if page>=r.get("last_page",1): break
        page+=1
    print(SHOP,json.dumps(st),flush=True)
os.makedirs("out",exist_ok=True);json.dump(st,open("out/hatlogo_result.json","w"));print("FINISHED",st)
