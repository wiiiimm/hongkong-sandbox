import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {RegionalDetail,surfaceGeometry} from '../regional.js';
import {validateRegionalPackage,regionalPlaceMatches} from '../regional-data.js';
const square=(id,x=0,kind='plaza')=>({id,kind,source:'https://www.openstreetmap.org/way/1',rings:[[[x,0],[x+40,0],[x+40,40],[x,40],[x,0]]]});
const pack=surfaces=>({schemaVersion:1,places:[],surfaces,sections:[]});
test('surface triangulation preserves holes and has upward-facing normals',()=>{
 const surface=square('hole');surface.rings.push([[10,10],[10,30],[30,30],[30,10],[10,10]]);
 const geometry=surfaceGeometry(surface,{height:()=>5}),p=geometry.attributes.position,n=geometry.attributes.normal;
 let area=0;
 for(let i=0;i<p.count;i+=3){
  const x=(p.getX(i)+p.getX(i+1)+p.getX(i+2))/3,z=(p.getZ(i)+p.getZ(i+1)+p.getZ(i+2))/3;
  assert.ok(!(x>10&&x<30&&z>10&&z<30),'hole must remain empty');
  area+=Math.abs((p.getX(i+1)-p.getX(i))*(p.getZ(i+2)-p.getZ(i))-(p.getX(i+2)-p.getX(i))*(p.getZ(i+1)-p.getZ(i)))/2;
  assert.ok(n.getY(i)>.99,'surface should face the sky');assert.ok(Math.abs(p.getY(i)-5.26)<1e-5);
 }
 assert.ok(Math.abs(area-1200)<.01);geometry.dispose();
});
test('draped detail samples terrain within large polygons, not just at corners',()=>{
 const geometry=surfaceGeometry(square('slope'),{height:(x,z)=>x*.1+z*.2}),p=geometry.attributes.position;
 assert.ok(p.count>6);for(let i=0;i<p.count;i++)assert.ok(Math.abs(p.getY(i)-(p.getX(i)*.1+p.getZ(i)*.2+.26))<1e-5);geometry.dispose();
});
test('invalid, unsupported or unsourced geometry is rejected before caching',()=>{
 assert.throws(()=>validateRegionalPackage(pack([{...square('bad'),source:null}])));
 assert.throws(()=>validateRegionalPackage(pack([{...square('bad'),kind:'invented'}])));
 assert.throws(()=>validateRegionalPackage(pack([{...square('bad'),rings:[[[0,0],[1,0],[1,1],[0,1]]]}])));
 assert.throws(()=>validateRegionalPackage(pack([square('duplicate'),square('duplicate')])));
 assert.equal(validateRegionalPackage(pack([square('valid')])).surfaces.length,1);
});
test('regional search accepts section references and bilingual names',()=>{
 const places={a:{title:'Mui Wo',zh:'梅窩',region:'lantau',sectionId:'10.6'},b:{title:'Central',zh:'中環',region:'island'}};
 assert.equal(regionalPlaceMatches(places,'10.6')[0][0],'a');assert.equal(regionalPlaceMatches(places,'梅窩')[0][0],'a');
 assert.equal(regionalPlaceMatches(places,'central','lantau').length,0);
});
test('surface loading retries failed packages, deduplicates seams, and bounds live geometry',async()=>{
 const previous=globalThis.fetch,scene=new THREE.Scene(),detail=new RegionalDetail({scene,sampler:{height:()=>2}});let calls=0;
 globalThis.fetch=async()=>{calls++;if(calls===1)return {ok:false,status:503};return {ok:true,json:async()=>pack(Array.from({length:35},(_,i)=>square('surface'+i,i*1800)))};};
 try{
  await detail.load('regions.json');assert.equal(detail.stats.errors.length,1);assert.equal(detail.stats.surfaces,0);
  await detail.retry();assert.equal(detail.stats.errors.length,0);assert.equal(detail.stats.packages,1);assert.equal(detail.stats.surfaces,35);
  let disposed=0;for(const group of detail.cache.values())group.traverse(o=>o.geometry?.addEventListener('dispose',()=>disposed++));
  detail.plan(50000,0,5000);assert.ok(disposed>0,'distant geometry should be released');assert.ok(detail.stats.tiles<=24);
  await detail.load('overlap.json');assert.equal(detail.stats.surfaces,35,'shared source geometry must appear once');
  assert.equal(detail.stats.pending,0);
 }finally{globalThis.fetch=previous;detail.dispose();assert.equal(scene.children.length,0);}
});

test('a late regional response cannot rebuild geometry after disposal',async()=>{
 const previous=globalThis.fetch;let finish;globalThis.fetch=()=>new Promise(resolve=>{finish=resolve;});
 const scene=new THREE.Scene(),detail=new RegionalDetail({scene,sampler:{height:()=>1}});
 try{const pending=detail.load('late.json');detail.dispose();finish({ok:true,json:async()=>pack([square('late')])});await pending;detail.plan(0,0);assert.equal(detail.stats.surfaces,0);assert.equal(detail.stats.tiles,0);assert.equal(scene.children.length,0);}finally{globalThis.fetch=previous;}
});
