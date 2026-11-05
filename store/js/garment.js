import {fit} from "./placement.js";
let CAL=null;
export const setCal=c=>{CAL=c};
export function isDark(hex){const n=parseInt(hex.slice(1),16);return (0.299*(n>>16)+0.587*((n>>8)&255)+0.114*(n&255))<110}
const aspects={};
export function aspect(url){return aspects[url]?Promise.resolve(aspects[url]):new Promise(res=>{const i=new Image();i.onload=()=>{aspects[url]=i.naturalWidth/i.naturalHeight||1;res(aspects[url])};i.onerror=()=>res(1);i.src=url})}
export function artUrl(d,dark){return d.custom?`api/custom/${d.custom}/art/${d.part}?k=${encodeURIComponent(d.k||"")}`:`art${dark?"_w":""}/${d.theme}_${d.style}/${d.breed}_${d.part==="head"?"front":"back"}.svg`}
const inkCache={};
/* recolour a single-colour SVG (fill) and hand it back as a data URI */
async function inkUrl(url,ink){const k=url+"|"+ink;if(inkCache[k])return inkCache[k];const txt=await (await fetch(url)).text();const svg=txt.replace(/fill="[^"]*"/g,`fill="${ink}"`);return inkCache[k]="data:image/svg+xml;charset=utf-8,"+encodeURIComponent(svg)}
export const photoUrl=(prod,slug,side)=>`img/${prod}_${slug}_${side}.webp`;
// d = {part,size,breed,theme,style} or null ; color = [name,hex,ok,slug]
export async function renderSVG(prod,side,color,d){
  const slug=color[3]||"white",P=CAL.photo;let art="";
  if(d){
    const dark=isDark(color[1]),src=artUrl(d,dark),a=await aspect(src),f=fit(prod,side,d.size,a),[ax,ay,aw,ah]=CAL[prod][side];
    const w=f.scale*aw,h=w/a,cx=ax+f.x*aw,cy=ay+f.y*ah;
    let url=src,flt="";const ink=d.ink||(dark?"#ffffff":"");
    if(d.custom){if(dark)flt="filter:invert(1);"}else if(ink&&ink.toLowerCase()!==(dark?"#ffffff":"#000000")){try{url=await inkUrl(src,ink)}catch(e){}}
    art=`<image href="${url}" x="${(cx-w/2).toFixed(1)}" y="${(cy-h/2).toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" style="${dark?"":"mix-blend-mode:multiply;"}${flt}opacity:${dark?".97":".93"}" preserveAspectRatio="xMidYMid meet"/>`;
  }
  return `<svg viewBox="0 0 ${P} ${P}" xmlns="http://www.w3.org/2000/svg" role="img"><image href="${photoUrl(prod,slug,side)}" width="${P}" height="${P}"/>${art}</svg>`;
}
