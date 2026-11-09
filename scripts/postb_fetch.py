"""Fetch the exact Printify mockup assets chosen in social/postb/briefs.json into out/pmk3/<id>/NN.jpg (run in Actions: Printify CDN is only reachable there)."""
import json,os,urllib.request,time,sys
B=json.load(open("social/postb/briefs.json")); only=set(sys.argv[1:])
for p in B:
    if only and p["id"] not in only: continue
    d=f"out/pmk3/{p['id']}"; os.makedirs(d,exist_ok=True)
    for i,a in enumerate(p["assets"]):
        f=f"{d}/{i:02d}.jpg"
        if os.path.exists(f): continue
        for t in range(3):
            try:
                b=urllib.request.urlopen(urllib.request.Request(a["src"],headers={"User-Agent":"Mozilla/5.0"}),timeout=40).read(); open(f,"wb").write(b); break
            except Exception as e: time.sleep(3)
        time.sleep(0.4)
    print("fetched",p["id"],len(os.listdir(d)),flush=True)
