// AlphaDog Styles store backend. Secrets (set with wrangler secret put): ADMIN_TOKEN, RESEND_API_KEY (optional), STRIPE_* (later).
import {priceCents} from "../js/placement.js";
import {makeDB,diag} from "./db.js";
import PostalMime from "postal-mime";
import cat from "../data/catalog.json";
import MPLAN from "../data/market_plan.json";
const esc=x=>String(x).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const J=(o,s=200,h={})=>new Response(JSON.stringify(o),{status:s,headers:{"content-type":"application/json","cache-control":"no-store",...h}});
const err=(m,s=400)=>J({error:m},s);
const now=()=>Date.now();
const hex=b=>[...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join("");
const sha=async s=>hex(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(s)));
const rnd=n=>hex(crypto.getRandomValues(new Uint8Array(n)));
const okEmail=e=>typeof e==="string"&&e.length<255&&/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e);
async function mail(env,to,subject,html,replyTo,from){
  if(env.RESEND_API_KEY){
    const body={from:from||env.MAIL_FROM,to:[to],subject,html};const rt=replyTo||env.OWNER_EMAIL;if(rt)body.reply_to=rt;
    const r=await fetch((env.MAIL_BASE||"https://api.resend.com")+"/emails",{method:"POST",headers:{authorization:"Bearer "+env.RESEND_API_KEY,"content-type":"application/json"},body:JSON.stringify(body)});
    return r.ok;
  }
  return false;
}
const SUPPORT_FROM="AlphaDog Support <support@alphadogstyles.com>", CUSTOM_FROM="AlphaDog Custom <customization@alphadogstyles.com>";
const CUSTOM_EM={
 en:{gotS:id=>`We got your custom design request (${id})`,gotP:n=>`Thanks! We received your photos${n?" of "+n:""}. Our artist will review them and email you a preview and a quote, usually within 2 to 4 business days.`,view:"View your request",readyS:id=>`Your custom design preview is ready (${id})`,readyP:"Good news: your dog's custom design is ready. Open the link to see it on your products, check the quote and order."},
 es:{gotS:id=>`Recibimos tu solicitud de diseño personalizado (${id})`,gotP:n=>`¡Gracias! Recibimos tus fotos${n?" de "+n:""}. Nuestro artista las revisará y te enviará una vista previa y una cotización, normalmente en 2 a 4 días hábiles.`,view:"Ver tu solicitud",readyS:id=>`La vista previa de tu diseño está lista (${id})`,readyP:"Buenas noticias: el diseño personalizado de tu perro está listo. Abre el enlace para verlo en tus productos, revisar la cotización y pedir."},
 pt:{gotS:id=>`Recebemos seu pedido de design personalizado (${id})`,gotP:n=>`Obrigado! Recebemos suas fotos${n?" de "+n:""}. Nosso artista vai analisar e enviar uma prévia e um orçamento por e-mail, normalmente em 2 a 4 dias úteis.`,view:"Ver seu pedido",readyS:id=>`A prévia do seu design está pronta (${id})`,readyP:"Boa notícia: o design personalizado do seu cachorro está pronto. Abra o link para ver nos produtos, conferir o orçamento e fazer o pedido."}};
/* ---------- customer emails in the customer's language ---------- */
const L=x=>["es","pt"].includes(x)?x:"en";
const EM={
 en:{code:"Your AlphaDog Styles login code",codeH:"Your code:",codeP:"It expires in 10 minutes. If you did not ask for it, ignore this email.",paidS:id=>`Order ${id} confirmed`,paidP:(id,tot)=>`Thank you! Payment received for order <b>${id}</b> ($${tot}). We are sending it to print now and will email tracking when it ships.`,shipS:id=>`Order ${id} has shipped`,shipP:"Your AlphaDog order is on its way.",track:"Track your package",resS:id=>`Order ${id} reserved`,resP:(id,tot)=>`Thanks for your order <b>${id}</b>. We will email you a secure payment link as soon as checkout opens.</p><p>Total: $${tot}`},
 es:{code:"Tu código de acceso de AlphaDog Styles",codeH:"Tu código:",codeP:"Vence en 10 minutos. Si no lo pediste, ignora este correo.",paidS:id=>`Pedido ${id} confirmado`,paidP:(id,tot)=>`¡Gracias! Recibimos el pago del pedido <b>${id}</b> ($${tot}). Lo estamos enviando a impresión y te enviaremos el seguimiento cuando salga.`,shipS:id=>`Tu pedido ${id} ya fue enviado`,shipP:"Tu pedido de AlphaDog va en camino.",track:"Seguir tu paquete",resS:id=>`Pedido ${id} reservado`,resP:(id,tot)=>`Gracias por tu pedido <b>${id}</b>. Te enviaremos un enlace de pago seguro en cuanto se abra el pago.</p><p>Total: $${tot}`},
 pt:{code:"Seu código de acesso da AlphaDog Styles",codeH:"Seu código:",codeP:"Expira em 10 minutos. Se você não pediu, ignore este e-mail.",paidS:id=>`Pedido ${id} confirmado`,paidP:(id,tot)=>`Obrigado! Recebemos o pagamento do pedido <b>${id}</b> ($${tot}). Estamos enviando para impressão e enviaremos o rastreamento quando sair.`,shipS:id=>`Seu pedido ${id} foi enviado`,shipP:"Seu pedido da AlphaDog está a caminho.",track:"Rastrear seu pacote",resS:id=>`Pedido ${id} reservado`,resP:(id,tot)=>`Obrigado pelo seu pedido <b>${id}</b>. Enviaremos um link de pagamento seguro por e-mail assim que o pagamento abrir.</p><p>Total: $${tot}`}
};


/* ---------- Stripe (Checkout Sessions via REST; no SDK) ---------- */
const stripeEnc=(o,pre="",out=[])=>{for(const[k,v]of Object.entries(o)){const key=pre?`${pre}[${k}]`:k;if(v&&typeof v==="object")stripeEnc(v,key,out);else out.push(encodeURIComponent(key)+"="+encodeURIComponent(v))}return out};
async function stripe(env,method,path,params){
  const r=await fetch((env.STRIPE_BASE||"https://api.stripe.com/v1")+path,{method,headers:{authorization:"Bearer "+env.STRIPE_SECRET_KEY,"content-type":"application/x-www-form-urlencoded"},body:method==="GET"?undefined:stripeEnc(params||{}).join("&")});
  const j=await r.json();if(!r.ok)throw new Error(j.error?.message||"Payment error");return j;
}
async function stripeVerify(raw,header,secret){
  const p=Object.fromEntries((header||"").split(",").map(x=>x.split("=")));if(!p.t||!p.v1)return false;
  if(Math.abs(Date.now()/1000-Number(p.t))>600)return false;
  const key=await crypto.subtle.importKey("raw",new TextEncoder().encode(secret),{name:"HMAC",hash:"SHA-256"},false,["sign"]);
  const sig=hex(await crypto.subtle.sign("HMAC",key,new TextEncoder().encode(p.t+"."+raw)));
  return sig.length===p.v1.length&&[...sig].reduce((a,c,i)=>a|(c.charCodeAt(0)^p.v1.charCodeAt(i)),0)===0;
}
async function markPaid(DB,env,id,live){
  const r=await DB.prepare("UPDATE orders SET status=?,updated=? WHERE id=? AND status IN ('reserved','awaiting_payment')").bind(live?'paid':'paid_test',now(),id).run();
  const o=await DB.prepare("SELECT email,total,data FROM orders WHERE id=?").bind(id).first();
  if(o&&r.meta?.changes!==0){const E=EM[L((JSON.parse(o.data)||{}).lang)],tot=(o.total/100).toFixed(2);
    await mail(env,o.email,E.paidS(id),`<p>${E.paidP(id,tot)}</p>`);
    if(env.OWNER_EMAIL)await mail(env,env.OWNER_EMAIL,`${live?"New order":"TEST order"} ${id} ($${tot})`,`<p>${live?"New paid order":"Stripe TEST order"} <b>${id}</b> from ${o.email}, total $${tot}. It is being sent to print automatically.</p>`,o.email);}
}

/* ---------- social login (Google / Facebook / Apple). Enabled when the matching secrets exist. ---------- */
const b64u=b=>btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");
const b64uJ=o=>b64u(new TextEncoder().encode(JSON.stringify(o)));
const unb64=s=>{s=s.replace(/-/g,"+").replace(/_/g,"/");return atob(s+"=".repeat((4-s.length%4)%4))};
function providers(env){return {google:!!(env.GOOGLE_CLIENT_ID&&env.GOOGLE_CLIENT_SECRET),facebook:!!(env.FACEBOOK_APP_ID&&env.FACEBOOK_APP_SECRET),apple:!!(env.APPLE_CLIENT_ID&&env.APPLE_TEAM_ID&&env.APPLE_KEY_ID&&env.APPLE_PRIVATE_KEY)}}
async function appleSecret(env){
  const pem=env.APPLE_PRIVATE_KEY.replace(/\\n/g,"\n").replace(/-----[^-]+-----/g,"").replace(/\s+/g,"");
  const key=await crypto.subtle.importKey("pkcs8",Uint8Array.from(atob(pem),c=>c.charCodeAt(0)),{name:"ECDSA",namedCurve:"P-256"},false,["sign"]);
  const head=b64uJ({alg:"ES256",kid:env.APPLE_KEY_ID}),t=Math.floor(Date.now()/1000),pl=b64uJ({iss:env.APPLE_TEAM_ID,iat:t,exp:t+600,aud:"https://appleid.apple.com",sub:env.APPLE_CLIENT_ID});
  const sig=await crypto.subtle.sign({name:"ECDSA",hash:"SHA-256"},key,new TextEncoder().encode(head+"."+pl));
  return head+"."+pl+"."+b64u(sig);
}
const OAUTH={
 google:{auth:"https://accounts.google.com/o/oauth2/v2/auth",scope:"openid email",id:e=>e.GOOGLE_CLIENT_ID,extra:{}},
 facebook:{auth:"https://www.facebook.com/v19.0/dialog/oauth",scope:"email public_profile",id:e=>e.FACEBOOK_APP_ID,extra:{}},
 apple:{auth:"https://appleid.apple.com/auth/authorize",scope:"name email",id:e=>e.APPLE_CLIENT_ID,extra:{response_mode:"form_post"}}
};
async function oauthEmail(prov,code,redirect,env){
  if(prov==="google"){
    const t=await (await fetch("https://oauth2.googleapis.com/token",{method:"POST",body:new URLSearchParams({code,client_id:env.GOOGLE_CLIENT_ID,client_secret:env.GOOGLE_CLIENT_SECRET,redirect_uri:redirect,grant_type:"authorization_code"})})).json();
    if(!t.access_token)throw new Error("Google sign-in failed");
    const u=await (await fetch("https://openidconnect.googleapis.com/v1/userinfo",{headers:{authorization:"Bearer "+t.access_token}})).json();
    if(!u.email||u.email_verified===false)throw new Error("Google did not share a verified email");return u.email;
  }
  if(prov==="facebook"){
    const t=await (await fetch("https://graph.facebook.com/v19.0/oauth/access_token?"+new URLSearchParams({client_id:env.FACEBOOK_APP_ID,client_secret:env.FACEBOOK_APP_SECRET,redirect_uri:redirect,code}))).json();
    if(!t.access_token)throw new Error("Facebook sign-in failed");
    const u=await (await fetch("https://graph.facebook.com/me?fields=email&access_token="+t.access_token)).json();
    if(!u.email)throw new Error("Facebook did not share your email. Please allow email access or use another sign-in.");return u.email;
  }
  const t=await (await fetch("https://appleid.apple.com/auth/token",{method:"POST",body:new URLSearchParams({code,client_id:env.APPLE_CLIENT_ID,client_secret:await appleSecret(env),redirect_uri:redirect,grant_type:"authorization_code"})})).json();
  if(!t.id_token)throw new Error("Apple sign-in failed");
  const pl=JSON.parse(unb64(t.id_token.split(".")[1]));if(!pl.email)throw new Error("Apple did not share an email");return pl.email;
}
async function startSession(env,email){const DB=env._db;
  email=email.toLowerCase();await DB.prepare("INSERT INTO users(email,created) VALUES(?,?) ON CONFLICT DO NOTHING").bind(email,now()).run();
  const token=rnd(32);await DB.prepare("INSERT INTO sessions(hash,email,exp) VALUES(?,?,?)").bind(await sha(token),email,now()+30*864e5).run();return token;
}
async function auth(req,env){const DB=env._db;
  const t=(req.headers.get("authorization")||"").replace(/^Bearer /,"");if(!t)return null;
  const r=await DB.prepare("SELECT email,exp FROM sessions WHERE hash=?").bind(await sha(t)).first();
  return r&&r.exp>now()?r.email:null;
}
function validItem(it,custId){
  const p=cat.products.find(x=>x.id===it.prod); if(!p)return null;
  const c=p.colors.find(x=>x[0]===it.color&&x[2]); if(!c||!p.sizes.includes(it.size))return null;
  const qty=Math.max(1,Math.min(20,parseInt(it.qty)||1));
  const side=(d,k)=>{ if(!d)return null; if(!(p.sides||["front","back"]).includes(k))return false; const al=p.opts&&p.opts[k];
    if(d.custom){ if(!custId)return false; const oc=cat[k+"_opts"].find(x=>x.part===d.part&&x.size===d.size&&(!al||al.includes(x.id))); return oc?{part:d.part,size:d.size,custom:custId}:false } const o=cat[k+"_opts"].find(x=>x.part===d.part&&x.size===d.size&&(!al||al.includes(x.id))); if(!o||!cat.breeds.some(b=>b.slug===d.breed)||!cat.themes.some(t=>t.id===d.theme)||!cat.styles.some(s=>s.id===d.style))return false; return {part:d.part,size:d.size,breed:d.breed,theme:d.theme,style:d.style}};
  const front=side(it.front,"front"),back=side(it.back,"back"); if(front===false||back===false||(!front&&!back))return null;
  return {prod:it.prod,color:it.color,size:it.size,qty,front,back};
}

/* ---------- marketplaces (consolidated listings, not linked to Printify): SKU -> store order item ---------- */
function marketItem(sku,qty){
  const m=String(sku||"").trim().toUpperCase().match(/^([A-Z])-([A-Z]{2})-(\d)-([A-Z]{2})(?:-(\w+))?$/); if(!m)return null;
  const pk=Object.keys(MPLAN.products).find(k=>MPLAN.products[k].L===m[1]); if(!pk)return null; const P=MPLAN.products[pk];
  const breed=Object.keys(MPLAN.codes.breed).find(k=>MPLAN.codes.breed[k]===m[2]); const d=P.designs.find(x=>x.code===m[3]); const c=P.colors.find(x=>x.code===m[4]);
  if(!breed||!d||!c)return null; const [theme,style]=d.art.split("_");
  const side=o=>o?{part:o.startsWith("head")?"head":"body",size:o.slice(-1),breed,theme,style}:null;
  return validItem({prod:c.prod,color:c.color,size:m[5]||"One size",qty,front:side(d.front),back:side(d.back)});
}
async function kvGet(DB,k){const r=await DB.prepare("SELECT v FROM kv WHERE k=?").bind(k).first();return r?JSON.parse(r.v):null}
async function kvSet(DB,k,v){await DB.prepare("INSERT INTO kv(k,v,updated) VALUES(?,?,?) ON CONFLICT(k) DO UPDATE SET v=EXCLUDED.v,updated=EXCLUDED.updated").bind(k,JSON.stringify(v),Date.now()).run()}
export default {
 // Inbound email (Cloudflare Email Routing -> this Worker): support@ and customization@ land in support_inbox for the scheduled support assistant.
 async email(message,env,ctx){
   const db=env.DB||makeDB(env.DATABASE_URL,env.HYPERDRIVE);
   try{
     const raw=await new Response(message.raw).arrayBuffer(); const mail_=await PostalMime.parse(raw);
     const to=String(message.to||"").toLowerCase(), box=to.startsWith("customization")?"custom":"support";
     const text=(mail_.text||String(mail_.html||"").replace(/<[^>]+>/g," ")).slice(0,20000);
     await db.prepare("INSERT INTO support_inbox(mailbox,from_addr,subject,body,raw_size,created) VALUES(?,?,?,?,?,?)").bind(box,String(message.from||"").toLowerCase(),String(mail_.subject||"").slice(0,300),text,raw.byteLength,Date.now()).run();
   }finally{ if(db.close)ctx.waitUntil(db.close()) }
   const fwd=String(message.to||"").toLowerCase().startsWith("customization")?env.FORWARD_CUSTOM:env.FORWARD_SUPPORT;  // separate mailboxes (verified Email Routing destinations)
   if(fwd){try{await message.forward(fwd)}catch(e){}}
 },
 async fetch(req,env0,ctx){const box={};try{return await this.handle(req,env0,ctx,box)}finally{if(box.db&&box.db.close)ctx.waitUntil(box.db.close())}},
 async handle(req,env0,ctx,box){
  const u=new URL(req.url),path=u.pathname,m=req.method;
  const env={...env0};if(path.startsWith("/api/")&&!path.startsWith("/api/health")){env._db=env0.DB||makeDB(env0.DATABASE_URL,env0.HYPERDRIVE);box.db=env._db}const DB=env._db;
  if(!path.startsWith("/api/"))return env0.ASSETS.fetch(req);
  let body={},raw="";if((m==="POST"||m==="PUT")&&!path.includes("/oauth/")){raw=await req.text();if(path!=="/api/stripe/webhook"){try{body=raw?JSON.parse(raw):{}}catch{return err("Bad JSON")}}}
  try{
  if(path==="/api/health")return J({ok:true,mail:!!env.RESEND_API_KEY||env.DEV_MODE==="1",providers:providers(env)});
  if(path==="/api/auth/request"&&m==="POST"){
    const email=String(body.email||"").trim().toLowerCase(); if(!okEmail(email))return err("Enter a valid email");
    const prev=await DB.prepare("SELECT sent FROM codes WHERE email=?").bind(email).first();
    if(prev&&now()-prev.sent<45000)return err("Please wait a moment before requesting another code",429);
    const code=String(100000+(crypto.getRandomValues(new Uint32Array(1))[0]%900000));
    await DB.prepare("INSERT INTO codes(email,hash,exp,tries,sent) VALUES(?,?,?,?,?) ON CONFLICT(email) DO UPDATE SET hash=EXCLUDED.hash,exp=EXCLUDED.exp,tries=EXCLUDED.tries,sent=EXCLUDED.sent").bind(email,await sha(email+code),now()+10*60000,0,now()).run();
    const E=EM[L(body.lang)];const sent=await mail(env,email,E.code,`<div style="font-family:system-ui;max-width:420px;margin:auto"><h2>${E.codeH} <b style="letter-spacing:4px">${code}</b></h2><p>${E.codeP}</p></div>`);
    if(!sent&&env.DEV_MODE==="1")return J({ok:true,dev_code:code});
    if(!sent)return err("Email service is not configured yet",503);
    return J({ok:true});
  }
  if(path==="/api/auth/verify"&&m==="POST"){
    const email=String(body.email||"").trim().toLowerCase(),code=String(body.code||"");
    const r=await DB.prepare("SELECT hash,exp,tries FROM codes WHERE email=?").bind(email).first();
    if(!r||r.exp<now()||r.tries>=5)return err("Code expired. Request a new one.");
    if(r.hash!==await sha(email+code)){await DB.prepare("UPDATE codes SET tries=tries+1 WHERE email=?").bind(email).run();return err("That code is not right")}
    await DB.prepare("DELETE FROM codes WHERE email=?").bind(email).run();
    await DB.prepare("INSERT INTO users(email,created) VALUES(?,?) ON CONFLICT DO NOTHING").bind(email,now()).run();
    const token=rnd(32);await DB.prepare("INSERT INTO sessions(hash,email,exp) VALUES(?,?,?)").bind(await sha(token),email,now()+30*864e5).run();
    return J({token,email});
  }
  let om;if((om=path.match(/^\/api\/auth\/oauth\/(google|facebook|apple)\/(start|callback)$/))){
    const prov=om[1],cfg=OAUTH[prov],redirect=u.origin+"/api/auth/oauth/"+prov+"/callback";
    if(!providers(env)[prov])return err("This sign-in is not enabled yet",503);
    if(om[2]==="start"){
      const state=rnd(16);await DB.prepare("INSERT INTO oauth_states(state,prov,next,exp) VALUES(?,?,?,?)").bind(state,prov,(u.searchParams.get("next")||"account").replace(/[^\w/?=&-]/g,"").slice(0,60),now()+10*60000).run();
      const q=new URLSearchParams({client_id:cfg.id(env),redirect_uri:redirect,response_type:"code",scope:cfg.scope,state,...cfg.extra});
      return Response.redirect(cfg.auth+"?"+q,302);
    }
    let code,state;
    if(m==="POST"){const f=await req.formData();code=f.get("code");state=f.get("state")}else{code=u.searchParams.get("code");state=u.searchParams.get("state")}
    const st=await DB.prepare("SELECT next,exp FROM oauth_states WHERE state=? AND prov=?").bind(state||"",prov).first();
    await DB.prepare("DELETE FROM oauth_states WHERE state=?").bind(state||"").run();
    if(!st||st.exp<now()||!code)return Response.redirect(u.origin+"/#/login?err="+encodeURIComponent("Sign-in was cancelled or expired"),302);
    try{const email=await oauthEmail(prov,code,redirect,env);const token=await startSession(env,email);
      return Response.redirect(u.origin+"/#/auth?token="+token+"&email="+encodeURIComponent(email.toLowerCase())+"&next="+st.next,302)}
    catch(e){return Response.redirect(u.origin+"/#/login?err="+encodeURIComponent(e.message),302)}
  }
  if(path==="/api/subscribe"&&m==="POST"){const e=String(body.email||"").trim().toLowerCase();if(!okEmail(e))return err("Enter a valid email");
    const lg=L(body.lang);const ex=await DB.prepare("SELECT email,unsub FROM subs WHERE email=?").bind(e).first();
    await DB.prepare("INSERT INTO subs(email,created,lang,unsub) VALUES(?,?,?,NULL) ON CONFLICT(email) DO UPDATE SET unsub=NULL,lang=EXCLUDED.lang").bind(e,now(),lg).run();
    if(!ex||ex.unsub){const k=(await sha(e+(env.ADMIN_TOKEN||"")+"unsub")).slice(0,24);const W={en:["Welcome to the pack!","You're on the AlphaDog Styles list. We'll email you first when new breeds, colors and drops arrive - no spam, ever.","Unsubscribe"],es:["¡Bienvenido a la manada!","Ya estás en la lista de AlphaDog Styles. Te avisaremos primero de nuevas razas, colores y lanzamientos - nunca spam.","Darse de baja"],pt:["Bem-vindo à matilha!","Você está na lista da AlphaDog Styles. Avisaremos primeiro sobre novas raças, cores e lançamentos - nunca spam.","Cancelar inscrição"]}[lg]||[];
      try{await mail(env,e,W[0],`<div style="font-family:system-ui;max-width:480px;margin:auto"><h2>${W[0]}</h2><p>${W[1]}</p><p><a href="${env.SITE_URL}/#/shop">alphadogstyles.com</a></p><p style="font-size:12px;color:#888"><a href="${env.SITE_URL}/api/unsubscribe?e=${encodeURIComponent(e)}&k=${k}">${W[2]}</a></p></div>`)}catch(x){}}
    return J({ok:true})}
  if(path==="/api/unsubscribe"&&m==="GET"){const e=String(u.searchParams.get("e")||"").toLowerCase();const k=(await sha(e+(env.ADMIN_TOKEN||"")+"unsub")).slice(0,24);
    if(u.searchParams.get("k")!==k)return new Response("Invalid link",{status:400});await DB.prepare("UPDATE subs SET unsub=? WHERE email=?").bind(now(),e).run();
    return new Response("<h2 style='font-family:system-ui'>You're unsubscribed. Sorry to see you go!</h2>",{headers:{"content-type":"text/html"}})}
  /* ----- custom design requests ----- */
  if(path==="/api/custom"&&m==="POST"){
    const e=String(body.email||"").trim().toLowerCase(); if(!okEmail(e))return err("Enter a valid email");
    const ph=Array.isArray(body.photos)?body.photos:[];
    if(ph.length<5)return err("Please add at least 5 photos of your dog");
    if(ph.length>12)return err("Please send 12 photos or fewer");
    for(const x of ph){if(!/^image\/(jpeg|png|webp)$/.test(x.mime||"")||typeof x.b64!=="string"||x.b64.length>2800000)return err("One of the photos could not be used. Please use JPG or PNG photos.")}
    const clean=v=>String(v||"").slice(0,1500);
    const dog=body.dog||{}, data={dog:{name:clean(dog.name),breed:clean(dog.breed),colors:clean(dog.colors),markings:clean(dog.markings),ears:clean(dog.ears),tail:clean(dog.tail),details:clean(dog.details)},
      style:{theme:clean(body.style?.theme),style:clean(body.style?.style)},products:(Array.isArray(body.products)?body.products:[]).filter(x=>cat.products.some(p=>p.id===x)),qty:clean(body.qty),notes:clean(body.notes)};
    if(!data.products.length)return err("Choose at least one product");
    const id="CU-"+rnd(3).toUpperCase(), tok=rnd(12), lang=L(body.lang);
    await DB.prepare("INSERT INTO custom_requests(id,token,email,name,lang,data,status,created,updated) VALUES(?,?,?,?,?,?,?,?,?)").bind(id,tok,e,clean(body.name),lang,JSON.stringify(data),"new",now(),now()).run();
    let i=0;for(const x of ph){await DB.prepare("INSERT INTO custom_photos(req_id,idx,mime,b64,created) VALUES(?,?,?,?,?)").bind(id,i++,x.mime,x.b64,now()).run()}
    const link=(env.SITE_URL||u.origin)+"/#/custom/"+id+"?k="+tok, CE=CUSTOM_EM[lang];
    await mail(env,e,CE.gotS(id),`<p>${CE.gotP(esc(data.dog.name||""))}</p><p><a href="${link}">${CE.view}</a></p>`,"customization@alphadogstyles.com",CUSTOM_FROM);
    const cto=env.FORWARD_CUSTOM||env.OWNER_EMAIL;if(cto)await mail(env,cto,`New custom design request ${id}`,`<p><b>${esc(e)}</b> asked for a custom design (${ph.length} photos).</p><pre style="white-space:pre-wrap">${esc(JSON.stringify(data,null,1))}</pre>`,e,CUSTOM_FROM);
    return J({id,k:tok});
  }
  let cm;
  if((cm=path.match(/^\/api\/custom\/(CU-[\w]+)$/))&&m==="GET"){
    const r=await DB.prepare("SELECT id,status,quote,note,data,created FROM custom_requests WHERE id=? AND token=?").bind(cm[1],u.searchParams.get("k")||"").first();
    if(!r)return err("Not found",404);
    const art=(await DB.prepare("SELECT part FROM custom_art WHERE req_id=?").bind(cm[1]).all()).results.map(x=>x.part);
    const d=JSON.parse(r.data);const paidBefore=await DB.prepare("SELECT 1 FROM orders WHERE data LIKE ? AND status IN ('paid','in_production','shipped') LIMIT 1").bind('%"custom":"'+r.id+'"%').first();return J({id:r.id,status:r.status,quote:r.quote,fee_due:paidBefore?0:(r.quote||0),note:r.note,products:d.products,style:d.style,dog:{name:d.dog.name},art,created:r.created});
  }
  if((cm=path.match(/^\/api\/custom\/(CU-[\w]+)\/art\/(head|body)$/))&&m==="GET"){
    const r=await DB.prepare("SELECT 1 FROM custom_requests WHERE id=? AND token=?").bind(cm[1],u.searchParams.get("k")||"").first();if(!r)return err("Not found",404);
    const a=await DB.prepare("SELECT mime,body FROM custom_art WHERE req_id=? AND part=?").bind(cm[1],cm[2]).first();if(!a)return err("Not found",404);
    return new Response(a.mime==="image/svg+xml"?a.body:Uint8Array.from(atob(a.body),c=>c.charCodeAt(0)),{headers:{"content-type":a.mime,"cache-control":"private, max-age=300"}});
  }
  if(path==="/api/contact"&&m==="POST"){if(!okEmail(body.email)||!body.msg)return err("Email and message required");await DB.prepare("INSERT INTO msgs(email,body,created) VALUES(?,?,?)").bind(body.email,String(body.msg).slice(0,4000),now()).run();if(env.OWNER_EMAIL)await mail(env,env.OWNER_EMAIL,"AlphaDog Styles: new message from "+body.email,`<p><b>${esc(body.email)}</b> wrote:</p><p style="white-space:pre-wrap">${esc(String(body.msg).slice(0,4000))}</p>`,body.email);return J({ok:true})}
  if(path==="/api/orders"&&m==="POST"){
    if((await kvGet(DB,"checkout_paused"))==="1")return err("Checkout is paused for a short while. Please try again soon.",503);
    let cust=null;
    if(body.custom){cust=await DB.prepare("SELECT id,quote,status FROM custom_requests WHERE id=? AND token=?").bind(String(body.custom.id||""),String(body.custom.k||"")).first();
      if(!cust||!["quoted","approved"].includes(cust.status))return err("This custom design is not ready to order yet")}
    const items=(Array.isArray(body.items)?body.items:[]).map(it=>validItem(it,cust&&cust.id));
    if(cust){const parts=(await DB.prepare("SELECT part FROM custom_art WHERE req_id=?").bind(cust.id).all()).results.map(x=>x.part);if(items.some(i=>i&&[i.front,i.back].some(d=>d&&d.custom&&!parts.includes(d.part))))return err("Your cart has an invalid item")}
    if(!items.length||items.length>30||items.includes(null))return err("Your cart has an invalid item");
    const s=body.ship||{};for(const k of["name","a1","city","st","zip"])if(!s[k]||String(s[k]).length>120)return err("Please complete the shipping address");
    if(!/^\d{5}(-\d{4})?$/.test(s.zip))return err("Enter a valid US ZIP code"); if(!okEmail(body.email))return err("Enter a valid email");
    const sub=items.reduce((a,i)=>a+priceCents(cat,i.prod,(i.front?1:0)+(i.back?1:0),i.size)*i.qty,0);
    let fee=cust?(cust.quote||0):0;
    if(cust&&fee){const prev=await DB.prepare("SELECT 1 FROM orders WHERE data LIKE ? AND status IN ('paid','in_production','shipped') LIMIT 1").bind('%"custom":"'+cust.id+'"%').first();if(prev)fee=0}
    const ship=sub>=cat.shipping.free_over?0:cat.shipping.flat, total=sub+ship+fee;
    const id="AD-"+rnd(4).toUpperCase(), email=String(body.email).toLowerCase();
    const data={lang:L(body.lang),items,ship:{name:s.name,a1:s.a1,a2:s.a2||"",city:s.city,st:s.st,zip:s.zip,phone:s.phone||""},subtotal:sub,shipping:ship,design_fee:fee,custom:cust?cust.id:null};
    await DB.prepare("INSERT INTO orders(id,email,data,total,status,created,updated) VALUES(?,?,?,?,?,?,?)").bind(id,email,JSON.stringify(data),total,"reserved",now(),now()).run();
    if(env.STRIPE_SECRET_KEY){
      try{
        const li={};items.forEach((i,n)=>{li[n]={quantity:i.qty,price_data:{currency:"usd",unit_amount:priceCents(cat,i.prod,(i.front?1:0)+(i.back?1:0),i.size),product_data:{name:"AlphaDog "+(cat.products.find(x=>x.id===i.prod)||{name:i.prod}).name+" - "+i.color+" / "+i.size}}}});
        if(ship)li[items.length]={quantity:1,price_data:{currency:"usd",unit_amount:ship,product_data:{name:"Shipping (US)"}}};
        if(fee)li[items.length+1]={quantity:1,price_data:{currency:"usd",unit_amount:fee,product_data:{name:"Custom dog design (one-time)"}}};
        const ss=await stripe(env,"POST","/checkout/sessions",{mode:"payment",customer_email:email,client_reference_id:id,locale:{es:"es",pt:"pt-BR",en:"en"}[data.lang],metadata:{order_id:id},line_items:li,
          success_url:u.origin+"/#/done/"+id+"?paid=1",cancel_url:u.origin+"/#/cart"});
        await DB.prepare("UPDATE orders SET status='awaiting_payment',printify_id=NULL,tracking=NULL,data=? WHERE id=?").bind(JSON.stringify({...data,session:ss.id}),id).run();
        return J({id,total,url:ss.url});
      }catch(e){return err("Payment could not start: "+e.message,502)}
    }
    {const E=EM[data.lang];await mail(env,email,E.resS(id),`<p>${E.resP(id,(total/100).toFixed(2))}</p>`)}
    return J({id,total});
  }
  if(path==="/api/orders/confirm"&&m==="POST"&&env.STRIPE_SECRET_KEY){
    const o=await DB.prepare("SELECT data,status FROM orders WHERE id=?").bind(String(body.id||"")).first();if(!o)return err("Order not found",404);
    if(o.status!=="awaiting_payment")return J({status:o.status});
    const sid=JSON.parse(o.data).session;if(!sid)return J({status:o.status});
    const ss=await stripe(env,"GET","/checkout/sessions/"+sid);
    if(ss.payment_status==="paid"&&ss.client_reference_id===body.id){await markPaid(DB,env,body.id,ss.livemode);return J({status:ss.livemode?"paid":"paid_test"})}
    return J({status:o.status});
  }
  if(path==="/api/stripe/webhook"&&m==="POST"){
    if(!env.STRIPE_WEBHOOK_SECRET)return err("not configured",503);
    if(!(await stripeVerify(raw,req.headers.get("stripe-signature"),env.STRIPE_WEBHOOK_SECRET)))return err("bad signature",400);
    const ev=JSON.parse(raw);
    if(ev.type==="checkout.session.completed"||ev.type==="checkout.session.async_payment_succeeded"){const ss=ev.data.object;if(ss.payment_status==="paid"&&ss.client_reference_id)await markPaid(DB,env,ss.client_reference_id,ss.livemode)}
    return J({received:true});
  }
  if(path==="/api/orders"&&m==="GET"){const e=await auth(req,env);if(!e)return err("Log in first",401);const r=await DB.prepare("SELECT id,status,total,tracking,created FROM orders WHERE email=? ORDER BY created DESC LIMIT 100").bind(e).all();return J({items:r.results})}
  if(path==="/api/designs"){
    const e=await auth(req,env);if(!e)return err("Log in first",401);
    if(m==="GET"){const r=await DB.prepare("SELECT id,data FROM designs WHERE email=? ORDER BY created DESC LIMIT 200").bind(e).all();return J({items:r.results.map(x=>({id:x.id,s:JSON.parse(x.data)}))})}
    if(m==="POST"){const id=String(body.id||rnd(6));await DB.prepare("INSERT INTO designs(id,email,data,created) VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET data=EXCLUDED.data,created=EXCLUDED.created WHERE designs.email=EXCLUDED.email").bind(id,e,JSON.stringify(body.s||{}).slice(0,6000),now()).run();return J({id})}
  }
  let mm;if((mm=path.match(/^\/api\/designs\/([\w-]+)$/))&&m==="DELETE"){const e=await auth(req,env);if(!e)return err("Log in first",401);await DB.prepare("DELETE FROM designs WHERE id=? AND email=?").bind(mm[1],e).run();return J({ok:true})}
  /* ----- Etsy OAuth (owner connects the shop once): /api/market/etsy/connect?t=ADMIN_TOKEN ----- */
  if(path==="/api/market/etsy/connect"&&m==="GET"){
    const nn=u.searchParams.get("n")||"";const nr=nn?await DB.prepare("SELECT exp FROM oauth_states WHERE state=? AND prov='etsylink'").bind(nn).first():null;
    if(!(env.ADMIN_TOKEN&&u.searchParams.get("t")===env.ADMIN_TOKEN)&&!(nr&&nr.exp>now()))return err("Forbidden",403);
    if(nn)await DB.prepare("DELETE FROM oauth_states WHERE state=?").bind(nn).run();
    if(!env.ETSY_KEYSTRING)return err("ETSY_KEYSTRING missing",500);
    const ver=rnd(32),state=rnd(16),ch=b64u(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(ver)));
    await DB.prepare("INSERT INTO oauth_states(state,prov,next,exp) VALUES(?,?,?,?)").bind(state,"etsy",ver,now()+15*60000).run();
    const q=new URLSearchParams({response_type:"code",client_id:env.ETSY_KEYSTRING,redirect_uri:env.SITE_URL+"/api/market/etsy/callback",scope:"listings_r listings_w listings_d transactions_r transactions_w shops_r shops_w profile_r email_r",state,code_challenge:ch,code_challenge_method:"S256"});
    return Response.redirect("https://www.etsy.com/oauth/connect?"+q,302);
  }
  if(path==="/api/market/etsy/callback"&&m==="GET"){
    const st=await DB.prepare("SELECT next,exp FROM oauth_states WHERE state=? AND prov='etsy'").bind(u.searchParams.get("state")||"").first();
    await DB.prepare("DELETE FROM oauth_states WHERE state=?").bind(u.searchParams.get("state")||"").run();
    if(!st||st.exp<now())return new Response("Link expired - start again.",{status:400});
    const r=await fetch("https://api.etsy.com/v3/public/oauth/token",{method:"POST",headers:{"content-type":"application/x-www-form-urlencoded"},body:new URLSearchParams({grant_type:"authorization_code",client_id:env.ETSY_KEYSTRING,redirect_uri:env.SITE_URL+"/api/market/etsy/callback",code:u.searchParams.get("code")||"",code_verifier:st.next})});
    const j=await r.json().catch(()=>({}));
    if(!j.access_token)return new Response("Etsy did not return a token: "+JSON.stringify(j).slice(0,300),{status:400});
    await kvSet(DB,"etsy_token",{...j,obtained:now()});
    return new Response("<h2 style='font-family:system-ui'>Etsy connected to AlphaDog Styles. You can close this tab.</h2>",{headers:{"content-type":"text/html"}});
  }
  /* ----- internal (GitHub Actions fulfillment + payment hooks) ----- */
  if(path.startsWith("/api/internal/")){
    if(!env.ADMIN_TOKEN||req.headers.get("x-admin-token")!==env.ADMIN_TOKEN)return err("Forbidden",403);
    let km;if((km=path.match(/^\/api\/internal\/kv\/([\w.-]+)$/))){if(m==="GET")return J({v:await kvGet(DB,km[1])});if(m==="POST"){await kvSet(DB,km[1],body.v);return J({ok:true})}}
    if(path==="/api/internal/market/etsy/link"&&m==="POST"){const n=rnd(16);await DB.prepare("INSERT INTO oauth_states(state,prov,next,exp) VALUES(?,?,?,?)").bind(n,"etsylink","",now()+60*60000).run();return J({url:env.SITE_URL+"/api/market/etsy/connect?n="+n})}
    if(path==="/api/internal/market/decode"&&m==="POST")return J({items:(body.skus||[]).map(s=>({sku:s,item:marketItem(s,1)}))});
    if(path==="/api/internal/market/order"&&m==="POST"){
      // body: {plat, ext_id, email, ship:{name,a1,a2,city,st,zip,phone}, items:[{sku,qty,title}], test}
      const plat=String(body.plat||"").replace(/[^a-z]/g,""),ext=String(body.ext_id||"").slice(0,80); if(!plat||!ext)return err("plat/ext_id required");
      const id=("MK-"+plat.slice(0,2)+"-"+ext).toUpperCase().replace(/[^A-Z0-9-]/g,"").slice(0,40);
      const ex=await DB.prepare("SELECT id,status FROM orders WHERE id=?").bind(id).first(); if(ex)return J({ok:true,dup:true,id,status:ex.status});
      const items=[],bad=[];for(const x of body.items||[]){const it=marketItem(x.sku,x.qty||1);if(it)items.push(it);else bad.push(x)}
      const s=body.ship||{}; const shipOk=s.name&&s.a1&&s.city&&s.zip&&(s.st||String(s.country||"US").toUpperCase()!=="US");
      const status=bad.length||!items.length||!shipOk?"needs_attention":(body.test?"paid_test":"paid");
      const data={items,ship:{name:s.name||"",a1:s.a1||"",a2:s.a2||"",city:s.city||"",st:s.st||"",zip:s.zip||"",phone:s.phone||"",country:String(s.country||"US").toUpperCase().slice(0,2)},source:{plat,ext_id:ext,bad,titles:(body.items||[]).map(x=>x.title||"")}};
      await DB.prepare("INSERT INTO orders(id,email,data,total,status,created,updated) VALUES(?,?,?,?,?,?,?)").bind(id,String(body.email||"").toLowerCase(),JSON.stringify(data),parseInt(body.total)||0,status,now(),now()).run();
      const lines=items.map(i=>`${i.qty} x ${i.prod} ${i.color} ${i.size} ${(i.front||i.back||{}).breed||""}`).join("<br>");
      await mail(env,env.OWNER_EMAIL,`${status==="needs_attention"?"ACTION NEEDED: ":""}New ${plat} order ${ext}`,`<p>${plat} order <b>${ext}</b> - status <b>${status}</b>.</p><p>${lines||"(no decodable items)"}</p>${bad.length?`<p>Could not decode: ${bad.map(b=>b.sku||b.title).join(", ")}</p>`:""}${shipOk?"":"<p>Shipping address missing.</p>"}`);
      return J({ok:true,id,status,bad});
    }
    if(path==="/api/internal/custom"&&m==="GET"){const st=u.searchParams.get("status");const r=await DB.prepare("SELECT id,token,email,name,lang,status,quote,note,data,created,updated FROM custom_requests"+(st?" WHERE status=?":"")+" ORDER BY created DESC LIMIT 100").bind(...(st?[st]:[])).all();
      const out=[];for(const x of r.results){const n=await DB.prepare("SELECT count(*)::int AS n FROM custom_photos WHERE req_id=?").bind(x.id).first();const a=(await DB.prepare("SELECT part FROM custom_art WHERE req_id=?").bind(x.id).all()).results.map(y=>y.part);out.push({...x,data:JSON.parse(x.data),photos:n.n,art:a})}return J({items:out})}
    let im;
    if((im=path.match(/^\/api\/internal\/custom\/(CU-[\w]+)\/photo\/(\d+)$/))&&m==="GET"){const p=await DB.prepare("SELECT mime,b64 FROM custom_photos WHERE req_id=? AND idx=?").bind(im[1],+im[2]).first();if(!p)return err("Not found",404);return new Response(Uint8Array.from(atob(p.b64),c=>c.charCodeAt(0)),{headers:{"content-type":p.mime}})}
    if((im=path.match(/^\/api\/internal\/custom\/(CU-[\w]+)\/art\/(head|body)$/))&&m==="GET"){const a=await DB.prepare("SELECT mime,body FROM custom_art WHERE req_id=? AND part=?").bind(im[1],im[2]).first();if(!a)return err("Not found",404);return new Response(a.mime==="image/svg+xml"?a.body:Uint8Array.from(atob(a.body),c=>c.charCodeAt(0)),{headers:{"content-type":a.mime}})}
    if((im=path.match(/^\/api\/internal\/custom\/(CU-[\w]+)$/))&&m==="POST"){
      const r=await DB.prepare("SELECT email,lang,token,status FROM custom_requests WHERE id=?").bind(im[1]).first();if(!r)return err("No such request",404);
      for(const part of ["head","body"]){const a=body.art&&body.art[part];if(a&&a.body&&/^image\/(svg\+xml|png)$/.test(a.mime||"")){if(a.mime==="image/svg+xml"&&!/^\s*(<\?xml[^>]*>\s*)?<svg[\s>]/i.test(a.body))return err("Art must be an SVG or PNG");if(a.body.length>6000000)return err("Art file too large");
        await DB.prepare("INSERT INTO custom_art(req_id,part,mime,body,created) VALUES(?,?,?,?,?) ON CONFLICT(req_id,part) DO UPDATE SET mime=EXCLUDED.mime,body=EXCLUDED.body,created=EXCLUDED.created").bind(im[1],part,a.mime,a.body,now()).run()}}
      const q=body.quote!=null?Math.max(0,Math.min(50000,parseInt(body.quote)||0)):null;
      await DB.prepare("UPDATE custom_requests SET status=COALESCE(?::text,status),quote=COALESCE(?::int,quote),note=COALESCE(?::text,note),updated=? WHERE id=?").bind(body.status||null,q,body.note!=null?String(body.note).slice(0,3000):null,now(),im[1]).run();
      if(body.notify&&(body.status||r.status)==="quoted"){const CE=CUSTOM_EM[L(r.lang)],link=(env.SITE_URL||u.origin)+"/#/custom/"+im[1]+"?k="+r.token;await mail(env,r.email,CE.readyS(im[1]),`<p>${CE.readyP}</p><p><a href="${link}">${CE.view}</a></p>`,"customization@alphadogstyles.com",CUSTOM_FROM)}
      return J({ok:true});
    }
    if(path==="/api/internal/stats"&&m==="GET"){
      const tz=d=>new Date(d).toLocaleDateString("en-CA",{timeZone:"America/Los_Angeles"});
      const rows=(await DB.prepare("SELECT id,email,data,total,status,created FROM orders WHERE created>? AND status NOT IN ('reserved','smoke_test') ORDER BY created DESC LIMIT 3000").bind(now()-90*864e5).all()).results;
      const REAL=["paid","in_production","shipped"],byStatus={},days={},chan={},prod={},breed={},color={};
      {const [y,mo,dd]=tz(now()).split("-").map(Number);for(let i=29;i>=0;i--)days[new Date(Date.UTC(y,mo-1,dd-i,12)).toISOString().slice(0,10)]={rev:0,n:0}}  // calendar walk: immune to DST days having 23/25 hours
      const sum={today:0,d7:0,d30:0,d90:0,n7:0,n30:0,n90:0,nToday:0};let real=0;
      const T=now(),day0=tz(T);
      for(const r of rows){byStatus[r.status]=(byStatus[r.status]||0)+1;if(!REAL.includes(r.status))continue;real++;
        const age=T-r.created,dk=tz(r.created),c=r.id.startsWith("MK-ET")?"etsy":r.id.startsWith("MK-EB")?"ebay":r.id.startsWith("MK-TI")?"tiktok":"store";
        sum.d90+=r.total;sum.n90++;if(age<30*864e5){sum.d30+=r.total;sum.n30++;if(days[dk]){days[dk].rev+=r.total;days[dk].n++}}
        if(age<7*864e5){sum.d7+=r.total;sum.n7++}if(dk===day0){sum.today+=r.total;sum.nToday++}
        chan[c]=chan[c]||{n:0,rev:0};chan[c].n++;chan[c].rev+=r.total;
        let d={};try{d=JSON.parse(r.data)}catch{}
        for(const it of d.items||[]){const q=it.qty||1;prod[it.prod]=(prod[it.prod]||0)+q;const b=(it.front||it.back||{}).breed;if(b)breed[b]=(breed[b]||0)+q;if(it.color)color[it.color]=(color[it.color]||0)+q}}
      const top=o=>Object.entries(o).sort((a,b)=>b[1]-a[1]).slice(0,10).map(([k,v])=>({k,v}));
      const cnt=async q=>(await DB.prepare(q).first()).n;
      const abandoned=await cnt("SELECT count(*)::int AS n FROM orders WHERE status='awaiting_payment' AND created>"+(now()-7*864e5));
      return J({sum,aov:real?Math.round(sum.d90/real):0,byStatus,days:Object.entries(days).map(([d,v])=>({d,...v})),chan,top:{prod:top(prod),breed:top(breed),color:top(color)},
        counts:{users:await cnt("SELECT count(*)::int AS n FROM users"),subs:await cnt("SELECT count(*)::int AS n FROM subs WHERE unsub IS NULL"),custom_open:await cnt("SELECT count(*)::int AS n FROM custom_requests WHERE status IN ('new','in_review')"),support_new:await cnt("SELECT count(*)::int AS n FROM support_inbox WHERE status='new'"),msgs:await cnt("SELECT count(*)::int AS n FROM msgs"),abandoned}});
    }
    if(path==="/api/internal/orders/all"&&m==="GET"){
      const G={real:["paid","in_production","shipped"],test:["paid_test","test_complete","test_failed"],problem:["needs_attention","test_failed"],open:["reserved","awaiting_payment"],done:["shipped"],refunded:["refunded","cancelled"]};
      const g=u.searchParams.get("g"),qq=(u.searchParams.get("q")||"").trim().toLowerCase().slice(0,80),st=u.searchParams.get("status");
      const w=[],bind=[];if(st){w.push("status=?");bind.push(st)}else if(G[g]){w.push("status IN ("+G[g].map(()=>"?").join(",")+")");bind.push(...G[g])}
      if(qq){w.push("(lower(id) LIKE ? OR lower(email) LIKE ?)");bind.push("%"+qq+"%","%"+qq+"%")}
      const r=await DB.prepare("SELECT id,email,data,total,status,printify_id,tracking,created,updated FROM orders"+(w.length?" WHERE "+w.join(" AND "):"")+" ORDER BY created DESC LIMIT 200").bind(...bind).all();
      return J({items:r.results.map(x=>({...x,data:JSON.parse(x.data)}))});
    }
    if(path==="/api/internal/customers"&&m==="GET"){const r=await DB.prepare("SELECT u.email,u.created,(SELECT count(*)::int FROM orders o WHERE o.email=u.email AND o.status IN ('paid','in_production','shipped')) AS orders,(SELECT COALESCE(sum(o.total),0)::int FROM orders o WHERE o.email=u.email AND o.status IN ('paid','in_production','shipped')) AS spent,(SELECT count(*)::int FROM designs d WHERE d.email=u.email) AS designs FROM users u ORDER BY u.created DESC LIMIT 500").all();return J({items:r.results})}
    if(path==="/api/internal/subscribers"&&m==="GET"){const r=await DB.prepare("SELECT email,created,lang,unsub FROM subs ORDER BY created DESC LIMIT 5000").all();return J({items:r.results})}
    if(path==="/api/internal/messages"&&m==="GET"){const r=await DB.prepare("SELECT id,email,body,created FROM msgs ORDER BY created DESC LIMIT 100").all();return J({items:r.results})}
    if(path==="/api/internal/health"&&m==="GET"){
      const cnt=async q=>(await DB.prepare(q).first()).n,T=now();let db=true;try{await cnt("SELECT 1::int AS n")}catch{db=false}
      const key=env.STRIPE_SECRET_KEY||"",fl=await kvGet(DB,"fulfil_last").catch(()=>null);
      const issues={paid_stuck:await cnt("SELECT count(*)::int AS n FROM orders WHERE status='paid' AND updated<"+(T-30*60000)),needs_attention:await cnt("SELECT count(*)::int AS n FROM orders WHERE status='needs_attention'"),
        in_production_old:await cnt("SELECT count(*)::int AS n FROM orders WHERE status='in_production' AND updated<"+(T-14*864e5)),unpaid_old:await cnt("SELECT count(*)::int AS n FROM orders WHERE status='awaiting_payment' AND created<"+(T-2*3600000)+" AND created>"+(T-7*864e5)),test_failed:await cnt("SELECT count(*)::int AS n FROM orders WHERE status='test_failed'")};
      return J({db,mail:!!env.RESEND_API_KEY,providers:providers(env),stripe:key?(/^(sk|rk)_live/.test(key)?"live":"test"):"off",webhook:!!env.STRIPE_WEBHOOK_SECRET,owner_email:!!env.OWNER_EMAIL,
        fulfil_last:fl,fulfil_age_min:fl?Math.round((T-fl)/60000):null,checkout_paused:(await kvGet(DB,"checkout_paused"))==="1",fulfil_paused:(await kvGet(DB,"fulfil_paused"))==="1",issues,server_time:T});
    }
    if(path==="/api/internal/send"&&m==="POST"){if(!okEmail(body.to)||!body.subject||!body.html)return err("to, subject, html required");
      const from=body.mailbox==="custom"?CUSTOM_FROM:SUPPORT_FROM,rt=body.mailbox==="custom"?"customization@alphadogstyles.com":"support@alphadogstyles.com";
      const ok=await mail(env,body.to,String(body.subject).slice(0,200),String(body.html).slice(0,20000),rt,from);return J({ok})}
    if(path==="/api/internal/support"&&m==="GET"){const st=u.searchParams.get("status")||"new";const r=await DB.prepare("SELECT id,mailbox,from_addr,subject,body,status,created,reply FROM support_inbox WHERE status=? ORDER BY created LIMIT 50").bind(st).all();return J({items:r.results})}
    if((im=path.match(/^\/api\/internal\/support\/(\d+)$/))&&m==="POST"){await DB.prepare("UPDATE support_inbox SET status=COALESCE(?::text,status),reply=COALESCE(?::text,reply),handled=? WHERE id=?").bind(body.status||null,body.reply||null,now(),+im[1]).run();return J({ok:true})}
    if(path==="/api/internal/support"&&m==="POST"){await DB.prepare("INSERT INTO support_inbox(mailbox,from_addr,subject,body,raw_size,created) VALUES(?,?,?,?,?,?)").bind(String(body.mailbox||"support"),String(body.from||""),String(body.subject||"").slice(0,300),String(body.body||"").slice(0,20000),0,now()).run();return J({ok:true})}
    if(path==="/api/internal/inbox"&&m==="GET"){const g=async q=>(await DB.prepare(q).all()).results;return J({messages:await g("SELECT email,body,created FROM msgs ORDER BY created DESC LIMIT 50"),subscribers:await g("SELECT email,created FROM subs ORDER BY created DESC LIMIT 200"),orders:await g("SELECT id,email,status,total,created FROM orders WHERE status NOT IN ('awaiting_payment','smoke_test') ORDER BY created DESC LIMIT 50")})}
    if(path==="/api/internal/dbcheck"&&m==="GET"){try{return J(await diag(env0.DATABASE_URL,env0.HYPERDRIVE))}catch(e){return J({error:String(e.message)},500)}}
    if(path==="/api/internal/orders"&&m==="GET"&&u.searchParams.get("email")){const r=await DB.prepare("SELECT id,email,data,total,status,printify_id,tracking,created FROM orders WHERE email=? ORDER BY created DESC LIMIT 20").bind(u.searchParams.get("email").toLowerCase()).all();return J({items:r.results.map(x=>({...x,data:JSON.parse(x.data)}))})}
    if(path==="/api/internal/orders"&&m==="GET"){const st=u.searchParams.get("status")||"paid";const r=await DB.prepare("SELECT id,email,data,total,status,printify_id FROM orders WHERE status=? ORDER BY created LIMIT 50").bind(st).all();return J({items:r.results.map(x=>({...x,data:JSON.parse(x.data)}))})}
    if((mm=path.match(/^\/api\/internal\/orders\/([\w-]+)$/))&&m==="POST"){
      const o=await DB.prepare("SELECT email FROM orders WHERE id=?").bind(mm[1]).first();if(!o)return err("No such order",404);
      if(body.action){
        const full=await DB.prepare("SELECT email,total,status,data FROM orders WHERE id=?").bind(mm[1]).first(),od=JSON.parse(full.data||"{}"),E=EM[L(od.lang)];
        if(body.action==="resend"){if(!["paid","paid_test","in_production","shipped","test_complete"].includes(full.status))return err("Order is not paid");await mail(env,full.email,E.paidS(mm[1]),`<p>${E.paidP(mm[1],(full.total/100).toFixed(2))}</p>`);return J({ok:true})}
        if(body.action==="requeue"){const to=full.status==="test_failed"?"paid_test":"paid";if(!["needs_attention","test_failed"].includes(full.status))return err("Only problem orders can be retried");await DB.prepare("UPDATE orders SET status=?,updated=? WHERE id=?").bind(to,now(),mm[1]).run();return J({ok:true,status:to})}
        if(body.action==="cancel"){if(/^MK-/.test(mm[1]))return err("Marketplace orders are never cancelled from here (it would not cancel on the marketplace and could hurt your seller standing). Handle it in the marketplace.");if(!["needs_attention","reserved","awaiting_payment","paid"].includes(full.status))return err("Too late to cancel here (already in production or finished)");await DB.prepare("UPDATE orders SET status='cancelled',updated=? WHERE id=?").bind(now(),mm[1]).run();return J({ok:true,status:"cancelled"})}
        if(body.action==="note"){const n=String(body.note||"").trim().slice(0,1000);if(!n)return err("Note is empty");od.notes=[...(od.notes||[]),{t:now(),n}].slice(-30);await DB.prepare("UPDATE orders SET data=?,updated=? WHERE id=?").bind(JSON.stringify(od),now(),mm[1]).run();return J({ok:true,notes:od.notes})}
        if(body.action==="refund"){
          if(!["paid","paid_test","in_production","shipped","test_complete","needs_attention"].includes(full.status))return err("Order is not refundable");
          if(!od.session)return err("No card payment on this order (marketplace orders are refunded on the marketplace)");
          try{const ss=await stripe(env,"GET","/checkout/sessions/"+od.session);if(!ss.payment_intent)return err("Stripe has no payment for this order");
            const amt=body.amount!=null?Math.max(1,Math.min(full.total,parseInt(body.amount)||0)):null;
            const rf=await stripe(env,"POST","/refunds",{payment_intent:ss.payment_intent,...(amt?{amount:amt}:{})});
            const partial=amt&&amt<full.total;if(!partial)await DB.prepare("UPDATE orders SET status='refunded',updated=? WHERE id=?").bind(now(),mm[1]).run();
            od.refunds=[...(od.refunds||[]),{t:now(),id:rf.id,amount:rf.amount}];await DB.prepare("UPDATE orders SET data=?,updated=? WHERE id=?").bind(JSON.stringify(od),now(),mm[1]).run();
            const R={en:["refunded","We refunded","to your original payment method. It can take 5-10 business days to appear."],es:["reembolsado","Reembolsamos","a tu método de pago original. Puede tardar 5-10 días hábiles en aparecer."],pt:["reembolsado","Reembolsamos","para o seu meio de pagamento original. Pode levar 5-10 dias úteis para aparecer."]}[L(od.lang)];
            await mail(env,full.email,`Order ${mm[1]} ${R[0]}`,`<p>${R[1]} $${(rf.amount/100).toFixed(2)} ${R[2]}</p>`);
            return J({ok:true,refund:rf.id,amount:rf.amount,status:partial?full.status:"refunded"});
          }catch(e){return err("Refund failed: "+e.message,502)}
        }
        return err("Unknown action");
      }
      await DB.prepare("UPDATE orders SET status=COALESCE(?::text,status),printify_id=COALESCE(?::text,printify_id),tracking=COALESCE(?::text,tracking),updated=? WHERE id=?").bind(body.status||null,body.printify_id||null,body.tracking||null,now(),mm[1]).run();
      if(body.status==="shipped"){const od=await DB.prepare("SELECT data FROM orders WHERE id=?").bind(mm[1]).first();const E=EM[L(od&&JSON.parse(od.data).lang)];await mail(env,o.email,E.shipS(mm[1]),`<p>${E.shipP}</p>${body.tracking?`<p><a href="${body.tracking}">${E.track}</a></p>`:""}`)}
      return J({ok:true});
    }
  }
  return err("Not found",404);
  }catch(e){return err("Server error: "+e.message,500)}
 }
};
