#!/usr/bin/env python3
"""QA sheets: every asset of every brief rendered exactly as in the video (tile+brand), 5x2 per video -> qa dir"""
import json,sys,os
sys.path.insert(0,"scripts/video"); sys.path.insert(0,"social/postb")
import postb_build as P
from PIL import Image
B=json.load(open("social/postb/briefs.json")); out=sys.argv[1]; os.makedirs(out,exist_ok=True); ids=sys.argv[2:]
for p in B:
    if ids and p["id"] not in ids: continue
    sh=Image.new("RGB",(5*270,2*480))
    for i,a in enumerate(p["assets"]):
        t=P.brand(P.tile(f"out/pmk3/{p['id']}/{i:02d}.jpg",1080,1920),None).resize((270,480)); sh.paste(t,((i%5)*270,(i//5)*480))
    sh.save(f"{out}/{p['id']}.png")
