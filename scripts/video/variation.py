#!/usr/bin/env python3
"""ENFORCES owner variation rules for every Post A video (docs/VIDEO_MODELS.md, docs/video_models.json).
  python3 scripts/video/variation.py brief YYYY-MM-DD     -> JSON brief for that day's video (model + allowed breeds/merch/bg/music constraints)
  python3 scripts/video/variation.py check ENTRY.json      -> exit 1 listing every violation (run BEFORE building/scheduling)
  python3 scripts/video/variation.py commit ENTRY.json     -> check, then append to docs/style_registry.json
ENTRY = {date, model, breeds[], merch["product/breed/code",..], bg[bg ids], music "mNN"/"mxNNN", joke, laugh, neon_color}"""
import json,sys,os,re,random,datetime,collections
R="docs/style_registry.json"; M=json.load(open("docs/video_models.json")); CAT=json.load(open("docs/merch_lib_catalog.json"))
def reg(): return json.load(open(R))
def fam(code): return {"BK":"dark","NV":"dark","DK":"dark","DG":"dark","CH":"dark","BR":"dark","GR":"dark","MA":"dark"}.get(code[-2:],code[-2:])
def parse(m):
    p=m.split("/"); return dict(product=p[0],breed=p[1],code=re.sub(r"_back$","",p[2]),back=p[2].endswith("_back"))
def view(m): 
    p=parse(m); c=next((x for x in CAT if x["file"].startswith(f"{p['product']}/{p['breed']}/{p['code']}")),None)
    return "back" if p["back"] else (c["view"] if c else "front")
def check(e,r=None):
    r=r if r is not None else reg(); v=[]; d=datetime.date.fromisoformat(e["date"]); past=[x for x in r if x.get("date","")<e["date"] and x.get("model") or x.get("type")]
    past=sorted([x for x in r if x.get("date","")<e["date"]],key=lambda x:x["date"]); prev=past[-1] if past else None
    mdl=e["model"]; 
    if mdl not in M["models"]: v.append(f"unknown model {mdl}")
    dow=d.strftime("%a")
    if dow in M["fixed_days"] and M["fixed_days"][dow]!=mdl: v.append(f"{dow} must be {M['fixed_days'][dow]}")
    if mdl in M["fixed_days"].values() and M["fixed_days"].get(dow)!=mdl: v.append(f"{mdl} only on {[k for k,x in M['fixed_days'].items() if x==mdl]}")
    if prev and (prev.get("model") or prev.get("type"))==mdl: v.append("same model as previous video (back-to-back)")
    n=M["cooldowns"]["breed_primary_last_n_videos"]; recent=[b for x in past[-n:] for b in (x.get("breeds") or [])]
    if mdl!="d6": 
        for b in e.get("breeds",[])[:1]:
            if b in recent: v.append(f"breed {b} used in the last {n} videos")
    if mdl=="d6":
        if len(e.get("breeds",[]))!=1: v.append("neon: exactly ONE breed")
        used=[b for x in r if (x.get("model") or x.get("type"))=="d6" for b in (x.get("breeds") or [])]
        allb=sorted({x["breed"] for x in CAT})
        if e["breeds"] and e["breeds"][0] in used and set(used)<set(allb): v.append("neon breed already had its week; pick a breed that has not")
        if not e.get("neon_color"): v.append("neon needs neon_color")
    # merch
    ms=[parse(m) for m in e.get("merch",[])]
    keys=[(x["product"],fam(x["code"])) for x in ms]
    if len(set(keys))<len(keys): v.append("two merch items share product+colour family in the same video")
    vs={view(m) for m in e.get("merch",[])}
    if len(ms)>=4 and len(vs)<M["cooldowns"]["min_distinct_views_when_4plus_items"]: v.append(f"only {len(vs)} distinct views (need {M['cooldowns']['min_distinct_views_when_4plus_items']})")
    if prev and prev.get("merch"):
        pm=[parse(m) for m in prev["merch"]]
        sp={x["product"] for x in pm}&{x["product"] for x in ms}; sc={fam(x["code"]) for x in pm}&{fam(x["code"]) for x in ms}
        if sp and len(ms)<=2: v.append(f"merch product repeated vs previous video: {sorted(sp)}")
        if len(ms)==1 and sc: v.append(f"merch colour repeated vs previous video: {sorted(sc)}")
        sd={re.sub(r'\D.*','',x["code"])[:1] for x in pm}&{re.sub(r'\D.*','',x["code"])[:1] for x in ms}
        if len(ms)==1 and sd: v.append("merch design repeated vs previous video")
    # background (60 days)
    cut=(d-datetime.timedelta(days=M["cooldowns"]["background_days"])).isoformat()
    usedbg={b for x in r if x.get("date","")>=cut and x.get("date","")<e["date"] for b in (x.get("bg_ids") or [])}
    for b in e.get("bg",[]):
        if b in usedbg: v.append(f"background {b} used within 60 days")
    if len(set(e.get("bg",[])))<len(e.get("bg",[])): v.append("same background twice in one video")
    if M["models"].get(mdl,{}).get("background_kind")=="scenery":
        for b in e.get("bg",[]):
            if not (b.startswith("pg_") or b.startswith("scenery_")): v.append(f"scenery model needs a real scenery photo, got {b}")
    # music / joke / laugh never
    mu=json.load(open("docs/music_used.json"))
    if e.get("music") and (e["music"]+".mp3" in mu or e["music"] in mu): v.append(f"music {e['music']} already used")
    if e.get("music") and any(x.get("music")==e["music"] for x in r): v.append(f"music {e['music']} already in registry")
    j=(e.get("joke") or "").lower().strip()
    if mdl in("laugh4","laugh2"):
        if not j: v.append("joke videos need a joke")
        if j and any((x.get("joke") or "").lower().strip()==j for x in r): v.append("joke already used")
        if e.get("laugh") and any(x.get("laugh")==e["laugh"] for x in r): v.append("laugh track already used")
    return v
def brief(date):
    r=reg(); d=datetime.date.fromisoformat(date); dow=d.strftime("%a")
    past=sorted([x for x in r if x.get("date","")<date],key=lambda x:x["date"]); last={}
    for x in past: last[x.get("model") or x.get("type")]=x["date"]
    if dow in M["fixed_days"]: mdl=M["fixed_days"][dow]
    else:
        cands=[m for m in M["models"] if m not in M["fixed_days"].values() and m!=((past[-1].get("model") or past[-1].get("type")) if past else None)]
        mdl=min(cands,key=lambda m:last.get(m,"0"))
    n=M["cooldowns"]["breed_primary_last_n_videos"]; recent={b for x in past[-n:] for b in (x.get("breeds") or [])}
    allb=sorted({x["breed"] for x in CAT}); ok=[b for b in allb if b not in recent]
    if mdl=="d6":
        used={b for x in r if (x.get("model") or x.get("type"))=="d6" for b in (x.get("breeds") or [])}; ok=[b for b in allb if b not in used] or allb
    return {"date":date,"model":mdl,"model_spec":M["models"][mdl],"allowed_breeds":ok,"previous_video":past[-1] if past else None,
            "must":["call variation.py check ENTRY.json before building and again before scheduling","music via scripts/video/pick_music.py pick <model>","backgrounds via scripts/video/bgmatch.py (60-day log)","commit to registry only after the video is approved/scheduled"]}
if __name__=="__main__":
    a=sys.argv
    if a[1]=="brief": print(json.dumps(brief(a[2]),indent=1)[:4000])
    else:
        e=json.load(open(a[2])); v=check(e)
        if v: print("VIOLATIONS:\n - "+"\n - ".join(v)); sys.exit(1)
        print("OK")
        if a[1]=="commit":
            r=reg(); e.setdefault("type",e["model"]); e["bg_ids"]=e.pop("bg",[]); r.append(e); json.dump(r,open(R,"w"),indent=1); print("committed")
