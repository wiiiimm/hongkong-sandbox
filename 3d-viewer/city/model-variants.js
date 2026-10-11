import {sha256Hex} from './sha256.js';
export const MODEL_QUALITY_LEVELS=Object.freeze(['base','lightweight','balanced','high','original']);
export const MODEL_QUALITY_LABELS=Object.freeze(['Base only','Lightweight','Balanced','High','Original']);
const HASH=/^[a-f0-9]{64}$/;
const GATES=['sourceIdentity','geometry','placement','visual','collision','devicePerformance'];
const canonical=value=>value&&typeof value==='object'?Array.isArray(value)?value.map(canonical):Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])])):value;
export async function sourceMetadataHash(entry,catalogue){
 const value={entry,rootTranslation:catalogue.rootTranslation,crs:catalogue.crs,verticalDatum:catalogue.verticalDatum,coordinatePolicy:catalogue.coordinatePolicy??null,datasetId:catalogue.datasetId??null};
 return sha256Hex(new TextEncoder().encode(JSON.stringify(canonical(value))));
}
/** Invalid optional variants never invalidate the original enhanced catalogue. */
export async function attachModelVariants(entries,catalogue,url){
 if(!Array.isArray(catalogue.optimisedVariants)||catalogue.optimisedVariants.length>8192)return entries;
 const byUid=new Map();for(const variant of catalogue.optimisedVariants){if(!variant||typeof variant.uid!=='string')continue;const list=byUid.get(variant.uid)||[];list.push(variant);byUid.set(variant.uid,list);}
 return Promise.all(entries.map(async(source,i)=>{
  const candidates=byUid.get(source.uid);if(!candidates)return source;
  const binding=await sourceMetadataHash(catalogue.models[i],catalogue),variants=[],seen=new Set();
  for(const v of candidates){
   if(v.runtimeVersion!==1||v.status!=='approved'||v.sourceSha256!==source.sha256||v.sourceMetadataSha256!==binding||![v.variantId,v.revisionId,v.recipeSha256,v.sha256].every(s=>typeof s==='string'&&HASH.test(s))||seen.has(v.variantId)||!MODEL_QUALITY_LEVELS.slice(1).includes(v.tier)||typeof v.lossy!=='boolean'||!['none','meshopt','draco'].includes(v.codec)||!['source-equivalent','validated-variant'].includes(v.collisionPolicy)||v.approval?.artifactSha256!==v.sha256||!GATES.every(g=>v.approval?.gates?.[g]==='passed'))continue;
   if(![v.bytes,v.glbBytes,v.decodedGeometryBytes,v.triangles,v.indexedVertices].every(n=>Number.isSafeInteger(n)&&n>0)||v.bytes>32*1024*1024||v.glbBytes>128*1024*1024||v.encoding!=='gzip'||typeof v.asset!=='string'||!v.asset.endsWith('.glb.gz')||!Number.isFinite(v.minPixels)||v.minPixels<0||!Number.isFinite(v.maxPixels)||v.maxPixels<=v.minPixels)continue;
   const bounds=v.worldBounds;
   if(!Array.isArray(bounds)||bounds.length!==2||!bounds.every(p=>Array.isArray(p)&&p.length===3&&p.every(Number.isFinite))||bounds[0].some((n,j)=>n>=bounds[1][j])||!Number.isFinite(v.maxPositionErrorMetres)||v.maxPositionErrorMetres<0||bounds.flat().some((n,j)=>Math.abs(n-source.worldBounds.flat()[j])>v.maxPositionErrorMetres+.002))continue;
   if(v.tier==='original'&&(v.lossy!==false||v.maxPositionErrorMetres!==0||v.collisionPolicy!=='source-equivalent'||v.triangles!==source.triangles))continue;
   let assetURL;try{assetURL=new URL(v.asset,url);if(assetURL.origin!==new URL(url).origin||!['http:','https:'].includes(assetURL.protocol)||assetURL.username||assetURL.password)continue;}catch{continue;}
   assetURL.searchParams.set('v',v.sha256);seen.add(v.variantId);
   variants.push({...source,asset:v.asset,assetURL:assetURL.href,sha256:v.sha256,bytes:v.bytes,glbBytes:v.glbBytes,decodedGeometryBytes:v.decodedGeometryBytes,triangles:v.triangles,indexedVertices:v.indexedVertices,worldBounds:bounds,
    variantId:v.variantId,revisionId:v.revisionId,recipeSha256:v.recipeSha256,sourceSha256:source.sha256,sourceMetadataSha256:binding,codec:v.codec,tier:v.tier,minPixels:v.minPixels,maxPixels:v.maxPixels,collisionPolicy:v.collisionPolicy});
  }
  return {...source,variants};
 }));
}
export function selectModelVariant(source,{quality='auto',profile='mobile',pixels=Infinity,current=null}={}){
 if(quality==='base')return null;
 const tier=quality==='auto'?(profile==='mobile'?'balanced':'high'):quality,maximum=MODEL_QUALITY_LEVELS.indexOf(tier);
 if(maximum<1)throw new Error('Unknown model quality');
 const allowed=v=>MODEL_QUALITY_LEVELS.indexOf(v.tier)<=maximum;
 const variants=(source.variants||[]).filter(v=>allowed(v)&&pixels>=v.minPixels&&pixels<=v.maxPixels).sort((a,b)=>MODEL_QUALITY_LEVELS.indexOf(b.tier)-MODEL_QUALITY_LEVELS.indexOf(a.tier)||a.bytes-b.bytes||a.variantId.localeCompare(b.variantId));
 // Retain a resident tier around thresholds, without exceeding its reviewed range.
 if(current?.variantId&&allowed(current)&&pixels>=current.minPixels&&pixels<=current.maxPixels){
  const next=variants[0];if(!next||next.variantId===current.variantId||pixels<next.minPixels*1.15)return current;
 }
 return variants[0]||source;
}
