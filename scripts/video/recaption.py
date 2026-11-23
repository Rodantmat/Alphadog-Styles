#!/usr/bin/env python3
"""Rewrite caption.txt + pin.json of already built (UNSCHEDULED) Post B reels with the current caption/pin rules (rule 16h).
Usage: python3 scripts/video/recaption.py c39 c40 ...   Never run on posted or Buffer-scheduled items. The video itself is untouched."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import postc2_build as P
for vid in sys.argv[1:]:
    d = f"out/postc/{vid}"; m = json.load(open(f"{d}/meta.json")); lead = m["meta"][0].get("breed") or "dog"
    if m.get("variant") != "v5": print(vid, "skip (not v5)"); continue
    open(f"{d}/caption.txt", "w").write(P.v5_caption(lead))
    json.dump(P.pin_json(lead, "v5", [x["prod"] for x in m["meta"]], vid), open(f"{d}/pin.json", "w"), indent=1)
    print(vid, lead, "recaptioned"); print(open(f"{d}/caption.txt").read()); print(open(f"{d}/pin.json").read())
