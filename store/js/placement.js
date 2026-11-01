// Shared by storefront preview and Worker order builder. Mirrors the Printify fit rules used for the marketplace listings.
export const AREAS={tee:{front:[2767,3362],back:[2767,3362]},hoodie:{front:[3531,2352],back:[3852,3210]}};
export const HOODBACK=0.77;
// aspect a = art width/height; returns {x,y,scale} as Printify fractions (x,y = centre, scale = width fraction of print area)
export function fit(prod,side,size,a){
  const [W,H]=AREAS[prod][side];
  let w,h,x=0.5,y=0.5;
  if(side==="back"){
    if(size==="s"){ w=Math.min(0.32*3185/W,0.30*H*a/W); h=w*W/a/H; y=0.04+h/2; }
    else if(prod==="hoodie"){ w=Math.min(0.97,HOODBACK*H*a/W); h=w*W/a/H; y=1-h/2-0.005; }
    else { w=Math.min(0.97,0.97*H*a/W); h=w*W/a/H; y=0.5; }
  } else if(size==="s"){
    const k=prod==="tee"?0.30:0.26;
    w=Math.min(k*3185/W,0.30*H*a/W); h=w*W/a/H; x=0.76; y=prod==="tee"?0.17:0.05+h/2;
  } else {
    w=Math.min(prod==="tee"?0.75:0.58,0.95*H*a/W); h=w*W/a/H; y=Math.min(0.5,0.04+h/2);
  }
  return {x:+x.toFixed(3),y:+y.toFixed(3),scale:+w.toFixed(3),h:+h.toFixed(3)};
}
export function priceCents(cat,prodId,sides,size){
  const p=cat.products.find(q=>q.id===prodId);
  return (sides>=2?p.price.both:p.price.one)+(p.sur[size]||0);
}
