import {renderSVG,artUrl,setCal} from "./garment.js";
import {priceCents} from "./placement.js";
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const app=$("#app"); let cat,cfg={api:""};
const money=c=>"$"+(c/100).toFixed(2);
const ls={get:(k,d)=>{try{return JSON.parse(localStorage.getItem(k))??d}catch{return d}},set:(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch{}}};
let cart=ls.get("ad_cart",[]), user=ls.get("ad_user",null);
const saveCart=()=>{ls.set("ad_cart",cart);$("#cartn").textContent=cart.reduce((a,l)=>a+l.qty,0)};
function toast(m){const t=$("#toast");t.textContent=m;t.classList.add("show");clearTimeout(toast.t);toast.t=setTimeout(()=>t.classList.remove("show"),2600)}
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const breedName=s=>cat.breeds.find(b=>b.slug===s)?.name||s;
const themeName=t=>cat.themes.find(x=>x.id===t).name, styleName=t=>cat.styles.find(x=>x.id===t).name;
const designLabel=d=>d?`${breedName(d.breed)} · ${themeName(d.theme)} ${styleName(d.style)} · ${d.part==="head"?"Head":"Body"} ${d.size==="s"?"emblem":"large"}`:"";
/* ---------- api (falls back to local preview mode when no backend is configured) ---------- */
async function api(path,body,method){
  if(!cfg.api) throw new Error("preview");
  const r=await fetch((cfg.api==="same"?"":cfg.api)+path,{method:method||(body?"POST":"GET"),headers:{"content-type":"application/json",...(user?{authorization:"Bearer "+user.token}:{})},body:body?JSON.stringify(body):undefined});
  const j=await r.json().catch(()=>({})); if(!r.ok) throw new Error(j.error||"Request failed"); return j;
}
/* ---------- design model ---------- */
const newSide=(opt,b)=>({opt,breed:b||"french_bulldog",theme:"line",style:"classic"});
function toDesign(side,kind){const o=cat[kind+"_opts"].find(x=>x.id===side.opt);return o&&o.part?{part:o.part,size:o.size,breed:side.breed,theme:side.theme,style:side.style}:null}
function priceOf(l){return priceCents(cat,l.prod,(l.front?1:0)+(l.back?1:0),l.size)}
/* ---------- router ---------- */
const routes={"":home,shop,design,cart:cartPage,checkout,account,login,page,done,auth};
async function route(){
  const h=location.hash.replace(/^#\/?/,""),[path,qs]=h.split("?"),parts=path.split("/"),q=Object.fromEntries(new URLSearchParams(qs||""));
  $("#links").classList.remove("open");
  $$("#links a").forEach(a=>a.classList.toggle("on",a.getAttribute("href")==="#/"+parts[0]));
  const fn=routes[parts[0]]||notFound; app.onclick=null; app.innerHTML=""; window.scrollTo(0,0);
  await fn(q,parts.slice(1)); document.title=(app.dataset.title||"AlphaDog Styles")+" - AlphaDog Styles";
}
function notFound(){app.innerHTML=`<div class="wrap narrow"><h1>Lost dog?</h1><p>That page wandered off. <a href="#/shop" class="btn">Back to the shop</a></p></div>`}
/* ---------- cards ---------- */
const designCard=(b,t,s)=>`<a class="card" href="#/design?breed=${b}&theme=${t}&style=${s}"><div class="art"><img loading="lazy" alt="${esc(breedName(b))} ${t} ${s} design" src="art/${t}_${s}/${b}_front.svg"></div><div class="meta"><b>${esc(breedName(b))}</b><span>${themeName(t)} · ${styleName(s)}</span></div></a>`;
function pick(arr,n,seed){let a=[...arr],r=seed;const o=[];while(o.length<n&&a.length){r=(r*9301+49297)%233280;o.push(a.splice(Math.floor(r/233280*a.length),1)[0])}return o}
/* ---------- pages ---------- */
async function home(){
  app.dataset.title="Wear your best friend";
  const day=Math.floor(Date.now()/864e5), feat=pick(cat.breeds,8,day).map((b,i)=>designCard(b.slug,cat.themes[i%2].id,cat.styles[(i+day)%3].id)).join("");
  const names=cat.breeds.map(b=>b.name).join(`<em>✦</em>`);
  app.innerHTML=`<div class="wrap hero"><div><span class="eyebrow">Made to order · Shipped across the US</span><h1>Your best friend, on your best tee.</h1><p>33 breeds, 2 art styles, 3 moods and every placement you can imagine. Design it your way, we print it just for you.</p><div class="cta"><a class="btn" href="#/design">Design yours</a><a class="btn ghost" href="#/shop">Browse designs</a></div></div><div class="stage" id="stage"><div class="blob" style="width:180px;height:180px;background:#ffd8a8;top:-40px;right:-30px"></div><div class="blob" style="width:120px;height:120px;background:#fff1d6;bottom:20px;left:-30px"></div></div></div>
  <div class="marquee"><span>${names}<em>✦</em>${names}<em>✦</em></span></div>
  <section class="sec"><div class="wrap"><div class="sh"><div><h2>Fresh from the kennel</h2><p>Today's picks. Tap any design to make it yours.</p></div><a class="btn ghost sm" href="#/shop">See all 198 designs</a></div><div class="grid">${feat}</div></div></section>
  <section class="sec"><div class="wrap"><div class="sh"><div><h2>Real garments, real art</h2><p>Premium tees and hoodies, printed to order.</p></div><a class="btn ghost sm" href="#/design">Design yours</a></div><div class="look">${[1,2,3,4,5,6].map(i=>`<a href="#/design"><img loading="lazy" alt="Printed tee mockup ${i}" src="img/look-${i}.webp"></a>`).join("")}</div></div></section>
  <section class="sec alt"><div class="wrap"><div class="sh"><div><h2>Three simple steps</h2></div></div><div class="steps"><div class="step"><i>1</i><h3>Pick your pup</h3><p>Choose from 33 breeds, in continuous line or geometric art, in Classic, Cool or Heart.</p></div><div class="step"><i>2</i><h3>Make it yours</h3><p>Front, back or both. Head or full body, small emblem or big statement. Different dogs on each side? Go for it.</p></div><div class="step"><i>3</i><h3>We print and ship</h3><p>Every piece is printed to order on premium blanks and shipped to your door.</p></div></div></div></section>
  <section class="sec"><div class="wrap"><div class="feat"><div><h3>Premium blanks</h3><p>Soft Bella+Canvas tees and cozy heavyweight hoodies that survive wash after wash.</p></div><div><h3>Truly custom</h3><p>You choose breed, style, placement and color. No two combinations look the same.</p></div><div><h3>Printed on demand</h3><p>Nothing sits in a warehouse. Your order is made when you order it.</p></div><div><h3>Easy help</h3><p>Questions? We answer fast. See our <a href="#/page/faq"><u>FAQ</u></a>.</p></div></div></div></section>`;
  const st=$("#stage"); st.insertAdjacentHTML("beforeend",await renderSVG("tee","front",cat.products[0].colors[1],{part:"head",size:"l",breed:"poodle",theme:"line",style:"classic"}));
}
function shop(q){
  app.dataset.title="Shop";
  const f={t:q.theme||"",s:q.style||"",q:""};
  app.innerHTML=`<div class="wrap" style="padding-top:34px"><h1 style="font-size:clamp(2rem,4vw,3rem)">Shop all designs</h1><div class="tools"><input id="sq" placeholder="Search a breed…" aria-label="Search breeds"><div class="chips" id="ft"></div><div class="chips" id="fs"></div></div><div class="grid" id="sg"></div><p id="none" hidden>No designs match. Try another breed.</p></div>`;
  const draw=()=>{
    $("#ft").innerHTML=`<button class="chip ${f.t?"":"on"}" data-t="">All styles</button>`+cat.themes.map(t=>`<button class="chip ${f.t===t.id?"on":""}" data-t="${t.id}">${t.name}</button>`).join("");
    $("#fs").innerHTML=`<button class="chip ${f.s?"":"on"}" data-s="">All moods</button>`+cat.styles.map(t=>`<button class="chip ${f.s===t.id?"on":""}" data-s="${t.id}">${t.name}</button>`).join("");
    const out=[];for(const b of cat.breeds){if(f.q&&!b.name.toLowerCase().includes(f.q))continue;for(const t of cat.themes){if(f.t&&f.t!==t.id)continue;for(const s of cat.styles){if(f.s&&f.s!==s.id)continue;out.push(designCard(b.slug,t.id,s.id))}}}
    $("#sg").innerHTML=out.join("");$("#none").hidden=!!out.length};
  draw();
  $("#sq").oninput=e=>{f.q=e.target.value.trim().toLowerCase();draw()};
  app.onclick=e=>{const c=e.target.closest(".chip");if(!c)return;if("t"in c.dataset)f.t=c.dataset.t;if("s"in c.dataset)f.s=c.dataset.s;draw()};
}
/* ---------- customizer ---------- */
async function design(q){
  app.dataset.title="Design yours";
  let S=window.__edit||null; window.__edit=null;
  if(!S){const b=q.breed&&cat.breeds.some(x=>x.slug===q.breed)?q.breed:"french_bulldog";S={prod:"tee",color:"White",size:"M",qty:1,view:"front",front:newSide("head_s",b),back:newSide("body_l",b)};if(q.theme){S.front.theme=S.back.theme=q.theme}if(q.style){S.front.style=S.back.style=q.style}}
  const P=()=>cat.products.find(p=>p.id===S.prod);
  const hex=()=>(P().colors.find(c=>c[0]===S.color)||P().colors[0]);
  app.innerHTML=`<div class="wrap"><p class="crumbs"><a href="#/shop">Shop</a> / Design yours</p><div class="dz"><div class="pv"><div class="pvbox" id="pv"></div><div class="pvtabs"><button class="chip" data-v="front">Front</button><button class="chip" data-v="back">Back</button></div><p style="text-align:center;color:var(--mut);font-size:.85rem">Preview is illustrative. Actual print is crisp on premium fabric.</p></div><div id="ctl"></div></div></div>`;
  const sideUI=(k)=>{const s=S[k],opts=cat[k+"_opts"];return `<div class="panel"><h3>${k==="front"?"Front design":"Back design"}</h3><div class="chips" style="margin-bottom:12px">${opts.map(o=>`<button class="chip ${s.opt===o.id?"on":""}" data-k="${k}" data-opt="${o.id}">${o.name}</button>`).join("")}</div>${s.opt==="none"?`<small style="color:var(--mut)">No print on the ${k}.</small>`:`<label style="font-weight:600;font-size:.9rem">Breed<select data-k="${k}" data-f="breed">${cat.breeds.map(b=>`<option value="${b.slug}" ${b.slug===s.breed?"selected":""}>${esc(b.name)}</option>`).join("")}</select></label><div class="seg" style="margin-top:10px">${cat.themes.map(t=>`<button class="${s.theme===t.id?"on":""}" data-k="${k}" data-f="theme" data-v="${t.id}">${t.name}</button>`).join("")}</div><div class="seg" style="margin-top:8px">${cat.styles.map(t=>`<button class="${s.style===t.id?"on":""}" data-k="${k}" data-f="style" data-v="${t.id}">${t.name}</button>`).join("")}</div>`}</div>`};
  const ctl=$("#ctl");
  const draw=()=>{
    const p=P(),n=(S.front.opt!=="none")+(S.back.opt!=="none"),pr=n?priceCents(cat,S.prod,n,S.size):0;
    ctl.innerHTML=`<h1 style="font-size:clamp(1.8rem,3.4vw,2.6rem)">Design yours</h1>
    <div class="panel"><h3>Garment</h3><div class="seg">${cat.products.map(x=>`<button class="${S.prod===x.id?"on":""}" data-prod="${x.id}">${x.name}<br><small style="color:var(--mut)">${x.sub}</small></button>`).join("")}</div></div>
    <div class="panel"><h3>Color <small>${esc(S.color)}</small></h3><div class="swatches">${p.colors.map(c=>`<button class="sw ${c[0]===S.color?"on":""} ${c[2]?"":"off"}" title="${c[0]}${c[2]?"":" - dark colors with white ink coming soon"}" aria-label="${c[0]}" data-color="${c[0]}" data-ok="${c[2]}" style="background:${c[1]}"></button>`).join("")}</div><small style="color:var(--mut);display:block;margin-top:8px">Dark colors with white-ink art are coming soon.</small></div>
    ${sideUI("front")}${sideUI("back")}
    <div class="panel"><h3>Size <small><a href="#/page/sizing"><u>Size guide</u></a></small></h3><div class="sizes">${p.sizes.map(z=>`<button class="${z===S.size?"on":""}" data-size="${z}">${z}</button>`).join("")}</div></div>
    <div class="buy"><div class="price">${n?money(pr):"—"} <small>${n?(S.qty>1?`× ${S.qty} = ${money(pr*S.qty)}`:"+ shipping"):"Add a front or back design"}</small></div></div>
    <div class="buy"><div class="qty"><button data-q="-1" aria-label="Less">−</button><b>${S.qty}</b><button data-q="1" aria-label="More">+</button></div><button class="btn" id="add" ${n?"":"disabled"}>Add to cart</button><button class="btn ghost" id="save">♡ Save design</button></div>
    <div class="trust"><span>Made to order for you</span><span>Ships across the US</span><span>Premium blanks</span><span>30-day damage guarantee</span></div>
    <details><summary>Fabric & fit</summary><p>${FABRIC[S.prod]}</p></details><details><summary>Shipping & delivery</summary><p>Production takes about 2 to 5 business days, then 3 to 7 business days in transit within the US. Shipping is $4.99, free over $75. You get tracking by email.</p></details><details><summary>Care</summary><p>Machine wash cold, inside out, with similar colors. Tumble dry low. Do not iron or dry clean the print. The art is printed directly into the fabric so it will not crack or peel.</p></details>
    <div class="stick"><div><b>${n?money(pr*S.qty):"—"}</b><br><small style="color:var(--mut)">${S.qty>1?`${S.qty} items`:"+ shipping"}</small></div><button class="btn" id="add2" ${n?"":"disabled"}>Add to cart</button></div>`;
    pv();
  };
  const pv=async()=>{const k=S.view,d=toDesign(S[k],k);$("#pv").innerHTML=await renderSVG(S.prod,k,hex(),d);$$(".pvtabs .chip").forEach(c=>c.classList.toggle("on",c.dataset.v===k))};
  ctl.onclick=e=>{const t=e.target.closest("button");if(!t)return;const d=t.dataset;
    if(d.prod){S.prod=d.prod;const c=P().colors.find(c=>c[0]===S.color);if(!c)S.color="White"}
    else if(d.color){if(d.ok==="0"){toast("Dark colors with white-ink art are coming soon");return}S.color=d.color}
    else if(d.size)S.size=d.size;
    else if(d.q){S.qty=Math.max(1,Math.min(20,S.qty+ +d.q))}
    else if(d.opt){S[d.k].opt=d.opt;S.view=d.k}
    else if(d.f){S[d.k][d.f]=d.v;S.view=d.k}
    else if(t.id==="add"||t.id==="add2"){cart.push({id:Date.now()+"",prod:S.prod,color:S.color,size:S.size,qty:S.qty,front:toDesign(S.front,"front"),back:toDesign(S.back,"back"),_s:JSON.parse(JSON.stringify(S))});saveCart();toast("Added to cart");return}
    else if(t.id==="save"){saveDesign(S);return}
    else return; draw()};
  ctl.onchange=e=>{const t=e.target;if(t.dataset.f==="breed"){S[t.dataset.k].breed=t.value;S.view=t.dataset.k;pv()}};
  $(".pvtabs").onclick=e=>{const v=e.target.dataset.v;if(v){S.view=v;pv()}};
  draw();
}
async function saveDesign(S){
  const item={id:Date.now()+"",s:JSON.parse(JSON.stringify(S))};
  if(!user){toast("Log in to save designs");location.hash="#/login?next=design";window.__edit=null;ls.set("ad_pending",item);return}
  try{await api("/api/designs",item)}catch(e){if(e.message!=="preview"){toast(e.message);return}const a=ls.get("ad_designs",[]);a.push(item);ls.set("ad_designs",a)}
  toast("Saved to your account")}
/* ---------- cart / checkout ---------- */
async function cartPage(){
  app.dataset.title="Cart";
  const sub=cart.reduce((a,l)=>a+priceOf(l)*l.qty,0), ship=!cart.length?0:sub>=cat.shipping.free_over?0:cat.shipping.flat;
  app.innerHTML=`<div class="wrap"><h1 style="padding-top:30px;font-size:clamp(2rem,4vw,3rem)">Your cart</h1>${cart.length?`<div class="cart"><div id="lines">${cart.map(l=>`<div class="line" data-id="${l.id}"><div class="th" data-th="${l.id}"></div><div><b>${l.prod==="tee"?"Premium Tee":"Heavy Hoodie"}</b><small>${esc(l.color)} · ${l.size}</small>${l.front?`<small>Front: ${esc(designLabel(l.front))}</small>`:""}${l.back?`<small>Back: ${esc(designLabel(l.back))}</small>`:""}<div style="margin-top:8px;display:flex;gap:12px;align-items:center"><div class="qty"><button data-d="-1" aria-label="Less">−</button><b>${l.qty}</b><button data-d="1" aria-label="More">+</button></div><button class="x" data-rm="1">Remove</button></div></div><b>${money(priceOf(l)*l.qty)}</b></div>`).join("")}</div><div class="sum"><div class="r"><span>Subtotal</span><b>${money(sub)}</b></div><div class="r"><span>Shipping (US)</span><b>${ship?money(ship):"Free"}</b></div><div class="bar"><i style="width:${Math.min(100,Math.round(sub/cat.shipping.free_over*100))}%"></i></div>${ship?`<small style="color:var(--mut)">Add ${money(cat.shipping.free_over-sub)} more for free shipping</small>`:`<small style="color:var(--teal)"><b>You unlocked free shipping!</b></small>`}<div class="r t"><span>Total</span><span>${money(sub+ship)}</span></div><a class="btn" style="width:100%;margin-top:14px" href="#/checkout">Checkout</a></div></div>`:`<p>Your cart is empty. <a href="#/design"><u>Design something</u></a> or <a href="#/shop"><u>browse the shop</u></a>.</p>`}</div>`;
  cart.forEach(async l=>{const th=$(`[data-th="${l.id}"]`);if(th)th.innerHTML=await renderSVG(l.prod,l.front?"front":"back",(cat.products.find(p=>p.id===l.prod).colors.find(c=>c[0]===l.color)||cat.products[0].colors[0]),l.front||l.back)});
  if(cart.length){const b0=(cart[0].front||cart[0].back).breed,more=cat.themes.flatMap(t=>cat.styles.map(x=>designCard(b0,t.id,x.id))).slice(0,6).join("");app.querySelector(".wrap").insertAdjacentHTML("beforeend",`<h2 style="font-size:1.5rem;margin:10px 0 14px">Complete the look</h2><div class="grid" style="padding-bottom:50px">${more}</div>`)}
  app.onclick=e=>{const ln=e.target.closest(".line");if(!ln)return;const l=cart.find(x=>x.id===ln.dataset.id),b=e.target.closest("button");if(!b||!l)return;if(b.dataset.d)l.qty=Math.max(1,Math.min(20,l.qty+ +b.dataset.d));if(b.dataset.rm)cart=cart.filter(x=>x!==l);saveCart();cartPage()}
}
const FABRIC={tee:"Bella+Canvas 3001 unisex jersey tee: about 4.2 oz, 100% Airlume combed and ring-spun cotton (heather shades include a little polyester). Soft, lightweight, retail fit that runs true to size. Size up for a relaxed fit.",hoodie:"Gildan 18500 heavy blend hoodie: about 8 oz, 50% cotton and 50% polyester with a double-lined hood, pouch pocket and matching drawcord. Classic roomy fit. Size down if you like it snug."};
const STATES="AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split(" ");
function checkout(){
  app.dataset.title="Checkout";
  if(!cart.length){location.hash="#/cart";return}
  const sub=cart.reduce((a,l)=>a+priceOf(l)*l.qty,0), ship=sub>=cat.shipping.free_over?0:cat.shipping.flat;
  app.innerHTML=`<div class="wrap"><h1 style="padding-top:30px;font-size:clamp(2rem,4vw,3rem)">Checkout</h1><form class="cart" id="co"><div class="form"><div class="panel form"><h3>Contact</h3><label>Email<input name="email" type="email" required value="${esc(user?.email||"")}" autocomplete="email"></label></div><div class="panel form"><h3>Ship to <small>United States only</small></h3><div class="row"><label>First name<input name="fn" required autocomplete="given-name"></label><label>Last name<input name="ln" required autocomplete="family-name"></label></div><label>Address<input name="a1" required autocomplete="address-line1"></label><label>Apt, suite (optional)<input name="a2" autocomplete="address-line2"></label><div class="row3"><label>City<input name="city" required autocomplete="address-level2"></label><label>State<select name="st" required>${STATES.map(s=>`<option>${s}</option>`).join("")}</select></label><label>ZIP<input name="zip" required pattern="\\d{5}(-\\d{4})?" inputmode="numeric" autocomplete="postal-code"></label></div><label>Phone (optional)<input name="ph" type="tel" autocomplete="tel"></label></div><div class="panel"><h3>Payment</h3><div class="notice">Card payments switch on very soon. Reserve your order now and we will email you a secure payment link the moment checkout opens. Nothing is charged today.</div></div></div><div class="sum"><h3>Order summary</h3>${cart.map(l=>`<div class="r"><span>${l.qty} × ${l.prod==="tee"?"Tee":"Hoodie"} (${esc(l.color)}, ${l.size})</span><b>${money(priceOf(l)*l.qty)}</b></div>`).join("")}<div class="r"><span>Shipping</span><b>${ship?money(ship):"Free"}</b></div><div class="r t"><span>Total</span><span>${money(sub+ship)}</span></div><button class="btn" style="width:100%;margin-top:14px" id="pay">Reserve my order</button><small style="color:var(--mut);display:block;margin-top:8px">Made to order. See <a href="#/page/returns"><u>returns</u></a>.</small></div></form></div>`;
  $("#co").onsubmit=async e=>{e.preventDefault();const f=Object.fromEntries(new FormData(e.target));const order={email:f.email,ship:{name:f.fn+" "+f.ln,a1:f.a1,a2:f.a2,city:f.city,st:f.st,zip:f.zip,phone:f.ph},items:cart.map(({_s,...l})=>l),subtotal:sub,shipping:ship,total:sub+ship};
    const b=$("#pay");b.disabled=true;b.textContent="Saving…";let id;
    try{id=(await api("/api/orders",order)).id}catch(err){if(err.message!=="preview"){toast(err.message);b.disabled=false;b.textContent="Reserve my order";return}id="PREVIEW-"+Date.now().toString(36).toUpperCase();const o=ls.get("ad_orders",[]);o.push({id,...order,status:"reserved",at:Date.now()});ls.set("ad_orders",o)}
    cart=[];saveCart();location.hash="#/done/"+id}
}
function done(q,[id]){app.dataset.title="Order reserved";app.innerHTML=`<div class="wrap narrow"><span class="eyebrow">Reserved</span><h1>Thank you!</h1><p>Your order <b>${esc(id||"")}</b> is saved. We will email you a secure payment link as soon as checkout opens, and your order goes straight to print after payment.</p><a class="btn" href="#/shop">Keep browsing</a></div>`}
/* ---------- account ---------- */
function auth(q){user={email:q.email,token:q.token};ls.set("ad_user",user);refreshAcct();toast("Welcome!");const pend=ls.get("ad_pending",null);if(pend&&q.next==="design"){window.__edit=pend.s;try{localStorage.removeItem("ad_pending")}catch{}saveDesign(pend.s).then(()=>{location.hash="#/design"});return}location.hash="#/"+(q.next&&/^[\w/?=&-]+$/.test(q.next)?q.next:"account")}
const SOC={google:["Google",'<svg viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.5l6.7-6.7C35.6 2.4 30.2 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.8 6.1C12.3 13.6 17.7 9.5 24 9.5z"/><path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.6 3-2.3 5.5-4.8 7.2l7.5 5.8c4.4-4.1 7.1-10.1 7.1-17.5z"/><path fill="#FBBC05" d="M10.4 28.7A14.5 14.5 0 0 1 9.5 24c0-1.6.3-3.2.8-4.7l-7.8-6.1A24 24 0 0 0 0 24c0 3.9.9 7.5 2.6 10.8l7.8-6.1z"/><path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.5-5.8c-2.1 1.4-4.9 2.3-8.4 2.3-6.3 0-11.7-4.1-13.6-9.8l-7.8 6.1C6.5 42.6 14.6 48 24 48z"/></svg>'],facebook:["Facebook",'<svg viewBox="0 0 24 24"><path fill="#1877F2" d="M24 12a12 12 0 1 0-13.9 11.9v-8.4H7.1V12h3V9.4c0-3 1.8-4.7 4.5-4.7 1.3 0 2.7.2 2.7.2v3h-1.5c-1.5 0-2 .9-2 1.9V12h3.4l-.5 3.5h-2.9v8.4A12 12 0 0 0 24 12z"/></svg>'],apple:["Apple",'<svg viewBox="0 0 24 24"><path fill="currentColor" d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701"/></svg>']};
const socialBtns=(next)=>{const pv=cfg.providers||{};return `<div class="socials">${Object.keys(SOC).map(k=>pv[k]?`<a class="btn social" href="/api/auth/oauth/${k}/start?next=${next}">${SOC[k][1]}Continue with ${SOC[k][0]}</a>`:`<button class="btn social off" type="button" data-soc="${k}" title="Not connected yet">${SOC[k][1]}Continue with ${SOC[k][0]}</button>`).join("")}<div class="or"><span>or use your email</span></div></div>`};
function login(q){
  app.dataset.title="Log in";let step=1,email="";
  const draw=()=>{app.innerHTML=`<div class="wrap narrow"><h1 style="font-size:2.2rem">Log in or sign up</h1><p style="color:var(--mut)">No password needed.</p>${socialBtns(q.next||"account")}${cfg.api?"":`<div class="notice">Preview mode: the email service is not connected yet, so use code <b>123456</b>.</div>`}<form class="form" id="lf">${step===1?`<label>Email<input type="email" name="email" required autocomplete="email" value="${esc(email)}"></label><button class="btn">Send my code</button>`:`<label>Code sent to ${esc(email)}<input name="code" required inputmode="numeric" pattern="\\d{6}" maxlength="6" autocomplete="one-time-code"></label><button class="btn">Log in</button><button type="button" class="chip" id="back">Use a different email</button>`}</form></div>`;
    $("#lf").onsubmit=async e=>{e.preventDefault();const f=Object.fromEntries(new FormData(e.target));
      try{
        if(step===1){email=f.email;try{await api("/api/auth/request",{email})}catch(x){if(x.message!=="preview")throw x}step=2;draw();return}
        let r;try{r=await api("/api/auth/verify",{email,code:f.code})}catch(x){if(x.message!=="preview")throw x;if(f.code!=="123456")throw new Error("That code is not right");r={token:"preview",email}}
        user={email:r.email||email,token:r.token};ls.set("ad_user",user);refreshAcct();toast("Welcome!");const pend=ls.get("ad_pending",null);if(pend&&q.next==="design"){window.__edit=pend.s;try{localStorage.removeItem("ad_pending")}catch{}await saveDesign(pend.s);location.hash="#/design";return}location.hash="#/account"
      }catch(x){toast(x.message)}};
    const bk=$("#back");if(bk)bk.onclick=()=>{step=1;draw()};$$("[data-soc]").forEach(b=>b.onclick=()=>toast("This sign-in is switching on soon. Use email for now."))};if(q.err)toast(q.err);draw();
}
async function account(){
  app.dataset.title="Account";if(!user){location.hash="#/login";return}
  let designs=[],orders=[];
  try{designs=(await api("/api/designs")).items;orders=(await api("/api/orders")).items}catch(e){designs=ls.get("ad_designs",[]);orders=ls.get("ad_orders",[])}
  app.innerHTML=`<div class="wrap" style="padding-bottom:60px"><div class="sh" style="padding-top:34px"><div><h1 style="font-size:clamp(2rem,4vw,3rem)">Hi there 🐾</h1><p>${esc(user.email)}</p></div><button class="btn ghost sm" id="lo">Log out</button></div>
  <h2 style="font-size:1.5rem">Saved designs</h2>${designs.length?`<div class="grid" id="sd">${designs.map(d=>`<div class="card"><div class="art" data-sd="${d.id}"></div><div class="meta"><b>${d.s.prod==="tee"?"Premium Tee":"Heavy Hoodie"}</b><span>${esc(d.s.color)}</span><div style="margin-top:8px;display:flex;gap:8px"><button class="btn sm" data-open="${d.id}">Open</button><button class="chip" data-del="${d.id}">Delete</button></div></div></div>`).join("")}</div>`:`<p style="color:var(--mut)">Nothing saved yet. <a href="#/design"><u>Design something</u></a> and tap Save.</p>`}
  <h2 style="font-size:1.5rem;margin-top:36px">Orders</h2>${orders.length?`<table><tr><th>Order</th><th>Status</th><th>Total</th></tr>${orders.map(o=>`<tr><td>${esc(o.id)}</td><td>${esc(o.status||"reserved")}${o.tracking?` · <a href="${esc(o.tracking)}" target="_blank" rel="noopener"><u>Track</u></a>`:""}</td><td>${money(o.total||0)}</td></tr>`).join("")}</table>`:`<p style="color:var(--mut)">No orders yet.</p>`}</div>`;
  designs.forEach(async d=>{const el=$(`[data-sd="${d.id}"]`);if(el){const S=d.s;el.style.background="#f3ecdf";el.innerHTML=await renderSVG(S.prod,S.front.opt!=="none"?"front":"back",(cat.products.find(p=>p.id===S.prod).colors.find(c=>c[0]===S.color)||cat.products[0].colors[0]),toDesign(S.front.opt!=="none"?S.front:S.back,S.front.opt!=="none"?"front":"back"))}});
  $("#lo").onclick=()=>{user=null;ls.set("ad_user",null);refreshAcct();location.hash="#/"};
  app.onclick=async e=>{const b=e.target.closest("button");if(!b)return;if(b.dataset.open){window.__edit=designs.find(x=>x.id===b.dataset.open).s;location.hash="#/design?x="+Date.now()}if(b.dataset.del){try{await api("/api/designs/"+b.dataset.del,null,"DELETE")}catch{ls.set("ad_designs",ls.get("ad_designs",[]).filter(x=>x.id!==b.dataset.del))}account()}}
}
const refreshAcct=()=>{$("#acct").title=user?user.email:"Log in"};
/* ---------- static pages ---------- */
const PAGES={
about:["Our story",`<p>AlphaDog Styles started with a poodle named Linda and a simple belief: your dog deserves better than a generic paw print. Every design is drawn in a bold single-line or geometric style so it looks like art, not clip art.</p><p>We print each piece to order on premium blanks, so nothing is wasted and every order is made just for you.</p>`],
faq:["Help & FAQ",`<details><summary>How long does an order take?</summary><p>Each piece is made to order. Production usually takes 2 to 5 business days, then shipping within the US takes about 3 to 7 business days.</p></details><details><summary>Can I put different dogs on the front and back?</summary><p>Yes. Choose the front and back designs separately in the designer: different breeds, styles and sizes.</p></details><details><summary>Can I order a dark color?</summary><p>Dark colors need white-ink art and are coming soon. For now we offer a range of light colors with black-ink art.</p></details><details><summary>Do you ship outside the US?</summary><p>Not yet. We are US-only for now.</p></details><details><summary>Is my breed missing?</summary><p>Tell us on the <a href="#/page/contact"><u>contact page</u></a>. Popular requests go next.</p></details>`],
shipping:["Shipping",`<p>We ship across the United States. Shipping is a flat $4.99, and free on orders over $75. Items in one order may ship separately and arrive on different days.</p><p>Made-to-order timing: 2 to 5 business days to produce, plus about 3 to 7 business days in transit. You get tracking by email as soon as it ships.</p>`],
returns:["Returns & exchanges",`<p>Every item is printed just for you, so we cannot accept returns for size or color changes. If your order arrives damaged, misprinted or wrong, contact us within 30 days of delivery with a photo and we will make it right with a reprint or refund.</p><p>Please check the <a href="#/page/sizing"><u>size guide</u></a> before ordering.</p>`],
sizing:["Size guide",`<p>Approximate flat measurements in inches. Fit varies slightly by batch (±1").</p><h2>Premium Tee (unisex)</h2><table><tr><th>Size</th><th>S</th><th>M</th><th>L</th><th>XL</th><th>2XL</th><th>3XL</th></tr><tr><td>Chest width</td><td>18</td><td>20</td><td>22</td><td>24</td><td>26</td><td>28</td></tr><tr><td>Length</td><td>28</td><td>29</td><td>30</td><td>31</td><td>32</td><td>33</td></tr></table><h2>Heavy Hoodie (unisex)</h2><table><tr><th>Size</th><th>S</th><th>M</th><th>L</th><th>XL</th><th>2XL</th><th>3XL</th></tr><tr><td>Chest width</td><td>20</td><td>22</td><td>24</td><td>26</td><td>28</td><td>30</td></tr><tr><td>Length</td><td>27</td><td>28</td><td>29</td><td>30</td><td>31</td><td>32</td></tr></table>`],
contact:["Contact us",`<form class="form" id="cf"><label>Your email<input type="email" name="email" required></label><label>Message<textarea name="msg" rows="5" required></textarea></label><button class="btn">Send</button></form>`],
privacy:["Privacy",`<p>We collect only what we need to make and ship your order: your email, shipping address and the designs you choose. We share your shipping details with our print partner solely to fulfill your order, and never sell your data. Ask us to delete your account any time via the contact page.</p>`],
terms:["Terms of service",`<p>By ordering you agree that items are made to order and are final sale except for defects or errors (see Returns). Prices are in US dollars. We may cancel and refund any order we cannot fulfill. These terms are a starting template and should be reviewed before launch.</p>`]};
function page(q,[id]){const p=PAGES[id];if(!p)return notFound();app.dataset.title=p[0];app.innerHTML=`<div class="wrap prose"><h1 style="font-size:clamp(2rem,4vw,3rem)">${p[0]}</h1>${p[1]}</div>`;
  const cf=$("#cf");if(cf)cf.onsubmit=async e=>{e.preventDefault();try{await api("/api/contact",Object.fromEntries(new FormData(cf)))}catch(x){if(x.message!=="preview"){toast(x.message);return}}cf.innerHTML="<p><b>Thanks!</b> We will reply by email soon.</p>"}}
/* ---------- boot ---------- */
$("#burger").onclick=()=>$("#links").classList.toggle("open");
$("#yr").textContent=new Date().getFullYear();
$("#news").onsubmit=async e=>{e.preventDefault();const email=e.target.querySelector("input").value;try{await api("/api/subscribe",{email})}catch(x){if(x.message!=="preview"){toast(x.message);return}}e.target.reset();toast("You're in the pack!")};
(async()=>{
  cat=await (await fetch("data/catalog.json")).json();setCal(cat.cal);
  try{cfg=await (await fetch("data/config.json")).json()}catch{}
  try{const h=await (await fetch("api/health")).json();if(h&&h.ok)cfg={api:"same",providers:h.providers||{}}}catch{}
  saveCart();refreshAcct();window.addEventListener("hashchange",route);route();
})();
