"""Generate style samples with Gemini image model from Linda reference photos.
Hard cap on images per run to protect the owner's budget."""
import base64, json, os, sys, time, urllib.request, urllib.error

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = os.environ.get("MODEL", "gemini-2.5-flash-image")
MAX_IMAGES = int(os.environ.get("MAX_IMAGES", "14"))  # hard cap per run
ONLY = [s for s in os.environ.get("ONLY", "").split(",") if s]
REFS = {"smile": "refs/linda/ref_2025-08_front_smile.jpg",
        "fluffy": "refs/linda/ref_2025-01_front_fluffy.jpg",
        "full": "refs/linda/ref_2014_full_sitting.jpg",
        "oneline_sheet": "refs/style_oneline_sheet.jpg",
        "frenchie_pair": "out/cust_sheets/p2_frenchie_classic.png",
        "frenchie_heart": "out/cust_sheets/p2_frenchie_heart.png"}

cfg = json.load(open(os.environ.get("STYLES_FILE", "scripts/styles.json")))
OUT = os.environ.get("OUT_DIR", "out/linda")
styles = [s for s in cfg["styles"] if not ONLY or s["id"] in ONLY][:MAX_IMAGES]
os.makedirs(OUT, exist_ok=True)
url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
log = []
for s in styles:
    img_b64 = base64.b64encode(open(REFS[s["ref"]], "rb").read()).decode()
    parts = [{"inline_data": {"mime_type": "image/png" if REFS[s["ref"]].endswith(".png") else "image/jpeg", "data": img_b64}}]
    if s.get("style_ref"):  # match an existing design's exact style (front/back coherence)
        parts.append({"inline_data": {"mime_type": "image/png", "data": base64.b64encode(open(s["style_ref"], "rb").read()).decode()}})
    parts.append({"text": cfg["base"] + " " + s["prompt"]})
    body = {"contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE"]}}
    if os.environ.get("ASPECT"): body["generationConfig"]["imageConfig"] = {"aspectRatio": os.environ["ASPECT"]}
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": API_KEY})
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:400]; print(s["id"], "HTTP", e.code, msg); log.append({"id": s["id"], "error": e.code, "msg": msg})
        if e.code in (400, 401, 403): break
        time.sleep(5); continue
    saved = False
    for c in resp.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            d = p.get("inlineData") or p.get("inline_data")
            if d:
                ext = "png" if "png" in d.get("mimeType", d.get("mime_type", "")) else "jpg"
                open(f"{OUT}/{s['id']}.{ext}", "wb").write(base64.b64decode(d["data"]))
                saved = True; break
        if saved: break
    print(s["id"], "OK" if saved else "NO IMAGE", resp.get("usageMetadata", {}))
    log.append({"id": s["id"], "ok": saved, "usage": resp.get("usageMetadata", {})})
    time.sleep(2)
json.dump(log, open(f"{OUT}/run_log.json", "w"), indent=1)
print("images:", sum(1 for x in log if x.get("ok")), "of", len(styles))
