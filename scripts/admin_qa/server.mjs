// Local, fully isolated test rig: the REAL store worker (bundled) + a throwaway Postgres + a MOCK Stripe + a MOCK email service.
// Nothing here can touch production, Stripe, Printify or a real customer.
import http from "node:http";import fs from "node:fs";import path from "node:path";
const bundle=process.argv[2],ROOT=path.resolve(process.argv[3]||"store"),PORT=8787,MOCK=9100;
const mod=(await import(path.resolve(bundle))).default;
const mails=[],stripeCalls=[],sessions={};let n=0;
// ---- mock Stripe + mock Resend + inspection endpoints
http.createServer(async(req,res)=>{
  let b="";for await(const c of req)b+=c;const u=new URL(req.url,"http://x"),j=o=>{res.setHeader("content-type","application/json");res.end(JSON.stringify(o))};
  if(u.pathname==="/emails"){mails.push(JSON.parse(b));return j({id:"m"+mails.length})}
  if(u.pathname==="/__mails")return j(mails);
  if(u.pathname==="/__stripe")return j(stripeCalls);
  if(u.pathname==="/__reset"){mails.length=0;stripeCalls.length=0;return j({ok:1})}
  if(u.pathname.startsWith("/v1/")){const f=new URLSearchParams(b);stripeCalls.push({m:req.method,p:u.pathname,body:Object.fromEntries(f)});
    if(u.pathname==="/v1/checkout/sessions"&&req.method==="POST"){const id="cs_mock_"+(++n);let tot=0;for(const [k,v] of f){const m=k.match(/^line_items\[(\d+)\]\[price_data\]\[unit_amount\]$/);if(m)tot+=(+v)*(+f.get(`line_items[${m[1]}][quantity]`)||1)}sessions[id]={total:tot,id,client_reference_id:f.get("client_reference_id"),payment_status:"unpaid",livemode:true,payment_intent:"pi_mock_"+n};return j({id,url:`http://localhost:${MOCK}/pay/${id}`})}
    let m;if((m=u.pathname.match(/^\/v1\/checkout\/sessions\/(\w+)$/))){const s=sessions[m[1]];if(!s){res.statusCode=404;return j({error:{message:"no such session"}})}return j({...s,payment_status:s.paid?"paid":"unpaid"})}
    if(u.pathname==="/v1/refunds"){if(process.env.FAIL_REFUND){res.statusCode=402;return j({error:{message:"mock refund denied"}})}return j({id:"re_mock_"+stripeCalls.length,amount:f.get("amount")?+f.get("amount"):(Object.values(sessions).find(x=>x.payment_intent===f.get("payment_intent"))||{}).total||0})}
    res.statusCode=404;return j({error:{message:"unmocked"}})}
  if(u.pathname.startsWith("/pay/")){const s=sessions[u.pathname.slice(5)];if(s)s.paid=true;res.end("paid")}
  res.statusCode=404;res.end();
}).listen(MOCK);
// ---- the store itself
const env={DATABASE_URL:process.env.DATABASE_URL,ADMIN_TOKEN:"test-admin-token",STRIPE_SECRET_KEY:"rk_live_mock",STRIPE_BASE:`http://localhost:${MOCK}/v1`,STRIPE_WEBHOOK_SECRET:"whsec_mock",MAIL_BASE:`http://localhost:${MOCK}`,RESEND_API_KEY:"re_mock",
  MAIL_FROM:"AlphaDog Styles <orders@alphadogstyles.com>",SITE_URL:`http://localhost:${PORT}`,OWNER_EMAIL:"owner@example.com",
  ASSETS:{async fetch(req){const u=new URL(req.url);let f=path.join(ROOT,decodeURIComponent(u.pathname));if(!f.startsWith(ROOT)||!fs.existsSync(f)||fs.statSync(f).isDirectory())f=path.join(ROOT,"index.html");
    const ext=path.extname(f),ct={".js":"text/javascript",".css":"text/css",".html":"text/html",".json":"application/json",".svg":"image/svg+xml",".png":"image/png",".jpg":"image/jpeg",".webp":"image/webp"}[ext]||"application/octet-stream";return new Response(fs.readFileSync(f),{headers:{"content-type":ct}})}}};
http.createServer(async(req,res)=>{
  let b=[];for await(const c of req)b.push(c);const body=Buffer.concat(b);
  const r=new Request(`http://localhost:${PORT}${req.url}`,{method:req.method,headers:req.headers,body:["GET","HEAD"].includes(req.method)?undefined:body});
  const w=[];try{const o=await mod.fetch(r,env,{waitUntil:p=>w.push(p)});res.statusCode=o.status;o.headers.forEach((v,k)=>res.setHeader(k,v));res.end(Buffer.from(await o.arrayBuffer()));await Promise.allSettled(w)}catch(e){console.error("WORKER CRASH",req.url,e);res.statusCode=500;res.end(String(e))}
}).listen(PORT,()=>console.log("rig ready on",PORT));
