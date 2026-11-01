import {fit} from "./placement.js";
let CAL=null;
export const setCal=c=>{CAL=c};
export function isDark(hex){const n=parseInt(hex.slice(1),16);return (0.299*(n>>16)+0.587*((n>>8)&255)+0.114*(n&255))<110}
const aspects={};
export function aspect(url){return aspects[url]?Promise.resolve(aspects[url]):new Promise(res=>{const i=new Image();i.onload=()=>{aspects[url]=i.naturalWidth/i.naturalHeight||1;res(aspects[url])};i.onerror=()=>res(1);i.src=url})}
export function artUrl(d){return d.custom?`api/custom/${d.custom}/art/${d.part}?k=${encodeURIComponent(d.k||"")}`:`art/${d.theme}_${d.style}/${d.breed}_${d.part==="head"?"front":"back"}.svg`}
export const photoUrl=(prod,slug,side)=>`img/${prod}_${slug}_${side}.webp`;
// d = {part,size,breed,theme,style} or null ; color = [name,hex,ok,slug]
export async function renderSVG(prod,side,color,d){
  const slug=color[3]||"white",P=CAL.photo;let art="";
  if(d){
    const url=artUrl(d),a=await aspect(url),f=fit(prod,side,d.size,a),[ax,ay,aw,ah]=CAL[prod][side];
    const w=f.scale*aw,h=w/a,cx=ax+f.x*aw,cy=ay+f.y*ah;
    art=`<image href="${url}" x="${(cx-w/2).toFixed(1)}" y="${(cy-h/2).toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" style="mix-blend-mode:multiply;opacity:.93" preserveAspectRatio="xMidYMid meet"/>`;
  }
  return `<svg viewBox="0 0 ${P} ${P}" xmlns="http://www.w3.org/2000/svg" role="img"><image href="${photoUrl(prod,slug,side)}" width="${P}" height="${P}"/>${art}</svg>`;
}
