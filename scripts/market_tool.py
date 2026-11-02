"""One entry point for marketplace jobs run from GitHub Actions (market-tool.yml). CMD: etsy-link | etsy-probe | etsy-sync | etsy-orders"""
import os,sys,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
cmd=os.environ.get("CMD","etsy-link"); arg=os.environ.get("ARG","")
if cmd=="etsy-link":
    import etsy_api as E; print("ETSY CONNECT LINK:",E.store("POST","/api/internal/market/etsy/link",{})["url"])
elif cmd=="etsy-probe":
    import etsy_probe
elif cmd=="etsy-sync":
    import etsy_sync; etsy_sync.main(arg)
elif cmd=="etsy-orders":
    import market_orders; print(market_orders.etsy_poll())
elif cmd=="test-order":
    # end-to-end bridge test: fake marketplace order (test flag -> paid_test: print files are built, Printify is never charged)
    import etsy_api as E, json, time
    plan=json.load(open("store/data/market_plan.json")); from market_plan import sku
    skus=[sku("tee","french_bulldog","1","WH","L"),sku("hoodie","golden_retriever","2","GR","XL"),sku("wtank","beagle","3","MI","M"),sku("polo","labrador_retriever","1","HE","2XL"),sku("cap","pug","2","FP","One size"),sku("tank","boxer","4","HE","S")]
    print("decode:",json.dumps(E.store("POST","/api/internal/market/decode",{"skus":skus}))[:1500])
    r=E.store("POST","/api/internal/market/order",{"plat":"etsy","ext_id":"TEST"+str(int(time.time())),"email":"orders@alphadogstyles.com","test":True,
        "ship":{"name":"Test Buyer","a1":"123 Test St","city":"San Diego","st":"CA","zip":"92101","country":"US"},"items":[{"sku":s,"qty":1} for s in skus]})
    print("ORDER:",r)
elif cmd=="orders-peek":
    import market_orders; market_orders.mail_peek()
elif cmd=="orders-poll":
    import market_orders; print(market_orders.mail_poll())
