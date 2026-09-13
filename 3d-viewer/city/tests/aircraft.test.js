import test from 'node:test';
import assert from 'node:assert/strict';
import {access} from 'node:fs/promises';
import * as THREE from '../../vendor/three.module.js';
import {AIRCRAFT,AircraftModel,prepareAircraft,disposeAircraft} from '../aircraft.js';
import {aircraftChaseDistance} from '../navigation.js';
const cube=()=>{const scene=new THREE.Group(),material=new THREE.MeshStandardMaterial({name:'paint'});scene.add(new THREE.Mesh(new THREE.BoxGeometry(10,3,12),material));return {scene};};
const prepare=(gltf,id)=>prepareAircraft(gltf,id,{reflections:false});

test('every original fleet option has a bundled model, provenance and explicit dimensions',async()=>{
 assert.deepEqual(AIRCRAFT.map(a=>a.id),['prop','betsy','cx747','cx777','a330','a350','ufo']);
 for(const a of AIRCRAFT){await access(new URL('../../data/models/'+a.file,import.meta.url));assert.ok(a.length>0&&a.wingspan>0&&a.credit&&a.licence&&a.source);if(a.nonCommercial)assert.ok(a.file.startsWith('nc/'));if(!a.approximate)assert.ok(a.dimensionSource);}
});
test('each source orientation becomes nose-forward in the shared negative-z flight frame',()=>{
 for(const d of AIRCRAFT.filter(a=>a.kind!=='ufo')){
  const gltf=cube(),nose=new THREE.Mesh(new THREE.SphereGeometry(.4,8,6),new THREE.MeshStandardMaterial({name:'nose-marker'}));
  const authorForward={prop:[0,0,-1],betsy:[0,0,1],cx747:[0,0,1],cx777:[-1,0,0],a330:[0,0,1],a350:[1,0,0]}[d.id];nose.position.fromArray(authorForward).multiplyScalar(9);gltf.scene.add(nose);
  const result=prepare(gltf,d.id),marker=result.getObjectByName('nose-marker'),z=new THREE.Box3().setFromObject(marker).getCenter(new THREE.Vector3()).z;assert.ok(z<0,d.id+' must face forward');disposeAircraft(result);
 }
});
test('paint and tyres sharing a source material are separated before calibration',()=>{
 const gltf=cube(),shared=gltf.scene.children[0].material,tire=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),shared);tire.name='l_tire_still';tire.position.y=-3;gltf.scene.add(tire);
 const root=prepare(gltf,'betsy'),materials=root.userData.aircraft.materials;assert.ok(materials.some(m=>m.metalness>.5));assert.ok(materials.some(m=>m.roughness>.7));disposeAircraft(root);
});
test('late loads cannot replace the latest selection and cancelled assets are disposed',async()=>{
 const requests=[];const loader={loadAsync:()=>new Promise(resolve=>requests.push(resolve))};const controller=new AircraftModel({target:new THREE.Group(),loader,prepare});
 const first=controller.setAircraft('cx747'),second=controller.setAircraft('cx777'),late=cube();let freed=0;late.scene.children[0].geometry.addEventListener('dispose',()=>freed++);
 requests[1](cube());assert.equal(await second,true);requests[0](late);assert.equal(await first,false);assert.equal(controller.state.id,'cx777');assert.equal(controller.state.status,'ready');assert.equal(freed,1);controller.dispose();
});
test('failed aircraft loads retain a correctly identified usable fallback and permit retry',async()=>{
 let fail=true;const controller=new AircraftModel({target:new THREE.Group(),loader:{loadAsync:async()=>{if(fail)throw new Error('Offline');return cube();}},prepare});
 assert.equal(await controller.setAircraft('a330'),false);assert.equal(controller.state.status,'fallback');assert.equal(controller.state.id,'a330');assert.match(controller.state.error,/simplified/);assert.ok(controller.current.children.length);
 fail=false;assert.equal(await controller.setAircraft('a330'),true);assert.equal(controller.state.status,'ready');controller.dispose();
});
test('disposing during a load releases the late model and cannot resurrect the aircraft',async()=>{
 let resolve;const target=new THREE.Group(),controller=new AircraftModel({target,loader:{loadAsync:()=>new Promise(r=>resolve=r)},prepare});const pending=controller.setAircraft('a350');controller.dispose();resolve(cube());assert.equal(await pending,false);assert.equal(target.children.length,0);
});
test('reduced motion holds propeller angle while night lowers simulated reflections',async()=>{
 const gltf=cube();gltf.scene.children[0].name='Propeller_Cone';const controller=new AircraftModel({target:new THREE.Group(),loader:{loadAsync:async()=>gltf},prepare});await controller.setAircraft('prop');controller.update(.1);const prop=controller.current.userData.aircraft.spinners[0],angle=prop.rotation.z;controller.setLighting({night:1,reducedMotion:true});controller.update(.1);assert.equal(prop.rotation.z,angle);assert.ok(controller.current.userData.aircraft.materials[0].envMapIntensity<.1);controller.dispose();
});

test('chase camera fits portrait aircraft across view angles and preserves default desktop distance',()=>{
 for(const definition of AIRCRAFT){
  const extent=Math.max(definition.length,definition.wingspan);
  for(const aspect of [1440/900,390/844,320/844]){
   const camera=new THREE.PerspectiveCamera(52,aspect,.5,100000);
   for(const yaw of [0,Math.PI/4,Math.PI/2]){
    const distance=aircraftChaseDistance(definition,camera,yaw),direction=new THREE.Vector3(Math.sin(yaw),0,-Math.cos(yaw));
    camera.position.copy(direction).multiplyScalar(-distance);camera.position.y=Math.max(13,extent*.37);
    const target=direction.clone().multiplyScalar(Math.max(80,extent*1.7));target.y=-.65*Math.max(45,extent*.65);
    camera.lookAt(target);camera.updateMatrixWorld();
    for(const x of [-definition.wingspan/2,definition.wingspan/2])for(const z of [-definition.length/2,definition.length/2]){
     const point=new THREE.Vector3(x,0,z).project(camera);assert.ok(Math.abs(point.x)<.9,`${definition.id} aspect ${aspect} yaw ${yaw}: x=${point.x}`);
    }
    if(aspect>1&&yaw===0)assert.equal(distance,Math.max(48,extent*1.55));
   }
  }
 }
});
