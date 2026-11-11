#!/usr/bin/env python3
"""Fetch the multi-breed/colour transparent cutouts listed in docs/trans2_plan.json (run in GitHub Actions; images.printify.com is unreachable from the sandbox).
Saves out/trans2/<Prod_>/<cam>__<pid8>_<colour>.png (tight RGBA) + out/trans2/index.json with transparent fraction; scenes (transparent<0.08) are dropped."""
import json,os,sys,time,re
sys.path.insert(0,"scripts/video"); import ptrans
plan=json.load(open("docs/trans2_plan.json")); out="out/trans2"; idx=[]; fails=0
for i,p in enumerate(plan):
    d=f"{out}/"+p["prod"].replace(" ","_"); os.makedirs(d,exist_ok=True)
    fn=f"{d}/{p['cam']}__{p['pid'][:8]}_{re.sub(r'[^A-Za-z0-9]','',p['colour'])}.png"
    try:
        im,tr=ptrans.fetch(p["pid"],p["var"],p["cam"],size=1600)
        if tr<0.08: print("SCENE drop",p["prod"],p["cam"],flush=True); continue
        im.save(fn,optimize=True); idx.append(dict(p,file=fn,transp=round(tr,2),size=list(im.size))); print(i,p["prod"],p["cam"],p["breed"],p["colour"],im.size,round(tr,2),flush=True)
    except Exception as e: fails+=1; print("FAIL",p["prod"],p["cam"],e,flush=True)
    time.sleep(.35)
json.dump(idx,open(f"{out}/index.json","w"),indent=0); print("DONE",len(idx),"ok",fails,"failed")
