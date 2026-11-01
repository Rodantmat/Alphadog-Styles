// Thin D1-style wrapper over node-postgres so the store code stays simple. DATABASE_URL = your DigitalOcean Postgres connection string.
import pg from "pg";
pg.types.setTypeParser(20,v=>parseInt(v,10)); // BIGINT -> number
export function makeDB(url){
  if(!url) throw new Error("DATABASE_URL is not set");
  let client=null,ready=null;
  const get=()=>ready||(ready=(async()=>{client=new pg.Client({connectionString:url,ssl:/sslmode=disable/.test(url)?false:{rejectUnauthorized:false}});await client.connect();return client})());
  const q=async(text,params)=>{const c=await get();let i=0;const r=await c.query(text.replace(/\?/g,()=>"$"+(++i)),params);return r};
  const db={prepare(text){let b=[];const o={bind(...a){b=a;return o},async first(){return (await q(text,b)).rows[0]||null},async run(){const r=await q(text,b);return {meta:{changes:r.rowCount}}},async all(){return {results:(await q(text,b)).rows}}};return o},
    async close(){if(client){await client.end()}}};
  return db;
}
// Diagnostics for the admin-only /api/internal/dbcheck endpoint: tries several connection styles and reports what works (never returns secrets).
export async function diag(url){
  const u=new URL(url.replace(/^postgres(ql)?:/,"http:")),out=[];
  const base=`postgres://${encodeURIComponent(decodeURIComponent(u.username))}:${encodeURIComponent(decodeURIComponent(u.password))}@${u.hostname}:${u.port}${u.pathname}`;
  const variants={asIs:{connectionString:url,ssl:{rejectUnauthorized:false}},noSslParam:{connectionString:base,ssl:{rejectUnauthorized:false}},sslTrue:{connectionString:base,ssl:true},poolPort:{connectionString:base.replace(":"+u.port+"/",":25061/"),ssl:{rejectUnauthorized:false}}};
  for(const [name,cfg] of Object.entries(variants)){
    const c=new pg.Client({...cfg,connectionTimeoutMillis:8000});const t=Date.now();
    try{await c.connect();const r=await c.query("select current_database() d, version() v");out.push({name,ok:true,ms:Date.now()-t,db:r.rows[0].d,v:r.rows[0].v.slice(0,30)});await c.end()}
    catch(e){out.push({name,ok:false,ms:Date.now()-t,err:String(e.message).slice(0,200),code:e.code||null});try{await c.end()}catch{}}
  }
  return {host:u.hostname,port:u.port,db:u.pathname,out};
}
