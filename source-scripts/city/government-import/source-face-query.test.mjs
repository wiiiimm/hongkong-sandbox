import test from 'node:test';
import assert from 'node:assert/strict';
import {createSourceFaceQuery} from './source-face-query.mjs';

test('exact point query retains face winding, duplicates and original indices',()=>{
 const g={position:[-8,0,-8,-8,1,-8,-8,0,-7],index:[0,1,2,2,1,0]},before=structuredClone(g),hits=createSourceFaceQuery(g)([-8,.2,-7.8]);
 assert.deepEqual(hits.map(h=>h.faceIndex),[0,1]);assert.equal(hits[0].normal[0],1);assert.equal(hits[1].normal[0],-1);assert.deepEqual(g,before);
});
test('nearby bounding-box candidates still require exact triangle proximity',()=>{
 const query=createSourceFaceQuery({position:[0,0,0,10,0,0,0,0,10],index:[0,1,2]});
 assert.deepEqual(query([9,0,9]),[]);assert.equal(query([1,.0009,1]).length,1);assert.deepEqual(query([1,.0011,1]),[]);
});
test('unreferenced vertices and empty source buffers grant no face hits',()=>{
 assert.deepEqual(createSourceFaceQuery({position:[0,0,0],index:[]})([0,0,0]),[]);
});
test('query metrics describe bounded work without changing contact output',()=>{
 const metrics={},query=createSourceFaceQuery({position:[0,0,0,1,0,0,0,1,0],index:[0,1,2]},{metrics});
 assert.equal(query([0,0,0]).length,1);assert.deepEqual(query([100,0,100]),[]);assert.equal(metrics.queries,2);assert.equal(metrics.exactTriangleTests,1);
});
