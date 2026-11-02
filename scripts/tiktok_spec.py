"""Compact per-listing spec for driving the TikTok product editor (title, description, option values, SKU rule)."""
import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import market_text as T, tiktok_feed as F
from market_plan import short,CODE,price
plan=T.plan; feed={x['id']:x for x in json.load(open(os.path.join(T.ROOT,'out/tiktok_feed.json')))}
FAB={"tee":"Bella+Canvas 3001 unisex jersey tee, about 4.2 oz, 100% Airlume combed and ring-spun cotton. Soft, lightweight retail fit that runs true to size - size up for a relaxed fit.",
 "hoodie":"Gildan 18500 heavy blend hoodie, about 8 oz, 50/50 cotton-poly, double-lined hood, pouch pocket. Classic roomy fit - size down for a snug fit.",
 "tank":"Bella+Canvas 3480 unisex jersey tank, about 4.2 oz, 100% Airlume cotton. Soft, light and breathable retail fit.",
 "wtank":"Next Level 1533 women's racerback tank, about 3.9 oz cotton/poly blend, slim racerback cut - size up for a looser fit.",
 "polo":"JERZEES 443M piqué polo, breathable cotton-blend piqué, ribbed collar, three-button placket. Dog printed on the chest.",
 "cap":"Dad Hat (Yupoong 6245CM, soft cotton twill, adjustable strap), Foam Trucker (retro foam front, mesh back, snapback) or Mesh Trucker (5-panel, mesh back, snapback). One size fits most."}
def spec(lid):
    L=next(l for l in plan['listings'] if l['id']==lid); f=feed[lid]; P=plan['products'][L['prod']]; cap=L['prod']=='cap'
    v1=list(dict.fromkeys(s['v1'] for s in f['skus'])); v2=list(dict.fromkeys(s['v2'] for s in f['skus']))
    D={}; 
    for d in P['designs']:
        D[F.DS.get(d['code'],d['code']) if L['prod'] not in('cap','polo') else d['name']]=d['code']
    C={}
    for c in P['colors']:
        C[c['name'] if cap else F.CS.get(c['color'],c['color'])]=c['code']
    S={"L":P['L'],"b1":CODE[L['breeds'][0]],"multi":len(L['breeds'])>1,"b":{short(b):CODE[b] for b in L['breeds']},"d":D,"c":C,"cap":cap}
    if cap: S["pr"]={c['name']:price(c['prod'],'One size') for c in P['colors']}
    else: S["base"]=price(P['colors'][0]['prod'],'S'); S["sur"]={s:round(price(P['colors'][0]['prod'],s)-S["base"],2) for s in L['sizes'] if price(P['colors'][0]['prod'],s)!=S["base"]}
    names=", ".join(T.BR[b] for b in L['breeds']); noun={"tee":"tee","hoodie":"hoodie","wtank":"racerback tank","tank":"tank top","polo":"polo","cap":"hat"}[L['prod']]
    dl="".join(f"<br>- {k}" for k in [ (F.DS.get(d,d) if L['prod'] not in('cap','polo') else next(x['name'] for x in P['designs'] if x['code']==d)) for d in L['designs']])
    desc=(f"<p>Wear your best friend. Minimalist {names} art on a soft {noun} - the gift every dog mom and dog dad actually wears.</p>"
          f"<p><b>HOW TO ORDER</b><br>1. Color: pick {'the breed and ' if len(L['breeds'])>1 else ''}design{'' if cap else ' and color'}.<br>2. {'Hat: pick the hat style and color' if cap else 'Size: pick your size'}.</p>"
          f"<p><b>DESIGNS</b>{dl}</p><p><b>FABRIC AND FIT</b><br>{FAB[L['prod']]}</p>"
          "<p><b>DETAILS</b><br>- Printed in the USA, made to order.<br>- Production 2-5 business days, then 3-7 days in transit. Tracking included.</p>"
          f"<p><b>CARE</b><br>{'Spot clean only.' if cap else 'Machine wash cold, inside out. Tumble dry low. Do not iron the print.'}</p>")
    return {"id":lid,"prod":L['prod'],"title":f['title'],"desc":desc,"v1":v1,"v2":v2,"S":S,"n":len(f['skus'])}
if __name__=="__main__":
    print(json.dumps(spec(sys.argv[1]),ensure_ascii=False,separators=(',',':')))
