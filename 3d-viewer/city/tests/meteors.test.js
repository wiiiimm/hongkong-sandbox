import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {createMeteorTrails,meteorGap,meteorCap,meteorRateLabel,METEOR_DEFAULTS,METEOR_N,METEOR_POOL} from '../../meteor-trails.js';
import {createCityMeteors} from '../meteors.js';
const near=(a,b,e=1e-6)=>assert.ok(Math.abs(a-b)<e,`${a} ≈ ${b}`);
const random=seed=>()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
function city(t){const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(44,1,.5,100000),effect=createCityMeteors({scene,camera,random:random(85)});t.after(()=>effect.dispose());effect.setOptions({rate:1});return {scene,camera,effect,group:scene.children[0]};}

test('HKS-85 default, logarithmic pacing, concurrency and original label boundaries are retained',()=>{
 assert.deepEqual(METEOR_DEFAULTS,{enabled:true,rate:.18});assert.equal(METEOR_N,20);assert.equal(METEOR_POOL,14);
 near(meteorGap(0),30);near(meteorGap(.5),1.8973665961010275);near(meteorGap(1),.12);
 assert.deepEqual([0,.18,.5,1].map(meteorCap),[1,2,6,14]);
 assert.deepEqual([0,.001,.41999,.42,.81999,.82,1].map(meteorRateLabel),['Off','Calm','Calm','Romantic','Romantic','Apocalypse','Apocalypse']);
});

test('original north/up orientation, spherical tail, white-blue gradient and fade remain coherent',t=>{
 const values=[0,0,0,.8,.2,.8,.5,.5,.5],effect=createMeteorTrails({random:()=>values.shift()??.5,rate:.01});t.after(()=>effect.dispose());
 effect.step(0,{starFade:1,radius:82000});const mo=effect.pool.find(m=>m.active);assert.ok(mo);near(mo.A.x,0);near(mo.A.y,Math.sin(20*Math.PI/180));near(mo.A.z,-Math.cos(20*Math.PI/180));near(mo.A.length(),1);near(mo.B.length(),1);assert.ok(mo.B.y<mo.A.y);near(mo.dur,1);
 assert.equal(mo.line.material.opacity,0,'no previous-arc flash during birth');effect.step(.05,{starFade:1,radius:82000});near(mo.line.material.opacity,.2125);
 const p=mo.line.geometry.attributes.position,c=mo.line.geometry.attributes.color;assert.equal(p.count,20);assert.equal(c.count,20);assert.deepEqual([c.getX(0),c.getY(0),c.getZ(0)],[1,1,1]);assert.deepEqual([c.getX(19),c.getY(19),c.getZ(19)],[0,0,0]);
 for(let i=0;i<p.count;i++)near(Math.hypot(p.getX(i),p.getY(i),p.getZ(i)),82000,.015);
 const end=new THREE.Vector3().fromBufferAttribute(p,19);near(end.x,mo.A.x*82000,.01);near(end.z,mo.A.z*82000,.01);
 effect.step(1.2,{starFade:1,radius:82000});near(mo.line.material.opacity,.425);effect.step(1.401,{starFade:1,radius:82000});assert.equal(mo.active,false);assert.equal(mo.line.visible,false);
});

test('apocalypse reuses its fixed pool and buffers through many births',t=>{
 const effect=createMeteorTrails({random:random(168),rate:1});t.after(()=>effect.dispose());const objects=effect.pool.map(m=>[m.line,m.line.geometry,m.line.geometry.attributes.position.array,m.line.material]);let peak=0;
 for(let frame=0;frame<3600;frame++){effect.step(frame/60,{starFade:1,radius:80000});peak=Math.max(peak,effect.state.active);assert.ok(effect.state.active<=14);}
 assert.ok(effect.state.spawned>300);assert.ok(peak>=8);assert.equal(effect.group.children.length,14);
 effect.pool.forEach((m,i)=>[m.line,m.line.geometry,m.line.geometry.attributes.position.array,m.line.material].forEach((object,j)=>assert.equal(object,objects[i][j])));
});

test('daylight/cloud wash, off and zero rate clear trails and reschedule without backlog',t=>{
 const effect=createMeteorTrails({random:random(85),rate:1});t.after(()=>effect.dispose());for(let i=0;i<120;i++)effect.step(i/60,{starFade:1});assert.ok(effect.state.active>0);
 effect.step(2,{starFade:.549});assert.equal(effect.state.active,0);assert.equal(effect.state.visibleTrails,0);const births=effect.state.spawned;effect.step(100000,{starFade:0});assert.equal(effect.state.spawned,births);
 effect.setOptions({enabled:false});effect.step(200000,{starFade:1});assert.equal(effect.state.active,0);effect.setOptions({enabled:true,rate:0});effect.step(300000,{starFade:1});assert.equal(effect.state.active,0);
 effect.setOptions({rate:.18});effect.step(400000,{starFade:1});assert.equal(effect.state.spawned,births);assert.equal(effect.state.rateLabel,'Calm');
});

test('city uses the current camera position and world horizontal axes without fog or duplicate resources',t=>{
 const {effect,camera,group}=city(t);camera.position.set(1200,340,-700);for(let i=0;i<120;i++)effect.update(1/60,{starFade:1});assert.deepEqual(group.position.toArray(),camera.position.toArray());near(effect.state.radius,80360);
 const arrays=group.children.map(line=>line.geometry.attributes.position.array.slice());camera.position.set(-30000,1500,4500);camera.lookAt(5000,3000,4000);effect.update(0,{starFade:1});assert.deepEqual(group.position.toArray(),camera.position.toArray());assert.deepEqual(group.quaternion.toArray(),[0,0,0,1]);
 group.children.forEach((line,i)=>{assert.equal(line.material.fog,false);assert.equal(line.material.depthTest,true);assert.equal(line.material.depthWrite,false);assert.deepEqual(line.geometry.attributes.position.array,arrays[i]);});
 camera.far=50000;effect.update(0,{starFade:1});near(effect.state.radius,40180);assert.ok(effect.state.radius<camera.far);
});

test('pause and reduced motion preserve settings, stop time and cannot accumulate a resumed storm',t=>{
 const {effect,group}=city(t);for(let i=0;i<120;i++)effect.update(1/60,{starFade:1});const before=effect.state,positions=group.children.map(line=>line.geometry.attributes.position.array.slice());assert.ok(before.active>0);
 effect.update(3600,{starFade:1,paused:true});near(effect.state.elapsed,before.elapsed);assert.equal(effect.state.spawned,before.spawned);assert.equal(effect.state.running,false);assert.equal(effect.state.visibleTrails,0);group.children.forEach((line,i)=>assert.deepEqual(line.geometry.attributes.position.array,positions[i]));
 effect.update(1/60,{starFade:1});near(effect.state.elapsed,before.elapsed+1/60);assert.ok(effect.state.spawned-before.spawned<=1);assert.equal(effect.state.running,true);
 effect.update(3600,{starFade:1,reducedMotion:true});assert.equal(effect.state.active,0);assert.equal(effect.state.visibleTrails,0);assert.equal(effect.state.enabled,true);assert.equal(effect.state.rate,1);const elapsed=effect.state.elapsed,births=effect.state.spawned;
 effect.update(3600,{starFade:1});near(effect.state.elapsed,elapsed+.1);assert.ok(effect.state.spawned-births<=1);assert.equal(group.children.length,14);
});

test('options remain finite, and disposal is idempotent with no late reattachment',t=>{
 const {effect,scene,group}=city(t);let geometries=0,materials=0;for(const line of group.children){line.geometry.addEventListener('dispose',()=>geometries++);line.material.addEventListener('dispose',()=>materials++);}
 effect.setOptions({rate:NaN});assert.equal(effect.state.rate,1);effect.setOptions({rate:-3});assert.equal(effect.state.rate,0);effect.setOptions({rate:8});assert.equal(effect.state.rate,1);
 effect.update(Infinity,{starFade:NaN});assert.equal(effect.state.elapsed,0);assert.equal(effect.state.active,0);effect.dispose();effect.dispose();effect.setOptions({rate:.18});effect.update(1,{starFade:1});assert.equal(scene.children.length,0);assert.equal(geometries,14);assert.equal(materials,14);assert.equal(effect.state.disposed,true);assert.equal(effect.state.running,false);
});
