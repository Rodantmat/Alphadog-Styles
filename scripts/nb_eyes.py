"""nb_eyes.py IN_GLOB OUT.json -- Gemini vision eye boxes for each png. -> {file: [{which,box_2d:[ymin,xmin,ymax,xmax]/1000}]}"""
import base64, glob, io, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
KEY=os.environ["GEMINI_API_KEY"]; MODEL=os.environ.get("MODEL","gemini-3.1-pro-preview")
files=sorted(glob.glob(sys.argv[1])); OUT=sys.argv[2]
res=json.load(open(OUT)) if os.path.exists(OUT) else {}
PROMPT=("This image has two line-art dog drawings: a small FRONT head emblem on the left and a full-body sitting dog on the right. "
 "List every visible dog EYE (the eyeball as drawn: ring/outline with or without pupil, or a solid dark shape). Each dog normally has two eyes. "
 "Do NOT include sunglasses lenses, noses, mouths or heart tags. If a dog wears sunglasses and no eye is visible, return nothing for that dog. "
 "Return ONLY JSON: a list of objects {\"which\":\"front\"|\"back\",\"box_2d\":[ymin,xmin,ymax,xmax]} with coordinates normalized 0-1000, boxes TIGHT around each single eye (just the eyeball, not the eyebrow or surrounding fold lines).")
def run(f):
    if f in res: return
    b=io.BytesIO(); Image.open(f).convert("RGB").save(b,"JPEG",quality=92)
    body={"contents":[{"parts":[{"inline_data":{"mime_type":"image/jpeg","data":base64.b64encode(b.getvalue()).decode()}},{"text":PROMPT}]}],"generationConfig":{"responseMimeType":"application/json","temperature":0}}
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    for a in range(4):
        try:
            req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
            r=json.load(urllib.request.urlopen(req,timeout=180)); res[f]=json.loads(r["candidates"][0]["content"]["parts"][0]["text"]); print(f,len(res[f]),flush=True); return
        except Exception as e: print(f,"err",repr(e)[:120],flush=True); time.sleep(6*(a+1))
with ThreadPoolExecutor(4) as ex: list(ex.map(run,files))
os.makedirs(os.path.dirname(OUT),exist_ok=True); json.dump(res,open(OUT,"w"),indent=1)
