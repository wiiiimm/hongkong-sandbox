import * as THREE from '../vendor/three.module.js';
import {mergeGeometries} from '../vendor/BufferGeometryUtils.js';
import {ORIGIN,inPolygon,random,smoothStep} from './geo.js';
import {buildingLighting} from './lighting.js';

const colour = x=>new THREE.Color(x);
export function makeTerrain(data) {
 const {w,h,elev,vegetation}=data,g=data.meta.georef;
 const positions=new Float32Array(w*h*3),colours=new Float32Array(w*h*3),indices=new Uint32Array((w-1)*(h-1)*6);
 const green=colour('#718764'),urban=colour('#cfccb3'),rock=colour('#999c83');
 const randomAt=random(8);
 for(let r=0;r<h;r++)for(let c=0;c<w;c++){
  const i=r*w+c,e=elev[i],x=g.bE+c*g.aE-ORIGIN[0],z=ORIGIN[1]-(g.bN+r*g.aN);
  positions.set([x,e>0?Math.max(1.2,e):-4,z],i*3);
  const co=(vegetation[i]?green:urban).clone();
  if(e>240)co.lerp(rock,smoothStep(240,900,e)*.38);
  co.multiplyScalar(.94+randomAt()*.10);colours.set([co.r,co.g,co.b],i*3);
 }
 let k=0;for(let r=0;r<h-1;r++)for(let c=0;c<w-1;c++){const a=r*w+c;if(!elev[a]&&!elev[a+1]&&!elev[a+w]&&!elev[a+w+1])continue;indices.set([a,a+w,a+1,a+1,a+w,a+w+1],k);k+=6;}
 const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(positions,3));geo.setAttribute('color',new THREE.BufferAttribute(colours,3));geo.setIndex(new THREE.BufferAttribute(indices.slice(0,k),1));geo.computeVertexNormals();
 const material=new THREE.MeshStandardMaterial({vertexColors:true,roughness:1,metalness:0,polygonOffset:true,polygonOffsetFactor:1,polygonOffsetUnits:1});
 const mesh=new THREE.Mesh(geo,material);mesh.receiveShadow=true;mesh.name='Lands Department · 70 m terrain';return mesh;
}
export function makeWater(){
 const material=new THREE.MeshStandardMaterial({color:'#6caba4',roughness:.36,metalness:.25});
 const time={value:0};
 material.onBeforeCompile=shader=>{
  shader.uniforms.uWaterTime=time;
  shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vWaterPosition;').replace('#include <begin_vertex>','#include <begin_vertex>\nvWaterPosition = (modelMatrix * vec4(transformed, 1.0)).xyz;');
  shader.fragmentShader=shader.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 vWaterPosition; uniform float uWaterTime;').replace('#include <color_fragment>',`#include <color_fragment>
   float ripple = sin(vWaterPosition.x * .065 + vWaterPosition.z * .038 + uWaterTime * .6) * sin(vWaterPosition.z * .071 - uWaterTime * .4);
   float swell = sin(vWaterPosition.x * .009 - vWaterPosition.z * .015 + uWaterTime * .2);
   diffuseColor.rgb *= .96 + ripple * .025 + swell * .025;`);
 };
 const mesh=new THREE.Mesh(new THREE.PlaneGeometry(180000,180000),material);mesh.rotation.x=-Math.PI/2;mesh.position.y=.3;mesh.name='Victoria Harbour';return {mesh,time,material};
}
export function extrudeBuilding(b){
 const path=ring=>ring.slice(0,-1).map(p=>new THREE.Vector2(p[0],-p[1]));
 const shape=new THREE.Shape(path(b.rings[0]));for(const hole of b.rings.slice(1))shape.holes.push(new THREE.Path(path(hole)));
 const geometry=new THREE.ExtrudeGeometry(shape,{depth:b.height-b.minimum,bevelEnabled:false,steps:1,curveSegments:1});geometry.rotateX(-Math.PI/2);geometry.translate(0,b.base+b.minimum,0);return geometry;
}
function facadeMaterial(hex,lighting){
 const material=new THREE.MeshStandardMaterial({color:hex,roughness:.69,metalness:.13});
 material.onBeforeCompile=shader=>{
  shader.uniforms.uCityNight=lighting.night;shader.uniforms.uCityActivity=lighting.activity;shader.uniforms.uCityRetail=lighting.retail;shader.uniforms.uCitySeconds=lighting.elapsed;shader.uniforms.uCityShimmer=lighting.shimmer;
  shader.vertexShader=shader.vertexShader.replace('#include <common>',`#include <common>
   attribute vec4 cityLight; varying vec4 vCityLight;
   varying vec3 vCityPosition; varying vec3 vCityNormal;`).replace('#include <begin_vertex>',`#include <begin_vertex>
   vCityLight = cityLight; vCityPosition = (modelMatrix * vec4(transformed, 1.0)).xyz;
   vCityNormal = normalize(mat3(modelMatrix) * objectNormal);`);
  shader.fragmentShader=shader.fragmentShader.replace('#include <common>',`#include <common>
   varying vec4 vCityLight; varying vec3 vCityPosition; varying vec3 vCityNormal;
   uniform float uCityNight; uniform vec4 uCityActivity; uniform float uCityRetail; uniform float uCitySeconds; uniform float uCityShimmer;
   float cityHash(vec2 p) { return fract(sin(dot(p, vec2(12.9898,78.233))) * 43758.5453); }
  `).replace('#include <color_fragment>',`#include <color_fragment>
   float wall = 1.0 - step(.6, abs(vCityNormal.y));
   float horizontal = abs(vCityNormal.x) > abs(vCityNormal.z) ? vCityPosition.z : vCityPosition.x;
   vec2 cell = vec2(horizontal / 3.6, (vCityPosition.y-vCityLight.z) / 3.5);
   vec2 grid = fract(cell);
   float windowMask = smoothstep(.12,.20,grid.x) * (1.0-smoothstep(.76,.84,grid.x)) * smoothstep(.20,.28,grid.y) * (1.0-smoothstep(.70,.78,grid.y));
   float glowMask = smoothstep(.0,.16,grid.x) * (1.0-smoothstep(.82,1.0,grid.x)) * smoothstep(.02,.24,grid.y) * (1.0-smoothstep(.74,.98,grid.y));
   float detailAA = 1.0-smoothstep(.25,1.3,max(fwidth(cell.x),fwidth(cell.y)));
   float activity = vCityLight.y < .5 ? uCityActivity.x : vCityLight.y < 1.5 ? uCityActivity.y : vCityLight.y < 2.5 ? uCityActivity.z : vCityLight.y < 3.5 ? uCityActivity.w : uCityRetail;
   if(vCityLight.w>0.0 && vCityPosition.y-vCityLight.z<vCityLight.w) activity=uCityRetail;
   // Each building and window has a stable bedtime; no frame-dependent flicker.
   activity = clamp(activity * (.80 + .40*vCityLight.x), 0.0, .985);
   vec2 room = floor(cell) + vCityLight.x * vec2(773.0,419.0) + vCityNormal.xz*31.0;
   float bedtime = cityHash(room);
   // Narrow the fade at very low occupancy so dark buildings stay dark at 4 am.
   float fade = min(.016,max(.0001,activity*.4));
   float lit = activity > 0.0 ? smoothstep(bedtime-fade,bedtime+fade,activity) : 0.0;
   vec3 warm = vec3(1.0,.63,.27), cool = vec3(.71,.85,1.0);
   float coolRooms = vCityLight.y > .5 && vCityLight.y < 1.5 ? .64 : vCityLight.y>3.5 ? .36 : .17;
   vec3 lightColour = mix(mix(warm,cool,coolRooms),mix(warm,cool,step(1.0-coolRooms,cityHash(room+97.0))),detailAA);
   diffuseColor.rgb *= 1.0-wall*windowMask*.28*detailAA;
  `).replace('#include <emissivemap_fragment>',`#include <emissivemap_fragment>
   // At a distance integrate coverage instead of aliasing sub-pixel windows.
   float windowLight = mix(.12*activity,windowMask*lit,detailAA);
   float softSpill = mix(.025*activity,glowMask*lit*.12,detailAA);
   // Small, independent low-frequency scintillation. Nearby windows stay steady.
   float distanceM = length(vViewPosition);
   float distant = smoothstep(650.0,3500.0,distanceM);
   float phase = mix(vCityLight.x,cityHash(room+57.0),detailAA)*6.2831853;
   float turbulence = sin(uCitySeconds*.83+phase)*.65 + sin(uCitySeconds*1.71+phase*2.37)*.35;
   float transmission = exp(-max(distanceM-400.0,0.0)/24000.0);
   float shimmer = 1.0 + .045*distant*uCityShimmer*turbulence;
   totalEmissiveRadiance += lightColour * (windowLight+softSpill) * wall * uCityNight * 1.8 * transmission * shimmer;
  `);
 };
 return material;
}
export async function makeBuildings(features,onProgress,options={}){
 const group=new THREE.Group();group.name='OSM building footprints';const lighting=options.lighting||{night:{value:0},activity:{value:new Float32Array([.8,.6,.9,.7])},retail:{value:.9},elapsed:{value:0},shimmer:{value:0}},night=lighting.night;
 const palette=['#d9d8c5','#ebe7d5','#b6c9c1','#a5bcb8','#c1c3b6','#e0d7bc','#8aafac','#bdc6bf'];
 const materials=palette.map(c=>facadeMaterial(c,lighting)),bins=palette.map(()=>[]);let totalVertices=0;
 for(let i=0;i<features.length;i++){
   const b=features[i];
   if(i%128===0)await new Promise(resolve=>setTimeout(resolve,0));
   const geo=extrudeBuilding(b),n=geo.attributes.position.count;
   geo.setAttribute('feature',new THREE.Float32BufferAttribute(new Float32Array(n).fill(i),1));
   const style=buildingLighting(b),light=new Float32Array(n*4);
   for(let v=0;v<n;v++)light.set([style.seed,style.profile,style.base,style.retailTop],v*4);
   geo.setAttribute('cityLight',new THREE.BufferAttribute(light,4));
   const id=Number(b.id.split('/')[1]);const bucket=b.height>150?6:b.material==='glass'?2:b.height>65?3:id%6;
   geo.clearGroups();bins[bucket].push(geo);totalVertices+=n;
 }
 for(let i=0;i<bins.length;i++){
   if(!bins[i].length)continue;
   const geo=mergeGeometries(bins[i],false);for(const g of bins[i])g.dispose();
   const mesh=new THREE.Mesh(geo,materials[i]);mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);
   onProgress?.(i);await new Promise(resolve=>setTimeout(resolve,0));
 }
 return {group,night,materials,totalVertices};
}
export function makeRoads(roads,sampler,lighting){
 const group=new THREE.Group();group.name='Streets and paths';const surfaces={road:[],path:[],bridge:[]},uvs={road:[],path:[],bridge:[]};
 const widthFor={motorway:15,trunk:13,primary:11,secondary:9,tertiary:8,residential:6,unclassified:6,service:4,living_street:5,pedestrian:5,footway:2.1,path:1.7,steps:2,cycleway:2.5,runway:45,taxiway:20};
 for(const r of roads){
  const width=widthFor[r.kind]||5,isPath=['footway','path','steps','pedestrian'].includes(r.kind),target=surfaces[r.bridge?'bridge':isPath?'path':'road'];
  const lift=r.bridge?Math.max(5,r.layer*5):.18;let along=0;const uv=uvs[r.bridge?'bridge':isPath?'path':'road'];
  for(let j=1;j<r.path.length;j++){
   const a=r.path[j-1],b=r.path[j],dx=b[0]-a[0],dz=b[1]-a[1],length=Math.hypot(dx,dz);if(length<.1)continue;
   const steps=Math.ceil(length/15),nx=-dz/length*width/2,nz=dx/length*width/2;
   for(let s=0;s<steps;s++){
    const ax=a[0]+dx*s/steps,az=a[1]+dz*s/steps,bx=a[0]+dx*(s+1)/steps,bz=a[1]+dz*(s+1)/steps;
    const corners=[[ax+nx,az+nz],[ax-nx,az-nz],[bx+nx,bz+nz],[bx-nx,bz-nz]].map(([x,z])=>[x,sampler.height(x,z)+lift,z]);
    for(const k of [0,2,1,1,2,3]){target.push(...corners[k]);uv.push(along+length*(s+(k>1?1:0))/steps,k%2);}
   }
   along+=length;
  }
 }
 for(const [name,p] of Object.entries(surfaces)){
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(p,3));geo.setAttribute('uv',new THREE.Float32BufferAttribute(uvs[name],2));geo.computeVertexNormals();
  const mat=new THREE.MeshStandardMaterial({color:name==='path'?'#e0d9bd':name==='bridge'?'#bcc3b7':'#939f95',roughness:1,side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2});
  if(lighting&&name!=='path')mat.onBeforeCompile=shader=>{
   shader.uniforms.uCityNight=lighting.night;
   shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec2 vStreetUV;').replace('#include <begin_vertex>','#include <begin_vertex>\nvStreetUV = uv;');
   shader.fragmentShader=shader.fragmentShader.replace('#include <common>','#include <common>\nvarying vec2 vStreetUV; uniform float uCityNight;').replace('#include <emissivemap_fragment>',`#include <emissivemap_fragment>
    float pool = pow(.5+.5*cos(vStreetUV.x*.1496),8.0) * pow(abs(vStreetUV.y-.5)*2.0,2.0);
    float resolved = 1.0-smoothstep(10.0,45.0,fwidth(vStreetUV.x));
    totalEmissiveRadiance += vec3(1.0,.67,.32) * mix(.06,pool*.45+.015,resolved) * uCityNight;
   `);
  };
  const mesh=new THREE.Mesh(geo,mat);mesh.receiveShadow=true;group.add(mesh);
 }
 return group;
}
export function makeNature(parks,terrain,sampler,index,options={}){
 const group=new THREE.Group(),points=[],rng=random(options.seed??163);const {w,h,elev,vegetation}=terrain,g=terrain.meta.georef;
 // Landcover-backed trees only. Avoid buildings and keep a compact urban draw budget.
 for(let r=0;r<h;r++)for(let c=0;c<w;c++){
  const i=r*w+c;if(!vegetation[i]||elev[i]<5)continue;
  const x=g.bE+c*g.aE-ORIGIN[0],z=ORIGIN[1]-(g.bN+r*g.aN);
  const bounds=options.bounds||[-4200,-2300,4200,4000];
  if(x<bounds[0]||x>=bounds[2]||z<bounds[1]||z>=bounds[3])continue;
  for(let j=0;j<3;j++){const px=x+(rng()-.5)*55,pz=z+(rng()-.5)*55;if(!index.collision(px,pz,0,1000,5))points.push([px,pz,4+rng()*6]);}
 }
 const parkGeos=[];
 for(const park of parks){
  const ring=park.rings[0],xs=ring.map(p=>p[0]),zs=ring.map(p=>p[1]);
  const shape=new THREE.Shape(ring.slice(0,-1).map(p=>new THREE.Vector2(p[0],-p[1])));for(const hole of park.rings.slice(1))shape.holes.push(new THREE.Path(hole.slice(0,-1).map(p=>new THREE.Vector2(p[0],-p[1]))));
  const geo=new THREE.ShapeGeometry(shape);geo.rotateX(-Math.PI/2);const p=geo.attributes.position;
  for(let i=0;i<p.count;i++)p.setY(i,sampler.height(p.getX(i),p.getZ(i))+.12);geo.computeVertexNormals();parkGeos.push(geo);
  const minX=Math.min(...xs),maxX=Math.max(...xs),minZ=Math.min(...zs),maxZ=Math.max(...zs);
  for(let x=minX;x<maxX;x+=21)for(let z=minZ;z<maxZ;z+=21){const px=x+rng()*15,pz=z+rng()*15;if(inPolygon(px,pz,park.rings)&&!index.collision(px,pz,0,1000,5))points.push([px,pz,4+rng()*4]);}
 }
 if(parkGeos.length){const geo=mergeGeometries(parkGeos);for(const g of parkGeos)g.dispose();const mesh=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:'#8da277',roughness:1,side:THREE.DoubleSide}));mesh.receiveShadow=true;group.add(mesh);}
 const canopy=new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1,1),new THREE.MeshStandardMaterial({color:'#ffffff',roughness:1}),points.length);
 const trunks=new THREE.InstancedMesh(new THREE.CylinderGeometry(.35,.5,1,5),new THREE.MeshStandardMaterial({color:'#827f5e',roughness:1}),points.length);
 const dummy=new THREE.Object3D(),greens=['#587b55','#759165','#65845c','#8a9d71'].map(colour);
 points.forEach(([x,z,h],i)=>{const ground=sampler.height(x,z);dummy.position.set(x,ground+h*.65,z);dummy.scale.set(h*.48,h*.58,h*.43);dummy.rotation.y=rng()*Math.PI;dummy.updateMatrix();canopy.setMatrixAt(i,dummy.matrix);canopy.setColorAt(i,greens[i%greens.length]);dummy.position.y=ground+h*.25;dummy.scale.set(1,h*.5,1);dummy.updateMatrix();trunks.setMatrixAt(i,dummy.matrix);});
 canopy.castShadow=true;canopy.receiveShadow=true;group.add(canopy,trunks);return {group,count:points.length};
}
export function makeFerries(){
 const group=new THREE.Group();const ferries=[];const mat=c=>new THREE.MeshStandardMaterial({color:c,roughness:.6});
 for(let i=0;i<3;i++){
  const boat=new THREE.Group();
  for(const [size,pos,c] of [[[9,3,24],[0,2,0],'#e5e6ce'],[[8,4,20],[0,5,0],'#397862'],[[8.7,.5,21],[0,7.2,0],'#f4f0d7'],[[6,2,7],[0,8,4],'#e2e4ce']]){const m=new THREE.Mesh(new THREE.BoxGeometry(...size),mat(c));m.position.set(...pos);boat.add(m);}
  const wake=new THREE.Mesh(new THREE.PlaneGeometry(11,48),new THREE.MeshBasicMaterial({color:'#d3e7d9',transparent:true,opacity:.16,depthWrite:false}));wake.rotation.x=-Math.PI/2;wake.position.set(0,.4,-28);boat.add(wake);group.add(boat);ferries.push(boat);
 }
 const update=t=>ferries.forEach((b,i)=>{const phase=t/190+i/3,u=(Math.sin(phase*Math.PI*2)+1)/2; b.position.set(80+790*u,.3,-85-570*u);b.rotation.y=Math.atan2(790,-570)+(Math.cos(phase*Math.PI*2)<0?Math.PI:0);});
 return {group,update};
}
