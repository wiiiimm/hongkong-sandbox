import test from 'node:test';
import assert from 'node:assert/strict';
import {verifySupportInterface} from './support-interface.mjs';
const deck={position:[-1,0,-1,5,0,-1,-1,0,5],index:[0,1,2]};
function source({depth=.46,wallTop=2,horizontal=false}={}){
 // One embedded bottom vertex plus two ordinary deck contacts.
 return {position:[1,-depth,1,1,wallTop,1,2,wallTop,1, 0,0,0,.2,0,0,0,0,.2],
  index:[0,1,2,3,4,5],...(horizontal?{position:[1,-depth,1,2,-depth,1,1,-depth,2,0,0,0,.2,0,0,0,0,.2]}:{})};
}
test('source wall intersects exact deck without moving its buried rim',()=>{
 const g=source(),before=structuredClone(g),r=verifySupportInterface(g,-.46,deck);
 // The usual global 0.35m band excludes the reference deck contacts; broaden
 // only the fixture's bottom depth, keeping the real rule unchanged.
 assert.equal(r.passed,false);assert.equal(r.wallIntersections,1);assert.deepEqual(g,before);
 const accepted=verifySupportInterface(source({depth:.3}),-.3,deck);assert.equal(accepted.passed,true);
 assert.equal(accepted.resolved[0].contactGapM,0);
});
test('horizontal buried floor is not a supported wall interface',()=>assert.equal(verifySupportInterface(source({depth:.3,horizontal:true}),-.3,deck).passed,false));
test('wall fully below deck cannot manufacture a contact',()=>assert.equal(verifySupportInterface(source({depth:.3,wallTop:-.1}),-.3,deck).passed,false));
test('deeply embedded source and enlarged embedding allowance remain rejected',()=>{
 assert.equal(verifySupportInterface(source({depth:.6}),-.6,deck).passed,false);
 assert.throws(()=>verifySupportInterface(source(),-.46,deck,{maximumEmbedding:1}));
});
test('missing podium and floating source remain rejected',()=>{
 assert.equal(verifySupportInterface(source({depth:.3}),-.3,{position:[],index:[]}).passed,false);
 const g=source({depth:.3});g.position=g.position.map((v,i)=>i%3===1?v+3:v);
 assert.equal(verifySupportInterface(g,2.7,deck).passed,false);
});
