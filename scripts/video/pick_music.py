#!/usr/bin/env python3
"""Enforced music picker over the 1,000+ track library (docs/music_catalog.json; clips in release assets musiclib_s0..s7).
  pick_music.py restore                                  -> download+unzip all clips to out/musiclib/clips (needs gh auth; run first in a fresh workspace/task)
  pick_music.py pick STYLE [--prev-theme T] [--sibling-theme T] [--n 3]   -> best never-used candidates for the style (theme+bpm), best energy first, spread over themes
  pick_music.py commit STYLE FILE YYYY-MM-DD USE         -> registers use (docs/music_used.json + docs/music_log.md); FILE like mx738.mp3 or legacy m25.mp3
  pick_music.py check
Rules: track never reused (legacy m## and mx### are the same track via url); theme allowed for style; bpm in range; theme != previous day / sibling."""
import json,sys,re,os,datetime,subprocess,glob
R=os.path.dirname(os.path.abspath(__file__))+"/../../"
CAT=R+"docs/music_catalog.json";MAP=R+"docs/music_style_map.json";USED=R+"docs/music_used.json";LOG=R+"docs/music_log.md";CLIPS=R+"out/musiclib/clips/"
def load_used(): return json.load(open(USED)) if os.path.exists(USED) else {}
def canon(lst):
    m={}
    for t in lst:
        m[t["file"]]=t["id"]
        if t.get("legacy"): m[t["legacy"]]=t["id"]
    return m
def clip_path(t):
    for p in (CLIPS+t["file"],R+"out/music2/"+(t.get("legacy") or "x")):
        if os.path.exists(p): return p
def main():
    a=sys.argv[1:]
    if a[0]=="restore":
        os.makedirs(CLIPS,exist_ok=True)
        for s in range(8):
            tag=f"musiclib_s{s}"; ids=subprocess.check_output(["gh","api",f"repos/Rodantmat/Alphadog-Styles/releases/tags/{tag}","--jq",'.assets[]|select(.name|endswith(".zip"))|.id']).split()
            for i in ids:
                z=f"/tmp/{tag}.zip"; open(z,"wb").write(subprocess.check_output(["gh","api","-H","Accept: application/octet-stream",f"repos/Rodantmat/Alphadog-Styles/releases/assets/{i.decode()}"])); subprocess.run(["unzip","-q","-o",z,"-d",CLIPS],check=True)
        print("clips",len(glob.glob(CLIPS+"*.mp3")));return
    lst=json.load(open(CAT));mp=json.load(open(MAP))["styles"];used=load_used();cm=canon(lst)
    usedid={cm.get(k,k) for k in used}
    if a[0]=="check": print("ok",len(usedid),"used of",len(lst));return
    if a[0]=="commit":
        st,f,d,use=a[1:5];assert st in mp,"unknown style"
        t=next(x for x in lst if x["file"]==f or x.get("legacy")==f)
        assert t["id"] not in usedid,"ALREADY USED"
        assert t["theme"] in mp[st]["themes"],"theme not allowed for style"
        used[t["file"] if t["file"] not in used else f]={"date":d,"use":use,"style":st,"theme":t["theme"],"title":t["title"]}
        json.dump(used,open(USED,"w"),indent=1)
        open(LOG,"a").write(f"- {d} {use}: {t['file']} \"{t['title']}\" - {t['artist']} [{t['theme']}, style {st}]\n");print("committed",t["file"]);return
    st=a[1];assert st in mp,"unknown style (add to docs/music_style_map.json first)"
    arg=lambda k:(a[a.index(k)+1] if k in a else None)
    prev=arg("--prev-theme");sib=arg("--sibling-theme");n=int(arg("--n") or 3);lo,hi=mp[st]["bpm"]
    c=[x for x in lst if x["id"] not in usedid and x["theme"] in mp[st]["themes"] and lo<=x.get("bpm",lo)<=hi and x["theme"] not in (prev,sib) and 30<=x.get("full_dur",60)]
    c.sort(key=lambda x:-x.get("energy",0));seen=set();out=[]
    for x in c:
        if x["theme"] not in seen: seen.add(x["theme"]);out.append(x)
    out+=[x for x in c if x not in out]
    print(f"{len(c)} candidates; clips in {CLIPS} (run 'restore' first if missing)")
    print(json.dumps([{k:x.get(k) for k in("file","title","artist","theme","bpm","energy")}|{"path":clip_path(x)} for x in out[:n]],indent=1))
main()
