import test from 'node:test';
import assert from 'node:assert/strict';
import {drapeRoadTriangle} from '../road-surface.js';
const input=[[0,.18,0,0,0],[10,.18,0,10,0],[0,.18,10,0,1]];
test('planar terrain retains one triangle and UV values',()=>{
 const out=[];drapeRoadTriangle(input,{height:()=>0,resolutionAt:()=>70},t=>out.push(t));
 assert.deepEqual(out,[input]);
});
test('fine terrain hill is followed rather than crossed by a flat road triangle',()=>{
 const sampler={height:(x,z)=>Math.max(0,2-Math.abs(x-3)-Math.abs(z-3)),resolutionAt:()=>1};
 const out=[];drapeRoadTriangle(input,sampler,t=>out.push(t));assert(out.length>1&&out.length<=4096);
 let minimum=Infinity;
 for(const t of out)for(let i=0;i<=5;i++)for(let j=0;j<=5-i;j++){
  const weights=[i/5,j/5,1-(i+j)/5],p=[0,1,2].map(k=>t.reduce((s,v,n)=>s+weights[n]*v[k],0));
  minimum=Math.min(minimum,p[1]-sampler.height(p[0],p[2]));
 }
 assert(minimum>0,'No sampled triangle interior goes below terrain: '+minimum);
 for(const t of out)for(const p of t){assert(Math.abs(p[3]-p[0])<1e-9);assert(Math.abs(p[4]-p[2]/10)<1e-9);}
});
