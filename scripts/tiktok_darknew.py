"""Create 16 new dark-shade single-breed tees in Printify (white ink), then swap them into the TikTok slots of the legacy light listings.
Env: PRINTIFY_TOKEN, MODE = create | swap (needs N = how many slots, START) | status"""
import os,json,time,sys
sys.argv=[sys.argv[0]]
os.environ.setdefault("MODE","status")
MODE=os.environ["MODE"]
import importlib.util
src=open("scripts/tiktok_repurpose.py").read().split("n=0\nfor i,(ts,key)")[0]   # reuse helpers/constants only
M0=MODE; os.environ["MODE"]="helpers"; exec(src); MODE=M0
ST="out/state_dark_tiktok.json"; S=json.load(open(ST)) if os.path.exists(ST) else {}
def save(): json.dump(S,open(ST,"w"),indent=1)
if MODE=="create":
    for i in range(16):
        slug,disp,d,lay,title,style,vs,ids,ph=build(i)
        k=f"{slug}|{d}|tee|{lay}"
        if k in S: continue
        body={"title":title,"description":f"<p>The {disp} in {style} on a premium soft Bella+Canvas 3001 unisex tee, printed in white ink so it pops on dark colors.</p><p>Unisex fit, soft and comfortable. Made to order, ships in about 5-10 business days.</p>",
          "blueprint_id":12,"print_provider_id":99,
          "tags":[t[:20] for t in [disp.lower(),f"{disp.lower()} shirt","dog lover shirt","dog mom gift","dog dad gift","black dog shirt","dog breed shirt","minimalist dog","pet lover gift","dog owner gift","unisex t-shirt","dog art","gift for dog lover"]][:13],
          "variants":[{"id":v["id"],"price":(3199 if lay=="pair" else 2499)+SUR.get(v["options"]["size"],0),"is_enabled":True} for v in vs],
          "print_areas":[{"variant_ids":ids,"placeholders":ph}]}
        p=call("POST",f"/v1/shops/{SHOP}/products.json",body)
        S[k]={"id":p["id"],"slot":SLOTS[i][0],"legacy":SLOTS[i][1],"published":False,"n":len(ids)}; save(); print("CREATED",i,k,p["id"],len(ids),flush=True); time.sleep(1)
    print("CREATE DONE",len(S))
if MODE=="swap":
    N=int(os.environ.get("N","1")); START=int(os.environ.get("START","0")); keys=list(S)[START:START+N]
    drop=[(S[k]["legacy"],LS[S[k]["legacy"]]["id"]) for k in keys]
    for lk,pid in drop:
        print("unpublish legacy",lk,call("POST",f"/v1/shops/{SHOP}/products/{pid}/unpublish.json",{}),flush=True); time.sleep(2)
    print("waiting 150s for TikTok to free slots",flush=True); time.sleep(150)
    for k in keys:
        r=call("POST",f"/v1/shops/{SHOP}/products/{S[k]['id']}/publish.json",{"title":True,"description":True,"images":True,"variants":True,"tags":True,"keyfeatures":True,"shipping_template":True})
        S[k]["published"]=True; save(); print("PUBLISHED new",k,S[k]["id"],flush=True); time.sleep(3)
    print("SWAP DONE",len(keys))
