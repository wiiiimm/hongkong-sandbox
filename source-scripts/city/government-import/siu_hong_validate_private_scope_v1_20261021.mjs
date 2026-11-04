/** Private source-bound scope injection; production validator remains unchanged. */
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {directOsmGroupScopes} from '../../../3d-viewer/city/official-model-direct-osm-group-data.js';
const args=process.argv.slice(2),at=args.indexOf('--conditional-scope');assert(at>=0);
const scope=JSON.parse(readFileSync(args[at+1]));assert.equal(scope.key,'direct-osm-group:siu-hong-private-pair-20261021');assert.equal(directOsmGroupScopes[scope.key],undefined);
const ordered=structuredClone(scope.definition);ordered.forms=ordered.forms.map(b=>({uid:b.uid,objectId:b.objectId,buildingCSUID:b.buildingCSUID,parent:b.parent,osmRefs:b.osmRefs??null,rings:b.rings}));assert.deepEqual(ordered,scope.definition);
directOsmGroupScopes[scope.key]=ordered;
try {await import('../building-batch/validate_candidates_footprint_scope.mjs');} finally {delete directOsmGroupScopes[scope.key];}
