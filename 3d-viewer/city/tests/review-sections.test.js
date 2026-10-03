import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {readinessFor,prepareReviewSections,reviewCounts,sectionAt,REVIEW_GATES} from '../review-sections-data.js';
const verified=()=>({state:'verified',scope:'section',evidence:[{path:'review.md',commit:'example'}]});
const record=()=>({id:'01.1',checks:Object.fromEntries(REVIEW_GATES.map(k=>[k,verified()]))});
const geometry=()=>({schemaVersion:1,sections:[{id:'01.1',name:'Review area',bounds:[0,0,10,10],label:[2,2],polygons:[{rings:[[[0,0],[10,0],[10,10],[0,10],[0,0]],[[4,4],[4,6],[6,6],[6,4],[4,4]]]}]}]});
const ledger=()=>({schemaVersion:1,sections:[record()]});
test('local route acceptance and imported geometry do not claim whole-section readiness',()=>{
 const r=record();for(const c of Object.values(r.checks))c.scope='local';assert.equal(readinessFor(r).status,'base');
 r.phase='active';assert.equal(readinessFor(r).status,'reviewing');assert.equal(readinessFor(r).verified,0);
});
test('readiness requires actual evidence, ground and buildings, with no known blockers',()=>{
 const r=record();assert.equal(readinessFor(r).status,'ready');
 r.checks.presentation.state='partial';r.checks.provenance.evidence=[];assert.equal(readinessFor(r).status,'close');
 r.checks.ground.scope='local';assert.equal(readinessFor(r).status,'reviewing');
 const b=record();b.blockers=['Terrain conflict'];assert.equal(readinessFor(b).status,'reviewing');
});
test('section membership respects holes and finite bounds',()=>{
 const sections=prepareReviewSections(geometry(),ledger(),{expectedCount:1});
 assert.equal(sectionAt(sections,2,2).id,'01.1');assert.equal(sectionAt(sections,5,5),null);assert.equal(sectionAt(sections,12,5),null);
 for(const mutate of [g=>g.sections[0].label=[5,5],g=>g.sections[0].bounds=[0,0,NaN,10],g=>g.sections[0].polygons[0].rings[0].pop()]){const g=geometry();mutate(g);assert.throws(()=>prepareReviewSections(g,ledger(),{expectedCount:1}));}
});
test('truncated or mismatched inventories fail visibly instead of implying coverage',()=>{
 assert.throws(()=>prepareReviewSections(geometry(),ledger()));const l=ledger();l.sections[0].id='01.2';assert.throws(()=>prepareReviewSections(geometry(),l,{expectedCount:1}));
 const g=geometry(),r=ledger();g.sections.push(g.sections[0]);r.sections.push(r.sections[0]);assert.throws(()=>prepareReviewSections(g,r,{expectedCount:2}));
});
test('published inventory covers every checklist ID exactly once with truthful totals',()=>{
 const g=JSON.parse(readFileSync(new URL('../data/review-sections.json',import.meta.url))),r=JSON.parse(readFileSync(new URL('../data/section-readiness.json',import.meta.url)));
 const sections=prepareReviewSections(g,r),checklist=readFileSync(new URL('../../../docs/astra-city/SECTION-CHECKLIST.md',import.meta.url),'utf8'),ids=[...checklist.matchAll(/^- \[[ xX]\] \*\*(\d{2}\.\d+)\*\*/gm)].map(m=>m[1]);
 assert.deepEqual(sections.map(s=>s.id),ids);assert.equal(Object.values(reviewCounts(sections)).reduce((n,v)=>n+v,0),132);
 for(const [id,parent]of [['10.12','HKS-123'],['11.6','HKS-122'],['14.8','HKS-123'],['17.1','HKS-126']])assert.ok(sections.find(s=>s.id===id).review.issues.includes(parent));
 for(const s of sections){assert.equal(sectionAt(sections,...s.label)?.id,s.id);assert.ok(s.review.issues.every(id=>/^HKS-\d+$/.test(id)));}
});
