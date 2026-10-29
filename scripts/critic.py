"""Layer B: 14-role critic panel via Gemini vision. Usage: python critic.py <dir>  (needs <dir>/tech.json)"""
import base64, json, os, sys, time, urllib.request, urllib.error

KEY = os.environ["GEMINI_API_KEY"]
MODEL = os.environ.get("CRITIC_MODEL", "gemini-3.1-pro-preview")
MAX = int(os.environ.get("MAX_CRITIQUES", "20"))  # hard cap per run
REF = os.environ.get("LIKENESS_REF", "refs/linda/ref_2025-08_front_smile.jpg")
d = sys.argv[1]
tech = {t["file"]: t for t in json.load(open(os.path.join(d, "tech.json")))}

ROLES = """PROFESSIONALS (judge craft and commercial viability):
1 art_director - composition, focal point, visual hierarchy, originality, how well the intended style is actually executed (is it truly that style or a generic drawing with a filter?), color harmony, wow factor.
2 print_technician - DTG/DTF on cotton tees: underbase halos from soft glows/feathered edges, gradients that print patchy on dark shirts, fine lines < 1 pt that disappear, tiny specks, white-on-white disappearing, how it reads at 12 in front print and 4 in left-chest.
3 embroidery_digitizer - can a simplified version be stitched on a cap front (4 x 2.25 in, max 6 thread colors, no gradients, lines >= 0.05 in, no tiny gaps)? What must be removed?
4 ai_artifact_inspector - eyes (shape, pupils, catchlights, matching), nose/mouth/tongue anatomy, ear symmetry, fur texture mush, melted or smeared areas, duplicated elements, stray marks, background bleed, uncanny look, upscaling halos.
5 ip_compliance_reviewer - any text/letters/signature/watermark; resemblance to a specific famous artwork composition, a protected character, a brand or logo; living-artist imitation. Flag hard_fail if real risk.
6 series_designer - would this style work as a consistent signature across 25 different dog breeds (short coats, pointy ears, wrinkled faces)? Is the style ownable/recognizable as one brand line?
7 marketplace_merchandiser - stopping power as a 150 px Etsy/eBay/TikTok Shop thumbnail, differentiation vs the saturated dog-shirt market, perceived value/price point.
8 breed_expert - does it read instantly as a Bichon-type poodle (round cloud head, drop ears, dark eyes, black nose)? Accuracy problems?
9 likeness_judge - compare with the reference photo (second image): does it look like THIS dog? What drifted?
CUSTOMERS (honest gut reactions, would they actually pay?):
10 genz_tiktok_shopper (19-25, trend-driven, wants fun/ironic/aesthetic)
11 millennial_dog_mom (28-40, owns a small fluffy dog, buys cute dog apparel)
12 male_owner_35_55 (owns a dog, dislikes 'cutesy', wears hoodies and caps)
13 gift_buyer (buying for a family member who loves their dog, price sensitive)
14 art_lover (gallery-goer, cares about craft and originality, hates generic AI look)"""

PROMPT = f"""You are a rigorous review board for a print-on-demand apparel brand (AlphaDog). Image 1 is a candidate t-shirt/hoodie/cap graphic: the head of a fluffy Bichon-style poodle in the style named "{{style}}". Image 2 is the real dog (likeness reference).
The brand wants rich, fun, exciting signature art that ALSO prints well on products and sells. Be harsh and specific. Calibrate scores: 5 = an average sellable POD design, 7 = clearly above average, 9-10 = exceptional and rare. Never give everyone 8. Every problem must be concrete (where, what) and every fix actionable (prompt change or post-processing step).
Measured technical data from our code (trust these numbers): {{tech}}
Roles:
{ROLES}
Return ONLY JSON:
{{{{"style_detected":"what style it actually reads as","roles":[{{{{"role":"<id>","score":0-10,"problems":["..."],"fixes":["..."],"hard_fail":false,"hard_fail_reason":"","would_buy":null,"max_price_usd":null}}}}],"top_strengths":["..."],"must_fix_before_production":["..."],"prompt_rewrite":"an improved full generation prompt for this style that fixes the issues while keeping the dog head front-facing, head-only, no text"}}}}
Customers (10-14) must fill would_buy (true/false) and max_price_usd for a tee."""

def call(img_path, style, techsum):
    parts = [{"inline_data": {"mime_type": "image/png", "data": base64.b64encode(open(img_path, "rb").read()).decode()}},
             {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(open(REF, "rb").read()).decode()}},
             {"text": PROMPT.format(style=style, tech=json.dumps(techsum))}]
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseMimeType": "application/json", "temperature": 0.3}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
    r = json.load(urllib.request.urlopen(req, timeout=300))
    txt = "".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"] if not p.get("thought"))
    txt = txt.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(txt), r.get("usageMetadata", {})

out = {}
errors = []
ONLY = [x for x in os.environ.get("ONLY", "").split(",") if x]
files = sorted(f for f in os.listdir(d) if f.endswith(".png") and (not ONLY or f in ONLY))[:MAX]
for f in files:
    t = tech.get(f, {})
    techsum = {k: t.get(k) for k in ["subject_bbox_px", "upscale_needed", "soft_edge_share", "bg_low_contrast_edge", "gradient_share",
                                      "thread_colors_est", "chest_detail_survival", "thumb_detail_survival", "near_white_share",
                                      "usable_garments", "asymmetry", "stray_marks_px", "tech_flags"]}
    style = f[3:-4].replace("_", " ")
    for attempt in range(3):
        try:
            res, usage = call(os.path.join(d, f), style, techsum); res["usage"] = usage; out[f] = res
            print(f, "ok", usage.get("totalTokenCount")); break
        except urllib.error.HTTPError as e:
            m = e.read().decode()[:600]; print(f, "HTTP", e.code, m); errors.append({"file": f, "http": e.code, "msg": m}); time.sleep(10)
        except Exception as e:
            print(f, "err", repr(e)[:300]); errors.append({"file": f, "err": repr(e)[:600]}); time.sleep(5)
    time.sleep(1)
json.dump(out, open(os.path.join(d, "critic.json"), "w"), indent=1)
json.dump(errors, open(os.path.join(d, "critic_errors.json"), "w"), indent=1)
