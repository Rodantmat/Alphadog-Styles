"""Fulfil paid store orders: store Worker -> print files -> Printify order -> production -> tracking back to the store.
Runs in GitHub Actions every 10 minutes. Env: PRINTIFY_TOKEN, PRINTIFY_API_SHOP_ID, STORE_URL, STORE_ADMIN_TOKEN."""
import os,sys,json,io,re,base64,time,urllib.request,urllib.error
import cairosvg
from PIL import Image
T=os.environ["PRINTIFY_TOKEN"]; SHOP=os.environ.get("PRINTIFY_API_SHOP_ID","").strip(); STORE=os.environ.get("STORE_URL","").rstrip("/"); ADM=os.environ.get("STORE_ADMIN_TOKEN","")
if not (SHOP and STORE and ADM): print("store fulfilment not configured yet (need PRINTIFY_API_SHOP_ID, STORE_URL, STORE_ADMIN_TOKEN) - nothing to do"); sys.exit(0)
def pf(m,p,b=None):
    for a in range(6):
        r=urllib.request.Request("https://api.printify.com"+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:500]
            if e.code in (429,500,502,503,504) and a<5: time.sleep(30*(a+1)); continue
            raise RuntimeError(f"Printify {e.code} {p}: {msg}")
def st(m,p,b=None):
    r=urllib.request.Request(STORE+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"x-admin-token":ADM,"content-type":"application/json","User-Agent":"a"})
    return json.load(urllib.request.urlopen(r,timeout=60))
AR={"tee":{"front":(2767,3362),"back":(2767,3362)},"hoodie":{"front":(3531,2352),"back":(3852,3210)}}; HB=0.77; BP={"tee":12,"hoodie":77}
RULE={"tee":"tee","hoodie":"hoodie"}; POS={}
cat=json.load(open("store/data/catalog.json"))
for _p in cat["products"]:
    BP[_p["id"]]=_p["blueprint"]
    if _p.get("area"): AR[_p["id"]]={k:tuple(v) for k,v in _p["area"].items()}
    if _p.get("rule"): RULE[_p["id"]]=_p["rule"]
    POS[_p["id"]]=_p.get("pos") or {"front":"front","back":"back"}
def fit(prod,side,size,a):  # identical to store/js/placement.js
    W,H=AR[prod][side]; x=.5; y=.5; rule=RULE.get(prod,"tee")
    if rule in("chest","cap"):
        k=.92 if rule=="cap" else .9; w=min(k,k*H*a/W); h=w*W/a/H
    elif side=="back":
        if size=="s": w=min(.32*3185/W,.30*H*a/W); h=w*W/a/H; y=.04+h/2
        elif rule=="hoodie": w=min(.97,HB*H*a/W); h=w*W/a/H; y=1-h/2-.005
        else: w=min(.97,.97*H*a/W); h=w*W/a/H
    elif size=="s":
        w=min((.26 if rule=="hoodie" else .30)*3185/W,.30*H*a/W); h=w*W/a/H; x=.76; y=.05+h/2 if rule=="hoodie" else .17
    else:
        w=min(.58 if rule=="hoodie" else .75,.95*H*a/W); h=w*W/a/H; y=min(.5,.04+h/2)
    return x,y,w,h
def custom_art(d):  # owner-uploaded custom art (SVG text or PNG) from the store
    r=urllib.request.Request(STORE+f"/api/internal/custom/{d['custom']}/art/{d['part']}",headers={"x-admin-token":ADM,"User-Agent":"a"})
    resp=urllib.request.urlopen(r,timeout=60); return resp.headers.get("content-type",""),resp.read()
def compose(prod,side,d):
    W,H=AR[prod][side]
    if d.get("custom"):
        ct,raw=custom_art(d)
        if "svg" in ct: svg=raw.decode()
        else:
            src=Image.open(io.BytesIO(raw)).convert("RGBA"); a=src.width/src.height; x,y,w,h=fit(prod,side,d["size"],a)
            pw=int(w*W); ph=int(pw/a); art=src.resize((pw,ph),Image.LANCZOS); can=Image.new("RGBA",(W,H),(0,0,0,0))
            can.paste(art,(int(x*W-pw/2),int(y*H-ph/2)),art); o=io.BytesIO(); can.save(o,"PNG",optimize=True); return o.getvalue()
    else: svg=open(f"store/art/{d['theme']}_{d['style']}/{d['breed']}_{'front' if d['part']=='head' else 'back'}.svg").read()
    m=re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"',svg)
    if m: a=float(m[1])/float(m[2])
    else:
        mw=re.search(r'<svg[^>]*\swidth="([\d.]+)',svg); mh=re.search(r'<svg[^>]*\sheight="([\d.]+)',svg); a=float(mw[1])/float(mh[1])
    x,y,w,h=fit(prod,side,d["size"],a)
    pw=int(w*W); ph=int(pw/a); png=cairosvg.svg2png(bytestring=svg.encode(),output_width=pw,output_height=ph)
    art=Image.open(io.BytesIO(png)).convert("RGBA"); can=Image.new("RGBA",(W,H),(0,0,0,0))
    can.paste(art,(int(x*W-pw/2),int(y*H-ph/2)),art); o=io.BytesIO(); can.save(o,"PNG",optimize=True)
    return o.getvalue()
_var={}
def variant(prod,color,size):
    if prod not in _var: _var[prod]=pf("GET",f"/v1/catalog/blueprints/{BP[prod]}/print_providers/99/variants.json")["variants"]
    for v in _var[prod]:
        if v["options"].get("color")==color and v["options"].get("size")==size: return v["id"]
    raise RuntimeError(f"no variant {prod} {color} {size}")
def upload(name,png):
    r=pf("POST","/v1/uploads/images.json",{"file_name":name,"contents":base64.b64encode(png).decode()}); return r["preview_url"]
neck=json.load(open("out/neck_ids.json")) if os.path.exists("out/neck_ids.json") else {}
def neck_url(prod):
    try: return pf("GET",f"/v1/uploads/{neck['blackink']}.json")["preview_url"]
    except Exception: return None
PRODS={p["id"]:p for p in cat["products"]}; _lab={}
def label_url(prod,lab):  # AlphaDog logo label: full-size canvas for the label area with the logo placed like the product listings
    if prod in _lab: return _lab[prod]
    W,H=lab["area"]; logo=Image.open("shop/brand/neck_blackink.png").convert("RGBA"); w=int(lab["scale"]*W); logo=logo.resize((w,int(w*logo.height/logo.width)),Image.LANCZOS)
    can=Image.new("RGBA",(W,H),(0,0,0,0)); can.paste(logo,(int(lab["x"]*W-logo.width/2),int(lab["y"]*H-logo.height/2)),logo)
    o=io.BytesIO(); can.save(o,"PNG"); _lab[prod]=upload(f"label_{prod}.png",o.getvalue()); return _lab[prod]
def build(o):
    items=[]; d=o["data"]; s=d["ship"]; nm=s["name"].split(" ",1)
    for i,it in enumerate(o["data"]["items"]):
        pa={}
        for side in ("front","back"):
            if it.get(side): pa[POS[it["prod"]][side]]=upload(f"{o['id']}_{i}_{side}.png",compose(it["prod"],side,it[side]))
        lab=PRODS[it["prod"]].get("label")
        if lab: pa[lab["pos"]]=label_url(it["prod"],lab)
        items.append({"print_provider_id":99,"blueprint_id":BP[it["prod"]],"variant_id":variant(it["prod"],it["color"],it["size"]),"print_areas":pa,"quantity":it["qty"]})
    body={"external_id":o["id"],"label":o["id"],"line_items":items,"shipping_method":1,"is_printify_express":False,"send_shipping_notification":not d.get("source"),
      "address_to":{"first_name":nm[0],"last_name":nm[1] if len(nm)>1 else ".","email":o["email"] or "orders@alphadogstyles.com","phone":s.get("phone") or "","country":s.get("country") or "US","region":s.get("st") or "","address1":s["a1"],"address2":s.get("a2",""),"city":s["city"],"zip":s["zip"]}}
    return body
def fulfil(o):
    body=build(o)
    r=pf("POST",f"/v1/shops/{SHOP}/orders.json",body)
    pf("POST",f"/v1/shops/{SHOP}/orders/{r['id']}/send_to_production.json",{})
    st("POST",f"/api/internal/orders/{o['id']}",{"status":"in_production","printify_id":r["id"]}); print("sent",o["id"],r["id"],flush=True)
for o in st("GET","/api/internal/orders?status=paid_test")["items"]:  # Stripe TEST payments: build every print file to prove the pipeline, never touch Printify
    try:
        for i,it in enumerate(o["data"]["items"]):
            for side in ("front","back"):
                if it.get(side): assert len(compose(it["prod"],side,it[side]))>1000; variant(it["prod"],it["color"],it["size"])
            assert it["prod"] in PRODS
        if os.environ.get("DRY_PRINTIFY","1")=="1":  # full payload incl. uploaded print files, priced by Printify's shipping quote: creates NO order, NO charge
            b=build({**o,"data":{**o["data"],"source":o["data"].get("source") or {"test":1}}}); q=pf("POST",f"/v1/shops/{SHOP}/orders/shipping.json",{"line_items":b["line_items"],"address_to":b["address_to"]}); assert q, "empty shipping quote"; print("printify quote ok",o["id"],json.dumps(q)[:160],flush=True)
        st("POST",f"/api/internal/orders/{o['id']}",{"status":"test_complete"}); print("test order verified",o["id"],flush=True)
    except Exception as e: print("TEST FAILED",o["id"],e,flush=True); st("POST",f"/api/internal/orders/{o['id']}",{"status":"test_failed"})
PAUSED=st("GET","/api/internal/kv/fulfil_paused").get("v")=="1" or os.environ.get("ONLY_TEST")=="1"
if PAUSED: print("fulfilment PAUSED by owner - paid orders wait",flush=True)
for o in ([] if PAUSED else st("GET","/api/internal/orders?status=paid")["items"]):
    try: fulfil(o)
    except Exception as e: print("FAILED",o["id"],e,flush=True); st("POST",f"/api/internal/orders/{o['id']}",{"status":"needs_attention"})
for o in ([] if os.environ.get("ONLY_TEST")=="1" else st("GET","/api/internal/orders?status=in_production")["items"]):
    try:
        p=pf("GET",f"/v1/shops/{SHOP}/orders/{o['printify_id']}.json"); sh=p.get("shipments") or []
        if sh and sh[0].get("url"):
            st("POST",f"/api/internal/orders/{o['id']}",{"status":"shipped","tracking":sh[0]["url"]}); print("shipped",o["id"])
            src=(o.get("data") or {}).get("source")
            if src:  # marketplace order: give the buyer's marketplace the tracking number
                try:
                    import market_orders; print("marketplace tracking",market_orders.push_tracking(src["plat"],src["ext_id"],sh[0].get("carrier",""),sh[0].get("number","")))
                except Exception as e: print("marketplace tracking error",o["id"],e)
    except Exception as e: print("track error",o["id"],e)
st("POST","/api/internal/kv/fulfil_last",{"v":int(time.time()*1000)})
print("DONE")
