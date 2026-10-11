import test from 'node:test';
import assert from 'node:assert/strict';
import {TerrainPatchIndex,terrainGridBounds} from '../terrain-patch-index.js';
import {makeTerrainSampler,ORIGIN} from '../geo.js';

test('hundreds of overlapping rectangles match ordered exhaustive lookup at edges and random points',()=>{
 const entries=Array.from({length:600},(_,i)=>({value:i,bounds:[(i%30)*10-150,Math.floor(i/30)*10-100,(i%30)*10-138,Math.floor(i/30)*10-88]}));
 entries.unshift({value:'wide',bounds:[-200,-200,200,200]});
 const index=new TerrainPatchIndex(entries),points=entries.flatMap(({bounds:[a,b,c,d]})=>[[a,b],[c,d],[(a+c)/2,(b+d)/2]]);
 let seed=17;for(let i=0;i<500;i++){seed=(Math.imul(seed,1664525)+1013904223)>>>0;const x=seed/2**32*450-225;seed=(Math.imul(seed,1664525)+1013904223)>>>0;points.push([x,seed/2**32*450-225]);}
 for(const [x,z] of points)assert.deepEqual(index.query(x,z),entries.filter(({bounds:b})=>x>=b[0]&&z>=b[1]&&x<=b[2]&&z<=b[3]).map(e=>e.value));
});

test('unknown bounds remain candidates and retain their source order',()=>{
 const index=new TerrainPatchIndex([{value:'unknown',bounds:null},{value:'near',bounds:[0,0,1,1]},{value:'nonfinite',bounds:[0,0,Infinity,1]}]);
 assert.deepEqual(index.query(.5,.5),['unknown','near','nonfinite']);assert.deepEqual(index.query(30,30),['unknown','nonfinite']);
});

function grid(x,z,stepX,stepZ,height,w=3,h=3){return {w,h,elev:Array(w*h).fill(height),meta:{georef:{aE:stepX,aN:-stepZ,bE:ORIGIN[0]+x,bN:ORIGIN[1]-z}}};}

test('grid bounds cover inverse-transform membership for reversed axes and fractional edges',()=>{
 for(const stepX of [-.1,5])for(const stepZ of [-.3,7]){
  const data=grid(36.12345678,-21.12345678,stepX,stepZ,8),sampler=makeTerrainSampler(data),bounds=terrainGridBounds(data,ORIGIN);
  for(const c of [0,.00000001,.5,1,1.99999999,2])for(const r of [0,.00000001,.5,1,1.99999999,2]){
   const x=data.meta.georef.bE-ORIGIN[0]+c*stepX,z=ORIGIN[1]-data.meta.georef.bN+r*stepZ;
   if(sampler.contains(x,z))assert(x>=bounds[0]&&x<=bounds[2]&&z>=bounds[1]&&z<=bounds[3]);
  }
 }
});

test('many siblings preserve top rendered height while raw height and resolution retain source order',()=>{
 const root=grid(-1000,-1000,1000,1000,2,4,4),low=grid(0,0,5,5,5),high=grid(2,2,1,1,12),nested=grid(3,3,.5,.5,18);
 high.patches=[nested];root.patches=[low,high,...Array.from({length:100},(_,i)=>grid(100+i*20,100,5,5,4))];
 const sampler=makeTerrainSampler(root);
 for(const [x,z,height,raw,resolution] of [[3.2,3.3,18,5,5],[2.2,2.3,12,5,5],[8,8,5,5,5],[40,40,2,2,1000],[102,102,4,4,5]]){
  assert.equal(sampler.height(x,z),height);assert.equal(sampler.raw(x,z),raw);assert.equal(sampler.resolutionAt(x,z),resolution);
 }
});
