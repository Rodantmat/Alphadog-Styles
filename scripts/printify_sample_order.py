import os,json,urllib.request,urllib.error
T=os.environ["PRINTIFY_TOKEN"].strip();SHOP=29544854;MODE=os.environ.get("MODE","calc");SHIP=os.environ.get("SHIP_METHOD","economy")
import subprocess,base64
open("/tmp/k.pem","w").write(os.environ["DATA_PRIV_KEY"])
A=json.loads(subprocess.run(["openssl","pkeyutl","-decrypt","-inkey","/tmp/k.pem","-pkeyopt","rsa_padding_mode:oaep","-in","/dev/stdin"],input=base64.b64decode(open("shop/private/sample_addr.enc").read()),capture_output=True,check=True).stdout)
def call(m,p,b=None):
    r=urllib.request.Request("https://api.printify.com"+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
    try: return json.load(urllib.request.urlopen(r,timeout=120))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:1500]); raise
CAP="6ae99d10eb5d7e24b80cb3b2"; TEE="6ae98c3776dc38811905cf5a"
cap=call("GET",f"/v1/shops/{SHOP}/products/{CAP}.json"); tee=call("GET",f"/v1/shops/{SHOP}/products/{TEE}.json")
cv=next(v for v in cap["variants"] if v["is_enabled"] and "Khaki" in v["title"]); tv=next(v for v in tee["variants"] if v["is_enabled"] and v["title"]=="Natural / S")
print("ITEMS",cv["title"],cv["cost"],"|",tv["title"],tv["cost"])
items=[{"product_id":CAP,"variant_id":cv["id"],"quantity":1},{"product_id":TEE,"variant_id":tv["id"],"quantity":1}]
addr={k:A.get(k,"") for k in ("first_name","last_name","country","region","address1","address2","city","zip")}
if os.environ.get("SAMPLE_PHONE"): addr["phone"]=os.environ["SAMPLE_PHONE"]
if os.environ.get("SAMPLE_EMAIL"): addr["email"]=os.environ["SAMPLE_EMAIL"]
print("SHIPPING",json.dumps(call("POST",f"/v1/shops/{SHOP}/orders/shipping.json",{"line_items":items,"address_to":addr})))
if MODE in ("order","draft"):
    meth={"standard":1,"priority":2,"express":3,"economy":4}[SHIP]
    o=call("POST",f"/v1/shops/{SHOP}/orders.json",{"external_id":"sample-minipoodle-001","label":"SAMPLE minipoodle cap+tee","line_items":items,"shipping_method":meth,"send_shipping_notification":False,"address_to":addr})
    oid=o["id"]; print("ORDER_ID",oid)
    if MODE=="order": print("PRODUCTION",json.dumps(call("POST",f"/v1/shops/{SHOP}/orders/{oid}/send_to_production.json",{})))
    d=call("GET",f"/v1/shops/{SHOP}/orders/{oid}.json"); print("ORDER",d.get("status"),d.get("app_order_id"),d.get("total_price"),d.get("total_shipping"),d.get("total_tax"),[(l.get("status"),l.get("cost"),l.get("metadata",{}).get("title"),l.get("metadata",{}).get("variant_label")) for l in d.get("line_items",[])])
