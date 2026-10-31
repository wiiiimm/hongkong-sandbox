import {test} from 'node:test';
import assert from 'node:assert/strict';
import {MODEL_PROFILES,OfficialModelLayer} from '../../../3d-viewer/city/official-models.js';
import {modelBudget} from '../../../3d-viewer/city/official-model-assets.js';

test('exact Lui original uses existing selected mobile allowance, not normal residency',()=>{
 const budget=modelBudget({decodedGeometryBytes:38679000,indexedVertices:963272,triangles:333434});
 const layer=Object.assign(Object.create(OfficialModelLayer.prototype),{cache:{entries:new Map()},retiring:new Map(),releaseFailures:new Map(),limits:MODEL_PROFILES.mobile,lastOptions:{selectedUid:null},drawCosts:new Map()});
 assert.equal(budget.residentBytes,141887880);
 assert(budget.residentBytes>MODEL_PROFILES.mobile.residentBytes);
 assert(budget.residentBytes<=MODEL_PROFILES.mobile.selectedResidentBytes);
 assert.equal(layer.canAdmit('landsd/160070:0',budget),false);
 layer.lastOptions={selectedUid:'landsd/160070:0'};
 assert.equal(layer.canAdmit('landsd/160070:0',budget),true);
 layer.lastOptions={selectedUid:'another-building'};
 assert.equal(layer.canAdmit('landsd/160070:0',budget),false);
});
