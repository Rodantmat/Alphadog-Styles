"""Admin console + order lifecycle QA against the isolated local rig (real worker, throwaway Postgres, mock Stripe/email).
Env: QA_BROWSER=chromium|firefox|webkit  QA_MOBILE=1"""
import os,sys,json,re,time,urllib.request,urllib.error
from playwright.sync_api import sync_playwright
B="http://localhost:8787"; MOCK="http://localhost:9100"; TOK="test-admin-token"; OUT=os.environ.get("QA_OUT","out/admin_qa"); os.makedirs(OUT,exist_ok=True)
BR=os.environ.get("QA_BROWSER","chromium"); MOB=os.environ.get("QA_MOBILE")=="1"
fails=[];passes=[0]
def ok(c,msg):
    if c: passes[0]+=1
    else: fails.append(msg); print("FAIL:",msg,flush=True)
def call(m,p,b=None,adm=True,base=B,raw=False):
    h={"content-type":"application/json"}
    if adm: h["x-admin-token"]=TOK
    r=urllib.request.Request(base+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers=h)
    try:
        resp=urllib.request.urlopen(r,timeout=30); t=resp.read(); return resp.status,(t if raw else json.loads(t or b"{}"))
    except urllib.error.HTTPError as e:
        t=e.read(); 
        try: return e.code,json.loads(t)
        except Exception: return e.code,{"raw":t[:200].decode("utf8","ignore")}
def mails(): return call("GET","/__mails",base=MOCK,adm=False)[1]
def stripe(): return call("GET","/__stripe",base=MOCK,adm=False)[1]
EMAIL="buyer@example.com"
def store_order(email=EMAIL,pay=True):
    it={"prod":"tee","color":"White","size":"M","qty":2,"front":{"part":"head","size":"s","breed":"beagle","theme":"geo","style":"heart"},"back":{"part":"body","size":"l","breed":"beagle","theme":"geo","style":"heart"}}
    s,r=call("POST","/api/orders",{"items":[it],"email":email,"lang":"en","ship":{"name":"Test Buyer","a1":"1 Main St","city":"San Diego","st":"CA","zip":"92101","phone":"5551234"}},adm=False)
    if s!=200: return s,r
    if pay:
        call("GET","/pay/"+re.search(r"cs_mock_\d+",r["url"]).group(0),base=MOCK,adm=False,raw=True)
        s2,r2=call("POST","/api/orders/confirm",{"id":r["id"]},adm=False); r["confirm"]=r2
    return s,r
def mk(plat,ext,sku,qty,total,email="m@example.com",**kw):
    return call("POST","/api/internal/market/order",{"plat":plat,"ext_id":ext,"email":email,"total":total,"ship":{"name":"Mk Buyer","a1":"9 Oak","city":"Austin","st":"TX","zip":"73301"},"items":[{"sku":sku,"qty":qty,"title":"t"}],**kw})
# ------------------------------------------------ seed
print("seeding",flush=True)
code=None
s,_=call("POST","/api/auth/request",{"email":EMAIL,"lang":"en"},adm=False); ok(s==200,"auth request 200")
m=[x for x in mails() if EMAIL in x["to"]]; code=re.search(r"\b(\d{6})\b",m[-1]["html"]).group(1) if m else None; ok(bool(code),"login email arrived with code")
s,r=call("POST","/api/auth/verify",{"email":EMAIL,"code":code},adm=False); ok(s==200 and r.get("token"),"login verify creates account")
s,so=store_order(); ok(s==200 and so.get("confirm",{}).get("status")=="paid","store order -> mock Stripe -> paid ("+str(so)[:200]+")"); SO=so.get("id")
s,so2=store_order(); SO2=so2.get("id"); ok(s==200,"second store order")
shipping_tot=so["total"]+so2["total"]
a=mk("etsy","1001","T-FB-1-WH-M",1,2999); b=mk("etsy","1002","H-LR-1-GR-L",2,4999); c=mk("ebay","2001","T-FB-1-WH-M",1,3500); d=mk("tiktok","3001","T-FB-1-WH-M",1,2800)
ok(all(x[1].get("status")=="paid" for x in (a,b,c,d)),"4 marketplace orders decoded & paid: "+str([x[1] for x in (a,b,c,d)])[:300])
bad=mk("etsy","1003","NOT-A-SKU",1,1000); ok(bad[1].get("status")=="needs_attention","undecodable SKU -> needs_attention")
tst=mk("ebay","2002","T-FB-1-WH-M",1,1500,test=True); ok(tst[1].get("status")=="paid_test","test flag -> paid_test (never revenue)")
tf=mk("tiktok","3002","T-FB-1-WH-M",1,1500,test=True); call("POST","/api/internal/orders/"+tf[1]["id"],{"status":"test_failed"})
dup=mk("etsy","1001","T-FB-1-WH-M",1,2999); ok(dup[1].get("dup") is True,"duplicate marketplace order ignored")
call("POST","/api/internal/orders/"+a[1]["id"],{"status":"in_production","printify_id":"pf1"}); call("POST","/api/internal/orders/"+c[1]["id"],{"status":"shipped","tracking":"https://track.example/ebay"})
s,_=call("POST","/api/subscribe",{"email":"s1@example.com","lang":"en"},adm=False); call("POST","/api/subscribe",{"email":"s2@example.com","lang":"es"},adm=False)
call("POST","/api/contact",{"email":"ask@example.com","msg":"Do you ship to Canada?"},adm=False)
call("POST","/api/internal/support",{"mailbox":"support","from":"cust@example.com","subject":"Where is my order","body":"Hello?"})
real_total=2999+4999+3500+2800+shipping_tot
# ------------------------------------------------ API-level checks
s,h=call("GET","/api/internal/health"); ok(s==200 and h["db"] and h["mail"] and h["stripe"]=="live" and h["webhook"],"health shape"); ok(h["issues"]["needs_attention"]==1 and h["issues"]["test_failed"]==1,"health counts problems")
s,st=call("GET","/api/internal/stats"); ok(st["sum"]["d90"]==real_total,f"stats revenue {st['sum']['d90']} == {real_total}"); ok(st["sum"]["n90"]==6,"stats counts 6 paid orders, got "+str(st["sum"]["n90"])); ok(st["chan"]["etsy"]["n"]==2 and st["chan"]["ebay"]["n"]==1 and st["chan"]["tiktok"]["n"]==1 and st["chan"]["store"]["n"]==2,"stats channels "+str(st["chan"]))
ok(st["counts"]["users"]==1 and st["counts"]["subs"]==2 and st["counts"]["support_new"]==1,"stats counts "+str(st["counts"])); ok(st["top"]["breed"] and st["top"]["prod"][0]["k"] in("tee","hoodie"),"top lists")
for p in ("/api/internal/orders/all","/api/internal/customers","/api/internal/subscribers","/api/internal/messages"): ok(call("GET",p)[0]==200,p+" 200")
for p in ("/api/internal/stats","/api/internal/health","/api/internal/orders/all","/api/internal/customers","/api/internal/subscribers","/api/internal/messages"): ok(call("GET",p,adm=False)[0]==403,p+" refuses without token")
ok(call("GET","/api/internal/stats",None)[0]==200,"stats ok with token")
ok(call("POST","/api/internal/orders/"+SO,{"action":"bogus"})[0]==400,"unknown action 400"); ok(call("POST","/api/internal/orders/NOPE",{"action":"resend"})[0]==404,"unknown order 404")
ok(call("POST","/api/internal/orders/"+a[1]["id"],{"action":"refund"})[0]==400,"marketplace order not refundable here")
ok(call("POST","/api/internal/orders/"+a[1]["id"],{"action":"cancel"})[0]==400,"cannot cancel order already in production")
ok(call("POST","/api/internal/orders/"+SO,{"action":"requeue"})[0]==400,"requeue only for problem orders")
# ------------------------------------------------ UI
def run_ui():
  with sync_playwright() as p:
    bt=getattr(p,BR)
    br=bt.launch()
    kw={}
    if MOB:
        dev=dict(p.devices["iPhone 13"]);
        if BR=="firefox": dev.pop("is_mobile",None)
        kw=dev
    ctx=br.new_context(accept_downloads=True,**kw); pg=ctx.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append("pageerror "+str(e))); pg.on("console",lambda m:m.type=="error" and errs.append("console "+m.text))
    dialogs=[]
    def dlg(d): dialogs.append((d.type,d.message)); d.accept("")
    pg.on("dialog",dlg)
    ctx.add_init_script("try{localStorage.setItem('ad_admin',JSON.stringify('bad'))}catch(e){}")
    pg.goto(B+"/#/admin"); pg.wait_for_selector("#at",timeout=15000); ok(True,"bad token -> asked again")
    pg.evaluate("localStorage.setItem('ad_admin',JSON.stringify('test-admin-token'))"); 
    # remove init script effect: reload after clearing by navigating with fresh context
    ctx2=br.new_context(accept_downloads=True,**kw); pg=ctx2.new_page(); pg.on("pageerror",lambda e:errs.append("pageerror "+str(e))); pg.on("console",lambda m:m.type=="error" and errs.append("console "+m.text)); pg.on("dialog",dlg)
    pg.goto(B+"/"); pg.wait_for_selector("#app, main, body"); 
    pg.goto(B+"/#/admin"); pg.wait_for_selector("#at"); pg.fill("#at input","test-admin-token"); pg.click("#at button")
    try: pg.wait_for_selector("#ap .kpi",timeout=15000)
    except Exception:
        print("DEBUG app html:",pg.inner_html("#app")[:1800],"| TEXT:",pg.inner_text("#app")[:300],"| errs:",errs[:5],flush=True); pg.screenshot(path=f"{OUT}/{BR}_debug.png"); raise
    ok(True,"token entry opens console")
    def overflow(tag): 
        w=pg.evaluate("[document.documentElement.scrollWidth,innerWidth]"); ok(w[0]<=w[1]+2,f"no sideways page scroll on {tag} ({w})")
    txt=lambda:pg.inner_text("#ap")
    # overview
    t=txt(); money=lambda c:"$%.2f"%(c/100)
    ok(money(real_total) in t,"overview shows revenue "+money(real_total)); ok("Needs your attention" in t and "1 order(s) need attention" in t,"overview alerts: needs attention"); ok("new support message" in t,"overview alerts support")
    ok("Etsy" in t and "TikTok" in t and "eBay" in t,"overview channels"); ok("beagle" in t.lower() or "french" in t.lower() or "labrador" in t.lower(),"overview top breeds"); pg.screenshot(path=f"{OUT}/{BR}{'_m' if MOB else ''}_overview.png"); overflow("overview")
    # orders
    pg.click("[data-tab=orders]"); pg.wait_for_selector("#aol table"); rows=lambda:pg.locator("#aol tr").count()-1
    ok(rows()==6,f"Paid filter lists 6 real orders, got {rows()}"); overflow("orders")
    pg.click("[data-f=problem]"); pg.wait_for_function("document.querySelectorAll('#aol tr').length==3"); ok(rows()==2,"Problems = needs_attention + test_failed")
    pg.click("[data-f=test]"); pg.wait_for_function("document.querySelectorAll('#aol tr').length==3"); ok(rows()==2,"Test filter = 2")
    pg.click("[data-f=all]"); pg.wait_for_timeout(500); ok(rows()>=8,"All filter lists everything")
    pg.click("[data-f=real]"); pg.wait_for_function("document.querySelectorAll('#aol tr').length==7")
    pg.fill("#aoq",SO); pg.wait_for_function("document.querySelectorAll('#aol tr').length==2"); ok(SO in pg.inner_text("#aol"),"search by order id"); 
    pg.fill("#aoq","nomatch-xyz"); pg.wait_for_function("document.querySelectorAll('#aol tr').length==2 && /No orders here/.test(document.querySelector('#aol').innerText)"); ok(True,"search with no match shows empty message")
    pg.fill("#aoq",""); pg.wait_for_function("document.querySelectorAll('#aol tr').length==7")
    with pg.expect_download() as dl: pg.click("#aocsv")
    path=dl.value.path(); csv=open(path).read(); ok(SO in csv and csv.count("\n")>=6,"orders CSV downloads with rows")
    # open store order
    pg.click(f"[data-oo={SO}]"); pg.wait_for_selector("#aodp"); d=pg.inner_text("#aodp"); ok("Test Buyer" in d and "San Diego" in d and buyer_has(d),"order detail shows address + items"); pg.screenshot(path=f"{OUT}/{BR}{'_m' if MOB else ''}_order.png"); overflow("order detail")
    n0=len(mails()); pg.click("#aodp [data-a=resend]"); pg.wait_for_timeout(800); ok(len(mails())==n0+1 and "confirmed" in mails()[-1]["subject"],"resend receipt emails the customer")
    pg.fill("#aon","Customer asked for gift wrap"); pg.click("#aodp [data-a=note]"); pg.wait_for_timeout(800); pg.click(f"[data-oo={SO}]"); ok("gift wrap" in pg.inner_text("#aodp"),"private note saved and shown")
    pg.fill("#aot","not a link"); pg.click("#aodp [data-a=ship]"); pg.wait_for_timeout(400); ok(call("GET","/api/internal/orders/all?q="+SO)[1]["items"][0]["status"]=="paid","shipping rejects a bad tracking link")
    pg.fill("#aot","https://track.example/AD1"); n0=len(mails()); pg.click("#aodp [data-a=ship]"); pg.wait_for_timeout(900)
    o=call("GET","/api/internal/orders/all?q="+SO)[1]["items"][0]; ok(o["status"]=="shipped" and o["tracking"]=="https://track.example/AD1","mark shipped saves tracking"); ok(len(mails())==n0+1 and "shipped" in mails()[-1]["subject"],"shipped email sent")
    # refund (full) on second store order via UI
    pg.click(f"[data-oo={SO2}]"); pg.wait_for_selector("#aodp"); ok(pg.locator("#aodp [data-a=refund]").count()==1,"refund button on card order")
    n0=len(mails()); pg.click("#aodp [data-a=refund]"); pg.wait_for_timeout(1200)
    rf=[x for x in stripe() if x["p"]=="/v1/refunds"]; ok(len(rf)==1 and rf[0]["body"].get("payment_intent","").startswith("pi_mock") and "amount" not in rf[0]["body"],"full refund calls Stripe once with the payment intent")
    o=call("GET","/api/internal/orders/all?q="+SO2)[1]["items"][0]; ok(o["status"]=="refunded","order marked refunded"); ok(len(mails())==n0+1 and "refunded" in mails()[-1]["subject"],"refund email sent"); ok(o["data"]["refunds"][0]["amount"]==so2["total"],"refund amount recorded = order total")
    ok(any(k=="prompt" for k,_ in dialogs),"refund asks for amount first")
    # revenue drops after refund
    st2=call("GET","/api/internal/stats")[1]; ok(st2["sum"]["d90"]==real_total-so2["total"],"refunded order leaves revenue")
    # marketplace order has no refund / no cancel when in production
    pg.click("[data-f=real]"); pg.wait_for_timeout(600); pg.click(f"[data-oo={a[1]['id']}]"); pg.wait_for_selector("#aodp"); ok(pg.locator("#aodp [data-a=refund]").count()==0 and pg.locator("#aodp [data-a=cancel]").count()==0,"marketplace in-production order: no refund, no cancel")
    # problems: cancel + requeue
    pg.click("[data-f=problem]"); pg.wait_for_timeout(700); pg.click(f"[data-oo={bad[1]['id']}]"); pg.wait_for_selector("#aodp"); pg.click("#aodp [data-a=cancel]"); pg.wait_for_timeout(900)
    ok(call("GET","/api/internal/orders/all?q="+bad[1]["id"])[1]["items"][0]["status"]=="cancelled","cancel problem order"); ok(any(k=="confirm" for k,_ in dialogs),"cancel asks to confirm")
    pg.click("[data-f=problem]"); pg.wait_for_timeout(700); pg.click(f"[data-oo={tf[1]['id']}]"); pg.wait_for_selector("#aodp"); pg.click("#aodp [data-a=requeue]"); pg.wait_for_timeout(900)
    ok(call("GET","/api/internal/orders/all?q="+tf[1]["id"])[1]["items"][0]["status"]=="paid_test","retry failed test order -> paid_test")
    pg.click("[data-f=refunded]"); pg.wait_for_timeout(700); ok(rows()==2,"refunded/cancelled filter shows 2")
    # customers
    pg.click("[data-tab=customers]"); pg.wait_for_selector("#ap table"); t=txt(); ok(EMAIL in t and "1 registered" in t,"customers lists the account"); overflow("customers")
    with pg.expect_download() as dl: pg.click("#acc")
    ok(EMAIL in open(dl.value.path()).read(),"customers CSV")
    pg.click("[data-tab=subs]"); pg.wait_for_selector("#ap table"); t=txt(); ok("s1@example.com" in t and "s2@example.com" in t and "2 active" in t,"subscribers list"); 
    with pg.expect_download() as dl: pg.click("#asc")
    ok("s2@example.com" in open(dl.value.path()).read(),"subscribers CSV")
    pg.click("[data-tab=custom]"); pg.wait_for_selector("#ap table"); ok("No requests yet" in txt(),"custom tab renders (empty)")
    pg.click("[data-tab=inbox]"); pg.wait_for_selector("[data-done]"); t=txt(); ok("Where is my order" in t and "ship to Canada" in t,"inbox shows support + contact messages"); pg.click("[data-done]"); pg.wait_for_timeout(1000); ok("Where is my order" not in txt(),"mark support handled")
    # system
    pg.click("[data-tab=system]"); pg.wait_for_selector("[data-k=checkout_paused]"); t=txt(); ok("LIVE mode" in t and "Database" in t,"system health"); overflow("system")
    pg.click("[data-k=checkout_paused]"); pg.wait_for_selector("text=Resume checkout",timeout=8000)
    s,r=store_order(pay=False); ok(s==503,"paused checkout blocks new orders (got %s)"%s)
    pg.click("[data-k=checkout_paused]"); pg.wait_for_selector("text=Pause checkout"); s,r=store_order(pay=False); ok(s==200,"resumed checkout accepts orders")
    pg.click("[data-k=fulfil_paused]"); pg.wait_for_selector("text=Resume sending to print"); ok(call("GET","/api/internal/kv/fulfil_paused")[1]["v"]=="1","pause print flag set (fulfilment robot reads it)")
    pg.click("[data-k=fulfil_paused]"); pg.wait_for_selector("text=Pause sending to print"); ok(call("GET","/api/internal/kv/fulfil_paused")[1]["v"]=="0","print flag cleared")
    n0=len(mails()); pg.fill("#atm input","me@example.com"); pg.click("#atm button"); pg.wait_for_timeout(900); ok(len(mails())==n0+1 and mails()[-1]["to"]==["me@example.com"],"test email delivered")
    # walk every tab on the way back
    for k,_ in [("overview",0),("orders",0),("customers",0),("subs",0),("custom",0),("inbox",0),("system",0)]:
        pg.click(f"[data-tab={k}]"); pg.wait_for_timeout(500); ok(not pg.locator("#ap >> text=failed to load").count(),f"tab {k} loads without error")
    pg.click("#alo"); pg.wait_for_timeout(500); ok(pg.evaluate("localStorage.getItem('ad_admin')")in("null","\"\"",None),"lock clears token")
    ok(not errs,"no console/page errors: "+"; ".join(errs[:4]))
    br.close()
def buyer_has(d): return "beagle" in d.lower() or "Beagle" in d
# refund failure path
call("POST","/__reset",base=MOCK,adm=False)
run_ui()
print(f"RESULT {BR}{' mobile' if MOB else ''}: {passes[0]} passed, {len(fails)} failed")
open(f"{OUT}/{BR}{'_m' if MOB else ''}.json","w").write(json.dumps({"passed":passes[0],"fails":fails}))
sys.exit(1 if fails else 0)
