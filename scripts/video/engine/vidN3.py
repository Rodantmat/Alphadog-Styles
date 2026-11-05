from mkvid import *
import mkvid
S=[dict(bg='lake_dusk',item=('tee','labrador_retriever','5LB',(640,540)),start=0,end=84,cy=985,texts=[(0,30,"DID YOU KNOW?",64),(30,84,"LABRADOR",80)],lines=["Labs have webbed paws,","so they swim like pros."],ly=548),
   dict(bg='forest_mist',item=('tank','dachshund','6HE',(600,560)),start=84,end=150,cy=985,texts=[(84,150,"DACHSHUND",80)],lines=["In German it means","\"badger dog\"."],ly=548),
   dict(bg='meadow',item=('cap_dad','poodle','2DP',(680,480)),start=150,end=204,cy=985,texts=[(150,204,"POODLE",80)],lines=["The name comes from \"Pudel\",","German for \"to splash\"."],ly=548),
   dict(bg='meadow',item=('cap_dad','poodle','2DP',(680,480)),start=204,end=240,t0=150,cy=960,texts=[(204,240,["WHICH BREED","IS YOURS?"],64)],cta=True,cta_f=204)]
mkvid.render('/tmp/kl/vN3_silent.mp4',S,"Comment your breed  ·  alphadogstyles.com")
