import json,os
B="out/sets"
def P(th,slug,v):
    for p in ("p1","p2"):
        f=f"{B}/{th}_{p}/{slug}__{v}.jpg"
        if os.path.exists(f):return f
    raise SystemExit(slug)
KEEP=(" HARD RULES: This is a surgical edit. Output the SAME image: same canvas, same two drawings in the same positions, same sizes, same line weight and same drawing style. "
      "Change ONLY what is described. Do not redraw, simplify, move, resize or restyle anything else. Pure black lines on flat white background, no gray, no shading, no text, no extra decorations.")
jobs=[]
def add(jid,th,slug,v,extra,prompt,side):
    jobs.append({"id":jid,"theme":th,"slug":slug,"variant":v,"side":side,"refs":[P(th,slug,v)]+[P(*e) for e in extra],"aspect":"3:2","prompt":prompt+KEEP})
add("L2_poodle_heart","line","poodle","heart",[("line","poodle","classic")],
 "Image 1 is the design to edit. Image 2 is the same poodle design (classic version). In image 1 the full-body sitting dog on the right is missing its tail. Add the same curly tail as the dog in image 2 has, same side, size and curl style. The heart, the front head and everything else must stay identical.","back")
add("L2_gsd_classic","line","german_shepherd","classic",[("line","german_shepherd","heart")],
 "Image 1 is the design to edit. Image 2 is the same German shepherd design (heart version). In image 1 the full-body sitting dog on the right is missing its tail. Add the same bushy tail as the dog in image 2 (same side, size, shape and line style, lying on the ground at the lower left behind the rump). Everything else stays identical, including the front head.","back")
add("G2_dachs_cool","geo","dachshund","cool",[("geo","dachshund","classic")],
 "Image 1 is the dachshund cool design to fix: its full-body dog on the right is turned sideways in a different pose. Image 2 is the classic dachshund: its pose (sitting, body and head facing the viewer, ears hanging, small tail) is the truth. Redraw ONLY the full-body dog on the right of image 1 so it is exactly the dog of image 2 (same pose, geometric facets, size, position, small tail) with only geometric sunglasses added on its face in the same style as the sunglasses in image 1. The front head on the left stays identical.","back")
add("G2_dachs_heart","geo","dachshund","heart",[("geo","dachshund","classic")],
 "Image 1 is the dachshund heart design to fix: its full-body dog on the right is turned sideways in a different pose. Image 2 is the classic dachshund: its pose (sitting, body and head facing the viewer, ears hanging, small tail) is the truth. Redraw ONLY the full-body dog on the right of image 1 so it is exactly the dog of image 2 (same pose, geometric facets, size, position, small tail) and add only a thin collar with a small heart tag on the chest in the same style as the collar and tag of image 1. The heart and front head on the left stay identical.","back")
add("G2_dane_cool","geo","great_dane","cool",[("geo","great_dane","classic")],
 "Image 1 is the Great Dane cool design to fix: the head of its full-body dog is turned sideways and the dog differs from the classic. Image 2 is the classic Great Dane: its pose (sitting, head facing the viewer, no tail) is the truth. Redraw ONLY the full-body dog on the right of image 1 so it is exactly the dog of image 2 (same pose, facets, size, position) with only geometric sunglasses added in the same style as image 1. The front head on the left stays identical.","back")
add("G2_dane_heart","geo","great_dane","heart",[("geo","great_dane","classic")],
 "Image 1 is the Great Dane heart design to fix: the head of its full-body dog is turned sideways, and it has a tail the classic does not have. Image 2 is the classic Great Dane: its pose (sitting, head facing the viewer, no tail) is the truth. Redraw ONLY the full-body dog on the right of image 1 so it is exactly the dog of image 2 (same pose, facets, size, position, no tail) and add only a thin collar with a small heart tag on the chest in the same style as image 1. The heart and front head on the left stay identical.","back")
json.dump({"base":json.load(open("scripts/fix_jobs.json"))["base"],"styles":jobs},open("scripts/fix2_jobs.json","w"),indent=1)
cands=[]
for j in jobs:
    for k in "abcd":
        c=dict(j);c["id"]=f"{j['id']}__{k}";cands.append(c)
json.dump({"base":json.load(open("scripts/fix_jobs.json"))["base"],"styles":cands},open("scripts/fix2_cands.json","w"),indent=1)
print(len(cands))
