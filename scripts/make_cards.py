import os,sys
from PIL import Image, ImageDraw, ImageFont
os.chdir('/home/claude/alphadog-styles')
br="french_bulldog labrador_retriever golden_retriever german_shepherd dachshund poodle beagle rottweiler german_shorthaired_pointer bulldog cane_corso cavalier_king_charles_spaniel yorkshire_terrier australian_shepherd doberman_pinscher pembroke_welsh_corgi miniature_schnauzer boxer pomeranian bernese_mountain_dog shih_tzu great_dane boston_terrier chihuahua havanese".split()
out=sys.argv[1]; only=set(int(x) for x in sys.argv[2:]) if len(sys.argv)>2 else None
def P(th,s,v):
    for p in('p1','p2'):
        f=f'out/sets/{th}_{p}/{s}__{v}.jpg'
        if os.path.exists(f): return f
os.makedirs(out,exist_ok=True)
W,H=800,537; F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',26)
for i,s in enumerate(br,1):
    if only and i not in only: continue
    c=Image.new('RGB',(2400,2*H+60),'white'); d=ImageDraw.Draw(c)
    d.text((10,14),f"{i:02d}  {s.replace('_',' ').title()}   |   top row: continuous line   bottom row: geometric   |   classic - cool - heart",fill=(180,0,0),font=F)
    for r,th in enumerate(('line','geo')):
        for k,v in enumerate(('classic','cool','heart')):
            c.paste(Image.open(P(th,s,v)).convert('RGB').resize((W,H),Image.LANCZOS),(k*W,60+r*H))
    d.line((0,60+H,2400,60+H),fill=(200,200,200),width=2)
    c.save(f'{out}/{i:02d}_{s}_6styles.jpg',quality=92)
