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
