"""Blank photos + print-area calibration for the new products (tanks, polos, caps).
For each product: a 'blank' draft (invisible dot) for clean garment photos, and a 'calib' draft with a solid magenta block
filling each print area, so the print area can be measured on Printify's own mockup photos. Drafts are never published."""
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
P={"tank":(39,["front","back"],["White","Athletic Heather"],"M"),
   "wtank":(18,["front","back"],["Solid White","Heather Grey","Solid Mint","Solid Tahiti Blue","Solid Light Orange","Solid Warm Gray"],"M"),
   "polo":(1402,["left_chest"],["White","Athletic Heather"],"M"),
   "wpolo":(6488,["left_chest_dtf"],["White","Platinum","Charity Pink"],"M"),
   "cap_dad":(1447,["front_dtf"],["White","Khaki","Stone","Light Blue","Pink"],"One size"),
   "cap_foam":(1735,["front_dtf"],["White","Light Pink/White","Blue/White"],"One size"),
   "cap_mesh":(1734,["front_dtf"],["White"],"One size")}
dot=png(64,64,[0,0,0,0]); dotid=up("dot.png",dot)
os.makedirs("out/blanks2",exist_ok=True); man=[]; meta={}
made={}
for k,(bp,poss,cols,size) in P.items():
    vs=pf("GET",f"/v1/catalog/blueprints/{bp}/print_providers/99/variants.json")["variants"]
    sel=[v for v in vs if v["options"].get("color") in cols and (v["options"].get("size") in (size,None) or size=="One size")]
    seen=set(); s2=[]
    for v in sel:
        c=v["options"].get("color")
        if c in seen: continue
        seen.add(c); s2.append(v)
    ids=[v["id"] for v in s2]; areas={ph["position"]:[ph["width"],ph["height"]] for ph in s2[0]["placeholders"]}
    meta[k]={"bp":bp,"positions":poss,"areas":{p:areas[p] for p in poss},"colors":{str(v["id"]):v["options"].get("color") for v in s2},"missing":[c for c in cols if c not in seen]}
    marks={}
    for p in poss:
        W,H=areas[p]; marks[p]=up(f"mark_{k}_{p}.png",png(max(8,W//10),max(8,H//10),[255,0,255,255]))
    for kind in ("blank","calib"):
        ph=[{"position":p,"images":[{"id":(dotid if kind=="blank" else marks[p]),"x":0.5,"y":0.5,"scale":(0.05 if kind=="blank" else 1.0),"angle":0}]} for p in poss]
        pr=pf("POST",f"/v1/shops/{SHOP}/products.json",{"title":f"BLANK mockup source - do not publish {k} {kind}","description":"blank","blueprint_id":bp,"print_provider_id":99,
            "variants":[{"id":i,"price":3000,"is_enabled":True} for i in ids],"print_areas":[{"variant_ids":ids,"placeholders":ph}]})
        made[(k,kind)]=pr["id"]; print("created",k,kind,flush=True); time.sleep(2)
time.sleep(120)
for (k,kind),pid in made.items():
    p=pf("GET",f"/v1/shops/{SHOP}/products/{pid}.json")
    for i,imx in enumerate(p["images"]):
        cols=sorted({meta[k]["colors"].get(str(v),"?") for v in imx.get("variant_ids",[])})
        fn=f"out/blanks2/{k}_{kind}_{i:02d}.jpg"
        try: open(fn,"wb").write(urllib.request.urlopen(urllib.request.Request(imx["src"],headers={"User-Agent":"a"}),timeout=60).read())
        except Exception as e: print("ERR",e); continue
        man.append({"file":fn,"prod":k,"kind":kind,"position":imx.get("position"),"colors":cols,"default":imx.get("is_default")})
json.dump({"meta":meta,"images":man,"products":{f"{a}|{b}":v for (a,b),v in made.items()}},open("out/blanks2/manifest.json","w"),indent=1); print("DONE",len(man))
