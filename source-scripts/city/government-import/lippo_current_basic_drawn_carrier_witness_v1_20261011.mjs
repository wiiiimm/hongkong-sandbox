/** Exact retained BASIC availability/drawn triangle witness; no whole-body credit. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const IDENTITY=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];
export function verifyDrawnBasicCarrier(expected,state){
 assert.equal(expected.uid,'landsd/231645:0');assert.equal(expected.csuid,'3551417531P20050812');
 assert.equal(state.uid,expected.uid);assert.equal(state.csuid,expected.csuid);
 assert(state.loaded&&state.tileWanted&&state.supportAvailable&&state.tileGroupVisible);
 assert.equal(state.detailedActive,false);assert.equal(state.hidden,false);assert.equal(state.suppressed,false);assert.equal(state.nativeCatalogueEntry,false);assert.equal(state.bakedModelGeometry,false);
 assert(state.meshMatrices.length&&state.meshMatrices.every(m=>JSON.stringify(m)===JSON.stringify(IDENTITY)));
 assert.equal(state.completeDrawnTriangles.length,284);assert.equal(expected.completeTriangles.length,284);
 assert(state.completeDrawnTriangles.every(t=>t.length===9&&t.every(Number.isFinite)));
 // Preserve orientation, repeated vertices, degenerate records and multiplicity.
 const encode=triangles=>triangles.map(t=>JSON.stringify(t)).sort();assert.deepEqual(encode(state.completeDrawnTriangles),encode(expected.completeTriangles));
 const canonical=encode(state.completeDrawnTriangles);return {uid:state.uid,csuid:state.csuid,completeDrawnFaces:284,completeOrientedTriangleMultisetSHA256:createHash('sha256').update(JSON.stringify(canonical)).digest('hex'),exactCurrentBasicGeometryVisible:true,productionSupportAvailable:true,wholeBasicReaccepted:false,nativeOrOriginalGovernmentPodiumSupportCredit:false};
}
