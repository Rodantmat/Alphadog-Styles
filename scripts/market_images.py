"""Listing photos for the consolidated marketplace listings, rendered exactly like the store preview
(real blank-garment photo + art multiplied at 93% into the calibrated print box, js/garment.js + placement.js).
Writes store/mk/<prod>/<breed>/<design><color>.jpg (+ hero/lineup per listing) and store/data/market_images.json.
Runs at deploy time (files are not committed). Usage: python3 scripts/market_images.py [--only LISTING_ID] [--limit N]"""
import json,os,io,sys,hashlib
from concurrent.futures import ProcessPoolExecutor
from PIL import Image,ImageDraw,ImageFont
import cairosvg
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cat=json.load(open(f"{ROOT}/store/data/catalog.json")); plan=json.load(open(f"{ROOT}/store/data/market_plan.json"))
CAL=cat["cal"]; PH=CAL["photo"]; OUT=f"{ROOT}/store/mk"
AR={"tee":{"front":(2767,3362),"back":(2767,3362)},"hoodie":{"front":(3531,2352),"back":(3852,3210)}}; RULE={"tee":"tee","hoodie":"hoodie"}; HB=0.77
for p in cat["products"]:
    if p.get("area"): AR[p["id"]]={k:tuple(v) for k,v in p["area"].items()}
    if p.get("rule"): RULE[p["id"]]=p["rule"]
PROD={p["id"]:p for p in cat["products"]}
def fit(prod,side,size,a):
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
_art={}
def art(theme_style,breed,part,wpx):
    k=(theme_style,breed,part,wpx)
    if k not in _art:
        svg=open(f"{ROOT}/store/art/{theme_style}/{breed}_{'front' if part=='head' else 'back'}.svg","rb").read()
        im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg,output_width=wpx))).convert("RGBA"); _art[k]=im
    return _art[k]
def slug_of(prod,color): return next(c[3] for c in PROD[prod]["colors"] if c[0]==color)
def side_img(prod,color,side,d):
    """d = {"part","size","art"} or None -> 1200px RGB"""
    base=Image.open(f"{ROOT}/store/img/{prod}_{slug_of(prod,color)}_{side}.webp").convert("RGB")
    if base.size!=(PH,PH): base=base.resize((PH,PH),Image.LANCZOS)
    if d:
        svg=open(f"{ROOT}/store/art/{d['art']}/{d['breed']}_{'front' if d['part']=='head' else 'back'}.svg","rb").read()
        probe=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg,output_width=64))); a=probe.width/probe.height
        ax,ay,aw,ah=CAL[prod][side]; x,y,w,h=fit(prod,side,d["size"],a)
        wpx=max(8,round(w*aw)); hpx=max(8,round(wpx/a)); cx=ax+x*aw; cy=ay+y*ah
        im=art(d["art"],d["breed"],d["part"],wpx).resize((wpx,hpx),Image.LANCZOS)
        x0,y0=round(cx-wpx/2),round(cy-hpx/2)
        region=base.crop((x0,y0,x0+wpx,y0+hpx)).convert("RGB")
        r=Image.new("RGB",(wpx,hpx),(255,255,255)); r.paste(im,(0,0),im)
        mult=Image.composite(Image.fromarray(__import__("numpy").uint8(__import__("numpy").asarray(region,dtype="float32")*__import__("numpy").asarray(r,dtype="float32")/255)),region,im.getchannel("A").point(lambda v:int(v*.93)))
        base.paste(mult,(x0,y0))
    return base
def opt(o,breed,art_):
    if not o: return None
    return {"part":"head" if o.startswith("head") else "body","size":o[-1],"breed":breed,"art":art_}
def render(job):
    """job: (path, prod, color, breed, design dict) -> writes jpg"""
    path,prod,color,breed,d=job
    full=f"{OUT}/{path}"
    if os.path.exists(full): return path
    os.makedirs(os.path.dirname(full),exist_ok=True)
    fo,bo=opt(d["front"],breed,d["art"]),opt(d["back"],breed,d["art"])
    if fo:
        im=side_img(prod,color,"front",fo)
        if bo:  # back view as an inset, bottom-right
            bk=side_img(prod,color,"back",bo).resize((500,500),Image.LANCZOS)
            fr=Image.new("RGB",(512,512),(255,255,255)); fr.paste(bk,(6,6))
            dr=ImageDraw.Draw(fr); dr.rectangle((0,0,511,511),outline=(210,210,210),width=3)
            im.paste(fr,(PH-512-24,PH-512-24))
    else:
        im=side_img(prod,color,"back",bo)
    im.save(full,"JPEG",quality=84,optimize=True,progressive=True)
    return path
def lineup(path,prod_colors,breed,d,label):
    """grid of the same design on every color of a listing"""
    full=f"{OUT}/{path}"
    if os.path.exists(full): return path
    n=len(prod_colors); cols=3 if n>4 else 2 if n>1 else 1; rows=(n+cols-1)//cols
    cell=PH//cols; im=Image.new("RGB",(PH,max(PH,rows*cell)),(255,255,255))
    for i,(prod,color,name) in enumerate(prod_colors):
        fo=opt(d["front"] or d["back"],breed,d["art"]); side="front" if d["front"] else "back"
        t=side_img(prod,color,side,fo).resize((cell,cell),Image.LANCZOS)
        im.paste(t,((i%cols)*cell,(i//cols)*cell))
        dr=ImageDraw.Draw(im)
        try: f=ImageFont.truetype("DejaVuSans-Bold.ttf",max(18,cell//16))
        except Exception: f=ImageFont.load_default()
        dr.text(((i%cols)*cell+cell//2,(i//cols)*cell+cell-14),name,fill=(60,60,60),font=f,anchor="ms")
    if im.height!=PH: im=im.resize((PH,PH),Image.LANCZOS) if rows*cell<PH*1.2 else im
    os.makedirs(os.path.dirname(full),exist_ok=True); im.save(full,"JPEG",quality=84,optimize=True); return path
def plan_jobs(only=None):
    jobs={}; meta={}; seen={}
    def hero_color(L,C):
        # main-photo color: the color this platform has shown least so far for this product (all colors take turns, white included),
        # so a storefront looks mixed instead of mostly white. Every color stays a buyable option.
        k=(L["plat"],L["prod"]); use=seen.setdefault(k,{})
        isw=lambda c:"white" in C[c]["color"].lower() and "/" not in C[c]["color"]
        c=min(L["colors"],key=lambda c:(use.get(c,0)+(0.5 if isw(c) else 0),L["colors"].index(c)))
        use[c]=use.get(c,0)+1; return c
    for L in plan["listings"]:
        if only and L["id"]!=only: continue
        P=plan["products"][L["prod"]]; D={d["code"]:d for d in P["designs"]}; C={c["code"]:c for c in P["colors"]}
        hero_c=C[hero_color(L,C)]; m={"hero":[],"bd":{},"bdc":{},"lineup":None}
        def key(b,dc,cc):
            c=C[cc]; return f"{c['prod']}/{b}/{dc}{cc}.jpg",(c["prod"],c["color"],b,D[dc])
        for b in L["breeds"]:
            for dc in L["designs"]:
                p,j=key(b,dc,hero_c["code"]); jobs[p]=(p,)+j; m["bd"][f"{b}|{dc}"]=p
                if L["plat"]=="tiktok":
                    for cc in L["colors"]:
                        p2,j2=key(b,dc,cc); jobs[p2]=(p2,)+j2; m["bdc"][f"{b}|{dc}|{cc}"]=p2
        if L["plat"]=="ebay":   # eBay variation pictures change with Color
            for cc in L["colors"]:
                p2,j2=key(L["breeds"][0],L["designs"][0],cc); jobs[p2]=(p2,)+j2; m["bdc"][f"{L['breeds'][0]}|{L['designs'][0]}|{cc}"]=p2
        # hero images: first breed x first 3 designs, then other breeds design 1
        hero=[m["bd"][f"{L['breeds'][0]}|{dc}"] for dc in L["designs"][:6]]+[m["bd"][f"{b}|{L['designs'][0]}"] for b in L["breeds"][1:]]
        m["hero"]=hero
        lp=f"lineup/{L['prod']}_{L['breeds'][0]}_{L['designs'][0]}_{''.join(L['colors'])}.jpg"
        m["lineup"]=(lp,[(C[c]["prod"],C[c]["color"],C[c]["name"]) for c in L["colors"]],L["breeds"][0],D[L["designs"][0]])
        meta[L["id"]]=m
    return jobs,meta
if __name__=="__main__":
    only=None; lim=None
    if "--only" in sys.argv: only=sys.argv[sys.argv.index("--only")+1]
    if "--limit" in sys.argv: lim=int(sys.argv[sys.argv.index("--limit")+1])
    jobs,meta=plan_jobs(only); js=list(jobs.values())[:lim]
    print("images to render:",len(jobs),"(this run",len(js),")")
    with ProcessPoolExecutor(max_workers=os.cpu_count() or 2) as ex:
        for i,_ in enumerate(ex.map(render,js,chunksize=8)):
            if i%200==0: print(" ",i,flush=True)
    out={}
    for lid,m in meta.items():
        lp,pc,b,d=m["lineup"]; lineup(lp,pc,b,d,lid)
        out[lid]={"hero":m["hero"],"lineup":lp,"bd":m["bd"],"bdc":m["bdc"]}
    if not only: json.dump(out,open(f"{ROOT}/store/data/market_images.json","w"),separators=(",",":"))
    print("done")
