import json,os,re,urllib.request,urllib.parse,sys
UA={'User-Agent':'AlphaDogStyles-research/1.0 (contact: rodolfoaamattos@gmail.com)'}
def api(**p):
    p.update(format='json');u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(p)
    return json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read())
os.makedirs('out/photos',exist_ok=True);out={}
terms=['dog sunglasses','dog wearing sunglasses','dog with sunglasses','puppy sunglasses','pug sunglasses','bulldog sunglasses','corgi sunglasses','husky sunglasses','dachshund sunglasses','labrador sunglasses','golden retriever sunglasses','poodle sunglasses','chihuahua sunglasses','dog goggles','dog shades','dog cool glasses']
for t in terms:
    try: r=api(action='query',generator='search',gsrsearch=t+' filetype:bitmap',gsrnamespace=6,gsrlimit=40,prop='imageinfo',iiprop='url|extmetadata|size|mime',iiurlwidth=1400)
    except Exception as e: print(t,'ERR',e);continue
    for pg in r.get('query',{}).get('pages',{}).values():
        ii=pg['imageinfo'][0];md=ii.get('extmetadata',{})
        lic=md.get('LicenseShortName',{}).get('value','?');art=re.sub('<[^>]+>','',md.get('Artist',{}).get('value',''))[:60]
        out[pg['pageid']]=dict(title=pg['title'],thumb=ii.get('thumburl'),w=ii['width'],h=ii['height'],lic=lic,artist=art,desc=re.sub('<[^>]+>','',md.get('ImageDescription',{}).get('value',''))[:120])
json.dump(out,open('out/photos/manifest.json','w'),indent=0);print(len(out),'candidates')
ok=[k for k,v in out.items() if re.search(r'CC0|Public domain|PD|CC BY|Unsplash|Pexels|Pixabay',v['lic'],re.I) and v['w']>=900 and v['thumb']]
print(len(ok),'licensed ok')
for k in ok[:80]:
    v=out[k]
    try: open(f'out/photos/{k}.jpg','wb').write(urllib.request.urlopen(urllib.request.Request(v['thumb'],headers=UA),timeout=60).read())
    except Exception as e: print(k,'dlERR',e)
