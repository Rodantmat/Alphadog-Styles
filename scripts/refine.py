"""Refinement loop for ONE design family, run inside GitHub Actions.
generate -> tech -> critic panel -> report -> next-round prompts from the critics' fixes, until PASS or rounds exhausted.
Env: FAMILY (geometric|continuous|silhouette), ROUNDS, VARIANTS, MODEL, CRITIC_MODEL, GEMINI_API_KEY"""
import json, os, subprocess, sys, shutil
FAMILY = os.environ["FAMILY"]; ROUNDS = int(os.environ.get("ROUNDS", "4")); VARIANTS = int(os.environ.get("VARIANTS", "4"))
ROOT = f"out/refine/{FAMILY}"
BASE = ("Using the attached photo of this exact dog as the likeness reference (keep her round fluffy head shape, long drop ears, dark eyes, button nose and happy tongue-out expression recognizable), "
        "create a professional brand-quality logo artwork of her HEAD ONLY for a premium apparel brand. Pure black on a flat pure white background, no gray, no gradients, no texture, no shadow, no frame, no collar, no body below the neck. "
        "Generous empty margin on every side, art centered and symmetric-feeling. All lines and shapes BOLD: minimum stroke about 3% of the image width so it stays readable at 4 inches and on a black shirt when inverted to white. "
        "Confident, deliberate, original graphic design (not generic clip art, not a photo filter, not an AI portrait). Crisp vector-like edges. Absolutely no text, letters, signature or watermark.")
SEEDS = {
 "geometric": [
  ("polyheavy", "Style: geometric polygon head, heavy bold outer outline, a few thick triangulation lines and bold solid black triangles for eyes and nose, perfectly symmetrical, front-facing."),
  ("compass", "Style: geometric icon built only from perfect circles and arcs (compass construction), thick even line weight, the round head, curly fur tufts and drop ears from overlapping circle segments, front-facing."),
  ("facets", "Style: bold faceted crystal head made of flat solid black and white triangles only (no gray), strong angular facets, symmetrical, front-facing."),
  ("wire", "Style: thick straight-line geometric construction, head formed by bold lines meeting at precise angles, a few solid black accents for eyes and nose, symmetrical, front-facing, architectural."),
 ],
 "continuous": [
  ("bold1line", "Style: ONE single continuous unbroken bold line (thick marker weight, even stroke) that never lifts, confident loops for the curly fur, front-facing."),
  ("loops", "Style: one continuous thick line spiraling and looping to describe the cloud-like curly fur, playful yet elegant, eyes and nose as bold dots, front-facing."),
  ("swash", "Style: one continuous bold calligraphic line with thick-to-thin swell, flowing ears that sweep outward, elegant and sparse, three-quarter view."),
  ("geoline", "Style: one continuous thick line made of smooth geometric curves and sharp turns, minimal, modern, the line crossing itself to form the ears, front-facing."),
 ],
 "silhouette": [
  ("solid", "Style: pure solid black silhouette of the head and ears with eyes, nose and tongue carved out as white negative space, iconic, front-facing."),
  ("badge", "Style: solid black circle badge with the dog head carved out as white negative space, the fluffy head breaking slightly out of the circle at the top, front-facing."),
  ("stencil", "Style: bold high-contrast stencil, solid black shapes and white negative space define fur masses, eyes and ears, crisp vinyl-cut decal, front-facing."),
  ("bridges", "Style: cut-paper stencil with bold white stencil bridges separating solid black shapes, graphic and industrial, front-facing."),
 ]}
def sh(cmd, env=None):
    e = dict(os.environ); e.update(env or {})
    r = subprocess.run(cmd, shell=True, env=e, capture_output=True, text=True); print(r.stdout[-1500:], r.stderr[-800:]); return r
variants = [{"id": f"r1_{n}", "ref": "smile", "prompt": p} for n, p in SEEDS[FAMILY]][:VARIANTS]
best_all = None; history = []
for rnd in range(1, ROUNDS + 1):
    d = f"{ROOT}/r{rnd}"; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    cfgp = f"{ROOT}/r{rnd}_styles.json"; json.dump({"base": BASE, "styles": variants}, open(cfgp, "w"), indent=1)
    sh("python3 scripts/generate.py", {"STYLES_FILE": cfgp, "OUT_DIR": d, "MAX_IMAGES": str(VARIANTS)})
    sh(f'python3 scripts/analyze_tech.py "{d}"')
    sh(f'python3 scripts/critic.py "{d}"', {"MAX_CRITIQUES": str(VARIANTS),
        "BRIEF": f"AlphaDog premium dog-head apparel line, family: {FAMILY}. Must be bold enough to print on black AND white tees, work as a small left-chest emblem and a large back print, and be replicable across 25 breeds.",
        "SUBJECT": f"the head of a fluffy Bichon-style poodle, {FAMILY} line style"})
    if not os.path.exists(f"{d}/critic.json") or not json.load(open(f"{d}/critic.json")): print("no critiques round", rnd); continue
    sh(f'python3 scripts/report.py "{d}"')
    v = json.load(open(f"{d}/verdicts.json"))
    history.append({"round": rnd, "top": [(r["file"], r["verdict"], r["concept"], r["would_buy"], r["avg_price"]) for r in v[:4]]})
    if v and (best_all is None or v[0]["concept"] > best_all[1]["concept"]): best_all = (f"{d}/{v[0]['file']}", v[0])
    if v and v[0]["verdict"] == "PASS": print("PASS reached round", rnd); break
    if rnd == ROUNDS: break
    # next round: evolve the top 2 (redraw with critics' fixes, anchored on the current best image) + their critic-written fresh prompts
    nxt = []
    for i, r in enumerate(v[:2]):
        fixes = "; ".join((r["must_fix"] or [])[:4])
        nxt.append({"id": f"r{rnd+1}_evolve{i+1}", "ref": "smile", "style_ref": f"{d}/{r['file']}",
            "prompt": f"Image 2 is the current best draft of this design. Redraw it improved: keep its concept and style identity and the dog likeness from image 1, head only, no text. Apply these fixes: {fixes}. Keep every line bold and the result perfectly clean black on white."})
        if r.get("prompt_rewrite"): nxt.append({"id": f"r{rnd+1}_fresh{i+1}", "ref": "smile", "prompt": "Bold lines minimum 3% of image width. " + r["prompt_rewrite"]})
    variants = nxt[:VARIANTS]
if best_all:
    shutil.copy(best_all[0], f"{ROOT}/BEST.png")
    json.dump({"family": FAMILY, "best": best_all[0], "best_verdict": best_all[1], "history": history}, open(f"{ROOT}/summary.json", "w"), indent=1)
    print("BEST", best_all[0], best_all[1]["verdict"], best_all[1]["concept"])
