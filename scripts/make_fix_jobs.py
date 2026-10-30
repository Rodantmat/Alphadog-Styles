import json,os,sys
def P(th,slug,v,base="out/sets_orig"):
    for p in ("p1","p2"):
        f=f"{base}/{th}_{p}/{slug}__{v}.jpg"
        if os.path.exists(f):return f
    raise SystemExit(f"missing {th} {slug} {v}")
KEEP=(" HARD RULES: This is a surgical edit. Output the SAME image: same canvas, same two drawings in the same positions, same sizes, same line weight and same drawing style. "
      "Change ONLY what is described. Do not redraw, simplify, move, resize or restyle anything else. Pure black lines on flat white background, no gray, no shading, no text, no extra decorations.")
jobs=[]
def add(jid,theme,slug,variant,extra,prompt,side):
    refs=[P(theme,slug,variant)]+extra
    jobs.append({"id":jid,"theme":theme,"slug":slug,"variant":variant,"side":side,"refs":refs,"aspect":"3:2",
                 "prompt":prompt+KEEP})
R=lambda t,s,v:P(t,s,v)
# ---------- LINE ----------
add("L_poodle_cool","line","poodle","cool",[R("line","poodle","classic")],
 "Image 1 is the design to edit. Image 2 is the same poodle design (classic version) for reference. In image 1 the full-body sitting dog on the right is missing its tail. Add the same curly tail as the dog in image 2 has, on the same side and with the same size and curl style. The front head emblem on the left must stay identical.","back")
add("L_dachshund_heart","line","dachshund","heart",[R("line","dachshund","classic")],
 "Image 1 is the design to edit. Image 2 is the same dachshund design (classic version) for reference. In image 1 the full-body sitting dog on the right is missing its tail. Add the same long thin tail as in image 2, same side, same length and curve, drawn in the same single flowing line. The heart, the front head and everything else must stay identical.","back")
add("L_corgi_cool","line","pembroke_welsh_corgi","cool",[R("line","pembroke_welsh_corgi","classic"),R("line","dachshund","cool")],
 "Image 1 is the corgi design to fix. Image 2 is the CORRECT corgi (classic version, no sunglasses): its face, body proportions, fur lines, ears and pose are the truth. Image 3 only shows how the sunglasses should look. Redraw image 1 so that BOTH the front head and the full-body dog are exactly the dog of image 2 (same face shape and muzzle, same body proportions, same fluffy chest and fur lines, same size and position of each drawing) and only ADD black aviator sunglasses like those in image 3 on both heads. The corgi must look like a real corgi (fox-like face, long muzzle, big upright ears), not like a pig.","both")
add("L_boxer_classic","line","boxer","classic",[R("line","boxer","heart")],
 "Image 1 is the design to edit. Image 2 is the same boxer design (heart version) for reference. Remove ONLY the tail from the full-body sitting dog on the right (the line curling up behind the rump at lower left); the rear should end cleanly like the dog in image 2 which has no tail. Do not touch anything else, the front head emblem stays identical.","back")
add("L_boxer_cool","line","boxer","cool",[R("line","boxer","classic"),R("line","boxer","heart")],
 "Image 1 is the boxer cool design to fix: its front head emblem is too small and the dogs look too small compared to the other versions. Image 2 is the boxer classic version: use its proportions, head size, drawing size and position as the truth for BOTH the front head emblem and the full-body dog. Image 3 is the boxer heart version for reference (no tail). Redraw image 1 so both drawings have the same size, proportions and drawing detail as image 2, with only black aviator sunglasses added on both heads (keep the sunglasses style of image 1), and NO tail on the full-body dog (the rear ends cleanly like image 3).","both")
add("L_pom_cool","line","pomeranian","cool",[R("line","pomeranian","classic"),R("line","pomeranian","cool")],
 "Image 1 is the Pomeranian cool design to fix: its line quality and fluff do not match the classic version. Image 2 is the classic Pomeranian (the truth: same fluffy face and body outline, same curly tail, same fur line style and weight, same size and position of each drawing). Image 3 is the current cool version, used only to see the sunglasses style. Redraw so that BOTH the front head and the full-body dog are exactly the dog of image 2 and the ONLY difference is black aviator sunglasses on both heads, like image 3.","both")
add("L_pom_heart","line","pomeranian","heart",[R("line","pomeranian","classic")],
 "Image 1 is the Pomeranian heart design to fix. Image 2 is the classic Pomeranian, the truth for the body. The full-body sitting dog on the RIGHT of image 1 is completely different from the classic one. Redraw ONLY that right-hand dog so it is exactly the dog of image 2 (same pose, fluffy fur lines, curly tail, proportions, line style, size and position) and ADD only a thin collar with a small heart tag hanging on the chest (keep the collar and tag style of the current dog in image 1). The left side (heart and head emblem) must stay identical.","back")
add("L_shih_heart","line","shih_tzu","heart",[R("line","shih_tzu","classic")],
 "Image 1 is the design to edit. Image 2 is the same shih tzu design (classic version) for reference. In image 1 the full-body sitting dog on the right has no tail. Add the same curled tail as in image 2, same side, size and curl, drawn in the same line style. Everything else stays identical.","back")
add("L_havanese_heart","line","havanese","heart",[R("line","havanese","classic"),R("line","havanese","cool")],
 "Image 1 is the Havanese heart design to fix. Images 2 (classic) and 3 (cool) are the same Havanese with a hairy, long silky fur look drawn with many flowing hair strands. In image 1 the full-body sitting dog on the right shows barely any hair lines. Redraw ONLY that dog so it keeps exactly the same pose, outline, collar and heart tag, size and position but has the same fur strand line density and style as the dog in images 2 and 3 (flowing wavy hair strands over body, chest and legs). Left side (heart and head emblem) stays identical.","back")
# ---------- GEO ----------
add("G_dachs_cool","geo","dachshund","cool",[R("geo","dachshund","classic")],
 "Image 1 is the design to edit. Image 2 is the same dachshund design (classic) for reference. In image 1 the full-body dog on the right has no tail. Add the same small angular geometric tail as in image 2 at the lower right behind the rump, same shape, size and line weight. Everything else stays identical, including the front head.","back")
add("G_lab_heart","geo","labrador_retriever","heart",[R("geo","labrador_retriever","classic")],
 "Image 1 is the design to edit. Image 2 is the same labrador design (classic). The tail of the full-body dog on the right in image 1 does not match: redraw ONLY the tail so it is the same short angular geometric tail as in image 2 (same shape, size, position and line weight). Everything else stays identical.","back")
add("G_poodle_classic","geo","poodle","classic",[R("geo","poodle","heart")],
 "Image 1 is the design to edit. Image 2 is the same poodle design (heart version). In image 1 the full-body dog on the right has no tail. Add the same geometric pom-pom tail as in image 2 (same angular tail line and polygon pom-pom, same size and position, behind the rump on the right). Everything else stays identical.","back")
add("G_gsp_classic","geo","german_shorthaired_pointer","classic",[R("geo","german_shorthaired_pointer","heart")],
 "Image 1 is the design to edit. Image 2 is the same pointer design (heart version). Image 2 has a SMALL short angular tail just at the base of the rump on the ground line at the lower right. Add exactly that same small tail (same shape, size, position, line weight) to the full-body dog in image 1, which currently has none. Everything else stays identical.","back")
add("G_gsp_cool","geo","german_shorthaired_pointer","cool",[R("geo","german_shorthaired_pointer","heart")],
 "Image 1 is the design to edit. Image 2 is the same pointer design (heart version). Image 2 has a SMALL short angular tail just at the base of the rump on the ground line at the lower right. The full-body dog in image 1 has a different, tall thin curved tail. Replace ONLY that tail with exactly the small tail of image 2 (same shape, size, position, line weight). Everything else stays identical.","back")
for v in ("classic","cool","heart"):
    add(f"G_yorkie_{v}","geo","yorkshire_terrier",v,[],
     "The face expression of the Yorkshire terrier in BOTH drawings (front head and full-body dog) looks angry. Make it look friendly and gentle: soften and relax the eyebrow/brow lines (no downward angled angry brows), keep the eyes open and gentle (if eyes are visible keep them as dark shapes with a calm, round look), and let the mouth line be calm and slightly upturned. Change only these expression lines; the head shape, hair lines, ears, topknot, sunglasses (if any), heart (if any), body and tail stay identical.","both")
add("G_corgi_classic","geo","pembroke_welsh_corgi","classic",[R("geo","pembroke_welsh_corgi","heart")],
 "Image 1 is the design to edit. Image 2 is the same corgi design (heart version). The nose of the dogs in image 1 is a plain solid black shape; the nose in image 2 has geometric detail (small facet lines and a white highlight). Add the same kind of nose detail to the noses of BOTH the front head and the full-body dog in image 1. Change only the noses; everything else stays identical.","both")
add("G_corgi_cool","geo","pembroke_welsh_corgi","cool",[R("geo","pembroke_welsh_corgi","classic"),R("geo","pembroke_welsh_corgi","cool")],
 "Image 1 is the corgi cool design to fix: the dogs look fatter and rounder than the other versions. Image 2 is the corgi classic version: use its slimmer face shape, head width, body width and proportions as the truth for both the front head and the full-body dog. Redraw image 1 so both drawings have the same slimmer proportions, size and construction as image 2, keeping the geometric sunglasses of image 1 as they are, and keeping the same line weight and drawing size/position.","both")
add("G_shih_heart","geo","shih_tzu","heart",[R("geo","shih_tzu","classic")],
 "Image 1 is the design to edit. Image 2 is the same shih tzu design (classic). The tail of the full-body dog on the right in image 1 does not match. Redraw ONLY the tail so it is the same curled geometric tail as in image 2 (same shape, size, side and line weight). Everything else stays identical.","back")
add("G_shih_cool","geo","shih_tzu","cool",[R("geo","shih_tzu","classic")],
 "Image 1 is the design to edit. Image 2 is the same shih tzu design (classic). The full-body dog on the right in image 1 has no tail. Add the same curled geometric tail as in image 2 (same shape, size, side, position and line weight). Everything else stays identical.","back")
add("G_chi_classic","geo","chihuahua","classic",[R("geo","chihuahua","heart")],
 "Image 1 is the design to edit. Image 2 is the same chihuahua design (heart version). The full-body dog on the right in image 1 has no tail. Add the same thin curved tail as in image 2 (same shape, size, side, position and line weight). Everything else stays identical.","back")
add("G_chi_heart","geo","chihuahua","heart",[R("geo","chihuahua","classic")],
 "Image 1 is the design to edit. Image 2 is the same chihuahua design (classic). In image 1 the front head inside the heart looks too full/busy. Clean up ONLY the face of the front head: reduce the number of face lines so the face has the same line density and look as the face of the classic version in image 2 (same eyes, nose, muzzle). Keep the heart, the head outline and ears, and the whole right-hand dog identical.","front")
add("G_boston_cool","geo","boston_terrier","cool",[R("geo","boston_terrier","classic")],
 "Image 1 is the design to edit. Image 2 is the same Boston terrier (classic). In image 1 the lines on the face of the front head are overcrowded (hatching, dots, extra lines around the muzzle and forehead). Clean up ONLY the front head face so its line density and construction match the face in image 2, while keeping the sunglasses of image 1 exactly. The right-hand full-body dog stays identical.","front")
json.dump({"base":"","styles":jobs},open("scripts/fix_jobs.json","w"),indent=1)
print(len(jobs))
