"""nb_gen.py JOBS.json OUTDIR [N=1] -- Gemini image generation/edit. env MODELS (comma, fallback order), THREADS.
job: {id, refs:[repo paths], prompt, aspect}. Outputs OUTDIR/<id>__<k>.png (k=a,b,c..). Skips existing."""
import base64, json, os, sys, time, urllib.request, urllib.error, threading
from concurrent.futures import ThreadPoolExecutor
KEY=os.environ["GEMINI_API_KEY"]
MODELS=os.environ.get("MODELS","gemini-3-pro-image-preview,gemini-2.5-flash-image").split(",")
jobs=json.load(open(sys.argv[1])); OUT=sys.argv[2]; N=int(sys.argv[3]) if len(sys.argv)>3 else 1
only=os.environ.get("ONLY","")
os.makedirs(OUT,exist_ok=True); log=[]; lock=threading.Lock()
def img(p): return {"inline_data":{"mime_type":"image/png" if p.endswith(".png") else "image/jpeg","data":base64.b64encode(open(p,"rb").read()).decode()}}
def run(a):
    j,k=a; fn=f"{OUT}/{j['id']}__{k}.png"
    if os.path.exists(fn): return
    parts=[img(r) for r in j["refs"]]+[{"text":j["prompt"]}]
    body={"contents":[{"parts":parts}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":j.get("aspect","3:2")}}}
    for model in MODELS:
        url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        for att in range(3):
            try:
                req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
                r=json.load(urllib.request.urlopen(req,timeout=300))
                for c in r.get("candidates",[]):
                    for p in c.get("content",{}).get("parts",[]):
                        d=p.get("inlineData") or p.get("inline_data")
                        if d:
                            open(fn,"wb").write(base64.b64decode(d["data"]))
                            print(j["id"],k,"OK",model,flush=True); return
                print(j["id"],k,"no image",model,str(r)[:200],flush=True); break
            except urllib.error.HTTPError as e:
                m=e.read().decode()[:200]; print(j["id"],k,"HTTP",e.code,model,m,flush=True)
                if e.code in(400,404): break
                time.sleep(10*(att+1))
            except Exception as e:
                print(j["id"],k,"err",repr(e)[:120],flush=True); time.sleep(8*(att+1))
    with lock: log.append(fn)
tasks=[(j,"abcdefgh"[i]) for j in jobs for i in range(N) if not only or any(o in j["id"] for o in only.split(","))]
with ThreadPoolExecutor(int(os.environ.get("THREADS","4"))) as ex: list(ex.map(run,tasks))
print("failed",log)
