import sys,os,glob,shutil
sys.path.insert(0,'/tmp')
import cut5
from PIL import Image
FLAT={"Tee_B":[92547,92720,102044,102045,102046,102047,102048],"Tee_A":[97992,97993,100615],"Hoodie":[98424,98425,98426,98432],"Polo":[101910,102236],"Racerback_Tank":[48,49,111806,111807],"Tank_Top":[101889,101892],"Dad_Hat":[135042,135043,135044,135045]}
TOL={"Racerback_Tank":55,"Tank_Top":40,"Dad_Hat":55}
REDO_ML={("Mesh_Trucker_Cap",110021)}
out="out/cutouts_final"
for d in sorted(glob.glob("out/cutouts_v6/*/")):
    p=os.path.basename(d[:-1]); os.makedirs(f"{out}/{p}",exist_ok=True)
    for f in sorted(glob.glob(d+"*.png")):
        i=int(os.path.basename(f)[:-4]); dst=f"{out}/{p}/{i}.png"
        src=f"out/mockexact/{p}/{i}.jpg"
        if i in FLAT.get(p,[]):
            r=cut5.cutout_flat(src,TOL.get(p,21))
        elif (p,i) in REDO_ML:
            r=cut5.cutout(src,caps=True)
        else:
            shutil.copy(f,dst); continue
        bb=r.split()[3].point(lambda v:255 if v>5 else 0).getbbox(); r.crop(bb).save(dst); print(p,i,flush=True)
open(f"{out}/DONE","w").write("ok")
