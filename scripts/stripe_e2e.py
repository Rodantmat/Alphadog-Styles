"""Live Stripe TEST-mode checkout on alphadogstyles.com (real backend, test card). Prints the order id and result."""
import json, os, re, sys, time
from playwright.sync_api import sync_playwright
BASE = "https://alphadogstyles.com"
EMAIL = os.environ["TEST_EMAIL"]
OUT = "out/stripe_e2e"; os.makedirs(OUT, exist_ok=True)
line = {"prod": "tee", "color": "Soft Pink", "slug": "soft-pink", "label": "Soft Pink", "size": "M", "qty": 1, "fo": "head_l", "bo": "none", "bf": "beagle", "bb": "beagle", "th": "geo", "st": "heart", "thb": "geo", "stb": "heart"}
def shot(p, n):
    try: p.screenshot(path=f"{OUT}/{n}.png", full_page=True)
    except Exception as e: print("shot fail", e)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 1280, "height": 900}); page = ctx.new_page()
    page.goto(BASE + "/#/shop"); page.wait_for_selector("#app > *")
    page.goto(BASE + "/#/design?prod=tee&breed=beagle&theme=geo&style=heart&color=Soft%20Pink"); page.wait_for_selector("#pv svg", timeout=30000)
    page.click("#ctl [data-k=front][data-opt='head_l']"); page.click("#ctl [data-k=back][data-opt='none']"); page.click("#add"); page.wait_for_timeout(500)
    page.goto(BASE + "/#/checkout"); page.wait_for_selector("#co", timeout=20000)
    page.fill("#co [name=email]", EMAIL); page.fill("#co [name=fn]", "Test"); page.fill("#co [name=ln]", "Order")
    page.fill("#co [name=a1]", "123 Test St"); page.fill("#co [name=city]", "San Diego"); page.select_option("#co [name=st]", "CA"); page.fill("#co [name=zip]", "92101")
    shot(page, "1_checkout")
    page.on("response", lambda r: print("RESP", r.status, r.url[:120], (r.text()[:300] if "/api/orders" in r.url else "")) if ("/api/" in r.url or "stripe.com" in r.url) else None)
    page.on("framenavigated", lambda f: print("NAV", f.url[:120]) if f == page.main_frame else None)
    page.click("#pay")
    page.wait_for_timeout(8000); shot(page, "1b_after_pay"); print("TOAST:", page.inner_text("#toast") if page.locator("#toast").count() else "-", "| URL", page.url[:120])
    page.wait_for_url(re.compile(r"checkout\.stripe\.com"), timeout=60000)
    print("stripe url host ok; livemode hint:", "cs_test_" in page.url)
    page.wait_for_timeout(4000)
    for how in ("radio-first","role","label"):
        try:
            if how=="radio-first": page.locator("input[type=radio]").first.check(force=True, timeout=6000)
            elif how=="role": page.get_by_role("radio", name=re.compile("Card")).first.check(force=True, timeout=6000)
            else: page.locator("label:has-text('Card')").first.click(timeout=6000)
            if page.locator("#cardNumber").count(): break
        except Exception as e: print("card via", how, "failed", str(e)[:120])
    print("RADIOS", page.locator("input[type=radio]").count(), "cardNumber", page.locator("#cardNumber").count())
    page.wait_for_selector("#cardNumber", timeout=30000)
    shot(page, "2_stripe")
    page.fill("#cardNumber", "4242424242424242"); page.fill("#cardExpiry", "1233"); page.fill("#cardCvc", "123")
    if page.locator("#billingName").count(): page.fill("#billingName", "Test Order")
    if page.locator("#billingPostalCode").count(): page.fill("#billingPostalCode", "92101")
    shot(page, "3_stripe_filled")
    page.click(".SubmitButton, button[type=submit]")
    page.wait_for_url(re.compile(r"alphadogstyles\.com/#/done/"), timeout=90000)
    m = re.search(r"#/done/([\w-]+)", page.url); oid = m.group(1)
    page.wait_for_timeout(6000)
    print("ORDER", oid); print("PAGE:", page.inner_text("#app")[:300].replace("\n", " | "))
    shot(page, "4_done")
    r = page.evaluate("""async id=>{const r=await fetch('/api/orders/confirm',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id})});return [r.status,await r.text()]}""", oid)
    print("CONFIRM", r)
    b.close()
