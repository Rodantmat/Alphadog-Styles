"""Draft custom dog art for new custom-design requests.
For each request with status "new": download the customer's photos from the store, ask Gemini to draw THIS dog in the exact AlphaDog
style (style sheet rendered from our own production art), vectorize with the same pipeline as the catalog art, upload head + full-body
SVGs to the store as drafts (status in_review) and email the owner to review and send the quote from the admin page.
Hard cap: 2 image generations per request (budget). Env: GEMINI_API_KEY, STORE_URL, STORE_ADMIN_TOKEN, ONLY (optional request id)."""
import os,json,base64,urllib.request,urllib.error,subprocess,time,io,random
import cairosvg
from PIL import Image
KEY=os.environ["GEMINI_API_KEY"]; STORE=os.environ["STORE_URL"].rstrip("/"); ADM=os.environ["STORE_ADMIN_TOKEN"]; ONLY=os.environ.get("ONLY","").strip()
MODEL=os.environ.get("MODEL","gemini-2.5-flash-image")
def st(m,p,b=None,raw=False):
    r=urllib.request.Request(STORE+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"x-admin-token":ADM,"content-type":"application/json","User-Agent":"a"})
    resp=urllib.request.urlopen(r,timeout=120); return resp.read() if raw else json.load(resp)
def sheet(theme,style):  # style reference: our own production pair (head emblem left, full body right) rendered from the catalog SVGs
    W,H=1600,900; can=Image.new("RGB",(W,H),"white")
    for i,(part,box) in enumerate([("front",(60,150,700,600)),("back",(860,60,680,780))]):
        png=cairosvg.svg2png(url=f"store/art/{theme}_{style}/labrador_retriever_{part}.svg",output_height=box[3])
        im=Image.open(io.BytesIO(png)).convert("RGBA")
        if im.width>box[2]: im=im.resize((box[2],int(im.height*box[2]/im.width)))
        can.paste(im,(box[0]+(box[2]-im.width)//2,box[1]+(box[3]-im.height)//2),im)
    o=io.BytesIO(); can.save(o,"PNG"); return o.getvalue()
def gemini(parts):
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    body={"contents":[{"parts":parts}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"16:9"}}}
    for a in range(3):
        try:
            r=json.load(urllib.request.urlopen(urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY}),timeout=240))
            for c in r.get("candidates",[]):
                for p in c.get("content",{}).get("parts",[]):
                    d=p.get("inlineData") or p.get("inline_data")
                    if d: return base64.b64decode(d["data"])
            print("no image in response",str(r)[:300])
        except urllib.error.HTTPError as e: print("gemini",e.code,e.read().decode()[:300]); time.sleep(10*(a+1))
    return None
reqs=st("GET","/api/internal/custom?status=new")["items"]
if ONLY: reqs=[r for r in st("GET","/api/internal/custom")["items"] if r["id"]==ONLY]
print("requests to draft:",[r["id"] for r in reqs])
os.makedirs("out/custom",exist_ok=True)
for r in reqs[:3]:
    rid=r["id"]; d=r["data"]; dog=d["dog"]
    theme=d["style"].get("theme") or "line"; style=d["style"].get("style") or "classic"
    if theme not in("line","geo"): theme="line"
    if style not in("classic","cool","heart"): style="classic"
    st("POST",f"/api/internal/custom/{rid}",{"status":"in_review","note":None})
    photos=[st("GET",f"/api/internal/custom/{rid}/photo/{i}",raw=True) for i in range(min(r["photos"],5))]
    desc=", ".join(f"{k}: {v}" for k,v in dog.items() if v and k!="name")
    prompt=("The first images are photos of ONE specific dog. The LAST image is our style sheet: on the left a head-only emblem, on the right the full body sitting, "
      "drawn as clean bold black line art on pure white. Draw THIS dog (keep its real proportions, ear shape and set, muzzle length, eye shape, tail, "
      "coat pattern and markings as outlined shapes) in EXACTLY the same art style, line weight and layout as the style sheet: head emblem on the left, full body sitting on the right, "
      "same size and spacing. Pure black lines on pure white, no gray, no shading, no color, no text, no frame, no background, no collar unless the owner asks. "
      +(f"Owner notes about the dog: {desc}." if desc else ""))
    parts=[{"inline_data":{"mime_type":"image/jpeg","data":base64.b64encode(p).decode()}} for p in photos]+[{"inline_data":{"mime_type":"image/png","data":base64.b64encode(sheet(theme,style)).decode()}},{"text":prompt}]
    ok=False
    for attempt in range(2):   # budget cap: 2 generations per request
        img=gemini(parts)
        if not img: continue
        src=f"out/custom/{rid}_sheet{attempt}.png"; Image.open(io.BytesIO(img)).convert("RGB").save(src)
        pre=f"out/custom/{rid}_{attempt}"
        if subprocess.run(["python3","scripts/vectorize.py",src,pre]).returncode!=0: continue
        try:
            head=open(pre+"_front.svg").read(); body=open(pre+"_back.svg").read()
            if len(head)<500 or len(body)<500: raise ValueError("empty trace")
        except Exception as e: print("vector fail",e); continue
        st("POST",f"/api/internal/custom/{rid}",{"art":{"head":{"mime":"image/svg+xml","body":head},"body":{"mime":"image/svg+xml","body":body}},"status":"in_review",
           "note":None})
        st("POST","/api/internal/send",{"to":os.environ.get("OWNER_EMAIL","rodolfoaamattos@gmail.com"),"mailbox":"custom","subject":f"Custom art draft ready: {rid}",
           "html":f"<p>A draft of the custom design for <b>{dog.get('name') or rid}</b> ({r['email']}) is ready.</p><p>Review it, set the design fee and press <b>Save + send preview</b> on <a href='{STORE}/#/admin'>the admin page</a>. If it needs another pass, reply here or redraw by running the custom-art workflow for {rid}.</p>"})
        print("DRAFTED",rid,flush=True); ok=True; break
    if not ok:
        st("POST",f"/api/internal/custom/{rid}",{"status":"new"})
        print("DRAFT FAILED",rid)
