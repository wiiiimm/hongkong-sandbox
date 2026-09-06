import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {LIGHT_PROFILES} from '../lighting.js';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url)));
const activity=read('../data/activity.json'),manifest=read('../data/manifest.json');
test('every imported form has an evidenced activity profile and reproducible source hashes',()=>{
 assert.deepEqual(activity.profiles,LIGHT_PROFILES);
 const ids=new Set(),counts={},basis={};
 for(const tile of manifest.tiles)for(const b of read(`../data/tiles/${tile.id}.json`).buildings){
  ids.add(b.uid);const a=activity.buildings[b.uid];assert.ok(a,b.uid);assert.ok(Number.isInteger(a.profile)&&a.profile>=0&&a.profile<5);
  assert.ok(['building-tag','parent-tag','landuse','research','fallback'].includes(a.source));assert.ok(a.ref);assert.ok(a.retailTop>=0);
  counts[a.profile]=(counts[a.profile]||0)+1;basis[a.source]=(basis[a.source]||0)+1;
 }
 assert.equal(Object.keys(activity.buildings).length,ids.size);assert.deepEqual(counts,activity.counts);assert.deepEqual(basis,activity.basisCounts);
 for(const s of activity.sources){const raw=gunzipSync(readFileSync(new URL('../../../'+s.file,import.meta.url)));assert.equal(createHash('sha256').update(raw).digest('hex'),s.sha256);}
});
test('mapped malls, office towers and researched podiums retain their different uses',()=>{
 const b=activity.buildings;
 for(const id of ['171780359','1049552289','710522579'])assert.equal(b[`way/${id}:0`].profile,1);
 for(const id of ['102411832','374802636','664250326'])assert.equal(b[`way/${id}:0`].profile,4);
 assert.equal(b['way/171224612:0'].retailTop,80);assert.equal(b['way/171224612:0'].source,'research');
 assert.equal(b['way/1323739469:0'].profile,1);assert.equal(b['way/1323739469:0'].retailTop,30);
});
