"""Shard config: the designer. Every product x color (incl. disabled) x size x front opt x back opt, every breed x theme x style
on both sides, view tabs, qty, product-switch carry-over, URL-param robustness, save-design redirect."""
import re, os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from common import *

STATE_JS = """()=>{const q=s=>document.querySelector(s);const p=q('#ctl .price');return {prod:q('#ctl [data-prod].on')?.dataset.prod,color:q('#ctl .sw.on')?.dataset.color,
  colorLabel:(q('#ctl .swatches')?.closest('.panel').querySelector('h3 small')||{}).innerText,size:q('#ctl [data-size].on')?.dataset.size,
  fo:q('#ctl [data-k=front][data-opt].on')?.dataset.opt,bo:q('#ctl [data-k=back][data-opt].on')?.dataset.opt,
  breedF:q('#ctl select[data-k=front]')?.value,breedB:q('#ctl select[data-k=back]')?.value,
  themeF:q('#ctl [data-k=front][data-f=theme].on')?.dataset.v,styleF:q('#ctl [data-k=front][data-f=style].on')?.dataset.v,
  themeB:q('#ctl [data-k=back][data-f=theme].on')?.dataset.v,styleB:q('#ctl [data-k=back][data-f=style].on')?.dataset.v,
  price:p?p.innerText:null,add:q('#add')?.disabled,add2:q('#add2')?.disabled,stick:q('.stick b')?.innerText,stickSmall:q('.stick small')?.innerText,qty:q('.qty b')?.innerText,
  pv:q('#pv').innerHTML,tab:q('.pvtabs .chip.on')?.dataset.v,backTabHidden:q('.pvtabs [data-v=back]').hidden,
  frontPanel:!!q('#ctl [data-k=front][data-opt]'),backPanel:!!q('#ctl [data-k=back][data-opt]'),toast:q('#toast').innerText}}"""
WAIT_JS = "async([ph,art])=>{const S=" + STATE_JS + ";const t0=Date.now();let s;while(Date.now()-t0<4000){s=S();const n=(s.pv.match(/<image /g)||[]).length;if(s.pv.includes('href=\"'+ph+'\"')&&(art?s.pv.includes('href=\"'+art+'\"'):n===1))return [true,s];await new Promise(r=>setTimeout(r,10))}return [false,s]}"
CLICK = "s=>{const e=document.querySelector(s);if(!e)return false;e.click();return true}"


def config_shard(qa, browser, p):
    ctx = qa.context(browser, viewport={"width": 1280, "height": 900})
    page = qa.watch(ctx.new_page())
    cat = catalog(ctx)
    P = {x["id"]: x for x in cat["products"]}
    CAL = cat["cal"]
    B = [b["slug"] for b in cat["breeds"]]
    TH = [t["id"] for t in cat["themes"]]
    ST = [s["id"] for s in cat["styles"]]
    fopt = {o["id"]: o for o in cat["front_opts"]}
    bopt = {o["id"]: o for o in cat["back_opts"]}
    qa.go(page, "#/design", wait="#pv svg")
    S = lambda: page.evaluate(STATE_JS)
    click = lambda sel: page.evaluate(CLICK, sel)
    T = lambda s, *a: page.evaluate("async([s,a])=>(await import('./js/i18n.js')).t(s,...a)", [s, list(a)])
    t_ship, t_soon_toast = T("+ shipping"), T("Dark colors with white-ink art are coming soon")
    hrefs = set()
    states = 0

    def art_for(opt_id, kind, breed="french_bulldog", theme="line", style="classic"):
        o = (fopt if kind == "front" else bopt).get(opt_id)
        if not o or not o.get("part"):
            return None
        return f"art/{theme}_{style}/{breed}_{'front' if o['part'] == 'head' else 'back'}.svg"

    # default state
    s = S()
    qa.ok("designer", (s["prod"], s["color"], s["size"], s["fo"], s["bo"]) == ("tee", "White", "M", "head_s", "body_l"), "Designer default state unexpected", sev="info", actual=(s["prod"], s["color"], s["size"], s["fo"], s["bo"]))
    garms = page.evaluate("[...document.querySelectorAll('#ctl [data-prod]')].map(b=>b.dataset.prod)")
    qa.ok("designer", sorted(garms) == sorted(P), "Garment picker does not list every catalog product", expected=sorted(P), actual=garms)

    for pid, prod in P.items():
        page.click(f"#ctl button[data-prod='{pid}']")
        page.wait_for_timeout(100)
        s = S()
        rep0 = f"#/design, click garment '{prod['name']}'"
        qa.ok("designer", s["prod"] == pid, f"Garment button {pid} does not select it", repro=rep0, actual=s["prod"])
        sw = page.evaluate("[...document.querySelectorAll('#ctl .sw')].map(b=>[b.dataset.color,b.dataset.ok,b.classList.contains('off'),b.getAttribute('aria-label'),getComputedStyle(b).backgroundColor])")
        qa.ok("designer", [x[0] for x in sw] == [c[0] for c in prod["colors"]], f"{pid}: color swatches differ from catalog", repro=rep0, expected=[c[0] for c in prod["colors"]], actual=[x[0] for x in sw])
        qa.ok("designer", all((x[1] == str(c[2])) and (x[2] == (c[2] == 0)) for x, c in zip(sw, prod["colors"])), f"{pid}: disabled-color marking wrong", repro=rep0, actual=sw)
        def rgb(h):
            n = int(h[1:], 16); return f"rgb({n >> 16}, {(n >> 8) & 255}, {n & 255})"
        qa.ok("designer", all(x[4] == rgb(c[1]) for x, c in zip(sw, prod["colors"])), f"{pid}: swatch colors differ from catalog hex", sev="low", repro=rep0, actual=[(x[0], x[4]) for x in sw])
        sizes = page.evaluate("[...document.querySelectorAll('#ctl [data-size]')].map(b=>b.dataset.size)")
        qa.ok("designer", sizes == prod["sizes"], f"{pid}: sizes differ from catalog", repro=rep0, expected=prod["sizes"], actual=sizes)
        fo_ids = page.evaluate("[...document.querySelectorAll('#ctl [data-k=front][data-opt]')].map(b=>b.dataset.opt)")
        bo_ids = page.evaluate("[...document.querySelectorAll('#ctl [data-k=back][data-opt]')].map(b=>b.dataset.opt)")
        efo = [o["id"] for o in opts_of(cat, pid, "front")] if "front" in sides_of(cat, pid) else []
        ebo = [o["id"] for o in opts_of(cat, pid, "back")] if "back" in sides_of(cat, pid) else []
        qa.ok("designer", fo_ids == efo, f"{pid}: front options differ from catalog rules", repro=rep0, expected=efo, actual=fo_ids)
        qa.ok("designer", bo_ids == ebo, f"{pid}: back options shown/hidden incorrectly", repro=rep0, expected=ebo, actual=bo_ids)
        qa.ok("designer", s["backTabHidden"] == ("back" not in sides_of(cat, pid)), f"{pid}: Back preview tab visibility wrong", repro=rep0, actual=s["backTabHidden"])
        fab = page.evaluate("[...document.querySelectorAll('#ctl details')].map(d=>d.querySelector('p').textContent)")
        qa.ok("designer", fab and len(fab[0]) > 30 and "undefined" not in fab[0], f"{pid}: 'Fabric & fit' text missing", sev="medium", repro=rep0 + ", open 'Fabric & fit'", actual=fab[:1])
        qa.ok("designer", (T("Finished with the AlphaDog logo label.") in fab[0]) == bool(prod.get("label")), f"{pid}: logo-label sentence inconsistent with catalog", sev="low", repro=rep0, actual=fab[:1])
        thumbs = page.evaluate("[...document.querySelectorAll('#ctl [data-prod] img')].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.getAttribute('src'))")
        qa.ok("designer", not thumbs, "Garment picker thumbnails broken", sev="high", actual=thumbs, page=page)
        # disabled colors must refuse
        for c in [c for c in prod["colors"] if not c[2]]:
            before = S()["color"]
            page.evaluate("()=>{document.querySelector('#toast').innerText=''}")
            page.click(f"#ctl .sw[data-color='{c[0]}']")
            page.wait_for_timeout(60)
            s2 = S()
            qa.ok("colors_disabled", s2["color"] == before and s2["toast"] == t_soon_toast, f"Disabled color {c[0]} on {pid} can be selected or gives no notice", sev="high",
                  repro=f"{rep0}, click swatch {c[0]}", expected=f"stays {before}, toast '{t_soon_toast}'", actual=(s2["color"], s2["toast"]), page=page)
        # exhaustive enabled color x size x front x back
        bos = ebo or [None]
        for col in [c for c in prod["colors"] if c[2]]:
            click(f"#ctl .sw[data-color='{col[0]}']")
            for size in prod["sizes"]:
                click(f"#ctl [data-size='{size}']")
                for fo in efo:
                    click(f"#ctl [data-k=front][data-opt='{fo}']")
                    for bo in bos:
                        if bo is not None:
                            click(f"#ctl [data-k=back][data-opt='{bo}']")
                        view = "back" if bo is not None else "front"
                        ph = f"img/{pid}_{col[3]}_{view}.webp"
                        art = art_for(bo, "back") if view == "back" else art_for(fo, "front")
                        okw, s = page.evaluate(WAIT_JS, [ph, art])
                        states += 1
                        rep = f"#/design, garment {pid}, color {col[0]}, size {size}, front '{fo}', back '{bo}'"
                        qa.ok("designer_states", okw, "Preview does not show the selected garment/color/side/art", sev="high", repro=rep, expected=(ph, art), actual=parse_svg(s["pv"]), page=page)
                        qa.ok("designer_states", (s["color"], s["size"], s["fo"], s["bo"]) == (col[0], size, fo, bo), "Designer option highlight differs from what was clicked", repro=rep, expected=(col[0], size, fo, bo), actual=(s["color"], s["size"], s["fo"], s["bo"]))
                        n = (fo != "none") + (bo not in (None, "none"))
                        if n:
                            pr = money(price_cents(cat, pid, n, size))
                            qa.ok("designer_price", s["price"].startswith(pr) and t_ship in s["price"] and s["stick"] == pr and not s["add"] and not s["add2"],
                                  "Designer price differs from catalog price rule", sev="high", repro=rep, expected=f"{pr} {t_ship}", actual=(s["price"], s["stick"], s["add"]), page=page)
                        else:
                            qa.ok("designer_price", s["price"].startswith("—") and s["add"] and s["add2"], "Nothing-on-either-side state still purchasable", sev="high", repro=rep, actual=(s["price"], s["add"]))
                        qa.ok("designer_states", s["tab"] == view, "Preview tab highlight differs from shown side", sev="low", repro=rep, expected=view, actual=s["tab"])
                        ph2, a2, rect = parse_svg(s["pv"])
                        if a2 and rect:
                            hrefs.add(a2)
                            ax, ay, aw, ah = CAL[pid][view]
                            x, y, w, h = rect
                            inside = x >= ax - 1.5 and y >= ay - 1.5 and x + w <= ax + aw + 1.5 and y + h <= ay + ah + 1.5
                            qa.ok("placement", inside, f"Art placed outside the {pid} {view} print area", sev="medium", repro=rep, expected=f"inside {CAL[pid][view]}", actual=rect, page=page)
                        if ph2:
                            hrefs.add(ph2)
            cl = S()["colorLabel"]
            qa.ok("designer", cl == (col[4] if len(col) > 4 and col[4] else col[0]), f"{pid}: color label wrong for {col[0]}", sev="low", actual=cl)
        # view tabs
        for v in (["front", "back"] if "back" in sides_of(cat, pid) else ["front"]):
            page.click(f".pvtabs [data-v={v}]")
            page.wait_for_timeout(120)
            s = S()
            qa.ok("view_tabs", f"_{v}.webp" in (parse_svg(s["pv"])[0] or "") and s["tab"] == v, f"{pid}: preview tab {v} does not switch the preview", repro=f"#/design {pid}, click {v} tab", actual=parse_svg(s["pv"])[0])
        qa.shot(page, f"designer_{pid}", quality=45)
    qa.data["designer_states_checked"] = states

    # every art / photo URL seen must load
    bad = page.evaluate("""async(urls)=>{const bad=[];await Promise.all(urls.map(u=>new Promise(r=>{const im=new Image();im.onload=()=>{if(!im.naturalWidth)bad.push(u);r()};im.onerror=()=>{bad.push(u);r()};im.src=u})));return bad}""", sorted(hrefs))
    qa.ok("designer", not bad, "Designer preview references images that do not load", sev="high", actual=bad[:20])

    # ---------- qty
    page.click("#ctl button[data-prod='tee']"); page.wait_for_timeout(100)
    click("#ctl [data-size='M']"); click("#ctl [data-k=front][data-opt='head_l']"); click("#ctl [data-k=back][data-opt='none']")
    for _ in range(25):
        click("#ctl [data-q='1']")
    s = S()
    pr = price_cents(cat, "tee", 1, "M")
    qa.ok("qty", s["qty"] == "20" and money(pr * 20) in s["price"] and s["stick"] == money(pr * 20) and "20" in s["stickSmall"], "Designer qty cap / multiplied price wrong", repro="#/design tee, press + 25 times",
          expected=f"qty 20, {money(pr*20)}", actual=(s["qty"], s["price"], s["stick"], s["stickSmall"]), page=page)
    for _ in range(25):
        click("#ctl [data-q='-1']")
    s = S()
    qa.ok("qty", s["qty"] == "1" and t_ship in s["price"], "Designer qty floor wrong", actual=(s["qty"], s["price"]))
    page.click("#ctl [data-q='1']"); page.click("#ctl [data-q='1']")
    qa.ok("qty", S()["qty"] == "3", "Real clicks on qty + do not increment", actual=S()["qty"])
    click("#ctl [data-q='-1']"); click("#ctl [data-q='-1']")

    # ---------- breed x theme x style, both sides (tee, front head_l, back body_l)
    click("#ctl [data-k=front][data-opt='head_l']"); click("#ctl [data-k=back][data-opt='body_l']")
    art_urls = set()
    combos = 0
    for k, part in (("front", "front"), ("back", "back")):
        for b in B:
            page.select_option(f"#ctl select[data-k={k}]", b)
            for th in TH:
                click(f"#ctl [data-k={k}][data-f=theme][data-v='{th}']")
                for st in ST:
                    click(f"#ctl [data-k={k}][data-f=style][data-v='{st}']")
                    art = f"art/{th}_{st}/{b}_{part}.svg"
                    okw, s = page.evaluate(WAIT_JS, [f"img/tee_white_{k}.webp", art])
                    combos += 1
                    art_urls.add(art)
                    rep = f"#/design tee White, {k} option {'Big head' if k=='front' else 'Full body'}, breed {b}, {th}, {st}"
                    qa.ok("art_combos", okw, "Designer preview art does not follow breed/theme/style selection", sev="high", repro=rep, expected=art, actual=parse_svg(s["pv"])[1], page=page)
                    qa.ok("art_combos", (s["breedF" if k == "front" else "breedB"], s["themeF" if k == "front" else "themeB"], s["styleF" if k == "front" else "styleB"]) == (b, th, st), "Breed/theme/style control highlight wrong", repro=rep, actual=s)
    qa.data["art_combos_checked"] = combos
    bad = page.evaluate("""async(urls)=>{const bad=[];await Promise.all(urls.map(u=>new Promise(r=>{const im=new Image();im.onload=()=>{if(!im.naturalWidth)bad.push(u);r()};im.onerror=()=>{bad.push(u);r()};im.src=u})));return bad}""", sorted(art_urls))
    qa.ok("art_combos", not bad, "Art files referenced by the designer fail to load", sev="critical", actual=bad[:30])
    # independent sides
    page.select_option("#ctl select[data-k=front]", "pug"); click("#ctl [data-k=front][data-f=theme][data-v='geo']"); click("#ctl [data-k=front][data-f=style][data-v='cool']")
    page.select_option("#ctl select[data-k=back]", "beagle"); click("#ctl [data-k=back][data-f=theme][data-v='line']"); click("#ctl [data-k=back][data-f=style][data-v='heart']")
    page.click(".pvtabs [data-v=front]"); okf, s1 = page.evaluate(WAIT_JS, ["img/tee_white_front.webp", "art/geo_cool/pug_front.svg"])
    page.click(".pvtabs [data-v=back]"); okb, s2 = page.evaluate(WAIT_JS, ["img/tee_white_back.webp", "art/line_heart/beagle_back.svg"])
    qa.ok("art_combos", okf and okb, "Front and back designs are not independent", sev="high", repro="tee: front pug geo cool, back beagle line heart, toggle tabs", actual=(parse_svg(s1["pv"])[1], parse_svg(s2["pv"])[1]), page=page)
    qa.shot(page, "designer_two_dogs")

    # ---------- product switch carry-over
    def setp(pid):
        page.click(f"#ctl button[data-prod='{pid}']"); page.wait_for_timeout(80); return S()
    setp("tee"); click("#ctl [data-k=front][data-opt='body_l']"); click("#ctl [data-k=back][data-opt='head_l']"); click("#ctl .sw[data-color='Ash']"); click("#ctl [data-size='3XL']")
    s = setp("polo")
    qa.ok("carry_over", s["fo"] == "body_s", "Switching garment turns a chosen full-body front into a head emblem", sev="low",
          repro="#/design tee, front 'Big body', then click Polo", expected="body_s (Body emblem, closest allowed option)", actual=s["fo"], page=page)
    qa.ok("carry_over", s["size"] == "3XL" and s["color"] == "White", "Polo carry-over of size/color unexpected", sev="info", actual=(s["size"], s["color"]))
    s = setp("tee")
    qa.ok("carry_over", s["bo"] == "head_l", "Back design lost after visiting a front-only garment", sev="medium", repro="tee back 'Big head' -> Polo -> Tee", expected="head_l", actual=s["bo"])
    qa.ok("carry_over", s["fo"] == "body_l", "Front 'Big body' not restored after returning from a front-only garment", sev="low", repro="tee front 'Big body' -> Polo -> Tee", expected="body_l", actual=s["fo"])
    click("#ctl .sw[data-color='Ash']"); s = setp("hoodie")
    qa.ok("carry_over", s["color"] == "Ash", "Shared color not kept when switching tee->hoodie", sev="low", actual=s["color"])
    setp("tee"); click("#ctl .sw[data-color='Natural']"); s = setp("hoodie")
    qa.ok("carry_over", s["color"] == "White", "Unavailable color not reset to first available", actual=s["color"])
    setp("tee"); click("#ctl [data-size='3XL']"); s = setp("tank")
    qa.ok("carry_over", s["size"] == "M", "Unavailable size not reset", actual=s["size"])
    s = setp("cap_dad")
    qa.ok("carry_over", s["size"] == "One size" and s["fo"] in ("head_s", "body_s") and s["bo"] is None, "Cap state wrong after switch", actual=(s["size"], s["fo"], s["bo"]))

    # ---------- URL param robustness
    cases = [("#/design?breed=bogus", {"breedF": "french_bulldog"}), ("#/design?prod=bogus", {"prod": "tee"}),
             ("#/design?prod=tee&color=Black", {"prod": "tee", "color": "White"}), ("#/design?prod=hoodie&color=Nope", {"prod": "hoodie", "color": "White"}),
             ("#/design?prod=polo&part=body", {"prod": "polo", "fo": "body_s"}), ("#/design?prod=cap_mesh&color=Pink", {"prod": "cap_mesh", "color": "White"}),
             ("#/design?prod=tank&part=body&breed=pug&theme=geo&style=heart", {"prod": "tank", "fo": "body_l", "breedF": "pug", "themeF": "geo", "styleF": "heart"}),
             ("#/design?theme=bogus", {"themeF": None}), ("#/design?style=bogus", {"styleF": None})]
    for h, exp in cases:
        m = qa.mark()
        qa.go(page, h, wait="#pv svg")
        page.wait_for_timeout(300)
        s = S()
        act = {k: s.get(k) for k in exp}
        e = qa.errs_since(m)
        if "bogus" in h and ("theme" in h or "style" in h):
            art = parse_svg(s["pv"])[1]
            qa.ok("url_params", s.get("themeF") in TH and s.get("styleF") in ST, f"Designer accepts unknown {'theme' if 'theme' in h else 'style'} from URL (broken preview art, invalid cart line)", sev="low",
                  repro=f"open {BASE}/{h}", expected="fallback to a valid theme/style", actual=f"no theme/style highlighted; preview art {art}; http errors {[x['url'] for x in e['http']][:2]}", page=page)
            if s.get("themeF") not in TH or s.get("styleF") not in ST:
                page.click("#add"); page.wait_for_timeout(200)
                m2 = qa.mark()
                try:
                    qa.go(page, "#/cart")
                except Exception:
                    pass
                page.wait_for_timeout(500)
                pe = qa.errs_since(m2)["pageerror"]
                qa.ok("url_params", not pe, "Cart page crashes after adding a design opened with an unknown theme/style URL", sev="medium",
                      repro=f"open {BASE}/{h}, Add to cart, open #/cart", expected="cart renders", actual=pe[:2], page=page)
                page.evaluate("localStorage.removeItem('ad_cart')"); page.goto(BASE + "/#/"); page.wait_for_selector("#app > *")
        else:
            qa.ok("url_params", act == exp and not e["pageerror"], f"Designer URL {h} not normalized", repro=f"open {BASE}/{h}", expected=exp, actual=[act, e["pageerror"][:1]], page=page)

    # ---------- save design while logged out
    qa.go(page, "#/design?breed=boxer", wait="#pv svg")
    page.click("#save"); page.wait_for_timeout(400)
    qa.ok("save_design", page.evaluate("location.hash").startswith("#/login") and page.evaluate("!!localStorage.getItem('ad_pending')"), "Save design while logged out does not go to login / keep pending design", actual=page.evaluate("location.hash"))

    # ---------- designer in es / pt: same prices, translated labels
    for l in ("es", "pt"):
        page.select_option("#lang", l); qa.quiet(page)
        qa.go(page, "#/design?prod=hoodie&breed=pug", wait="#pv svg")
        s = S()
        qa.ok("i18n", s["price"].startswith(money(price_cents(cat, "hoodie", 2, "M"))), f"Designer price differs in {l}", sev="high", actual=s["price"])
        chips = page.evaluate("[...document.querySelectorAll('#ctl .chips .chip, #ctl .seg button, #ctl h3')].map(e=>e.childNodes[0].textContent.trim())")
        en = {"Front design", "Back design", "Garment", "Color", "Size", "Head emblem", "Big head", "Body emblem", "Big body", "Full body", "Nothing", "Continuous Line", "Geometric", "Classic", "Cool", "Heart"}
        left = [c for c in chips if c in en]
        qa.ok("i18n", not left, f"Designer labels left in English in {l}", sev="low", repro=f"language {l}, #/design", actual=left)
        qa.shot(page, f"designer_{l}", quality=45)
    page.select_option("#lang", "en")
    ctx.close()


if __name__ == "__main__":
    run(config_shard, "config")
