import test from 'node:test';import assert from 'node:assert/strict';
import {retainOutsideInset} from './retained_terrain_inset_clip_v1.mjs';
import {clipParentTriangle} from './clip_parent_terrain_triangle_v1.mjs';
const area=f=>{const u=f[1].map((v,j)=>v-f[0][j]),v=f[2].map((v,j)=>v-f[0][j]);return Math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])/2;};
const sum=fs=>fs.reduce((n,f)=>n+area(f),0),domain=[0,0,10,10],cut=[3,3,7,7];
test('sloping source plane and complete area survive the partition',()=>{const f=[[0,2,0],[10,12,0],[0,22,10]],old=structuredClone(f),out=retainOutsideInset(f,domain,cut),inside=clipParentTriangle(f,cut);assert(Math.abs(sum(out)+sum(inside)-area(f))<1e-10);for(const tri of out)for(const [x,y,z]of tri)assert(Math.abs(y-(2+x+2*z))<1e-10);assert.deepEqual(f,old);});
test('vertical source crossing cut preserves exact outside plus inside area',()=>{const f=[[5,0,0],[5,10,0],[5,10,10]],out=retainOutsideInset(f,domain,cut);assert(Math.abs(sum(out)+sum(clipParentTriangle(f,cut))-area(f))<1e-10);});
test('boundary-only vertical facet retained exactly once',()=>{const f=[[3,0,0],[3,10,0],[3,10,10]];const out=retainOutsideInset(f,domain,cut);assert.equal(out.length,1);assert.equal(out[0],f);});
test('outside and inside source facets retain correct ownership',()=>{const outside=[[0,0,0],[2,0,0],[0,0,2]],inside=[[4,0,4],[6,0,4],[4,0,6]];assert.equal(retainOutsideInset(outside,domain,cut)[0],outside);assert.deepEqual(retainOutsideInset(inside,domain,cut),[]);});
