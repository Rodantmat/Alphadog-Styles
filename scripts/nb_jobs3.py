import json
jobs=[]
for sty,nm in (("out/sets/geo_p2/doberman_pinscher__classic.jpg","dob"),("out/sets/geo_p3/american_pit_bull_terrier__classic.jpg","pit")):
  for idr,tag in (("out/nb2/m1/M_line_miniature_pinscher_classic__a.png","la"),):
    pr=("Image 1 is the identity reference: a continuous-line drawing of a Miniature Pinscher (front head left, sitting full-body dog right). Image 2 is an APPROVED example of the target ART STYLE: bold geometric polygon lines (angular facets, thick uniform outer outline, thinner inner facet lines). Redraw the exact same two Miniature Pinscher dogs of image 1 in the geometric polygon style of image 2, with the same pose and layout. "
    "IMPORTANT anatomy of a Miniature Pinscher (it is a toy dog, NOT a chihuahua and NOT a doberman): the ears are SMALL-to-MEDIUM upright triangles that stay close to the head: each ear only about 1/3 the height of the head and clearly narrower than the head, NEVER huge or wide; rounded skull; a short wedge-shaped muzzle; eyes of moderate size (not huge); a short strong arched neck; compact square body; slim straight legs; a short tail carried up. Both dogs sitting. "
    "Eyes: one simple round ring outline with a solid black round pupil, both identical. Pure black lines on flat pure white, no gray, no shading, no fills except the nose, no text, nothing cut off, the two drawings must not touch each other or the edges. No accessories.")
    jobs.append({"id":f"M3_geo_miniature_pinscher_{nm}","refs":[idr,sty],"aspect":"3:2","prompt":pr})
json.dump(jobs,open("scripts/nb_jobs3.json","w"),indent=1)
