import json
NM={"lhasa_apso":"Lhasa Apso","miniature_pinscher":"Miniature Pinscher","vira_lata":"Vira-lata"}
SG={"line":"classic aviator sunglasses drawn in the same thin continuous-line style: a thin frame with a nose bridge and thin temple arms, two teardrop-shaped lenses",
    "geo":"angular geometric aviator sunglasses made of straight polygon edges: a bold frame with a bridge and temple arms, two angular faceted lenses"}
COMMON=(" Everything else must stay IDENTICAL to image 1, line for line: same dog, same pose, same layout and positions, same hair/coat amount and line density, same eyebrows, nostrils, mouth, chest lines, tail, paws, same line weight. Pure black on flat pure white, no gray, no shading, no text, nothing cut off or touching the canvas edge.")
jobs=[]
for th in("line","geo"):
  for b,n in NM.items():
    base=f"out/nb2/master/{th}_{b}_classic.png"
    cool=(f"Image 1 is a finished {th=='line' and 'continuous-line' or 'geometric'} design of a {n}: front head emblem (left) and full-body sitting dog (right). Make an exact copy and ONLY add sunglasses to BOTH dogs (the front head and the full-body dog): {SG[th]}. The lenses must be COMPLETELY SOLID PURE BLACK fills (like black ink), fully opaque: nothing visible through them, no eyes, no highlights, no white inside the lenses. The sunglasses sit over the eyes exactly where the eyes were, the same style and size relation on both dogs. Erase the eyes (they are hidden behind the lenses)."+COMMON)
    heart=(f"Image 1 is a finished {th=='line' and 'continuous-line' or 'geometric'} design of a {n}: front head emblem (left) and full-body sitting dog (right). Make an exact copy and ONLY add the heart theme: (1) draw a large heart-shaped outline frame {'in one thin flowing continuous line that ends in a small loop at the bottom point and a tiny heart at the top' if th=='line' else 'made of angular geometric facets (like a faceted gem heart) with a small faceted diamond-heart on top'} surrounding the FRONT head so the head sits inside the heart (the heart must be clearly larger than the head and fully visible, not cut off); (2) give the FULL-BODY dog a thin collar line around its neck with one small heart-shaped tag. Keep both dogs' eyes exactly as in image 1."+COMMON)
    jobs.append({"id":f"V_{th}_{b}_cool","refs":[base],"aspect":"3:2","prompt":cool})
    jobs.append({"id":f"V_{th}_{b}_heart","refs":[base],"aspect":"3:2","prompt":heart})
json.dump(jobs,open("scripts/nb_jobs4.json","w"),indent=1);print(len(jobs))
