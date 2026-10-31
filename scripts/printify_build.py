"""Create UNPUBLISHED Printify drafts. env: SHOP, CHANNEL(etsy|ebay|tiktok), BREEDS (n top breeds), DESIGNS (csv), PRODUCTS (tee,hoodie), LAYOUT, MAXN"""
import os, json, base64, urllib.request, urllib.error, time, sys
T=os.environ["PRINTIFY_TOKEN"]; SHOP=int(os.environ["SHOP"]); CH=os.environ.get("CHANNEL","etsy")
NB=int(os.environ.get("BREEDS","10")); DESIGNS=os.environ.get("DESIGNS","line_classic,line_cool,line_heart").split(",")
PRODS=os.environ.get("PRODUCTS","tee,hoodie").split(","); LAYOUTS=os.environ.get("LAYOUT","pair").split(","); MAXN=int(os.environ.get("MAXN","1000"))
def call(method,path,body=None,retry=3):
    for a in range(retry):
        data=json.dumps(body).encode() if body is not None else None
        r=urllib.request.Request("https://api.printify.com"+path,data=data,method=method,
            headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"alphadog"})
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:600]
            if e.code in (429,500,502,503) and a<retry-1: time.sleep(10*(a+1)); continue
            print("HTTP",e.code,msg); raise
V=json.load(open("out/printify_variants.json"))
BREEDS=json.load(open("scripts/breeds25.json"))[:NB]
LIGHT={"tee":["White","Natural","Sand","Sport Grey","Ice Grey","Light Blue","Light Pink"],
       "hoodie":["White","Sand","Sport Grey","Light Blue","Light Pink","Ash"]}
DARK={"tee":["Black","Navy","Charcoal","Dark Heather","Forest Green","Maroon","Heather Navy","Military Green","Dark Chocolate"],
      "hoodie":["Black","Navy","Charcoal","Dark Heather","Forest Green","Maroon","Heather Navy","Military Green","Dark Chocolate"]}
if CH=="etsy":
    LIGHT["tee"]=LIGHT["tee"][:5]; DARK["tee"]=DARK["tee"][:6]
    LIGHT["hoodie"]=LIGHT["hoodie"][:4]; DARK["hoodie"]=DARK["hoodie"][:6]
BP={"tee":(145,"145"),"hoodie":(77,"77")}
SIZES={"tee":["S","M","L","XL","2XL","3XL"],"hoodie":["S","M","L","XL","2XL","3XL"]}
PRICE={"tee":{"S":2799,"M":2799,"L":2799,"XL":2799,"2XL":2999,"3XL":3199},
       "hoodie":{"S":4999,"M":4999,"L":4999,"XL":4999,"2XL":5399,"3XL":5799}}
AREA={"tee":{"front":(3185,3636),"back":(3185,3636)},"hoodie":{"front":(2919,1944),"back":(3033,2528)}}
ASP={"front":1169/1200,"back":4471/5400}
def place(prod,side,kind):
    W,H=AREA[prod][side]; a=ASP[side]
    if kind=="pocket":   # small head emblem, wearer's left chest
        w=0.30*3185/W if prod=="tee" else 0.26; h=w*W/a/H
        return dict(x=0.76,y=round(0.05+h/2 if prod=="hoodie" else 0.17,3),scale=round(w,3))
    if kind=="back":
        hh=0.95; w=hh*H*a/W; w=min(w,0.95)
        return dict(x=0.5,y=0.5,scale=round(w,3))
    if kind=="bighead":
        w=0.75 if prod=="tee" else 0.5; h=w*W/a/H
        return dict(x=0.5,y=round(min(0.5, 0.04+h/2),3),scale=w)
THEME={"line":"Continuous Line Art","geo":"Geometric"}; VAR={"classic":"Classic","cool":"Cool","heart":"Heart"}
PNAME={"tee":"T-Shirt","hoodie":"Hoodie"}
STATE="out/state_%s.json"%CH
state=json.load(open(STATE)) if os.path.exists(STATE) else {}
uploads=json.load(open("out/uploads.json")) if os.path.exists("out/uploads.json") else {}
import io
def art_bytes(slug,des,side,ink):
    p=f"shop/art/{slug}/{des}/{side}_{ink}.png"
    if os.path.exists(p): return open(p,"rb").read()
    import cairosvg
    from PIL import Image
    base="back" if side=="back" else "front"
    w={"front":1169,"frontbig":2400,"back":4471}[side]
    png=cairosvg.svg2png(url=f"shop/svg/{des}/{slug}_{base}.svg",output_width=w)
    if ink=="whiteink":
        im=Image.open(io.BytesIO(png)).convert("RGBA"); a=im.split()[3]
        im=Image.merge("RGBA",(a.point(lambda v:255),a.point(lambda v:255),a.point(lambda v:255),a)); o=io.BytesIO(); im.save(o,"PNG"); png=o.getvalue()
    return png
def upload(slug,des,side,ink):
    k=f"{slug}/{des}/{side}_{ink}"
    if k in uploads: return uploads[k]
    b=base64.b64encode(art_bytes(slug,des,side,ink)).decode()
    r=call("POST","/v1/uploads/images.json",{"file_name":f"{slug}_{des}_{side}_{ink}.png","contents":b})
    uploads[k]=r["id"]; json.dump(uploads,open("out/uploads.json","w")); return r["id"]
made=0
for LAYOUT in LAYOUTS:
 for slug,disp,desc in BREEDS:
  for des in DESIGNS:
    th,vr=des.split("_")
    for prod in PRODS:
      key=f"{slug}|{des}|{prod}|{LAYOUT}"
      if key in state: continue
      if made>=MAXN: break
      bp,bk=BP[prod]
      vs=[v for v in V[bk]["variants"] if v["options"]["size"] in SIZES[prod]]
      lv=[v for v in vs if v["options"]["color"] in LIGHT[prod]]; dv=[v for v in vs if v["options"]["color"] in DARK[prod]]
      def pa(vl,ink):
        ph=[]
        if LAYOUT in("pair","pocket"):
            ph.append({"position":"front","images":[dict(id=upload(slug,des,"front",ink),angle=0,**place(prod,"front","pocket"))]})
        if LAYOUT=="portrait":
            ph.append({"position":"front","images":[dict(id=upload(slug,des,"frontbig",ink),angle=0,**place(prod,"front","bighead"))]})
        if LAYOUT=="pair":
            ph.append({"position":"back","images":[dict(id=upload(slug,des,"back",ink),angle=0,**place(prod,"back","back"))]})
        return {"variant_ids":[v["id"] for v in vl],"placeholders":ph}
      variants=[{"id":v["id"],"price":PRICE[prod][v["options"]["size"]],"is_enabled":True} for v in lv+dv]
      lay={"pair":"Pocket Portrait + Full Body Back","pocket":"Pocket Portrait","portrait":"Portrait"}[LAYOUT]
      title=f"{disp} {THEME[th]} {VAR[vr]} Dog Lover {PNAME[prod]} | {lay}"
      if CH!="etsy":
          ls={"pair":"Front & Back","pocket":"Pocket Print","portrait":"Big Portrait"}[LAYOUT]; ts={"line":"Line Art","geo":"Geometric"}[th]
          title=f"{disp} {PNAME[prod]} Dog Lover {ts} {VAR[vr]} {ls}"
          if len(title)>80: title=f"{disp} {PNAME[prod]} Dog {ts} {VAR[vr]} {ls}"
          if len(title)>80: title=title[:80].rsplit(" ",1)[0]
      body={"title":title,
        "description":f"<p>{disp} dog lover {PNAME[prod].lower()} with {THEME[th].lower()} artwork, {VAR[vr].lower()} style. Layout: {lay.lower()}.</p><p>Unisex fit, soft and comfortable. Made to order and printed in the USA/EU by a Printify partner; allow about 10 business days to produce before shipping.</p><p>Art style: black ink on light colors, white ink on dark colors.</p>",
        "blueprint_id":bp,"print_provider_id":99,"variants":variants,
        "print_areas":[x for x in (pa(lv,"blackink") if lv else None, pa(dv,"whiteink") if dv else None) if x],
        "tags":[t[:20] for t in [disp.lower(),"dog lover shirt" if prod=="tee" else "dog lover hoodie","dog mom gift","dog dad gift","dog breed shirt","line art dog","minimalist dog","pet lover gift","dog owner gift","unisex "+PNAME[prod].lower(),"dog portrait","gift for dog lover","dog art"]][:13]}
      p=call("POST",f"/v1/shops/{SHOP}/products.json",body)
      state[key]={"id":p["id"],"title":title,"variants":len([x for x in p["variants"] if x.get("is_enabled")])}
      json.dump(state,open(STATE,"w"),indent=1); made+=1
      print("OK",key,p["id"],state[key]["variants"],flush=True)
      time.sleep(0.4)
print("made",made,"total",len(state))
