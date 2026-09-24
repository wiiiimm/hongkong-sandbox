import test from 'node:test';
import assert from 'node:assert/strict';
import {prepareBridges} from '../bridge-data.js';
const path=(id,points,nodes,tags={})=>({id,source:'https://www.openstreetmap.org/'+id,kind:'footway',role:'bridge',path:points,nodes,tags});
const pack=bridges=>({schemaVersion:1,bridges});
const sampler={height:()=>10};
test('source-connected spans share deck heights while coincident crossings remain separate',()=>{
 const a=path('way/1',[[0,0],[10,0]],[1,2]);a.level=1;
 const b=path('way/2',[[10,0],[20,0]],[2,3]);b.level=2;
 const c=path('way/3',[[10,-5],[10,0],[10,5]],[4,5,6]);c.level=4;
 const [ra,rb,rc]=prepareBridges(pack([a,b,c]),sampler);
 assert.equal(ra.deckPath.at(-1)[1],rb.deckPath[0][1]);assert.notEqual(ra.deckPath.at(-1)[1],rc.deckPath[1][1]);
});
test('layer and total height never masquerade as measured deck elevations',()=>{
 const a={...path('way/1',[[0,0],[10,0]],[1,2]),height:80,layer:2,tags:{height:'80'}};
 const r=prepareBridges(pack([a]),sampler)[0];assert.ok(r.deckPath[0][1]<30);assert.equal(r.estimatedElevation,true);assert.match(r.elevationBasis,/not a measured height/);assert.match(r.elevationBasis,/not used as deck elevation/);
});
test('an access way joins only an exported bridge at its actual source node',()=>{
 const bridge=path('way/1',[[0,0],[10,0]],[1,2]);
 const access={...path('way/2',[[-10,0],[0,0]],[3,1]),role:'access',kind:'steps',connectsTo:['way/1']};
 const unrelated={...path('way/3',[[-10,1],[0,0]],[4,5]),role:'access',connectsTo:['way/1']};
 const result=prepareBridges(pack([bridge,access,unrelated]),sampler);
 assert.equal(result.length,2);assert.equal(result[1].deckPath.at(-1)[1],result[0].deckPath[0][1]);assert.equal(result[1].deckPath[0][1],10.16);
});
test('ordinary indoor floor corridors are omitted, but explicitly mapped indoor bridges remain',()=>{
 const corridor={...path('way/1',[[0,0],[10,0]],[1,2],{indoor:'yes'}),role:'elevated-link',level:2};
 const bridge={...path('way/2',[[10,0],[20,0]],[2,3],{indoor:'yes',bridge:'yes',covered:'yes'}),role:'elevated-link',level:2,width:4.5};
 const result=prepareBridges(pack([corridor,bridge]),sampler);assert.equal(result.length,1);assert.equal(result[0].covered,true);assert.equal(result[0].width,4.5);assert.equal(result[0].widthBasis,'Mapped width in metres');
});
test('invalid coordinates and duplicate source IDs reject the inventory',()=>{
 assert.throws(()=>prepareBridges(pack([path('bad',[[0,0],[NaN,0]],[1,2])]),sampler));const b=path('way/1',[[0,0],[10,0]],[1,2]);assert.throws(()=>prepareBridges(pack([b,b]),sampler));
});
