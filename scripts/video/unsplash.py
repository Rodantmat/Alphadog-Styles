import json,os,re,urllib.request,urllib.parse,sys,time
UA={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36','Accept':'application/json'}
os.makedirs('out/unsplash',exist_ok=True);out={}
breeds=['dog','pug','french bulldog','bulldog','golden retriever','labrador','husky','corgi','dachshund','poodle','chihuahua','beagle','german shepherd','boxer dog','shiba inu','pomeranian','yorkshire terrier','australian shepherd','border collie','rottweiler','great dane','doberman','shih tzu','maltese','boston terrier','pit bull','cavalier','schnauzer','bernese','havanese','bichon','puppy']
for b in breeds:
    for q in (b+' sunglasses',b+' wearing glasses'):
        try:
            u='https://unsplash.com/napi/search/photos?'+urllib.parse.urlencode({'query':q,'per_page':20})
            r=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read())
        except Exception as e: print(q,'ERR',repr(e)[:100]);continue
        for p in r.get('results',[]):
            txt=' '.join(str(x) for x in [p.get('alt_description'),p.get('description')]+[t.get('title') for t in p.get('tags',[])]).lower()
            if re.search(r'sunglass|glasses|shades|goggles',txt) and re.search(r'dog|puppy|pug|bulldog|retriever|husky|corgi|poodle|terrier|dachshund|chihuahua',txt):
                out[p['id']]=dict(q=b,alt=p.get('alt_description'),desc=p.get('description'),w=p['width'],h=p['height'],url=p['urls']['regular'],user=p['user']['name'],link=p['links']['html'],tags=[t.get('title') for t in p.get('tags',[])][:8])
        time.sleep(0.4)
json.dump(out,open('out/unsplash/manifest.json','w'),indent=0);print(len(out),'matches')
for k,v in list(out.items())[:150]:
    try: open(f'out/unsplash/{k}.jpg','wb').write(urllib.request.urlopen(urllib.request.Request(v['url'],headers=UA),timeout=60).read())
    except Exception as e: print(k,'dlERR',repr(e)[:80])
