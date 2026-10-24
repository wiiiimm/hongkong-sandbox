/** Display camera only. Full indexed source coordinates remain unchanged. */
export function fitIndexedSourceBox(points,{fov,aspect,direction,margin=[.74,.70],near=.5}){
 if(!points.length||!points.every(p=>p.length===3&&p.every(Number.isFinite))||!(fov>0&&fov<180&&aspect>0&&near>0)||!direction?.every(Number.isFinite)||direction.length!==3||!margin.every(m=>m>0&&m<1))throw new Error('Invalid display framing input');
 const lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];for(const p of points)for(let j=0;j<3;j++){lo[j]=Math.min(lo[j],p[j]);hi[j]=Math.max(hi[j],p[j]);}
 const norm=a=>{const n=Math.hypot(...a);if(!n)throw new Error('Degenerate display direction');return a.map(v=>v/n);},dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
 const back=norm(direction),right=norm(cross([0,1,0],back)),up=norm(cross(back,right)),target=lo.map((v,i)=>(v+hi[i])/2),corners=[];
 for(let mask=0;mask<8;mask++)corners.push(lo.map((v,i)=>(mask&(1<<i))?hi[i]:v));
 const ty=Math.tan(fov*Math.PI/360),tx=ty*aspect;let distance=near;
 for(const c of corners){const p=c.map((v,i)=>v-target[i]),b=dot(p,back);distance=Math.max(distance,b+Math.abs(dot(p,right))/(tx*margin[0]),b+Math.abs(dot(p,up))/(ty*margin[1]),b+near);}
 // Camera-only overscan ensures strict projected bounds; no geometry epsilon.
 distance=distance*1.08+near;const camera=target.map((v,i)=>v+back[i]*distance),projected=corners.map(c=>{const p=c.map((v,i)=>v-target[i]),depth=distance-dot(p,back);return[dot(p,right)/(depth*tx),dot(p,up)/(depth*ty),depth];});
 if(!projected.every(p=>Math.abs(p[0])<margin[0]&&Math.abs(p[1])<margin[1]&&p[2]>near))throw new Error('Display framing failed');
 return{camera,target,indexedSourceBounds:[lo,hi],boundsCorners:corners,projectedCornerCoordinates:projected,projectionDerivedDistance:distance,margin,fov,aspect,cameraOnly:true,noSourceRescaleOrRecast:true};
}
