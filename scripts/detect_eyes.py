"""Ask Gemini (vision) for tight eye boxes in each pair image. env: IN_DIRS (comma), OUT_FILE, MODEL."""
import base64, json, os, sys, time, glob, urllib.request, urllib.error
KEY=os.environ["GEMINI_API_KEY"]; MODEL=os.environ.get("MODEL","gemini-3.1-pro-preview")
OUT=os.environ.get("OUT_FILE","out/eyes/eyes.json"); os.makedirs(os.path.dirname(OUT),exist_ok=True)
files=[]
for d in os.environ["IN_DIRS"].split(","):
    files+=sorted(glob.glob(d.strip()+"/*.jpg"))
only=os.environ.get("ONLY","")
if only: files=[f for f in files if any(o in f for o in only.split(","))]
res=json.load(open(OUT)) if os.path.exists(OUT) else {}
PROMPT=("This image has two line-art dog drawings: a small FRONT head emblem on the left and a full-body sitting dog on the right. "
 "List every visible dog EYE (the eyeball itself, as drawn: ring/outline with or without pupil, or a solid dark shape). "
 "Do NOT include sunglasses lenses, noses, mouths or tag/heart shapes. If a dog wears sunglasses and no eye is visible, return nothing for that dog. "
 "Return ONLY JSON: a list of objects {\"which\":\"front\"|\"back\",\"box_2d\":[ymin,xmin,ymax,xmax]} with coordinates normalized 0-1000, boxes tight around each single eye.")
url=f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
for f in files:
    k=f
    if k in res: continue
    body={"contents":[{"parts":[{"inline_data":{"mime_type":"image/jpeg","data":base64.b64encode(open(f,"rb").read()).decode()}},{"text":PROMPT}]}],
          "generationConfig":{"responseMimeType":"application/json","temperature":0}}
    req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    for a in range(4):
        try:
            r=json.load(urllib.request.urlopen(req,timeout=180))
            txt=r["candidates"][0]["content"]["parts"][0]["text"]
            res[k]=json.loads(txt); print(k,len(res[k])); break
        except Exception as e:
            print(k,"err",repr(e)[:150]); time.sleep(6*(a+1))
    json.dump(res,open(OUT,"w"),indent=1)
