"""Shard nav: routes, links, pages x 3 languages, 404, forms (mocked), login flow, home widgets, mobile pass, deploy drift."""
import re, os, hashlib, json, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import *

TOK = re.compile(r"\bundefined\b|\bNaN\b|\{\d\}|\[object Object\]|\bnull\b")
PROBE = """()=>{const app=document.querySelector('#app');
 const broken=[...document.images].filter(i=>i.complete&&i.naturalWidth===0&&i.getAttribute('src')).map(i=>i.getAttribute('src'));
 const vis=e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0};
 return {hash:location.hash,title:document.title,h1:(app.querySelector('h1')||{}).innerText||'',text:app.innerText,
  chrome:(document.querySelector('header').innerText+'\\n'+document.querySelector('footer').innerText+'\\n'+document.querySelector('#promo').innerText),
  broken,overflow:document.documentElement.scrollWidth-window.innerWidth,
  links:[...document.querySelectorAll('a[href]')].filter(vis).map(a=>({href:a.getAttribute('href'),text:a.innerText.trim().slice(0,50),where:a.closest('#app')?'app':a.closest('header')?'header':'footer'}))}}"""


def scroll_all(page):
    page.evaluate("""async()=>{const H=()=>document.documentElement.scrollHeight;for(let y=0;y<H();y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,60))}window.scrollTo(0,0)}""")


def T(page, s, *a):
    return page.evaluate("async([s,a])=>(await import('./js/i18n.js')).t(s,...a)", [s, list(a)])


def nav_shard(qa, browser, p):
    ctx = qa.context(browser, viewport={"width": 1280, "height": 800})
    page = qa.watch(ctx.new_page())
    cat = catalog(ctx)
    qa.data["catalog_counts"] = {"breeds": len(cat["breeds"]), "themes": len(cat["themes"]), "styles": len(cat["styles"]), "products": len(cat["products"])}

    # ---------- deploy drift (live files vs repo main)
    repo = os.environ.get("QA_REPO", ".")
    drift = {}
    for f in ["index.html", "js/app.js", "js/garment.js", "js/placement.js", "js/i18n.js", "js/pages.js", "data/catalog.json", "css/style.css"]:
        r = ctx.request.get(f"{BASE}/{f}")
        live = hashlib.sha1(r.body()).hexdigest() if r.ok else f"HTTP {r.status}"
        try:
            loc = hashlib.sha1(open(f"{repo}/store/{f}", "rb").read()).hexdigest()
        except Exception:
            loc = "missing"
        drift[f] = {"same": live == loc, "live": live[:10], "repo": loc[:10]}
    qa.data["deploy_drift"] = drift
    qa.ok("deploy", all(v["same"] for v in drift.values()), "Live site files differ from repo main (deploy drift)", sev="info",
          expected="live == repo store/", actual=json.dumps({k: v for k, v in drift.items() if not v["same"]}))

    health = ctx.request.get(BASE + "/api/health")
    qa.data["health"] = health.json() if health.ok else health.status

    qa.mock("GET", r"^/api/custom/QA-NOPE", lambda r: (404, {"error": "Not found"}, "application/json"))
    qa.go(page, "#/")
    pages = page.evaluate("async()=>Object.fromEntries(Object.entries((await import('./js/pages.js')).PAGES).map(([l,v])=>[l,Object.keys(v)]))")
    qa.data["page_ids"] = pages
    langs = ["en", "es", "pt"]
    for l in langs:
        qa.ok("i18n", sorted(pages.get(l, [])) == sorted(pages["en"]), f"Static page set differs in '{l}'", expected=pages["en"], actual=pages.get(l))

    routes = [("#/", None), ("#/shop", None), ("#/shop?theme=line", None), ("#/shop?theme=geo", None), ("#/shop?style=heart", None),
              ("#/design", None), ("#/cart", None), ("#/checkout", "#/cart"), ("#/custom", None), ("#/login", None),
              ("#/account", "#/login"), ("#/admin", None), ("#/done/QA-TEST-ORDER", None), ("#/custom/QA-NOPE?k=x", None)]
    routes += [(f"#/page/{pid}", None) for pid in pages["en"]]
    not_found = [("#/page/does-not-exist", None), ("#/no-such-route", None)]
    seen_text = {}
    all_links = {}
    for l in langs:
        qa.go(page, "#/")
        page.select_option("#lang", l)
        qa.quiet(page)
        qa.ok("i18n", page.evaluate("document.documentElement.lang") == ("pt-BR" if l == "pt" else l), f"<html lang> not updated for {l}")
        lost = T(page, "Lost dog?")
        for h, redirect in routes + not_found:
            m = qa.mark()
            qa.go(page, h)
            scroll_all(page)
            qa.quiet(page, 300)
            r = page.evaluate(PROBE)
            area = f"routes_{l}"
            rep = f"open {BASE}/{h} (language {l})"
            if redirect:
                qa.ok(area, r["hash"] == redirect, f"{h} should redirect to {redirect}", repro=rep, expected=redirect, actual=r["hash"], page=page)
            is404 = (h, None) in not_found
            if h.startswith("#/custom/QA-NOPE"):
                qa.ok(area, T(page, "We could not find that request. Check the link in your email.") in r["text"], "Unknown custom-request link does not show the 'could not find' message", repro=rep, actual=r["text"][:200], page=page)
            elif is404:
                qa.ok(area, r["h1"].strip() == lost, f"Unknown route {h} does not show the 404 page", repro=rep, expected=lost, actual=r["h1"], page=page)
            elif True:
                qa.ok(area, r["h1"].strip() != lost, f"Route {h} renders the 404 page", repro=rep, actual=r["h1"], page=page)
            qa.ok(area, len(r["text"].strip()) > 20, f"Route {h} renders empty", repro=rep, page=page)
            bad = TOK.findall(r["text"] + "\n" + r["title"] + "\n" + r["chrome"])
            qa.ok(area, not bad, f"Placeholder/undefined text on {h.split('?')[0]} ({l})", sev="medium", repro=rep, expected="no undefined/NaN/{0}", actual=bad, page=page)
            qa.ok(area, not r["broken"], f"Broken images on {h.split('?')[0]}", sev="high", repro=rep, actual=r["broken"], page=page)
            qa.ok(area, r["overflow"] <= 1, f"Horizontal overflow on {h.split('?')[0]} (desktop)", sev="low", repro=rep, actual=f"{r['overflow']}px", page=page)
            e = qa.errs_since(m)
            pe = e["pageerror"]
            qa.ok(area, not pe, f"JavaScript error on {h.split('?')[0]}", sev="high", repro=rep, actual=pe[:3], page=page)
            http = [x for x in e["http"] if "QA-NOPE" not in x["url"]]
            qa.ok(area, not http, f"HTTP 4xx/5xx while loading {h.split('?')[0]}", sev="medium", repro=rep, actual=http[:5])
            if l == "en":
                seen_text[h] = set(x.strip() for x in (r["text"] + "\n" + r["chrome"]).split("\n") if x.strip())
                for ln in r["links"]:
                    all_links.setdefault(ln["href"], {"text": ln["text"], "from": h, "where": ln["where"]})
            elif h in seen_text:
                same = [x for x in set(x.strip() for x in (r["text"] + "\n" + r["chrome"]).split("\n") if x.strip()) & seen_text[h]
                        if re.search(r"[a-z]{4,}", x) and not re.search(r"@|AlphaDog|^\$|Bella|Gildan|Yupoong|JERZEES|OTTO|Next Level|CORE365|Stripe", x)]
                if same:
                    qa.data.setdefault("possibly_untranslated", {}).setdefault(l, {})[h] = sorted(same)[:40]
            name = re.sub(r"\W+", "_", h.strip("#/")) or "home"
            if l == "en" or h in ("#/", "#/shop", "#/design", "#/page/faq", "#/custom"):
                qa.shot(page, f"{l}_{name}", quality=45)
        miss = [k for k in page.evaluate("[...window.__missing]") if not re.fullmatch(r"\d+|Not found|That code is not right|Enter a valid email", k)]
        if any(re.fullmatch(r"\d+", k) for k in page.evaluate("[...window.__missing]")):
            qa.data["data_i_collision"] = True
            qa.defect("info", "i18n", "Language switch runs translation over design cards: their data-i index attribute collides with the i18n data-i hook (card art briefly replaced by digits until the page re-renders; digits logged as missing keys)",
                      repro="open #/shop or #/ and change the footer language selector", expected="only [data-i] text nodes from index.html translated", actual="applyStatic() sets textContent of every [data-i] element incl. .art.mock cards")
        qa.data.setdefault("i18n_missing_keys", {})[l] = miss
        if l != "en":
            qa.ok("i18n", not miss, f"Untranslated UI strings in {l} (t() keys with no {l} entry)", sev="medium",
                  repro=f"switch language to {l}, visit all routes", expected="0 missing", actual=miss[:30])
    page.select_option("#lang", "en")
    qa.quiet(page)

    # ---------- link crawl: every unique link found on any page
    qa.data["links_found"] = len(all_links)
    lost = T(page, "Lost dog?")
    for href, info in sorted(all_links.items()):
        if href.startswith("#/"):
            m = qa.mark()
            qa.go(page, href)
            h1 = page.evaluate("(document.querySelector('#app h1')||{}).innerText||''")
            qa.ok("links", h1.strip() != lost, f"Link '{info['text']}' ({href}) leads to 404", sev="high",
                  repro=f"on {info['from']} click '{info['text']}'", actual=h1, page=page)
            pe = qa.errs_since(m)["pageerror"]
            qa.ok("links", not pe, f"JS error after following link {href}", sev="high", actual=pe[:2], page=page)
        elif href.startswith("mailto:"):
            qa.ok("links", re.match(r"mailto:[\w.+-]+@[\w-]+\.[\w.]+$", href) is not None, f"Malformed mailto {href}")
        elif href.startswith("/api/"):
            qa.note(f"API link not followed (would start OAuth): {href}")
        elif href.startswith("http"):
            try:
                rr = ctx.request.get(href, timeout=15000)
                qa.ok("links", rr.status < 400, f"External link {href} returns {rr.status}", sev="medium")
            except Exception as ex:
                qa.ok("links", False, f"External link {href} unreachable", actual=str(ex)[:200])
        else:
            qa.ok("links", False, f"Unexpected link format {href}", sev="low", repro=f"found on {info['from']}")

    # real clicks on header + footer links
    qa.go(page, "#/")
    hdr = page.evaluate("[...document.querySelectorAll('header a[href^=\"#\"],footer a[href^=\"#\"]')].map((a,i)=>[i,a.getAttribute('href'),a.innerText.trim()])")
    for i, href, txt in hdr:
        qa.go(page, "#/")
        loc = page.locator('header a[href^="#"],footer a[href^="#"]').nth(i)
        loc.click()
        page.wait_for_timeout(250)
        qa.quiet(page, 250)
        hh = page.evaluate("location.hash")
        exp = href.split("?")[0] if href != "#/" else "#/"
        if href == "#/account" and hh == "#/login":
            exp = "#/login"  # logged out: account redirects to login (expected)
        qa.ok("clicks", hh.split("?")[0] == exp or (href == "#/" and hh in ("", "#/")), f"Clicking '{txt}' does not navigate to {href}", repro=f"home, click '{txt}'", expected=href, actual=hh, page=page)
        if href.startswith("#/shop?theme="):
            th = href.split("=")[1]
            on = page.evaluate("(document.querySelector('#ft .chip.on')||{}).dataset?.t")
            qa.ok("clicks", on == th, f"Footer link {href} does not preselect theme chip", expected=th, actual=on, page=page)
        active = page.evaluate("[...document.querySelectorAll('#links a.on')].map(a=>a.getAttribute('href'))")
        if href in ("#/shop", "#/design", "#/page/about", "#/page/faq"):
            # nav highlight logic compares only first path segment
            pass
    qa.data["header_footer_clicks"] = len(hdr)

    # ---------- newsletter (mocked)
    qa.go(page, "#/")
    inp = page.locator("#news input")
    inp.fill("not-an-email")
    qa.ok("forms", page.evaluate("document.querySelector('#news').checkValidity()") is False, "Newsletter accepts an invalid email client-side")
    n0 = len(qa.api_calls)
    page.locator("#news button").click()
    page.wait_for_timeout(300)
    qa.ok("forms", not any(c["path"] == "/api/subscribe" for c in qa.api_calls[n0:]), "Newsletter posts an invalid email")
    inp.fill("qa-test@example.com")
    page.locator("#news button").click()
    page.wait_for_timeout(600)
    sub = [c for c in qa.api_calls[n0:] if c["path"] == "/api/subscribe"]
    qa.ok("forms", len(sub) == 1 and sub[0]["body"].get("email") == "qa-test@example.com" and sub[0]["body"].get("lang") == "en",
          "Newsletter submit does not send {email,lang}", actual=sub)
    toast = page.evaluate("document.querySelector('#toast').innerText")
    qa.ok("forms", toast == T(page, "You're in the pack!"), "Newsletter success toast wrong", actual=toast, page=page)
    qa.ok("forms", inp.input_value() == "", "Newsletter input not cleared after success")
    qa.mock("POST", r"^/api/subscribe$", lambda r: (400, {"error": "Enter a valid email"}, "application/json"))
    inp.fill("qa-test2@example.com")
    page.locator("#news button").click()
    page.wait_for_timeout(600)
    toast = page.evaluate("document.querySelector('#toast').innerText")
    qa.ok("forms", toast == "Enter a valid email", "Newsletter server error not surfaced to user", actual=toast)

    # ---------- contact form (mocked)
    qa.go(page, "#/page/contact")
    has = page.locator("#cf").count()
    if qa.ok("forms", has == 1, "Contact page has no form #cf", page=page):
        qa.ok("forms", page.evaluate("document.querySelector('#cf').checkValidity()") is False, "Contact form valid while empty")
        page.fill("#cf input[name=email]", "qa-test@example.com")
        page.fill("#cf textarea[name=msg]", "QA automated test message - please ignore")
        n0 = len(qa.api_calls)
        page.locator("#cf button").click()
        page.wait_for_timeout(600)
        c = [x for x in qa.api_calls[n0:] if x["path"] == "/api/contact"]
        qa.ok("forms", len(c) == 1 and c[0]["body"].get("msg") and c[0]["body"].get("lang") == "en", "Contact submit payload wrong", actual=c)
        qa.ok("forms", "Thanks" in page.inner_text("#app"), "Contact form shows no thank-you after submit", page=page)
    for l in ("es", "pt"):
        page.select_option("#lang", l); qa.quiet(page)
        qa.go(page, "#/page/contact")
        qa.ok("forms", page.locator("#cf").count() == 1, f"Contact form missing in {l}", page=page)
        lab = page.evaluate("[...document.querySelectorAll('#cf label, #cf button')].map(e=>e.childNodes[0].textContent.trim())")
        qa.ok("i18n", not any(x in ("Your email", "Message", "Send") for x in lab), f"Contact form labels untranslated in {l}", sev="low", actual=lab, page=page)
    page.select_option("#lang", "en"); qa.quiet(page)

    # ---------- login flow (mocked backend)
    qa.mock("POST", r"^/api/auth/request$", lambda r: (200, {"ok": True}, "application/json"))
    def verify(r):
        b = json.loads(r.post_data or "{}")
        return (200, {"token": "qa-fake-token", "email": b.get("email")}, "application/json") if b.get("code") == "123456" else (400, {"error": "That code is not right"}, "application/json")
    qa.mock("POST", r"^/api/auth/verify$", verify)
    qa.mock("GET", r"^/api/designs$", lambda r: (200, {"items": []}, "application/json"))
    qa.mock("GET", r"^/api/orders$", lambda r: (200, {"items": [{"id": "AD-QA01", "status": "shipped", "total": 3298, "tracking": "https://example.com/track"}]}, "application/json"))
    qa.go(page, "#/login")
    qa.data["social_login_buttons"] = page.evaluate("[...document.querySelectorAll('.socials a')].map(a=>a.getAttribute('href'))")
    page.fill("#lf input[name=email]", "qa-test@example.com")
    page.locator("#lf button.btn").click()
    ok2 = True
    try:
        page.wait_for_selector("#lf input[name=code]", timeout=5000)
    except Exception:
        ok2 = False
    qa.ok("login", ok2, "Login step 2 (code entry) never appears", page=page)
    if ok2:
        page.click("#back")
        qa.ok("login", page.input_value("#lf input[name=email]") == "qa-test@example.com", "'Use a different email' loses the typed email")
        page.locator("#lf button.btn").click()
        page.wait_for_selector("#lf input[name=code]")
        page.fill("#lf input[name=code]", "12")
        qa.ok("login", page.evaluate("document.querySelector('#lf').checkValidity()") is False, "Code field accepts 2 digits")
        page.fill("#lf input[name=code]", "000000")
        page.locator("#lf button.btn").click()
        page.wait_for_timeout(500)
        qa.ok("login", page.inner_text("#toast") == T(page, "That code is not right") or "not right" in page.inner_text("#toast"), "Wrong code error not shown", actual=page.inner_text("#toast"))
        page.fill("#lf input[name=code]", "123456")
        page.locator("#lf button.btn").click()
        page.wait_for_timeout(800)
        qa.quiet(page)
        qa.ok("login", page.evaluate("location.hash") == "#/account", "Successful login does not land on account", actual=page.evaluate("location.hash"), page=page)
        txt = page.inner_text("#app")
        qa.ok("login", "qa-test@example.com" in txt and "AD-QA01" in txt and "$32.98" in txt, "Account page does not show email/orders", actual=txt[:300], page=page)
        qa.ok("login", page.locator("#app a[href='https://example.com/track']").count() == 1, "Order tracking link missing on account")
        qa.shot(page, "en_account_logged_in")
        page.click("#lo")
        page.wait_for_timeout(300)
        qa.ok("login", page.evaluate("location.hash") in ("#/", "") and page.evaluate("localStorage.getItem('ad_user')") == "null", "Logout does not clear user", actual=page.evaluate("localStorage.getItem('ad_user')"))
    # magic link route
    qa.go(page, "#/auth?email=qa-test@example.com&token=qa-fake&next=shop")
    page.wait_for_timeout(500)
    qa.ok("login", page.evaluate("location.hash").startswith("#/shop") and "qa-fake" in (page.evaluate("localStorage.getItem('ad_user')") or ""), "#/auth magic link does not log in / redirect", actual=page.evaluate("location.hash"))
    qa.go(page, "#/auth?email=qa-test@example.com&token=qa-fake&next=https://evil.example")
    page.wait_for_timeout(500)
    qa.ok("login", page.evaluate("location.hash") == "#/account", "#/auth open-redirect check: external next= not rejected", sev="high", actual=page.evaluate("location.hash"))
    qa.go(page, "#/account", wait="#lo"); page.click("#lo"); page.wait_for_timeout(300)

    # ---------- admin: only confirm it asks for a token
    n0 = len(qa.api_calls)
    page.evaluate("localStorage.removeItem('ad_admin')")
    qa.go(page, "#/admin")
    qa.ok("admin", page.locator("#at input[type=password]").count() == 1, "Admin page does not ask for a token", sev="high", page=page)
    qa.ok("admin", not any("/api/internal" in c["path"] for c in qa.api_calls[n0:]), "Admin page calls internal API without a token", sev="high")

    # ---------- home widgets
    qa.go(page, "#/")
    page.mouse.move(5, 790)
    left = page.evaluate("""async(sel)=>{for(let pass=0;pass<6;pass++){const un=[...document.querySelectorAll(sel)].filter(e=>!e.classList.contains('on'));if(!un.length)return 0;
  for(const e of un){e.scrollIntoView({block:'center'});await new Promise(r=>setTimeout(r,120))}await new Promise(r=>setTimeout(r,1500))}
  return [...document.querySelectorAll(sel)].filter(e=>!e.classList.contains('on')).length}""", ".sec .grid .art.mock")
    qa.ok("home", left == 0, "Home featured cards never render their mockup even when scrolled into view", sev="medium", actual=f"{left} unpainted", page=page)
    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(1500)
    qa.quiet(page)
    home = page.evaluate("""()=>({hero:document.querySelector('.hero p').innerText,seeall:[...document.querySelectorAll('.sec .sh a')].map(a=>a.innerText),
      cards:[...document.querySelectorAll('.sec .grid a.card')].map(a=>({href:a.getAttribute('href'),svg:a.querySelector('.art').innerHTML,meta:a.querySelector('.meta').innerText})),
      marquee:document.querySelectorAll('.marquee em').length, slides:[...document.querySelectorAll('#stage .slide')].map(s=>[s.getAttribute('aria-label'),s.innerHTML]),
      looks:[...document.querySelectorAll('.look .lk')].map(a=>[a.className,a.innerHTML.slice(0,400)])})""")
    nb, nt, ns = len(cat["breeds"]), len(cat["themes"]), len(cat["styles"])
    nums = re.findall(r"\d+", home["hero"])
    qa.ok("home", nums[:3] == [str(nb), str(nt), str(ns)], "Home hero counts don't match catalog", sev="low", expected=f"{nb} breeds, {nt} art styles, {ns} moods", actual=home["hero"])
    qa.ok("home", any(str(nb * nt * ns) in s for s in home["seeall"]), "'See all N designs' count doesn't match catalog", sev="low", expected=nb * nt * ns, actual=home["seeall"])
    qa.ok("home", len(home["cards"]) == 8, "Home should show 8 featured cards", actual=len(home["cards"]))
    for c in home["cards"]:
        q = dict(up.parse_qsl(c["href"].split("?", 1)[1]))
        ph, art, _ = parse_svg(c["svg"])
        qa.ok("home", art and f"art/{q['theme']}_{q['style']}/{q['breed']}_" in art and ph == f"img/{q['prod']}_{next(x for x in next(p for p in cat['products'] if p['id']==q['prod'])['colors'] if x[0]==q['color'])[3]}_front.webp",
              "Home featured card preview doesn't match its link", repro="home page featured grid", expected=c["href"], actual=f"{ph} {art}", page=page)
    qa.ok("home", home["marquee"] == 2 * nb, "Breed marquee count off", sev="low", expected=2 * nb, actual=home["marquee"])
    qa.ok("home", len(home["slides"]) >= 1 and parse_svg(home["slides"][-1][1])[1], "Hero carousel shows no product mockup", sev="medium", actual=home["slides"][:1], page=page)
    qa.ok("home", len(home["looks"]) == 6 and all("mk" in x[0] and "<svg" in x[1] for x in home["looks"]), "'Real garments' strip not rendered as mockups", sev="low", actual=[x[0] for x in home["looks"]], page=page)
    page.mouse.move(5, 790)
    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(9500)
    labels = page.evaluate("[...document.querySelectorAll('#stage .slide')].map(s=>s.getAttribute('aria-label'))")
    qa.ok("home", labels and labels[-1] != (home["slides"][-1][0] if home["slides"] else None), "Hero carousel does not rotate", sev="low", actual=labels)
    qa.shot(page, "en_home_after_carousel")

    # ---------- mobile pass (iPhone 13)
    dev = dict(p.devices["iPhone 13"])
    if browser.browser_type.name == "firefox":
        dev.pop("is_mobile", None)  # Firefox cannot emulate isMobile; viewport + UA + touch still apply
    mctx = qa.context(browser, **dev)
    mp = qa.watch(mctx.new_page())
    MOB = """()=>{const W=window.innerWidth;const off=[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.right>W+1&&getComputedStyle(e).position!=='fixed'&&!e.closest('.marquee')&&!e.closest('#stage')}).slice(0,8).map(e=>e.tagName.toLowerCase()+(e.id?'#'+e.id:'')+(e.className&&typeof e.className==='string'?'.'+e.className.split(' ').join('.'):'')+' r='+Math.round(e.getBoundingClientRect().right));
      const small=[...document.querySelectorAll('button,a[href],select,input:not([type=hidden]),summary')].filter(e=>{const r=e.getBoundingClientRect();const s=getComputedStyle(e);const inline=e.tagName==='A'&&!!e.closest('p,small,li,td,.legal,.crumbs,h3,label');return r.width>0&&r.height>0&&s.visibility!=='hidden'&&(r.width<24||r.height<24)&&!e.closest('.marquee')&&!inline&&!(e.tagName==='INPUT'&&e.closest('label'))}).map(e=>(e.tagName.toLowerCase()+(e.className&&typeof e.className==='string'?'.'+e.className.split(' ')[0]:'')+' "'+(e.innerText||e.getAttribute('aria-label')||'').trim().slice(0,20)+'" '+Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height)));
      return {sw:document.documentElement.scrollWidth,W,off,small}}"""
    mres = {}
    for h in ["#/", "#/shop", "#/design", "CART", "#/cart", "#/checkout", "#/custom", "#/page/faq", "#/page/sizing", "#/login"]:
        if h == "CART":
            qa.go(mp, "#/design?breed=pug&theme=geo&style=cool", wait="#pv svg")
            st = mp.locator(".stick #add2")
            qa.ok("mobile", st.is_visible(), "Mobile sticky 'Add to cart' bar not visible on design page", sev="medium", page=mp)
            st.click()
            mp.wait_for_timeout(400)
            qa.ok("mobile", mp.inner_text("#cartn") == "1", "Mobile sticky Add to cart did not add the item", actual=mp.inner_text("#cartn"))
            continue
        qa.go(mp, h)
        scroll_all(mp)
        r = mp.evaluate(MOB)
        mres[h] = r
        rep = f"iPhone 13 viewport (390x844), open {BASE}/{h}"
        qa.ok("mobile", r["sw"] <= r["W"] + 1, f"Horizontal overflow on mobile {h}", sev="medium", repro=rep, expected=f"scrollWidth<={r['W']}", actual=f"scrollWidth={r['sw']}; {r['off']}", page=mp)
        qa.ok("mobile", len(r["small"]) == 0, f"Tap targets smaller than 24px on mobile {h}", sev="low", repro=rep, expected=">=24x24 CSS px (WCAG 2.2 AA)", actual=r["small"][:12])
        qa.shot(mp, "mobile_" + (re.sub(r"\W+", "_", h.strip("#/")) or "home"), quality=50)
    qa.data["mobile"] = mres
    # burger menu
    qa.go(mp, "#/")
    qa.ok("mobile", mp.locator("#burger").is_visible(), "Burger button hidden on mobile", sev="high", page=mp)
    mp.click("#burger")
    mp.wait_for_timeout(300)
    qa.ok("mobile", mp.evaluate("document.querySelector('#links').classList.contains('open')"), "Burger does not open the menu", sev="high", page=mp)
    qa.shot(mp, "mobile_burger_open")
    links = mp.evaluate("[...document.querySelectorAll('#links a')].map(a=>a.getAttribute('href'))")
    for i, href in enumerate(links):
        qa.go(mp, "#/")
        mp.click("#burger"); mp.wait_for_timeout(250)
        lk = mp.locator("#links a").nth(i)
        vis = lk.is_visible()
        qa.ok("mobile", vis, f"Burger menu link {href} not visible when menu open", sev="high", page=mp)
        if vis:
            lk.click(); mp.wait_for_timeout(300); qa.quiet(mp, 200)
            qa.ok("mobile", mp.evaluate("location.hash") == href, f"Burger link {href} does not navigate", actual=mp.evaluate("location.hash"))
            qa.ok("mobile", not mp.evaluate("document.querySelector('#links').classList.contains('open')"), "Burger menu stays open after navigating", sev="low")
    mp.click("#burger"); mp.wait_for_timeout(200); mp.click("#burger"); mp.wait_for_timeout(200)
    qa.ok("mobile", not mp.evaluate("document.querySelector('#links').classList.contains('open')"), "Burger does not close on second tap", sev="low")
    mctx.close()
    ctx.close()


if __name__ == "__main__":
    run(nav_shard, "nav")
