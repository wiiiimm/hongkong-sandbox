import * as THREE from '../vendor/three.module.js';
import {random} from './geo.js';
import {createWeatherData,DEFAULT_WEATHER} from './weather-data.js';

const clamp=x=>Math.max(0,Math.min(1,x));
// Returned atmosphere parameters are visual estimates in the city's metre-scale world.
export function weatherAtmosphere(settings=DEFAULT_WEATHER){
 const cloudCover=clamp(settings.clouds),wet=Math.max(settings.rain,settings.snow*.4);
 const visibilityMetres=Math.max(650,30000*Math.exp(-settings.fog*3.45-wet*.45));
 const radians=(settings.windFrom??0)*Math.PI/180,speed=Number.isFinite(settings.windFrom)?settings.wind*18:0;
 return {fogDensity:Math.sqrt(-Math.log(.02))/visibilityMetres,visibilityMetres,cloudCover,ambientMultiplier:1-cloudCover*.24-wet*.08,sunMultiplier:1-cloudCover*.80,skyMultiplier:1-cloudCover*.22,wetness:settings.rain,waveStrength:settings.waves,windVector:{x:-Math.sin(radians)*speed,z:Math.cos(radians)*speed}};
}
function cloudTexture(){
 const size=96,data=new Uint8Array(size*size*4);
 for(let y=0;y<size;y++)for(let x=0;x<size;x++){
  const u=(x/(size-1)-.5)*2,v=(y/(size-1)-.5)*2;
  const lobe=(cx,cy,sx,sy)=>Math.exp(-((u-cx)**2/sx+(v-cy)**2/sy)*3.5);
  const density=lobe(-.3,.10,.42,.33)+lobe(.12,-.02,.50,.58)+lobe(.44,.12,.21,.25);
  const edge=Math.max(0,1-u*u)*Math.max(0,1-v*v);
  const wisps=.94+.06*Math.sin(x*.4)*Math.sin(y*.47);
  const i=(y*size+x)*4;data[i]=data[i+1]=data[i+2]=255;data[i+3]=Math.round(Math.min(.78,density*.48)*edge*wisps*255);
 }
 const texture=new THREE.DataTexture(data,size,size,THREE.RGBAFormat);texture.needsUpdate=true;return texture;
}
function makeClouds(){
 const texture=cloudTexture(),geometry=new THREE.PlaneGeometry(1,1);
 const uniforms={map:{value:texture},cover:{value:0},tint:{value:new THREE.Color('#f1f0e5')},...THREE.UniformsUtils.clone(THREE.UniformsLib.fog)};
 const material=new THREE.ShaderMaterial({uniforms,transparent:true,depthWrite:false,fog:true,
  vertexShader:`#include <common>
   #include <fog_pars_vertex>
   #include <logdepthbuf_pars_vertex>
   varying vec2 vUv; varying float vCloudIndex;
   void main(){
    vUv=uv;vCloudIndex=instanceMatrix[3].w;
    vec4 centre=modelViewMatrix*vec4(instanceMatrix[3].xyz,1.0);
    vec4 mvPosition=centre+vec4(position.x*instanceMatrix[0].x,position.y*instanceMatrix[1].y,0.0,0.0);
    gl_Position=projectionMatrix*mvPosition;
    #include <logdepthbuf_vertex>
    #include <fog_vertex>
   }`,
  fragmentShader:`#include <common>
   #include <fog_pars_fragment>
   #include <logdepthbuf_pars_fragment>
   uniform sampler2D map;uniform float cover;uniform vec3 tint;
   varying vec2 vUv;varying float vCloudIndex;
   void main(){
    float visible=smoothstep(vCloudIndex-.07,vCloudIndex+.07,cover);
    float alpha=texture2D(map,vUv).a*visible*(.52+cover*.32);
    if(alpha<.004)discard;
    gl_FragColor=vec4(tint,alpha);
    #include <logdepthbuf_fragment>
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
    #include <fog_fragment>
   }`,
 });
 const mesh=new THREE.InstancedMesh(geometry,material,80),rnd=random(422);
 const matrix=new THREE.Matrix4(),positions=[];
 for(let i=0;i<80;i++){
  // Stratified sky coverage: no territory-size particle field or global geometry rebuild.
  const col=i%10,row=Math.floor(i/10),x=(col-4.5)*2000+(rnd()-.5)*1000,z=(row-3.5)*2300+(rnd()-.5)*1000;
  const y=1050+rnd()*800,sx=1800+rnd()*1900,sy=420+rnd()*470,threshold=(i*.61803398875)%1;
  matrix.makeScale(sx,sy,1);matrix.setPosition(x,y,z);
  matrix.elements[15]=threshold; // shader treats this slot as a stable per-cloud coverage threshold.
  mesh.setMatrixAt(i,matrix);positions.push({x,y,z,sx,sy,threshold});
 }
 mesh.frustumCulled=false;mesh.name='Local weather · soft cloud deck';mesh.renderOrder=2;
 return {mesh,uniforms,positions,matrix,texture};
}
function makeRain(){
 const count=2400,data=new Float32Array(count*6),seeds=new Float32Array(count*3),rnd=random(905);
 for(let i=0;i<count;i++)seeds.set([rnd(),rnd(),rnd()],i*3);
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(data,3).setUsage(THREE.DynamicDrawUsage));
 const material=new THREE.LineBasicMaterial({color:'#b6d6df',transparent:true,opacity:.24,depthWrite:false,fog:true});
 const mesh=new THREE.LineSegments(geometry,material);mesh.frustumCulled=false;mesh.name='Local weather · rain';return {mesh,seeds,data,count};
}
function makeSnow(){
 const count=900,seeds=new Float32Array(count*3),data=new Float32Array(count*3),rnd=random(633);
 for(let i=0;i<count;i++)seeds.set([rnd(),rnd(),rnd()],i*3);
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(data,3).setUsage(THREE.DynamicDrawUsage));
 const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,fog:true,
  uniforms:{tint:{value:new THREE.Color('#f7faf8')},...THREE.UniformsUtils.clone(THREE.UniformsLib.fog)},
  vertexShader:`#include <common>
   #include <fog_pars_vertex>
   #include <logdepthbuf_pars_vertex>
   void main(){vec4 mvPosition=modelViewMatrix*vec4(position,1.);gl_Position=projectionMatrix*mvPosition;gl_PointSize=clamp(100./max(1.,-mvPosition.z),1.,3.5);
    #include <logdepthbuf_vertex>
    #include <fog_vertex>
   }`,
  fragmentShader:`#include <common>
   #include <fog_pars_fragment>
   #include <logdepthbuf_pars_fragment>
   uniform vec3 tint;
   void main(){float edge=1.-smoothstep(.16,.5,length(gl_PointCoord-vec2(.5)));if(edge<.01)discard;gl_FragColor=vec4(tint,edge*.8);
    #include <logdepthbuf_fragment>
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
    #include <fog_fragment>
   }`,
 });
 const mesh=new THREE.Points(geometry,material);mesh.frustumCulled=false;mesh.name='Local weather · manual snow';return {mesh,seeds,data,count};
}
const wrap=(x,size)=>((x%size)+size)%size;
export function createWeather({scene,camera,...options}){
 const data=createWeatherData(options),cloud=makeClouds(),rain=makeRain(),snow=makeSnow();
 const group=new THREE.Group();group.name='City weather';group.add(cloud.mesh,rain.mesh,snow.mesh);scene.add(group);
 let elapsed=0,positionTimer=Infinity,lastX=Infinity,lastZ=Infinity,disposed=false;
 function update(dt,{position=camera.position,reducedMotion=false,paused=false,night=0,suspended=false}={}){
  if(disposed)return weatherAtmosphere(DEFAULT_WEATHER);
  const delta=Math.max(0,Math.min(.1,Number.isFinite(dt)?dt:0));positionTimer+=delta;
  if(positionTimer>=1&&(Math.hypot(position.x-lastX,position.z-lastZ)>100||lastX===Infinity)){
   data.setPosition(position);positionTimer=0;lastX=position.x;lastZ=position.z;
  }
  if(!paused&&!suspended)data.poll();
  const settings=data.state.settings,atmosphere=weatherAtmosphere(suspended?{...DEFAULT_WEATHER,clouds:0,rain:0,snow:0,fog:0,waves:0}:settings);
  group.visible=!suspended;
  if(!paused&&!reducedMotion)elapsed+=delta;
  const wind=atmosphere.windVector;
  cloud.mesh.visible=settings.clouds>.005;
  cloud.uniforms.cover.value=settings.clouds;
  cloud.uniforms.tint.value.set('#f2f1e8').lerp(new THREE.Color('#506078'),clamp(night)*.82).multiplyScalar(1-settings.rain*.24);
  // Re-centre on a kilometre grid so walking does not visibly drag the clouds.
  cloud.mesh.position.set(Math.round(position.x/2000)*2000,0,Math.round(position.z/2000)*2000);
  for(let i=0;i<cloud.positions.length;i++){
   const p=cloud.positions[i];cloud.matrix.makeScale(p.sx,p.sy,1);
   cloud.matrix.setPosition(wrap(p.x+wind.x*elapsed*.35+11000,22000)-11000,p.y,wrap(p.z+wind.z*elapsed*.35+11000,22000)-11000);
   cloud.matrix.elements[15]=p.threshold;cloud.mesh.setMatrixAt(i,cloud.matrix);
  }
  cloud.mesh.instanceMatrix.needsUpdate=true;
  // Avoid snow/rain motion under reduced motion; fog, cloud cover and wet surfaces still communicate weather.
  const belowCloud=camera.position.y<1650;
  rain.mesh.visible=settings.rain>.005&&!reducedMotion&&belowCloud;
  snow.mesh.visible=settings.snow>.005&&!reducedMotion&&belowCloud;
  const cx=camera.position.x,cy=camera.position.y,cz=camera.position.z;
  if(rain.mesh.visible){
   const n=Math.round(rain.count*settings.rain),size=180,fall=24+settings.rain*15;
   rain.mesh.geometry.setDrawRange(0,n*2);rain.mesh.material.opacity=.14+settings.rain*.28;
   for(let i=0;i<n;i++){
    const s=i*3,j=i*6,x=cx+wrap(rain.seeds[s]*size+wind.x*elapsed,size)-size/2;
    const z=cz+wrap(rain.seeds[s+2]*size+wind.z*elapsed,size)-size/2,y=cy+wrap(rain.seeds[s+1]*100-elapsed*fall,100)-25;
    rain.data.set([x,y,z,x-wind.x*.035,y+1.4+settings.rain,z-wind.z*.035],j);
   }
   rain.mesh.geometry.attributes.position.needsUpdate=true;
  }
  if(snow.mesh.visible){
   const n=Math.round(snow.count*settings.snow),size=140;snow.mesh.geometry.setDrawRange(0,n);
   for(let i=0;i<n;i++){
    const j=i*3;snow.data.set([cx+wrap(snow.seeds[j]*size+wind.x*elapsed*.5+Math.sin(elapsed*.6+i)*2,size)-size/2,cy+wrap(snow.seeds[j+1]*80-elapsed*2.1,80)-20,cz+wrap(snow.seeds[j+2]*size+wind.z*elapsed*.5,size)-size/2],j);
   }
   snow.mesh.geometry.attributes.position.needsUpdate=true;
  }
  return atmosphere;
 }
 return {update,setManual:values=>data.setManual(values),setLive:value=>data.setLive(value),refresh:()=>data.refresh(),
  get state(){return {...data.state,elapsed};},
  dispose(){if(disposed)return;disposed=true;data.dispose();scene.remove(group);for(const mesh of [cloud.mesh,rain.mesh,snow.mesh]){mesh.geometry.dispose();mesh.material.dispose();}cloud.texture.dispose();},
 };
}
