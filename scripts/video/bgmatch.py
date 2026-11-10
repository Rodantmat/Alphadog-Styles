#!/usr/bin/env python3
"""Background matching: pick a real-photo background (catalog from bg-fetch shards) for a cutout by combination quality.
Rules come from docs/research/11 (contrast ratios, busyness, hue) and the owner's variety rules (no reuse within 60 days, never same family adjacent).
  from bgmatch import Catalog;  c=Catalog(); b=c.pick(garment_rgb, kind, avoid_families, used)  -> catalog row (has .file)
kind: person | flat | folded | closeup(cap or detail)"""
import json,glob,math,random,os,datetime,colorsys
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"../..")
USED=ROOT+"/docs/bg_used.json"
def lin(c): c/=255; return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def relL(rgb): r,g,b=rgb; return 0.2126*lin(r)+0.7152*lin(g)+0.0722*lin(b)
def ratio(a,b): hi,lo=max(a,b),min(a,b); return (hi+.05)/(lo+.05)
def bgL(row): return (row["centre_lum"]/255)**2.2     # approx linear luminance of the centre region
def hue_d(a,b): d=abs(a-b)%360; return min(d,360-d)
BUSY={"person":(7.0,58),"closeup":(8.0,60),"flat":(3.2,32),"folded":(4.0,36)}   # (max laplacian busyness, max centre std)
def family(r):
    cats=[c for c in (r.get("cats") or []) if c in("skies","nature","urban","studio","outdoor","indoor","sunrise-sunset","floor","wall","wood","fabric","concrete","plaster","marble","paper","tiles","brick","rock","metal","leather")]
    return f"{r['kind']}:{(cats[0] if cats else 'x')}:{(r['hue']//60)}"
def score(row,garment,kind):
    """Higher = better combination; None = reject."""
    if not row.get("ok"): return None
    mb,ms=BUSY[kind]
    if row.get("kind")!="hdri" and kind in("flat","folded"): mb=16.0   # fine-grain textures read as calm behind a garment
    if row["busy"]>mb or row["centre_std"]>ms: return None
    if kind in("flat","folded") and row["kind"]=="hdri" and not (row["busy"]<=3.6 and "studio" in (row.get("cats") or [])): 
        return None if row["busy"]>3.0 else 0
    g=relL(garment); b=bgL(row); r=ratio(g,b); s=0.0
    if r<3.0: return None                              # minimum garment/background separation
    s+= 3.0 - abs(math.log(r/7.0))                     # best around ratio 5-11
    gh,gs,gv=colorsys.rgb_to_hsv(*[x/255 for x in garment])
    if gs>0.25 and row["sat"]>0.45: s-=2.0             # saturated bg behind coloured garment
    if gs>0.25 and hue_d(gh*360,row["hue"])<35 and row["sat"]>0.25: s-=1.5   # same hue as the garment
    if row["sat"]<0.45 and row["sat"]>0.04: s+=0.5     # quiet-luxury muted tones
    if kind=="person":
        if row["kind"]=="hdri": s+=1.0 + 0.8*min(1,row["sky"]/0.3)           # real places with a visible sky/horizon
        if row["lum_bot"]<row["lum_top"]*0.95 or True: s+=0.2
        s-= row["busy"]/10.0                                                 # calmer is better behind a person
    elif kind in("flat","folded"):
        if row["kind"]=="texture": s+=1.2
        s-= row["busy"]/(8.0 if row["kind"]!="hdri" else 3.0)
    elif kind=="closeup":
        if row["kind"]=="hdri": s+=0.8
    return s
class Catalog:
    def __init__(self,path=None):
        paths=[path] if path else sorted(glob.glob(ROOT+"/out/bgcat/catalog_*.json"))
        self.rows=[]
        for p in paths: self.rows+=json.load(open(p))
        self.used=json.load(open(USED)) if os.path.exists(USED) else {}
    def recent(self,days=60):
        lim=(datetime.date.today()-datetime.timedelta(days=days)).isoformat(); return {k for k,v in self.used.items() if v>=lim}
    def pick(self,garment,kind,avoid_fam=(),taken=(),rnd=random,top=12,only=None):
        rec=self.recent(); cands=[]
        for r in self.rows:
            if r["file"] in rec or r["file"] in taken or family(r) in avoid_fam: continue
            if only and not only(r): continue
            s=score(r,garment,kind)
            if s is not None: cands.append((s,r))
        cands.sort(key=lambda x:-x[0]); cands=cands[:top]
        if not cands: return None
        w=[math.exp(s/1.5) for s,_ in cands]; return rnd.choices([r for _,r in cands],weights=w)[0]
    def commit(self,files,day=None):
        day=day or datetime.date.today().isoformat()
        for f in files: self.used[f]=day
        json.dump(self.used,open(USED,"w"),indent=0)
