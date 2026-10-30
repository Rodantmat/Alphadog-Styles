import json,os,sys
sys.path.insert(0,"scripts")
B="out/sets"
def P(th,s,v):
    for p in("p1","p2"):
        f=f"{B}/{th}_{p}/{s}__{v}.jpg"
        if os.path.exists(f): return f
    raise SystemExit((th,s,v))
KEEP=(" HARD RULES: Output the SAME canvas, same two drawings in the same positions and sizes, same line weight and drawing style. Change ONLY what is described. Pure black lines on flat white background, no gray, no shading, no text, no extra decorations.")
jobs=[]
jobs.append(("F5_cav_line_heart","line","cavalier_king_charles_spaniel","heart",[P("line","cavalier_king_charles_spaniel","classic")],
 "Image 1 is the cavalier heart design to fix: its full-body sitting dog on the right has NO chest lines. Image 2 is the classic cavalier: the flowing chest, neck and feathered chest contour lines on its chest and front are the truth. In image 1 draw exactly the same chest lines as the dog in image 2 (same shapes, same position, same line weight), keeping its collar with the small heart tag, ears and everything else. The heart and front head stay identical."+KEEP,"back"))
for th,desc in(("line","single flowing continuous line style"),("geo","bold geometric polygon lines style")):
  for v,acc in(("classic","no accessories"),("cool","the aviator sunglasses of image 1"),("heart","the collar with small heart tag and the heart of image 1")):
    jobs.append((f"M_{th}_{v}",th,"mini_poodle",v,[P(th,"poodle",v)],
     f"Image 1 is an APPROVED finished design of a standard poodle in {desc}. Redraw it as a MINI poodle: a small, cute, compact dog with a rounder fluffy head, a soft mid-length curly-ish wavy coat covering the head, ears and body (like a bichon / maltipoo / maltese mix: natural fluffy teddy-bear look, NOT a clipped show poodle, no pompoms, no topknot), soft fluffy drop ears, dark eyes, black nose. Draw the curly-ish texture with the same kind of lines as image 1 (do not add extra detail). KEEP IDENTICAL to image 1: the exact same drawing style, line weight, eye style (white iris, off-centre black pupil with highlight), layout (small front head emblem on the left, matching full-body sitting dog on the right), pose, composition, and accessories ({acc}). Pure black on flat white, no text.","both"))
c=[]
for jid,th,slug,v,refs,pr,side in jobs:
    ref=[P(th,slug,v)] if slug!="mini_poodle" else []
    r=([P(th,slug,v)] if slug!="mini_poodle" else [])+refs
    for k in "abcd":
        c.append({"id":f"{jid}__{k}","theme":th,"slug":slug,"variant":v,"side":side,"refs":r,"aspect":"3:2","prompt":pr})
json.dump({"base":"","styles":c},open("scripts/fix5_cands.json","w"),indent=1)
print(len(c))
