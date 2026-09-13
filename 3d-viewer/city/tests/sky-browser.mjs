import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';

const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:900,height:640}}),errors=[];
page.on('pageerror',error=>errors.push(error.message));page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
try{
 const base=new URL(process.env.CITY_URL||'http://127.0.0.1:4176/city.html');
 await page.route('**/sky-fixture.html',route=>route.fulfill({contentType:'text/html',body:'<!doctype html><title>Sky renderer verification</title><style>body{margin:0;background:#000}</style>'}));
 await page.goto(base.origin+'/sky-fixture.html');
 const result=await page.evaluate(async()=>{
  const THREE=await import('/vendor/three.module.js'),{createSky}=await import('/city/sky.js'),{dateFromHKT,getSkyState,horizontalDirection}=await import('/city/sky-time.js'),{starPosition}=await import('/vendor/astro.js');
  const scene=new THREE.Scene();scene.background=new THREE.Color('#000000');scene.fog=new THREE.Fog('#ff0000',1,2);
  const camera=new THREE.PerspectiveCamera(60,900/640,.5,100000);camera.position.set(12345,350,6789);
  const renderer=new THREE.WebGLRenderer({antialias:true,logarithmicDepthBuffer:true,preserveDrawingBuffer:true});renderer.setSize(900,640);document.body.append(renderer.domElement);
  const sky=await createSky({scene,camera}),date=dateFromHKT('2026-09-06',21),vega=starPosition(date,22.3,114.17,18.6156*Math.PI/12,38.784*Math.PI/180),view=horizontalDirection(vega.azimuth,vega.altitude);
  const look=()=>{camera.lookAt(camera.position.clone().add(new THREE.Vector3().copy(view).multiplyScalar(100)));camera.updateMatrixWorld();};look();
  const target=new THREE.WebGLRenderTarget(900,640),read=()=>{renderer.setRenderTarget(target);renderer.render(scene,camera);const pixels=new Uint8Array(900*640*4);renderer.readRenderTargetPixels(target,0,0,900,640,pixels);return pixels;};
  const stats=pixels=>{let lit=0,total=0;for(let i=0;i<pixels.length;i+=4){total+=pixels[i]+pixels[i+1]+pixels[i+2];if(pixels[i]+pixels[i+1]+pixels[i+2]>70)lit++;}return {lit,total};};
  sky.update({date,stargazing:true});const clear=stats(read()),picked=sky.pick({x:0,y:0}),initialUpdates=sky.state.coordinateUpdates;
  sky.update({date:new Date(date.getTime()+1000),stargazing:true});const cached=sky.state.coordinateUpdates===initialUpdates;
  const selected=sky.state.selected;sky.setSelectedConstellation(null);sky.setConstellations(true);const figures=stats(read());sky.setConstellations(false);
  camera.position.add(new THREE.Vector3(19000,1800,-12000));look();sky.update({date,stargazing:true});const translated=stats(read());
  sky.update({date,stargazing:false,cloudCover:0});const city=stats(read());
  sky.update({date,stargazing:false,cloudCover:1});const overcast=stats(read());
  sky.update({date:dateFromHKT('2026-09-06',12),stargazing:false});const day={...stats(read()),visibleStars:sky.state.visibleStars};
  sky.update({date,stargazing:true});
  const blocker=new THREE.Mesh(new THREE.PlaneGeometry(100,100),new THREE.MeshBasicMaterial({color:'#000000',fog:false}));
  blocker.position.copy(camera.position).addScaledVector(new THREE.Vector3().copy(view),10);blocker.quaternion.copy(camera.quaternion);scene.add(blocker);const occluded=stats(read());scene.remove(blocker);blocker.geometry.dispose();blocker.material.dispose();
  // Zoom onto the Moon: full/new brightness must follow geometry of sunlight.
  const phases={};camera.fov=4;camera.updateProjectionMatrix();
  for(const [name,day,hour]of [['full','2026-06-30',7.95],['new','2026-06-15',10.9],['quarter','2026-06-22',18]]){
   let instant=dateFromHKT(day,hour),state=getSkyState(instant);
   // June full moon has set by 07:57; use the same date's 04:00 visible phase.
   if(state.moon.altitudeDeg<=0){instant=dateFromHKT(day,4);state=getSkyState(instant);}
   camera.lookAt(camera.position.clone().add(new THREE.Vector3().copy(state.moon.direction).multiplyScalar(100)));camera.updateMatrixWorld();sky.update({date:instant,stargazing:true,limitingMagnitude:1});
   phases[name]={...stats(read()),fraction:state.moon.fraction,altitudeDeg:state.moon.altitudeDeg};
  }
  sky.dispose();const removed=scene.getObjectByName('Hong Kong sky')===undefined;target.dispose();renderer.dispose();
  return {clear,picked,selected,cached,figures,translated,city,overcast,day,occluded,phases,removed};
 });
 assert.ok(result.clear.lit>250,'stars render with logarithmic depth despite dense scene fog');
 assert.equal(result.picked.hr,7001,'Vega is selectable in the projected centre');assert.equal(result.selected.iau,'Lyr');assert.ok(result.cached,'small elapsed changes reuse catalogue positions');
 assert.ok(result.figures.lit>result.clear.lit*1.5,'constellation arcs are visible');
 assert.ok(Math.abs(result.translated.total-result.clear.total)<result.clear.total*.003,'moving the observer has no sky parallax');
 assert.ok(result.city.lit<result.clear.lit,'the city sky suppresses faint stars');assert.equal(result.overcast.lit,0);assert.equal(result.day.visibleStars,0);
 assert.equal(result.occluded.lit,0,'opaque city geometry occludes sky under logarithmic depth');
 assert.ok(result.phases.full.fraction>.99);assert.ok(result.phases.new.fraction<.01);assert.ok(result.phases.full.total>result.phases.new.total*8);
 assert.ok(result.phases.quarter.total>result.phases.new.total*3);assert.ok(result.phases.quarter.total<result.phases.full.total*.85);
 assert.ok(result.removed);assert.deepEqual(errors,[]);
 result.result='passed';result.errors=errors;await writeFile(new URL('../../../docs/astra-city/sky-verification.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}
