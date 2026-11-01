var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// ../js/placement.js
function priceCents(cat, prodId, sides, size) {
  const p = cat.products.find((q) => q.id === prodId);
  return (sides >= 2 ? p.price.both : p.price.one) + (p.sur[size] || 0);
}
__name(priceCents, "priceCents");

// ../data/catalog.json
var catalog_default = {
  brand: {
    name: "AlphaDog Styles",
    tag: "Wear your best friend."
  },
  breeds: [
    {
      slug: "french_bulldog",
      name: "French Bulldog",
      desc: "bat-like erect ears, flat wrinkled face, compact body"
    },
    {
      slug: "labrador_retriever",
      name: "Labrador Retriever",
      desc: "short dense coat, broad head, medium floppy ears, thick otter tail"
    },
    {
      slug: "golden_retriever",
      name: "Golden Retriever",
      desc: "feathered medium-long coat, friendly face, floppy ears, plumed tail"
    },
    {
      slug: "german_shepherd",
      name: "German Shepherd",
      desc: "tall erect pointed ears, long muzzle, sloping back, bushy tail"
    },
    {
      slug: "dachshund",
      name: "Dachshund",
      desc: "very long low body, short legs, long drooping ears, smooth coat"
    },
    {
      slug: "poodle",
      name: "Standard Poodle",
      desc: "curly topknot, long drop ears with curly fur, long muzzle, curly coat"
    },
    {
      slug: "beagle",
      name: "Beagle",
      desc: "long drop ears, domed head, soft expression, white-tipped upright tail"
    },
    {
      slug: "rottweiler",
      name: "Rottweiler",
      desc: "broad powerful head, short coat, drop ears, muscular chest, stocky body"
    },
    {
      slug: "german_shorthaired_pointer",
      name: "German Shorthaired Pointer",
      desc: "sleek short coat, long drop ears, long muzzle, athletic lean body"
    },
    {
      slug: "bulldog",
      name: "English Bulldog",
      desc: "heavy wrinkled pushed-in face, rose ears, jowls, wide stocky body"
    },
    {
      slug: "cane_corso",
      name: "Cane Corso",
      desc: "large mastiff head, heavy muzzle, loose jowls, drop ears, muscular body"
    },
    {
      slug: "cavalier_king_charles_spaniel",
      name: "Cavalier King Charles Spaniel",
      desc: "long silky feathered drop ears, large round eyes, small body, feathered tail"
    },
    {
      slug: "yorkshire_terrier",
      name: "Yorkshire Terrier",
      desc: "tiny dog, long silky straight coat, small erect V ears, topknot"
    },
    {
      slug: "australian_shepherd",
      name: "Australian Shepherd",
      desc: "medium-long fluffy coat, semi-drop ears, bright eyes, bobbed tail"
    },
    {
      slug: "doberman_pinscher",
      name: "Doberman Pinscher",
      desc: "sleek short coat, erect pointed ears, long narrow muzzle, athletic body"
    },
    {
      slug: "pembroke_welsh_corgi",
      name: "Pembroke Welsh Corgi",
      desc: "large erect ears, fox-like face, short legs, long body, no tail"
    },
    {
      slug: "miniature_schnauzer",
      name: "Miniature Schnauzer",
      desc: "bushy eyebrows, beard and mustache, folded ears, wiry coat"
    },
    {
      slug: "boxer",
      name: "Boxer",
      desc: "square muzzle, short coat, folded ears, wrinkled forehead, muscular body"
    },
    {
      slug: "pomeranian",
      name: "Pomeranian",
      desc: "tiny fluffy dog, thick ruff of fur, fox face, small pointed ears, plumed tail curled over back"
    },
    {
      slug: "bernese_mountain_dog",
      name: "Bernese Mountain Dog",
      desc: "big fluffy thick coat, drop ears, gentle face, bushy tail"
    },
    {
      slug: "shih_tzu",
      name: "Shih Tzu",
      desc: "long flowing coat, flat short muzzle, drop ears, topknot"
    },
    {
      slug: "great_dane",
      name: "Great Dane",
      desc: "very tall, long deep muzzle, folded drop ears, deep chest, long legs"
    },
    {
      slug: "boston_terrier",
      name: "Boston Terrier",
      desc: "erect bat ears, square flat face, short muzzle, compact body"
    },
    {
      slug: "chihuahua",
      name: "Chihuahua",
      desc: "tiny dog, very large erect ears, apple-shaped head, big round eyes"
    },
    {
      slug: "havanese",
      name: "Havanese",
      desc: "silky wavy long coat, drop ears, small sturdy body, plumed tail curled over back"
    },
    {
      slug: "siberian_husky",
      name: "Siberian Husky",
      desc: "erect triangular ears, thick double coat"
    },
    {
      slug: "pug",
      name: "Pug",
      desc: "wrinkled flat face, curled tail"
    },
    {
      slug: "american_pit_bull_terrier",
      name: "American Pit Bull Terrier",
      desc: "muscular, blocky head"
    },
    {
      slug: "border_collie",
      name: "Border Collie",
      desc: "feathered coat, semi-erect ears"
    },
    {
      slug: "shiba_inu",
      name: "Shiba Inu",
      desc: "fox-like, curled tail"
    },
    {
      slug: "mini_poodle",
      name: "Mini Poodle",
      desc: "small, mid-length curly coat"
    },
    {
      slug: "bichon_frise",
      name: "Bichon Frise",
      desc: "round powder-puff"
    },
    {
      slug: "maltese",
      name: "Maltese",
      desc: "long silky coat"
    }
  ],
  themes: [
    {
      id: "line",
      name: "Continuous Line",
      blurb: "One flowing line, pure and elegant."
    },
    {
      id: "geo",
      name: "Geometric",
      blurb: "Sharp facets, bold modern attitude."
    }
  ],
  styles: [
    {
      id: "classic",
      name: "Classic",
      blurb: "The timeless portrait."
    },
    {
      id: "cool",
      name: "Cool",
      blurb: "Aviator sunglasses, zero worries."
    },
    {
      id: "heart",
      name: "Heart",
      blurb: "Framed in a heart, made with love."
    }
  ],
  parts: [
    {
      id: "head",
      name: "Head",
      file: "front"
    },
    {
      id: "body",
      name: "Full Body",
      file: "back"
    }
  ],
  front_opts: [
    {
      id: "none",
      name: "Nothing"
    },
    {
      id: "head_s",
      name: "Head emblem",
      part: "head",
      size: "s"
    },
    {
      id: "head_l",
      name: "Big head",
      part: "head",
      size: "l"
    },
    {
      id: "body_s",
      name: "Body emblem",
      part: "body",
      size: "s"
    },
    {
      id: "body_l",
      name: "Big body",
      part: "body",
      size: "l"
    }
  ],
  back_opts: [
    {
      id: "none",
      name: "Nothing"
    },
    {
      id: "head_l",
      name: "Big head",
      part: "head",
      size: "l"
    },
    {
      id: "body_l",
      name: "Full body",
      part: "body",
      size: "l"
    },
    {
      id: "body_s",
      name: "Body emblem",
      part: "body",
      size: "s"
    },
    {
      id: "head_s",
      name: "Head emblem",
      part: "head",
      size: "s"
    }
  ],
  products: [
    {
      id: "tee",
      name: "Premium Tee",
      sub: "Bella+Canvas 3001 - soft Airlume cotton",
      blueprint: 12,
      provider: 99,
      price: {
        one: 2799,
        both: 3299
      },
      sur: {
        "2XL": 200,
        "3XL": 400
      },
      colors: [
        [
          "White",
          "#f3f4f4",
          1,
          "white"
        ],
        [
          "Natural",
          "#f6f0e2",
          1,
          "natural"
        ],
        [
          "Soft Cream",
          "#f0ddcc",
          1,
          "soft-cream"
        ],
        [
          "Ash",
          "#ebeceb",
          1,
          "ash"
        ],
        [
          "Athletic Heather",
          "#a8a8a6",
          1,
          "athletic-heather"
        ],
        [
          "Light Blue",
          "#b4bec8",
          1,
          "light-blue"
        ],
        [
          "Soft Pink",
          "#f7e2dd",
          1,
          "soft-pink"
        ],
        [
          "Black",
          "#16161A",
          0,
          "black"
        ],
        [
          "Navy",
          "#1F2A44",
          0,
          "navy"
        ],
        [
          "Forest",
          "#24402F",
          0,
          "forest"
        ],
        [
          "Maroon",
          "#5A1E2B",
          0,
          "maroon"
        ]
      ],
      sizes: [
        "S",
        "M",
        "L",
        "XL",
        "2XL",
        "3XL"
      ]
    },
    {
      id: "hoodie",
      name: "Heavy Hoodie",
      sub: "Gildan 18500 - cozy heavy blend",
      blueprint: 77,
      provider: 99,
      price: {
        one: 4999,
        both: 5799
      },
      sur: {
        "2XL": 400,
        "3XL": 800
      },
      colors: [
        [
          "White",
          "#eaebeb",
          1,
          "white"
        ],
        [
          "Sand",
          "#d0c3af",
          1,
          "sand"
        ],
        [
          "Sport Grey",
          "#a2a3a4",
          1,
          "sport-grey"
        ],
        [
          "Light Blue",
          "#c7d8eb",
          1,
          "light-blue"
        ],
        [
          "Light Pink",
          "#efd1dd",
          1,
          "light-pink"
        ],
        [
          "Ash",
          "#d5d5d5",
          1,
          "ash"
        ],
        [
          "Black",
          "#17171B",
          0,
          "black"
        ],
        [
          "Navy",
          "#1E2A47",
          0,
          "navy"
        ],
        [
          "Forest",
          "#23402F",
          0,
          "forest"
        ],
        [
          "Maroon",
          "#5B1F2C",
          0,
          "maroon"
        ]
      ],
      sizes: [
        "S",
        "M",
        "L",
        "XL",
        "2XL",
        "3XL"
      ]
    }
  ],
  shipping: {
    flat: 499,
    free_over: 7500
  },
  area: {
    tee: {
      w: 2767,
      h: 3362
    },
    hoodie_front: {
      w: 3531,
      h: 2352
    },
    hoodie_back: {
      w: 3852,
      h: 3210
    }
  },
  cal: {
    tee: {
      front: [
        387.6,
        373,
        424.2,
        515.4
      ],
      back: [
        403.5,
        303.2,
        409.5,
        497.6
      ]
    },
    hoodie: {
      front: [
        424.5,
        395.1,
        334,
        222.7
      ],
      back: [
        441.7,
        368.9,
        341.6,
        284.6
      ]
    },
    photo: 1200
  }
};

// index.js
var J = /* @__PURE__ */ __name((o, s = 200, h = {}) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json", "cache-control": "no-store", ...h } }), "J");
var err = /* @__PURE__ */ __name((m, s = 400) => J({ error: m }, s), "err");
var now = /* @__PURE__ */ __name(() => Date.now(), "now");
var hex = /* @__PURE__ */ __name((b) => [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join(""), "hex");
var sha = /* @__PURE__ */ __name(async (s) => hex(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s))), "sha");
var rnd = /* @__PURE__ */ __name((n) => hex(crypto.getRandomValues(new Uint8Array(n))), "rnd");
var okEmail = /* @__PURE__ */ __name((e) => typeof e === "string" && e.length < 255 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e), "okEmail");
async function mail(env, to, subject, html) {
  if (env.RESEND_API_KEY) {
    const r = await fetch("https://api.resend.com/emails", { method: "POST", headers: { authorization: "Bearer " + env.RESEND_API_KEY, "content-type": "application/json" }, body: JSON.stringify({ from: env.MAIL_FROM, to: [to], subject, html }) });
    return r.ok;
  }
  return false;
}
__name(mail, "mail");
var b64u = /* @__PURE__ */ __name((b) => btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""), "b64u");
var b64uJ = /* @__PURE__ */ __name((o) => b64u(new TextEncoder().encode(JSON.stringify(o))), "b64uJ");
var unb64 = /* @__PURE__ */ __name((s) => {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  return atob(s + "=".repeat((4 - s.length % 4) % 4));
}, "unb64");
function providers(env) {
  return { google: !!(env.GOOGLE_CLIENT_ID && env.GOOGLE_CLIENT_SECRET), facebook: !!(env.FACEBOOK_APP_ID && env.FACEBOOK_APP_SECRET), apple: !!(env.APPLE_CLIENT_ID && env.APPLE_TEAM_ID && env.APPLE_KEY_ID && env.APPLE_PRIVATE_KEY) };
}
__name(providers, "providers");
async function appleSecret(env) {
  const pem = env.APPLE_PRIVATE_KEY.replace(/\\n/g, "\n").replace(/-----[^-]+-----/g, "").replace(/\s+/g, "");
  const key = await crypto.subtle.importKey("pkcs8", Uint8Array.from(atob(pem), (c) => c.charCodeAt(0)), { name: "ECDSA", namedCurve: "P-256" }, false, ["sign"]);
  const head = b64uJ({ alg: "ES256", kid: env.APPLE_KEY_ID }), t = Math.floor(Date.now() / 1e3), pl = b64uJ({ iss: env.APPLE_TEAM_ID, iat: t, exp: t + 600, aud: "https://appleid.apple.com", sub: env.APPLE_CLIENT_ID });
  const sig = await crypto.subtle.sign({ name: "ECDSA", hash: "SHA-256" }, key, new TextEncoder().encode(head + "." + pl));
  return head + "." + pl + "." + b64u(sig);
}
__name(appleSecret, "appleSecret");
var OAUTH = {
  google: { auth: "https://accounts.google.com/o/oauth2/v2/auth", scope: "openid email", id: /* @__PURE__ */ __name((e) => e.GOOGLE_CLIENT_ID, "id"), extra: {} },
  facebook: { auth: "https://www.facebook.com/v19.0/dialog/oauth", scope: "email public_profile", id: /* @__PURE__ */ __name((e) => e.FACEBOOK_APP_ID, "id"), extra: {} },
  apple: { auth: "https://appleid.apple.com/auth/authorize", scope: "name email", id: /* @__PURE__ */ __name((e) => e.APPLE_CLIENT_ID, "id"), extra: { response_mode: "form_post" } }
};
async function oauthEmail(prov, code, redirect, env) {
  if (prov === "google") {
    const t2 = await (await fetch("https://oauth2.googleapis.com/token", { method: "POST", body: new URLSearchParams({ code, client_id: env.GOOGLE_CLIENT_ID, client_secret: env.GOOGLE_CLIENT_SECRET, redirect_uri: redirect, grant_type: "authorization_code" }) })).json();
    if (!t2.access_token) throw new Error("Google sign-in failed");
    const u = await (await fetch("https://openidconnect.googleapis.com/v1/userinfo", { headers: { authorization: "Bearer " + t2.access_token } })).json();
    if (!u.email || u.email_verified === false) throw new Error("Google did not share a verified email");
    return u.email;
  }
  if (prov === "facebook") {
    const t2 = await (await fetch("https://graph.facebook.com/v19.0/oauth/access_token?" + new URLSearchParams({ client_id: env.FACEBOOK_APP_ID, client_secret: env.FACEBOOK_APP_SECRET, redirect_uri: redirect, code }))).json();
    if (!t2.access_token) throw new Error("Facebook sign-in failed");
    const u = await (await fetch("https://graph.facebook.com/me?fields=email&access_token=" + t2.access_token)).json();
    if (!u.email) throw new Error("Facebook did not share your email. Please allow email access or use another sign-in.");
    return u.email;
  }
  const t = await (await fetch("https://appleid.apple.com/auth/token", { method: "POST", body: new URLSearchParams({ code, client_id: env.APPLE_CLIENT_ID, client_secret: await appleSecret(env), redirect_uri: redirect, grant_type: "authorization_code" }) })).json();
  if (!t.id_token) throw new Error("Apple sign-in failed");
  const pl = JSON.parse(unb64(t.id_token.split(".")[1]));
  if (!pl.email) throw new Error("Apple did not share an email");
  return pl.email;
}
__name(oauthEmail, "oauthEmail");
async function startSession(env, email) {
  email = email.toLowerCase();
  await env.DB.prepare("INSERT OR IGNORE INTO users(email,created) VALUES(?,?)").bind(email, now()).run();
  const token = rnd(32);
  await env.DB.prepare("INSERT INTO sessions(hash,email,exp) VALUES(?,?,?)").bind(await sha(token), email, now() + 30 * 864e5).run();
  return token;
}
__name(startSession, "startSession");
async function auth(req, env) {
  const t = (req.headers.get("authorization") || "").replace(/^Bearer /, "");
  if (!t) return null;
  const r = await env.DB.prepare("SELECT email,exp FROM sessions WHERE hash=?").bind(await sha(t)).first();
  return r && r.exp > now() ? r.email : null;
}
__name(auth, "auth");
function validItem(it) {
  const p = catalog_default.products.find((x) => x.id === it.prod);
  if (!p) return null;
  const c = p.colors.find((x) => x[0] === it.color && x[2]);
  if (!c || !p.sizes.includes(it.size)) return null;
  const qty = Math.max(1, Math.min(20, parseInt(it.qty) || 1));
  const side = /* @__PURE__ */ __name((d, k) => {
    if (!d) return null;
    const o = catalog_default[k + "_opts"].find((x) => x.part === d.part && x.size === d.size);
    if (!o || !catalog_default.breeds.some((b) => b.slug === d.breed) || !catalog_default.themes.some((t) => t.id === d.theme) || !catalog_default.styles.some((s) => s.id === d.style)) return false;
    return { part: d.part, size: d.size, breed: d.breed, theme: d.theme, style: d.style };
  }, "side");
  const front = side(it.front, "front"), back = side(it.back, "back");
  if (front === false || back === false || !front && !back) return null;
  return { prod: it.prod, color: it.color, size: it.size, qty, front, back };
}
__name(validItem, "validItem");
var index_default = {
  async fetch(req, env) {
    const u = new URL(req.url), path = u.pathname, m = req.method;
    if (!path.startsWith("/api/")) return env.ASSETS.fetch(req);
    let body = {};
    if ((m === "POST" || m === "PUT") && !path.includes("/oauth/")) {
      try {
        body = await req.json();
      } catch {
        return err("Bad JSON");
      }
    }
    try {
      if (path === "/api/health") return J({ ok: true, mail: !!env.RESEND_API_KEY || env.DEV_MODE === "1", providers: providers(env) });
      if (path === "/api/auth/request" && m === "POST") {
        const email = String(body.email || "").trim().toLowerCase();
        if (!okEmail(email)) return err("Enter a valid email");
        const prev = await env.DB.prepare("SELECT sent FROM codes WHERE email=?").bind(email).first();
        if (prev && now() - prev.sent < 45e3) return err("Please wait a moment before requesting another code", 429);
        const code = String(1e5 + crypto.getRandomValues(new Uint32Array(1))[0] % 9e5);
        await env.DB.prepare("INSERT OR REPLACE INTO codes(email,hash,exp,tries,sent) VALUES(?,?,?,?,?)").bind(email, await sha(email + code), now() + 10 * 6e4, 0, now()).run();
        const sent = await mail(env, email, "Your AlphaDog Styles login code", `<div style="font-family:system-ui;max-width:420px;margin:auto"><h2>Your code: <b style="letter-spacing:4px">${code}</b></h2><p>It expires in 10 minutes. If you did not ask for it, ignore this email.</p></div>`);
        if (!sent && env.DEV_MODE === "1") return J({ ok: true, dev_code: code });
        if (!sent) return err("Email service is not configured yet", 503);
        return J({ ok: true });
      }
      if (path === "/api/auth/verify" && m === "POST") {
        const email = String(body.email || "").trim().toLowerCase(), code = String(body.code || "");
        const r = await env.DB.prepare("SELECT hash,exp,tries FROM codes WHERE email=?").bind(email).first();
        if (!r || r.exp < now() || r.tries >= 5) return err("Code expired. Request a new one.");
        if (r.hash !== await sha(email + code)) {
          await env.DB.prepare("UPDATE codes SET tries=tries+1 WHERE email=?").bind(email).run();
          return err("That code is not right");
        }
        await env.DB.prepare("DELETE FROM codes WHERE email=?").bind(email).run();
        await env.DB.prepare("INSERT OR IGNORE INTO users(email,created) VALUES(?,?)").bind(email, now()).run();
        const token = rnd(32);
        await env.DB.prepare("INSERT INTO sessions(hash,email,exp) VALUES(?,?,?)").bind(await sha(token), email, now() + 30 * 864e5).run();
        return J({ token, email });
      }
      let om;
      if (om = path.match(/^\/api\/auth\/oauth\/(google|facebook|apple)\/(start|callback)$/)) {
        const prov = om[1], cfg = OAUTH[prov], redirect = u.origin + "/api/auth/oauth/" + prov + "/callback";
        if (!providers(env)[prov]) return err("This sign-in is not enabled yet", 503);
        if (om[2] === "start") {
          const state2 = rnd(16);
          await env.DB.prepare("INSERT INTO oauth_states(state,prov,next,exp) VALUES(?,?,?,?)").bind(state2, prov, (u.searchParams.get("next") || "account").replace(/[^\w/?=&-]/g, "").slice(0, 60), now() + 10 * 6e4).run();
          const q = new URLSearchParams({ client_id: cfg.id(env), redirect_uri: redirect, response_type: "code", scope: cfg.scope, state: state2, ...cfg.extra });
          return Response.redirect(cfg.auth + "?" + q, 302);
        }
        let code, state;
        if (m === "POST") {
          const f = await req.formData();
          code = f.get("code");
          state = f.get("state");
        } else {
          code = u.searchParams.get("code");
          state = u.searchParams.get("state");
        }
        const st = await env.DB.prepare("SELECT next,exp FROM oauth_states WHERE state=? AND prov=?").bind(state || "", prov).first();
        await env.DB.prepare("DELETE FROM oauth_states WHERE state=?").bind(state || "").run();
        if (!st || st.exp < now() || !code) return Response.redirect(u.origin + "/#/login?err=" + encodeURIComponent("Sign-in was cancelled or expired"), 302);
        try {
          const email = await oauthEmail(prov, code, redirect, env);
          const token = await startSession(env, email);
          return Response.redirect(u.origin + "/#/auth?token=" + token + "&email=" + encodeURIComponent(email.toLowerCase()) + "&next=" + st.next, 302);
        } catch (e) {
          return Response.redirect(u.origin + "/#/login?err=" + encodeURIComponent(e.message), 302);
        }
      }
      if (path === "/api/subscribe" && m === "POST") {
        const e = String(body.email || "").toLowerCase();
        if (!okEmail(e)) return err("Enter a valid email");
        await env.DB.prepare("INSERT OR IGNORE INTO subs(email,created) VALUES(?,?)").bind(e, now()).run();
        return J({ ok: true });
      }
      if (path === "/api/contact" && m === "POST") {
        if (!okEmail(body.email) || !body.msg) return err("Email and message required");
        await env.DB.prepare("INSERT INTO msgs(email,body,created) VALUES(?,?,?)").bind(body.email, String(body.msg).slice(0, 4e3), now()).run();
        return J({ ok: true });
      }
      if (path === "/api/orders" && m === "POST") {
        const items = (Array.isArray(body.items) ? body.items : []).map(validItem);
        if (!items.length || items.length > 30 || items.includes(null)) return err("Your cart has an invalid item");
        const s = body.ship || {};
        for (const k of ["name", "a1", "city", "st", "zip"]) if (!s[k] || String(s[k]).length > 120) return err("Please complete the shipping address");
        if (!/^\d{5}(-\d{4})?$/.test(s.zip)) return err("Enter a valid US ZIP code");
        if (!okEmail(body.email)) return err("Enter a valid email");
        const sub = items.reduce((a, i) => a + priceCents(catalog_default, i.prod, (i.front ? 1 : 0) + (i.back ? 1 : 0), i.size) * i.qty, 0);
        const ship = sub >= catalog_default.shipping.free_over ? 0 : catalog_default.shipping.flat, total = sub + ship;
        const id = "AD-" + rnd(4).toUpperCase(), email = String(body.email).toLowerCase();
        const data = { items, ship: { name: s.name, a1: s.a1, a2: s.a2 || "", city: s.city, st: s.st, zip: s.zip, phone: s.phone || "" }, subtotal: sub, shipping: ship };
        await env.DB.prepare("INSERT INTO orders(id,email,data,total,status,created,updated) VALUES(?,?,?,?,?,?,?)").bind(id, email, JSON.stringify(data), total, "reserved", now(), now()).run();
        await mail(env, email, `Order ${id} reserved`, `<p>Thanks for your order <b>${id}</b>. We will email you a secure payment link as soon as checkout opens.</p><p>Total: $${(total / 100).toFixed(2)}</p>`);
        return J({ id, total });
      }
      if (path === "/api/orders" && m === "GET") {
        const e = await auth(req, env);
        if (!e) return err("Log in first", 401);
        const r = await env.DB.prepare("SELECT id,status,total,tracking,created FROM orders WHERE email=? ORDER BY created DESC LIMIT 100").bind(e).all();
        return J({ items: r.results });
      }
      if (path === "/api/designs") {
        const e = await auth(req, env);
        if (!e) return err("Log in first", 401);
        if (m === "GET") {
          const r = await env.DB.prepare("SELECT id,data FROM designs WHERE email=? ORDER BY created DESC LIMIT 200").bind(e).all();
          return J({ items: r.results.map((x) => ({ id: x.id, s: JSON.parse(x.data) })) });
        }
        if (m === "POST") {
          const id = String(body.id || rnd(6));
          await env.DB.prepare("INSERT OR REPLACE INTO designs(id,email,data,created) VALUES(?,?,?,?)").bind(id, e, JSON.stringify(body.s || {}).slice(0, 6e3), now()).run();
          return J({ id });
        }
      }
      let mm;
      if ((mm = path.match(/^\/api\/designs\/([\w-]+)$/)) && m === "DELETE") {
        const e = await auth(req, env);
        if (!e) return err("Log in first", 401);
        await env.DB.prepare("DELETE FROM designs WHERE id=? AND email=?").bind(mm[1], e).run();
        return J({ ok: true });
      }
      if (path.startsWith("/api/internal/")) {
        if (!env.ADMIN_TOKEN || req.headers.get("x-admin-token") !== env.ADMIN_TOKEN) return err("Forbidden", 403);
        if (path === "/api/internal/orders" && m === "GET") {
          const st = u.searchParams.get("status") || "paid";
          const r = await env.DB.prepare("SELECT id,email,data,total,status,printify_id FROM orders WHERE status=? ORDER BY created LIMIT 50").bind(st).all();
          return J({ items: r.results.map((x) => ({ ...x, data: JSON.parse(x.data) })) });
        }
        if (mm = path.match(/^\/api\/internal\/orders\/([\w-]+)$/) && m === "POST") {
          const o = await env.DB.prepare("SELECT email FROM orders WHERE id=?").bind(mm[1]).first();
          if (!o) return err("No such order", 404);
          await env.DB.prepare("UPDATE orders SET status=COALESCE(?,status),printify_id=COALESCE(?,printify_id),tracking=COALESCE(?,tracking),updated=? WHERE id=?").bind(body.status || null, body.printify_id || null, body.tracking || null, now(), mm[1]).run();
          if (body.status === "shipped") await mail(env, o.email, `Order ${mm[1]} has shipped`, `<p>Your AlphaDog order is on its way.</p>${body.tracking ? `<p><a href="${body.tracking}">Track your package</a></p>` : ""}`);
          return J({ ok: true });
        }
      }
      return err("Not found", 404);
    } catch (e) {
      return err("Server error: " + e.message, 500);
    }
  }
};

// ../../../.npm/_npx/c943b712072b77c4/node_modules/wrangler/templates/middleware/middleware-ensure-req-body-drained.ts
var drainBody = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } finally {
    try {
      if (request.body !== null && !request.bodyUsed) {
        const reader = request.body.getReader();
        while (!(await reader.read()).done) {
        }
      }
    } catch (e) {
      console.error("Failed to drain the unused request body.", e);
    }
  }
}, "drainBody");
var middleware_ensure_req_body_drained_default = drainBody;

// ../../../.npm/_npx/c943b712072b77c4/node_modules/wrangler/templates/middleware/middleware-miniflare3-json-error.ts
function reduceError(e) {
  return {
    name: e?.name,
    message: e?.message ?? String(e),
    stack: e?.stack,
    cause: e?.cause === void 0 ? void 0 : reduceError(e.cause)
  };
}
__name(reduceError, "reduceError");
var jsonError = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } catch (e) {
    const error = reduceError(e);
    const body = JSON.stringify(error);
    const headers = {
      "Content-Type": "application/json",
      "MF-Experimental-Error-Stack": "true"
    };
    const encoded = encodeURIComponent(body);
    if (encoded.length <= 8192) {
      headers["MF-Experimental-Error-Stack-Payload"] = encoded;
    }
    return new Response(body, { status: 500, headers });
  }
}, "jsonError");
var middleware_miniflare3_json_error_default = jsonError;

// .wrangler/tmp/bundle-ZQOrKR/middleware-insertion-facade.js
var __INTERNAL_WRANGLER_MIDDLEWARE__ = [
  middleware_ensure_req_body_drained_default,
  middleware_miniflare3_json_error_default
];
var middleware_insertion_facade_default = index_default;

// ../../../.npm/_npx/c943b712072b77c4/node_modules/wrangler/templates/middleware/common.ts
var __facade_middleware__ = [];
function __facade_register__(...args) {
  __facade_middleware__.push(...args.flat());
}
__name(__facade_register__, "__facade_register__");
function __facade_invokeChain__(request, env, ctx, dispatch, middlewareChain) {
  const [head, ...tail] = middlewareChain;
  const middlewareCtx = {
    dispatch,
    next(newRequest, newEnv) {
      return __facade_invokeChain__(newRequest, newEnv, ctx, dispatch, tail);
    }
  };
  return head(request, env, ctx, middlewareCtx);
}
__name(__facade_invokeChain__, "__facade_invokeChain__");
function __facade_invoke__(request, env, ctx, dispatch, finalMiddleware) {
  return __facade_invokeChain__(request, env, ctx, dispatch, [
    ...__facade_middleware__,
    finalMiddleware
  ]);
}
__name(__facade_invoke__, "__facade_invoke__");

// .wrangler/tmp/bundle-ZQOrKR/middleware-loader.entry.ts
var __Facade_ScheduledController__ = class ___Facade_ScheduledController__ {
  constructor(scheduledTime, cron, noRetry) {
    this.scheduledTime = scheduledTime;
    this.cron = cron;
    this.#noRetry = noRetry;
  }
  scheduledTime;
  cron;
  static {
    __name(this, "__Facade_ScheduledController__");
  }
  #noRetry;
  noRetry() {
    if (!(this instanceof ___Facade_ScheduledController__)) {
      throw new TypeError("Illegal invocation");
    }
    this.#noRetry();
  }
};
function wrapExportedHandler(worker) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return worker;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  const fetchDispatcher = /* @__PURE__ */ __name(function(request, env, ctx) {
    if (worker.fetch === void 0) {
      throw new Error("Handler does not export a fetch() function.");
    }
    return worker.fetch(request, env, ctx);
  }, "fetchDispatcher");
  return {
    ...worker,
    fetch(request, env, ctx) {
      const dispatcher = /* @__PURE__ */ __name(function(type, init) {
        if (type === "scheduled" && worker.scheduled !== void 0) {
          const controller = new __Facade_ScheduledController__(
            Date.now(),
            init.cron ?? "",
            () => {
            }
          );
          return worker.scheduled(controller, env, ctx);
        }
      }, "dispatcher");
      return __facade_invoke__(request, env, ctx, dispatcher, fetchDispatcher);
    }
  };
}
__name(wrapExportedHandler, "wrapExportedHandler");
function wrapWorkerEntrypoint(klass) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return klass;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  return class extends klass {
    #fetchDispatcher = /* @__PURE__ */ __name((request, env, ctx) => {
      this.env = env;
      this.ctx = ctx;
      if (super.fetch === void 0) {
        throw new Error("Entrypoint class does not define a fetch() function.");
      }
      return super.fetch(request);
    }, "#fetchDispatcher");
    #dispatcher = /* @__PURE__ */ __name((type, init) => {
      if (type === "scheduled" && super.scheduled !== void 0) {
        const controller = new __Facade_ScheduledController__(
          Date.now(),
          init.cron ?? "",
          () => {
          }
        );
        return super.scheduled(controller);
      }
    }, "#dispatcher");
    fetch(request) {
      return __facade_invoke__(
        request,
        this.env,
        this.ctx,
        this.#dispatcher,
        this.#fetchDispatcher
      );
    }
  };
}
__name(wrapWorkerEntrypoint, "wrapWorkerEntrypoint");
var WRAPPED_ENTRY;
if (typeof middleware_insertion_facade_default === "object") {
  WRAPPED_ENTRY = wrapExportedHandler(middleware_insertion_facade_default);
} else if (typeof middleware_insertion_facade_default === "function") {
  WRAPPED_ENTRY = wrapWorkerEntrypoint(middleware_insertion_facade_default);
}
var middleware_loader_entry_default = WRAPPED_ENTRY;
export {
  __INTERNAL_WRANGLER_MIDDLEWARE__,
  middleware_loader_entry_default as default
};
//# sourceMappingURL=index.js.map
