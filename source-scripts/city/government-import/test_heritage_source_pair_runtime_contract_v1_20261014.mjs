/** Saved result/public API fixture only. No source decode or renderer. */
import {readFileSync}from'node:fs';import assert from'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import{GLTFLoader}from'../../../3d-viewer/vendor/GLTFLoader.js';
const root=new URL('../../../',import.meta.url),p=JSON.parse(readFileSync(new URL('docs/astra-city/government-import/government-xl-heritage165054-starmart57455-private-interface-review-v3-20261014/actual-private-interface-preview.json',root)));
assert.equal(typeof GLTFLoader.prototype.parseAsync,'function');assert.equal(typeof THREE.Object3D.prototype.lookAt,'function');assert.equal(typeof THREE.Object3D.prototype.updateMatrixWorld,'function');assert.equal(typeof THREE.Raycaster.prototype.intersectObjects,'function');assert.equal(typeof THREE.WebGLRenderer,'function');assert.equal(typeof THREE.DirectionalLight,'function');
assert.equal(p.views.length,3);assert.equal(p.scenarios.length,1);assert.equal(p.scenarios[0].currentBASICDrawnFaces,24);assert.equal(p.scenarios[0].sources[0].faces,15140);assert.equal(p.scenarios[0].sources[0].actualGPU[0].vertices,43248);
for(const v of p.views)for(const k of ['cleanSolidImage','markedImage'])assert(readFileSync(new URL(v[k],root)).length>1000);
const d=p.loadingDiagnostics.at(-1);assert.equal(d.uid,'landsd/57455:0');assert.equal(d.modelKnown,true);assert.equal(d.detailedActive,false);assert.match(d.cacheError,/Official model does not fit its matched footprint/);assert.equal(d.official.loadingPaused,false);
console.log(JSON.stringify({passed:true,sixCurrentExportsAndSourceBindingRetained:true,genuineProductionStarFootprintRejectionRetained:true,actualRawGLTFAndCameraRayPublicAPIsBound:true,sourceDecodeGeometryRenderDBLease:false}));
