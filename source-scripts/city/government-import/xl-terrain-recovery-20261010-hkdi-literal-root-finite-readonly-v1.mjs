/** Production JS support plus exact finite actual-terrain genuine anchors. */
import assert from 'node:assert/strict';
import {readFileSync}from'node:fs';import{gunzipSync}from'node:zlib';
import {verifySupportInterface}from'./support-interface.mjs';
import {lowRimSamples}from'./support-contact.mjs';
import {nativeTerrainSurface}from'../../../3d-viewer/city/native-terrain.js';
const x=JSON.parse(gunzipSync(readFileSync(process.argv[2])));
assert.equal(x.uid,'landsd/22089:0');assert([134,135,144,156].includes(x.component));
assert(x.terrain.position.every(v=>Number.isFinite(v)&&Math.fround(v)===v),'Literal drawn-ground coordinates must already be Float32; no quantization credit');
const legacy=verifySupportInterface(x.part,x.part.bottomHKPD,x.terrain),surface=nativeTerrainSurface(x.terrain);
const rows=lowRimSamples(x.part,x.part.bottomHKPD).map(position=>{const ground=surface.height(position[0],position[2]);return{position,ground,gap:ground===null?null:position[1]-ground};});
const missing=rows.filter(r=>r.gap===null),anchors=rows.filter(r=>r.gap!==null&&r.gap>=-.1&&r.gap<=.1);
const passed=legacy.passed&&rows.length>0&&missing.length===0&&anchors.length>0&&rows.every(r=>r.gap>=-.5&&r.gap<=1);
console.log(JSON.stringify({contract:'hkdi-literal-original-root-production-js-and-closed-finite-genuine-anchor-v1',passed,unchangedProductionSupport:legacy,completeLiteralLowRim:rows,strictGenuineAnchorSamples:anchors,missing:missing.length,geometryChanges:0,minimumClearanceLimitM:-.5,rimMaximumLimitM:1,anchorBandM:[-.1,.1],noArithmeticParityCredit:true}));
