"""TikTok gallery images per consolidated listing -> /mnt/user-data/uploads/tt/<listing-id>/img1..6.jpg (lineup + 5 designs on different colours)"""
import sys,os,shutil,json
sys.path.insert(0,os.path.dirname(__file__))
import market_images as mi
out="/mnt/user-data/uploads/tt"
ids=[l["id"] for l in mi.plan["listings"] if l["plat"]=="tiktok"]
sel=sys.argv[1:] or ids
for lid in sel:
    jobs,meta=mi.plan_jobs(lid); m=meta[lid]
    L=next(l for l in mi.plan["listings"] if l["id"]==lid)
    # extra per-colour hero images: design i on colour i (cycling, dark colours first for variety)
    C={c["code"]:c for c in mi.plan["products"][L["prod"]]["colors"]}; D={d["code"]:d for d in mi.plan["products"][L["prod"]]["designs"]}
    order=[c for c in L["colors"] if mi.cdark(C[c]["prod"],C[c]["color"])]+[c for c in L["colors"] if not mi.cdark(C[c]["prod"],C[c]["color"])]
    pick=[]
    for i,dc in enumerate(L["designs"][:5]):
        cc=order[i%len(order)]; c=C[cc]; p=f"{c['prod']}/{L['breeds'][0]}/{dc}{cc}.jpg"
        jobs[p]=(p,c["prod"],c["color"],L["breeds"][0],D[dc]); pick.append(p)
    for j in jobs.values(): mi.render(j)
    lp,pc,b,d=m["lineup"]; mi.lineup(lp,pc,b,d,lid)
    os.makedirs(f"{out}/{lid}",exist_ok=True)
    srcs=[lp]+pick
    for i,s in enumerate(srcs[:6],1): shutil.copy(f"{mi.OUT}/{s}",f"{out}/{lid}/img{i}.jpg")
    print(lid,len(srcs[:6]))
