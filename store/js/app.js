import {renderSVG,artUrl,setCal} from "./garment.js";
import {priceCents,registerProducts} from "./placement.js";
import {t,tn,lang,setLang,missing} from "./i18n.js";
import {PAGES as ALLPAGES} from "./pages.js";
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
window.__missing=missing;
const app=$("#app"); let cat,cfg={api:""};
const money=c=>"$"+(c/100).toFixed(2);
const ls={get:(k,d)=>{try{return JSON.parse(localStorage.getItem(k))??d}catch{return d}},set:(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch{}}};
let cart=ls.get("ad_cart",[]), user=ls.get("ad_user",null);
const saveCart=()=>{ls.set("ad_cart",cart);$("#cartn").textContent=cart.reduce((a,l)=>a+l.qty,0)};
function toast(m){const t=$("#toast");t.textContent=m;t.classList.add("show");clearTimeout(toast.t);toast.t=setTimeout(()=>t.classList.remove("show"),2600)}
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const breedName=s=>tn(cat.breeds.find(b=>b.slug===s)?.name||s);
const themeName=i=>tn((cat.themes.find(x=>x.id===i)||cat.themes[0]).name), styleName=i=>tn((cat.styles.find(x=>x.id===i)||cat.styles[0]).name);
const prodName=id=>tn(cat.products.find(p=>p.id===id).name);
const PROD=id=>cat.products.find(p=>p.id===id);
const colorLabel=(pid,c)=>{const x=(PROD(pid)?.colors||[]).find(k=>k[0]===c);return tn(x&&x[4]||c)};
const sidesOf=pid=>PROD(pid).sides||["front","back"];
const optsOf=(pid,k)=>{const p=PROD(pid);const ids=p.opts&&p.opts[k];return cat[k+"_opts"].filter(o=>ids?ids.includes(o.id):true)};
/* mixed merchandise for the design grid: every card shows the art on a different garment / color */
const MIX=["hoodie","tee","tank","cap_dad","wtank","polo","cap_foam","tee","hoodie","polo","cap_mesh","tank","wtank","cap_dad","tee","hoodie"];
function mixFor(i){const pid=MIX[i%MIX.length],p=PROD(pid);if(!p)return null;const ok=p.colors.filter(c=>c[2]);
  // nth time this garment appears in the grid -> walk its colors with a stride so neighbours never share a color and white is not the default
  let nth=0;for(let k=0;k<i;k++)if(MIX[k%MIX.length]===pid)nth++;const g=(a,b)=>b?g(b,a%b):a,st=[3,5,7,2,1].find(x=>x<ok.length&&g(x,ok.length)===1)||1,nw=ok.filter(c=>!/white/i.test(c[0])||/\//.test(c[0])),col=ok.length===2&&nw.length===1&&nth%3!==2?nw[0]:ok[(nth*st+1)%ok.length];
  const part=(i>>1)%2?"body":"head",size=(p.rule==="chest"||p.rule==="cap")?"s":"l";return {pid,col,part,size}}
const designLabel=(d,side)=>{if(d&&side)d={...d,side};if(!d)return "";if(d.custom){const o=cat.front_opts.find(x=>x.part===d.part&&x.size===d.size);return `${t("Your custom design")} · ${tn(o?o.name:"")}`}const o=(d.side==="back"?cat.back_opts:cat.front_opts).find(x=>x.part===d.part&&x.size===d.size)||cat.front_opts.find(x=>x.part===d.part&&x.size===d.size);return `${breedName(d.breed)} · ${themeName(d.theme)} ${styleName(d.style)} · ${tn(o?o.name:"")}`};
/* ---------- api (falls back to local preview mode when no backend is configured) ---------- */
async function api(path,body,method){
  if(!cfg.api) throw new Error("preview");
  const r=await fetch((cfg.api==="same"?"":cfg.api)+path,{method:method||(body?"POST":"GET"),headers:{"content-type":"application/json",...(user?{authorization:"Bearer "+user.token}:{})},body:body?JSON.stringify(body):undefined});
  const j=await r.json().catch(()=>({})); if(!r.ok) throw new Error(t(j.error||"Request failed")); return j;
}
/* ---------- design model ---------- */
const newSide=(opt,b)=>({opt,breed:b||"french_bulldog",theme:"line",style:"classic"});
function toDesign(side,kind,S0){const o=cat[kind+"_opts"].find(x=>x.id===side.opt);if(!o||!o.part)return null;const c=(S0||curS||{}).custom;return c?{part:o.part,size:o.size,custom:c.id,k:c.k,breed:"custom",theme:"custom",style:"custom"}:{part:o.part,size:o.size,breed:side.breed,theme:side.theme,style:side.style}}
let curS=null;
const custOf=()=>{for(const l of cart)for(const d of[l.front,l.back])if(d&&d.custom)return {id:d.custom,k:d.k,fee:(ls.get("ad_cfee",{})[d.custom])||0};return null};
function priceOf(l){return priceCents(cat,l.prod,(l.front?1:0)+(l.back?1:0),l.size)}
/* ---------- router ---------- */
const routes={"":home,shop,design,cart:cartPage,checkout,account,login,page,done,auth,custom,admin};
async function route(){
  const h=location.hash.replace(/^#\/?/,""),[path,qs]=h.split("?"),parts=path.split("/"),q=Object.fromEntries(new URLSearchParams(qs||""));
  $("#links").classList.remove("open");
  $$("#links a").forEach(a=>a.classList.toggle("on",a.getAttribute("href")==="#/"+parts[0]));
  const fn=routes[parts[0]]||notFound; app.onclick=null; app.innerHTML=""; window.scrollTo(0,0);
  await fn(q,parts.slice(1)); document.title=tn(app.dataset.title||"AlphaDog Styles")+" - AlphaDog Styles";
}
function notFound(){app.innerHTML=`<div class="wrap narrow"><h1>${t("Lost dog?")}</h1><p>${t("That page wandered off.")} <a href="#/shop" class="btn">${t("Back to the shop")}</a></p></div>`}
/* ---------- cards ---------- */
let cardN=0;
const designCard=(b,tt,s,ix)=>{const i=ix??cardN++,m=mixFor(i);return `<a class="card" href="#/design?breed=${b}&theme=${tt}&style=${s}${m?`&prod=${m.pid}&color=${encodeURIComponent(m.col[0])}&part=${m.part}`:""}"><div class="art mock" role="img" aria-label="${esc(t("{0} {1} {2} design",breedName(b),themeName(tt),styleName(s)))}" data-b="${b}" data-t="${tt}" data-s="${s}" data-n="${i}"><img loading="lazy" alt="" src="art/${tt}_${s}/${b}_front.svg"></div><div class="meta"><b>${esc(breedName(b))}</b><span>${themeName(tt)} · ${styleName(s)}${m?` · ${prodName(m.pid)}`:""}</span></div></a>`};
const mockIO="IntersectionObserver" in window?new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){mockIO.unobserve(e.target);paintMock(e.target)}}),{rootMargin:"300px"}):null;
async function paintMock(el){const m=mixFor(+el.dataset.n);if(!m)return;const d={part:m.part,size:m.size,breed:el.dataset.b,theme:el.dataset.t,style:el.dataset.s};try{el.innerHTML=await renderSVG(m.pid,"front",m.col,d);el.classList.add("on")}catch{}}
const watchMocks=()=>$$(".art.mock:not(.on)").forEach(el=>mockIO?mockIO.observe(el):paintMock(el));
function pick(arr,n,seed){let a=[...arr],r=seed;const o=[];while(o.length<n&&a.length){r=(r*9301+49297)%233280;o.push(a.splice(Math.floor(r/233280*a.length),1)[0])}return o}
/* ---------- pages ---------- */
async function home(){
  app.dataset.title="Wear your best friend";
  const day=Math.floor(Date.now()/864e5), feat=pick(cat.breeds,8,day).map((b,i)=>designCard(b.slug,cat.themes[i%2].id,cat.styles[(i+day)%3].id,i+day%5)).join("");
  const names=cat.breeds.map(b=>tn(b.name)).join(`<em>✦</em>`);
  app.innerHTML=`<div class="wrap hero"><div><span class="eyebrow">${t("Made to order · Shipped across the US")}</span><h1>${t("Your best friend, on your best tee.")}</h1><p>${t("33 breeds, 2 art styles, 3 moods and every placement you can imagine. Design it your way, we print it just for you.")}</p><div class="cta"><a class="btn" href="#/design">${t("Design yours")}</a><a class="btn ghost" href="#/shop">${t("Browse designs")}</a></div></div><div class="stage" id="stage"><div class="blob" style="width:180px;height:180px;background:#ffd8a8;top:-40px;right:-30px"></div><div class="blob" style="width:120px;height:120px;background:#fff1d6;bottom:20px;left:-30px"></div></div></div>
  <div class="marquee"><span>${names}<em>✦</em>${names}<em>✦</em></span></div>
  <section class="sec"><div class="wrap"><div class="sh"><div><h2>${t("Fresh from the kennel")}</h2><p>${t("Today's picks. Tap any design to make it yours.")}</p></div><a class="btn ghost sm" href="#/shop">${t("See all 198 designs")}</a></div><div class="grid">${feat}</div></div></section>
  ${customBanner()}<section class="sec"><div class="wrap"><div class="sh"><div><h2>${t("Real garments, real art")}</h2><p>${t("Premium tees and hoodies, printed to order.")}</p></div><a class="btn ghost sm" href="#/design">${t("Design yours")}</a></div><div class="look">${[1,2,3,4,5,6].map(i=>`<a href="#/design" class="lk" data-k="${i}" aria-label="${esc(t("Printed tee mockup {0}",i))}"><img loading="lazy" alt="" src="img/look-${i}.webp"></a>`).join("")}</div></div></section>
  <section class="sec alt"><div class="wrap"><div class="sh"><div><h2>${t("Three simple steps")}</h2></div></div><div class="steps"><div class="step"><i>1</i><h3>${t("Pick your pup")}</h3><p>${t("Choose from 33 breeds, in continuous line or geometric art, in Classic, Cool or Heart.")}</p></div><div class="step"><i>2</i><h3>${t("Make it yours")}</h3><p>${t("Front, back or both. Head or full body, small emblem or big statement. Different dogs on each side? Go for it.")}</p></div><div class="step"><i>3</i><h3>${t("We print and ship")}</h3><p>${t("Every piece is printed to order on premium blanks and shipped to your door.")}</p></div></div></div></section>
  <section class="sec"><div class="wrap"><div class="feat"><div><h3>${t("Premium blanks")}</h3><p>${t("Soft Bella+Canvas tees and cozy heavyweight hoodies that survive wash after wash.")}</p></div><div><h3>${t("Truly custom")}</h3><p>${t("You choose breed, style, placement and color. No two combinations look the same.")}</p></div><div><h3>${t("Printed on demand")}</h3><p>${t("Nothing sits in a warehouse. Your order is made when you order it.")}</p></div><div><h3>${t("Easy help")}</h3><p>${t("Questions? We answer fast. See {0}.",`<a href="#/page/faq"><u>${t("FAQ")}</u></a>`)}</p></div></div></div></section>`;
  watchMocks();
  heroCarousel($("#stage")); looksMix();
}
/* hero: auto-rotating showcase, no controls. Every slide is a different product, color, breed and design. */
function randMock(prev){
  const prods=cat.products.filter(p=>p.colors.some(c=>c[2]));let p,col,b,th,st,tries=0;
  do{p=prods[Math.floor(Math.random()*prods.length)];const ok=p.colors.filter(c=>c[2]);col=ok[Math.floor(Math.random()*ok.length)];
     b=cat.breeds[Math.floor(Math.random()*cat.breeds.length)].slug;th=cat.themes[Math.floor(Math.random()*cat.themes.length)].id;st=cat.styles[Math.floor(Math.random()*cat.styles.length)].id;tries++}
  while(prev&&tries<30&&(p.id===prev.p||col[0]===prev.c||b===prev.b||th+st===prev.d||(/white/i.test(col[0])&&!/\//.test(col[0])&&Math.random()<.6)));
  const small=p.rule==="chest"||p.rule==="cap";const part=small?"head":(Math.random()<.5?"head":"body");
  return {p:p.id,c:col[0],b,d:th+st,col,args:{part,size:small?"s":"l",breed:b,theme:th,style:st}};
}
async function heroCarousel(stage){
  if(!stage)return;const reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;let prev=null,cur=null,busy=false;
  const show=async()=>{if(busy||document.hidden||!document.body.contains(stage))return;busy=true;
    try{const m=randMock(prev);prev=m;const svg=await renderSVG(m.p,"front",m.col,m.args);const el=document.createElement("div");el.className="slide";el.innerHTML=svg;
      el.setAttribute("aria-label",`${breedName(m.b)} · ${prodName(m.p)} · ${colorLabel(m.p,m.c)}`);stage.appendChild(el);
      await new Promise(r=>{const im=new Image();im.onload=im.onerror=r;im.src=photoUrlOf(m.p,m.col)});
      requestAnimationFrame(()=>el.classList.add("on"));if(cur){const old=cur;old.classList.remove("on");setTimeout(()=>old.remove(),900)}cur=el}catch(e){}
    busy=false};
  await show();if(reduce)return;
  const tick=setInterval(()=>{if(!document.body.contains(stage)){clearInterval(tick);return}if(!stage.matches(":hover"))show()},4000);
}
const photoUrlOf=(pid,col)=>`img/${pid}_${col[3]||"white"}_front.webp`;
/* "Real garments" strip: every tile a different garment + color, no all-white row */
async function looksMix(){
  const tiles=$$(".look .lk");let prev=null;const used=new Set();
  for(const a of tiles){let m;let n=0;do{m=randMock(prev);n++}while(n<20&&(used.has(m.p+m.c)||/^white$|^solid white$/i.test(m.c)));used.add(m.p+m.c);prev=m;
    try{a.innerHTML=await renderSVG(m.p,"front",m.col,m.args);a.classList.add("mk")}catch(e){}}
}
function shop(q){
  app.dataset.title="Shop";
  const f={t:cat.themes.some(x=>x.id===q.theme)?q.theme:"",s:cat.styles.some(x=>x.id===q.style)?q.style:"",q:""};
  app.innerHTML=`<div class="wrap" style="padding-top:34px"><h1 style="font-size:clamp(2rem,4vw,3rem)">${t("Shop all designs")}</h1><div class="tools"><input id="sq" placeholder="${t("Search a breed…")}" aria-label="${t("Search breeds")}"><div class="chips" id="ft"></div><div class="chips" id="fs"></div></div><div class="grid" id="sg"></div><p id="none" hidden>${t("No designs match. Try another breed.")}</p></div>${customBanner()}`;
  const draw=()=>{
    $("#ft").innerHTML=`<button class="chip ${f.t?"":"on"}" data-t="">${t("All styles")}</button>`+cat.themes.map(x=>`<button class="chip ${f.t===x.id?"on":""}" data-t="${x.id}">${tn(x.name)}</button>`).join("");
    $("#fs").innerHTML=`<button class="chip ${f.s?"":"on"}" data-s="">${t("All moods")}</button>`+cat.styles.map(x=>`<button class="chip ${f.s===x.id?"on":""}" data-s="${x.id}">${tn(x.name)}</button>`).join("");
    cardN=0;const out=[];for(const b of cat.breeds){if(f.q&&!(b.name.toLowerCase().includes(f.q)||tn(b.name).toLowerCase().includes(f.q)))continue;for(const th of cat.themes){if(f.t&&f.t!==th.id)continue;for(const s of cat.styles){if(f.s&&f.s!==s.id)continue;out.push(designCard(b.slug,th.id,s.id))}}}
    $("#sg").innerHTML=out.join("");$("#none").hidden=!!out.length;watchMocks()};
  draw();
  $("#sq").oninput=e=>{f.q=e.target.value.trim().toLowerCase();draw()};
  app.onclick=e=>{const c=e.target.closest(".chip");if(!c)return;if("t"in c.dataset)f.t=c.dataset.t;if("s"in c.dataset)f.s=c.dataset.s;draw()};
}
/* ---------- customizer ---------- */
async function design(q){
  app.dataset.title="Design yours";
  let S=window.__edit||null; window.__edit=null;
  if(!S){const b=q.breed&&cat.breeds.some(x=>x.slug===q.breed)?q.breed:"french_bulldog";S={prod:"tee",color:"White",size:"M",qty:1,view:"front",front:newSide("head_s",b),back:newSide("body_l",b)};if(q.theme&&cat.themes.some(x=>x.id===q.theme)){S.front.theme=S.back.theme=q.theme}if(q.style&&cat.styles.some(x=>x.id===q.style)){S.front.style=S.back.style=q.style}
    if(q.custom){S.custom={id:q.custom,k:q.k||""};S.front.opt="head_l";S.back.opt="body_l"}
    if(q.prod&&PROD(q.prod)){S.prod=q.prod;if(q.color)S.color=q.color;const big=PROD(q.prod).rule==="chest"||PROD(q.prod).rule==="cap"?"_s":"_l";S.front.opt=(q.part==="body"?"body":"head")+big}}

  curS=S;const P=()=>cat.products.find(p=>p.id===S.prod);
  const hex=()=>(P().colors.find(c=>c[0]===S.color)||P().colors[0]);
  const norm=()=>{const p=P();if(!p.colors.some(c=>c[0]===S.color&&c[2]))S.color=p.colors.find(c=>c[2])[0];if(!p.sizes.includes(S.size))S.size=p.sizes.includes("M")?"M":p.sizes[0];
    for(const k of["front","back"]){if(!sidesOf(S.prod).includes(k)){if(S[k].opt!=="none")S[k].saved=S[k].opt;S[k].opt="none";continue}if(S[k].opt==="none"&&S[k].saved){S[k].opt=S[k].saved;delete S[k].saved}const ids=optsOf(S.prod,k).map(o=>o.id);if(!ids.includes(S[k].opt)){if(S[k].opt!=="none")S[k].want=S[k].opt;const part=(S[k].want||S[k].opt).split("_")[0];S[k].opt=ids.includes(part+"_s")?part+"_s":ids.includes("head_s")&&k==="front"?"head_s":ids[0]}else if(S[k].want&&ids.includes(S[k].want)&&S[k].opt!==S[k].want&&S[k].opt.split("_")[0]===S[k].want.split("_")[0]){S[k].opt=S[k].want;delete S[k].want}}
    if(!sidesOf(S.prod).includes(S.view))S.view="front"};
  norm();

  app.innerHTML=`<div class="wrap"><p class="crumbs"><a href="#/shop">${t("Shop")}</a> / ${t("Design yours")}</p><div class="dz"><div class="pv"><div class="pvbox" id="pv"></div><div class="pvtabs"><button class="chip" data-v="front">${t("Front")}</button><button class="chip" data-v="back">${t("Back")}</button></div><p style="text-align:center;color:var(--mut);font-size:.85rem">${t("Preview is illustrative. Actual print is crisp on premium fabric.")}</p></div><div id="ctl"></div></div></div>`;
  const sideUI=(k)=>{if(!sidesOf(S.prod).includes(k))return "";const s=S[k],opts=optsOf(S.prod,k);return `<div class="panel"><h3>${k==="front"?t("Front design"):t("Back design")}</h3><div class="chips" style="margin-bottom:12px">${opts.map(o=>`<button class="chip ${s.opt===o.id?"on":""}" data-k="${k}" data-opt="${o.id}">${tn(o.name)}</button>`).join("")}</div>${s.opt==="none"?`<small style="color:var(--mut)">${k==="front"?t("No print on the front."):t("No print on the back.")}</small>`:S.custom?`<div class="notice">${t("Your custom design")}</div>`:`<label style="font-weight:600;font-size:.9rem">${t("Breed")}<select data-k="${k}" data-f="breed">${cat.breeds.map(b=>`<option value="${b.slug}" ${b.slug===s.breed?"selected":""}>${esc(tn(b.name))}</option>`).join("")}</select></label><div class="seg" style="margin-top:10px">${cat.themes.map(x=>`<button class="${s.theme===x.id?"on":""}" data-k="${k}" data-f="theme" data-v="${x.id}">${tn(x.name)}</button>`).join("")}</div><div class="seg" style="margin-top:8px">${cat.styles.map(x=>`<button class="${s.style===x.id?"on":""}" data-k="${k}" data-f="style" data-v="${x.id}">${tn(x.name)}</button>`).join("")}</div>`}</div>`};
  const ctl=$("#ctl");
  const draw=()=>{
    const p=P(),n=(S.front.opt!=="none")+(S.back.opt!=="none"),pr=n?priceCents(cat,S.prod,n,S.size):0;
    ctl.innerHTML=`<h1 style="font-size:clamp(1.8rem,3.4vw,2.6rem)">${t("Design yours")}</h1>
    <div class="panel"><h3>${t("Garment")} <small>${esc(tn(p.sub))}</small></h3>${["tops","polos","caps"].map(g=>`<div class="glabel">${t({tops:"Tees, hoodies & tanks",polos:"Polos",caps:"Caps"}[g])}</div><div class="garms">${cat.products.filter(x=>(x.group||"tops")===g).map(x=>`<button class="${S.prod===x.id?"on":""}" data-prod="${x.id}" aria-label="${esc(tn(x.name))}"><img src="img/${x.id}_${(x.colors.find(c=>c[2])||x.colors[0])[3]}_front.webp" alt="" loading="lazy" width="56" height="56"><span>${tn(x.name)}</span></button>`).join("")}</div>`).join("")}</div>
    <div class="panel"><h3>${t("Color")} <small>${esc(colorLabel(S.prod,S.color))}</small></h3><div class="swatches">${p.colors.map(c=>`<button class="sw ${c[0]===S.color?"on":""} ${c[2]?"":"off"}" title="${esc(c[2]?tn(c[4]||c[0]):t("{0} - dark colors with white-ink art coming soon",tn(c[4]||c[0])))}" aria-label="${esc(tn(c[4]||c[0]))}" data-color="${c[0]}" data-ok="${c[2]}" style="background:${c[1]}"></button>`).join("")}</div><small style="color:var(--mut);display:block;margin-top:8px">${t("Dark colors with white-ink art are coming soon.")}</small></div>
    ${sideUI("front")}${sideUI("back")}
    <div class="panel"><h3>${t("Size")} <small><a href="#/page/sizing"><u>${t("Size guide")}</u></a></small></h3><div class="sizes">${p.sizes.map(z=>`<button class="${z===S.size?"on":""}" data-size="${z}">${t(z)}</button>`).join("")}</div></div>
    <div class="buy"><div class="price">${n?money(pr):"—"} <small>${n?(S.qty>1?t("× {0} = {1}",S.qty,money(pr*S.qty)):t("+ shipping")):t("Add a front or back design")}</small></div></div>
    <div class="buy"><div class="qty"><button data-q="-1" aria-label="${t("Less")}">−</button><b>${S.qty}</b><button data-q="1" aria-label="${t("More")}">+</button></div><button class="btn" id="add" ${n?"":"disabled"}>${t("Add to cart")}</button><button class="btn ghost" id="save">${t("♡ Save design")}</button></div>
    <div class="trust"><span>${t("Made to order for you")}</span><span>${t("Ships across the US")}</span><span>${t("Premium blanks")}</span><span>${t("30-day damage guarantee")}</span></div>
    <details><summary>${t("Fabric & fit")}</summary><p>${t(FABRIC[S.prod])}${p.label?" "+t("Finished with the AlphaDog logo label."):""}</p></details><details><summary>${t("Shipping & delivery")}</summary><p>${t("Production takes about 2 to 5 business days, then 3 to 7 business days in transit within the US. Shipping is $4.99, free over $75. You get tracking by email.")}</p></details><details><summary>${t("Care")}</summary><p>${t("Machine wash cold, inside out, with similar colors. Tumble dry low. Do not iron or dry clean the print. The art is printed directly into the fabric so it will not crack or peel.")}</p></details>
    <div class="stick"><div><b>${n?money(pr*S.qty):"—"}</b><br><small style="color:var(--mut)">${S.qty>1?t("{0} items",S.qty):t("+ shipping")}</small></div><button class="btn" id="add2" ${n?"":"disabled"}>${t("Add to cart")}</button></div>`;
    $(".pvtabs [data-v=back]").hidden=!sidesOf(S.prod).includes("back");
    pv();
  };
  let pvSeq=0;const pv=async()=>{const my=++pvSeq,k=S.view,d=toDesign(S[k],k);const html=await renderSVG(S.prod,k,hex(),d);if(my!==pvSeq)return;$("#pv").innerHTML=html;$$(".pvtabs .chip").forEach(c=>c.classList.toggle("on",c.dataset.v===k))};
  ctl.onclick=e=>{const bt=e.target.closest("button");if(!bt)return;const d=bt.dataset;
    if(d.prod){S.prod=d.prod;norm()}
    else if(d.color){if(d.ok==="0"){toast(t("Dark colors with white-ink art are coming soon"));return}S.color=d.color}
    else if(d.size)S.size=d.size;
    else if(d.q){S.qty=Math.max(1,Math.min(20,S.qty+ +d.q))}
    else if(d.opt){S[d.k].opt=d.opt;S.view=d.k}
    else if(d.f){S[d.k][d.f]=d.v;S.view=d.k}
    else if(bt.id==="add"||bt.id==="add2"){const cc=custOf();if(S.custom&&cc&&cc.id!==S.custom.id){cart=cart.filter(l=>![l.front,l.back].some(d=>d&&d.custom))}if(cart.length>=30){toast(t("Your cart is full (30 items max). Please check out first."));return}cart.push({id:Date.now()+"",prod:S.prod,color:S.color,size:S.size,qty:S.qty,front:toDesign(S.front,"front"),back:toDesign(S.back,"back"),_s:JSON.parse(JSON.stringify(S))});saveCart();toast(t("Added to cart"));return}
    else if(bt.id==="save"){saveDesign(S);return}
    else return; draw()};
  ctl.onchange=e=>{const el=e.target;if(el.dataset.f==="breed"){S[el.dataset.k].breed=el.value;S.view=el.dataset.k;pv()}};
  $(".pvtabs").onclick=e=>{const v=e.target.dataset.v;if(v){S.view=v;pv()}};
  draw();
}
async function saveDesign(S){
  const item={id:Date.now()+"",s:JSON.parse(JSON.stringify(S))};
  if(!user){toast(t("Log in to save designs"));location.hash="#/login?next=design";window.__edit=null;ls.set("ad_pending",item);return}
  try{await api("/api/designs",item)}catch(e){if(e.message!=="preview"){toast(e.message);return}const a=ls.get("ad_designs",[]);a.push(item);ls.set("ad_designs",a)}
  toast(t("Saved to your account"))}
/* ---------- cart / checkout ---------- */
async function cartPage(){
  app.dataset.title="Cart";
  const cu=custOf(),fee=cu?cu.fee:0,sub=cart.reduce((a,l)=>a+priceOf(l)*l.qty,0), ship=!cart.length?0:sub>=cat.shipping.free_over?0:cat.shipping.flat;
  app.innerHTML=`<div class="wrap"><h1 style="padding-top:30px;font-size:clamp(2rem,4vw,3rem)">${t("Your cart")}</h1>${cart.length?`<div class="cart"><div id="lines">${cart.map(l=>`<div class="line" data-id="${l.id}"><div class="th" data-th="${l.id}"></div><div><b>${prodName(l.prod)}</b><small>${esc(colorLabel(l.prod,l.color))} · ${t(l.size)}</small>${l.front?`<small>${esc(t("Front: {0}",designLabel(l.front)))}</small>`:""}${l.back?`<small>${esc(t("Back: {0}",designLabel(l.back,"back")))}</small>`:""}<div style="margin-top:8px;display:flex;gap:12px;align-items:center"><div class="qty"><button data-d="-1" aria-label="${t("Less")}">−</button><b>${l.qty}</b><button data-d="1" aria-label="${t("More")}">+</button></div><button class="x" data-rm="1" style="min-height:32px;padding:6px 10px">${t("Remove")}</button></div></div><b>${money(priceOf(l)*l.qty)}</b></div>`).join("")}</div><div class="sum"><div class="r"><span>${t("Subtotal")}</span><b>${money(sub)}</b></div><div class="r"><span>${t("Shipping (US)")}</span><b>${ship?money(ship):t("Free")}</b></div><div class="bar"><i style="width:${Math.min(100,Math.round(sub/cat.shipping.free_over*100))}%"></i></div>${ship?`<small style="color:var(--mut)">${t("Add {0} more for free shipping",money(cat.shipping.free_over-sub))}</small>`:`<small style="color:var(--teal)"><b>${t("You unlocked free shipping!")}</b></small>`}${fee?`<div class="r"><span>${t("Custom design (one-time)")}</span><b>${money(fee)}</b></div>`:""}<div class="r t"><span>${t("Total")}</span><span>${money(sub+ship+fee)}</span></div><a class="btn" style="width:100%;margin-top:14px" href="#/checkout">${t("Checkout")}</a></div></div>`:`<p>${t("Your cart is empty.")} <a href="#/design"><u>${t("Design something")}</u></a> ${t("or")} <a href="#/shop"><u>${t("browse the shop")}</u></a>.</p>`}</div>`;
  cart.forEach(async l=>{const th=$(`[data-th="${l.id}"]`);if(th)th.innerHTML=await renderSVG(l.prod,l.front?"front":"back",(cat.products.find(p=>p.id===l.prod).colors.find(c=>c[0]===l.color)||cat.products[0].colors[0]),l.front||l.back)});
  const b0x=(cart.flatMap(l=>[l.front,l.back]).find(d=>d&&!d.custom&&cat.breeds.some(b=>b.slug===d.breed))||{}).breed;if(cart.length&&b0x){const b0=b0x,more=cat.themes.flatMap(th=>cat.styles.map(x=>designCard(b0,th.id,x.id))).slice(0,6).map((h,i)=>h).join("");app.querySelector(".wrap").insertAdjacentHTML("beforeend",`<h2 style="font-size:1.5rem;margin:10px 0 14px">${t("Complete the look")}</h2><div class="grid" style="padding-bottom:50px">${more}</div>`);watchMocks()}
  app.onclick=e=>{const ln=e.target.closest(".line");if(!ln)return;const l=cart.find(x=>x.id===ln.dataset.id),b=e.target.closest("button");if(!b||!l)return;if(b.dataset.d)l.qty=Math.max(1,Math.min(20,l.qty+ +b.dataset.d));if(b.dataset.rm)cart=cart.filter(x=>x!==l);saveCart();cartPage()}
}
const FABRIC={tee:"Bella+Canvas 3001 unisex jersey tee: about 4.2 oz, 100% Airlume combed and ring-spun cotton (heather shades include a little polyester). Soft, lightweight, retail fit that runs true to size. Size up for a relaxed fit.",hoodie:"Gildan 18500 heavy blend hoodie: about 8 oz, 50% cotton and 50% polyester with a double-lined hood, pouch pocket and matching drawcord. Classic roomy fit. Size down if you like it snug.",
tank:"Bella+Canvas 3480 unisex jersey tank: about 4.2 oz, 100% Airlume combed and ring-spun cotton (heathers include polyester). Soft, light and breathable with a retail fit.",
wtank:"Next Level 1533 women's ideal racerback tank: about 3.9 oz cotton and polyester blend, slim racerback cut that sits close to the body. Size up for a looser fit.",
polo:"JERZEES 443M men's piqué polo: breathable cotton-blend piqué, ribbed collar and three-button placket. The dog is printed on the chest.",
wpolo:"CORE365 Origin women's performance piqué polo: moisture-wicking, snag-resistant polyester with a feminine fit. The dog is printed on the chest.",
cap_dad:"Yupoong 6245CM classic dad cap: unstructured six-panel cotton twill, low profile, curved visor and adjustable strap. Printed front (sharper than embroidery for fine line art).",
cap_foam:"OTTO 39-165 foam trucker hat: retro high-crown foam front, breathable mesh back and snapback closure. Printed front.",
cap_mesh:"Yupoong 6006 five-panel trucker cap: structured front, mesh back, snapback closure. Printed front."};
const STATES="AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split(" ");
function checkout(){
  app.dataset.title="Checkout";
  if(!cart.length){location.hash="#/cart";return}
  const cu=custOf(),fee=cu?cu.fee:0,sub=cart.reduce((a,l)=>a+priceOf(l)*l.qty,0), ship=sub>=cat.shipping.free_over?0:cat.shipping.flat;
  app.innerHTML=`<div class="wrap"><h1 style="padding-top:30px;font-size:clamp(2rem,4vw,3rem)">${t("Checkout")}</h1><form class="cart" id="co"><div class="form"><div class="panel form"><h3>${t("Contact")}</h3><label>${t("Email")}<input name="email" type="email" required value="${esc(user?.email||"")}" autocomplete="email"></label></div><div class="panel form"><h3>${t("Ship to")} <small>${t("United States only")}</small></h3><div class="row"><label>${t("First name")}<input name="fn" required autocomplete="given-name"></label><label>${t("Last name")}<input name="ln" required autocomplete="family-name"></label></div><label>${t("Address")}<input name="a1" required autocomplete="address-line1"></label><label>${t("Apt, suite (optional)")}<input name="a2" autocomplete="address-line2"></label><div class="row3"><label>${t("City")}<input name="city" required autocomplete="address-level2"></label><label>${t("State")}<select name="st" required><option value="" selected disabled>${t("State")}</option>${STATES.map(s=>`<option>${s}</option>`).join("")}</select></label><label>${t("ZIP")}<input name="zip" required pattern="\\d{5}(-\\d{4})?" inputmode="numeric" autocomplete="postal-code"></label></div><label>${t("Phone (optional)")}<input name="ph" type="tel" autocomplete="tel"></label></div><div class="panel"><h3>${t("Payment")}</h3><div class="notice" id="paynote">${t("You will enter your card on Stripe\u2019s secure page after you tap Pay. We never see or store your card details.")}</div></div></div><div class="sum"><h3>${t("Order summary")}</h3>${cart.map(l=>`<div class="r"><span>${esc(t("{0} × {1} ({2}, {3})",l.qty,prodName(l.prod),colorLabel(l.prod,l.color),t(l.size)))}</span><b>${money(priceOf(l)*l.qty)}</b></div>`).join("")}<div class="r"><span>${t("Shipping")}</span><b>${ship?money(ship):t("Free")}</b></div>${fee?`<div class="r"><span>${t("Custom design (one-time)")}</span><b>${money(fee)}</b></div>`:""}<div class="r t"><span>${t("Total")}</span><span>${money(sub+ship+fee)}</span></div><button class="btn" style="width:100%;margin-top:14px" id="pay">${t("Pay securely")}</button><small style="color:var(--mut);display:block;margin-top:8px">${t("Made to order. See")} <a href="#/page/returns"><u>${t("returns")}</u></a>.</small></div></form></div>`;
  $("#co").onsubmit=async e=>{e.preventDefault();const f=Object.fromEntries(new FormData(e.target));const order={email:f.email,ship:{name:f.fn+" "+f.ln,a1:f.a1,a2:f.a2,city:f.city,st:f.st,zip:f.zip,phone:f.ph},items:cart.map(({_s,...l})=>l),lang,subtotal:sub,shipping:ship,total:sub+ship+fee,...(cu?{custom:{id:cu.id,k:cu.k}}:{})};
    const b=$("#pay");b.disabled=true;b.textContent=t("Opening secure payment…");let id;
    try{const r=await api("/api/orders",order);id=r.id;if(r.url){cart=[];saveCart();location.href=r.url;return}}catch(err){if(err.message!=="preview"){toast(err.message);b.disabled=false;b.textContent=t("Pay securely");return}id="PREVIEW-"+Date.now().toString(36).toUpperCase();const o=ls.get("ad_orders",[]);o.push({id,...order,status:"reserved",at:Date.now()});ls.set("ad_orders",o)}
    cart=[];saveCart();location.hash="#/done/"+id}
}
function done(q,[id]){app.dataset.title="Order";const paid=/paid=1/.test(location.hash);app.innerHTML=`<div class="wrap narrow"><span class="eyebrow">${paid?t("Payment received"):t("Reserved")}</span><h1>${t("Thank you!")}</h1><p id="dmsg">${paid?t("Order {0} is confirmed. Checking payment…",`<b>${esc(id||"")}</b>`):t("Your order {0} is saved. We will email you a secure payment link as soon as checkout opens.",`<b>${esc(id||"")}</b>`)}</p><a class="btn" href="#/shop">${t("Keep browsing")}</a></div>`;
  if(paid)api("/api/orders/confirm",{id}).then(r=>{const m=$("#dmsg");if(m)m.innerHTML=["paid","paid_test","in_production","shipped"].includes(r.status)?t("Order {0} is paid and on its way to print. We will email you tracking when it ships.",`<b>${esc(id)}</b>`):t("Order {0} received. Your payment is still processing; you will get an email when it clears.",`<b>${esc(id)}</b>`)}).catch(()=>{})}
/* ---------- custom design requests (customer) ---------- */
const customBanner=()=>`<section class="sec"><div class="wrap"><div class="custombox"><div><span class="eyebrow">${t("Custom design")}</span><h2>${t("Didn't find your breed?")}</h2><p>${t("Doesn't quite look like your dog? Send us a few photos and our artist will draw your own dog in our style, ready for any tee, hoodie, tank, polo or cap.")}</p></div><a class="btn" href="#/custom">${t("Get a custom design")}</a></div></div></section>`;
const resizeImg=(file,max=1600)=>new Promise((res,rej)=>{const r=new FileReader();r.onerror=rej;r.onload=()=>{const im=new Image();im.onerror=rej;im.onload=()=>{const k=Math.min(1,max/Math.max(im.width,im.height)),c=document.createElement("canvas");c.width=Math.round(im.width*k);c.height=Math.round(im.height*k);c.getContext("2d").drawImage(im,0,0,c.width,c.height);res(c.toDataURL("image/jpeg",.86))};im.src=r.result};r.readAsDataURL(file)});
async function custom(q,[id]){
  if(id)return customStatus(q,id);
  app.dataset.title="Custom design";const photos=[];
  const prodBoxes=cat.products.map(p=>`<label class="pick"><input type="checkbox" name="prod" value="${p.id}"><span>${prodName(p.id)}</span></label>`).join("");
  app.innerHTML=`<div class="wrap narrow2"><span class="eyebrow">${t("Custom design")}</span><h1 style="font-size:clamp(2rem,4vw,3rem)">${t("Your dog, drawn just for you")}</h1>
  <p style="color:var(--mut)">${t("Tell us about your dog and send photos. We reply by email with a preview on your products and a quote. You only pay if you love it.")}</p><div class="notice"><b>${t("One-time design fee: {0}",money(cat.custom_fee||2499))}</b> ${t("Pay it once, then put your dog on any product at regular prices, as often as you like.")}</div>
  <div class="panel tips"><h3>${t("Photo checklist (at least 5)")}</h3><ol><li>${t("Full body, standing, seen from the side")}</li><li>${t("Sitting, facing the camera")}</li><li>${t("A sharp close-up of the face, straight on")}</li><li>${t("The face from the side or at an angle")}</li><li>${t("Any favorite photo that shows their personality")}</li></ol><p>${t("Use bright, natural light, no filters, and let your dog fill the frame with the eyes clearly visible.")}</p></div>
  <form class="form" id="cuf">
   <div class="panel form"><h3>${t("You")}</h3><div class="row"><label>${t("Your name")}<input name="name" required autocomplete="name"></label><label>${t("Email")}<input name="email" type="email" required autocomplete="email" value="${esc(user?.email||"")}"></label></div></div>
   <div class="panel form"><h3>${t("Your dog")}</h3><div class="row"><label>${t("Dog's name")}<input name="dname"></label><label>${t("Breed or mix")}<input name="breed" placeholder="${t("e.g. Labrador and poodle mix")}"></label></div>
    <label>${t("Coat colors")}<input name="colors" placeholder="${t("e.g. black and tan, cream, merle")}"></label>
    <label>${t("Markings and patches")}<input name="markings" placeholder="${t("e.g. white chest, spot over one eye, brindle")}"></label>
    <div class="row"><label>${t("Ears")}<input name="ears" placeholder="${t("e.g. pointy, floppy, one up one down")}"></label><label>${t("Tail")}<input name="tail" placeholder="${t("e.g. curly, long, short")}"></label></div>
    <label>${t("Anything special we should capture?")}<textarea name="details" rows="3" placeholder="${t("Haircut, collar, favorite toy, missing tooth...")}"></textarea></label></div>
   <div class="panel form"><h3>${t("Style")}</h3><div class="row"><label>${t("Art style")}<select name="theme"><option value="">${t("Not sure, surprise me")}</option>${cat.themes.map(x=>`<option value="${x.id}">${tn(x.name)}</option>`).join("")}</select></label><label>${t("Mood")}<select name="style"><option value="">${t("Not sure, surprise me")}</option>${cat.styles.map(x=>`<option value="${x.id}">${tn(x.name)}</option>`).join("")}</select></label></div></div>
   <div class="panel form"><h3>${t("Which products do you want?")}</h3><div class="picks">${prodBoxes}</div><label>${t("About how many pieces?")}<input name="qty" inputmode="numeric" placeholder="1"></label><label>${t("Notes")}<textarea name="notes" rows="2"></textarea></label></div>
   <div class="panel form"><h3>${t("Photos")} <small id="pc">0 / 5</small></h3><label class="drop"><input type="file" id="pf" accept="image/*" multiple><span>${t("Tap to add photos")}</span></label><div class="thumbs" id="th"></div></div>
   <button class="btn" id="cus" style="width:100%">${t("Send my request")}</button><small style="color:var(--mut);display:block;margin-top:8px">${t("No payment now. We email you a preview and a quote first.")}</small>
  </form></div>`;
  const draw=()=>{$("#th").innerHTML=photos.map((p,i)=>`<div class="thumb"><img src="${p}" alt=""><button type="button" data-rm="${i}" aria-label="${t("Remove")}">×</button></div>`).join("");$("#pc").textContent=`${photos.length} / 5`;$("#pc").style.color=photos.length>=5?"var(--teal)":"var(--mut)"};
  $("#pf").onchange=async e=>{for(const f of [...e.target.files].slice(0,12-photos.length)){try{photos.push(await resizeImg(f))}catch{toast(t("One of the photos could not be used. Please use JPG or PNG photos."))}}e.target.value="";draw()};
  $("#th").onclick=e=>{const b=e.target.closest("[data-rm]");if(b){photos.splice(+b.dataset.rm,1);draw()}};
  $("#cuf").onsubmit=async e=>{e.preventDefault();const f=new FormData(e.target),g=k=>String(f.get(k)||"").trim();const prods=f.getAll("prod");
    if(photos.length<5){toast(t("Please add at least 5 photos of your dog"));return}if(!prods.length){toast(t("Choose at least one product"));return}
    const b=$("#cus");b.disabled=true;b.textContent=t("Sending…");
    const body={name:g("name"),email:g("email"),lang,dog:{name:g("dname"),breed:g("breed"),colors:g("colors"),markings:g("markings"),ears:g("ears"),tail:g("tail"),details:g("details")},style:{theme:g("theme"),style:g("style")},products:prods,qty:g("qty"),notes:g("notes"),photos:photos.map(d=>({mime:"image/jpeg",b64:d.split(",")[1]}))};
    try{const r=await api("/api/custom",body);location.hash=`#/custom/${r.id}?k=${r.k}&new=1`}catch(x){toast(x.message==="preview"?t("Request failed"):x.message);b.disabled=false;b.textContent=t("Send my request")}};
}
async function customStatus(q,id){
  app.dataset.title="Custom design";let r;
  try{r=await api(`/api/custom/${id}?k=${encodeURIComponent(q.k||"")}`)}catch(x){app.innerHTML=`<div class="wrap narrow"><h1>${t("Lost dog?")}</h1><p>${t("We could not find that request. Check the link in your email.")}</p></div>`;return}
  ls.set("ad_cfee",{...ls.get("ad_cfee",{}),[id]:r.fee_due??r.quote??0});
  const ready=["quoted","approved","paid"].includes(r.status)&&r.art.length;
  const steps=[["new",t("Request received")],["in_review",t("Our artist is drawing")],["quoted",t("Preview ready")],["paid",t("Ordered")]];const si=Math.max(0,steps.findIndex(s=>s[0]===(r.status==="approved"?"quoted":r.status)));
  app.innerHTML=`<div class="wrap narrow2"><span class="eyebrow">${t("Custom design")} · ${esc(id)}</span><h1 style="font-size:clamp(2rem,4vw,3rem)">${q.new?t("Thank you! Request sent."):esc(r.dog.name||t("Your custom design"))}</h1>
   <ol class="steps2">${steps.map((s,i)=>`<li class="${i<=si?"on":""}">${s[1]}</li>`).join("")}</ol>
   ${ready?`<p>${t("Here is your dog in our style. Pick any product, color and placement in the designer.")}</p><div class="grid" id="cprev"></div>${r.quote?`<p><b>${t("One-time design fee")}: ${money(r.quote)}</b> <small style="color:var(--mut)">${t("added once to your first order")}</small></p>`:""}${r.note?`<div class="notice">${esc(r.note)}</div>`:""}<a class="btn" href="#/design?custom=${id}&k=${encodeURIComponent(q.k)}&prod=${r.products[0]||"tee"}">${t("Design your products")}</a>`
   :`<p>${t("We have your photos. Our artist will email you a preview and a quote, usually within 2 to 4 business days. Keep this link to check progress.")}</p>`}</div>`;
  if(ready){const box=$("#cprev");const show=(r.products.length?r.products:["tee"]).slice(0,4);
    for(const pid of show){const p=PROD(pid);if(!p)continue;const part=r.art.includes("head")?"head":"body",size=(p.rule==="chest"||p.rule==="cap")?"s":"l";
      const col=p.colors.find(c=>c[2]);const svg=await renderSVG(pid,"front",col,{part,size,custom:id,k:q.k});box.insertAdjacentHTML("beforeend",`<div class="card"><div class="art mock on">${svg}</div><div class="meta"><b>${prodName(pid)}</b></div></div>`)}}
}
/* ---------- admin console (owner only; every call needs the admin token) ---------- */
const ADM_TABS=[["overview","Overview"],["orders","Orders"],["customers","Customers"],["subs","Subscribers"],["custom","Custom designs"],["inbox","Inbox"],["system","System"]];
const ST_COL={paid:"#c77d00",in_production:"#2563eb",shipped:"#15803d",paid_test:"#7c3aed",test_complete:"#7c3aed",test_failed:"#b91c1c",needs_attention:"#b91c1c",awaiting_payment:"#6b7280",reserved:"#6b7280",refunded:"#b91c1c",cancelled:"#6b7280"};
const pill=s=>`<span class="pill" style="background:${ST_COL[s]||"#6b7280"}">${esc(String(s).replace(/_/g," "))}</span>`;
const dt=x=>x?new Date(+x).toLocaleString([], {dateStyle:"medium",timeStyle:"short"}):"-";
const chanOf=id=>/^MK-ET/.test(id)?"Etsy":/^MK-EB/.test(id)?"eBay":/^MK-TI/.test(id)?"TikTok":"Store";
function csvDownload(name,rows){const c=rows.map(r=>r.map(v=>{v=String(v??"");return /[",\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v}).join(",")).join("\n");const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([c],{type:"text/csv"}));a.download=name;document.body.appendChild(a);a.click();a.remove()}
async function admin(q,[sec]){
  app.dataset.title="Admin";let tok=ls.get("ad_admin","");sec=ADM_TABS.some(t=>t[0]===sec)?sec:"overview";
  const A=async(path,body,method)=>{const r=await fetch(path,{method:method||(body?"POST":"GET"),headers:{"x-admin-token":tok,"content-type":"application/json"},body:body?JSON.stringify(body):undefined});const j=await r.json().catch(()=>({}));if(!r.ok)throw new Error(j.error||"failed");return j};
  if(!tok){app.innerHTML=`<div class="wrap narrow"><h1>Admin</h1><form class="form" id="at"><label>Admin token<input name="t" type="password" required></label><button class="btn">Enter</button></form></div>`;$("#at").onsubmit=e=>{e.preventDefault();ls.set("ad_admin",new FormData(e.target).get("t"));admin(q,[sec])};return}
  let H;try{H=await A("/api/internal/health")}catch(e){ls.set("ad_admin","");toast("Token rejected");return admin(q,[sec])}
  const iss=H.issues,nIss=iss.paid_stuck+iss.needs_attention+iss.in_production_old+iss.unpaid_old+iss.test_failed,bad=!H.db||!H.mail||H.stripe==="off"||!H.webhook||nIss>0||(H.fulfil_age_min!=null&&H.fulfil_age_min>45);
  app.innerHTML=`<div class="wrap" style="padding-bottom:70px"><div class="sh" style="padding-top:26px"><h1 style="font-size:2rem">Admin <span id="ahl" title="${bad?"Something needs attention":"All systems normal"}" style="font-size:.9rem;color:${bad?"#b91c1c":"#15803d"}">${bad?"● needs attention":"● all good"}</span></h1><button class="chip" id="alo">Lock</button></div>
   <div class="chips" id="anav" style="margin-bottom:18px">${ADM_TABS.map(([k,n])=>`<a class="chip ${k===sec?"on":""}" href="#/admin/${k}" data-tab="${k}">${n}${k==="orders"&&nIss?` <b style="color:#ef4444">(${nIss})</b>`:""}</a>`).join("")}</div><div id="ap"><p style="color:var(--mut)">Loading…</p></div></div>`;
  $("#alo").onclick=()=>{ls.set("ad_admin","");location.hash="#/"};
  const P=$("#ap"),T=(h)=>`<div style="overflow-x:auto">${h}</div>`,kpi=(l,v,s)=>`<div class="panel kpi" style="margin:0"><small style="color:var(--mut)">${l}</small><div style="font:700 1.6rem var(--f2)">${v}</div>${s?`<small style="color:var(--mut)">${s}</small>`:""}</div>`,grid=h=>`<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:18px">${h}</div>`;
  const S={};
  S.overview=async()=>{const s=await A("/api/internal/stats"),c=s.counts,mx=Math.max(1,...s.days.map(d=>d.rev));
    const al=[];if(iss.needs_attention)al.push(`${iss.needs_attention} order(s) need attention`);if(iss.paid_stuck)al.push(`${iss.paid_stuck} paid order(s) waiting over 30 min for print`);if(iss.unpaid_old)al.push(`${iss.unpaid_old} checkout(s) started but unpaid`);if(iss.in_production_old)al.push(`${iss.in_production_old} order(s) in production over 14 days`);if(iss.test_failed)al.push(`${iss.test_failed} test order(s) failed`);if(c.support_new)al.push(`${c.support_new} new support message(s)`);if(c.custom_open)al.push(`${c.custom_open} custom design request(s) to review`);if(!H.mail)al.push("Email sending is OFF");if(H.stripe==="off")al.push("Payments are OFF");if(H.checkout_paused)al.push("Checkout is PAUSED");if(H.fulfil_paused)al.push("Fulfilment is PAUSED");
    const top=(t,a)=>`<div class="panel" style="margin:0"><h3>${t}</h3>${a.length?a.map(x=>`<div style="display:flex;justify-content:space-between"><span>${esc(x.k)}</span><b>${x.v}</b></div>`).join(""):'<small style="color:var(--mut)">No sales yet</small>'}</div>`;
    P.innerHTML=(al.length?`<div class="panel" id="aal" style="border-color:#f59e0b"><h3>Needs your attention</h3>${al.map(x=>`<div>• ${esc(x)}</div>`).join("")}</div>`:`<div class="panel" id="aal"><b>✓ Nothing needs your attention.</b></div>`)+
    grid(kpi("Today",money(s.sum.today),s.sum.nToday+" orders")+kpi("Last 7 days",money(s.sum.d7),s.sum.n7+" orders")+kpi("Last 30 days",money(s.sum.d30),s.sum.n30+" orders")+kpi("Last 90 days",money(s.sum.d90),s.sum.n90+" orders")+kpi("Average order",money(s.aov),"last 90 days")+kpi("Customers",c.users,"with accounts")+kpi("Subscribers",c.subs,"newsletter")+kpi("Abandoned checkouts",c.abandoned,"last 7 days"))+
    `<div class="panel"><h3>Revenue, last 30 days <small>real paid orders, store + marketplaces</small></h3><svg viewBox="0 0 ${s.days.length*10} 80" style="width:100%;height:120px" role="img" aria-label="30 day revenue">${s.days.map((d,i)=>`<rect x="${i*10+1}" y="${78-(d.rev/mx)*74}" width="8" height="${Math.max(d.rev?2:0.6,(d.rev/mx)*74)}" rx="1.5" fill="#ff6a3d"><title>${d.d}: ${money(d.rev)} (${d.n})</title></rect>`).join("")}</svg><div style="display:flex;justify-content:space-between;font-size:.8rem;color:var(--mut)"><span>${s.days[0].d}</span><span>${s.days[s.days.length-1].d}</span></div></div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-bottom:14px">
     <div class="panel" style="margin:0"><h3>By channel <small>90 days</small></h3>${["Store","Etsy","eBay","TikTok"].map(k=>{const v=s.chan[k.toLowerCase()]||{n:0,rev:0};return `<div style="display:flex;justify-content:space-between"><span>${k}</span><span>${v.n} · <b>${money(v.rev)}</b></span></div>`}).join("")}</div>
     <div class="panel" style="margin:0"><h3>Order status <small>90 days</small></h3>${Object.entries(s.byStatus).map(([k,v])=>`<div style="display:flex;justify-content:space-between">${pill(k)}<b>${v}</b></div>`).join("")||'<small style="color:var(--mut)">No orders yet</small>'}</div>
     ${top("Top products",s.top.prod)}${top("Top breeds",s.top.breed)}${top("Top colors",s.top.color)}</div>`};
  S.orders=async()=>{let f=ls.get("ad_of","real");let list=[],qs="";
    const draw=async()=>{const r=await A("/api/internal/orders/all?g="+(f==="all"?"":f)+"&q="+encodeURIComponent(qs));list=r.items;
      $("#aol").innerHTML=T(`<table><tr><th>Order</th><th>Date</th><th>Customer</th><th>Channel</th><th>Items</th><th>Total</th><th>Status</th><th></th></tr>${list.map(o=>`<tr><td>${esc(o.id)}</td><td>${dt(o.created)}</td><td>${esc(o.email||"-")}</td><td>${chanOf(o.id)}</td><td>${(o.data.items||[]).reduce((a,i)=>a+(i.qty||1),0)}</td><td>${money(o.total||0)}</td><td>${pill(o.status)}</td><td><button class="chip" data-oo="${esc(o.id)}">Open</button></td></tr>`).join("")||'<tr><td colspan="8">No orders here</td></tr>'}</table>`)};
    P.innerHTML=`<div class="chips" id="aof" style="margin-bottom:10px">${[["real","Paid"],["problem","Problems"],["open","Unpaid / open"],["test","Test"],["refunded","Refunded / cancelled"],["all","All"]].map(([k,n])=>`<button class="chip ${k===f?"on":""}" data-f="${k}">${n}</button>`).join("")}<input id="aoq" placeholder="Search order ID or email" style="padding:8px 12px;border-radius:99px;border:1px solid var(--line);flex:1;min-width:160px"><button class="chip" id="aocsv">Export CSV</button></div><div id="aod"></div><div id="aol"></div>`;
    await draw();
    $("#aoq").oninput=e=>{clearTimeout(S._t);S._t=setTimeout(()=>{qs=e.target.value;draw()},300)};
    $("#aocsv").onclick=()=>csvDownload("orders.csv",[["id","date","email","channel","status","total_usd","items","tracking","printify_id"],...list.map(o=>[o.id,new Date(+o.created).toISOString(),o.email,chanOf(o.id),o.status,(o.total/100).toFixed(2),(o.data.items||[]).map(i=>`${i.qty}x ${i.prod} ${i.color} ${i.size}`).join("; "),o.tracking||"",o.printify_id||""])]);
    P.onclick=async e=>{const b=e.target.closest("button");if(!b)return;
      if(b.dataset.f){f=b.dataset.f;ls.set("ad_of",f);$$("#aof [data-f]").forEach(x=>x.classList.toggle("on",x.dataset.f===f));$("#aod").innerHTML="";return draw()}
      if(b.dataset.oo){const o=list.find(x=>x.id===b.dataset.oo),d=o.data,sp=d.ship||{};
        $("#aod").innerHTML=`<div class="panel" id="aodp"><h3>${esc(o.id)} ${pill(o.status)} <small>${dt(o.created)} · ${chanOf(o.id)}</small></h3>
         <p><b>${esc(o.email||"-")}</b> · ${esc(sp.name||"")}<br>${esc(sp.a1||"")} ${esc(sp.a2||"")}, ${esc(sp.city||"")}, ${esc(sp.st||"")} ${esc(sp.zip||"")} ${esc(sp.country||"")} ${sp.phone?"· "+esc(sp.phone):""}</p>
         ${T(`<table>${(d.items||[]).map(i=>{const dd=i.front||i.back||{};return `<tr><td>${i.qty}× ${esc(i.prod)}</td><td>${esc(i.color)} / ${esc(i.size)}</td><td>${[i.front&&"front: "+[i.front.breed,i.front.theme,i.front.style,i.front.part].filter(Boolean).join(" "),i.back&&"back: "+[i.back.breed,i.back.theme,i.back.style,i.back.part].filter(Boolean).join(" ")].filter(Boolean).map(esc).join("<br>")||esc(dd.breed||"")}</td></tr>`}).join("")}</table>`)}
         <p>Subtotal ${money(d.subtotal||0)} · Shipping ${money(d.shipping||0)}${d.design_fee?` · Design fee ${money(d.design_fee)}`:""} · <b>Total ${money(o.total||0)}</b>${(d.refunds||[]).map(r=>` · refunded ${money(r.amount)}`).join("")}</p>
         <p style="color:var(--mut)">Printify: ${esc(o.printify_id||"-")} · Tracking: ${o.tracking?`<a href="${esc(o.tracking)}" target="_blank" rel="noopener"><u>open</u></a>`:"-"}</p>
         ${(d.notes||[]).map(n=>`<div style="font-size:.9rem">📝 ${dt(n.t)}: ${esc(n.n)}</div>`).join("")}
         <div style="display:flex;gap:8px;flex-wrap:wrap;margin:12px 0"><button class="chip" data-a="resend">Resend receipt</button>${["needs_attention","test_failed"].includes(o.status)?'<button class="chip" data-a="requeue">Retry fulfilment</button>':""}${["needs_attention","reserved","awaiting_payment","paid"].includes(o.status)?'<button class="chip" data-a="cancel">Cancel order</button>':""}${d.session&&!["refunded","cancelled","reserved","awaiting_payment"].includes(o.status)?'<button class="chip" data-a="refund">Refund…</button>':""}</div>
         <div style="display:flex;gap:8px;flex-wrap:wrap"><input id="aon" placeholder="Add a private note" style="flex:1;min-width:160px;padding:8px 12px;border-radius:99px;border:1px solid var(--line)"><button class="chip" data-a="note">Save note</button></div>
         <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px"><input id="aot" placeholder="Tracking link (to mark shipped)" style="flex:1;min-width:160px;padding:8px 12px;border-radius:99px;border:1px solid var(--line)"><button class="chip" data-a="ship">Mark shipped + email</button></div></div>`;
        $("#aodp").dataset.id=o.id;$("#aodp").scrollIntoView({behavior:"smooth"});return}
      if(b.dataset.a){const id=$("#aodp").dataset.id,a=b.dataset.a;
        try{
          if(a==="resend"){await A("/api/internal/orders/"+id,{action:"resend"});toast("Receipt sent")}
          else if(a==="requeue"){await A("/api/internal/orders/"+id,{action:"requeue"});toast("Queued: next fulfilment run (within 10 min) retries it")}
          else if(a==="cancel"){if(!confirm("Cancel order "+id+"? This does not refund a card payment."))return;await A("/api/internal/orders/"+id,{action:"cancel"});toast("Cancelled")}
          else if(a==="refund"){const o=list.find(x=>x.id===id),v=prompt("Refund amount in USD (blank = full "+(o.total/100).toFixed(2)+"). The customer is emailed.","");if(v===null)return;const amt=v.trim()?Math.round(parseFloat(v)*100):null;if(v.trim()&&!(amt>0))return toast("Enter a valid amount");const r=await A("/api/internal/orders/"+id,{action:"refund",amount:amt});toast("Refunded "+money(r.amount))}
          else if(a==="note"){await A("/api/internal/orders/"+id,{action:"note",note:$("#aon").value});toast("Note saved")}
          else if(a==="ship"){const tr=$("#aot").value.trim();if(!/^https?:\/\//.test(tr))return toast("Paste the tracking link (https://…)");await A("/api/internal/orders/"+id,{status:"shipped",tracking:tr});toast("Marked shipped, customer emailed")}
          await draw();$("#aod").innerHTML=""}catch(er){toast(er.message)}}}};
  S.customers=async()=>{const r=(await A("/api/internal/customers")).items;P.innerHTML=`<p style="color:var(--mut)">${r.length} registered customers · <button class="chip" id="acc">Export CSV</button></p>`+T(`<table><tr><th>Email</th><th>Joined</th><th>Paid orders</th><th>Spent</th><th>Saved designs</th></tr>${r.map(x=>`<tr><td>${esc(x.email)}</td><td>${dt(x.created)}</td><td>${x.orders}</td><td>${money(x.spent)}</td><td>${x.designs}</td></tr>`).join("")||'<tr><td colspan="5">No customers yet</td></tr>'}</table>`);$("#acc").onclick=()=>csvDownload("customers.csv",[["email","joined","orders","spent_usd","designs"],...r.map(x=>[x.email,new Date(+x.created).toISOString(),x.orders,(x.spent/100).toFixed(2),x.designs])])};
  S.subs=async()=>{const r=(await A("/api/internal/subscribers")).items,act=r.filter(x=>!x.unsub);P.innerHTML=`<p style="color:var(--mut)">${act.length} active · ${r.length-act.length} unsubscribed · <button class="chip" id="asc">Export CSV</button></p>`+T(`<table><tr><th>Email</th><th>Joined</th><th>Lang</th><th>Status</th></tr>${r.map(x=>`<tr><td>${esc(x.email)}</td><td>${dt(x.created)}</td><td>${esc(x.lang||"en")}</td><td>${x.unsub?"unsubscribed":"active"}</td></tr>`).join("")||'<tr><td colspan="4">No subscribers yet</td></tr>'}</table>`);$("#asc").onclick=()=>csvDownload("subscribers.csv",[["email","joined","lang","status"],...r.map(x=>[x.email,new Date(+x.created).toISOString(),x.lang||"en",x.unsub?"unsubscribed":"active"])])};
  S.custom=async()=>{const list=(await A("/api/internal/custom")).items;
    P.innerHTML=`<table><tr><th>ID</th><th>Customer</th><th>Dog</th><th>Status</th><th>Photos</th><th>Art</th><th></th></tr>${list.map(x=>`<tr><td>${esc(x.id)}</td><td>${esc(x.email)}</td><td>${esc(x.data.dog.name||"")} ${esc(x.data.dog.breed||"")}</td><td>${esc(x.status)}</td><td>${x.photos}</td><td>${x.art.join(", ")||"-"}</td><td><button class="chip" data-open="${x.id}">Open</button></td></tr>`).join("")||`<tr><td colspan="7">No requests yet</td></tr>`}</table><div id="adet"></div>`;
    P.onclick=async e=>{const b=e.target.closest("button");if(!b||!b.dataset.open)return;const x=list.find(y=>y.id===b.dataset.open);const d=x.data;
      $("#adet").innerHTML=`<div class="panel"><h3>${esc(x.id)} · ${esc(x.name||"")} &lt;${esc(x.email)}&gt; · ${esc(x.lang)}</h3><p><b>Dog:</b> ${esc(JSON.stringify(d.dog))}</p><p><b>Style:</b> ${esc(d.style.theme||"any")} / ${esc(d.style.style||"any")} · <b>Products:</b> ${esc(d.products.join(", "))} · <b>Qty:</b> ${esc(d.qty||"")}</p><p><b>Notes:</b> ${esc(d.notes||"")}</p>
       <div class="thumbs" id="aph"></div>
       <form class="form" id="aart"><div class="row"><label>Head art (SVG or PNG)<input type="file" name="head" accept=".svg,image/svg+xml,image/png"></label><label>Full body art (SVG or PNG)<input type="file" name="body" accept=".svg,image/svg+xml,image/png"></label></div>
       <div class="row"><label>Design fee (USD)<input name="quote" inputmode="decimal" value="${x.quote!=null?(x.quote/100).toFixed(2):((cat.custom_fee||2499)/100).toFixed(2)}"></label><label>Status<select name="status">${["new","in_review","quoted","approved","paid","declined"].map(s=>`<option ${s===x.status?"selected":""}>${s}</option>`).join("")}</select></label></div>
       <label>Note to customer<textarea name="note" rows="2">${esc(x.note||"")}</textarea></label><div style="display:flex;gap:10px;flex-wrap:wrap"><button class="btn" name="save">Save</button><button class="btn ghost" name="send" type="button" id="asend">Save + send preview to customer</button><a class="btn ghost" target="_blank" href="#/custom/${x.id}?k=${x.token}">Customer view</a></div></form></div>`;
      for(let i=0;i<x.photos;i++){const r=await fetch(`/api/internal/custom/${x.id}/photo/${i}`,{headers:{"x-admin-token":tok}});if(r.ok){const u=URL.createObjectURL(await r.blob());$("#aph").insertAdjacentHTML("beforeend",`<a class="thumb" href="${u}" target="_blank"><img src="${u}" alt="photo ${i+1}"></a>`)}}
      const save=async notify=>{const f=$("#aart"),fd=new FormData(f),art={};
        for(const part of["head","body"]){const file=fd.get(part);if(file&&file.size){const isSvg=/svg/.test(file.type)||/\.svg$/i.test(file.name);art[part]=isSvg?{mime:"image/svg+xml",body:await file.text()}:{mime:"image/png",body:(await new Promise(r=>{const fr=new FileReader();fr.onload=()=>r(fr.result);fr.readAsDataURL(file)})).split(",")[1]}}}
        const st=notify?"quoted":fd.get("status");await A("/api/internal/custom/"+x.id,{art,quote:Math.round(parseFloat(fd.get("quote")||"0")*100),note:fd.get("note"),status:st,notify});toast(notify?"Saved and emailed":"Saved");admin(q,[sec])};
      $("#aart").onsubmit=e=>{e.preventDefault();save(false).catch(er=>toast(er.message))};$("#asend").onclick=()=>save(true).catch(er=>toast(er.message));
      $("#adet").scrollIntoView({behavior:"smooth"})}};
  S.inbox=async()=>{const sup=(await A("/api/internal/support?status=new")).items,ms=(await A("/api/internal/messages")).items;
    P.innerHTML=`<h2 style="font-size:1.3rem">Support inbox (new)</h2>${sup.length?sup.map(m=>`<div class="panel"><b>${esc(m.subject||"(no subject)")}</b> <small>${esc(m.from_addr)} · ${esc(m.mailbox)} · ${dt(m.created)}</small><p style="white-space:pre-wrap">${esc(m.body.slice(0,1500))}</p><button class="chip" data-done="${m.id}">Mark handled</button></div>`).join(""):`<p style="color:var(--mut)">Nothing new. The scheduled support assistant handles these automatically.</p>`}
     <h2 style="font-size:1.3rem;margin-top:26px">Website contact messages</h2>${ms.length?ms.map(m=>`<div class="panel"><small>${esc(m.email)} · ${dt(m.created)}</small><p style="white-space:pre-wrap">${esc(m.body.slice(0,1500))}</p><a class="chip" href="mailto:${esc(m.email)}">Reply by email</a></div>`).join(""):`<p style="color:var(--mut)">No messages yet.</p>`}`;
    P.onclick=async e=>{const b=e.target.closest("button");if(b&&b.dataset.done){await A("/api/internal/support/"+b.dataset.done,{status:"handled"});admin(q,[sec])}}};
  S.system=async()=>{const row=(ok,l,d)=>`<div style="display:flex;gap:10px;padding:6px 0;border-bottom:1px solid var(--line)"><span style="color:${ok?"#15803d":"#b91c1c"}">${ok?"●":"✖"}</span><span style="flex:1">${l}</span><small style="color:var(--mut)">${d||""}</small></div>`;
    const fa=H.fulfil_age_min;
    P.innerHTML=`<div class="panel"><h3>Health</h3>${row(H.db,"Database",H.db?"connected":"DOWN")}${row(H.mail,"Email sending (Resend)",H.mail?"on":"OFF")}${row(H.stripe!=="off","Payments (Stripe)",H.stripe==="live"?"LIVE mode":H.stripe==="test"?"TEST mode (no real charges)":"OFF")}${row(H.webhook,"Stripe webhook secret",H.webhook?"set":"missing")}${row(H.owner_email,"Owner notifications",H.owner_email?"on":"missing")}${row(fa!=null&&fa<=45,"Fulfilment robot",fa==null?"has not reported yet":fa+" min ago (runs every 10 min)")}${row(H.providers.google,"Google sign-in",H.providers.google?"on":"off")}${row(!H.checkout_paused,"Checkout",H.checkout_paused?"PAUSED":"open")}${row(!H.fulfil_paused,"Sending paid orders to print",H.fulfil_paused?"PAUSED":"running")}</div>
     <div class="panel"><h3>Order problems</h3>${row(!iss.needs_attention,"Orders needing attention",iss.needs_attention)}${row(!iss.paid_stuck,"Paid but waiting over 30 min",iss.paid_stuck)}${row(!iss.unpaid_old,"Checkouts unpaid over 2 h (last 7 days)",iss.unpaid_old)}${row(!iss.in_production_old,"In production over 14 days",iss.in_production_old)}${row(!iss.test_failed,"Failed test orders",iss.test_failed)}</div>
     <div class="panel"><h3>Controls</h3><div style="display:flex;gap:10px;flex-wrap:wrap"><button class="chip" data-k="checkout_paused" data-v="${H.checkout_paused?0:1}">${H.checkout_paused?"▶ Resume checkout":"⏸ Pause checkout (emergency)"}</button><button class="chip" data-k="fulfil_paused" data-v="${H.fulfil_paused?0:1}">${H.fulfil_paused?"▶ Resume sending to print":"⏸ Pause sending to print"}</button></div>
      <form id="atm" style="display:flex;gap:8px;flex-wrap:wrap;margin-top:14px"><input name="to" type="email" required placeholder="Send a test email to…" style="flex:1;min-width:180px;padding:8px 12px;border-radius:99px;border:1px solid var(--line)"><button class="chip">Send test email</button></form></div>
     <div class="panel"><h3>Your dashboards</h3><div style="display:flex;gap:8px;flex-wrap:wrap">${[["Stripe","https://dashboard.stripe.com/payments"],["Printify orders","https://printify.com/app/orders"],["Etsy shop","https://www.etsy.com/your/shops/me/dashboard"],["eBay seller hub","https://www.ebay.com/sh/ovw"],["TikTok Shop seller","https://seller-us.tiktok.com/homepage"],["Cloudflare","https://dash.cloudflare.com/"],["Fulfilment runs","https://github.com/Rodantmat/Alphadog-Styles/actions/workflows/store-fulfill.yml"]].map(([n,u])=>`<a class="chip" target="_blank" rel="noopener" href="${u}">${n} ↗</a>`).join("")}</div></div>`;
    P.onclick=async e=>{const b=e.target.closest("button[data-k]");if(!b)return;if(b.dataset.v==="1"&&!confirm("Pause now? "+(b.dataset.k==="checkout_paused"?"Customers cannot place orders until you resume.":"Paid orders will wait until you resume.")))return;try{await A("/api/internal/kv/"+b.dataset.k,{v:b.dataset.v==="1"?"1":"0"});toast("Done");admin(q,[sec])}catch(er){toast(er.message)}};
    $("#atm").onsubmit=async e=>{e.preventDefault();try{const r=await A("/api/internal/send",{to:new FormData(e.target).get("to"),subject:"AlphaDog admin test email",html:"<p>If you can read this, order emails are working.</p>"});toast(r.ok?"Test email sent":"Email failed")}catch(er){toast(er.message)}}};
  try{await S[sec]()}catch(er){P.innerHTML=`<div class="panel" style="border-color:#b91c1c"><b>This section failed to load:</b> ${esc(er.message)}<br><small style="color:var(--mut)">${esc(String(er.stack||"").split("\n").slice(0,3).join(" | ").slice(0,300))}</small></div>`;console.error("admin section",sec,er)}
}

/* ---------- account ---------- */
function auth(q){user={email:q.email,token:q.token};ls.set("ad_user",user);refreshAcct();toast(t("Welcome!"));const pend=ls.get("ad_pending",null);if(pend&&q.next==="design"){window.__edit=pend.s;try{localStorage.removeItem("ad_pending")}catch{}saveDesign(pend.s).then(()=>{location.hash="#/design"});return}location.hash="#/"+(q.next&&/^[\w/?=&-]+$/.test(q.next)?q.next:"account")}
const SOC={google:["Google",'<svg viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.5l6.7-6.7C35.6 2.4 30.2 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.8 6.1C12.3 13.6 17.7 9.5 24 9.5z"/><path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.6 3-2.3 5.5-4.8 7.2l7.5 5.8c4.4-4.1 7.1-10.1 7.1-17.5z"/><path fill="#FBBC05" d="M10.4 28.7A14.5 14.5 0 0 1 9.5 24c0-1.6.3-3.2.8-4.7l-7.8-6.1A24 24 0 0 0 0 24c0 3.9.9 7.5 2.6 10.8l7.8-6.1z"/><path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.5-5.8c-2.1 1.4-4.9 2.3-8.4 2.3-6.3 0-11.7-4.1-13.6-9.8l-7.8 6.1C6.5 42.6 14.6 48 24 48z"/></svg>'],facebook:["Facebook",'<svg viewBox="0 0 24 24"><path fill="#1877F2" d="M24 12a12 12 0 1 0-13.9 11.9v-8.4H7.1V12h3V9.4c0-3 1.8-4.7 4.5-4.7 1.3 0 2.7.2 2.7.2v3h-1.5c-1.5 0-2 .9-2 1.9V12h3.4l-.5 3.5h-2.9v8.4A12 12 0 0 0 24 12z"/></svg>']};
const socialBtns=(next)=>{const pv=cfg.providers||{};const on=Object.keys(SOC).filter(k=>pv[k]&&k!=="facebook"/*hidden until Meta app is Live*/);if(!on.length)return "";return `<div class="socials">${on.map(k=>`<a class="btn social" href="/api/auth/oauth/${k}/start?next=${next}">${SOC[k][1]}${t("Continue with {0}",SOC[k][0])}</a>`).join("")}<div class="or"><span>${t("or use your email")}</span></div></div>`};
function login(q){
  app.dataset.title="Log in";let step=1,email="";
  const draw=()=>{app.innerHTML=`<div class="wrap narrow"><h1 style="font-size:2.2rem">${t("Log in or sign up")}</h1><p style="color:var(--mut)">${t("No password needed.")}</p>${socialBtns(q.next||"account")}${cfg.api?"":`<div class="notice">${t("Preview mode: the email service is not connected yet, so use code")} <b>123456</b>.</div>`}<form class="form" id="lf">${step===1?`<label>${t("Email")}<input type="email" name="email" required autocomplete="email" value="${esc(email)}"></label><button class="btn">${t("Send my code")}</button>`:`<label>${esc(t("Code sent to {0}",email))}<input name="code" required inputmode="numeric" pattern="\\d{6}" maxlength="6" autocomplete="one-time-code"></label><button class="btn">${t("Log in")}</button><button type="button" class="chip" id="back">${t("Use a different email")}</button>`}</form></div>`;
    $("#lf").onsubmit=async e=>{e.preventDefault();const f=Object.fromEntries(new FormData(e.target));
      try{
        if(step===1){email=f.email;try{await api("/api/auth/request",{email,lang})}catch(x){if(x.message!=="preview")throw x}step=2;draw();return}
        let r;try{r=await api("/api/auth/verify",{email,code:f.code})}catch(x){if(x.message!=="preview")throw x;if(f.code!=="123456")throw new Error(t("That code is not right"));r={token:"preview",email}}
        user={email:r.email||email,token:r.token};ls.set("ad_user",user);refreshAcct();toast(t("Welcome!"));const pend=ls.get("ad_pending",null);if(pend&&q.next==="design"){window.__edit=pend.s;try{localStorage.removeItem("ad_pending")}catch{}await saveDesign(pend.s);location.hash="#/design";return}location.hash="#/account"
      }catch(x){toast(x.message)}};
    const bk=$("#back");if(bk)bk.onclick=()=>{step=1;draw()};$$("[data-soc]").forEach(b=>b.onclick=()=>toast(t("This sign-in is switching on soon. Use email for now.")))};if(q.err)toast(q.err);draw();
}
async function account(){
  app.dataset.title="Account";if(!user){location.hash="#/login";return}
  let designs=[],orders=[];
  try{designs=(await api("/api/designs")).items;orders=(await api("/api/orders")).items}catch(e){designs=ls.get("ad_designs",[]);orders=ls.get("ad_orders",[])}
  app.innerHTML=`<div class="wrap" style="padding-bottom:60px"><div class="sh" style="padding-top:34px"><div><h1 style="font-size:clamp(2rem,4vw,3rem)">${t("Hi there 🐾")}</h1><p>${esc(user.email)}</p></div><button class="btn ghost sm" id="lo">${t("Log out")}</button></div>
  <h2 style="font-size:1.5rem">${t("Saved designs")}</h2>${designs.length?`<div class="grid" id="sd">${designs.map(d=>`<div class="card"><div class="art" data-sd="${d.id}"></div><div class="meta"><b>${prodName(d.s.prod)}</b><span>${esc(colorLabel(d.s.prod,d.s.color))}</span><div style="margin-top:8px;display:flex;gap:8px"><button class="btn sm" data-open="${d.id}">${t("Open")}</button><button class="chip" data-del="${d.id}">${t("Delete")}</button></div></div></div>`).join("")}</div>`:`<p style="color:var(--mut)">${t("Nothing saved yet.")} <a href="#/design"><u>${t("Design something")}</u></a> ${t("and tap Save.")}</p>`}
  <h2 style="font-size:1.5rem;margin-top:36px">${t("Orders")}</h2>${orders.length?`<table><tr><th>${t("Order")}</th><th>${t("Status")}</th><th>${t("Total")}</th></tr>${orders.map(o=>`<tr><td>${esc(o.id)}</td><td>${esc(t(o.status||"reserved"))}${o.tracking?` · <a href="${esc(o.tracking)}" target="_blank" rel="noopener"><u>${t("Track")}</u></a>`:""}</td><td>${money(o.total||0)}</td></tr>`).join("")}</table>`:`<p style="color:var(--mut)">${t("No orders yet.")}</p>`}</div>`;
  designs.forEach(async d=>{const el=$(`[data-sd="${d.id}"]`);if(el){const S=d.s;el.style.background="#f3ecdf";el.innerHTML=await renderSVG(S.prod,S.front.opt!=="none"?"front":"back",(cat.products.find(p=>p.id===S.prod).colors.find(c=>c[0]===S.color)||cat.products[0].colors[0]),toDesign(S.front.opt!=="none"?S.front:S.back,S.front.opt!=="none"?"front":"back",S))}});
  $("#lo").onclick=()=>{user=null;ls.set("ad_user",null);refreshAcct();location.hash="#/"};
  app.onclick=async e=>{const b=e.target.closest("button");if(!b)return;if(b.dataset.open){window.__edit=designs.find(x=>x.id===b.dataset.open).s;location.hash="#/design?x="+Date.now()}if(b.dataset.del){try{await api("/api/designs/"+b.dataset.del,null,"DELETE")}catch{ls.set("ad_designs",ls.get("ad_designs",[]).filter(x=>x.id!==b.dataset.del))}account()}}
}
const refreshAcct=()=>{$("#acct").title=user?user.email:t("Log in")};
/* ---------- static pages ---------- */
function page(q,[id]){const p=(ALLPAGES[lang]||ALLPAGES.en)[id];if(!p)return notFound();app.dataset.title=p[0];app.innerHTML=`<div class="wrap prose"><h1 style="font-size:clamp(2rem,4vw,3rem)">${p[0]}</h1>${p[1]}</div>`;
  const cf=$("#cf");if(cf)cf.onsubmit=async e=>{e.preventDefault();try{await api("/api/contact",{...Object.fromEntries(new FormData(cf)),lang})}catch(x){if(x.message!=="preview"){toast(x.message);return}}cf.innerHTML="<p><b>"+t("Thanks! We will reply by email soon.")+"</b></p>"}}
/* ---------- boot ---------- */
$("#burger").onclick=()=>$("#links").classList.toggle("open");
$("#yr").textContent=new Date().getFullYear();
$("#news").onsubmit=async e=>{e.preventDefault();const email=e.target.querySelector("input").value;try{await api("/api/subscribe",{email,lang})}catch(x){if(x.message!=="preview"){toast(x.message);return}}e.target.reset();toast(t("You're in the pack!"))};
function applyStatic(){
  document.documentElement.lang=lang==="pt"?"pt-BR":lang;
  $("#promo").textContent=t("Free US shipping on orders over $75")+" \u00a0·\u00a0 "+t("Made to order, printed just for you");
  $$("[data-i]").forEach(e=>{e.textContent=t(e.dataset.i)});
  $$("[data-iph]").forEach(e=>{e.placeholder=t(e.dataset.iph)});
  $$("[data-ia]").forEach(e=>{e.setAttribute("aria-label",t(e.dataset.ia))});
  const md=$('meta[name=description]');if(md)md.content=t("Custom dog-breed tees and hoodies. Pick your breed, art style and placement, we print it to order and ship it across the US.");
  const sel=$("#lang");if(sel){sel.value=lang;sel.onchange=()=>{setLang(sel.value);applyStatic();refreshAcct();saveCart();route()}}
}
(async()=>{
  cat=await (await fetch("data/catalog.json")).json();setCal(cat.cal);registerProducts(cat.products);
  try{cfg=await (await fetch("data/config.json")).json()}catch{}
  try{const h=await (await fetch("api/health")).json();if(h&&h.ok)cfg={api:"same",providers:h.providers||{}}}catch{}
  applyStatic();saveCart();refreshAcct();window.addEventListener("hashchange",route);route();
})();
