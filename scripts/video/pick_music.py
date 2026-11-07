#!/usr/bin/env python3
"""Enforced music picker.
  pick_music.py pick STYLE [--prev-theme T] [--sibling-theme T] [--n 3]   -> prints best candidates (JSON), never used, style-matched
  pick_music.py commit STYLE FILE YYYY-MM-DD USE                            -> registers use in docs/music_used.json (+ line in docs/music_log.md)
  pick_music.py check                                                      -> validate registry (no duplicates)
Rules: track never reused; theme must be allowed for the style; bpm within the style range; theme != prev day's theme and != same-day sibling's theme;
prefer higher energy within the style; spread across themes."""
import json,sys,re,os,datetime
R=os.path.dirname(os.path.abspath(__file__))+"/../../"
LIST=R+"out/music2/list.json";MAP=R+"docs/music_style_map.json";USED=R+"docs/music_used.json";LOG=R+"docs/music_log.md"
def idx(f): return int(re.search(r"m(\d+)",f).group(1))
def load_used():
    return json.load(open(USED)) if os.path.exists(USED) else {}
def main():
    a=sys.argv[1:]
    lst=json.load(open(LIST));mp=json.load(open(MAP))["styles"];used=load_used()
    if a[0]=="check":
        ks=[idx(k) for k in used];assert len(ks)==len(set(ks));print("ok",len(ks),"used of",len(lst));return
    if a[0]=="commit":
        st,f,d,use=a[1:5];assert st in mp,"unknown style"
        t=[x for x in lst if idx(x["file"])==idx(f)][0]
        assert f"{idx(f)}" not in {str(idx(k)) for k in used},"ALREADY USED"
        assert t["theme"] in mp[st]["themes"],"theme not allowed for style"
        used[f]={"date":d,"use":use,"style":st,"theme":t["theme"],"title":t["title"]}
        json.dump(used,open(USED,"w"),indent=1)
        open(LOG,"a").write(f"- {d} {use}: {f} \"{t['title']}\" - {t['artist']} [{t['theme']}, style {st}]\n");print("committed",f);return
    st=a[1];assert st in mp,"unknown style (add to docs/music_style_map.json first)"
    arg=lambda k:(a[a.index(k)+1] if k in a else None)
    prev=arg("--prev-theme");sib=arg("--sibling-theme");n=int(arg("--n") or 3)
    usedi={idx(k) for k in used};lo,hi=mp[st]["bpm"]
    c=[x for x in lst if idx(x["file"]) not in usedi and x["theme"] in mp[st]["themes"] and lo<=x.get("bpm",lo)<=hi and x["theme"] not in (prev,sib)]
    c.sort(key=lambda x:-x.get("energy",0))
    # theme spread: best of each theme first
    seen=set();out=[]
    for x in c:
        if x["theme"] not in seen: seen.add(x["theme"]);out.append(x)
    out+= [x for x in c if x not in out]
    print(json.dumps([{k:x.get(k) for k in("file","title","artist","theme","bpm","energy")} for x in out[:n]],indent=1))
main()
