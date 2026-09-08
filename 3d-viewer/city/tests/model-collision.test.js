import test from 'node:test';
import assert from 'node:assert/strict';
import {modelRoofHeight,modelSurfaceCollision} from '../model-collision.js';
import {BuildingIndex} from '../geo.js';
import {describeBuilding} from '../building-geometry.js';
const model=triangles=>({position:triangles.flat(2)});
const triangle=[[-2,2,-2],[2,2,-2],[0,4,2]];
function building(extra={}){return {uid:'fixture',base:0,height:10,minimum:0,structureType:'Tower',rings:[[[0,-2],[2,0],[0,2],[-2,0],[0,-2]]],...extra};}

test('vertical clipping excludes low actors below a sloped source roof',()=>{
 const m=model([[[0,0,-2],[10,10,-2],[10,10,2]]]);
 assert.equal(modelSurfaceCollision(m,9,0,0,1,.55),false);
 assert.equal(modelSurfaceCollision(m,9,0,8,10,.55),true);
 assert.equal(modelSurfaceCollision(m,9,0,11,12,.55),false);
});
test('vertical wall cylinder contact and exact zero-radius contact survive degenerate projection',()=>{
 const m=model([[[5,0,-3],[5,8,-3],[5,8,3]],[[5,0,-3],[5,8,3],[5,0,3]]]);
 assert.equal(modelSurfaceCollision(m,4.5,0,1,2,.55),true);
 assert.equal(modelSurfaceCollision(m,4.4,0,1,2,.55),false);
 assert.equal(modelSurfaceCollision(m,5,0,1,2,0),true);
});
test('indexed triangles and negative world cells match non-indexed geometry',()=>{
 const p=triangle.map(([x,y,z])=>[x-30600,y,z+3600]);
 const a=model([p]),b={position:p.flat(),index:[0,1,2]};
 for(const x of [-30602,-30601,-30600,-30599,-30598])for(const z of [3598,3599,3600,3601,3602])assert.equal(modelSurfaceCollision(a,x,z,1,5,.4),modelSurfaceCollision(b,x,z,1,5,.4));
});
test('large source triangles and large query radii use bounded-index fallback',()=>{
 const m=model([[[-1000,5,-1000],[1000,5,-1000],[0,5,1000]]]);
 assert.equal(modelSurfaceCollision(m,0,0,4,6,.55),true);
 assert.equal(modelSurfaceCollision(m,0,0,0,2,1000),false);
 assert.equal(modelSurfaceCollision(m,1100,0,4,6,1100),true);
});
test('source footprint retains solid interiors while empty corners beside rotated models remain clear',()=>{
 const b=building({modelGeometry:model([[[0,0,-2.2],[2.2,0,0],[0,10,-2.2]],[[-2.2,0,0],[0,0,2.2],[0,10,2.2]],[[0,10,-2.2],[2.2,10,0],[0,10,2.2]],[[0,10,-2.2],[0,10,2.2],[-2.2,10,0]]])}),saved=JSON.stringify(b),index=new BuildingIndex([b]);
 assert.equal(index.collision(1.9,1.9,1,2,.1),null,'old AABB would close this street corner');
 assert.equal(index.collision(0,0,1,2,.1),b,'solid sourced building interior remains blocked');
 assert.equal(JSON.stringify(b),saved,'source geometry/elevations stay immutable');
});
test('true walls outside the footprint block movement and overhead roofs only block their own elevation',()=>{
 const wall=building({modelGeometry:model([[[5,0,-3],[5,8,-3],[5,8,3]],[[5,0,-3],[5,8,3],[5,0,3]],[[4,0,-3],[5,0,-3],[5,0,3]]])});
 assert.equal(new BuildingIndex([wall]).collision(4.5,0,1,2,.55),wall);
 const roof=building({modelGeometry:model([[[3,8,-3],[7,10,-3],[7,10,3]],[[3,8,-3],[7,10,3],[3,8,3]]])});
 const index=new BuildingIndex([roof]);assert.equal(index.collision(5,0,1,3,.55),null);assert.equal(index.collision(5,0,8,10,.55),roof);
});
test('open-sided structures keep their existing roof/posts and do not acquire closed mesh walls',()=>{
 const b=building({structureType:'Open-sided Structure',modelGeometry:model([[[5,0,-3],[5,8,-3],[5,8,3]],[[5,0,-3],[5,8,3],[5,0,3]],[[4,0,-3],[5,0,-3],[5,0,3]]])});
 assert.ok(describeBuilding(b).parts.every(p=>p.kind==='roof'||p.kind==='post'));
 assert.equal(new BuildingIndex([b]).collision(4.5,0,1,2,.55),null);
});
test('invalid actor spans never create contacts',()=>{
 const m=model([triangle]);
 for(const args of [[0,0,1,1,0],[0,0,2,1,0],[NaN,0,0,5,1],[0,0,0,5,-1]])assert.equal(modelSurfaceCollision(m,...args),false);
});

test('aircraft roof envelope includes the actual model top and retains a taller outline fallback',()=>{
 const source=model([[[0,2,-2],[2,2,0],[0,18,-2]],[[-2,2,0],[0,2,2],[0,18,2]]]);
 const short=building({base:2,height:4,modelGeometry:source}),saved=JSON.stringify(short);
 assert.equal(new BuildingIndex([short]).maximumRoof(0,0,2),18);
 assert.equal(JSON.stringify(short),saved);
 const tall=building({base:2,height:24,modelGeometry:source});assert.equal(new BuildingIndex([tall]).maximumRoof(0,0,2),26);
 const malformed=building({base:NaN,height:NaN});assert.equal(new BuildingIndex([malformed]).maximumRoof(0,0,2),0);
});

// Closed source prisms, including bottom faces, exercise real interior occupancy.
function prism(x0,z0,x1,z1,top,bottom=0){
 const q=[[x0,bottom,z0],[x1,bottom,z0],[x1,bottom,z1],[x0,bottom,z1],[x0,top,z0],[x1,top,z0],[x1,top,z1],[x0,top,z1]];
 return [[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]].map(t=>t.map(i=>q[i]));
}
function nativeBuilding(triangles){return building({rings:[[[-10,-10],[10,-10],[10,10],[-10,10],[-10,-10]]],modelGeometry:model(triangles)});}
test('native low wings retain solid rooms and physical roofs without the tall-wing ghost volume',()=>{
 const b=nativeBuilding([...prism(-8,-5,0,5,8),...prism(0,-5,8,5,40)]),idx=new BuildingIndex([b]);
 assert.equal(idx.collision(-4,0,3,5,.3),b,'closed low wing interior');
 assert.equal(idx.collision(-4,0,7.9,8.1,.3),b,'aircraft touches the actual low roof');
 assert.equal(idx.collision(-4,0,9,10,.3),null,'clear air above low roof, below global top');
 assert.equal(idx.collision(4,0,30,32,.3),b,'closed tall wing interior');
 assert.equal(idx.collision(4,0,39.9,40.1,.3),b,'actual tall roof');
 assert.equal(modelRoofHeight(b.modelGeometry,-4,0),8);
 assert.equal(modelRoofHeight(b.modelGeometry,4,0),40);
});
test('native courtyard and disconnected shell gap remain clear despite a filled survey footprint',()=>{
 const b=nativeBuilding([...prism(-8,-8,-3,8,20),...prism(3,-8,8,8,25),...prism(-3,3,3,8,10)]),idx=new BuildingIndex([b]);
 assert.equal(modelRoofHeight(b.modelGeometry,0,0),null);
 assert.equal(idx.collision(0,0,1,3,.5),null);
 assert.equal(idx.collision(0,0,15,17,.5),null);
 assert.equal(idx.collision(-2.7,0,1,3,.5),b,'real courtyard wall retains radius collision');
 assert.equal(idx.collision(-2.4,0,1,3,.5),null);
 assert.equal(idx.collision(0,5,1,3,.5),b,'covered rear wing retains interior');
});
test('local roof heights interpolate slopes without filling uncovered triangle corners',()=>{
 const m=model([[[0,2,0],[8,10,0],[8,10,8]],[[0,2,0],[8,10,8],[0,2,8]]]);
 assert.equal(modelRoofHeight(m,2,4),4);assert.equal(modelRoofHeight(m,6,4),8);
 assert.equal(modelRoofHeight(m,9,4),null);assert.equal(modelRoofHeight(m,NaN,4),null);
 const indexed={position:[0,2,0,8,10,0,8,10,8,0,2,8],index:[0,1,2,0,2,3]};
 assert.equal(modelRoofHeight(indexed,2,4),4);
 const triangleOnly=model([[[0,2,0],[8,10,0],[8,10,8]]]);assert.equal(modelRoofHeight(triangleOnly,1,7),null);
});
test('vertical walls alone do not invent a local roof or closed interior',()=>{
 const b=nativeBuilding([[[0,0,-3],[0,30,-3],[0,30,3]],[[0,0,-3],[0,30,3],[0,0,3]],[[2,0,-3],[2,30,-3],[2,30,3]]]),idx=new BuildingIndex([b]);
 assert.equal(modelRoofHeight(b.modelGeometry,0,0),null);
 assert.equal(idx.collision(1,0,2,3,.1),null,'two open wall fragments do not enclose a room');
 assert.equal(idx.collision(0,0,2,3,0),b,'real wall remains solid');
});
test('large source faces and negative cells retain local roof queries',()=>{
 const m=model([[[-1000,5,-1000],[1000,5,-1000],[0,5,1000]]]);assert.equal(modelRoofHeight(m,0,0),5);assert.equal(modelRoofHeight(m,1000,1000),null);
 const shifted=model(prism(-30608,3592,-30592,3608,23));assert.equal(modelRoofHeight(shifted,-30600,3600),23);
});
