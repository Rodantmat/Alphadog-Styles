import json,os,re,urllib.request,urllib.parse,time
UA={'User-Agent':'AlphaDogStyles-research/1.0','Accept':'application/json'}
os.makedirs('out/unsplash',exist_ok=True);out={}
breeds=['dog','pug','french bulldog','bulldog','golden retriever','labrador','husky','corgi','dachshund','poodle','chihuahua','beagle','german shepherd','boxer','shiba inu','pomeranian','yorkshire terrier','australian shepherd','border collie','rottweiler','great dane','doberman','shih tzu','maltese','boston terrier','pit bull','cavalier king charles','schnauzer','bernese mountain dog','havanese','bichon frise','puppy']
for b in breeds:
    for q in (b+' sunglasses',):
        for lic in ('cc0,pdm','by'):
            try:
                u='https://api.openverse.org/v1/images/?'+urllib.parse.urlencode({'q':q,'license':lic,'page_size':20,'extension':'jpg'})
                r=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read())
            except Exception as e: print(q,lic,'ERR',repr(e)[:100]);continue
            for p in r.get('results',[]):
                txt=(str(p.get('title'))+' '+' '.join(t['name'] for t in p.get('tags',[]) if t.get('name'))).lower()
                if re.search(r'sunglass|glasses|shades|goggle',txt) and re.search(r'dog|puppy|pug|bulldog|retriever|husky|corgi|poodle|terrier|dachshund|chihuahua|beagle',txt) and (p.get('width') or 0)>=900:
                    out[p['id']]=dict(q=b,title=p['title'],lic=p['license'],ver=p.get('license_version'),src=p.get('source'),creator=p.get('creator'),url=p['url'],page=p.get('foreign_landing_url'),w=p['width'],h=p['height'])
            time.sleep(0.6)
json.dump(out,open('out/unsplash/manifest.json','w'),indent=0);print(len(out),'matches')
for k,v in list(out.items())[:120]:
    try: open(f'out/unsplash/{k}.jpg','wb').write(urllib.request.urlopen(urllib.request.Request(v['url'],headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read())
    except Exception as e: print(k,'dlERR',repr(e)[:80])
