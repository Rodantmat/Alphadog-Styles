// AlphaDog Styles store backend. Secrets (set with wrangler secret put): ADMIN_TOKEN, RESEND_API_KEY (optional), STRIPE_* (later).
import {priceCents} from "../js/placement.js";
import {makeDB,diag} from "./db.js";
import cat from "../data/catalog.json";
const esc=x=>String(x).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const J=(o,s=200,h={})=>new Response(JSON.stringify(o),{status:s,headers:{"content-type":"application/json","cache-control":"no-store",...h}});
const err=(m,s=400)=>J({error:m},s);
const now=()=>Date.now();
const hex=b=>[...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join("");
const sha=async s=>hex(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(s)));
const rnd=n=>hex(crypto.getRandomValues(new Uint8Array(n)));
const okEmail=e=>typeof e==="string"&&e.length<255&&/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e);
async function mail(env,to,subject,html,replyTo){
  if(env.RESEND_API_KEY){
    const body={from:env.MAIL_FROM,to:[to],subject,html};const rt=replyTo||env.OWNER_EMAIL;if(rt)body.reply_to=rt;
    const r=await fetch("https://api.resend.com/emails",{method:"POST",headers:{authorization:"Bearer "+env.RESEND_API_KEY,"content-type":"application/json"},body:JSON.stringify(body)});
    return r.ok;
  }
  return false;
}
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
function validItem(it){
  const p=cat.products.find(x=>x.id===it.prod); if(!p)return null;
  const c=p.colors.find(x=>x[0]===it.color&&x[2]); if(!c||!p.sizes.includes(it.size))return null;
  const qty=Math.max(1,Math.min(20,parseInt(it.qty)||1));
  const side=(d,k)=>{ if(!d)return null; if(!(p.sides||["front","back"]).includes(k))return false; const al=p.opts&&p.opts[k]; const o=cat[k+"_opts"].find(x=>x.part===d.part&&x.size===d.size&&(!al||al.includes(x.id))); if(!o||!cat.breeds.some(b=>b.slug===d.breed)||!cat.themes.some(t=>t.id===d.theme)||!cat.styles.some(s=>s.id===d.style))return false; return {part:d.part,size:d.size,breed:d.breed,theme:d.theme,style:d.style}};
  const front=side(it.front,"front"),back=side(it.back,"back"); if(front===false||back===false||(!front&&!back))return null;
  return {prod:it.prod,color:it.color,size:it.size,qty,front,back};
}
export default {
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
  if(path==="/api/subscribe"&&m==="POST"){const e=String(body.email||"").toLowerCase();if(!okEmail(e))return err("Enter a valid email");await DB.prepare("INSERT INTO subs(email,created) VALUES(?,?) ON CONFLICT DO NOTHING").bind(e,now()).run();return J({ok:true})}
  if(path==="/api/contact"&&m==="POST"){if(!okEmail(body.email)||!body.msg)return err("Email and message required");await DB.prepare("INSERT INTO msgs(email,body,created) VALUES(?,?,?)").bind(body.email,String(body.msg).slice(0,4000),now()).run();if(env.OWNER_EMAIL)await mail(env,env.OWNER_EMAIL,"AlphaDog Styles: new message from "+body.email,`<p><b>${esc(body.email)}</b> wrote:</p><p style="white-space:pre-wrap">${esc(String(body.msg).slice(0,4000))}</p>`,body.email);return J({ok:true})}
  if(path==="/api/orders"&&m==="POST"){
    const items=(Array.isArray(body.items)?body.items:[]).map(validItem);
    if(!items.length||items.length>30||items.includes(null))return err("Your cart has an invalid item");
    const s=body.ship||{};for(const k of["name","a1","city","st","zip"])if(!s[k]||String(s[k]).length>120)return err("Please complete the shipping address");
    if(!/^\d{5}(-\d{4})?$/.test(s.zip))return err("Enter a valid US ZIP code"); if(!okEmail(body.email))return err("Enter a valid email");
    const sub=items.reduce((a,i)=>a+priceCents(cat,i.prod,(i.front?1:0)+(i.back?1:0),i.size)*i.qty,0);
    const ship=sub>=cat.shipping.free_over?0:cat.shipping.flat, total=sub+ship;
    const id="AD-"+rnd(4).toUpperCase(), email=String(body.email).toLowerCase();
    const data={lang:L(body.lang),items,ship:{name:s.name,a1:s.a1,a2:s.a2||"",city:s.city,st:s.st,zip:s.zip,phone:s.phone||""},subtotal:sub,shipping:ship};
    await DB.prepare("INSERT INTO orders(id,email,data,total,status,created,updated) VALUES(?,?,?,?,?,?,?)").bind(id,email,JSON.stringify(data),total,"reserved",now(),now()).run();
    if(env.STRIPE_SECRET_KEY){
      try{
        const li={};items.forEach((i,n)=>{li[n]={quantity:i.qty,price_data:{currency:"usd",unit_amount:priceCents(cat,i.prod,(i.front?1:0)+(i.back?1:0),i.size),product_data:{name:"AlphaDog "+(cat.products.find(x=>x.id===i.prod)||{name:i.prod}).name+" - "+i.color+" / "+i.size}}}});
        if(ship)li[items.length]={quantity:1,price_data:{currency:"usd",unit_amount:ship,product_data:{name:"Shipping (US)"}}};
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
  /* ----- internal (GitHub Actions fulfillment + payment hooks) ----- */
  if(path.startsWith("/api/internal/")){
    if(!env.ADMIN_TOKEN||req.headers.get("x-admin-token")!==env.ADMIN_TOKEN)return err("Forbidden",403);
    if(path==="/api/internal/inbox"&&m==="GET"){const g=async q=>(await DB.prepare(q).all()).results;return J({messages:await g("SELECT email,body,created FROM msgs ORDER BY created DESC LIMIT 50"),subscribers:await g("SELECT email,created FROM subs ORDER BY created DESC LIMIT 200"),orders:await g("SELECT id,email,status,total,created FROM orders WHERE status NOT IN ('awaiting_payment','smoke_test') ORDER BY created DESC LIMIT 50")})}
    if(path==="/api/internal/dbcheck"&&m==="GET"){try{return J(await diag(env0.DATABASE_URL,env0.HYPERDRIVE))}catch(e){return J({error:String(e.message)},500)}}
    if(path==="/api/internal/orders"&&m==="GET"){const st=u.searchParams.get("status")||"paid";const r=await DB.prepare("SELECT id,email,data,total,status,printify_id FROM orders WHERE status=? ORDER BY created LIMIT 50").bind(st).all();return J({items:r.results.map(x=>({...x,data:JSON.parse(x.data)}))})}
    if((mm=path.match(/^\/api\/internal\/orders\/([\w-]+)$/))&&m==="POST"){
      const o=await DB.prepare("SELECT email FROM orders WHERE id=?").bind(mm[1]).first();if(!o)return err("No such order",404);
      await DB.prepare("UPDATE orders SET status=COALESCE(?::text,status),printify_id=COALESCE(?::text,printify_id),tracking=COALESCE(?::text,tracking),updated=? WHERE id=?").bind(body.status||null,body.printify_id||null,body.tracking||null,now(),mm[1]).run();
      if(body.status==="shipped"){const od=await DB.prepare("SELECT data FROM orders WHERE id=?").bind(mm[1]).first();const E=EM[L(od&&JSON.parse(od.data).lang)];await mail(env,o.email,E.shipS(mm[1]),`<p>${E.shipP}</p>${body.tracking?`<p><a href="${body.tracking}">${E.track}</a></p>`:""}`)}
      return J({ok:true});
    }
  }
  return err("Not found",404);
  }catch(e){return err("Server error: "+e.message,500)}
 }
};
