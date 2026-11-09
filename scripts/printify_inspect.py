"""Dump print_areas (placement x/y/scale/angle) of products: PRINTIFY_TOKEN env; args: SHOP PID..."""
import os,json,sys,urllib.request
T=os.environ["PRINTIFY_TOKEN"].strip(); shop=sys.argv[1]; os.makedirs("out/pinspect",exist_ok=True)
for pid in sys.argv[2:]:
    p=json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.printify.com/v1/shops/{shop}/products/{pid}.json",headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
    json.dump(p,open(f"out/pinspect/{pid}.json","w"),indent=1)
    print(pid,p["title"],"bp",p["blueprint_id"],"prov",p["print_provider_id"])
    for a in p["print_areas"]:
        for ph in a["placeholders"]:
            print("  area vars",len(a["variant_ids"]),ph["position"],[ (i["name"],i["x"],i["y"],i["scale"],i["angle"],i.get("width"),i.get("height")) for i in ph["images"]])
    import re
    for i in [x for x in p.get("images",[]) if "camera_label=back" in x["src"]][:6]:
        try: open(f"out/pinspect/{pid}_{i['variant_ids'][0]}.jpg","wb").write(urllib.request.urlopen(urllib.request.Request(i["src"],headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read()); print("img",i["src"][:120])
        except Exception as e: print("imgerr",e)
