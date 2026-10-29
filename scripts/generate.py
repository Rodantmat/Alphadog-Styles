"""Generate style samples with Gemini image model from Linda reference photos.
Hard cap on images per run to protect the owner's budget."""
import base64, json, os, sys, time, urllib.request, urllib.error

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = os.environ.get("MODEL", "gemini-2.5-flash-image")
MAX_IMAGES = int(os.environ.get("MAX_IMAGES", "14"))  # hard cap per run
ONLY = [s for s in os.environ.get("ONLY", "").split(",") if s]
REFS = {"smile": "refs/linda/ref_2025-08_front_smile.jpg",
        "fluffy": "refs/linda/ref_2025-01_front_fluffy.jpg"}

cfg = json.load(open("scripts/styles.json"))
styles = [s for s in cfg["styles"] if not ONLY or s["id"] in ONLY][:MAX_IMAGES]
os.makedirs("out/linda", exist_ok=True)
url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
log = []
for s in styles:
    img_b64 = base64.b64encode(open(REFS[s["ref"]], "rb").read()).decode()
    body = {"contents": [{"parts": [
        {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}},
        {"text": cfg["base"] + " " + s["prompt"]}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]}}
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
                open(f"out/linda/{s['id']}.{ext}", "wb").write(base64.b64decode(d["data"]))
                saved = True; break
        if saved: break
    print(s["id"], "OK" if saved else "NO IMAGE", resp.get("usageMetadata", {}))
    log.append({"id": s["id"], "ok": saved, "usage": resp.get("usageMetadata", {})})
    time.sleep(2)
json.dump(log, open("out/linda/run_log.json", "w"), indent=1)
print("images:", sum(1 for x in log if x.get("ok")), "of", len(styles))
