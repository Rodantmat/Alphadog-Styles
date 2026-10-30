import json, os, sys, shutil, cv2
sys.path.insert(0, "scripts")
from fix_tools import *
SEL = {  # job id -> (candidate letter, mode)
 "L_poodle_cool": ("a", "tail"), "L_dachshund_heart": ("a", "tail"), "L_corgi_cool": ("a", "full"),
 "L_boxer_classic": ("a", "full"), "L_boxer_cool": ("a", "full"), "L_pom_cool": ("a", "full"),
 "L_pom_heart": ("a", "full"), "L_shih_heart": ("a", "tail"), "L_havanese_heart": ("a", "full"),
 "G_dachs_cool": ("a", "tail"), "G_lab_heart": ("a", "full"), "G_poodle_classic": ("a", "tail"),
 "G_gsp_classic": ("a", "tail"), "G_gsp_cool": ("a", "full"),
 "G_yorkie_classic": ("a", "full"), "G_yorkie_cool": ("a", "full"), "G_yorkie_heart": ("a", "full"),
 "G_corgi_classic": ("a", "full"), "G_corgi_cool": ("a", "full"),
 "G_shih_heart": ("d", "full"), "G_shih_cool": ("d", "tail"),
 "G_chi_classic": ("b", "tail"), "G_chi_heart": ("a", "full"), "G_boston_cool": ("a", "full")}
OVR = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
SEL.update({k: tuple(v) for k, v in OVR.items()})
jobs = {j["id"]: j for j in json.load(open("scripts/fix_jobs.json"))["styles"]}
if os.path.exists("out/sets_fix"): shutil.rmtree("out/sets_fix")
shutil.copytree("out/sets_orig", "out/sets_fix")
def cand(jid, k):
    for p in (1, 2, 3):
        f = f"out/fix1/p{p}/{jid}__{k}.jpg"
        if os.path.exists(f): return f
changed = []
for jid, (k, mode) in SEL.items():
    j = jobs[jid]; o = j["refs"][0]
    c = cand(jid, k)
    side = j["side"]
    img = composite_tail(o, c) if mode == "tail" else composite(o, c, side if side != "both" else "both")
    dst = o.replace("sets_orig", "sets_fix")
    cv2.imwrite(dst, img, [cv2.IMWRITE_JPEG_QUALITY, 95]); changed.append(dst)
json.dump(changed, open("out/sets_fix_changed.json", "w"), indent=0)
print(len(changed))
