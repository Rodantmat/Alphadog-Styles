// Shared by storefront preview, Worker order builder and (mirrored in Python) the fulfilment script.
// Printify fit rules: x,y = centre, scale = art width as a fraction of the print-area width.
export const AREAS={tee:{front:[2767,3362],back:[2767,3362]},hoodie:{front:[3531,2352],back:[3852,3210]}};
export const RULES={tee:"tee",hoodie:"hoodie"};
export const HOODBACK=0.77;
// products from catalog.json can add their own print areas + rule ("tee" | "hoodie" | "chest" | "cap")
export function registerProducts(products){for(const p of products||[]){if(p.area)AREAS[p.id]=p.area;if(p.rule)RULES[p.id]=p.rule}}
export function fit(prod,side,size,a){
  const [W,H]=AREAS[prod][side], rule=RULES[prod]||"tee";
  let w,h,x=0.5,y=0.5;
  if(rule==="chest"||rule==="cap"){ // small fixed area (polo chest, cap front): fill it, centred
    const k=rule==="cap"?0.92:0.9; w=Math.min(k,k*H*a/W); h=w*W/a/H;
  } else if(side==="back"){
    if(size==="s"){ w=Math.min(0.32*3185/W,0.30*H*a/W); h=w*W/a/H; y=0.04+h/2; }
    else if(rule==="hoodie"){ w=Math.min(0.97,HOODBACK*H*a/W); h=w*W/a/H; y=1-h/2-0.005; }
    else { w=Math.min(0.97,0.97*H*a/W); h=w*W/a/H; y=0.5; }
  } else if(size==="s"){
    const k=rule==="hoodie"?0.26:0.30;
    w=Math.min(k*3185/W,0.30*H*a/W); h=w*W/a/H; x=0.76; y=rule==="hoodie"?0.05+h/2:0.17;
  } else {
    w=Math.min(rule==="hoodie"?0.58:0.75,0.95*H*a/W); h=w*W/a/H; y=Math.min(0.5,0.04+h/2);
  }
  return {x:+x.toFixed(3),y:+y.toFixed(3),scale:+w.toFixed(3),h:+h.toFixed(3)};
}
export function priceCents(cat,prodId,sides,size){
  const p=cat.products.find(q=>q.id===prodId);
  return (sides>=2&&p.price.both?p.price.both:p.price.one)+(p.sur[size]||0);
}
