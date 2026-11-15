"""Probe: do the Printify person/hanging/scene camera ids work on REAL design products (not only on the blank mockup sources)?
Writes out/person_probe.png (contact sheet of everything that renders) and prints status per camera."""
import json,io,time,urllib.request,os
from PIL import Image,ImageDraw
from concurrent.futures import ThreadPoolExecutor
R=json.load(open("out/mockidx/index.json")); CAM=json.load(open("docs/printify_cameras.json"))
ex=json.load(open("store/data/amazon_extras.json"))
picks=[("french_bulldog|NV","Tee A"),("french_bulldog|WH","Tee B")]
COL={"french_bulldog|NV":"Navy","french_bulldog|WH":"White"}
def vid(r,key):
    for v,l in r["variants"].items():
        if l.split(" / ")[-1].strip()==COL[key]: return str(v)
def get(u):
    try:
        b=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read(); return Image.open(io.BytesIO(b)).convert("RGB")
    except Exception as e: return str(e)[:60]
tiles=[]
for key,_ in picks:
    pid=ex[key]["pid"]; r=[x for x in R if x["pid"]==pid][0]; v=vid(r,key); bp=r["bp"]; name="Tee A" if bp==145 else "Tee B"
    print(key,pid,"bp",bp,"variant",v,name)
    cams=CAM[name]
    def one(c):
        u=f"https://images.printify.com/mockup/{pid}/{v}/{c}/x.jpg?camera_label=front&s=800&use_cache=false&t={int(time.time()*1000)}"
        return c,get(u)
    with ThreadPoolExecutor(8) as ex2:
        for c,im in ex2.map(one,list(cams)):
            ok=isinstance(im,Image.Image)
            print("  ",c,cams[c]["kind"],cams[c].get("side"),"OK" if ok else im)
            if ok: tiles.append((f"{key} {c} {cams[c]['kind']}",im))
if tiles:
    n=len(tiles); cols=6; rows=(n+cols-1)//cols; S=300
    sheet=Image.new("RGB",(cols*S,rows*S),(255,255,255)); d=ImageDraw.Draw(sheet)
    for i,(t,im) in enumerate(tiles):
        im=im.copy(); im.thumbnail((S,S)); sheet.paste(im,((i%cols)*S,(i//cols)*S)); d.text(((i%cols)*S+4,(i//cols)*S+2),t[-34:],fill=(200,0,0))
    sheet.save("out/person_probe.png")
print("tiles",len(tiles))
