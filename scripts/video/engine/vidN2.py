from mkvid import *
B=(760,700)
S=[dict(bg='gift_red',item=('hoodie','pembroke_welsh_corgi','2SA',B),start=0,end=72,texts=[(0,36,"WHO'S YOUR DOG PERSON?",50),(36,72,"FOR MOM",84)]),
   dict(bg='gift_green',item=('tee','german_shepherd','5CR',(700,660)),start=72,end=120,texts=[(72,120,"FOR DAD",84)]),
   dict(bg='gift_blue',item=('polo','pomeranian','2HE',(700,660)),start=120,end=168,texts=[(120,168,"FOR YOUR BEST FRIEND",56)]),
   dict(bg='gift_plum',item=('hoodie','dachshund','5PK',(660,560)),cy=870,start=168,end=240,texts=[(168,204,"FOR GRANDMA",76),(204,240,["GIVE THEIR BREED"],60)],cta=True,cta_f=204)]
mkvid.render('/tmp/kl/vN2_silent.mp4',S,"Gift ideas  ·  alphadogstyles.com") if False else None
import mkvid;mkvid.render('/tmp/kl/vN2_silent.mp4',S,"Gift ideas  ·  alphadogstyles.com")
