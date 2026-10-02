/** Conservative vertical support diagnostics. No geometry edits or acceptance credit. */
export function lowRimSamples({position,index},bottom,{band=.35,spacing=1}={}){
 if(!Number.isFinite(bottom)||!(band>=0)||!(spacing>0))throw new Error('Invalid rim sampling parameters');
 const unique=new Map(),add=p=>unique.set(p.map(n=>n.toFixed(5)).join(','),p);
 for(let i=0;i<position.length;i+=3)if(position[i+1]<=bottom+band)add(Array.from(position.slice(i,i+3)));
 for(let i=0;i<index.length;i+=3){const v=[0,1,2].map(k=>Array.from(position.slice(index[i+k]*3,index[i+k]*3+3)));
  for(let edge=0;edge<3;edge++){const a=v[edge],b=v[(edge+1)%3];if(Math.max(a[1],b[1])>bottom+band)continue;
   const steps=Math.ceil(Math.hypot(a[0]-b[0],a[2]-b[2])/spacing);for(let j=1;j<steps;j++)add(a.map((n,k)=>n+(b[k]-n)*j/steps));}
 }
 return [...unique.values()];
}
export function supportSurface({position,index},{cell=16}={}){
 if(!(cell>0))throw new Error('Invalid support grid size');
 const grid=new Map(),large=[];let triangles=0;
 for(let i=0;i<index.length;i+=3){const [a,b,c]=[0,1,2].map(k=>Array.from(position.slice(index[i+k]*3,index[i+k]*3+3)));
  const det=(b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0]);if(Math.abs(det)<1e-10)continue;
  const t={a,b,c,det},x0=Math.floor(Math.min(a[0],b[0],c[0])/cell),x1=Math.floor(Math.max(a[0],b[0],c[0])/cell),z0=Math.floor(Math.min(a[2],b[2],c[2])/cell),z1=Math.floor(Math.max(a[2],b[2],c[2])/cell);triangles++;
  if((x1-x0+1)*(z1-z0+1)>4096){large.push(t);continue;}
  for(let x=x0;x<=x1;x++)for(let z=z0;z<=z1;z++){const key=x+','+z;if(!grid.has(key))grid.set(key,[]);grid.get(key).push(t);}
 }
 return {triangles,height(x,z){let highest=null;for(const {a,b,c,det} of [...(grid.get(Math.floor(x/cell)+','+Math.floor(z/cell))||[]),...large]){
   const px=x-a[0],pz=z-a[2],u=(px*(c[2]-a[2])-pz*(c[0]-a[0]))/det,v=((b[0]-a[0])*pz-(b[2]-a[2])*px)/det;
   if(u>=-1e-7&&v>=-1e-7&&u+v<=1+1e-7){const y=a[1]+u*(b[1]-a[1])+v*(c[1]-a[1]);highest=highest===null?y:Math.max(highest,y);}
  }return highest;}};
}
export function measureSupport(rim,surface,{minimumGap=-.1,maximumGap=1}={}){
 if(!Number.isFinite(minimumGap)||!Number.isFinite(maximumGap)||minimumGap>maximumGap)throw new Error('Invalid contact interval');
 let missing=0,contacts=0,minGap=null,maxGap=null;const failed=[];
 for(const position of rim){const y=surface.height(position[0],position[2]);if(y===null){missing++;failed.push({position,reason:'no-vertical-support'});continue;}
  const gap=position[1]-y;minGap=minGap===null?gap:Math.min(minGap,gap);maxGap=maxGap===null?gap:Math.max(maxGap,gap);
  if(gap>=minimumGap&&gap<=maximumGap)contacts++;else failed.push({position,gap,reason:gap<minimumGap?'support-above-rim':'rim-above-support'});
 }
 return {samples:rim.length,contacts,missing,minGap,maxGap,minimumGap,maximumGap,allSampledContactsPass:rim.length>0&&contacts===rim.length,failed};
}
