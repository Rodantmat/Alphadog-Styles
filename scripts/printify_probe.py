"""Cost probe: create one DRAFT product per candidate blank in the API shop (never published) and read Printify's real costs.
Products are titled 'COST PROBE - do not publish'."""
import os,json,urllib.request,urllib.error,time,base64,zlib,struct
T=os.environ["PRINTIFY_TOKEN"]; SHOP=29559517
def pf(m,p,b=None):
    for a in range(6):
        r=urllib.request.Request("https://api.printify.com"+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:400]
            if e.code in(429,500,502,503) and a<5: time.sleep(25*(a+1)); continue
            raise RuntimeError(f"{e.code} {p} {msg}")
def png(w=600,h=600):
    raw=b"".join(b"\x00"+bytes([0,0,0,255]*w) if (y//20)%2==0 else b"\x00"+bytes([0,0,0,0]*w) for y in range(h))
    ch=lambda t,d: struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    return b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))+ch(b"IDAT",zlib.compress(raw))+ch(b"IEND",b"")
img=pf("POST","/v1/uploads/images.json",{"file_name":"probe.png","contents":base64.b64encode(png()).decode()})["id"]
C=[("tank_bc3480",39,"front"),("tank_gildan5200",880,"front"),("tank_cc9360",1459,"front"),("wtank_nl1533",18,"front"),("wtank_bc6008",3038,"front_dtg"),
   ("polo_core365_m",6497,"left_chest_dtf"),("polo_core365_w",6488,"left_chest_dtf"),("polo_jerzees_m",1402,"left_chest"),("polo_lk8000_w",3393,"left_chest_dtf"),
   ("cap_dad_6245",1447,"front_dtf"),("cap_trucker_6006",1734,"front_dtf"),("cap_foam_39165",1735,"front_dtf"),("cap_mid_31069",2041,"front_dtf")]
out={}
for name,bp,pos in C:
    try:
        vs=pf("GET",f"/v1/catalog/blueprints/{bp}/print_providers/99/variants.json")["variants"][:100]
        ids=[v["id"] for v in vs]
        body={"title":"COST PROBE - do not publish "+name,"description":"probe","blueprint_id":bp,"print_provider_id":99,
              "variants":[{"id":i,"price":9999,"is_enabled":True} for i in ids],
              "print_areas":[{"variant_ids":ids,"placeholders":[{"position":pos,"images":[{"id":img,"x":0.5,"y":0.5,"scale":0.6,"angle":0}]}]}]}
        p=pf("POST",f"/v1/shops/{SHOP}/products.json",body)
        p=pf("GET",f"/v1/shops/{SHOP}/products/{p['id']}.json")
        vmap={v["id"]:v for v in vs}; rows={}
        for v in p["variants"]:
            o=vmap.get(v["id"],{}).get("options",{}); rows[f'{o.get("color")}|{o.get("size")}']=v["cost"]
        out[name]={"bp":bp,"pos":pos,"product":p["id"],"costs":rows,"images":[i["src"] for i in p.get("images",[])[:4]]}
        print(name,"min",min(rows.values()),"max",max(rows.values()),flush=True)
    except Exception as e: out[name]={"err":str(e)[:300]}; print(name,"ERR",e,flush=True)
    time.sleep(3)
json.dump(out,open("out/probe.json","w"),indent=1)
