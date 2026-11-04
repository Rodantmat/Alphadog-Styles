import json,urllib.request,io,os
from PIL import Image,ImageDraw
os.makedirs("out/scenery",exist_ok=True)
L=[]
for p in range(1,5):
    L+=json.load(urllib.request.urlopen(f"https://picsum.photos/v2/list?page={p}&limit=100"))
L=[x for x in L if x["height"]>=x["width"]*0.7 or x["width"]>=1600]
json.dump(L,open("out/scenery/list.json","w"))
tw,th=240,320
for s in range(0,len(L),48):
    sh=Image.new("RGB",(8*tw,6*th),"white");d=ImageDraw.Draw(sh)
    for k,x in enumerate(L[s:s+48]):
        try:
            im=Image.open(io.BytesIO(urllib.request.urlopen(f"https://picsum.photos/id/{x['id']}/{tw}/{th}").read())).convert("RGB")
            sh.paste(im,((k%8)*tw,(k//8)*th));d.rectangle(((k%8)*tw,(k//8)*th,(k%8)*tw+46,(k//8)*th+20),fill="black");d.text(((k%8)*tw+4,(k//8)*th+4),x["id"],fill="yellow")
        except Exception as e: print(x["id"],e)
    sh.save(f"out/scenery/sheet_{s//48}.jpg",quality=80)
print(len(L))
