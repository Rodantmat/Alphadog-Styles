import os,json,urllib.request,urllib.error
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(m,p):
    r=urllib.request.Request("https://api.printify.com"+p,method=m,headers={"Authorization":"Bearer "+T,"User-Agent":"a"})
    try: return json.load(urllib.request.urlopen(r,timeout=60))
    except urllib.error.HTTPError as e: return {"ERR":e.code,"msg":e.read().decode()[:200]}
for shop,pid in [(29545924,"6ae588ecc0e74489cc070b2a"),(29546485,"6ae6cfcd5d17aa531b00d623"),(29546485,"6ae7a5d17861ac1c1c042638")]:
    p=call("GET",f"/v1/shops/{shop}/products/{pid}.json")
    print("PRODUCT",pid,p.get("title"),p.get("blueprint_id"),p.get("print_provider_id"))
    seen=set()
    for a in p["print_areas"]:
        for ph in a["placeholders"]:
            for im in ph["images"]:
                if im["id"] in seen: continue
                seen.add(im["id"]); u=call("GET",f"/v1/uploads/{im['id']}.json")
                print("  ",ph["position"],im["id"],im.get("name"),"->",u.get("file_name") if "ERR" not in u else u)
