from mkvid import *
B=(760,700)
S=[dict(bg='mtn_dawn',item=('hoodie','dachshund','5SA',B),start=0,end=72,texts=[(0,36,"A DAY ON THE TRAIL",54),(36,72,"SUNRISE",84)]),
   dict(bg='mtn_noon',item=('cap_dad','golden_retriever','2DP',(760,520)),start=72,end=120,texts=[(72,120,"HIGH NOON",84)]),
   dict(bg='mtn_dusk',item=('tee','german_shepherd','5LB',(700,660)),start=120,end=168,texts=[(120,168,"GOLDEN HOUR",78)]),
   dict(bg='camp_night',item=('tank','border_collie','2HE',(560,560)),cy=870,start=168,end=240,texts=[(168,204,"CAMPFIRE NIGHTS",70),(204,240,["MADE FOR TRAIL-DOG","PEOPLE"],56)],cta=True),
]
S[3]['cta']=True;S[3]['cta_f']=204
S.append(None);S.pop()
import mkvid
mkvid.render('/tmp/kl/vN1_silent.mp4',S,"alphadogstyles.com  ·  link in bio")
