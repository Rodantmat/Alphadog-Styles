"""Marketplace order bridge: pull paid, unshipped marketplace orders and hand them to the store (which fulfils
through the same Printify pipeline as website orders); push tracking numbers back when Printify ships.
Etsy via Open API v3 (eBay / TikTok added when their API keys exist). Only orders whose SKUs are our consolidated-listing
SKUs are taken; anything else (old Printify-linked listings) is left for Printify.
Usage: python3 scripts/market_orders.py [poll]"""
import os,sys,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import re
SKU=re.compile(r"^[A-Z]-[A-Z]{2}-\d-[A-Z]{2}(-\w+)?$")
def etsy_poll():
    import etsy_api as E
    if not E.KEY: print("etsy: no keys"); return 0
    r=E.call("GET",f"/shops/{E.shop_id()}/receipts",q={"was_paid":"true","was_shipped":"false","was_canceled":"false","limit":50})
    if r.get("_err"): print("etsy receipts error",r); return 0
    n=0
    for rc in r.get("results",[]):
        tr=rc.get("transactions",[])
        ours=[t for t in tr if SKU.match((t.get("sku") or "").upper())]
        if not ours: continue
        if len(ours)!=len(tr): print("etsy receipt",rc["receipt_id"],"mixes old Printify items - ours only")
        items=[{"sku":t["sku"],"qty":t.get("quantity",1),"title":t.get("title","")[:80]} for t in ours]
        ship={"name":rc.get("name",""),"a1":rc.get("first_line",""),"a2":rc.get("second_line") or "","city":rc.get("city",""),"st":rc.get("state",""),"zip":rc.get("zip",""),"phone":"","country":rc.get("country_iso") or "US"}
        tot=rc.get("grandtotal") or {}; cents=int(round(tot.get("amount",0)*100/ (tot.get("divisor") or 100))) if tot else 0
        res=E.store("POST","/api/internal/market/order",{"plat":"etsy","ext_id":str(rc["receipt_id"]),"email":rc.get("buyer_email") or "","ship":ship,"items":items,"total":cents})
        print("etsy order",rc["receipt_id"],res); n+=0 if res.get("dup") else 1
    return n
CARRIER={"usps":"usps","ups":"ups","fedex":"fedex","dhl":"dhl"}
def push_tracking(plat,ext,carrier,number):
    if not number: return "no tracking number yet"
    if plat=="etsy":
        import etsy_api as E
        c=next((v for k,v in CARRIER.items() if k in (carrier or "").lower()),carrier or "other")
        return E.call("POST",f"/shops/{E.shop_id()}/receipts/{ext}/tracking",form={"tracking_code":number,"carrier_name":c,"send_bcc":"false"})
    return f"{plat}: tracking push not available yet"

# ---------------- eBay / TikTok sale emails (forwarded from the seller Gmail to orders@alphadogstyles.com) ----------------
import imaplib,email,email.utils,ssl
from email.header import decode_header,make_header
def _mail_text(msg):
    import html as H
    for part in msg.walk():
        if part.get_content_type()=="text/plain" and "attachment" not in str(part.get("Content-Disposition","")):
            return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8","replace")
    for part in msg.walk():
        if part.get_content_type()=="text/html":
            t=part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8","replace")
            t=re.sub(r"(?is)<(style|script).*?</\1>","",t); t=re.sub(r"(?i)<br\s*/?>|</(p|div|tr|td|h\d|li)>","\n",t); t=re.sub(r"<[^>]+>","",t)
            return H.unescape(t)
    return ""
def _lines(t): return [re.sub(r"[​-‏ ]"," ",l).strip() for l in t.splitlines() if l.strip()]
EBAY_ITEMS=None
def parse_ebay(text):
    """'You made the sale' email -> dict(order, ship, items[{title,qty,specifics}]) or None"""
    L=_lines(text)
    if not any("shipping details" in l.lower() for l in L): return None
    i=next(k for k,l in enumerate(L) if "shipping details" in l.lower())
    addr=[]
    for l in L[i+1:i+8]:
        if l.lower().startswith("ship by") or l.lower().startswith("hi "): break
        addr.append(l)
    get=lambda key: next((L[k+1] for k,l in enumerate(L[:-1]) if l.rstrip(":").lower()==key),"")
    order=get("order"); qty=int(re.sub(r"\D","",get("quantity sold") or "1") or 1)
    spec={}
    for l in L:
        m=re.match(r"^(Dog Breed|Design|Color|Size|Hat Type)\s*:\s*(.+)$",l)
        if m: spec[m.group(1)]=m.group(2).strip()
    k=next((k for k,l in enumerate(L) if l.rstrip(":").lower()=="sold"),None); title=""
    if k:
        j=k-1
        while j>0 and re.match(r"^[A-Za-z /]+\s*:\s*\S",L[j]): j-=1
        title=L[j]
    ship={"name":addr[0] if addr else "","a1":addr[1] if len(addr)>1 else "","a2":"","city":"","st":"","zip":"","country":"US"}
    cityline=next((a for a in addr[2:] if re.search(r",\s*[A-Z]{2}\s+\d{5}",a)),"")
    if len(addr)>3 and addr[2]!=cityline: ship["a2"]=addr[2]
    m=re.search(r"^(.*),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)",cityline)
    if m: ship.update(city=m.group(1),st=m.group(2),zip=m.group(3))
    return {"order":order,"ship":ship,"qty":qty,"title":title,"spec":spec}
def ebay_sku(p):
    """Map title + item specifics from the sale email to our SKU (None if not ours / not decodable)."""
    plan=json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"store/data/market_plan.json")))
    t=p["title"].replace("...","").strip().lower()
    Ls=[l for l in plan["listings"] if l["plat"]=="ebay" and l["title"].lower().startswith(t[:40])]
    if not Ls: return None,"not ours"
    import market_plan as MP
    for L in Ls:
        P=plan["products"][L["prod"]]; sp=p["spec"]
        br=[b for b in L["breeds"] if len(L["breeds"])==1 or MP.BR[b]==sp.get("Dog Breed") or MP.short(b)==sp.get("Dog Breed")]
        ds=[d for d in P["designs"] if d["code"] in L["designs"] and d["name"].replace("·","-")==sp.get("Design")]
        if L["prod"]=="cap":
            cs=[c for c in P["colors"] if c["code"] in L["colors"] and c["name"].endswith(sp.get("Color","~")) and ({"cap_dad":"Dad Hat","cap_foam":"Trucker Hat","cap_mesh":"Mesh Trucker Hat"}[c["prod"]]==sp.get("Hat Type"))]
        else: cs=[c for c in P["colors"] if c["code"] in L["colors"] and c["name"]==sp.get("Color")]
        size=sp.get("Size","One size") if L["prod"]!="cap" else "One size"
        if len(br)==1 and len(ds)==1 and len(cs)==1: return MP.sku(L["prod"],br[0],ds[0]["code"],cs[0]["code"],size),"ok"
    return None,"ours but variation not in email"
def mail_poll():
    import mail_bridge as MB
    c=MB.creds(); addr="orders@alphadogstyles.com"
    if addr not in c: print("orders mailbox missing"); return 0
    M=imaplib.IMAP4_SSL(MB.HOST,993,ssl_context=ssl.create_default_context()); M.login(addr,c[addr]); M.select("INBOX")
    typ,data=M.uid("search",None,"UNKEYWORD","$AlphaDone"); n=0
    import etsy_api as E
    for uid in (data[0].split() if data and data[0] else [])[-100:]:
        msg=email.message_from_bytes(M.uid("fetch",uid,"(BODY.PEEK[])")[1][0][1]); subj=str(make_header(decode_header(msg.get("Subject",""))))
        text=_mail_text(msg); res=None
        if "made the sale" in subj.lower() or "sold" in subj.lower():
            p=parse_ebay(text)
            if p:
                sku,why=ebay_sku(p)
                if why=="not ours": res="ignored (not an AlphaDog listing)"
                else:
                    items=[{"sku":sku,"qty":p["qty"],"title":p["title"]}] if sku else [{"sku":"","qty":p["qty"],"title":p["title"]+" | "+json.dumps(p["spec"])}]
                    res=E.store("POST","/api/internal/market/order",{"plat":"ebay","ext_id":p["order"] or uid.decode(),"ship":p["ship"],"items":items})
                    n+=0 if res.get("dup") else 1
        print("orders@",uid.decode(),subj[:70],"->",res)
        M.uid("store",uid,"+FLAGS","($AlphaDone)")
    M.logout(); return n
def mail_peek(q="code"):
    import mail_bridge as MB
    c=MB.creds(); addr="orders@alphadogstyles.com"
    M=imaplib.IMAP4_SSL(MB.HOST,993); M.login(addr,c[addr]); M.select("INBOX")
    typ,data=M.uid("search",None,"ALL")
    for uid in (data[0].split() if data and data[0] else [])[-5:]:
        msg=email.message_from_bytes(M.uid("fetch",uid,"(BODY.PEEK[])")[1][0][1]); subj=str(make_header(decode_header(msg.get("Subject",""))))
        t=_mail_text(msg); m=re.search(r"(?:code|código)[^0-9]{0,40}(\d{6,10})",t,re.I)
        print("MAIL",uid.decode(),subj[:90],"| CODE:",m.group(1) if m else "-")
    M.logout()
# ---------------- read sale emails straight from the seller Gmail (IMAP + app password; read-only, nothing is marked or moved) -------------
def gmail_poll():
    pw=os.environ.get("FLIPPING_GMAIL_APP_PASSWORD","").replace(" ","").strip(); user=os.environ.get("FLIPPING_GMAIL_USER","flippingmagic.sales@gmail.com")
    if not pw: print("gmail: no app password"); return 0
    import etsy_api as E
    seen=set((E.store("GET","/api/internal/kv/gmail_seen").get("v") or [])[-2000:])
    M=imaplib.IMAP4_SSL("imap.gmail.com",993,ssl_context=ssl.create_default_context()); M.login(user,pw)
    M.select("INBOX",readonly=True)
    import datetime; since=(datetime.date.today()-datetime.timedelta(days=int(os.environ.get("GMAIL_DAYS","3")))).strftime("%d-%b-%Y")
    typ,data=M.search(None,f'(SINCE {since} FROM "ebay" SUBJECT "made the sale")'); n=0; new=[]
    for num in (data[0].split() if data and data[0] else []):
        msg=email.message_from_bytes(M.fetch(num,"(BODY.PEEK[])")[1][0][1]); mid=msg.get("Message-ID","") or num.decode()
        if mid in seen: continue
        p=parse_ebay(_mail_text(msg)); res="unparsed"
        if p:
            sku,why=ebay_sku(p)
            if why=="not ours": res="not ours"
            else:
                items=[{"sku":sku,"qty":p["qty"],"title":p["title"]}] if sku else [{"sku":"","qty":p["qty"],"title":p["title"]+" | "+json.dumps(p["spec"])}]
                res=E.store("POST","/api/internal/market/order",{"plat":"ebay","ext_id":p["order"] or mid,"ship":p["ship"],"items":items}); n+=0 if res.get("dup") else 1
        print("gmail",str(make_header(decode_header(msg.get("Subject",""))))[:70],"->",res); new.append(mid)
    M.logout()
    if new: E.store("POST","/api/internal/kv/gmail_seen",{"v":(list(seen)+new)[-2000:]})
    return n

if __name__=="__main__":
    n=0
    try: n+=etsy_poll()
    except SystemExit as e: print(e)
    except Exception as e: print("etsy poll error",e)
    try: n+=mail_poll()
    except Exception as e: print("mail poll error",e)
    try: n+=gmail_poll()
    except Exception as e: print("gmail poll error",e)
    print("new marketplace orders:",n)
