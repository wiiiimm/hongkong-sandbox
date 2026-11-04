/** Focused browser regression: actual terrain rendering, height queries and walking. */
import {createServer} from 'node:http';
import {createRequire} from 'node:module';
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {parseArgs} from 'node:util';
import assert from 'node:assert/strict';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
const root=new URL('../../../',import.meta.url),require=createRequire(new URL('3d-viewer/city/package.json',root));
const {chromium}=require('playwright'),{values:args}=parseArgs({options:{out:{type:'string'}}});
assert(args.out&&!args.out.includes('..'));
const out=new URL(args.out+'/',root);mkdirSync(out,{recursive:true});assert(!existsSync(new URL('browser.json',out)),'Fresh evidence only');
const hash=b=>createHash('sha256').update(b).digest('hex'),inputHashes={},errors=[],views=[];
const html=`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Coastal terrain sampler regression</title>
<script type="importmap">{"imports":{"three":"/vendor/three.module.js"}}</script>
<style>body{margin:0;background:#e6eef2;color:#153042;font:16px system-ui}header{padding:16px}h1{font-size:22px;margin:0}main{display:flex;flex-wrap:wrap}section{flex:1 1 350px;min-width:0}h2{font-size:17px;margin:12px 16px}canvas{width:100%;display:block}p{margin:8px 16px}</style>
<header><h1>Coastal terrain and walking checks</h1><p>Regression fixtures using the production renderer and sampler · no model installation credit</p></header><main></main>
<script type="module">
import * as THREE from '/vendor/three.module.js';import {makeTerrainSampler,ORIGIN} from '/city/geo.js';import {makeTerrain} from '/city/world.js';import {Navigation} from '/city/navigation.js';
const grid=(elev,step=10,w=2,h=2)=>({w,h,elev,vegetation:Array(w*h).fill(0),meta:{georef:{aE:step,aN:-step,bE:ORIGIN[0],bN:ORIGIN[1]}}});
const child={...grid(Array(9).fill(3),5,3,3),coarseCells:[0,0,1,1]};
const native={...grid(Array(4).fill(3),2),coarseCells:[0,0,1,1],meta:{georef:{aE:2,aN:-2,bE:ORIGIN[0]+1,bN:ORIGIN[1]-1}},nativeMesh:{position:[1,7,1,3,7,1,1,7,3,3,7,3],index:[0,2,1,1,2,3]}};child.patches=[native];
const hydro={bounds:[0,0,10,10],water:[{rings:[[[0,0],[10,0],[10,10],[0,10],[0,0]]]}],illustrativeBed:-4,bedTriangles:[0,-4,0,0,-4,10,10,-4,0,10,-4,0,0,-4,10,10,-4,10],terrainCuts:[{georef:child.meta.georef,cells:[0,1].flatMap(c=>[0,1].map(r=>({x:c*5,z:r*5,land:[]})))}]};
const fixtures=[{name:'Coastal slope',data:grid([0,2,2,2]),points:[[1,1,-2.8],[4,4,.8],[8,8,2]]},{name:'Mapped water and native overlay',data:{...grid(Array(4).fill(3)),patches:[child],hydro},points:[[2,2.2,7],[7,7,-4]]}];
window.__coastStage='modules loaded';const proofs=[];for(const f of fixtures){window.__coastStage='start '+f.name;const section=document.createElement('section');section.innerHTML='<h2>'+f.name+'</h2>';document.querySelector('main').append(section);
 const sampler=makeTerrainSampler(f.data),terrain=makeTerrain(f.data);terrain.updateMatrixWorld(true);const probes=[];
 for(const [x,z,expected] of f.points){const hits=new THREE.Raycaster(new THREE.Vector3(x,100,z),new THREE.Vector3(0,-1,0)).intersectObject(terrain,true);if(!hits.length||Math.abs(hits[0].point.y-expected)>1e-5||Math.abs(sampler.height(x,z)-hits[0].point.y)>1e-5)throw Error('Rendered/sampled mismatch '+f.name);probes.push({x,z,expected,drawn:hits[0].point.y,sampled:sampler.height(x,z)});}
 const scene=new THREE.Scene();scene.background=new THREE.Color('#e6eef2');scene.add(terrain,new THREE.HemisphereLight(0xffffff,0x405462,2.5));const sun=new THREE.DirectionalLight(0xffffff,2);sun.position.set(12,20,8);scene.add(sun);
 const width=Math.round(section.getBoundingClientRect().width),height=Math.round(width*.65),camera=new THREE.PerspectiveCamera(45,width/height,.1,200);camera.position.set(19,18,22);camera.lookAt(5,0,5);
 window.__coastStage='render '+f.name;const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(1);renderer.setSize(width,height);section.append(renderer.domElement);renderer.render(scene,camera);
 const gl=renderer.getContext(),pixels=new Uint8Array(width*height*4);gl.readPixels(0,0,width,height,gl.RGBA,gl.UNSIGNED_BYTE,pixels);let nonBackground=0;for(let i=0;i<pixels.length;i+=4)if(Math.abs(pixels[i]-pixels[0])+Math.abs(pixels[i+1]-pixels[1])+Math.abs(pixels[i+2]-pixels[2])>20)nonBackground++;if(nonBackground<200)throw Error('Empty render');
 proofs.push({name:f.name,probes,nonBackgroundPixels:nonBackground,webglError:gl.getError()});}
const sampler=makeTerrainSampler(fixtures[0].data),nav=Object.assign(Object.create(Navigation.prototype),{sampler,index:{collision:()=>false},waterLevel:()=>.3});
if(nav.walkHeight(2,2,1.2,4)!==undefined)throw Error('Walking entered submerged ground');const safe=nav.safeGround(2,2);if(!safe||Math.hypot(safe.x-2,safe.z-2)<=1)throw Error('Dry arrival not found');
window.__coast={ready:true,proofs,submergedWalkRejected:true,dryArrival:safe,wholeCityAcceptance:false,newlyInstalled:0};
</script>`;
const server=createServer((req,res)=>{try{const url=new URL(req.url,'http://localhost');if(url.pathname==='/'){res.setHeader('Content-Type','text/html');res.end(html);return;}
 assert(/^\/[a-zA-Z0-9_./-]+\.js$/.test(url.pathname)&&!url.pathname.includes('..'));
 const path='3d-viewer'+url.pathname,raw=readFileSync(new URL(path,root));inputHashes[path]=hash(raw);res.setHeader('Content-Type','text/javascript');res.end(raw);
 }catch(e){res.statusCode=404;res.end(e.message);}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));let browser;
try{browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 for(const [name,viewport,isMobile] of [['desktop',{width:1280,height:900},false],['mobile',{width:390,height:844},true]]){
  const page=await browser.newPage({viewport,isMobile,hasTouch:isMobile,deviceScaleFactor:1});page.on('pageerror',e=>errors.push({name,error:e.message}));page.on('console',m=>{if(m.type()==='error')console.log('browser-console: '+m.text());});page.on('requestfailed',r=>console.log('request-failed: '+r.url()+' '+r.failure()?.errorText));await page.goto('http://127.0.0.1:'+server.address().port+'/');
  try{await page.waitForFunction(()=>window.__coast?.ready,null,{timeout:30000});}catch(error){console.log(JSON.stringify(await page.evaluate(()=>({stage:window.__coastStage,proof:window.__coast,html:document.body.innerHTML.slice(0,600)}))));throw error;}
  const proof=await page.evaluate(()=>window.__coast);assert(proof.submergedWalkRejected);assert(proof.proofs.every(p=>p.webglError===0));await page.screenshot({path:new URL(name+'.png',out).pathname,fullPage:true});views.push({name,viewport,...proof,imageSHA256:hash(readFileSync(new URL(name+'.png',out)))});await page.close();console.log(JSON.stringify({name,passed:true}));
 }
 assert.deepEqual(errors,[]);inputHashes['source-scripts/city/government-import/check-coastal-sampler-browser.mjs']=hash(readFileSync(new URL('./check-coastal-sampler-browser.mjs',import.meta.url)));
 for(const [path,sha] of Object.entries(inputHashes))assert.equal(hash(readFileSync(new URL(path,root))),sha);
 writeFileSync(new URL('browser.json',out),JSON.stringify({views,errors,inputHashes,qualification:'Focused production-module browser fixture verification only; not whole-city, performance, architectural or installation acceptance.',newlyInstalled:0,modelGeometryChanges:0,scriptExternalAICalls:0},null,2)+'\n');
}catch(error){writeFileSync(new URL('browser-failed.json',out),JSON.stringify({error:String(error),errors,inputHashes},null,2)+'\n');throw error;
}finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
