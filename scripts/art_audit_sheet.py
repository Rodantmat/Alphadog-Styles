import os,json,io,urllib.request,time
from PIL import Image,ImageDraw
T=os.environ["PRINTIFY_TOKEN"].strip()
def g(p):
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
        except Exception: time.sleep(4)
up=json.load(open("out/uploads.json")); breeds=sorted({k.split("/")[0] for k in up})
os.makedirs("out/art_audit",exist_ok=True)
for kind in ["front","frontbig","back"]:
  for des in ["geo_heart","geo_classic","geo_cool","line_heart","line_classic","line_cool"]:
    cell=160; G=Image.new("RGB",(cell*11,cell*3+0),"white"); d=ImageDraw.Draw(G)
    for i,b in enumerate(breeds):
        k=f"{b}/{des}/{kind}_blackink"
        if k not in up: continue
        u=g(f"/v1/uploads/{up[k]}.json") or {}
        try:
            im=Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u["preview_url"],headers={"User-Agent":"a"}),timeout=60).read())).convert("RGBA")
            bg=Image.new("RGBA",im.size,"white"); bg.alpha_composite(im); im=bg.convert("RGB"); im.thumbnail((cell-8,cell-22))
            G.paste(im,((i%11)*cell+4,(i//11)*cell+4))
        except Exception as e: pass
        d.text(((i%11)*cell+4,(i//11)*cell+cell-16),b[:22],fill=(200,0,0))
    G.save(f"out/art_audit/{kind}_{des}.jpg",quality=80); print("sheet",kind,des,flush=True)
