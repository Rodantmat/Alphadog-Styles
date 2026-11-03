"""Merge shard artifacts (_qa/qa-<shard>/...) into out/site_qa and write results.json + SUMMARY.txt."""
import json, os, shutil, sys, glob

src, dst = sys.argv[1], sys.argv[2]
if os.path.isdir(dst):
    shutil.rmtree(dst)
os.makedirs(dst)
for d in sorted(glob.glob(f"{src}/qa-*")):
    shutil.copytree(d, dst, dirs_exist_ok=True)
res = {}
for f in sorted(glob.glob(f"{dst}/*.json")):
    if f.endswith("results.json"):
        continue
    r = json.load(open(f))
    res[r["shard"]] = r
lines = []
tp = tf = 0
for sh, r in res.items():
    p = sum(v[0] for v in r["checks"].values()); fl = sum(v[1] for v in r["checks"].values())
    tp += p; tf += fl
    lines.append(f"== {sh}: {p} checks passed, {fl} failed, {len(r['defects'])} distinct defects, {r['secs']}s, errors {r['error_counts']}")
    for a, (ap, af) in sorted(r["checks"].items()):
        lines.append(f"   {a}: {ap} pass / {af} fail")
    for d in sorted(r["defects"], key=lambda d: ["critical", "high", "medium", "low", "info"].index(d["sev"])):
        lines.append(f"   [{d['sev']}] {d['title']} (x{d['count']})")
lines.insert(0, f"TOTAL {tp} checks passed, {tf} failed; shards: {list(res)}")
open(f"{dst}/SUMMARY.txt", "w").write("\n".join(lines) + "\n")
json.dump({k: {kk: vv for kk, vv in v.items() if kk not in ("data",)} for k, v in res.items()}, open(f"{dst}/results.json", "w"), indent=1, ensure_ascii=False)
print("\n".join(lines))
