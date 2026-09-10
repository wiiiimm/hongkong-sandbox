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
test('presentation rejects inconsistent totals and handles empty inventory',()=>{
 const d={version:2,status:'available',unit:'source-building-form',totalForms:10,updatedAt:'2026-09-10',breakdown:{enhanced:2,goodToGo:3,enhancementRequired:1,unassessed:4}};
 assert.equal(coveragePresentation(d).ready,5);assert.equal(coveragePresentation(d).percent,50);
 assert.equal(coveragePresentation({...d,totalForms:9}),null);
 assert.equal(coveragePresentation({...d,totalForms:0,breakdown:{enhanced:0,goodToGo:0,enhancementRequired:0,unassessed:0}}).percent,null);
});
