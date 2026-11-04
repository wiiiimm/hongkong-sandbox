import assert from 'node:assert/strict';
import {test} from 'node:test';
import {installedDependencyState as check} from './installed-dependency-state.mjs';
const fixture=()=>[{uid:'landsd/1:0',csuid:'1234567890P20200101',state:'candidate'},
 {uid:'landsd/1:0',buildingCSUID:'1234567890P20200101',sha256:'a'.repeat(64),publicationApproved:true,placementReviewed:true,sourceIdentityReviewed:true},
 {uid:'landsd/1:0',csuid:'1234567890P20200101',sourceSHA256:'a'.repeat(64),assetSHA256:'a'.repeat(64),reviewState:'installed-verified',snapshotVerified:true,snapshotId:'snapshot'}];
test('stale candidate label resolves only from exact installed evidence without mutation',()=>{const args=fixture(),before=JSON.stringify(args),r=check(...args);assert.equal(r.passed,true);assert.equal(r.declaredState,'candidate');assert.equal(r.effectiveState,'installed');assert.equal(JSON.stringify(args),before);});
test('an installed label alone does not establish acceptance',()=>{const a=fixture();a[0].state='installed';assert.equal(check(a[0],a[1],null).passed,false);a[2].reviewState='approved';assert.equal(check(...a).passed,false);});
test('foreign support UID/CSUID or changed bytes cannot be reused',()=>{for(const [index,key,value]of [[1,'uid','landsd/2:0'],[2,'uid','landsd/2:0'],[1,'buildingCSUID','different'],[2,'csuid','different'],[1,'sha256','b'.repeat(64)],[2,'assetSHA256','b'.repeat(64)],[2,'sourceSHA256','b'.repeat(64)]]){const a=fixture();a[index][key]=value;assert.equal(check(...a).passed,false);}});
test('rework/unverified snapshot/unknown explicit states stay blocked',()=>{for(const [index,key,value]of [[2,'reviewState','rework'],[2,'snapshotVerified',false],[2,'snapshotId',null],[0,'state','held'],[0,'state','missing']]){const a=fixture();a[index][key]=value;assert.equal(check(...a).passed,false);}});
test('all current publication approvals remain required',()=>{for(const key of ['placementReviewed','sourceIdentityReviewed']){const a=fixture();a[1][key]=false;assert.equal(check(...a).passed,false);}});

test('legacy unpublished flag needs exact verified installed acceptance, not a current review label alone',()=>{const a=fixture();a[1].publicationApproved=false;assert.equal(check(...a).passed,false);a[2].installedAcceptanceVerified=true;assert.equal(check(...a).passed,true);a[2].reviewState='rework';assert.equal(check(...a).passed,false);});
