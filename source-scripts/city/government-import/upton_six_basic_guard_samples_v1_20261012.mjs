/** Diagnostic exact existing sample order and binary64 subtraction boundary; no terrain. */
import assert from 'node:assert/strict';
import {inPolygon} from '../../../3d-viewer/city/geo.js';
const SIGN=1n<<63n,MASK=(1n<<64n)-1n,buffer=new ArrayBuffer(8),view=new DataView(buffer);
export function bits(value){assert(Number.isFinite(value));view.setFloat64(0,value,false);return view.getBigUint64(0,false).toString(16).padStart(16,'0');}
function key(value){view.setFloat64(0,value,false);const b=view.getBigUint64(0,false);return b&SIGN?(~b)&MASK:b^SIGN;}
function fromKey(k){const b=k&SIGN?k^SIGN:(~k)&MASK;view.setBigUint64(0,b,false);return view.getFloat64(0,false);}
export function gapBoundary(base,maxOldGap){
 assert(Number.isFinite(base)&&Number.isFinite(maxOldGap));const limit=Math.max(1,maxOldGap)+.25;assert(Number.isFinite(limit));
 const accepts=h=>base-h<=limit;let lo=key(-Number.MAX_VALUE),hi=key(Number.MAX_VALUE);assert(!accepts(fromKey(lo))&&accepts(fromKey(hi)));
 while(lo<hi){const mid=(lo+hi)>>1n;if(accepts(fromKey(mid)))hi=mid;else lo=mid+1n;}
 const minimum=fromKey(lo),previous=fromKey(lo-1n);assert(Number.isFinite(minimum)&&Number.isFinite(previous)&&accepts(minimum)&&!accepts(previous));
 return {base,maxOldGap,existingGapLimitM:limit,nominalAlgebraicBoundaryM:base-limit,minimumAcceptedBinary64HeightM:minimum,minimumHeightBitsHex:bits(minimum),previousRejectedHeightM:previous,previousHeightBitsHex:bits(previous),minimumOrderedKey:String(lo),originalSubtractionAtMinimum:base-minimum,originalSubtractionAtPrevious:base-previous,allFiniteBinary64HeightsAboveBoundaryAccepted:true,noToleranceOrAcceptanceCredit:true};
}
export function guardSamples(building){
 assert(Array.isArray(building.rings)&&building.rings.length);for(const ring of building.rings){assert(ring.length>=3);for(const p of ring)assert(p.length===2&&p.every(Number.isFinite));}
 const points=building.rings.flat().map(p=>[p[0],p[1]]),origins=building.rings.flatMap((r,ring)=>r.map((p,vertex)=>({kind:'exactExistingRingVertex',ring,vertex}))),outer=building.rings[0],xs=outer.map(p=>p[0]),zs=outer.map(p=>p[1]),lo=[Math.min(...xs),Math.min(...zs)],hi=[Math.max(...xs),Math.max(...zs)];
 const step=Math.max(2,Math.sqrt((hi[0]-lo[0])*(hi[1]-lo[1])/2500));assert(Number.isFinite(step));let xi=0;
 for(let x=lo[0]+step/2;x<hi[0];x+=step,xi++){let zi=0;for(let z=lo[1]+step/2;z<hi[1];z+=step,zi++)if(inPolygon(x,z,building.rings)){points.push([x,z]);origins.push({kind:'exactExistingInteriorLattice',xStep:xi,zStep:zi});}}
 assert(points.length===origins.length&&points.every(p=>p.every(Number.isFinite)));return {points,origins,step,closedBounds:[...lo,...hi],ordering:'all rings in raw order including duplicate closure vertices, then x-major/z-minor original JS loops',sameInPolygonProductionFunction:true};
}
