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
