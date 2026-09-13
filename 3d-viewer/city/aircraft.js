import * as THREE from '../vendor/three.module.js';
import {GLTFLoader} from '../vendor/GLTFLoader.js';
import {mergeGeometries} from '../vendor/BufferGeometryUtils.js';

// Manufacturer dimensions are metre-scale targets, not a claim of survey-grade source meshes.
export const AIRCRAFT=Object.freeze([
 {id:'prop',label:'Light prop plane',file:'plane-prop.glb',length:9.75,wingspan:11.1,rotation:0,kind:'prop',approximate:true,credit:'Vojtěch Balák · Small Airplane',licence:'CC BY 3.0',source:'https://poly.pizza/m/7cvx6ex-xfL',dimensionSource:null},
 {id:'betsy',label:'Betsy · Douglas DC-3',file:'nc/plane-betsy.glb',length:19.66,wingspan:28.96,rotation:Math.PI,kind:'twin-prop',credit:'OUTPISTON · McDonnell Douglas DC-3; existing Betsy repaint',licence:'CC BY-NC-SA 4.0',nonCommercial:true,source:'https://sketchfab.com/3d-models/mcdonnell-douglas-dc-3-7673f61636554c02bf86015f1b6a8333',dimensionSource:'https://airandspace.si.edu/collection-objects/douglas-dc-3/nasm_A19530075000'},
 {id:'cx747',label:'Cathay · Boeing 747-400',file:'plane-747.glb',length:70.67,wingspan:64.44,rotation:Math.PI,kind:'four-jet',credit:'zairiqzairiq · Air France Boeing 747-400; existing Cathay repaint',licence:'CC BY 4.0',source:'https://sketchfab.com/3d-models/air-france-boeing-747-400-58113c1d27984d90bd1f49cb1ff90db4',dimensionSource:'https://www.boeing.com/content/dam/boeing/v2/airports/acaps/747-400_Rev_F.pdf'},
 {id:'cx777',label:'Cathay · Boeing 777-300ER',file:'plane-777.glb',length:73.86,wingspan:64.8,rotation:-Math.PI/2,kind:'twin-jet',credit:'Omatar · Boeing 777-300ER Saudia; existing Cathay repaint',licence:'CC BY 4.0',source:'https://sketchfab.com/3d-models/boeing-777-300er-saudi-arabian-airlines-saudia-410ec4a0d4b646918ac2e5f83b48c27e',dimensionSource:'https://www.boeing.com/content/dam/boeing/v2/airports/acaps/777-200LR-300ER-F_Rev_G.pdf'},
 {id:'a330',label:'Cathay · Airbus A330-300',file:'nc/plane-a330.glb',length:63.66,wingspan:60.3,rotation:Math.PI,kind:'twin-jet',credit:'OUTPISTON · Cathay Pacific Airbus A330-300',licence:'CC BY-NC-SA 4.0',nonCommercial:true,source:'https://sketchfab.com/3d-models/cathay-pacific-airbus-a330-300-45a62d88607145c4afb1f46b281aa277',dimensionSource:'https://www.aircraft.airbus.com/en/aircraft/a330/a330-300'},
 {id:'a350',label:'Cathay · Airbus A350-1000',file:'plane-a350.glb',length:73.78,wingspan:64.75,rotation:Math.PI/2,kind:'twin-jet',credit:'Newbie99999993 · A350 V3 with animation; existing Cathay repaint',licence:'CC BY 4.0',source:'https://sketchfab.com/3d-models/a350-v3-with-animation-965439a6041847a0b8decba253ffdf6f',dimensionSource:'https://www.aircraft.airbus.com/en/aircraft/a350/a350-1000'},
 {id:'ufo',label:'UFO · fictional',file:'plane-ufo.glb',length:18,wingspan:18,rotation:0,kind:'ufo',approximate:true,credit:'Islide · UFO',licence:'CC BY 4.0',source:'https://sketchfab.com/3d-models/ufo-1f9f59a76c4b44f2b2c356ed07b9db06',dimensionSource:null},
].map(row=>Object.freeze(row)));
export const aircraftById=id=>AIRCRAFT.find(a=>a.id===id)||AIRCRAFT[0];
const vec=()=>new THREE.Vector3(),clamp=THREE.MathUtils.clamp;
export function disposeAircraft(root){
 if(!root)return;const geometries=new Set(),materials=new Set(),textures=new Set();
 root.traverse(o=>{if(o.geometry)geometries.add(o.geometry);for(const material of [].concat(o.material||[])){materials.add(material);for(const value of Object.values(material))if(value?.isTexture)textures.add(value);}});
 for(const value of geometries)value.dispose();for(const value of materials)value.dispose();for(const value of textures)value.dispose();
 root.clear();
}
function reflectionTexture(){
 const faces=[];
 for(let i=0;i<6;i++){
  const canvas=document.createElement('canvas');canvas.width=canvas.height=64;const c=canvas.getContext('2d');
  const gradient=c.createLinearGradient(0,0,0,64);
  if(i===2){gradient.addColorStop(0,'#d5e6ef');gradient.addColorStop(1,'#bacbd7');}
  else if(i===3){gradient.addColorStop(0,'#65746e');gradient.addColorStop(1,'#9fa99c');}
  else {gradient.addColorStop(0,'#afc4d3');gradient.addColorStop(.48,'#e2e8e5');gradient.addColorStop(.53,'#abb7b0');gradient.addColorStop(1,'#62716a');}
  c.fillStyle=gradient;c.fillRect(0,0,64,64);faces.push(canvas);
 }
 const texture=new THREE.CubeTexture(faces);texture.colorSpace=THREE.SRGBColorSpace;texture.needsUpdate=true;return texture;
}
function tuneMaterial(material,definition,environment,name){
 // Preserve authored liveries, normal maps, alpha and colour-space assignments.
 if(material.map){material.map.anisotropy=8;material.map.minFilter=THREE.LinearMipmapLinearFilter;material.map.magFilter=THREE.LinearFilter;material.map.generateMipmaps=true;material.map.needsUpdate=true;}
 if(!material.isMeshStandardMaterial)return;
 const label=material.name+' '+name,gear=/gear|tyre|tire|wheel/i.test(label);
 const dark=!material.map&&material.color&&material.color.getHSL({}).l<.10;
 if(gear){material.roughness=.76;material.metalness=.12;}
 else if(/glass/i.test(label)){material.roughness=.14;material.metalness=.18;}
 else if(definition.id==='betsy'){material.roughness=material.transparent?.2:.32;material.metalness=material.transparent?.06:.56;}
 else if(definition.id==='ufo'){material.roughness=.27;material.metalness=.62;}
 else if(/Silver|Engine_Cones/i.test(label)){material.roughness=.29;material.metalness=.62;}
 else {material.roughness=dark?.48:.36;material.metalness=dark?.05:.06;}
 material.envMap=environment;material.envMapIntensity=definition.id==='ufo'?.95:definition.id==='betsy'?.72:.36;
 material.userData.aircraftReflection=material.envMapIntensity;material.needsUpdate=true;
}
function ancestry(object){const names=[];for(let o=object;o;o=o.parent)names.push(o.name);return names.join(' / ');}
function spinnerKey(names){if(/Propeller_Cone/i.test(names))return 'prop';const match=names.match(/prop([01])_still/i);return match?'prop'+match[1]:null;}
function standardGeometry(source,matrix){
 let geometry=source.clone();geometry.applyMatrix4(matrix);
 if(geometry.index){const previous=geometry;geometry=geometry.toNonIndexed();previous.dispose();}
 for(const key of Object.keys(geometry.attributes))if(!['position','normal','uv','color'].includes(key))geometry.deleteAttribute(key);
 if(!geometry.attributes.normal)geometry.computeVertexNormals();
 if(!geometry.attributes.uv)geometry.setAttribute('uv',new THREE.Float32BufferAttribute(new Float32Array(geometry.attributes.position.count*2),2));
 // Uniform vertex layout permits material batches while retaining any source colours.
 if(!geometry.attributes.color){const array=new Float32Array(geometry.attributes.position.count*3);array.fill(1);geometry.setAttribute('color',new THREE.Float32BufferAttribute(array,3));}
 else if(geometry.attributes.color.itemSize!==3){const old=geometry.attributes.color,array=new Float32Array(old.count*3);for(let i=0;i<old.count;i++)array.set([old.getX(i),old.getY(i),old.getZ(i)],i*3);geometry.setAttribute('color',new THREE.Float32BufferAttribute(array,3));}
 for(const [key,old] of Object.entries(geometry.attributes)){if(old.array instanceof Float32Array&&!old.normalized)continue;const array=new Float32Array(old.count*old.itemSize);for(let i=0;i<old.count;i++)for(let j=0;j<old.itemSize;j++)array[i*old.itemSize+j]=(j===0?old.getX(i):j===1?old.getY(i):j===2?old.getZ(i):old.getW(i));geometry.setAttribute(key,new THREE.Float32BufferAttribute(array,old.itemSize));}
 geometry.clearGroups();return geometry;
}
function wingtip(root,side,span){
 const sum=vec(),point=vec();let count=0;
 root.traverse(o=>{if(!o.isMesh||o.userData.aircraftGear)return;const a=o.geometry.attributes.position;if(!a)return;
  for(let i=0;i<a.count;i++){point.fromBufferAttribute(a,i).applyMatrix4(o.matrixWorld);if(point.x*side>span*.492){sum.add(point);count++;}}
 });
 return count?sum.divideScalar(count):new THREE.Vector3(side*span/2,0,0);
}
function addWinglets(root,definition,tips){
 if(definition.id!=='cx747')return;
 // The bundled -400 hull lacks winglets. 1.8 m height follows the museum's real pair;
 // chord, sweep and inward root offset are an illustrative reconstruction.
 const material=new THREE.MeshStandardMaterial({color:'#edf0ed',roughness:.36,metalness:.06,side:THREE.DoubleSide});
 for(let i=0;i<2;i++){
  const side=i===0?-1:1,tip=tips[i],x=side*(definition.wingspan/2-.32),z=tip.z,y=tip.y;
  const points=[x,y,z-.75,x,y,z+.65,side*definition.wingspan/2,y+1.8,z+.9,side*definition.wingspan/2,y+1.8,z+.3];
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(points,3));geometry.setIndex([0,1,2,0,2,3]);geometry.computeVertexNormals();
  const mesh=new THREE.Mesh(geometry,material);mesh.name='Reconstructed 747-400 winglet';mesh.castShadow=true;root.add(mesh);
 }
}
function addLights(root,definition,tips){
 const lights=[],radius=clamp(definition.wingspan*.0028,.07,.18),geometry=new THREE.SphereGeometry(radius,8,6);
 const add=(name,colour,position,beacon=false)=>{const material=new THREE.MeshStandardMaterial({color:colour,emissive:colour,emissiveIntensity:1.8,toneMapped:false,roughness:.2});const mesh=new THREE.Mesh(geometry,material);mesh.name=name;mesh.position.copy(position);mesh.userData.beacon=beacon;root.add(mesh);lights.push(mesh);};
 if(definition.kind==='ufo'){
  for(let i=0;i<8;i++){const a=i*Math.PI/4;add('Fictional saucer rim light','#8ddde1',new THREE.Vector3(Math.cos(a)*definition.wingspan*.47,-.5,Math.sin(a)*definition.wingspan*.47));}
 }else{
  add('Port navigation light · red','#ff352e',tips[0]);add('Starboard navigation light · green','#45ed85',tips[1]);
  const tail=vec(),candidate=vec();let tailCount=0;const beacon=vec();beacon.y=-Infinity;
  root.updateMatrixWorld(true);root.traverse(o=>{if(!o.isMesh||o.userData.aircraftGear||/navigation light/.test(o.name))return;const a=o.geometry.attributes.position;for(let i=0;i<a.count;i++){candidate.fromBufferAttribute(a,i).applyMatrix4(o.matrixWorld);if(candidate.z>definition.length*.485){tail.add(candidate);tailCount++;}if(Math.abs(candidate.x)<definition.wingspan*.025&&Math.abs(candidate.z+definition.length*.06)<definition.length*.025&&candidate.y>beacon.y)beacon.copy(candidate);}});
  if(tailCount)tail.divideScalar(tailCount);else tail.set(0,0,definition.length*.495);
  add('Tail navigation light · white','#fff7e9',tail);
  if(!Number.isFinite(beacon.y))beacon.set(0,1,-definition.length*.06);beacon.y+=radius*.4;
  add('Upper anticollision beacon','#ef322b',beacon,true);
 }
 return lights;
}
export function prepareAircraft(gltf,id,{reflections=true}={}){
 const definition=aircraftById(id),source=gltf.scene,wrapper=new THREE.Group();wrapper.rotation.y=definition.rotation;wrapper.add(source);wrapper.updateMatrixWorld(true);
 const sourceBox=new THREE.Box3().setFromObject(wrapper,true),size=sourceBox.getSize(vec());
 if(!Number.isFinite(size.length())||size.x<.00001||size.z<.00001)throw new Error('Aircraft asset contains no usable geometry');
 const sx=definition.wingspan/size.x,sz=definition.length/size.z,sy=sz;
 const centre=sourceBox.getCenter(vec()),bodyY=sourceBox.min.y+size.y*(definition.kind.includes('jet')?.35:.43);
 const transform=new THREE.Matrix4().makeScale(sx,sy,sz);transform.setPosition(-centre.x*sx,-bodyY*sy,-centre.z*sz);
 const environment=reflections?reflectionTexture():null,root=new THREE.Group();root.name=definition.label;
 const groups=new Map(),tunedMaterials=new Map(),originalGeometries=new Set(),materials=new Set(),blurCentres=new Map();let sourceMeshes=0,hiddenVariants=0;
 source.traverse(o=>{
  if(!o.isMesh)return;sourceMeshes++;originalGeometries.add(o.geometry);const names=ancestry(o),matrix=new THREE.Matrix4().multiplyMatrices(transform,o.matrixWorld);
  const blurred=names.match(/prop([01])_blurred/);
  if(blurred){const box=new THREE.Box3().setFromObject(o).applyMatrix4(transform),s=box.getSize(vec());if(s.x>1&&s.y>1)blurCentres.set('prop'+blurred[1],box.getCenter(vec()));}
  if(/prop\d+_(slow|blurred)/i.test(names)){hiddenVariants++;return;}
  const sourceMaterial=Array.isArray(o.material)?o.material[0]:o.material;if(!sourceMaterial)return;
  const style=/CXGear|tyre|tire|wheel/i.test(sourceMaterial.name+' '+names)?'gear':/glass/i.test(sourceMaterial.name+' '+names)?'glass':'skin';
  const materialKey=sourceMaterial.uuid+'|'+style;
  if(!tunedMaterials.has(materialKey)){const copy=sourceMaterial.clone();tuneMaterial(copy,definition,environment,style);tunedMaterials.set(materialKey,copy);materials.add(copy);}
  const material=tunedMaterials.get(materialKey);
  const gear=definition.id!=='betsy'&&definition.id!=='prop'&&/CXGear|landing.?gear|undercarriage|bogie/i.test(material.name+' '+names);
  const spin=spinnerKey(names),key=material.uuid+'|'+(gear?'gear':spin||'hull');
  if(!groups.has(key))groups.set(key,{material,gear,spin,geometries:[]});
  groups.get(key).geometries.push(standardGeometry(o.geometry,matrix));
 });
 const spinnerGroups=new Map(),gearMeshes=[];
 for(const batch of groups.values()){
  const geometry=mergeGeometries(batch.geometries,false);for(const g of batch.geometries)g.dispose();if(!geometry)throw new Error('Aircraft material batch could not be built');
  const mesh=new THREE.Mesh(geometry,batch.material);mesh.name=batch.gear?'Retractable landing gear':batch.spin||batch.material.name||'Airframe';mesh.castShadow=mesh.receiveShadow=true;mesh.userData.aircraftGear=batch.gear;
  if(batch.spin){if(!spinnerGroups.has(batch.spin))spinnerGroups.set(batch.spin,new THREE.Group());spinnerGroups.get(batch.spin).add(mesh);}else root.add(mesh);
  if(batch.gear){mesh.visible=false;gearMeshes.push(mesh);}
 }
 const spinners=[];
 for(const [key,group] of spinnerGroups){
  group.updateMatrixWorld(true);const centre=new THREE.Box3().setFromObject(group).getCenter(vec());if(blurCentres.has(key)){centre.x=blurCentres.get(key).x;centre.y=blurCentres.get(key).y;}
  for(const mesh of group.children)mesh.geometry.translate(-centre.x,-centre.y,-centre.z);
  group.position.copy(centre);group.name='Hub-centred '+key;root.add(group);spinners.push(group);
 }
 for(const geometry of originalGeometries)geometry.dispose();
 // Materials used only by removed duplicate prop variants also need release.
 const discardedMaterials=new Set();source.traverse(o=>{for(const m of [].concat(o.material||[]))if(!materials.has(m))discardedMaterials.add(m);});
 const usedTextures=new Set();for(const m of materials)for(const value of Object.values(m))if(value?.isTexture)usedTextures.add(value);
 for(const m of discardedMaterials){for(const value of Object.values(m))if(value?.isTexture&&!usedTextures.has(value))value.dispose();m.dispose();}
 wrapper.remove(source);root.updateMatrixWorld(true);
 const tips=[wingtip(root,-1,definition.wingspan),wingtip(root,1,definition.wingspan)];
 addWinglets(root,definition,tips);const lights=addLights(root,definition,tips);
 const bounds=new THREE.Box3().setFromObject(root),dimensions=bounds.getSize(vec());
 const metadata={id:definition.id,status:'ready',sourceMeshes,drawMeshes:[...groups].length,hiddenVariants,gearMeshes:gearMeshes.length,spinners:spinners.length,dimensions:{length:definition.length,wingspan:definition.wingspan,height:dimensions.y},scale:{x:sx,y:sy,z:sz},approximate:true,dimensionsEstimated:!!definition.approximate};
 root.userData.aircraft={definition,spinners,gearMeshes,lights,materials:[...materials],metadata,environment};return root;
}
export function buildAircraftFallback(id){
 const d=aircraftById(id),root=new THREE.Group(),paint=new THREE.MeshStandardMaterial({color:'#e7ebe7',roughness:.36,metalness:.06}),trim=new THREE.MeshStandardMaterial({color:d.kind==='prop'?'#c84d36':'#2d6c65',roughness:.4}),dark=new THREE.MeshStandardMaterial({color:'#243238',roughness:.4});
 if(d.kind==='ufo'){
  const body=new THREE.Mesh(new THREE.SphereGeometry(d.wingspan/2,32,12),paint);body.scale.y=.16;root.add(body);const dome=new THREE.Mesh(new THREE.SphereGeometry(d.wingspan*.19,24,12),dark);dome.scale.y=.6;dome.position.y=.6;root.add(dome);
 }else{
  const radius=d.kind.includes('jet')?d.length*.041:d.length*.067;
  const body=new THREE.Mesh(new THREE.CapsuleGeometry(radius,Math.max(radius,d.length-radius*2),10,24),paint);body.rotation.x=Math.PI/2;root.add(body);
  const makeWing=(span,chord,z,y)=>{const g=new THREE.BufferGeometry(),sweep=d.kind.includes('jet')?.16:.025;g.setAttribute('position',new THREE.Float32BufferAttribute([-span/2,y,z+span*sweep,span/2,y,z+span*sweep,0,y,z-chord*.65,-span/2,y,z+span*sweep+chord*.3,0,y,z+chord*.55,span/2,y,z+span*sweep+chord*.3],3));g.setIndex([0,1,2,0,3,4,0,4,1,1,4,5]);g.computeVertexNormals();const m=new THREE.Mesh(g,trim);m.material.side=THREE.DoubleSide;root.add(m);};
  makeWing(d.wingspan,d.length*.16,-d.length*.02,0);makeWing(d.wingspan*.35,d.length*.08,d.length*.34,.4);
  const fin=new THREE.Mesh(new THREE.BoxGeometry(radius*.18,radius*2.4,d.length*.13),trim);fin.position.set(0,radius*1.6,d.length*.37);root.add(fin);
  const canopy=new THREE.Mesh(new THREE.SphereGeometry(radius,16,8),dark);canopy.scale.set(.92,.58,1.5);canopy.position.set(0,radius*.7,-d.length*.32);root.add(canopy);
  const engines=d.kind==='four-jet'?[-.32,-.17,.17,.32]:d.kind==='twin-jet'||d.kind==='twin-prop'?[-.20,.20]:[];
  for(const x of engines){const engine=new THREE.Mesh(new THREE.CylinderGeometry(radius*.64,radius*.56,d.length*.08,16),paint);engine.rotation.x=Math.PI/2;engine.position.set(x*d.wingspan,-radius*.7,-d.length*.035);root.add(engine);const intake=new THREE.Mesh(new THREE.CircleGeometry(radius*.51,16),dark);intake.rotation.y=Math.PI;intake.position.set(engine.position.x,engine.position.y,engine.position.z-d.length*.041);root.add(intake);}
 }
 root.name=d.label+' · simplified fallback';root.userData.aircraft={definition:d,spinners:[],lights:[],gearMeshes:[],materials:[paint,trim,dark],metadata:{id:d.id,status:'fallback',dimensions:{length:d.length,wingspan:d.wingspan,height:d.length*.2},approximate:true}};return root;
}
export class AircraftModel {
 constructor({target,loader=new GLTFLoader(),onChange=()=>{},prepare=prepareAircraft}){this.target=target;this.loader=loader;this.prepare=prepare;this.onChange=onChange;this.token=0;this.elapsed=0;this.night=0;this.reducedMotion=false;this.current=null;this.disposed=false;this.id='prop';this.status='idle';this.error=null;}
 get state(){return {id:this.id,status:this.status,error:this.error,...this.current?.userData.aircraft?.metadata,status:this.status};}
 async setAircraft(id){
  if(this.disposed)return false;const d=aircraftById(id);if(d.id===this.id&&this.status==='ready')return true;
  const token=++this.token;this.id=d.id;this.status='loading';this.error=null;this.swap(buildAircraftFallback(d.id));this.onChange(this.state);
  let gltf;
  try{gltf=await this.loader.loadAsync(new URL('../data/models/'+d.file,import.meta.url).href);if(this.disposed||token!==this.token){disposeAircraft(gltf.scene);return false;}
   const prepared=this.prepare(gltf,d.id);this.swap(prepared);this.status='ready';this.onChange(this.state);return true;
  }catch(error){if(gltf?.scene)disposeAircraft(gltf.scene);if(this.disposed||token!==this.token)return false;this.status='fallback';this.error='Detailed aircraft unavailable; flying the simplified '+d.label;this.onChange(this.state);return false;}
 }
 swap(model){if(this.current){this.target.remove(this.current);disposeAircraft(this.current);}this.current=model;this.target.add(model);}
 setLighting({night=this.night,reducedMotion=this.reducedMotion}={}){this.night=clamp(night,0,1);this.reducedMotion=!!reducedMotion;}
 update(dt){
  if(!this.current)return;const data=this.current.userData.aircraft;if(!this.reducedMotion)this.elapsed+=Math.max(0,Math.min(dt,.1));
  for(const pivot of data.spinners)pivot.rotation.z=this.elapsed*38;
  for(const light of data.lights)light.material.emissiveIntensity=(light.userData.beacon?(this.reducedMotion?.8:.55+.9*(.5+.5*Math.sin(this.elapsed*Math.PI*1.25))**5):1.1)*(1+this.night*1.6);
  for(const material of data.materials)if(material.userData.aircraftReflection!=null)material.envMapIntensity=material.userData.aircraftReflection*(1-this.night*.85);
 }
 dispose(){this.disposed=true;this.token++;if(this.current){this.target.remove(this.current);disposeAircraft(this.current);this.current=null;}}
}
