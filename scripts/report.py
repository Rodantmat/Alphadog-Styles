"""Combine tech + critic into verdicts. Usage: python report.py <dir> -> <dir>/REPORT.md, verdicts.json"""
import json, os, sys
d = sys.argv[1]
tech = {t["file"]: t for t in json.load(open(os.path.join(d, "tech.json")))}
crit = json.load(open(os.path.join(d, "critic.json")))
PRO_W = {"art_director": 10, "print_technician": 10, "ai_artifact_inspector": 10, "series_designer": 10,
         "marketplace_merchandiser": 10, "embroidery_digitizer": 4, "breed_expert": 4, "likeness_judge": 4, "ip_compliance_reviewer": 4}
CUST = ["genz_tiktok_shopper", "millennial_dog_mom", "male_owner_35_55", "gift_buyer", "art_lover"]
HARD_TECH = ("T10", "T2 no transparency")
rows = []
for f in sorted(set(tech) | set(crit)):
    c = crit.get(f, {}); t = tech.get(f, {})
    roles = {r.get("role"): r for r in c.get("roles", [])}
    pw = sum(PRO_W.values()); pro = sum(roles.get(k, {}).get("score", 0) * w for k, w in PRO_W.items()) / pw
    cs = [roles.get(k, {}).get("score", 0) for k in CUST]; cust = sum(cs) / len(cs)
    total = round(0.6 * pro + 0.4 * cust, 2)
    buyers = sum(1 for k in CUST if roles.get(k, {}).get("would_buy")); prices = [roles[k].get("max_price_usd") or 0 for k in CUST if k in roles]
    hard = [f"{k}: {r.get('hard_fail_reason')}" for k, r in roles.items() if r.get("hard_fail")]
    flags = t.get("tech_flags", [])
    rework_tech = [x for x in flags if x.startswith(("T2", "T3", "T7", "T10", "T11"))]
    if hard or not c or total < 5.5: verdict = "REJECT"
    elif total >= 7.5 and not rework_tech: verdict = "PASS"
    else: verdict = "REWORK"
    rows.append({"file": f, "verdict": verdict, "total": total, "pro": round(pro, 2), "customers": round(cust, 2),
                 "would_buy": f"{buyers}/5", "avg_price": round(sum(prices) / max(len(prices), 1), 2), "hard_fails": hard,
                 "tech_flags": flags, "scores": {k: roles.get(k, {}).get("score") for k in list(PRO_W) + CUST},
                 "must_fix": c.get("must_fix_before_production", []), "strengths": c.get("top_strengths", []),
                 "style_detected": c.get("style_detected"), "prompt_rewrite": c.get("prompt_rewrite")})
rows.sort(key=lambda r: -r["total"])
json.dump(rows, open(os.path.join(d, "verdicts.json"), "w"), indent=1)
L = ["# Art Analyzer Report", "", "| Rank | Design | Verdict | Total | Pros | Customers | Would buy | Avg $ | Tech flags |", "|---|---|---|---|---|---|---|---|---|"]
for i, r in enumerate(rows, 1):
    L.append(f"| {i} | {r['file'][:-4]} | **{r['verdict']}** | {r['total']} | {r['pro']} | {r['customers']} | {r['would_buy']} | {r['avg_price']} | {len(r['tech_flags'])} |")
for r in rows:
    L += ["", f"## {r['file'][:-4]} — {r['verdict']} ({r['total']})", f"Reads as: {r['style_detected']}",
          "Scores: " + ", ".join(f"{k}={v}" for k, v in r["scores"].items())]
    if r["hard_fails"]: L.append("HARD FAILS: " + "; ".join(r["hard_fails"]))
    L.append("Strengths: " + "; ".join(r["strengths"]))
    L.append("Must fix: " + "; ".join(r["must_fix"]))
    L.append("Tech flags: " + "; ".join(r["tech_flags"]))
open(os.path.join(d, "REPORT.md"), "w").write("\n".join(L))
for r in rows: print(r["verdict"], r["total"], r["file"])
