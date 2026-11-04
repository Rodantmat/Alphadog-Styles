"""READ-ONLY: list live Etsy + eBay prices (titles, min/max price, shipping). Changes nothing."""
import os,sys,re,json,base64,urllib.request,urllib.parse,urllib.error
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
def kind(t):
    t=t.lower()
    k="hoodie" if re.search(r"hood|sweat",t) else "tee" if re.search(r"tee|t-shirt|shirt",t) else "other"
    return k
rows=[]
try:
    import etsy_api as E
    for st in ("active",):
        for l in E.listings(st):
            p=l.get("price") or {}; pr=p.get("amount",0)/(p.get("divisor") or 100)
            rows.append(("etsy",kind(l.get("title","")),pr,l.get("title","")[:60],l.get("shipping_profile_id")))
except Exception as e: print("etsy err",str(e)[:200])
try:
    ID,SEC,RT=[os.environ[k] for k in("EBAY_CLIENT_ID","EBAY_CLIENT_SECRET","EBAY_REFRESH_TOKEN")]
    d=urllib.parse.urlencode({"grant_type":"refresh_token","refresh_token":RT,"scope":"https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.inventory"}).encode()
    tok=json.load(urllib.request.urlopen(urllib.request.Request("https://api.ebay.com/identity/v1/oauth2/token",d,{"Authorization":"Basic "+base64.b64encode(f"{ID}:{SEC}".encode()).decode(),"Content-Type":"application/x-www-form-urlencoded"}),timeout=60))["access_token"]
    pg=1
    while True:
        x=("<?xml version='1.0' encoding='utf-8'?><GetMyeBaySellingRequest xmlns='urn:ebay:apis:eBLBaseComponents'><ActiveList><Include>true</Include><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination></ActiveList></GetMyeBaySellingRequest>"%pg).encode()
        r=urllib.request.Request("https://api.ebay.com/ws/api.dll",x,{"X-EBAY-API-IAF-TOKEN":tok,"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"1193","X-EBAY-API-CALL-NAME":"GetMyeBaySelling","Content-Type":"text/xml"})
        t=urllib.request.urlopen(r,timeout=90).read().decode()
        for it in re.findall(r"<Item>(.*?)</Item>",t,re.S):
            ti=(re.findall(r"<Title>(.*?)</Title>",it) or [""])[0]
            pr=float((re.findall(r"<CurrentPrice[^>]*>([\d.]+)",it) or ["0"])[0])
            sh=(re.findall(r"<ShippingServiceCost[^>]*>([\d.]+)",it) or ["?"])[0]
            rows.append(("ebay",kind(ti),pr,ti[:60],sh))
        tp=int((re.findall(r"<TotalNumberOfPages>(\d+)",t) or ["1"])[0])
        if pg>=tp: break
        pg+=1
except Exception as e: print("ebay err",str(e)[:200])
from collections import defaultdict
g=defaultdict(list)
for c,k,p,t,s in rows: g[(c,k)].append(p)
for key,v in sorted(g.items()): print(key,"n=",len(v),"min",min(v),"max",max(v),"avg",round(sum(v)/len(v),2))
print("-- low/odd samples --")
for c,k,p,t,s in sorted(rows,key=lambda r:r[2])[:8]: print(c,k,p,"ship",s,t)
for c,k,p,t,s in sorted(rows,key=lambda r:-r[2])[:5]: print(c,k,p,"ship",s,t)
from collections import Counter
print("eBay shipping cost values:",Counter(str(s) for c,k,p,t,s in rows if c=="ebay").most_common(5))
print("etsy shipping profiles:",Counter(str(s) for c,k,p,t,s in rows if c=="etsy").most_common(5))
