"""eBay Sell Fulfillment API client for the order bridge. Env: EBAY_CLIENT_ID, EBAY_CLIENT_SECRET, EBAY_REFRESH_TOKEN.
Reads paid, unshipped orders and posts tracking back. Never prints buyer details."""
import os,json,base64,urllib.request,urllib.parse,urllib.error,datetime
ID=os.environ.get("EBAY_CLIENT_ID","").strip(); SEC=os.environ.get("EBAY_CLIENT_SECRET","").strip(); RT=os.environ.get("EBAY_REFRESH_TOKEN","").strip()
API="https://api.ebay.com/sell/fulfillment/v1"; _tok=None
def token():
    global _tok
    if _tok: return _tok
    d=urllib.parse.urlencode({"grant_type":"refresh_token","refresh_token":RT,"scope":"https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.inventory"}).encode()
    r=urllib.request.Request("https://api.ebay.com/identity/v1/oauth2/token",d,{"Authorization":"Basic "+base64.b64encode(f"{ID}:{SEC}".encode()).decode(),"Content-Type":"application/x-www-form-urlencoded"})
    _tok=json.load(urllib.request.urlopen(r,timeout=60))["access_token"]; return _tok
def call(m,p,body=None):
    r=urllib.request.Request(API+p,data=json.dumps(body).encode() if body is not None else None,method=m,headers={"Authorization":"Bearer "+token(),"Content-Type":"application/json","Accept":"application/json","Content-Language":"en-US"})
    try:
        x=urllib.request.urlopen(r,timeout=60); t=x.read(); return json.loads(t) if t else {"_status":x.status}
    except urllib.error.HTTPError as e: return {"_err":e.code,"body":e.read().decode()[:300]}
def open_orders(days=30):
    since=(datetime.datetime.utcnow()-datetime.timedelta(days=days)).strftime("%Y-%m-%dT00:00:00.000Z")
    out=[];off=0
    while True:
        r=call("GET","/order?"+urllib.parse.urlencode({"filter":f"orderfulfillmentstatus:{{NOT_STARTED|IN_PROGRESS}},creationdate:[{since}..]","limit":50,"offset":off}))
        if r.get("_err"): print("ebay orders error",r); return out
        out+=r.get("orders",[]); off+=50
        if off>=r.get("total",0): return out
CARR={"usps":"USPS","ups":"UPS","fedex":"FEDEX","dhl":"DHL"}
def add_tracking(order_id,carrier,number):
    o=call("GET","/order/"+urllib.parse.quote(order_id))
    if o.get("_err"): return o
    li=[{"lineItemId":x["lineItemId"],"quantity":x.get("quantity",1)} for x in o.get("lineItems",[])]
    code=next((v for k,v in CARR.items() if k in (carrier or "").lower()),"OTHER")
    body={"lineItems":li,"shippedDate":datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),"trackingNumber":number,"shippingCarrierCode":code}
    return call("POST","/order/"+urllib.parse.quote(order_id)+"/shipping_fulfillment",body)
if __name__=="__main__":
    import sys
    if sys.argv[1:]==["peek"]:
        for o in open_orders(60):
            print("EBAY ORDER",o["orderId"],o.get("creationDate","")[:10],o.get("orderPaymentStatus"),o.get("orderFulfillmentStatus"),"skus:",[x.get("sku") for x in o.get("lineItems",[])],"total:",(o.get("pricingSummary",{}).get("total") or {}).get("value"))
        print("peek done")
