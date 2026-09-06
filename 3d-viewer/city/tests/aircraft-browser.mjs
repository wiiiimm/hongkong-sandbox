import {chromium} from 'playwright';
import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
try{
 const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 const base=new URL(process.env.CITY_URL||'http://127.0.0.1:4176/city.html');await page.route('**/aircraft-fixture.html',r=>r.fulfill({contentType:'text/html',body:'<!doctype html><title>Aircraft verification</title>'}));await page.goto(base.origin+'/aircraft-fixture.html');
 const report=await page.evaluate(async()=>{
  const THREE=await import('/vendor/three.module.js'),{AIRCRAFT,AircraftModel}=await import('/city/aircraft.js');
  const scene=new THREE.Scene(),target=new THREE.Group();scene.add(target);scene.background=new THREE.Color('#ccdce0');scene.fog=new THREE.FogExp2('#ccdce0',.000065);scene.add(new THREE.HemisphereLight('#edf5ff','#607068',2));const sun=new THREE.DirectionalLight('#fff1da',3);sun.position.set(-100,200,-100);scene.add(sun);
  const camera=new THREE.PerspectiveCamera(40,1.5,.5,100000),renderer=new THREE.WebGLRenderer({logarithmicDepthBuffer:true});renderer.setSize(600,400);renderer.toneMapping=THREE.ACESFilmicToneMapping;
  const model=new AircraftModel({target}),records=[];
  for(const definition of AIRCRAFT){
   const ok=await model.setAircraft(definition.id);if(!ok)throw new Error(model.state.error);
   const data=model.current.userData.aircraft,box=new THREE.Box3();model.current.updateMatrixWorld(true);
   model.current.traverse(o=>{if(o.isMesh&&!data.lights.includes(o))box.expandByObject(o,true);});const dimensions=box.getSize(new THREE.Vector3());
   const extent=Math.max(definition.length,definition.wingspan);camera.position.set(extent*.8,extent*.5,-extent);camera.lookAt(0,0,0);model.update(.1);renderer.render(scene,camera);
   const daytimeReflections=data.materials.map(m=>m.envMapIntensity),angles=data.spinners.map(p=>p.rotation.z);model.setLighting({night:1,reducedMotion:true});model.update(.1);renderer.render(scene,camera);
   const record={...model.state,measured:{length:dimensions.z,wingspan:dimensions.x},drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,hiddenGear:data.gearMeshes.every(m=>!m.visible),propsSteady:data.spinners.every((p,i)=>p.rotation.z===angles[i]),daytimeReflections,nightReflections:data.materials.map(m=>m.envMapIntensity),portLight:data.lights.find(m=>m.name.startsWith('Port'))?.position.x,starboardLight:data.lights.find(m=>m.name.startsWith('Starboard'))?.position.x};records.push(record);model.setLighting({night:0,reducedMotion:false});
  }
  const memoryBeforeSecondPass={...renderer.info.memory};for(const d of AIRCRAFT){await model.setAircraft(d.id);model.update(.1);renderer.render(scene,camera);}const memoryAfterSecondPass={...renderer.info.memory};model.dispose();renderer.render(scene,camera);const memoryAfterDispose={...renderer.info.memory};renderer.dispose();return {records,memoryBeforeSecondPass,memoryAfterSecondPass,memoryAfterDispose};
 });
 for(const row of report.records){assert.equal(row.status,'ready');assert.ok(Math.abs(row.measured.length-row.dimensions.length)<.005,row.id+' length');assert.ok(Math.abs(row.measured.wingspan-row.dimensions.wingspan)<.005,row.id+' span');assert.equal(row.hiddenGear,true);assert.equal(row.propsSteady,true);assert.ok(row.drawCalls<35,row.id+' draw budget');if(row.id!=='ufo'){assert.ok(row.portLight<0);assert.ok(row.starboardLight>0);}assert.ok(row.nightReflections.every((v,i)=>v<=row.daytimeReflections[i]));}
 assert.ok(report.memoryAfterSecondPass.geometries<=report.memoryBeforeSecondPass.geometries+1,'repeated switching does not leak geometry');assert.ok(report.memoryAfterSecondPass.textures<=report.memoryBeforeSecondPass.textures+1,'repeated switching does not leak textures');
 assert.equal(report.records.find(r=>r.id==='betsy').spinners,2);assert.equal(report.records.find(r=>r.id==='betsy').hiddenVariants,8);assert.ok(report.records.find(r=>r.id==='cx777').drawMeshes<25);assert.deepEqual(errors,[]);
 await writeFile(new URL('../../../docs/astra-city/aircraft/verification.json',import.meta.url),JSON.stringify({...report,errors,result:'passed'},null,2)+'\n');console.log(JSON.stringify({...report,errors,result:'passed'},null,2));
}finally{await browser.close();}
