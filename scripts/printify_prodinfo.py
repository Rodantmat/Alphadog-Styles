import os,json,urllib.request,time
T=os.environ["PRINTIFY_TOKEN"].strip();SHOP=29546485
def call(p):
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
        except Exception as e: time.sleep(10)
out={}
for f in ["out/state_light_etsy.json","out/state_etsy.json","out/state_dark_tiktok.json"]:
    st=json.load(open(f))
    for k,v in st.items():
        pid=v["id"]
        if pid in [o["id"] for o in out.values()]: continue
        try: p=call(f"/v1/shops/{SHOP}/products/{pid}.json")
        except Exception as e: continue
        if not p: continue
        cols={}
        for var in p["variants"]:
            if var.get("is_enabled"):
                c=var["title"].split(" / ")[0]; cols.setdefault(c,var["id"])
        out[k]=dict(id=pid,bp=p["blueprint_id"],pp=p["print_provider_id"],title=p["title"][:70],cols=cols,src=f)
        print("P",k,p["blueprint_id"],len(cols),flush=True); time.sleep(0.3)
os.makedirs("out",exist_ok=True);json.dump(out,open("out/prodinfo.json","w"),indent=1)
