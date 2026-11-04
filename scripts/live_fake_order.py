"""Safe fake order on the LIVE store: a marketplace-style order flagged test=true -> status paid_test (never revenue, never a Printify order).
Then store_fulfill (ONLY_TEST) builds every real print file, checks the Printify variants, and asks Printify for a shipping quote (creates no order).
Expected end state: test_complete. Also read-checks every admin endpoint on the live site."""
import os,sys,json,time,urllib.request,urllib.error
S=os.environ["STORE_URL"].rstrip("/"); T=os.environ["STORE_ADMIN_TOKEN"]
def call(m,p,b=None):
    r=urllib.request.Request(S+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"x-admin-token":T,"content-type":"application/json","User-Agent":"a"})
    try: x=urllib.request.urlopen(r,timeout=60); return x.status,json.load(x)
    except urllib.error.HTTPError as e: return e.code,json.loads(e.read() or b"{}")
bad=[]
for p in ["/api/internal/health","/api/internal/stats","/api/internal/orders/all?g=real","/api/internal/orders/all?g=test","/api/internal/customers","/api/internal/subscribers","/api/internal/messages","/api/internal/custom","/api/internal/support?status=new"]:
    s,j=call("GET",p); print(s,p,json.dumps(j)[:140]); 
    if s!=200: bad.append(p)
h=call("GET","/api/internal/health")[1]; print("HEALTH",json.dumps(h))
if len(call("GET","/api/internal/stats")[1]["days"])!=30: bad.append("stats days")
ext="FAKE"+str(int(time.time()))
s,r=call("POST","/api/internal/market/order",{"plat":"etsy","ext_id":ext,"email":"fake-test@example.com","total":2799,"test":True,"ship":{"name":"Fake Tester","a1":"123 Test St","city":"San Diego","st":"CA","zip":"92101"},"items":[{"sku":"T-FB-1-WH-M","qty":1,"title":"fake"},{"sku":"H-LR-1-GR-L","qty":1,"title":"fake"}]})
print("created",s,r); oid=r.get("id")
if s!=200 or r.get("status")!="paid_test": bad.append("fake order not created as paid_test")
open("fake_order_id.txt","w").write(oid or "")
if bad: print("BAD",bad); sys.exit(1)
