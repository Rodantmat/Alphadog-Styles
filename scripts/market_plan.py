"""Consolidated marketplace listings (not linked to Printify): few listings per product, breeds grouped by family,
designs / colors / sizes as variations, filled up to each marketplace's variation cap.
Every variation gets a SKU that the order bridge decodes back into a store order item (store/worker validItem format).
Output: store/data/market_plan.json  (also used by the Worker to decode marketplace orders)."""
import json,math,os,re
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cat=json.load(open(f"{ROOT}/store/data/catalog.json"))
BR={b["slug"]:b["name"] for b in cat["breeds"]}
# popularity order (AKC 2025 + search demand) - order of store catalog = breeds25 order
POP=[b["slug"] for b in cat["breeds"]]
SHORT={"french_bulldog":"Frenchie","labrador_retriever":"Labrador","golden_retriever":"Golden Retriever","german_shepherd":"German Shepherd",
 "german_shorthaired_pointer":"GSP Pointer","cavalier_king_charles_spaniel":"Cavalier KCS","yorkshire_terrier":"Yorkie","australian_shepherd":"Aussie",
 "doberman_pinscher":"Doberman","pembroke_welsh_corgi":"Corgi","miniature_schnauzer":"Mini Schnauzer","bernese_mountain_dog":"Bernese",
 "american_pit_bull_terrier":"Pit Bull","mini_poodle":"Mini Poodle","boston_terrier":"Boston Terrier","bichon_frise":"Bichon Frise","siberian_husky":"Husky"}
short=lambda s:SHORT.get(s,BR[s])
CODE={"french_bulldog":"FB","labrador_retriever":"LR","golden_retriever":"GR","german_shepherd":"GS","dachshund":"DA","poodle":"PO","beagle":"BE",
 "rottweiler":"RO","german_shorthaired_pointer":"GP","bulldog":"BU","cane_corso":"CC","cavalier_king_charles_spaniel":"CK","yorkshire_terrier":"YT",
 "australian_shepherd":"AS","doberman_pinscher":"DP","pembroke_welsh_corgi":"CO","miniature_schnauzer":"MS","boxer":"BX","pomeranian":"PM",
 "bernese_mountain_dog":"BM","shih_tzu":"ST","great_dane":"GD","boston_terrier":"BT","chihuahua":"CH","havanese":"HV","siberian_husky":"SH",
 "pug":"PU","american_pit_bull_terrier":"PB","border_collie":"BC","shiba_inu":"SI","mini_poodle":"MP","bichon_frise":"BF","maltese":"MA"}
assert set(CODE)==set(BR), set(BR)^set(CODE)
# breed families (shoppers of similar breeds browse together; titles stay coherent)
FAM=[("Bulldog",["french_bulldog","bulldog","boston_terrier","pug"]),
     ("Retriever",["labrador_retriever","golden_retriever"]),
     ("Herding",["german_shepherd","australian_shepherd","border_collie","pembroke_welsh_corgi"]),
     ("Guardian",["rottweiler","doberman_pinscher","cane_corso","great_dane"]),
     ("Snow & Mountain",["siberian_husky","bernese_mountain_dog","shiba_inu","pomeranian"]),
     ("Hound & Pointer",["dachshund","beagle","german_shorthaired_pointer"]),
     ("Poodle & Fluffy",["poodle","mini_poodle","bichon_frise","maltese"]),
     ("Toy",["yorkshire_terrier","shih_tzu","havanese","chihuahua"]),
     ("Bully",["american_pit_bull_terrier","boxer"]),
     ("Spaniel & Terrier",["cavalier_king_charles_spaniel","miniature_schnauzer"])]
assert sorted(sum([f[1] for f in FAM],[]))==sorted(BR)
MERGE=[(8,0),(9,5),(7,6),(4,3),(1,2)]   # family merges used when fewer than 10 listings: bully+bulldog, spaniel+hound, toy+poodle, snow+guardian, retriever+herding
W={s:1/(i+1)**0.8 for i,s in enumerate(POP)}
def groups(n):
    g=[list(f[1]) for f in FAM]
    if n<len(g):
        for a,b in MERGE:
            if len(g)<=n: break
            g[b]=g[b]+g[a]; g[a]=None
            g=[x for x in g]  # keep indexes stable until done
        g=[x for x in g if x]
        while len(g)>n:  # still too many: merge two smallest
            g.sort(key=len); g=[g[0]+g[1]]+g[2:]
    while len(g)<n:      # split the most-demanded multi-breed group: its most popular breed gets its own listing
        multi=[x for x in g if len(x)>1]
        if not multi: break
        x=max(multi,key=lambda x:sum(W[s] for s in x)/len(x)**0.35)
        top=min(x,key=POP.index); x.remove(top); g.append([top])
    for x in g: x.sort(key=POP.index)
    return sorted(g,key=lambda x:POP.index(x[0]))
# designs: theme_style + placement (opt ids from catalog front_opts/back_opts)
TOPS=[("1","line_classic","head_s","body_l","Line Art · Emblem + Back","Line+Back"),
      ("2","geo_cool","head_l",None,"Geometric Sunglasses · Big Front","Geo Cool"),
      ("3","line_heart","head_s","body_l","Line Art Heart · Emblem + Back","Heart+Back"),
      ("4","geo_classic","head_s","body_l","Geometric · Emblem + Back","Geo+Back"),
      ("5","line_cool","head_l",None,"Line Art Sunglasses · Big Front","Line Cool"),
      ("6","geo_heart","head_l",None,"Geometric Heart · Big Front","Geo Heart")]
CHEST=[("1","line_classic","head_s",None,"Line Art Emblem","Line"),("2","geo_classic","head_s",None,"Geometric Emblem","Geo"),
       ("3","line_heart","head_s",None,"Line Art Heart Emblem","Heart"),("4","geo_cool","head_s",None,"Geometric Sunglasses Emblem","Geo Cool")]
CAPD=[("1","line_classic","head_s",None,"Line Art","Line"),("2","geo_cool","head_s",None,"Geometric Sunglasses","Geo Cool"),
      ("3","line_heart","head_s",None,"Line Art Heart","Heart"),("4","geo_classic","head_s",None,"Geometric","Geo")]
def cols(pid,pairs):
    """pairs = [(printify color, 2-letter code)] in marketplace priority order (first ones go live first; ALL stay decodable)."""
    p=next(x for x in cat["products"] if x["id"]==pid); ok={c[0]:c for c in p["colors"] if c[2]}
    return [(code,pid,c,(ok[c][4] if len(ok[c])>4 and ok[c][4] else c)) for c,code in pairs if c in ok]
# product families as listed on marketplaces. colors: (code, store product id, printify color, display)
# Priority = bestseller colors first (white, black, navy ...). Dark colors print WHITE lines, light colors BLACK lines.
PRODUCTS={
 "tee":   {"L":"T","name":"T-Shirt","designs":TOPS,"sizes":["S","M","L","XL","2XL"],"colors":cols("tee",[("White","WH"),("Black","BK"),("Navy","NV"),("Ash","AS"),("Dark Grey Heather","DG"),("Light Blue","LB"),("Athletic Heather","HE"),("Soft Pink","PK"),("Soft Cream","CR"),("Natural","NA"),("Asphalt","AP"),("Forest","FO"),("Maroon","MR"),("Red","RD")])},
 "hoodie":{"L":"H","name":"Hoodie","designs":TOPS,"sizes":["S","M","L","XL","2XL"],"colors":cols("hoodie",[("White","WH"),("Black","BK"),("Navy","NV"),("Sport Grey","GR"),("Charcoal","CH"),("Sand","SA"),("Light Blue","LB"),("Light Pink","PK"),("Ash","AS"),("Forest Green","FG"),("Maroon","MR"),("Dark Heather","DH")])},
 "wtank": {"L":"W","name":"Women's Racerback Tank","designs":TOPS,"sizes":["S","M","L","XL","2XL"],"colors":cols("wtank",[("Solid White","WH"),("Solid Black","BK"),("Solid Midnight Navy","NV"),("Heather Grey","HG"),("Solid Tahiti Blue","TB"),("Solid Mint","MI"),("Solid Light Orange","LO"),("Solid Military Green","MG"),("Solid Indigo","IN")])},
 "tank":  {"L":"K","name":"Tank Top","designs":TOPS,"sizes":["S","M","L","XL","2XL"],"colors":cols("tank",[("White","WH"),("Black","BK"),("Navy","NV"),("Athletic Heather","HE")])},
 "polo":  {"L":"P","name":"Polo Shirt","designs":CHEST,"sizes":["S","M","L","XL","2XL"],"colors":cols("polo",[("White","WH"),("Black","BK"),("J. Navy","NV"),("Athletic Heather","HE")])},
 "cap":   {"L":"C","name":"Hat","designs":CAPD,"sizes":["One size"],
           "colors":cols("cap_dad",[("White","DW"),("Black","DL"),("Navy","DN"),("Stone","DS"),("Khaki","DK"),("Light Blue","DB"),("Pink","DP"),("Dark Grey","DG"),("Spruce","DR"),("Green Camo","DC")])+cols("cap_foam",[("White","FW"),("Black","FK"),("Dark Navy","FN"),("Light Pink/White","FP"),("Blue/White","FB")])+cols("cap_mesh",[("White","MW"),("Black","MK"),("Navy","MN"),("Charcoal","MC")])},
}
CAPLABEL={"cap_dad":"Dad Hat","cap_foam":"Foam Trucker","cap_mesh":"Mesh Trucker"}
COUNTS={"etsy":{"tee":13,"hoodie":13,"wtank":11,"tank":8,"polo":8,"cap":8},
        "ebay":{"tee":22,"hoodie":20,"wtank":18,"tank":14,"polo":12,"cap":14},
        "tiktok":{"tee":18,"hoodie":16,"wtank":14,"tank":11,"polo":9,"cap":12}}
CAP={"ebay":250,"etsy":400,"tiktok":100}
TIK1=20  # TikTok: tier-1 values (breed·design·color) x 5 sizes <= 100
def price(pid,size):
    p=next(x for x in cat["products"] if x["id"]==pid); base=p["price"].get("both",p["price"]["one"])
    return (base+p["sur"].get(size,0))/100
def fill(plat,pk,nb):
    P=PRODUCTS[pk]; S=len(P["sizes"]); D=1; C=1; cap=CAP[plat]
    nd,nc=len(P["designs"]),len(P["colors"])
    def ok(d,c): return nb*d*c*S<=cap and (plat!="tiktok" or (nb*d*c<=TIK1 if pk!="cap" else nb*d<=TIK1 and c<=9))
    if pk=="cap":   # hats: every hat/color, then designs
        C=nc
        while not ok(D,C) and C>1: C-=1
        while D<nd and ok(D+1,C): D+=1
        return D,C
    want_c=min(nc,4)
    while True:
        moved=False
        if D<min(nd,3) and ok(D+1,C): D+=1; moved=True
        if C<want_c and ok(D,C+1): C+=1; moved=True
        if not moved:
            if D<nd and ok(D+1,C): D+=1; moved=True
            elif C<nc and ok(D,C+1): C+=1; moved=True
        if not moved: return D,C
ALIAS={"french_bulldog":"Frenchie","labrador_retriever":"Lab","golden_retriever":"Golden","german_shepherd":"GSD","dachshund":"Doxie Wiener Dog",
 "rottweiler":"Rottie","german_shorthaired_pointer":"GSP","bulldog":"Bulldog","cane_corso":"Corso","cavalier_king_charles_spaniel":"Cavalier",
 "yorkshire_terrier":"Yorkie","australian_shepherd":"Aussie","doberman_pinscher":"Dobie","pembroke_welsh_corgi":"Corgi","miniature_schnauzer":"Schnauzer",
 "pomeranian":"Pom","bernese_mountain_dog":"Berner","great_dane":"Dane","boston_terrier":"Boston","chihuahua":"Chi","siberian_husky":"Husky",
 "american_pit_bull_terrier":"Pitbull","shiba_inu":"Shiba","mini_poodle":"Poodle","bichon_frise":"Bichon","poodle":"Poodle"}
NOUN={"tee":"Shirt","hoodie":"Hoodie","wtank":"Women's Tank Top","tank":"Tank Top","polo":"Polo Shirt","cap":"Hat"}
POOL={"tee":["T-Shirt","Dog Mom","Dog Dad","Gift","Line Art","Geometric","Dog Lover","Unisex Tee","Minimalist","Portrait"],
      "hoodie":["Sweatshirt","Dog Mom","Dog Dad","Gift","Line Art","Geometric","Dog Lover","Unisex","Minimalist","Portrait"],
      "wtank":["Racerback","Dog Mom","Gift","Line Art","Geometric","Dog Lover","Summer","Workout","Minimalist"],
      "tank":["Dog Dad","Dog Mom","Gift","Line Art","Geometric","Dog Lover","Summer","Unisex","Minimalist"],
      "polo":["Dog Dad","Gift","Embroidered Look Emblem","Line Art","Geometric","Dog Lover","Golf","Minimalist"],
      "cap":["Dad Hat","Trucker Cap","Dog Mom","Dog Dad","Gift","Line Art","Geometric","Dog Lover","Baseball Cap"]}
def title(plat,pk,br,fam):
    lim={"ebay":80,"etsy":140,"tiktok":200}[plat]; noun=NOUN[pk]
    names=[BR[b] for b in br]
    if plat=="ebay" and len(br)>1: names=[short(b) for b in br]
    sep=" " if plat=="ebay" else ", "
    t=sep.join(names)+" "+noun
    if len(t)>lim:
        names=[short(b) for b in br]; t=sep.join(names)+" "+noun
    if plat!="ebay":
        al=ALIAS.get(br[0]) if len(br)==1 else None
        if al and al.lower() in t.lower(): al=None
        kind={"tee":"T-Shirt","hoodie":"Sweatshirt","wtank":"Racerback Tank","tank":"Tank","polo":"Polo","cap":"Dad Hat, Trucker Cap"}[pk]
        for tail in [f" | {al+' ' if al else ''}Line Art & Geometric Dog {kind}, Dog Mom Dad Gift", f" | Line Art Dog {kind}, Dog Lover Gift", " - Dog Lover Gift", ""]:
            if len(t+tail)<=lim: return t+tail
        return t[:lim]
    extra=[]
    if len(br)==1 and br[0] in ALIAS and ALIAS[br[0]] not in t: extra.append(ALIAS[br[0]])
    extra+=POOL[pk]
    joiner=" " if plat=="ebay" else ", "
    first=True
    for w in extra:
        if w.lower() in t.lower(): continue
        cand=t+(" - " if (first and plat!="ebay") else joiner)+w
        if len(cand)<=lim: t=cand; first=False
    return t
def tags(pk,br,fam):
    base={"tee":["dog shirt","dog lover shirt","dog mom shirt","dog dad shirt","line art dog","geometric dog"],"hoodie":["dog hoodie","dog lover hoodie","dog mom sweatshirt","dog dad hoodie","line art dog"],
          "wtank":["dog mom tank","racerback tank","dog lover tank","line art dog","workout tank"],"tank":["dog tank top","dog dad tank","dog lover tank","line art dog","summer tank"],
          "polo":["dog dad polo","dog polo shirt","golf polo dog","dog lover gift","line art dog"],"cap":["dog mom hat","dog dad hat","dog trucker hat","dog dad cap","line art dog"]}[pk]
    t=[]
    for b in br:
        n=BR[b].lower(); a=ALIAS.get(b,"").lower().split(" ")[0]
        noun={"tee":"shirt","hoodie":"hoodie","wtank":"tank","tank":"tank","polo":"polo","cap":"hat"}[pk]
        for x in [f"{n} {noun}",f"{a} {noun}" if a and a!=n else "",f"{n} gift",f"{a} mom" if a else f"{n} mom"]:
            if x and len(x)<=20 and x not in t: t.append(x)
    for x in base+["dog owner gift","pet lover gift"]:
        if x not in t: t.append(x)
    noun={"tee":"shirt","hoodie":"hoodie","wtank":"tank","tank":"tank","polo":"polo","cap":"hat"}[pk]
    first=[]
    for b in br:
        c=[x for x in (f"{BR[b].lower()} {noun}",f"{ALIAS.get(b,'').lower().split(' ')[0]} {noun}",BR[b].lower()) if len(x)<=20 and not x.startswith(" ")]
        if c and c[0] not in first: first.append(c[0])
    rest=[x for x in t if x not in first]
    return (first+rest)[:13]
def famname(br):
    for n,m in FAM:
        if set(br)<=set(m): return n
    return "Dog Breed"
def build():
    out={"version":1,"products":{},"listings":[]}
    for pk,P in PRODUCTS.items():
        out["products"][pk]={"L":P["L"],"name":P["name"],"sizes":P["sizes"],
            "designs":[{"code":d[0],"art":d[1],"front":d[2],"back":d[3],"name":d[4],"short":d[5]} for d in P["designs"]],
            "colors":[{"code":c[0],"prod":c[1],"color":c[2],"name":(CAPLABEL[c[1]]+" "+c[3] if pk=="cap" else c[3])} for c in P["colors"]]}
    for plat,cn in COUNTS.items():
        for pk,n in cn.items():
            P=PRODUCTS[pk]
            for i,br in enumerate(groups(n)):
                D,C=fill(plat,pk,len(br)); fam=famname(br)
                L={"id":f"{plat}-{pk}-{i+1:02d}","plat":plat,"prod":pk,"breeds":br,"family":fam,
                   "designs":[d[0] for d in P["designs"][:D]],"colors":[c[0] for c in P["colors"][:C]],"sizes":P["sizes"],
                   "title":title(plat,pk,br,fam),"tags":tags(pk,br,fam)}
                L["n"]=len(br)*D*C*len(P["sizes"])
                out["listings"].append(L)
    out["codes"]={"breed":CODE}
    return out
def sku(pk,b,d,c,s):
    return f"{PRODUCTS[pk]['L']}-{CODE[b]}-{d}-{c}"+("" if s=="One size" else f"-{s}")
def decode(plan,s):
    """SKU -> store order item (validItem format)."""
    m=re.fullmatch(r"([A-Z])-([A-Z]{2})-(\d)-([A-Z]{2})(?:-(\w+))?",s.strip().upper())
    if not m: return None
    L,bc,dc,cc,sz=m.groups(); pk=next((k for k,v in plan["products"].items() if v["L"]==L),None)
    if not pk: return None
    P=plan["products"][pk]; inv={v:k for k,v in plan["codes"]["breed"].items()}
    b=inv.get(bc); d=next((x for x in P["designs"] if x["code"]==dc),None); c=next((x for x in P["colors"] if x["code"]==cc),None)
    if not(b and d and c): return None
    th,st=d["art"].split("_"); fo=lambda o:None if not o else {"part":"head" if o.startswith("head") else "body","size":o[-1],"breed":b,"theme":th,"style":st}
    return {"prod":c["prod"],"color":c["color"],"size":sz or "One size","qty":1,"front":fo(d["front"]),"back":fo(d["back"])}
if __name__=="__main__":
    plan=build()
    json.dump(plan,open(f"{ROOT}/store/data/market_plan.json","w"),separators=(",",":"))
    for plat in COUNTS:
        Ls=[l for l in plan["listings"] if l["plat"]==plat]; print(plat,len(Ls),"listings, max variations",max(l["n"] for l in Ls))
        for l in Ls: print(f"  {l['id']:16} n={l['n']:3} D={len(l['designs'])} C={len(l['colors'])} {'/'.join(short(b) for b in l['breeds'])} | {l['title']} ({len(l['title'])})")
    # self-test: every SKU decodes and passes basic catalog checks
    bad=0
    for l in plan["listings"]:
        for b in l["breeds"]:
            for d in l["designs"]:
                for c in l["colors"]:
                    for s in l["sizes"]:
                        it=decode(plan,sku(l["prod"],b,d,c,s)); p=next(x for x in cat["products"] if x["id"]==it["prod"])
                        if s not in p["sizes"] or not any(k[0]==it["color"] and k[2] for k in p["colors"]): bad+=1
    print("SKU decode check bad:",bad)
