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
if __name__=="__main__":
    n=0
    try: n+=etsy_poll()
    except SystemExit as e: print(e)
    except Exception as e: print("etsy poll error",e)
    print("new marketplace orders:",n)
