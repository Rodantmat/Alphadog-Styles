import os, json, re, time, requests
OUT = "docs/brazil_data"
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
def save(name, data):
    p = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=1))
    print("saved", p, len(data))
def get(url, **kw):
    try:
        r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"}, timeout=25, **kw)
        return r
    except Exception as e:
        print("ERR", url, e); return None
def text_of_html(html):
    from bs4 import BeautifulSoup
    s = BeautifulSoup(html, "lxml")
    for t in s(["script", "style", "noscript", "svg"]): t.decompose()
    return re.sub(r"\n\s*\n+", "\n", s.get_text("\n"))
