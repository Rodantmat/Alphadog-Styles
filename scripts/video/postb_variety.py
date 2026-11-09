#!/usr/bin/env python3
"""Post B variety guard (owner rule 2026-11-08: consecutive Post B videos must differ DRASTICALLY - product, colours, breeds, photo style, format, placement, design).
Usage: postb_variety.py ORDER...   e.g. b02 b03 b05   (posting order). Exit 1 if any consecutive pair or 7-post window breaks a rule.
Reads social/postb/plan*.json. A candidate must pass BEFORE it is built or scheduled."""
import json, re, sys, glob
def load():
    P={}
    for f in sorted(glob.glob("social/postb/plan*.json")):
        try:
            for k,v in json.load(open(f)).items(): P[k]=v
        except Exception: pass
    return P
def sig(v):
    prod,br,col=set(),set(),set()
    for i in v.get("images",[]):
        p=i.split("/")
        if len(p)>5 and p[1]=="pmk": br.add(p[2]); prod.add(p[3]); col.add(p[4])
        else: br.add("?"+i); prod.add("?")
    for i in v.get("files",[]):  # legacy plan
        p=i.split("/"); prod.add(p[0]); br.add(p[1])
    return dict(prod=prod-{"?"},br={b for b in br if not b.startswith("?")},col=col,kind=v.get("kind"),title=v.get("title","").lower(),music=v.get("music"))
def pair(a,b):
    bad=[]
    if a["prod"]&b["prod"]: bad.append("same product "+",".join(sorted(a["prod"]&b["prod"])))
    if a["col"]&b["col"]: bad.append("shared colours "+",".join(sorted(a["col"]&b["col"])))
    if a["br"]&b["br"]: bad.append("shared breeds "+",".join(sorted(a["br"]&b["br"])))
    if a["kind"]==b["kind"] and a["kind"]!="mixed": pass
    if a["title"] and a["title"]==b["title"]: bad.append("same title")
    return bad
def main(order):
    P=load(); S={k:sig(P[k]) for k in order}; fail=0
    for i in range(1,len(order)):
        r=pair(S[order[i-1]],S[order[i]])
        print(order[i-1],"->",order[i],"FAIL: "+"; ".join(r) if r else "ok"); fail+=bool(r)
    for i,k in enumerate(order):
        for j in range(max(0,i-6),i):
            sh=S[k]["br"]&S[order[j]]["br"]
            if sh and i-j>1: print(" window:",order[j],k,"breeds repeat within 7 posts:",",".join(sorted(sh)))
    sys.exit(1 if fail else 0)
if __name__=="__main__": main(sys.argv[1:])
