"""Shard cart: add-to-cart for every product x option family, cart lines/prices/shipping/qty/remove/persistence/i18n,
checkout validation + intercepted order payload, custom-design flow (mocked), saved designs (mocked)."""
import re, os, sys, json, zlib, struct
sys.path.insert(0, os.path.dirname(__file__))
from common import *

LINES = """()=>[...document.querySelectorAll('#lines .line')].map(l=>({id:l.dataset.id,name:l.querySelector('div:nth-child(2) > b').innerText,
  smalls:[...l.querySelectorAll('div:nth-child(2) > small')].map(s=>s.innerText),qty:l.querySelector('.qty b').innerText,price:l.querySelector(':scope > b').innerText,
  th:(l.querySelector('.th')||{}).innerHTML||''}))"""
SUM = """()=>Object.fromEntries([...document.querySelectorAll('.sum .r')].map(r=>[r.children[0].innerText,r.children[1].innerText]).concat([['_note',(document.querySelector('.sum small')||{}).innerText||''],['_badge',document.querySelector('#cartn').innerText]]))"""


def png(rgb):
    w = h = 48
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


def cart_shard(qa, browser, p):
    ctx = qa.context(browser, viewport={"width": 1280, "height": 900})
    page = qa.watch(ctx.new_page())
    page.route("https://checkout.stripe.com/**", lambda r: r.fulfill(status=200, content_type="text/html", body="<h1>QA fake Stripe page</h1>"))
    cat = catalog(ctx)
    P = {x["id"]: x for x in cat["products"]}
    B = [b["slug"] for b in cat["breeds"]]
    TH = [t["id"] for t in cat["themes"]]
    ST = [s["id"] for s in cat["styles"]]
    bname = {b["slug"]: b["name"] for b in cat["breeds"]}
    tname = {t["id"]: t["name"] for t in cat["themes"]}
    sname = {s["id"]: s["name"] for s in cat["styles"]}
    FO = {o["id"]: o for o in cat["front_opts"]}
    BO = {o["id"]: o for o in cat["back_opts"]}
    SHIP = cat["shipping"]
    click = lambda sel: page.evaluate("s=>{const e=document.querySelector(s);if(!e)return false;e.click();return true}", sel)
    T = lambda s, *a: page.evaluate("async([s,a])=>(await import('./js/i18n.js')).t(s,...a)", [s, list(a)])
    qa.go(page, "#/cart")
    page.evaluate("localStorage.removeItem('ad_cart')")
    page.reload(); page.wait_for_selector("#app > *")

    # ---------- plan: every product x every option family
    plan = []
    i = 0
    for pid, prod in P.items():
        fos = [o["id"] for o in opts_of(cat, pid, "front") if o["id"] != "none"] if "front" in sides_of(cat, pid) else []
        bos = [o["id"] for o in opts_of(cat, pid, "back") if o["id"] != "none"] if "back" in sides_of(cat, pid) else []
        has_none_f = any(o["id"] == "none" for o in opts_of(cat, pid, "front"))
        combos = [(f, "none" if bos else None) for f in fos] + ([("none", b) for b in bos] if has_none_f else []) + ([(fos[-1], bos[0])] if fos and bos else [])
        cols = [c for c in prod["colors"] if c[2]]
        for f, b in combos:
            col = cols[i % len(cols)]
            size = prod["sizes"][(i * 5 + 3) % len(prod["sizes"])]
            if i % 7 == 0 and prod["sizes"][-1] in prod.get("sur", {}):
                size = prod["sizes"][-1]
            plan.append({"prod": pid, "color": col[0], "slug": col[3], "label": col[4] if len(col) > 4 and col[4] else col[0], "size": size, "qty": 2 if i % 5 == 4 else 1,
                         "fo": f, "bo": b, "bf": B[i % len(B)], "bb": B[(i * 7 + 3) % len(B)], "th": TH[i % len(TH)], "st": ST[i % len(ST)], "thb": TH[(i + 1) % len(TH)], "stb": ST[(i + 2) % len(ST)]})
            i += 1
    qa.data["cart_plan_lines"] = len(plan)

    def add_items(items):
        badge = 0
        for n, it in enumerate(items):
            qa.go(page, f"#/design?prod={it['prod']}&breed={it['bf']}&theme={it['th']}&style={it['st']}&qa={n}", wait="#pv svg", quiet=False)
            click(f"#ctl .sw[data-color='{it['color']}']"); click(f"#ctl [data-size='{it['size']}']")
            click(f"#ctl [data-k=front][data-opt='{it['fo']}']")
            if it["bo"] is not None:
                click(f"#ctl [data-k=back][data-opt='{it['bo']}']")
                if it["bo"] != "none":
                    page.select_option("#ctl select[data-k=back]", it["bb"])
                    click(f"#ctl [data-k=back][data-f=theme][data-v='{it['thb']}']"); click(f"#ctl [data-k=back][data-f=style][data-v='{it['stb']}']")
            for _ in range(it["qty"] - 1):
                click("#ctl [data-q='1']")
            page.click("#add")
            page.wait_for_timeout(80)
            badge += it["qty"]
            tb = page.inner_text("#cartn")
            qa.ok("add_to_cart", tb == str(badge) and page.inner_text("#toast") == T("Added to cart"), "Add to cart does not update badge / show toast", sev="high",
                  repro=f"#/design {it['prod']} {it['color']} {it['size']} front {it['fo']} back {it['bo']} -> Add to cart", expected=badge, actual=(tb, page.inner_text("#toast")), page=page)

    def exp_label(side, it):
        o = (FO if side == "front" else BO)[it["fo"] if side == "front" else it["bo"]]
        b, th, st = (it["bf"], it["th"], it["st"]) if side == "front" else (it["bb"], it["thb"], it["stb"])
        if side == "back" and it["fo"] != "none" and False:
            pass
        intended = f"{bname[b]} · {tname[th]} {sname[st]} · {o['name']}"
        fo_name = next((x["name"] for x in cat["front_opts"] if x.get("part") == o["part"] and x.get("size") == o["size"]), "")
        coded = f"{bname[b]} · {tname[th]} {sname[st]} · {fo_name}"
        return intended, coded

    def check_cart(items, tag):
        qa.go(page, "#/cart", wait="#app h1")
        qa.quiet(page, 500)
        lines = page.evaluate(LINES)
        qa.ok("cart_lines", len(lines) == len(items), f"Cart shows wrong number of lines ({tag})", sev="high", expected=len(items), actual=len(lines), page=page)
        sub = 0
        for ln, it in zip(lines, items):
            front = it["fo"] != "none"
            back = it["bo"] not in (None, "none")
            # what the designer shows: back keeps front breed/theme/style unless changed
            if back and it["bo"] != "none":
                pass
            pr = price_cents(cat, it["prod"], front + back, it["size"]) * it["qty"]
            sub += pr
            rep = f"{tag}: add {it['prod']} {it['color']} {it['size']} x{it['qty']} front={it['fo']} ({it['bf']} {it['th']} {it['st']}) back={it['bo']} ({it['bb']} {it['thb']} {it['stb']}), open #/cart"
            qa.ok("cart_lines", ln["name"] == P[it["prod"]]["name"], "Cart line product name wrong", sev="high", repro=rep, expected=P[it["prod"]]["name"], actual=ln["name"])
            qa.ok("cart_lines", ln["smalls"] and ln["smalls"][0] == f"{it['label']} · {it['size']}", "Cart line color/size wrong", sev="high", repro=rep, expected=f"{it['label']} · {it['size']}", actual=ln["smalls"][:1])
            exp_smalls = 1 + front + back
            qa.ok("cart_lines", len(ln["smalls"]) == exp_smalls, "Cart line design sides wrong", sev="high", repro=rep, expected=exp_smalls, actual=ln["smalls"])
            sm = ln["smalls"][1:]
            if front and sm:
                intended, _ = exp_label("front", it)
                qa.ok("cart_lines", sm[0] == f"Front: {intended}", "Cart front design label wrong", sev="high", repro=rep, expected=f"Front: {intended}", actual=sm[0], page=page)
            if back and len(sm) >= 1:
                intended, coded = exp_label("back", it)
                act = sm[-1]
                if act != f"Back: {intended}" and act == f"Back: {coded}":
                    qa.defect("low", "cart_lines", "Cart/checkout names the back placement with the front-option name (e.g. 'Full body' shows as 'Big body')", repro=rep,
                              expected=f"Back: {intended}", actual=act)
                    qa.count("cart_lines")
                else:
                    qa.ok("cart_lines", act == f"Back: {intended}", "Cart back design label wrong", sev="high", repro=rep, expected=f"Back: {intended}", actual=act, page=page)
            qa.ok("cart_price", ln["price"] == money(pr), "Cart line price differs from catalog rule (sides/size surcharge/qty)", sev="high", repro=rep, expected=money(pr), actual=ln["price"], page=page)
            qa.ok("cart_lines", ln["qty"] == str(it["qty"]), "Cart line qty wrong", repro=rep, expected=it["qty"], actual=ln["qty"])
            ph, art, _ = parse_svg(ln["th"])
            side = "front" if front else "back"
            o = (FO[it["fo"]] if front else BO[it["bo"]])
            b, th, st = (it["bf"], it["th"], it["st"]) if front else (it["bb"], it["thb"], it["stb"])
            ea = f"art/{th}_{st}/{b}_{'front' if o['part'] == 'head' else 'back'}.svg"
            qa.ok("cart_thumbs", ph == f"img/{it['prod']}_{it['slug']}_{side}.webp" and art == ea, "Cart thumbnail does not match the line", sev="medium", repro=rep, expected=(f"img/{it['prod']}_{it['slug']}_{side}.webp", ea), actual=(ph, art))
        s = page.evaluate(SUM)
        ship = 0 if sub >= SHIP["free_over"] else SHIP["flat"]
        qa.ok("cart_totals", s.get("Subtotal") == money(sub), f"Cart subtotal wrong ({tag})", sev="high", expected=money(sub), actual=s.get("Subtotal"), page=page)
        qa.ok("cart_totals", s.get("Shipping (US)") == (money(ship) if ship else "Free"), f"Cart shipping rule wrong ({tag})", sev="high", expected=money(ship) if ship else "Free", actual=s.get("Shipping (US)"))
        qa.ok("cart_totals", s.get("Total") == money(sub + ship + items_fee(items)), f"Cart total wrong ({tag})", sev="high", expected=money(sub + ship + items_fee(items)), actual=s.get("Total"))
        note = T("Add {0} more for free shipping", money(SHIP["free_over"] - sub)) if ship else T("You unlocked free shipping!")
        qa.ok("cart_totals", s.get("_note") == note, f"Free-shipping progress note wrong ({tag})", sev="low", expected=note, actual=s.get("_note"))
        qa.ok("cart_totals", s.get("_badge") == str(sum(x["qty"] for x in items)), f"Cart badge wrong ({tag})", expected=sum(x["qty"] for x in items), actual=s.get("_badge"))
        return lines, sub, ship

    def items_fee(items):
        return sum(x.get("fee", 0) for x in items[:1]) if any(x.get("fee") for x in items) else 0

    CH = 30
    chunks = [plan[i:i + CH] for i in range(0, len(plan), CH)]
    for ci, chunk in enumerate(chunks):
        page.evaluate("localStorage.setItem('ad_cart','[]')"); page.reload(); page.wait_for_selector("#app > *")
        add_items(chunk)
        if len(chunk) == CH:
            it = chunk[0]
            qa.go(page, f"#/design?prod={it['prod']}&breed={it['bf']}", wait="#pv svg", quiet=False)
            b0 = page.inner_text("#cartn"); page.click("#add"); page.wait_for_timeout(120)
            qa.ok("add_to_cart", page.inner_text("#cartn") == b0 and "30" in page.inner_text("#toast"), "31st cart line not refused with a clear limit message", sev="medium", actual=(b0, page.inner_text("#cartn"), page.inner_text("#toast")), page=page)
        lines, sub, ship = check_cart(chunk, f"cart chunk {ci + 1}/{len(chunks)}")
    plan = chunks[-1]
    badge = sum(x["qty"] for x in plan)
    qa.shot(page, "cart_full", full=False)
    # complete the look
    look = page.evaluate("[...document.querySelectorAll('.wrap > .grid a.card .art')].map(e=>e.dataset.b)")
    qa.ok("cart_misc", len(look) == 6 and set(look) == {plan[0]["bf"]}, "'Complete the look' does not show 6 designs of the first line's breed", sev="low", actual=look)
    # persistence
    page.reload(); page.wait_for_selector("#app h1"); qa.quiet(page)
    qa.ok("cart_misc", len(page.evaluate(LINES)) == len(plan), "Cart not persisted across reload", sev="high", actual=len(page.evaluate(LINES)))
    # every planned item must pass backend validation
    stored = page.evaluate("JSON.parse(localStorage.getItem('ad_cart'))")
    bad = [x for x in stored if not valid_item(cat, {k: v for k, v in x.items() if k != "_s"})]
    qa.ok("checkout", not bad, "Cart lines that the backend validItem() would reject", sev="critical", actual=bad[:3])
    qa.count("checkout", len(stored))
    # language: prices identical, labels translated
    for l in ("es", "pt"):
        page.select_option("#lang", l); qa.quiet(page)
        ls2 = page.evaluate(LINES)
        qa.ok("i18n", [x["price"] for x in ls2] == [x["price"] for x in lines], f"Cart prices change with language {l}", sev="high")
        qa.ok("i18n", not any(s.startswith("Front:") or s.startswith("Back:") for x in ls2 for s in x["smalls"]), f"Cart side labels untranslated in {l}", sev="low", actual=ls2[0]["smalls"])
        qa.shot(page, f"cart_{l}", quality=40)
    page.select_option("#lang", "en"); qa.quiet(page)

    # qty +/- and remove
    def line0():
        return page.evaluate(LINES)[0]
    q0 = int(line0()["qty"])
    page.locator("#lines .line").nth(0).locator("[data-d='1']").click(); page.wait_for_timeout(150)
    qa.ok("cart_qty", line0()["qty"] == str(q0 + 1) and page.inner_text("#cartn") == str(badge + 1), "Cart + does not increase qty/badge", sev="high", actual=(line0()["qty"], page.inner_text("#cartn")))
    unit = price_cents(cat, plan[0]["prod"], (plan[0]["fo"] != "none") + (plan[0]["bo"] not in (None, "none")), plan[0]["size"])
    qa.ok("cart_qty", line0()["price"] == money(unit * (q0 + 1)), "Cart line price not updated after +", sev="high", expected=money(unit * (q0 + 1)), actual=line0()["price"])
    for _ in range(25):
        click("#lines .line [data-d='1']")
        page.wait_for_timeout(15)
    qa.ok("cart_qty", line0()["qty"] == "20", "Cart qty cap is not 20", actual=line0()["qty"])
    for _ in range(25):
        click("#lines .line [data-d='-1']")
        page.wait_for_timeout(15)
    qa.ok("cart_qty", line0()["qty"] == "1", "Cart qty floor is not 1", actual=line0()["qty"])
    n0 = len(page.evaluate(LINES))
    page.locator("#lines .line").nth(n0 - 1).locator("[data-rm]").click(); page.wait_for_timeout(150)
    qa.ok("cart_qty", len(page.evaluate(LINES)) == n0 - 1, "Remove does not delete the line", sev="high")
    qa.data["cart_edit_supported"] = False
    qa.note("Cart has no 'edit line' action (no UI to reopen a line in the designer); stored _s state is unused - not tested further.")

    # ---------- small cart: shipping threshold + checkout
    page.evaluate("localStorage.removeItem('ad_cart')"); page.reload(); page.wait_for_selector("#app > *")
    qa.go(page, "#/checkout")
    qa.ok("checkout", page.evaluate("location.hash") == "#/cart", "Checkout with empty cart does not redirect to cart", actual=page.evaluate("location.hash"))
    qa.ok("cart_misc", T("Your cart is empty.") in page.inner_text("#app"), "Empty cart message missing")
    one = {"prod": "tee", "color": "Soft Pink", "slug": "soft-pink", "label": "Soft Pink", "size": "M", "qty": 1, "fo": "head_l", "bo": "none", "bf": "beagle", "bb": "beagle", "th": "geo", "st": "heart", "thb": "geo", "stb": "heart"}
    qa.go(page, "#/design?prod=tee&breed=beagle&theme=geo&style=heart&color=Soft%20Pink", wait="#pv svg")
    click("#ctl [data-k=front][data-opt='head_l']"); click("#ctl [data-k=back][data-opt='none']"); page.click("#add"); page.wait_for_timeout(100)
    _, sub1, ship1 = check_cart([one], "single tee")
    qa.ok("cart_totals", ship1 == SHIP["flat"], "Below-threshold cart not charged flat shipping", actual=ship1)
    page.locator("#lines .line [data-d='1']").click(); page.wait_for_timeout(100)
    page.locator("#lines .line [data-d='1']").click(); page.wait_for_timeout(100)
    one3 = dict(one, qty=3)
    _, sub3, ship3 = check_cart([one3], "tee x3 (over threshold)")
    # boundary just under threshold: hoodie both 2XL + ... use catalog math
    # checkout page
    qa.go(page, "#/checkout", wait="#co")
    rows = page.evaluate("[...document.querySelectorAll('.sum .r')].map(r=>[r.children[0].innerText,r.children[1].innerText])")
    exp_row = [f"3 × {P['tee']['name']} (Soft Pink, M)", money(sub3)]
    qa.ok("checkout", rows and rows[0] == exp_row, "Checkout summary line wrong", sev="high", expected=exp_row, actual=rows[:1])
    qa.ok("checkout", rows[-1][1] == money(sub3 + ship3), "Checkout total wrong", sev="high", expected=money(sub3 + ship3), actual=rows[-1])
    n0 = len(qa.api_calls)
    page.click("#pay"); page.wait_for_timeout(300)
    req = page.evaluate("[...document.querySelectorAll('#co [required]')].filter(e=>e.validity.valueMissing).map(e=>e.name)")
    qa.ok("checkout", not any(c["path"] == "/api/orders" for c in qa.api_calls[n0:]), "Empty checkout form submits an order", sev="critical")
    qa.ok("checkout", set(req) == {"email", "fn", "ln", "a1", "city", "st", "zip"}, "Checkout required fields wrong", expected=["email", "fn", "ln", "a1", "city", "st", "zip"], actual=req)
    stv = page.evaluate("document.querySelector('#co [name=st]').value")
    if stv:
        qa.defect("low", "checkout", "State dropdown is pre-filled with 'AL' instead of an empty 'Select state' option",
                  repro="#/checkout with any cart; leave State untouched", expected="State required with no default, so a customer cannot accidentally ship to Alabama", actual=f"default value '{stv}' passes validation")
    fill = {"email": "qa-test@example.com", "fn": "QA", "ln": "Tester", "a1": "123 Test Street", "city": "San Diego", "zip": "92101", "ph": "5555550100"}
    for k, v in fill.items():
        page.fill(f"#co [name={k}]", v)
    page.select_option("#co [name=st]", "CA")
    for z, okz in [("1234", False), ("92101-12", False), ("abcde", False), ("92101-1234", True), ("92101", True)]:
        page.fill("#co [name=zip]", z)
        qa.ok("checkout", page.evaluate("document.querySelector('#co [name=zip]').checkValidity()") == okz, f"ZIP '{z}' validity wrong", expected=okz)
    page.fill("#co [name=email]", "bad-email")
    qa.ok("checkout", not page.evaluate("document.querySelector('#co [name=email]').checkValidity()"), "Invalid email accepted at checkout")
    page.fill("#co [name=email]", fill["email"])
    # server error path
    qa.mock("POST", r"^/api/orders$", lambda r: (400, {"error": "Enter a valid US ZIP code"}, "application/json"))
    page.click("#pay"); page.wait_for_timeout(600)
    qa.ok("checkout", page.inner_text("#toast") == T("Enter a valid US ZIP code") and not page.evaluate("document.querySelector('#pay').disabled") and page.inner_text("#cartn") == "3",
          "Order API error not handled (toast / button re-enabled / cart kept)", sev="high", actual=(page.inner_text("#toast"), page.inner_text("#cartn")), page=page)
    # success path (no Stripe url -> reserved)
    qa.mock("POST", r"^/api/orders$", lambda r: (200, {"id": "QA-ORDER-1", "total": sub3 + ship3}, "application/json"))
    n0 = len(qa.api_calls)
    page.click("#pay"); page.wait_for_timeout(800)
    calls = [c for c in qa.api_calls[n0:] if c["path"] == "/api/orders"]
    if qa.ok("checkout", len(calls) == 1, "Pay does not post exactly one order", sev="critical", actual=len(calls)):
        o = calls[0]["body"]
        qa.data["order_payload_sample"] = o
        qa.ok("checkout", o["email"] == fill["email"] and o["ship"] == {"name": "QA Tester", "a1": "123 Test Street", "a2": "", "city": "San Diego", "st": "CA", "zip": "92101", "phone": "5555550100"},
              "Order payload contact/shipping wrong", sev="high", actual=o.get("ship"))
        qa.ok("checkout", o["subtotal"] == sub3 and o["shipping"] == ship3 and o["total"] == sub3 + ship3 and o["lang"] == "en", "Order payload totals wrong", sev="high", actual={k: o.get(k) for k in ("subtotal", "shipping", "total", "lang")})
        it = o["items"][0]
        qa.ok("checkout", len(o["items"]) == 1 and "_s" not in it and it["qty"] == 3 and it["front"] == {"part": "head", "size": "l", "breed": "beagle", "theme": "geo", "style": "heart"} and it["back"] is None and valid_item(cat, it),
              "Order payload item wrong / would be rejected by backend", sev="critical", actual=it)
    qa.ok("checkout", page.evaluate("location.hash") == "#/done/QA-ORDER-1" and page.inner_text("#cartn") == "0", "After order: no confirmation page or cart not cleared", sev="high", actual=(page.evaluate("location.hash"), page.inner_text("#cartn")), page=page)
    qa.ok("checkout", "QA-ORDER-1" in page.inner_text("#app"), "Confirmation page does not show the order id", sev="medium")
    qa.shot(page, "checkout_done_reserved")
    # paid confirmation page
    qa.mock("POST", r"^/api/orders/confirm$", lambda r: (200, {"status": "paid"}, "application/json"))
    qa.go(page, "#/done/QA-ORDER-1?paid=1")
    page.wait_for_timeout(600)
    qa.ok("checkout", T("Order {0} is paid and on its way to print. We will email you tracking when it ships.", "QA-ORDER-1") in page.inner_text("#app"), "Paid confirmation message not shown", sev="medium", actual=page.inner_text("#app")[:200])
    # Stripe redirect path (es, both sides, hoodie)
    page.select_option("#lang", "es"); qa.quiet(page)
    qa.go(page, "#/design?prod=hoodie&breed=pug&theme=line&style=cool", wait="#pv svg")
    click("#ctl [data-size='3XL']"); page.click("#add"); page.wait_for_timeout(100)
    qa.go(page, "#/checkout", wait="#co")
    for k, v in fill.items():
        page.fill(f"#co [name={k}]", v)
    page.select_option("#co [name=st]", "CA")
    qa.mock("POST", r"^/api/orders$", lambda r: (200, {"id": "QA-ORDER-2", "total": 1, "url": "https://checkout.stripe.com/c/pay/cs_test_QA"}, "application/json"))
    n0 = len(qa.api_calls)
    page.click("#pay")
    try:
        page.wait_for_url("https://checkout.stripe.com/**", timeout=8000)
        went = True
    except Exception:
        went = False
    qa.ok("checkout", went, "Checkout does not redirect to the Stripe URL returned by the API", sev="critical", actual=page.url)
    calls = [c for c in qa.api_calls[n0:] if c["path"] == "/api/orders"]
    if calls:
        o = calls[0]["body"]
        hp = price_cents(cat, "hoodie", 2, "3XL")
        qa.ok("checkout", o["lang"] == "es" and o["subtotal"] == hp and o["shipping"] == (0 if hp >= SHIP["free_over"] else SHIP["flat"]) and valid_item(cat, o["items"][0]), "Spanish hoodie order payload wrong", sev="high", actual=o)
    page.goto(BASE + "/#/cart"); page.wait_for_selector("#app > *")
    qa.ok("checkout", page.inner_text("#cartn") == "0", "Cart not cleared after redirect to Stripe", sev="medium", actual=page.inner_text("#cartn"))
    page.select_option("#lang", "en"); qa.quiet(page)

    # ---------- custom design flow (all API mocked)
    svg = ctx.request.get(BASE + "/art/line_classic/poodle_front.svg").text()
    svgb = ctx.request.get(BASE + "/art/line_classic/poodle_back.svg").text()
    qa.mock("POST", r"^/api/custom$", lambda r: (200, {"id": "QAC1", "k": "qak"}, "application/json"))
    qa.mock("GET", r"^/api/custom/QAC1$", lambda r: (200, {"status": "quoted", "art": ["head", "body"], "products": ["tee", "cap_dad"], "quote": 1999, "fee_due": 1999, "dog": {"name": "Rex"}, "note": "QA note"}, "application/json"))
    qa.mock("GET", r"^/api/custom/QAC1/art/head", lambda r: (200, svg, "image/svg+xml"))
    qa.mock("GET", r"^/api/custom/QAC1/art/body", lambda r: (200, svgb, "image/svg+xml"))
    qa.go(page, "#/custom", wait="#cuf")
    boxes = page.evaluate("[...document.querySelectorAll('#cuf input[name=prod]')].map(i=>i.value)")
    qa.ok("custom", sorted(boxes) == sorted(P), "Custom form product list differs from catalog", actual=boxes)
    qa.ok("custom", money(cat.get("custom_fee", 2499)) in page.inner_text("#app"), "Custom fee shown differs from catalog custom_fee", sev="medium", expected=money(cat.get("custom_fee", 2499)))
    n0 = len(qa.api_calls)
    page.click("#cus"); page.wait_for_timeout(200)
    qa.ok("custom", not any(c["path"] == "/api/custom" for c in qa.api_calls[n0:]) and not page.evaluate("document.querySelector('#cuf').checkValidity()"), "Custom form submits without name/email")
    page.fill("#cuf [name=name]", "QA Tester"); page.fill("#cuf [name=email]", "qa-test@example.com"); page.fill("#cuf [name=dname]", "Rex")
    page.click("#cus"); page.wait_for_timeout(200)
    qa.ok("custom", page.inner_text("#toast") == T("Please add at least 5 photos of your dog"), "Custom form: missing-photos warning not shown", actual=page.inner_text("#toast"))
    files = [{"name": f"dog{i}.png", "mimeType": "image/png", "buffer": png((40 * i, 120, 200 - 30 * i))} for i in range(6)]
    page.set_input_files("#pf", files[:3]); page.wait_for_timeout(600)
    qa.ok("custom", page.inner_text("#pc") == "3 / 5" and page.locator("#th .thumb").count() == 3, "Photo counter/thumbnails wrong after 3 uploads", actual=page.inner_text("#pc"))
    page.set_input_files("#pf", files[3:]); page.wait_for_timeout(600)
    page.locator("#th .thumb button").nth(0).click(); page.wait_for_timeout(100)
    qa.ok("custom", page.inner_text("#pc") == "5 / 5" and page.locator("#th .thumb").count() == 5, "Photo remove does not work", actual=page.inner_text("#pc"))
    page.click("#cus"); page.wait_for_timeout(200)
    qa.ok("custom", page.inner_text("#toast") == T("Choose at least one product"), "Custom form: no-product warning not shown", actual=page.inner_text("#toast"))
    page.check("#cuf input[value=tee]"); page.check("#cuf input[value=cap_dad]")
    page.select_option("#cuf [name=theme]", "geo")
    page.click("#cus"); page.wait_for_timeout(1500)
    c = [x for x in qa.api_calls[n0:] if x["path"] == "/api/custom" and x["m"] == "POST"]
    if qa.ok("custom", len(c) == 1, "Custom request not posted", sev="high"):
        b = c[0]["body"]
        qa.ok("custom", b["name"] == "QA Tester" and b["products"] == ["tee", "cap_dad"] and len(b["photos"]) == 5 and all(len(ph["b64"]) > 100 and ph["mime"] == "image/jpeg" for ph in b["photos"]) and b["style"]["theme"] == "geo" and b["dog"]["name"] == "Rex",
              "Custom request payload wrong", sev="high", actual={k: (v if k != "photos" else len(v)) for k, v in b.items()})
    page.wait_for_timeout(800)
    qa.ok("custom", page.evaluate("location.hash").startswith("#/custom/QAC1?k=qak"), "Custom submit does not open the status page", actual=page.evaluate("location.hash"))
    page.wait_for_selector("#cprev .card", timeout=8000)
    st = page.evaluate("({h1:document.querySelector('#app h1').innerText,on:document.querySelectorAll('.steps2 li.on').length,cards:[...document.querySelectorAll('#cprev .card')].map(c=>c.innerHTML.slice(0,600)),link:(document.querySelector('a[href^=\"#/design?custom=\"]')||{}).getAttribute?.('href'),txt:document.querySelector('#app').innerText})")
    qa.ok("custom", st["h1"] == T("Thank you! Request sent.") and st["on"] == 3 and len(st["cards"]) == 2 and all("api/custom/QAC1/art/head?k=qak" in x for x in st["cards"]) and "$19.99" in st["txt"] and "QA note" in st["txt"],
          "Custom status page (quoted) renders wrong", sev="medium", actual={k: v for k, v in st.items() if k != "cards"}, page=page)
    qa.shot(page, "custom_status_quoted")
    qa.ok("custom", st["link"] == "#/design?custom=QAC1&k=qak&prod=tee", "'Design your products' link wrong", actual=st["link"])
    page.click("a[href^='#/design?custom=']"); page.wait_for_selector("#pv svg image"); page.wait_for_timeout(500)
    s = page.evaluate("({notice:[...document.querySelectorAll('#ctl .notice')].map(n=>n.innerText),sel:document.querySelectorAll('#ctl select[data-k]').length,pv:document.querySelector('#pv').innerHTML,fo:document.querySelector('#ctl [data-k=front][data-opt].on')?.dataset.opt,bo:document.querySelector('#ctl [data-k=back][data-opt].on')?.dataset.opt})")
    qa.ok("custom", s["sel"] == 0 and s["notice"] and parse_svg(s["pv"])[1] == "api/custom/QAC1/art/head?k=qak" and (s["fo"], s["bo"]) == ("head_l", "body_l"), "Designer in custom mode wrong", sev="high", actual=s, page=page)
    page.click("#add"); page.wait_for_timeout(150)
    qa.go(page, "#/cart", wait="#lines")
    page.wait_for_timeout(500)
    ln = page.evaluate(LINES)[0]
    s2 = page.evaluate(SUM)
    tp = price_cents(cat, "tee", 2, "M")
    qa.ok("custom", ln["smalls"][1:] == [f"Front: {T('Your custom design')} · Big head", f"Back: {T('Your custom design')} · Big body"] or ln["smalls"][1].startswith("Front: Your custom design"), "Custom cart labels wrong", sev="medium", actual=ln["smalls"])
    qa.ok("custom", s2.get("Custom design (one-time)") == "$19.99" and s2.get("Total") == money(tp + (0 if tp >= SHIP["free_over"] else SHIP["flat"]) + 1999), "Custom design fee not added once in cart", sev="high", actual=s2, page=page)
    qa.shot(page, "cart_custom")
    page.evaluate("async()=>{for(const a of document.querySelectorAll('.wrap > .grid a.card')){a.scrollIntoView();await new Promise(r=>setTimeout(r,80))}}")
    page.wait_for_timeout(1200)
    look = page.evaluate("""async()=>{const cs=[...document.querySelectorAll('.wrap > .grid a.card')];const r=[];for(const a of cs){const u=[...a.querySelectorAll('img,image')].map(i=>i.getAttribute('src')||i.getAttribute('href'));
      const bad=[];await Promise.all(u.map(x=>new Promise(res=>{const im=new Image();im.onload=()=>{if(!im.naturalWidth)bad.push(x);res()};im.onerror=()=>{bad.push(x);res()};im.src=x})));r.push({href:a.getAttribute('href'),name:a.querySelector('.meta b').innerText,bad})}return r}""")
    badlook = [x for x in look if x["bad"] or "breed=custom" in x["href"]]
    if not qa.ok("custom", not badlook, "Cart 'Complete the look' shows broken 'custom' cards when the first cart line is a custom design", sev="medium",
                  repro="custom request status page -> 'Design your products' -> Add to cart -> #/cart, scroll to 'Complete the look'",
                  expected="suggestions for a real breed (or section hidden)", actual=badlook[:3]):
        page.locator(".wrap > .grid").scroll_into_view_if_needed()
        qa.shot(page, "cart_custom_complete_the_look_broken")
    qa.mock("POST", r"^/api/orders$", lambda r: (200, {"id": "QA-ORDER-3", "total": 1}, "application/json"))
    qa.go(page, "#/checkout", wait="#co")
    for k, v in fill.items():
        page.fill(f"#co [name={k}]", v)
    page.select_option("#co [name=st]", "CA")
    n0 = len(qa.api_calls)
    page.click("#pay"); page.wait_for_timeout(800)
    calls = [c for c in qa.api_calls[n0:] if c["path"] == "/api/orders"]
    if qa.ok("custom", len(calls) == 1, "Custom order not posted"):
        o = calls[0]["body"]
        qa.ok("custom", o.get("custom") == {"id": "QAC1", "k": "qak"} and o["total"] == tp + (0 if tp >= SHIP["free_over"] else SHIP["flat"]) + 1999 and valid_item(cat, o["items"][0], "QAC1"),
              "Custom order payload wrong", sev="high", actual=o)

    # ---------- saved designs (logged in, mocked)
    saved = []
    def post_design(r):
        saved.append(json.loads(r.post_data)); return (200, {"ok": True}, "application/json")
    qa.mock("POST", r"^/api/designs$", post_design)
    qa.mock("GET", r"^/api/designs$", lambda r: (200, {"items": saved}, "application/json"))
    qa.mock("GET", r"^/api/orders$", lambda r: (200, {"items": []}, "application/json"))
    qa.mock("DELETE", r"^/api/designs/", lambda r: (200, {"ok": True}, "application/json"))
    page.evaluate("localStorage.setItem('ad_user',JSON.stringify({email:'qa-test@example.com',token:'qa-fake'}))")
    page.reload(); page.wait_for_selector("#app > *")
    qa.go(page, "#/design?prod=hoodie&breed=shiba_inu&theme=geo&style=heart&color=Sand", wait="#pv svg")
    page.click("#save"); page.wait_for_timeout(500)
    qa.ok("saved_designs", len(saved) == 1 and saved[0]["s"]["prod"] == "hoodie" and saved[0]["s"]["front"]["breed"] == "shiba_inu" and page.inner_text("#toast") == T("Saved to your account"),
          "Save design (logged in) does not post the design", sev="medium", actual=(saved[:1], page.inner_text("#toast")))
    qa.go(page, "#/account", wait="#lo")
    page.wait_for_timeout(600)
    card = page.evaluate("(document.querySelector('[data-sd]')||{}).innerHTML||''")
    qa.ok("saved_designs", "img/hoodie_sand_front.webp" in card and "art/geo_heart/shiba_inu_front.svg" in card, "Saved design card preview wrong", sev="medium", actual=card[:300], page=page)
    if page.locator("[data-open]").count():
        page.click("[data-open]"); page.wait_for_selector("#pv svg image"); page.wait_for_timeout(300)
        s = page.evaluate("({prod:document.querySelector('#ctl [data-prod].on')?.dataset.prod,color:document.querySelector('#ctl .sw.on')?.dataset.color,b:document.querySelector('#ctl select[data-k=front]')?.value})")
        qa.ok("saved_designs", s == {"prod": "hoodie", "color": "Sand", "b": "shiba_inu"}, "Opening a saved design does not restore it", sev="medium", actual=s)
        qa.go(page, "#/account", wait="#lo"); page.wait_for_timeout(300)
        n0 = len(qa.api_calls)
        page.click("[data-del]"); page.wait_for_timeout(400)
        qa.ok("saved_designs", any(c["m"] == "DELETE" for c in qa.api_calls[n0:]), "Delete saved design sends no DELETE", sev="medium")
    # pending save across login
    page.click("#lo"); page.wait_for_timeout(200)
    qa.mock("POST", r"^/api/auth/request$", lambda r: (200, {"ok": True}, "application/json"))
    qa.mock("POST", r"^/api/auth/verify$", lambda r: (200, {"token": "qa-fake", "email": "qa-test@example.com"}, "application/json"))
    qa.go(page, "#/design?prod=tank&breed=boxer&theme=line&style=heart", wait="#pv svg")
    page.click("#save"); page.wait_for_timeout(300)
    page.fill("#lf input[name=email]", "qa-test@example.com"); page.locator("#lf button.btn").click()
    page.wait_for_selector("#lf input[name=code]"); page.fill("#lf input[name=code]", "123456"); page.locator("#lf button.btn").click()
    page.wait_for_timeout(1200)
    s = page.evaluate("({h:location.hash,prod:document.querySelector('#ctl [data-prod].on')?.dataset.prod,b:document.querySelector('#ctl select[data-k=front]')?.value})")
    qa.ok("saved_designs", s["h"] == "#/design" and s["prod"] == "tank" and s["b"] == "boxer" and saved and saved[-1]["s"]["prod"] == "tank", "Design pending save is lost across login", sev="medium", actual=s)
    ctx.close()


if __name__ == "__main__":
    run(cart_shard, "cart")
