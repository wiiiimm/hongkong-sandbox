// Drape short road triangles to the same final terrain sampled by walking.
// Refine source detail at 1 m or finer; retain the existing road budget elsewhere.
// Bridge decks bypass draping because their elevation is intentional.
export function drapeRoadTriangle(vertices, sampler, emit, depth=0) {
 const mid=(a,b)=>a.map((v,i)=>(v+b[i])/2);
 const [a,b,c]=vertices,ab=mid(a,b),bc=mid(b,c),ca=mid(c,a);
 const centre=a.map((v,i)=>(v+b[i]+c[i])/3);
 const probes=[ab,bc,ca,centre];

 const span=Math.max(...[[a,b],[b,c],[c,a]].map(([p,q])=>Math.hypot(p[0]-q[0],p[2]-q[2])));
 const resolution=Math.min(...probes.map(p=>sampler.resolutionAt?.(p[0],p[2])??70));
 if(resolution>1.01){emit(vertices);return;}
 const error=Math.max(...probes.map(p=>Math.abs(sampler.height(p[0],p[2])+.18-p[1])));
 if(depth<6&&(error>.08||span>resolution)) {
  for(const p of[ab,bc,ca])p[1]=sampler.height(p[0],p[2])+.18;
  for(const triangle of[[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]])drapeRoadTriangle(triangle,sampler,emit,depth+1);
 }else emit(vertices);
}
