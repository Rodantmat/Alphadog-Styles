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
        "anchor_poodle_line": "out/sets/line_p1/poodle__classic.jpg",
        "anchor_line": "out/oneline/gemini-nano-banana-2.1/line_bolder.jpg",
        "anchor_geo": "out/themes/gemini-nano-banana-2.1/geo_poly.jpg",
        "frenchie_pair": "out/cust_sheets/p2_frenchie_classic.png",
        "frenchie_heart": "out/cust_sheets/p2_frenchie_heart.png"}

cfg = json.load(open(os.environ.get("STYLES_FILE", "scripts/styles.json")))
OUT = os.environ.get("OUT_DIR", "out/linda")
styles = [s for s in cfg["styles"] if not ONLY or s["id"] in ONLY][:MAX_IMAGES]
os.makedirs(OUT, exist_ok=True)
url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
log = []
for s in styles:
    def _img(path):
        return {"inline_data": {"mime_type": "image/png" if path.endswith(".png") else "image/jpeg", "data": base64.b64encode(open(path, "rb").read()).decode()}}
    if s.get("refs"):  # explicit ordered list of image paths (edit jobs)
        parts = [_img(r) for r in s["refs"]]
    else:
        parts = [_img(REFS.get(s["ref"], s["ref"]))]
        if s.get("style_ref"):
            parts.append(_img(s["style_ref"]))
    parts.append({"text": cfg["base"] + " " + s["prompt"]})
    body = {"contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE"]}}
    asp = s.get("aspect") or os.environ.get("ASPECT")
    if asp: body["generationConfig"]["imageConfig"] = {"aspectRatio": asp}
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": API_KEY})
    resp = None
    for attempt in range(4):
        try:
            resp = json.load(urllib.request.urlopen(req, timeout=240)); break
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:400]; print(s["id"], "HTTP", e.code, msg, "attempt", attempt)
            if e.code in (401, 403): break
            time.sleep(8 * (attempt + 1))
        except Exception as e:
            print(s["id"], "err", repr(e)[:200]); time.sleep(8 * (attempt + 1))
    if resp is None:
        log.append({"id": s["id"], "ok": False, "error": "failed"}); continue
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
