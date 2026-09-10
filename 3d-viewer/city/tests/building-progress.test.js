import test from 'node:test';import assert from 'node:assert/strict';import{countCoverage}from '../../../source-scripts/city/building-progress/counts.mjs';
const review=(uid,sha='a',state='installed-verified')=>({uid,source_sha256:sha,review_state:state});
test('multipart forms and replacements count once without claiming whole buildings',()=>{const r=countCoverage({forms:[{uid:'a'},{uid:'a'},{uid:'b'},{uid:'c'}],models:[{uid:'a',sha256:'a'},{uid:'a',sha256:'a'},{uid:'b',sha256:'a'}],reviews:[review('a'),review('b')]});assert.equal(r.totalForms,3);assert.equal(r.reviewedEnhancedForms,2);assert.ok(Math.abs(r.percent-200/3)<1e-10);assert.equal(r.wholeBuildingCompletion,null);});
test('held, pending, downloaded-only and mismatched sources excluded',()=>{const r=countCoverage({forms:[{uid:'a'},{uid:'b'},{uid:'c'}],models:[{uid:'a',sha256:'b'},{uid:'b',sha256:'a'},{uid:'c',sha256:'a'}],reviews:[review('a'),review('b','a','held'),review('c','a','approved-for-integration'),review('downloaded')]});assert.equal(r.reviewedEnhancedForms,0);assert.equal(r.totalForms,3);});
test('new deployed forms included and removed bridge proxies excluded',()=>{const r=countCoverage({forms:[{uid:'bridge'}],models:[{uid:'bridge',sha256:'a'},{uid:'new',sha256:'a'}],reviews:[review('bridge'),review('new')],suppressed:['bridge']});assert.equal(r.totalForms,1);assert.equal(r.reviewedEnhancedForms,1);});
test('empty data is unknown coverage, never100%; conflicting source IDs rejected',()=>{assert.equal(countCoverage({forms:[],models:[],reviews:[]}).percent,null);assert.throws(()=>countCoverage({forms:[],models:[{uid:'a',sha256:'a'},{uid:'a',sha256:'b'}],reviews:[]}));});

import {SCREENING_POLICY,screeningFingerprint} from '../../scripts/building-progress/screening.mjs';
import {coveragePresentation} from '../building-progress.js';
const screening=(uid,decision='good-to-go',inputHash='current')=>({uid,decision,inputHash,policy:SCREENING_POLICY,reason:'Adequate current silhouette',evidence:'review.json',evidenceHash:'a'.repeat(64),reviewedAt:'2026-09-10T00:00:00Z'});
test('good enough earns progress without a new model; unknown is not required',()=>{
 const result=countCoverage({forms:['a','b','c','d'].map(uid=>({uid,inputHash:'current'})),models:[{uid:'b',sha256:'a'}],reviews:[review('b')],screenings:[screening('a'),screening('c','enhancement-required')]});
 assert.deepEqual(result.breakdown,{enhanced:1,goodToGo:1,enhancementRequired:1,unassessed:1});assert.equal(result.readyForms,2);assert.equal(result.readyPercent,50);
});
test('stale decisions lose skip credit and current rework overrides verified geometry',()=>{
 const args={forms:[{uid:'a',inputHash:'current'},{uid:'b',inputHash:'current'}],models:[{uid:'b',sha256:'a'}],reviews:[review('b')],screenings:[screening('a','good-to-go','old'),screening('b','enhancement-required')]};
 assert.deepEqual(countCoverage(args).breakdown,{enhanced:0,goodToGo:0,enhancementRequired:1,unassessed:1});
 args.screenings=[{...screening('a'),policy:'old-policy'}];assert.equal(countCoverage(args).breakdown.goodToGo,0);
});
test('fingerprints ignore object ordering but change with geometry or context',()=>{
 assert.equal(screeningFingerprint({a:1,b:2},null,'terrain'),screeningFingerprint({b:2,a:1},null,'terrain'));
 assert.notEqual(screeningFingerprint({a:1},null,'terrain'),screeningFingerprint({a:2},null,'terrain'));
 assert.notEqual(screeningFingerprint({a:1},null,'terrain'),screeningFingerprint({a:1},null,'changed terrain'));
});
test('screened and enhanced categories never double count; removed forms stay removed',()=>{
 const r=countCoverage({forms:[{uid:'a',inputHash:'current'},{uid:'hidden',inputHash:'current'}],models:[{uid:'a',sha256:'a'}],reviews:[review('a')],screenings:[screening('a'),screening('hidden')],suppressed:['hidden']});
 assert.equal(r.totalForms,1);assert.equal(r.breakdown.enhanced,1);assert.equal(r.breakdown.goodToGo,0);
});
const sourceForm=uid=>({uid,buildingCSUID:'source-'+uid,inputHash:'current'});
test('government scope intersects current identities, suppression and accepted reviews',()=>{
 const r=countCoverage({forms:['a','b','c','stale','hidden'].map(sourceForm),models:[{uid:'a',sha256:'a'},{uid:'c',sha256:'a'}],reviews:[review('a'),review('c')],suppressed:['hidden'],governmentSources:[['a','source-a'],['b','source-b'],['stale','old-source'],['hidden','source-hidden'],['removed','source-removed']]});
 assert.equal(r.totalForms,4);assert.equal(r.breakdown.enhanced,2);
 assert.deepEqual(r.government,{available:2,enhanced:1,goodToGo:0,ready:1,remaining:1,percent:50,noMatchedSource:2,enhancedOutside:1,goodToGoOutside:0});
 assert.throws(()=>countCoverage({forms:[],models:[],reviews:[],governmentSources:[['a','source-a'],['a','source-a']]}));
});
test('government completion uses matched source scope; good-to-go and rework stay source-bound',()=>{
 const args={forms:['a','b','c','d'].map(sourceForm),models:[{uid:'a',sha256:'a'}],reviews:[review('a')],screenings:[screening('a','enhancement-required'),screening('b'),screening('c')],governmentSources:[['a','source-a'],['b','source-b']]};
 const r=countCoverage(args);assert.equal(r.government.ready,1);assert.equal(r.government.remaining,1);assert.equal(r.government.percent,50);assert.equal(r.government.goodToGoOutside,1);assert.equal(r.breakdown.enhanced,0);
 args.screenings=[screening('b','good-to-go','old')];args.models=[{uid:'a',sha256:'changed'}];const stale=countCoverage(args);assert.equal(stale.government.ready,0);assert.equal(stale.government.remaining,2);
});
test('presentation validates source scope and reports unknown completion with no matched sources',()=>{
 const r=countCoverage({forms:['a','b','c','d'].map(sourceForm),models:[{uid:'a',sha256:'a'},{uid:'c',sha256:'a'}],reviews:[review('a'),review('c')],governmentSources:[['a','source-a'],['b','source-b']]});
 const d={version:3,status:'available',updatedAt:'2026-09-11',...r};
 assert.equal(coveragePresentation(d).enhanced,2);assert.equal(coveragePresentation(d).ready,1);assert.equal(coveragePresentation(d).percent,50);assert.equal(coveragePresentation(d).sourcePending,1);
 assert.equal(coveragePresentation({...d,totalForms:9}),null);assert.equal(coveragePresentation({...d,version:2}),null);
 assert.equal(coveragePresentation({...d,government:{...d.government,remaining:0}}),null);
 assert.equal(coveragePresentation({...d,government:{...d.government,enhancedOutside:0}}),null);
 const empty=countCoverage({forms:[],models:[],reviews:[],governmentSources:[]});assert.equal(coveragePresentation({...d,...empty}).percent,null);
});
