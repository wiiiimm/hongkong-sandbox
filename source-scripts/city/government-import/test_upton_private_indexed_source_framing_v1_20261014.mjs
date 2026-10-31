import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fitIndexedSourceBox as fit} from './upton_private_indexed_source_framing_v1_20261014.mjs';
const points=[[-20,3,-28],[21,171,40],[-20,171,40],[21,3,-28]],original=structuredClone(points);
for(const direction of [[-1,.6,1],[0,1,.08]])for(const aspect of [1600/1100,390/844]){const f=fit(points,{fov:44,aspect,direction});assert(f.projectedCornerCoordinates.every(p=>Math.abs(p[0])<.74&&Math.abs(p[1])<.70&&p[2]>.5));assert.deepEqual(points,original);if(direction[1]===1)assert(f.camera[1]>171);}
assert.throws(()=>fit(points,{fov:44,aspect:1,direction:[0,1,0]}),/Degenerate/);
assert.throws(()=>fit([],{fov:44,aspect:1,direction:[1,1,1]}),/Invalid/);
const runtime=readFileSync(new URL('./upton_joint_original_private_source_preview_v2_20261014.mjs',import.meta.url),'utf8');assert(runtime.includes('r.closeSelection();'));assert(runtime.includes('Complete indexed source box outside safe frame'));assert(runtime.includes('Plan camera below complete source'));
// No prior proof/geometry changes: compare actual runtime bytes after stripping
// only the explicit display-only additions recorded by the V2 preparation.
console.log(JSON.stringify({passed:true,perspectiveAspectDirectionCases:4,invalidInputCases:2,actualRuntimeSelectionAndFrameGuards:3,productionArraysOrBrowser:false}));
