"""Shared harness for the alphadogstyles.com storefront QA (Playwright, Chromium).

Safety: every /api/* request except GET /api/health is intercepted and answered with a mock,
so no order, login email, subscription, contact message or custom request ever reaches the backend.
"""
import json, os, re, time, hashlib, urllib.parse as up
from playwright.sync_api import sync_playwright

BASE = os.environ.get("QA_BASE", "https://alphadogstyles.com").rstrip("/")
OUT = os.environ.get("QA_OUT", "out/site_qa")
LOCAL = "localhost" in BASE or "127.0.0.1" in BASE


class QA:
    def __init__(self, shard):
        self.shard = shard
        self.checks = {}          # area -> [pass, fail]
        self.defects = []         # dicts
        self.notes = []
        self.data = {}
        self.errors = {"console": [], "pageerror": [], "http": [], "failed": []}
        self.api_calls = []
        self.mocks = []           # (method, regex, fn(request)->(status, body, ctype))
        self.shots = 0
        self.t0 = time.time()
        os.makedirs(f"{OUT}/shots/{shard}", exist_ok=True)

    # ---- bookkeeping
    def ok(self, area, cond, title=None, **kw):
        c = self.checks.setdefault(area, [0, 0])
        if cond:
            c[0] += 1
        else:
            c[1] += 1
            if title:
                self.defect(kw.pop("sev", "medium"), area, title, **kw)
        return cond

    def count(self, area, n=1):
        self.checks.setdefault(area, [0, 0])[0] += n

    def defect(self, sev, area, title, repro="", expected="", actual="", shot=None, page=None):
        for d in self.defects:
            if d["title"] == title:
                d["count"] += 1
                if len(d["examples"]) < 6:
                    d["examples"].append({"repro": repro, "actual": str(actual)[:400]})
                return
        if page is not None and shot is None and self.shots < 40:
            shot = self.shot(page, "defect_" + re.sub(r"\W+", "_", title)[:50])
        self.defects.append({"sev": sev, "area": area, "title": title, "repro": repro, "expected": str(expected)[:600],
                             "actual": str(actual)[:600], "shot": shot, "count": 1, "examples": []})

    def note(self, s):
        self.notes.append(s)

    def shot(self, page, name, full=False, quality=50):
        p = f"{OUT}/shots/{self.shard}/{name}.jpg"
        try:
            page.screenshot(path=p, type="jpeg", quality=quality, full_page=full)
            self.shots += 1
            return p
        except Exception as e:
            self.note(f"screenshot {name} failed: {e}")
            return None

    def save(self):
        res = {"shard": self.shard, "base": BASE, "secs": round(time.time() - self.t0, 1), "checks": self.checks,
               "defects": self.defects, "notes": self.notes, "data": self.data,
               "errors": {k: v[:300] for k, v in self.errors.items()},
               "error_counts": {k: len(v) for k, v in self.errors.items()},
               "api_calls": self.api_calls[:400]}
        with open(f"{OUT}/{self.shard}.json", "w") as f:
            json.dump(res, f, indent=1, ensure_ascii=False)
        print(f"[{self.shard}] saved: checks={sum(v[0] for v in self.checks.values())} pass / "
              f"{sum(v[1] for v in self.checks.values())} fail, defects={len(self.defects)}")

    # ---- browser
    def mock(self, method, pattern, fn):
        self.mocks.insert(0, (method, re.compile(pattern), fn))

    def _route(self, route, request):
        u = up.urlparse(request.url)
        p = u.path
        if p == "/api/health" and request.method == "GET":
            if LOCAL:
                return route.fulfill(status=200, content_type="application/json", body='{"ok":true,"providers":{}}')
            return route.continue_()
        body = request.post_data
        rec = {"m": request.method, "path": p, "q": u.query, "body": None, "hash": None}
        try:
            rec["body"] = json.loads(body) if body else None
        except Exception:
            rec["body"] = (body or "")[:300]
        self.api_calls.append(rec)
        for m, rx, fn in self.mocks:
            if (m == "*" or m == request.method) and rx.search(p):
                st, b, ct = fn(request)
                return route.fulfill(status=st, content_type=ct, body=b if isinstance(b, (str, bytes)) else json.dumps(b))
        return route.fulfill(status=200, content_type="application/json", body='{"ok":true}')

    def context(self, browser, **kw):
        ctx = browser.new_context(**kw)
        ctx.add_init_script("try{if(!localStorage.getItem('ad_lang'))localStorage.setItem('ad_lang','en')}catch(e){}")
        ctx.route(re.compile(r".*/api/.*"), self._route)
        return ctx

    def watch(self, page):
        page._qa_inflight = 0
        def where():
            try:
                return page.url.split("#", 1)[1] if "#" in page.url else "/"
            except Exception:
                return "?"
        def req(r):
            page._qa_inflight += 1
        def done(r):
            page._qa_inflight = max(0, page._qa_inflight - 1)
        def resp(r):
            if r.status >= 400:
                self.errors["http"].append({"at": where(), "status": r.status, "url": r.url})
        def failed(r):
            done(r)
            f = r.failure or ""
            if "ERR_ABORTED" in f and ("/img/" in r.url or "/art/" in r.url):
                return  # image superseded by re-render (not a defect)
            self.errors["failed"].append({"at": where(), "url": r.url, "err": f})
        page.on("request", req)
        page.on("requestfinished", done)
        page.on("requestfailed", failed)
        page.on("response", resp)
        page.on("console", lambda m: m.type == "error" and self.errors["console"].append({"at": where(), "text": m.text[:300]}))
        page.on("pageerror", lambda e: self.errors["pageerror"].append({"at": where(), "text": str(e)[:400]}))
        return page

    def quiet(self, page, ms=400, maxms=8000):
        t = time.time()
        calm = None
        while (time.time() - t) * 1000 < maxms:
            if getattr(page, "_qa_inflight", 0) == 0:
                calm = calm or time.time()
                if (time.time() - calm) * 1000 >= ms:
                    return True
            else:
                calm = None
            page.wait_for_timeout(50)
        return False

    def go(self, page, h, wait=None, quiet=True):
        """navigate the SPA to hash h (e.g. '#/shop'); first call loads the site."""
        if not page.url.startswith(BASE):
            page.goto(BASE + "/" + h, wait_until="domcontentloaded")
        else:
            page.evaluate("h=>{if(location.hash===h)window.dispatchEvent(new HashChangeEvent('hashchange'));else location.hash=h}", h)
        page.wait_for_function("document.querySelector('#app')&&document.querySelector('#app').children.length>0", timeout=15000)
        if wait:
            page.wait_for_selector(wait, timeout=15000)
        if quiet:
            self.quiet(page)

    def errs_since(self, marks):
        return {k: self.errors[k][marks[k]:] for k in self.errors}

    def mark(self):
        return {k: len(v) for k, v in self.errors.items()}


def catalog(ctx):
    return ctx.request.get(BASE + "/data/catalog.json").json()


def price_cents(cat, pid, sides, size):
    p = next(x for x in cat["products"] if x["id"] == pid)
    base = p["price"]["both"] if sides >= 2 and p["price"].get("both") else p["price"]["one"]
    return base + p.get("sur", {}).get(size, 0)


def money(c):
    return "$%.2f" % (c / 100)


def opts_of(cat, pid, k):
    p = next(x for x in cat["products"] if x["id"] == pid)
    ids = (p.get("opts") or {}).get(k)
    return [o for o in cat[k + "_opts"] if (ids is None or o["id"] in ids)]


def sides_of(cat, pid):
    p = next(x for x in cat["products"] if x["id"] == pid)
    return p.get("sides") or ["front", "back"]


def valid_item(cat, it, cust_id=None):
    """Python port of worker/index.js validItem() - what the backend would accept."""
    p = next((x for x in cat["products"] if x["id"] == it.get("prod")), None)
    if not p:
        return None
    if not any(c[0] == it.get("color") and c[2] for c in p["colors"]) or it.get("size") not in p["sizes"]:
        return None
    def side(d, k):
        if not d:
            return None
        if k not in (p.get("sides") or ["front", "back"]):
            return False
        al = (p.get("opts") or {}).get(k)
        o = next((x for x in cat[k + "_opts"] if x.get("part") == d.get("part") and x.get("size") == d.get("size") and (not al or x["id"] in al)), None)
        if d.get("custom"):
            return {"ok": 1} if (cust_id and o) else False
        if not o or not any(b["slug"] == d.get("breed") for b in cat["breeds"]) or not any(t["id"] == d.get("theme") for t in cat["themes"]) or not any(s["id"] == d.get("style") for s in cat["styles"]):
            return False
        return {"ok": 1}
    f, b = side(it.get("front"), "front"), side(it.get("back"), "back")
    if f is False or b is False or (not f and not b):
        return None
    return True


IMG_RX = re.compile(r'<image href="([^"]+)"(?: x="([\d.-]+)" y="([\d.-]+)" width="([\d.-]+)" height="([\d.-]+)")?')


def parse_svg(html):
    """returns (photo_href, art_href or None, art_rect or None)"""
    ims = IMG_RX.findall(html or "")
    if not ims:
        return None, None, None
    photo = ims[0][0]
    if len(ims) > 1:
        a = ims[1]
        return photo, a[0], tuple(float(v) for v in a[1:5]) if a[1] else None
    return photo, None, None


def run(shard_fn, shard):
    qa = QA(shard)
    with sync_playwright() as p:
        browser = getattr(p, os.environ.get('QA_BROWSER','chromium')).launch()
        try:
            shard_fn(qa, browser, p)
        except Exception as e:
            import traceback
            traceback.print_exc()
            qa.defect("info", "harness", f"QA harness crashed in shard {shard}: {e}", actual=traceback.format_exc()[-1500:])
        finally:
            qa.save()
            browser.close()
