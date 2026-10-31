import test from 'node:test';
import assert from 'node:assert/strict';
import {prepareBasicFallbackProtections,basicFallbackIsProtected} from '../basic-fallback-protections.js';
const policy={uid:'landsd/1:0',buildingCSUID:'one',sourceSHA256:'a'.repeat(64),suppressorUid:'landsd/2:0',suppressorSourceSHA256:'b'.repeat(64)};
const building={uid:policy.uid,buildingCSUID:policy.buildingCSUID};
const detail={record:{uid:policy.suppressorUid},entry:{sha256:policy.suppressorSourceSHA256,publicationApproved:false}};
test('only the reviewed compound source and current building identity retain BASIC',()=>{
 const raw=[{...policy}],protections=prepareBasicFallbackProtections(raw);
 assert.equal(basicFallbackIsProtected(protections,building,detail),true);
 assert.equal(basicFallbackIsProtected(protections,{...building,buildingCSUID:'changed'},detail),false);
 assert.equal(basicFallbackIsProtected(protections,building,{...detail,record:{uid:'landsd/3:0'}}),false);
 assert.equal(basicFallbackIsProtected(protections,building,{...detail,entry:{sha256:'c'.repeat(64)}}),false);
 raw[0].buildingCSUID='mutated';assert.equal(basicFallbackIsProtected(protections,building,detail),true);
 assert.equal(detail.entry.publicationApproved,false);
});
test('compatible approved variant source identity can retain the same BASIC fallback',()=>{
 const protections=prepareBasicFallbackProtections([policy]);
 assert.equal(basicFallbackIsProtected(protections,building,{...detail,entry:{sha256:'c'.repeat(64),sourceSha256:policy.suppressorSourceSHA256}}),true);
 assert.equal(basicFallbackIsProtected(protections,building,null),false);
 assert.equal(basicFallbackIsProtected(prepareBasicFallbackProtections(),building,detail),false);
});
test('malformed, duplicate and self protections reject before use',()=>{
 for(const rows of [{},[null],[{...policy,sourceSHA256:'bad'}],[{...policy,suppressorUid:policy.uid}],[{...policy,unreviewed:true}],[policy,policy]])assert.throws(()=>prepareBasicFallbackProtections(rows),/fallback protection/);
});
