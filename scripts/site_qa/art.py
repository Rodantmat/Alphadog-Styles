"""Shard art: every advertised breed x theme x style x part art file + every garment photo; HTTP status, SVG sanity,
rendered ink coverage, duplicates; contact sheets for visual review; mini_poodle geo heart close-up."""
import re, os, sys, json, hashlib
sys.path.insert(0, os.path.dirname(__file__))
from common import *

INK = """async(urls)=>{const out={};await Promise.all(urls.map(u=>new Promise(res=>{const im=new Image();im.onload=()=>{const c=document.createElement('canvas');c.width=c.height=160;const g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,160,160);
  const a=im.naturalWidth/im.naturalHeight||1;let w=160,h=160;if(a>1)h=160/a;else w=160*a;g.drawImage(im,(160-w)/2,(160-h)/2,w,h);let d;try{d=g.getImageData(0,0,160,160).data}catch(e){out[u]={err:'taint'};return res()}
  let ink=0,col=0,x0=160,y0=160,x1=-1,y1=-1;for(let i=0;i<d.length;i+=4){const L=0.299*d[i]+0.587*d[i+1]+0.114*d[i+2];if(L<200){ink++;const p=i/4,x=p%160,y=(p-x)/160;if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y}
  if(Math.max(d[i],d[i+1],d[i+2])-Math.min(d[i],d[i+1],d[i+2])>40)col++}
  out[u]={w:im.naturalWidth,h:im.naturalHeight,ink:ink/25600,color:col/25600,bbox:[x0,y0,x1,y1]};res()};im.onerror=()=>{out[u]={err:'load'};res()};im.src=u})));return out}"""


def art_shard(qa, browser, p):
    ctx = qa.context(browser, viewport={"width": 1700, "height": 1000})
    page = qa.watch(ctx.new_page())
    cat = catalog(ctx)
    B = [b["slug"] for b in cat["breeds"]]
    bname = {b["slug"]: b["name"] for b in cat["breeds"]}
    TH = [t["id"] for t in cat["themes"]]
    ST = [s["id"] for s in cat["styles"]]
    urls = [f"art/{t}_{s}/{b}_{part}.svg" for t in TH for s in ST for b in B for part in ("front", "back")]
    meta = {}
    sha = {}
    for u in urls:
        r = ctx.request.get(f"{BASE}/{u}")
        body = r.body() if r.ok else b""
        txt = body.decode("utf-8", "replace")
        h = hashlib.sha1(body).hexdigest()
        shapes = len(re.findall(r"<(path|polygon|polyline|circle|ellipse|line|rect)\b", txt))
        meta[u] = {"status": r.status, "ctype": r.headers.get("content-type", ""), "bytes": len(body), "sha": h[:12], "shapes": shapes,
                   "raster": "<image" in txt, "viewBox": (re.search(r'viewBox="([^"]+)"', txt) or [None, None])[1]}
        sha.setdefault(h, []).append(u)
        rep = f"GET {BASE}/{u}"
        if qa.ok("art_files", r.status == 200, f"Art file missing: {u}", sev="critical", repro=rep, expected=200, actual=r.status):
            qa.ok("art_files", "svg" in meta[u]["ctype"], "Art served with wrong content-type", sev="medium", repro=rep, actual=meta[u]["ctype"])
            qa.ok("art_files", len(body) > 1500 and shapes >= 1, f"Art file nearly empty: {u}", sev="high", repro=rep, actual=f"{len(body)} bytes, {shapes} shapes")
    for h, us in sha.items():
        if len(us) > 1:
            qa.defect("high", "art_files", "Identical art files reused for different breed/theme/style/part", repro="compare SHA-1 of art files", expected="unique art per combination", actual=us)
    qa.count("art_files", 0)
    qa.data["art_meta"] = meta

    # rendered ink coverage (same-origin page so canvas is readable)
    page.goto(BASE + "/robots.txt")
    ink = page.evaluate(INK, ["/" + u for u in urls])
    qa.data["art_ink"] = {k.lstrip("/"): v for k, v in ink.items()}
    vals = sorted(v.get("ink", 0) for v in ink.values() if "ink" in v)
    med = vals[len(vals) // 2] if vals else 0
    qa.data["art_ink_median"] = med
    for u, v in ink.items():
        u2 = u.lstrip("/")
        if "err" in v:
            qa.ok("art_render", False, f"Art does not render in the browser: {u2}", sev="critical", actual=v)
            continue
        qa.ok("art_render", v["ink"] > 0.01, f"Art renders (nearly) blank: {u2}", sev="critical", repro=f"open {BASE}/{u2}", expected="visible drawing (>1% ink)", actual=f"ink {v['ink']:.4f}")
        qa.ok("art_render", v["ink"] < 0.6, f"Art renders as a mostly solid blob: {u2}", sev="high", repro=f"open {BASE}/{u2}", actual=f"ink {v['ink']:.3f}")
        bw, bh = v["bbox"][2] - v["bbox"][0], v["bbox"][3] - v["bbox"][1]
        qa.ok("art_render", max(bw, bh) > 60, f"Art drawing is tiny inside its canvas: {u2}", sev="medium", repro=f"open {BASE}/{u2}", actual=f"bbox {v['bbox']} of 160px")
    # outliers vs same theme_style median
    for t in TH:
        for s in ST:
            for part in ("front", "back"):
                grp = {b: ink.get(f"/art/{t}_{s}/{b}_{part}.svg", {}).get("ink", 0) for b in B}
                gv = sorted(grp.values())
                gm = gv[len(gv) // 2]
                for b, x in grp.items():
                    if gm and (x < gm * 0.25 or x > gm * 3.5):
                        qa.defect("medium", "art_render", f"Art ink coverage far from its group: {t}_{s}/{b}_{part}", repro=f"open {BASE}/art/{t}_{s}/{b}_{part}.svg",
                                  expected=f"near group median {gm:.3f}", actual=f"{x:.3f}")

    # contact sheets (visual review)
    os.makedirs(f"{OUT}/sheets", exist_ok=True)
    for t in TH:
        for s in ST:
            cells = "".join(f'<div class="c"><img src="/art/{t}_{s}/{b}_{part}.svg"><span>{bname[b]} · {"head" if part=="front" else "body"}</span></div>' for b in B for part in ("front", "back"))
            page.evaluate("""([title,cells])=>{document.documentElement.innerHTML='<head><style>body{margin:0;font:11px sans-serif;background:#fff}.g{display:grid;grid-template-columns:repeat(11,150px);gap:4px;padding:6px}.c{border:1px solid #ddd;height:170px;display:flex;flex-direction:column;align-items:center}.c img{width:146px;height:146px;object-fit:contain}h2{margin:6px}</style></head><body><h2>'+title+'</h2><div class=g>'+cells+'</div></body>'}""", [f"{t}_{s}", cells])
            page.wait_for_function("[...document.images].every(i=>i.complete)", timeout=30000)
            page.screenshot(path=f"{OUT}/sheets/{t}_{s}.jpg", type="jpeg", quality=70, full_page=True)
    # mini_poodle geo heart close-up next to poodle
    cells = "".join(f'<div class="c"><img src="/art/geo_heart/{b}_{part}.svg"><span>{b}_{part}</span></div>' for b in ("mini_poodle", "poodle") for part in ("front", "back"))
    page.evaluate("""(cells)=>{document.documentElement.innerHTML='<head><style>body{margin:0;font:14px sans-serif;background:#fff}.g{display:grid;grid-template-columns:repeat(4,400px);gap:6px;padding:6px}.c{border:1px solid #ccc;text-align:center}.c img{width:396px;height:396px;object-fit:contain}</style></head><body><div class=g>'+cells+'</div></body>'}""", cells)
    page.wait_for_function("[...document.images].every(i=>i.complete)", timeout=20000)
    page.screenshot(path=f"{OUT}/sheets/mini_poodle_geo_heart_closeup.jpg", type="jpeg", quality=80, full_page=True)
    qa.data["mini_poodle_geo_heart"] = {u: (meta.get(u), qa.data["art_ink"].get(u)) for u in ("art/geo_heart/mini_poodle_front.svg", "art/geo_heart/mini_poodle_back.svg", "art/geo_heart/poodle_front.svg")}

    # garment photos
    photos = 0
    for pr in cat["products"]:
        for c in pr["colors"]:
            for side in (pr.get("sides") or ["front", "back"]):
                u = f"img/{pr['id']}_{c[3]}_{side}.webp"
                r = ctx.request.get(f"{BASE}/{u}")
                photos += 1
                if c[2]:
                    qa.ok("photos", r.status == 200 and len(r.body()) > 5000, f"Garment photo missing for selectable color: {u}", sev="critical", repro=f"GET {BASE}/{u}", actual=r.status)
                elif r.status != 200:
                    qa.data.setdefault("photos_missing_for_disabled_colors", []).append(u)
    for u in [f"img/look-{i}.webp" for i in range(1, 7)] + ["logo.png", "robots.txt"]:
        r = ctx.request.get(f"{BASE}/{u}")
        qa.ok("photos", r.status == 200, f"Static asset missing: {u}", sev="high", actual=r.status)
    qa.data["photos_checked"] = photos
    # garment photo sheet per product (all selectable colors, both sides)
    cells = "".join(f'<div class="c"><img src="/img/{pr["id"]}_{c[3]}_{side}.webp"><span>{pr["id"]} {c[0]} {side}</span></div>' for pr in cat["products"] for c in pr["colors"] if c[2] for side in (pr.get("sides") or ["front", "back"]))
    page.evaluate("""(cells)=>{document.documentElement.innerHTML='<head><style>body{margin:0;font:11px sans-serif;background:#fff}.g{display:grid;grid-template-columns:repeat(10,160px);gap:4px;padding:6px}.c{border:1px solid #ddd;text-align:center}.c img{width:156px;height:156px;object-fit:contain}</style></head><body><div class=g>'+cells+'</div></body>'}""", cells)
    page.wait_for_function("[...document.images].every(i=>i.complete)", timeout=30000)
    page.screenshot(path=f"{OUT}/sheets/garment_photos.jpg", type="jpeg", quality=65, full_page=True)
    ctx.close()


if __name__ == "__main__":
    run(art_shard, "art")
