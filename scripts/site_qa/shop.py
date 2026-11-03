"""Shard shop: every theme x style filter, search (every breed, en/es/pt, edge cases), every card (preview + link) and click-through to the designer."""
import re, os, sys, json, urllib.parse as up
sys.path.insert(0, os.path.dirname(__file__))
from common import *

PAINT = """async(sel)=>{for(let pass=0;pass<6;pass++){const un=[...document.querySelectorAll(sel)].filter(e=>!e.classList.contains('on'));if(!un.length)return 0;
  for(const e of un){e.scrollIntoView({block:'center'});await new Promise(r=>setTimeout(r,120))}await new Promise(r=>setTimeout(r,1500))}
  return [...document.querySelectorAll(sel)].filter(e=>!e.classList.contains('on')).length}"""
CARDS = """()=>[...document.querySelectorAll('#sg a.card')].map(a=>{const m=a.querySelector('.art');return {href:a.getAttribute('href'),b:m.dataset.b,t:m.dataset.t,s:m.dataset.s,on:m.classList.contains('on'),svg:m.innerHTML,img:(m.querySelector('img')||{}).getAttribute?.('src'),name:a.querySelector('.meta b').innerText,sub:a.querySelector('.meta span').innerText,aria:m.getAttribute('aria-label')}})"""
STATE = """()=>{const q=s=>document.querySelector(s);return {prod:q('#ctl [data-prod].on')?.dataset.prod,color:q('#ctl .sw.on')?.dataset.color,
  fo:q('#ctl [data-k=front][data-opt].on')?.dataset.opt,bo:q('#ctl [data-k=back][data-opt].on')?.dataset.opt,
  breedF:q('#ctl select[data-k=front]')?.value,breedB:q('#ctl select[data-k=back]')?.value,
  themeF:q('#ctl [data-k=front][data-f=theme].on')?.dataset.v,styleF:q('#ctl [data-k=front][data-f=style].on')?.dataset.v,
  themeB:q('#ctl [data-k=back][data-f=theme].on')?.dataset.v,styleB:q('#ctl [data-k=back][data-f=style].on')?.dataset.v,
  pv:q('#pv').innerHTML,price:q('#ctl .price')?.innerText,nbreeds:document.querySelectorAll('#ctl select[data-k=front] option').length}}"""


def shop_shard(qa, browser, p):
    ctx = qa.context(browser, viewport={"width": 1280, "height": 900})
    page = qa.watch(ctx.new_page())
    cat = catalog(ctx)
    B = [b["slug"] for b in cat["breeds"]]
    TH = [t["id"] for t in cat["themes"]]
    ST = [s["id"] for s in cat["styles"]]
    P = {x["id"]: x for x in cat["products"]}
    name = {b["slug"]: b["name"] for b in cat["breeds"]}
    tname = {t["id"]: t["name"] for t in cat["themes"]}
    sname = {s["id"]: s["name"] for s in cat["styles"]}
    qa.go(page, "#/shop", wait="#sg .card")

    def cards():
        return page.evaluate(CARDS)

    def chips():
        return page.evaluate("[(document.querySelector('#ft .chip.on')||{}).dataset?.t,(document.querySelector('#fs .chip.on')||{}).dataset?.s,!document.querySelector('#none').hidden]")

    # ---------- filters
    for ft in [""] + TH:
        for fs in [""] + ST:
            page.click(f"#ft .chip[data-t='{ft}']")
            page.click(f"#fs .chip[data-s='{fs}']")
            got = {(c["b"], c["t"], c["s"]) for c in cards()}
            n = len(cards())
            exp = {(b, t, s) for b in B for t in TH for s in ST if (not ft or t == ft) and (not fs or s == fs)}
            rep = f"#/shop, click theme chip '{ft or 'All styles'}' then mood chip '{fs or 'All moods'}'"
            qa.ok("shop_filters", got == exp and n == len(exp), f"Shop filter theme={ft or 'all'} style={fs or 'all'} shows wrong cards", repro=rep, expected=len(exp), actual=f"{n} cards, missing={list(exp-got)[:3]}, extra={list(got-exp)[:3]}", page=page)
            c = chips()
            qa.ok("shop_filters", c[0] == ft and c[1] == fs, "Shop filter chip highlight wrong", repro=rep, expected=[ft, fs], actual=c[:2])
    page.click("#ft .chip[data-t='']"); page.click("#fs .chip[data-s='']")
    # URL params
    for qs, ft, fs in [("theme=line", "line", ""), ("theme=geo", "geo", ""), ("style=heart", "", "heart"), ("theme=geo&style=cool", "geo", "cool"), ("theme=bogus", None, None), ("style=bogus", None, None)]:
        qa.go(page, f"#/shop?{qs}")
        n = len(cards())
        c = chips()
        if ft is None:
            qa.ok("shop_filters", n > 0, f"Shop with invalid URL filter (?{qs}) shows zero designs and no active chip", sev="low",
                  repro=f"open {BASE}/#/shop?{qs}", expected="ignore unknown filter and show all designs", actual=f"{n} cards, chips on={c[:2]}, 'no designs' message shown={c[2]}", page=page)
        else:
            exp = len(B) * (1 if ft else len(TH)) * (1 if fs else len(ST))
            qa.ok("shop_filters", n == exp and c[0] == ft and c[1] == fs, f"Shop URL filter ?{qs} wrong", expected=exp, actual=[n, c])
    qa.go(page, "#/shop", wait="#sg .card")

    # ---------- search
    def search(q):
        page.fill("#sq", q)
        page.wait_for_timeout(30)
        return {(c["b"], c["t"], c["s"]) for c in cards()}, chips()[2]
    for b in B:
        q = name[b]
        got, none = search(q)
        expb = {x for x in B if q.lower().strip() in name[x].lower()}
        exp = {(x, t, s) for x in expb for t in TH for s in ST}
        qa.ok("shop_search", got == exp, f"Search '{q}' returns wrong breeds", repro=f"#/shop, type '{q}' in search", expected=sorted(expb), actual=sorted({g[0] for g in got}), page=page)
    for q, expf in [("POODLE", lambda n: "poodle" in n.lower()), ("  pug  ", lambda n: "pug" in n.lower()), ("pood", lambda n: "pood" in n.lower()),
                    ("retriever", lambda n: "retriever" in n.lower()), ("", lambda n: True), ("zzqx-no-such-dog", lambda n: False), ("<script>", lambda n: False), ("terrier", lambda n: "terrier" in n.lower())]:
        got, none = search(q)
        expb = {x for x in B if expf(name[x])}
        qa.ok("shop_search", {g[0] for g in got} == expb and none == (not expb), f"Search '{q}' wrong", repro=f"#/shop, type '{q}'", expected=sorted(expb), actual=[sorted({g[0] for g in got}), "none-msg" if none else ""], page=page)
    # search + filter combination
    search("poodle")
    page.click("#ft .chip[data-t='geo']"); page.click("#fs .chip[data-s='heart']")
    got = {(c["b"], c["t"], c["s"]) for c in cards()}
    expb = {x for x in B if "poodle" in name[x].lower()}
    qa.ok("shop_search", got == {(x, "geo", "heart") for x in expb}, "Search + filter combination wrong", actual=sorted(got))
    page.click("#ft .chip[data-t='']"); page.click("#fs .chip[data-s='']"); search("")
    # translated names
    for l in ("es", "pt"):
        page.select_option("#lang", l); qa.quiet(page)
        qa.go(page, "#/shop", wait="#sg .card")
        tn = page.evaluate("async(n)=>{const m=await import('./js/i18n.js');return n.map(x=>m.tn(x))}", [name[b] for b in B])
        diff = 0
        for b, tname_l in zip(B, tn):
            got, _ = search(tname_l)
            qa.ok("shop_search", b in {g[0] for g in got}, f"Search by {l} breed name '{tname_l}' does not find {b}", repro=f"language {l}, #/shop, search '{tname_l}'", actual=sorted({g[0] for g in got})[:5])
            diff += tname_l != name[b]
            got, _ = search(name[b])
            qa.ok("shop_search", b in {g[0] for g in got}, f"Search by English breed name fails in {l}", actual=name[b])
        qa.data[f"translated_breed_names_{l}"] = diff
        search("")
        sub = page.evaluate("document.querySelector('#sg a.card .meta span').innerText")
        qa.data[f"card_subtitle_{l}"] = sub
    page.select_option("#lang", "en"); qa.quiet(page)

    # ---------- every card: preview + link
    qa.go(page, "#/shop", wait="#sg .card")
    page.evaluate("""async()=>{for(const a of document.querySelectorAll('#sg a.card')){a.scrollIntoView();await new Promise(r=>setTimeout(r,25))}window.scrollTo(0,0)}""")
    left = page.evaluate(PAINT, "#sg .art.mock")
    qa.ok("shop_cards", left == 0, "Some shop cards never render their garment mockup even when scrolled into view", sev="medium", repro="#/shop, scroll each card into view", actual=f"{left} unpainted")
    qa.quiet(page, 800, 30000)
    cs = cards()
    combos = {(c["b"], c["t"], c["s"]) for c in cs}
    qa.ok("shop_cards", len(cs) == len(B) * len(TH) * len(ST) and len(combos) == len(cs), "Shop does not list every breed x theme x style exactly once", actual=f"{len(cs)} cards, {len(combos)} unique")
    broken = page.evaluate("""async()=>{const urls=[...new Set([...document.querySelectorAll('#sg svg image')].map(i=>i.getAttribute('href')))];const bad=[];
      await Promise.all(urls.map(u=>new Promise(r=>{const im=new Image();im.onload=()=>{if(!im.naturalWidth)bad.push(u);r()};im.onerror=()=>{bad.push(u);r()};im.src=u})));return [urls.length,bad]}""")
    qa.data["shop_unique_images"] = broken[0]
    qa.ok("shop_cards", not broken[1], "Shop card images fail to load", sev="high", repro="#/shop, scroll through all cards", actual=broken[1][:20], page=page)
    used = {}
    for i, c in enumerate(cs):
        q = dict(up.parse_qsl(c["href"].split("?", 1)[1]))
        rep = f"#/shop card #{i+1} ({c['name']} {c['sub']})"
        qa.ok("shop_cards", q.get("breed") == c["b"] and q.get("theme") == c["t"] and q.get("style") == c["s"], "Shop card link breed/theme/style differs from card art", repro=rep, expected=(c["b"], c["t"], c["s"]), actual=c["href"])
        qa.ok("shop_cards", c["name"] == name[c["b"]] and c["sub"].startswith(f"{tname[c['t']]} · {sname[c['s']]}"), "Shop card label wrong", repro=rep, expected=f"{name[c['b']]} / {tname[c['t']]} · {sname[c['s']]}", actual=f"{c['name']} / {c['sub']}")
        pid = q.get("prod")
        prod = P.get(pid)
        if not qa.ok("shop_cards", prod is not None, "Shop card links an unknown product", repro=rep, actual=pid):
            continue
        qa.ok("shop_cards", c["sub"].endswith(prod["name"]), "Shop card subtitle product differs from link product", repro=rep, expected=prod["name"], actual=c["sub"])
        col = next((x for x in prod["colors"] if x[0] == q.get("color")), None)
        qa.ok("shop_cards", col is not None and col[2] == 1, "Shop card links a disabled/unknown color", repro=rep, actual=q.get("color"))
        ph, art, rect = parse_svg(c["svg"])
        part = q.get("part", "head")
        exp_art = f"art/{c['t']}_{c['s']}/{c['b']}_{'front' if part == 'head' else 'back'}.svg"
        qa.ok("shop_cards", art == exp_art, "Shop card preview art differs from its breed/theme/style/part", sev="high", repro=rep, expected=exp_art, actual=art, page=page)
        qa.ok("shop_cards", col is not None and ph == f"img/{pid}_{col[3]}_front.webp", "Shop card garment photo differs from linked product/color", sev="medium", repro=rep, expected=f"img/{pid}_{col[3] if col else '?'}_front.webp", actual=ph)
        used[(pid, q.get("color"))] = used.get((pid, q.get("color")), 0) + 1
        c["q"] = q
        c["rect"] = rect
        c["art"] = art
        c["ph"] = ph
    qa.data["shop_card_product_color_mix"] = {f"{k[0]}|{k[1]}": v for k, v in sorted(used.items())}
    qa.shot(page, "shop_all", quality=45)
    # same product+color on adjacent cards
    adj = sum(1 for a, b in zip(cs, cs[1:]) if a.get("q") and b.get("q") and a["q"].get("prod") == b["q"].get("prod") and a["q"].get("color") == b["q"].get("color"))
    qa.data["adjacent_same_garment_color"] = adj

    # real clicks on first cards
    for i in range(6):
        qa.go(page, "#/shop", wait="#sg .card")
        href = page.locator("#sg a.card").nth(i).get_attribute("href")
        page.locator("#sg a.card").nth(i).click()
        page.wait_for_selector("#pv svg")
        qa.ok("shop_cards", page.evaluate("location.hash") == href, "Clicking a shop card does not open its design link", expected=href, actual=page.evaluate("location.hash"))

    # click-through every card -> designer state must match
    for i, c in enumerate(cs):
        if "q" not in c:
            continue
        q = c["q"]
        qa.go(page, c["href"], wait="#pv svg image", quiet=False)
        try:
            page.wait_for_function("document.querySelectorAll('#pv svg image').length>=2", timeout=5000)
        except Exception:
            pass
        s = page.evaluate(STATE)
        prod = P[q["prod"]]
        small = prod.get("rule") in ("chest", "cap")
        exp_fo = ("body" if q.get("part") == "body" else "head") + ("_s" if small else "_l")
        rep = f"open {BASE}/{c['href']} (from shop card {c['name']} {c['sub']})"
        exp = {"prod": q["prod"], "color": q["color"], "fo": exp_fo, "breedF": c["b"], "themeF": c["t"], "styleF": c["s"]}
        act = {k: s.get(k) for k in exp}
        qa.ok("card_to_designer", act == exp, "Designer state differs from the shop card that opened it", sev="high", repro=rep, expected=exp, actual=act, page=page)
        ph, art, rect = parse_svg(s["pv"])
        qa.ok("card_to_designer", (ph, art) == (c["ph"], c["art"]), "Designer preview differs from shop card preview", sev="high", repro=rep, expected=(c["ph"], c["art"]), actual=(ph, art), page=page)
        if rect and c["rect"]:
            qa.ok("card_to_designer", all(abs(a - b) < 1.5 for a, b in zip(rect, c["rect"])), "Designer art placement differs from shop card mockup", sev="low", repro=rep, expected=c["rect"], actual=rect)
        if "back" in sides_of(cat, q["prod"]):
            qa.ok("card_to_designer", s["breedB"] == c["b"] and s["themeB"] == c["t"] and s["styleB"] == c["s"], "Designer back side does not inherit card breed/theme/style", sev="low", repro=rep, expected=(c["b"], c["t"], c["s"]), actual=(s["breedB"], s["themeB"], s["styleB"]))
        qa.ok("card_to_designer", s["nbreeds"] == len(B), "Designer breed dropdown count wrong", actual=s["nbreeds"])
    qa.data["cards_clicked_through"] = len(cs)
    ctx.close()


if __name__ == "__main__":
    run(shop_shard, "shop")
