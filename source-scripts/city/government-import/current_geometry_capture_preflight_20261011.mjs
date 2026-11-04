/** Read-only schema/census and ordered numeric-array guards; no geometry edits. */
import assert from 'node:assert/strict';
export function appendFiniteOrdered(target,values){assert(Array.isArray(target));for(const value of values){assert(typeof value==='number'&&Number.isFinite(value),'Finite numeric records only');target.push(value);}return target;}
export function preflightCurrentActorCensus(input,{ownedUID,ownedFaces,basicUID}){
 assert(input.rows.length===1&&input.rows[0].uid===ownedUID);const row=input.rows[0];assert(row.triangles===ownedFaces&&row.candidate.entry.triangles===ownedFaces&&row.candidate.entry.uid===ownedUID&&row.candidate.entry.sha256===row.sourceSHA256);
 assert.deepEqual(row.candidate.entry.rootTranslation,[-834500,0,816500]);assert(input.terrainProposal===null&&input.terrainGeometryChanges===0);
 const native=new Map();for(const r of input.completeCurrentNativeOriginalPOSITIONCensus){assert(typeof r.uid==='string'&&!native.has(r.uid)&&/^[0-9a-f]{64}$/.test(r.sourceSHA256));native.set(r.uid,r);}
 assert(!native.has(ownedUID)&&!native.has(basicUID));const scope=new Set();for(const r of input.completeCurrentForms){const b=r.building;assert(typeof b.uid==='string'&&!scope.has(b.uid));scope.add(b.uid);assert(typeof r.existingNative==='boolean'&&r.existingNative===native.has(b.uid),'Native flag must match unique current catalogue membership');assert.deepEqual(input.currentAllSourceForms[b.uid],b);}
 assert(scope.has(ownedUID)&&scope.has(basicUID));const near=new Set();for(const r of input.nearbyCurrentNativeActors){assert(native.has(r.uid)&&!near.has(r.uid)&&native.get(r.uid).sourceSHA256===r.entry.sha256);near.add(r.uid);assert(r.entry.uid===r.uid&&r.building.uid===r.uid&&r.entry.buildingCSUID===r.building.buildingCSUID);}
 const cats=input.currentCatalogueRefs.map(r=>r.path);assert(new Set(cats).size===cats.length&&cats.every(p=>typeof p==='string'&&p.startsWith('3d-viewer/')));return {completeScopeForms:scope.size,completeNativeActors:native.size,capturedNearbyNativeActors:near.size};
}
export function preflightActualRenderMesh(mesh){
 const geometry=mesh.geometry,p=geometry.attributes.position,ix=geometry.index?.array,m=mesh.matrixWorld.elements;
 assert(p.array instanceof Float32Array&&p.itemSize===3&&p.count>0&&p.array.length===p.count*3);assert(ix instanceof Uint16Array||ix instanceof Uint32Array);assert(ix.length>0&&ix.length%3===0);
 for(const v of p.array)assert(Number.isFinite(v));for(const i of ix)assert(i<p.count,'Actual index outside complete POSITION attribute');
 for(const name of ['normal','color']){const a=geometry.attributes[name];assert(a&&a.count===p.count&&a.array.length===a.count*a.itemSize&&a.itemSize>=3&&a.itemSize<=4);for(const v of a.array)assert(Number.isFinite(v));}
 assert(m.length===16&&Array.from(m).every(Number.isFinite)&&m[3]===0&&m[7]===0&&m[11]===0&&m[15]===1);return {completePositionVertices:p.count,completeIndexedFaces:ix.length/3};
}
