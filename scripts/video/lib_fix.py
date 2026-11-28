#!/usr/bin/env python3
"""Clean every merch_lib cutout in place (white fringe, backdrop slivers, grey cast shadow) and audit it. Idempotent: out/merch_lib/.clean_v2 lists finished items.
Run right after restoring merch_lib (docs/ASSET_RESTORE.md). usage: lib_fix.py [fix|audit] [KEYPREFIX ...]   (KEY = product/breed/code)"""
import sys,os,glob
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import sprite_clean as S, edge_audit as E
from multiprocessing import Pool
LIB="/home/claude/alphadog-styles/out/merch_lib/"; MARK=LIB+".clean_v2"
def kind(key): return "flat_front"
def fix(p):
    key=p[len(LIB):-5]
    try:
        im=Image.open(p).convert("RGBA"); c=S.clean(im,kind(key)); bb=c.getbbox()
        if bb: c=c.crop(bb)
        a0=(np.array(im)[...,3]>128).sum(); a1=(np.array(c)[...,3]>128).sum()
        if a1<0.90*a0: return key,{"ok":False,"err":"LOST_AREA %.3f"%(a1/max(a0,1))}   # cleaner must never eat the garment: keep the original and flag it
        tmp=p+".tmp.webp"; c.save(tmp,"WEBP",lossless=True,quality=100,method=4); os.replace(tmp,p); r=E.audit(c,kind(key))
        return key,r
    except Exception as e: return key,{"ok":False,"err":str(e)}
def main():
    mode=sys.argv[1] if len(sys.argv)>1 else "fix"; pre=sys.argv[2:]
    done=set(open(MARK).read().split()) if os.path.exists(MARK) else set()
    fs=sorted(glob.glob(LIB+"*/*/*.webp")); fs=[f for f in fs if not f.endswith(".tmp.webp")]
    if pre: fs=[f for f in fs if any(f[len(LIB):].startswith(x) for x in pre)]
    if mode=="audit":
        bad=[]
        for f in fs:
            r=E.audit(Image.open(f).convert("RGBA"),"flat_front")
            if not r["ok"]: bad.append((f[len(LIB):-5],r))
        print("AUDIT items",len(fs),"fail",len(bad)); [print(b) for b in bad[:30]]; sys.exit(1 if bad else 0)
    todo=[f for f in fs if f[len(LIB):-5] not in done]; print("todo",len(todo),flush=True)
    bad=[]
    with Pool(2) as P:
        for i,(key,r) in enumerate(P.imap_unordered(fix,todo,chunksize=8)):
            if r.get("ok"): open(MARK,"a").write(key+"\n")
            else: bad.append((key,r))
            if i%200==0: print(i,flush=True)
    print("FIXED",len(todo)-len(bad),"audit-fail",len(bad)); [print(b) for b in bad[:30]]
if __name__=="__main__": main()
