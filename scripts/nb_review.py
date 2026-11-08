"""nb_review.py REQS.json OUT.json -- Gemini-vision reviewer. REQS: [{id, images:[paths], prompt}] -> OUT: {id: parsed JSON or raw}. env MODEL, THREADS"""
import base64, io, json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
KEY=os.environ["GEMINI_API_KEY"]; MODEL=os.environ.get("MODEL","gemini-3.1-pro-preview")
reqs=json.load(open(sys.argv[1])); OUT=sys.argv[2]
res=json.load(open(OUT)) if os.path.exists(OUT) else {}
def enc(p):
    im=Image.open(p).convert("RGB")
    if im.width>1600: im=im.resize((1600,round(im.height*1600/im.width)),Image.LANCZOS)
    b=io.BytesIO(); im.save(b,"JPEG",quality=90)
    return {"inline_data":{"mime_type":"image/jpeg","data":base64.b64encode(b.getvalue()).decode()}}
def run(r):
    if r["id"] in res: return
    parts=[]
    for i,p in enumerate(r["images"]): parts+= [{"text":f"Image {i+1}:"},enc(p)]
    parts.append({"text":r["prompt"]})
    body={"contents":[{"parts":parts}],"generationConfig":{"responseMimeType":"application/json","temperature":0}}
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    for a in range(4):
        try:
            req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
            t=json.load(urllib.request.urlopen(req,timeout=240))["candidates"][0]["content"]["parts"][0]["text"]
            try: res[r["id"]]=json.loads(t)
            except Exception: res[r["id"]]={"raw":t}
            print(r["id"],"ok",flush=True); return
        except Exception as e:
            print(r["id"],"err",repr(e)[:150],flush=True); time.sleep(6*(a+1))
with ThreadPoolExecutor(int(os.environ.get("THREADS","4"))) as ex: list(ex.map(run,reqs))
os.makedirs(os.path.dirname(OUT),exist_ok=True); json.dump(res,open(OUT,"w"),indent=1)
