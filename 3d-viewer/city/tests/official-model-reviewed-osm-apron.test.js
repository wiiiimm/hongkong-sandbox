import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {CityStreaming} from '../streaming.js';
import {prepareModelCatalogue} from '../official-model-assets.js';
import {officialModelFootprint} from '../official-model-footprint-scopes.js';
import {reviewedOsmApronFormMatches} from '../official-model-reviewed-osm-apron.js';
const fixture=JSON.parse(readFileSync(new URL('./fixtures/disneyland-reviewed-osm-apron.json',import.meta.url)));
const copy=()=>structuredClone(fixture),url='https://example.test/city/data/official-models/apron/catalogue.json';
function suppressed(e,b){const s=Object.create(CityStreaming.prototype);s.basicFallbackProtections=new Map();return s.detailSuppressions(new Map(e?[[e.uid,{entry:e}]]:[]),[b]);}
test('exact original and unchanged estimated apron form are bound to the actual reviewed decision',()=>{
 const f=copy(),e=f.catalogue.models[0],before=structuredClone(f),decision=readFileSync(new URL('../../../'+f.decisionPath,import.meta.url));
 assert.equal(createHash('sha256').update(decision).digest('hex'),e.reviewedOsmApronGraphic.reviewSHA256);
 assert.equal(prepareModelCatalogue(f.catalogue,url).length,1);assert(officialModelFootprint(e,f.sourceBuilding,null));assert(reviewedOsmApronFormMatches(e,f.exactBasicForm));assert(suppressed(e,f.exactBasicForm).has(f.exactBasicForm.uid));assert.deepEqual(f,before);
});
test('unreviewed OSM suppression and forged or expanded markers reject',()=>{
 for(const change of [e=>delete e.reviewedOsmApronGraphic,e=>e.reviewedOsmApronGraphic.policy='other',e=>e.reviewedOsmApronGraphic.reviewSHA256='0'.repeat(64),e=>e.reviewedOsmApronGraphic.basicFormSHA256='0'.repeat(64),e=>e.reviewedOsmApronGraphic.extra=true,e=>e.suppressesBuildingUids.push('way/1:0')]){const f=copy();change(f.catalogue.models[0]);assert.throws(()=>prepareModelCatalogue(f.catalogue,url));}
});
test('another source, pose, coordinate scope or generated variant cannot inherit the graphic review',()=>{
 for(const change of [e=>e.uid='landsd/75642:0',e=>e.sha256='0'.repeat(64),e=>e.modelId='other',e=>e.buildingCSUID='other',e=>e.verticalPlacementOffsetHKPD=1,e=>e.footprintScope='reviewed-original-feature:landsd/99482:0',e=>e.worldBounds[0][0]+=.01,e=>e.variantId='derived',e=>e.sourceWorldBounds=e.worldBounds]){const f=copy();change(f.catalogue.models[0]);assert.throws(()=>prepareModelCatalogue(f.catalogue,url));}
});
test('changed or newly enriched BASIC data retains the original fallback and collision form',()=>{
 for(const change of [b=>b.base++,b=>b.height=3,b=>b.heightSource='surveyed',b=>b.rings[0][0][0]+=.001,b=>b.levels=1,b=>b.part=true,b=>b.baseHeightHKPD=4.41,b=>b.topHeightHKPD=28.41,b=>b.structureType='Canopy',b=>b.surveyedAt='2026',b=>b.name='new metadata']){const f=copy();change(f.exactBasicForm);assert.equal(reviewedOsmApronFormMatches(f.catalogue.models[0],f.exactBasicForm),false);assert.equal(suppressed(f.catalogue.models[0],f.exactBasicForm).size,0);}
});
test('source disappearance restores BASIC, while the normal activity annotation remains eligible',()=>{
 const f=copy();assert.equal(suppressed(null,f.exactBasicForm).size,0);assert(reviewedOsmApronFormMatches(f.catalogue.models[0],{...f.exactBasicForm,activity:{profile:1}}));
});
test('other complete original-feature scopes keep their no-suppression guard',()=>{
 const f=copy();for(const uid of ['landsd/75642:0','landsd/99482:0'])assert.throws(()=>officialModelFootprint({...f.catalogue.models[0],uid},f.sourceBuilding,null));
});
