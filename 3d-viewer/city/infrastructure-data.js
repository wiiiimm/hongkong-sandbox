import {modelSurfaceCollision} from './model-collision.js';
import {validateProxyClips} from './infrastructure-replacements.js';
export const isOfficialInfrastructure=data=>['official-infrastructure','tai-o-official-infrastructure'].includes(data?.kind);

// Source coordinates are already city metres / HKPD. Never terrain-lift these meshes.
export function prepareInfrastructure(data){
 if(data?.schemaVersion!==1||!isOfficialInfrastructure(data)||data.crs!=='EPSG:2326'||data.verticalDatum!=='Hong Kong Principal Datum'||!Array.isArray(data.models)||!data.models.length)throw new Error('Invalid source infrastructure inventory');
 const clips=validateProxyClips(data.proxyClips),buildingUids=new Set();
 const seen=new Set();const models=data.models.map(input=>{
  const m=input.modelGeometry,b=input.worldBounds,p=m?.position;
  if(typeof input.id!=='string'||!input.id||seen.has(input.id)||typeof input.sourceUrl!=='string'||!/^https?:\/\//.test(input.sourceUrl)||!Array.isArray(p)||!p.length||p.length%9||!p.every(Number.isFinite)||!Array.isArray(m.normal)||m.normal.length!==p.length||!m.normal.every(Number.isFinite)||!Array.isArray(m.colour)||m.colour.length!==p.length||!m.colour.every(Number.isFinite)||!Array.isArray(b)||b.length!==2||!b.every(v=>Array.isArray(v)&&v.length===3&&v.every(Number.isFinite))||b[0].some((v,i)=>v>b[1][i]))throw new Error('Invalid source infrastructure '+input.id);
  for(let i=0;i<p.length;i++)if(p[i]<b[0][i%3]-.001||p[i]>b[1][i%3]+.001)throw new Error('Source infrastructure bounds mismatch '+input.id);
  let hasSurface=false;
  for(let i=0;i<p.length&&!hasSurface;i+=9){
   const ax=p[i+3]-p[i],ay=p[i+4]-p[i+1],az=p[i+5]-p[i+2],bx=p[i+6]-p[i],by=p[i+7]-p[i+1],bz=p[i+8]-p[i+2];
   hasSurface=Math.hypot(ay*bz-az*by,az*bx-ax*bz,ax*by-ay*bx)>1e-10;
  }
  if(!hasSurface)throw new Error('Empty source infrastructure surface '+input.id);
  const walk=input.walkTriangleIndices||[];
  if(typeof input.walkable!=='boolean'||!Array.isArray(walk)||new Set(walk).size!==walk.length||walk.some(t=>!Number.isInteger(t)||t<0||t>=p.length/9)||input.walkable&&(!walk.length||typeof input.publicAccessSource!=='string'||!/^https?:\/\//.test(input.publicAccessSource)))throw new Error('Invalid public deck source '+input.id);
  for(const t of walk){
   const i=t*9,ab=[p[i+3]-p[i],p[i+4]-p[i+1],p[i+5]-p[i+2]],ac=[p[i+6]-p[i],p[i+7]-p[i+1],p[i+8]-p[i+2]];
   const nx=ab[1]*ac[2]-ab[2]*ac[1],ny=ab[2]*ac[0]-ab[0]*ac[2],nz=ab[0]*ac[1]-ab[1]*ac[0];
   if(!(ny/Math.hypot(nx,ny,nz)>.6))throw new Error('Invalid source deck top face '+input.id);
  }
  if(!Array.isArray(input.suppresses)||input.suppresses.some(id=>typeof id!=='string'||!id))throw new Error('Invalid infrastructure replacements '+input.id);
  const uids=input.suppressesBuildingUids||[];
  if(!Array.isArray(uids)||new Set(uids).size!==uids.length||uids.some(uid=>typeof uid!=='string'||!/^landsd\/\d+:\d+$/.test(uid)||buildingUids.has(uid)))throw new Error('Invalid infrastructure building replacements '+input.id);
  for(const uid of uids){
   const match=Array.isArray(input.buildingMatches)&&input.buildingMatches.find(m=>m.uid===uid);
   if(!match||String(match.objectId)!==uid.split('/')[1].split(':')[0]||typeof match.buildingCSUID!=='string'||!match.buildingCSUID||typeof match.policy!=='string'||!match.policy)throw new Error('Missing source building match '+uid);
   buildingUids.add(uid);
  }
  seen.add(input.id);
  const centre=b[0].map((v,i)=>(v+b[1][i])/2);
  return {...input,source:input.sourceUrl,bounds:[b[0][0],b[0][2],b[1][0],b[1][2]],base:b[0][1],height:b[1][1]-b[0][1],length:Math.hypot(b[1][0]-b[0][0],b[1][2]-b[0][2]),focus:centre,estimatedElevation:false};
 });
 if(clips.some(c=>models.some(m=>m.suppresses.includes(c.id))))throw new Error('Conflicting full and partial infrastructure replacement');
 const approaches=data.approaches||[];if(!Array.isArray(approaches))throw new Error('Invalid public approach inventory');
 for(const r of approaches){
  if(!r||typeof r.id!=='string'||!r.id||seen.has(r.id)||typeof r.source!=='string'||!/^https?:\/\//.test(r.source)||r.walkable!==true||r.estimatedPublicApproach!==true||r.estimatedElevation!==true||typeof r.publicAccessSource!=='string'||!/^https?:\/\//.test(r.publicAccessSource)||typeof r.elevationBasis!=='string'||!r.elevationBasis||typeof r.widthBasis!=='string'||!r.widthBasis||!Number.isFinite(r.width)||r.width<=0||!Array.isArray(r.deckPath)||r.deckPath.length<2||!r.deckPath.every(p=>Array.isArray(p)&&p.length===3&&p.every(Number.isFinite))||!Array.isArray(r.bounds)||r.bounds.length!==4||!r.bounds.every(Number.isFinite))throw new Error('Invalid estimated public approach '+r?.id);
  if(r.bounds[0]>r.bounds[2]||r.bounds[1]>r.bounds[3]||r.deckPath.some(p=>p[0]<r.bounds[0]||p[0]>r.bounds[2]||p[2]<r.bounds[1]||p[2]>r.bounds[3]))throw new Error('Invalid public approach bounds '+r.id);
  seen.add(r.id);const length=r.deckPath.slice(1).reduce((sum,p,i)=>sum+Math.hypot(p[0]-r.deckPath[i][0],p[2]-r.deckPath[i][2]),0);models.push({...r,length,base:Math.min(...r.deckPath.map(p=>p[1]))-.24,height:Math.max(...r.deckPath.map(p=>p[1]))-Math.min(...r.deckPath.map(p=>p[1]))+.24,focus:r.deckPath[Math.floor(r.deckPath.length/2)]});
 }
 // Declared source counts guard against a parseable but incomplete download,
 // particularly when one deck half carries suppression for a complete bridge.
 const source=models.filter(m=>m.modelGeometry),triangles=source.reduce((sum,m)=>sum+m.modelGeometry.position.length/9,0),walkable=source.filter(m=>m.walkable).length;
 const counts={models:source.length,sourceTriangles:triangles,triangles,publicWalkModels:walkable,walkableModels:walkable,publicWalkTriangles:source.filter(m=>m.walkable).reduce((sum,m)=>sum+(m.walkTriangleIndices?.length||0),0),estimatedPublicApproaches:approaches.length,matchedBuildingExtrusions:buildingUids.size,genericBridgeProxiesReplaced:new Set(source.flatMap(m=>m.suppresses)).size,genericBridgeProxiesPartlyReplaced:clips.length};
 for(const [key,count] of Object.entries(counts))if(data.counts?.[key]!==undefined&&data.counts[key]!==count)throw new Error('Incomplete source infrastructure count '+key);
 return models;
}
// The same selected source triangles supply visible floors and walking heights.
function heightAt(p,t,x,z){
 const i=t*9,ax=p[i],az=p[i+2],bx=p[i+3],bz=p[i+5],cx=p[i+6],cz=p[i+8];
 const determinant=(bz-cz)*(ax-cx)+(cx-bx)*(az-cz);if(Math.abs(determinant)<1e-8)return null;
 const a=((bz-cz)*(x-cx)+(cx-bx)*(z-cz))/determinant,b=((cz-az)*(x-cx)+(ax-cx)*(z-cz))/determinant,c=1-a-b;
 // City coordinates upload as Float32: tolerate at most2mm at a rendered edge,
 // rather than losing support at nominal OSM endpoints after sub-mm rounding.
 const twiceArea=Math.abs(determinant),slack=.002;
 const covered=a*twiceArea>=-slack*Math.hypot(bx-cx,bz-cz)&&b*twiceArea>=-slack*Math.hypot(ax-cx,az-cz)&&c*twiceArea>=-slack*Math.hypot(ax-bx,az-bz);
 return covered?a*p[i+1]+b*p[i+4]+c*p[i+7]:null;
}
export class InfrastructureSurfaces {
 constructor(){this.models=new Map();}
 add(record){this.models.set(record.id,record);}
 clear(){this.models.clear();}
 candidates(x,z,r=0){return [...this.models.values()].filter(m=>x+r>=m.bounds[0]&&x-r<=m.bounds[2]&&z+r>=m.bounds[1]&&z-r<=m.bounds[3]);}
 heights(x,z){
  const result=[];for(const model of this.candidates(x,z))if(model.walkable===true){
   for(const t of model.walkTriangleIndices){const y=heightAt(model.modelGeometry.position,t,x,z);if(y!==null&&!result.some(value=>Math.abs(value-y)<.001))result.push(y);}
  }return result;
 }
 collision(x,z,bottom,top,radius=.5){for(const record of this.candidates(x,z,radius))if(modelSurfaceCollision(record.modelGeometry,x,z,bottom,top,radius))return record;return null;}
 maximumRoof(x,z,radius=20){return this.candidates(x,z,radius).reduce((height,m)=>Math.max(height,m.base+m.height),0);}
}
