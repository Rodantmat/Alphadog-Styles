import json,os
B="out/sets"
def P(th,s,v):
    for p in("p1","p2"):
        f=f"{B}/{th}_{p}/{s}__{v}.jpg"
        if os.path.exists(f): return f
    raise SystemExit((th,s,v))
KEEP=(" HARD RULES: This is a surgical edit. Output the SAME image: same canvas, same two drawings in the same positions, same sizes, same line weight and same drawing style. "
      "Change ONLY what is described. Do not redraw, simplify, move, resize or restyle anything else (eyes, nose, ears, heart, collar and every other line stay exactly as they are). Pure black lines on flat white background, no gray, no shading, no text, no extra decorations.")
jobs=[]
def add(jid,th,slug,v,refs,prompt,side,mode):
    jobs.append({"id":jid,"theme":th,"slug":slug,"variant":v,"side":side,"mode":mode,"refs":[P(th,slug,v)]+[P(*r) for r in refs],"aspect":"3:2","prompt":prompt+KEEP})
add("F_golden_classic","line","golden_retriever","classic",[("line","labrador_retriever","classic")],
 "Image 1 is the design to edit. Image 2 is a reference that shows the exact EYE STYLE wanted. Redraw ONLY the four eyes of image 1 (two eyes of the front head on the left, two eyes of the full-body dog on the right) in the eye style of image 2: keep each eye's eyelid outline, make the iris mostly WHITE with ONE solid black pupil that does not touch the ring and leaves a visible white crescent around it, with a small white highlight dot at the pupil's upper right. The pupils sit slightly off-centre, all four looking the same direction (slightly right and a little up), so both eyes of each dog are perfectly aligned. Same size and style in all four eyes.","both","both")
add("F_gsd_cool","line","german_shepherd","cool",[("line","german_shepherd","classic")],
 "Image 1 is the German shepherd cool design to fix: its full-body sitting dog on the right has a body that is too wide and fat compared to the classic. Image 2 is the classic German shepherd: its slim body, pose, proportions, size and position are the truth. Redraw ONLY the full-body dog on the right of image 1 so it is exactly the dog of image 2 (same slim body and chest, same legs, same tail, same line style, size and position) with only the aviator sunglasses of image 1 kept on its face. The front head on the left stays identical.","back","full")
add("F_dachshund_heart","line","dachshund","heart",[("line","dachshund","classic")],
 "Image 1 is the dachshund heart design to fix: its full-body sitting dog on the right is missing the chest lines. Image 2 is the classic dachshund: the flowing chest and neck contour lines on its chest and shoulders are the truth. In image 1 add exactly the same chest and shoulder lines as the dog in image 2 (same shapes, same position, same line weight), keeping the collar with the small heart tag. The heart and front head stay identical.","back","full")
add("F_poodle_heart","line","poodle","heart",[("line","poodle","classic")],
 "Image 1 is the poodle heart design to fix: its full-body sitting dog on the right is missing the curly chest and body curl lines. Image 2 is the classic poodle: the curly lines on its chest, front and body are the truth. In image 1 add exactly the same curly chest and body lines as the dog in image 2 (same shapes, same position, same line weight), keeping the collar with the small heart tag. The heart and front head stay identical.","back","full")
add("F_beagle_heart","line","beagle","heart",[("line","beagle","classic")],
 "Image 1 is the beagle heart design to fix: its full-body sitting dog on the right is missing the chest and body contour lines. Image 2 is the classic beagle: the flowing contour lines across its chest and torso are the truth. In image 1 add exactly the same chest and body contour lines as the dog in image 2 (same shapes, same position, same line weight), keeping the collar with the small heart tag and the tail. The heart and front head stay identical.","back","full")
add("F_cav_heart","line","cavalier_king_charles_spaniel","heart",[("line","cavalier_king_charles_spaniel","classic")],
 "Image 1 is the cavalier heart design to fix: on the front head inside the heart, the dog's left ear (on the viewer's left) is cut off and ends abruptly, not continuous like the other ears. Image 2 is the classic cavalier: its long, flowing, wavy ears are the truth. Redraw ONLY that left ear of the front head so it is a complete, continuous, long wavy ear like the ears of image 2 and like the right ear of the same head, flowing down naturally, drawn in front of the heart line. The back dog, the heart and everything else stay identical.","front","full")
for v in("classic","cool","heart"):
    add(f"F_chi_{v}","line","chihuahua",v,[("line","dachshund","classic")],
     "Image 1 is the design to edit. In image 1 the full-body sitting chihuahua on the right is missing its tail. Add a small, thin, slightly curved tail coming out behind the rump at the lower left, resting on the ground, drawn as a single flowing line with the same line weight as the rest of the dog. Image 2 is a different dog shown ONLY to show the style of a small thin tail line; do not copy its body. The front head, heart, collar and the rest stay identical.","back","tail")
add("F_dach_geo_heart","geo","dachshund","heart",[("geo","dachshund","classic")],
 "Image 1 is the geometric dachshund heart design to fix: the ears of the full-body dog on the right are cut off at the top. Image 2 is the classic geometric dachshund: its two complete hanging ears are the truth. Redraw ONLY the ears of the full-body dog on the right of image 1 so both are complete angular geometric ears exactly like the ears in image 2 (same shape, size and facets, attached to the head the same way). Keep the collar and heart tag, the heart and front head, and everything else identical.","back","full")
c=[]
for j in jobs:
    for k in "abcd": x=dict(j); x["id"]=f"{j['id']}__{k}"; c.append(x)
json.dump({"base":"","styles":c},open("scripts/fix3_cands.json","w"),indent=1)
json.dump({j["id"]:{"side":j["side"],"mode":j["mode"],"orig":j["refs"][0]} for j in jobs},open("scripts/fix3_meta.json","w"),indent=1)
print(len(jobs),len(c))
