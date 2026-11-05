"""Clean garment photos for the new DARK colors (blank drafts with an invisible dot, never published)."""
import os,json,urllib.request,urllib.error,time,base64,zlib,struct
T=os.environ["PRINTIFY_TOKEN"]; SHOP=29559517
def pf(m,p,b=None):
    for a in range(6):
        r=urllib.request.Request("https://api.printify.com"+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:300]
            if e.code in(429,500,502,503) and a<5: time.sleep(25*(a+1)); continue
            raise RuntimeError(f"{e.code} {p} {msg}")
def png(w,h,rgba):
    row=b"\x00"+bytes(rgba)*w; raw=row*h
    ch=lambda t,d: struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    return b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))+ch(b"IDAT",zlib.compress(raw,9))+ch(b"IEND",b"")
up=lambda name,data: pf("POST","/v1/uploads/images.json",{"file_name":name,"contents":base64.b64encode(data).decode()})["id"]
P={"tee":(12,["front","back"],["Black","Dark Grey Heather","Navy","Asphalt","Forest","Maroon","Red"],"M"),
   "hoodie":(77,["front","back"],["Black","Navy","Charcoal","Forest Green","Maroon","Dark Heather"],"M"),
   "tank":(39,["front","back"],["Black","Dark Grey","Navy"],"M"),
   "wtank":(18,["front","back"],["Solid Black","Solid Dark Gray","Solid Midnight Navy","Solid Military Green","Solid Indigo"],"M"),
   "polo":(1402,["left_chest"],["Black","J. Navy"],"M"),
   "cap_dad":(1447,["front_dtf"],["Black","Navy","Dark Grey","Spruce","Green Camo"],"One size"),
   "cap_foam":(1735,["front_dtf"],["Black","Dark Navy","Black/White"],"One size"),
   "cap_mesh":(1734,["front_dtf"],["Black","Navy","Charcoal"],"One size")}
dotid=up("dot.png",png(64,64,[0,0,0,0]))
os.makedirs("out/blanks_dark",exist_ok=True); man=[]; meta={}; made={}
for k,(bp,poss,cols,size) in P.items():
    vs=pf("GET",f"/v1/catalog/blueprints/{bp}/print_providers/99/variants.json")["variants"]
    sel=[v for v in vs if v["options"].get("color") in cols and (size=="One size" or v["options"].get("size")==size)]
    seen=set(); s2=[]
    for v in sel:
        c=v["options"]["color"]
        if c in seen: continue
        seen.add(c); s2.append(v)
    ids=[v["id"] for v in s2]
    meta[k]={"bp":bp,"colors":{str(v["id"]):v["options"]["color"] for v in s2},"missing":[c for c in cols if c not in seen],"sizes":{c:sorted({v["options"].get("size") for v in vs if v["options"].get("color")==c}) for c in cols}}
    ph=[{"position":p,"images":[{"id":dotid,"x":0.5,"y":0.5,"scale":0.05,"angle":0}]} for p in poss]
    pr=pf("POST",f"/v1/shops/{SHOP}/products.json",{"title":f"BLANK dark mockup source - do not publish {k}","description":"blank","blueprint_id":bp,"print_provider_id":99,
        "variants":[{"id":i,"price":3000,"is_enabled":True} for i in ids],"print_areas":[{"variant_ids":ids,"placeholders":ph}]})
    made[k]=pr["id"]; print("created",k,meta[k]["missing"],flush=True); time.sleep(2)
time.sleep(150)
for k,pid in made.items():
    p=pf("GET",f"/v1/shops/{SHOP}/products/{pid}.json")
    for i,imx in enumerate(p["images"]):
        cols=sorted({meta[k]["colors"].get(str(v),"?") for v in imx.get("variant_ids",[])})
        fn=f"out/blanks_dark/{k}_{i:02d}.jpg"
        try: open(fn,"wb").write(urllib.request.urlopen(urllib.request.Request(imx["src"],headers={"User-Agent":"a"}),timeout=60).read())
        except Exception as e: print("ERR",e); continue
        man.append({"file":fn,"prod":k,"position":imx.get("position"),"colors":cols,"default":imx.get("is_default")})
json.dump({"meta":meta,"images":man,"products":made},open("out/blanks_dark/manifest.json","w"),indent=1); print("DONE",len(man))
