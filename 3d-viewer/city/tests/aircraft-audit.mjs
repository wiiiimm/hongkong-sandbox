import {chromium} from 'playwright';
import {writeFile,mkdir} from 'node:fs/promises';
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
try{
 const page=await browser.newPage({viewport:{width:1440,height:920}});page.on('console',m=>{if(m.type()==='error')console.error(m.text());});
 await page.route('**/aircraft-audit.html',r=>r.fulfill({contentType:'text/html',body:'<!doctype html><style>body{margin:0;background:#e1e6e7;font:14px system-ui}canvas{display:block}.label{position:absolute;padding:16px;color:#283a42}.sub{font-size:11px;color:#4c5d63}</style><title>Bundled aircraft audit</title>'}));await page.goto('http://127.0.0.1:4176/aircraft-audit.html');
 const improved=process.env.AIRCRAFT_AFTER==='1';
 const report=await page.evaluate(async(improved)=>{
  const THREE=await import('/vendor/three.module.js'),{GLTFLoader}=await import('/vendor/GLTFLoader.js'),{prepareAircraft}=await import('/city/aircraft.js');
  const rows=[['prop','plane-prop.glb',0],['betsy','nc/plane-betsy.glb',Math.PI],['cx747','plane-747.glb',Math.PI],['cx777','plane-777.glb',-Math.PI/2],['a330','nc/plane-a330.glb',Math.PI],['a350','plane-a350.glb',Math.PI/2],['ufo','plane-ufo.glb',0]];
  const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(1440,920);renderer.setPixelRatio(1);renderer.toneMapping=THREE.ACESFilmicToneMapping;document.body.append(renderer.domElement);renderer.setScissorTest(true);
  const output=[];
  for(let i=0;i<rows.length;i++){
   const [id,file,rot]=rows[i],gltf=await new GLTFLoader().loadAsync('/data/models/'+file),model=improved?prepareAircraft(gltf,id):gltf.scene;
   const scene=new THREE.Scene();scene.background=new THREE.Color(i%2?'#d6dfe2':'#e1e6e7');scene.add(new THREE.HemisphereLight('#edf5ff','#647469',2));const sun=new THREE.DirectionalLight('#fff7e8',3);sun.position.set(-200,300,-100);scene.add(sun);
   const group=new THREE.Group();group.rotation.y=improved?0:rot;group.add(model);scene.add(group);group.updateMatrixWorld(true);
   const box=new THREE.Box3().setFromObject(group),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());group.position.sub(center);group.updateMatrixWorld(true);
   const meshes=[];let triangles=0;model.traverse(o=>{if(!o.isMesh)return;const b=new THREE.Box3().setFromObject(o),s=b.getSize(new THREE.Vector3());triangles+=(o.geometry.index?.count||o.geometry.attributes.position.count)/3;meshes.push({name:o.name,bounds:[b.min.toArray(),b.max.toArray()],size:s.toArray(),materials:[].concat(o.material).map(m=>({name:m.name,color:m.color?.getHexString(),roughness:m.roughness,metalness:m.metalness,transparent:m.transparent,opacity:m.opacity,map:!!m.map,mapSize:m.map?.image?[m.map.image.width,m.map.image.height]:null}))});});
   const width=360,height=440,x=i%4*width,y=Math.floor(i/4)*height;
   const camera=new THREE.PerspectiveCamera(32,width/height,.01,1000000);camera.position.set(size.length()*1.06,size.length()*.70,-size.length()*1.25);camera.lookAt(0,0,0);
   renderer.setViewport(x,920-y-height,width,height);renderer.setScissor(x,920-y-height,width,height);renderer.render(scene,camera);
   const label=document.createElement('div');label.className='label';label.style.left=x+'px';label.style.top=y+'px';label.innerHTML=`<strong>${id}</strong><div class="sub">${Math.round(triangles).toLocaleString()} triangles · ${meshes.length} meshes</div>`;document.body.append(label);
   output.push({id,file,rot,improvements:model.userData.aircraft?.metadata,bounds:[box.min.toArray(),box.max.toArray()],size:size.toArray(),triangles,animations:gltf.animations.map(a=>a.name),meshes});
  }
  return output;
 },improved);
 await mkdir(new URL('../../../docs/astra-city/aircraft/',import.meta.url),{recursive:true});
 await writeFile(new URL('../../../docs/astra-city/aircraft/'+(improved?'improved-audit':'source-audit')+'.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
 await page.screenshot({path:new URL('../../../docs/astra-city/aircraft/'+(improved?'after':'before')+'.png',import.meta.url).pathname});
 console.log(JSON.stringify(report.map(({meshes,...other})=>({...other,meshCount:meshes.length})),null,2));
}finally{await browser.close();}
