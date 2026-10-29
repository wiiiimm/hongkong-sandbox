import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {CityStreaming} from '../streaming.js';
import {prepareModelCatalogue} from '../official-model-assets.js';
import {reviewedOsmRoofFormMatches} from '../official-model-reviewed-osm-roof.js';
const data=JSON.parse(readFileSync(new URL('./fixtures/peninsula-reviewed-osm-roof.json',import.meta.url)));
const fixture=data.catalogue,review=data;
function entry(){const e=structuredClone(fixture.models.find(m=>m.uid==='landsd/270876:0'));e.suppressesBuildingUids=['way/709674357:0'];e.reviewedOsmRoofReplacement={policy:'exact-original-peninsula-entrance-roof-v1',sourceSHA256:e.sha256,roofFormSHA256:review.roofFormSHA256};return e;}
function catalogue(e){return {...fixture,models:[e],counts:{packedModels:1}};}
function suppressions(e,b){const stream=Object.create(CityStreaming.prototype);stream.detailedModels=new Map([[e.uid,{entry:e}]]);stream.basicFallbackProtections=new Map();return stream.detailSuppressions(stream.detailedModels,[b]);}
const url='https://example.test/city/data/official-models/test/catalogue.json';
test('exact reviewed source and current roof are eligible without modifying either',()=>{const e=entry(),before=structuredClone(e),b=structuredClone(review.exactRoofForm);assert.equal(prepareModelCatalogue(catalogue(e),url).length,1);assert(reviewedOsmRoofFormMatches(e,b));assert(suppressions(e,b).has(b.uid));assert.deepEqual(e,before);assert.deepEqual(b,review.exactRoofForm);});
test('unreviewed OSM suppression still rejects',()=>{const e=entry();delete e.reviewedOsmRoofReplacement;assert.throws(()=>prepareModelCatalogue(catalogue(e),url),/suppression/);});
test('another source revision, pose, marker or OSM target cannot inherit this review',()=>{for(const mutate of [e=>e.sha256='0'.repeat(64),e=>e.modelId='B999999999902063C0',e=>e.verticalPlacementOffsetHKPD=1,e=>e.reviewedOsmRoofReplacement.policy='other',e=>e.reviewedOsmRoofReplacement.extra=true,e=>e.suppressesBuildingUids=['way/709674358:0']]){const e=entry();mutate(e);assert.throws(()=>prepareModelCatalogue(catalogue(e),url));}});
test('any changed roof source field keeps BASIC visible',()=>{for(const mutate of [b=>b.base++,b=>b.height++,b=>b.rings[0][0][0]+=.1,b=>b.part=false,b=>b.levels=2,b=>b.uid='way/other:0']){const b=structuredClone(review.exactRoofForm);mutate(b);assert.equal(reviewedOsmRoofFormMatches(entry(),b),false);assert.equal(suppressions(entry(),b).size,0);}});
test('absence of the exact owner restores the roof, runtime activity annotations are harmless',()=>{const stream=Object.create(CityStreaming.prototype);stream.basicFallbackProtections=new Map();assert.equal(stream.detailSuppressions(new Map(),[review.exactRoofForm]).size,0);assert(reviewedOsmRoofFormMatches(entry(),{...review.exactRoofForm,activity:{profile:1}}));});
test('existing LandsD suppressions retain their previous behaviour',()=>{const e=structuredClone(fixture.models[0]);e.suppressesBuildingUids=['landsd/999:0'];assert.equal(prepareModelCatalogue(catalogue(e),url).length,1);assert(suppressions(e,{uid:'landsd/999:0'}).has('landsd/999:0'));});
