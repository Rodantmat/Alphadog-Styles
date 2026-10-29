"""Combine tech + critic into verdicts. Usage: python report.py <dir> -> <dir>/REPORT.md, verdicts.json
Two separate grades:
  CONCEPT  = is the art good and sellable (art, series, market, artifacts, breed, likeness, IP, customers)
  PRODUCTION = what must be fixed before printing (auto-fixable in post vs needs regeneration)"""
import json, os, re, sys
d = sys.argv[1]
tech = {t["file"]: t for t in json.load(open(os.path.join(d, "tech.json")))}
crit = json.load(open(os.path.join(d, "critic.json")))
CONCEPT_W = {"art_director": 12, "series_designer": 10, "marketplace_merchandiser": 10, "ai_artifact_inspector": 8,
             "breed_expert": 5, "likeness_judge": 5, "ip_compliance_reviewer": 5}
CUST = ["genz_tiktok_shopper", "millennial_dog_mom", "male_owner_35_55", "gift_buyer", "art_lover"]
CONCEPT_HARD = {"ai_artifact_inspector", "ip_compliance_reviewer", "breed_expert", "art_director"}
AUTO_FIX = {"T1": "AI upscale to 4500 px", "T2": "background removal to transparent PNG", "T3": "hard alpha threshold (no semi-transparent pixels)",
            "T4": "halftone gradients 35-45 LPI for dark garments", "T11": "despeckle / remove stray marks", "T9": "symmetry check"}
NEEDS_REGEN = {"T7": "too low contrast for most garments", "T10": "art cropped by canvas", "T6": "detail lost at small sizes"}
ORDER = ["art_director", "print_technician", "embroidery_digitizer", "ai_artifact_inspector", "ip_compliance_reviewer", "series_designer",
         "marketplace_merchandiser", "breed_expert", "likeness_judge", "genz_tiktok_shopper", "millennial_dog_mom", "male_owner_35_55", "gift_buyer", "art_lover"]
def norm(s):
    s = str(s or "").strip().lower()
    if s.isdigit() and 1 <= int(s) <= len(ORDER): return ORDER[int(s) - 1]
    return re.sub(r"^\d+\s*[-_.:]?\s*", "", s)
rows = []
for f in sorted(set(tech) | set(crit)):
    c = crit.get(f, {}); t = tech.get(f, {})
    roles = {norm(r.get("role")): r for r in c.get("roles", [])}
    sc = lambda k: (roles.get(k, {}).get("score") or 0)
    concept_pro = sum(sc(k) * w for k, w in CONCEPT_W.items()) / sum(CONCEPT_W.values())
    cust = sum(sc(k) for k in CUST) / len(CUST)
    concept = round(0.6 * concept_pro + 0.4 * cust, 2)
    buyers = sum(1 for k in CUST if roles.get(k, {}).get("would_buy"))
    prices = [roles[k].get("max_price_usd") or 0 for k in CUST if k in roles]
    avg_price = round(sum(prices) / max(len(prices), 1), 2)
    concept_hard = [f"{k}: {r.get('hard_fail_reason')}" for k, r in roles.items() if r.get("hard_fail") and k in CONCEPT_HARD]
    prod_notes = [f"{k}: {r.get('hard_fail_reason')}" for k, r in roles.items() if r.get("hard_fail") and k not in CONCEPT_HARD]
    flags = t.get("tech_flags", [])
    auto = sorted({AUTO_FIX[x[:3].strip()] for x in flags if x[:3].strip() in AUTO_FIX})
    regen = sorted({NEEDS_REGEN[x[:3].strip()] for x in flags if x[:3].strip() in NEEDS_REGEN})
    cap_ok = sc("embroidery_digitizer") >= 6 and t.get("thread_colors_est", 99) <= 6
    print_ok = sc("print_technician") >= 6
    # verdict on CONCEPT (production handled by pipeline unless regen needed)
    if not c: verdict = "NO REVIEW"
    elif concept_hard or concept < 5.5 or buyers <= 1: verdict = "REJECT"
    elif concept >= 7.5 and buyers >= 4 and avg_price >= 24 and not regen: verdict = "PASS"
    else: verdict = "REWORK"
    rows.append({"file": f, "verdict": verdict, "concept": concept, "concept_pro": round(concept_pro, 2), "customers": round(cust, 2),
                 "would_buy": f"{buyers}/5", "avg_price": avg_price, "concept_hard_fails": concept_hard,
                 "print_score": sc("print_technician"), "cap_score": sc("embroidery_digitizer"), "cap_ready": cap_ok, "print_ready_raw": print_ok,
                 "auto_fixes": auto, "needs_regen": regen, "production_notes": prod_notes, "tech_flags": flags,
                 "scores": {k: roles.get(k, {}).get("score") for k in list(CONCEPT_W) + ["print_technician", "embroidery_digitizer"] + CUST},
                 "must_fix": c.get("must_fix_before_production", []), "strengths": c.get("top_strengths", []),
                 "style_detected": c.get("style_detected"), "prompt_rewrite": c.get("prompt_rewrite"),
                 "customer_quotes": {k: (roles.get(k, {}).get("problems") or [""])[0] for k in CUST}})
rows.sort(key=lambda r: -r["concept"])
json.dump(rows, open(os.path.join(d, "verdicts.json"), "w"), indent=1)
L = ["# Art Analyzer Report", "", "PASS needs: concept >= 7.5, >= 4/5 customers buy, avg price >= $24 (our tee price), no concept hard-fail, nothing needing regeneration.", "",
     "| Rank | Design | Verdict | Concept | Pros | Customers | Would buy | Avg $ | Print | Cap | Auto-fixes | Needs regen |",
     "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for i, r in enumerate(rows, 1):
    L.append(f"| {i} | {r['file'][:-4]} | **{r['verdict']}** | {r['concept']} | {r['concept_pro']} | {r['customers']} | {r['would_buy']} | {r['avg_price']} | {r['print_score']} | {r['cap_score']} | {len(r['auto_fixes'])} | {', '.join(r['needs_regen']) or '-'} |")
for r in rows:
    L += ["", f"## {r['file'][:-4]} — {r['verdict']} (concept {r['concept']})", f"Reads as: {r['style_detected']}",
          "Scores: " + ", ".join(f"{k}={v}" for k, v in r["scores"].items())]
    if r["concept_hard_fails"]: L.append("CONCEPT HARD FAILS: " + "; ".join(r["concept_hard_fails"]))
    L += ["Strengths: " + "; ".join(r["strengths"]), "Must fix: " + "; ".join(r["must_fix"]),
          "Auto-fixes in post: " + "; ".join(r["auto_fixes"]), "Customer reactions: " + " | ".join(f"{k}: {v}" for k, v in r["customer_quotes"].items())]
open(os.path.join(d, "REPORT.md"), "w").write("\n".join(L))
for r in rows: print(r["verdict"].ljust(7), r["concept"], r["would_buy"], r["avg_price"], r["file"])
