import * as THREE from '../vendor/three.module.js';
import {applyWaterSurfaceShader} from '../water-surface.js';
import {createWaterNoiseTexture,applyShorelineShader} from '../shoreline-surface.js';

const clamp=value=>Math.max(0,Math.min(1,Number.isFinite(Number(value))?Number(value):0));
// Water normals, rain pocks and glint are the original viewer's shared shader.
// Uniform surface heave is a small visual approximation, not a wave-height forecast.
export function createTidalWater(){
 const material=new THREE.MeshStandardMaterial({color:'#6caba4',roughness:.36,metalness:.25});
 const time={value:0},strength={value:.18},sunView=new THREE.Vector3(0,1,0);
 let shorelineTexture=null;const shoreMaterials=new Map();
 const shorelineUniforms={uWaterY:{value:.3},uBand:{value:.6},uWetAmt:{value:1},uFoamAmt:{value:.18},uCloudTex:{value:null},uCloudScale:{value:1/6000},uTime:time};
 const uniforms={uTime:time,uWaveAmp:{value:.05},uWaveK:{value:1100/63700},uSparkAmt:{value:0},uGlintAmt:{value:.55},uSunDirV:{value:sunView}};
 material.onBeforeCompile=shader=>{
  Object.assign(shader.uniforms,uniforms);
  shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vWpos;').replace('#include <begin_vertex>','#include <begin_vertex>\nvWpos=(modelMatrix * vec4(transformed,1.0)).xyz;');
  shader.fragmentShader=shader.fragmentShader.replace('#include <common>',`#include <common>
   varying vec3 vWpos; uniform float uTime; uniform float uWaveAmp; uniform float uWaveK;
   uniform float uSparkAmt; uniform float uGlintAmt; uniform vec3 uSunDirV;`);
  applyWaterSurfaceShader(shader);
 };
 material.customProgramCacheKey=()=> 'city-original-water-v1';
 const mesh=new THREE.Mesh(new THREE.PlaneGeometry(180000,180000),material);mesh.rotation.x=-Math.PI/2;mesh.position.y=.3;mesh.name='Hong Kong tidal water';
 let restingLevelHKPD=.3,waveOffset=0,phase=0,disposed=false,paused=false,reducedMotion=false,suspended=false;
 const state=()=>({restingLevelHKPD,renderedLevelHKPD:mesh.position.y,waveOffset,shaderTime:time.value,wavePhase:phase,waveStrength:strength.value,waveNormalAmplitude:uniforms.uWaveAmp.value,rainSpark:uniforms.uSparkAmt.value,glint:uniforms.uGlintAmt.value,paused,reducedMotion,suspended,approximateWaves:true,shorelineMaterials:shoreMaterials.size,wetBandMetres:shorelineUniforms.uBand.value,foamStrength:shorelineUniforms.uFoamAmt.value});
 return {
  mesh,material,time,strength,
  // Reuses each existing terrain material; no extra draw call or coastline geometry.
  attachShoreline(terrainRoot,{texture=null}={}){
   if(disposed)return;
   if(!shorelineTexture){shorelineTexture=texture||createWaterNoiseTexture();shorelineUniforms.uCloudTex.value=shorelineTexture;}
   terrainRoot.traverse(node=>{
    if(!node.isMesh)return;
    for(const mat of (Array.isArray(node.material)?node.material:[node.material])){
     if(!mat?.isMeshStandardMaterial||shoreMaterials.has(mat))continue;
     const previous=mat.onBeforeCompile,key=mat.customProgramCacheKey;
     const compile=(shader,renderer)=>{
      previous.call(mat,shader,renderer);Object.assign(shader.uniforms,shorelineUniforms);
      shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vWpos;').replace('#include <begin_vertex>','#include <begin_vertex>\nvWpos=(modelMatrix*vec4(transformed,1.0)).xyz;');
      shader.fragmentShader=shader.fragmentShader.replace('#include <common>',`#include <common>
       varying vec3 vWpos; uniform float uWaterY; uniform float uBand; uniform float uWetAmt; uniform float uFoamAmt;
       uniform sampler2D uCloudTex; uniform float uCloudScale; uniform float uTime;`);
      applyShorelineShader(shader);
     };
     shoreMaterials.set(mat,{previous,key,compile});mat.onBeforeCompile=compile;mat.customProgramCacheKey=()=>key.call(mat)+'-tidal-shore-v1';mat.needsUpdate=true;
    }
   });
  },
  get state(){return state();},
  get restingLevelHKPD(){return restingLevelHKPD;},
  get renderedLevelHKPD(){return mesh.position.y;},
  setLevel(level){if(!disposed&&typeof level==='number'&&Number.isFinite(level)){restingLevelHKPD=level;mesh.position.y=level+waveOffset;shorelineUniforms.uWaterY.value=mesh.position.y;}return state();},
  levelAt(){return mesh.position.y;},
  update(dt,{settings={},camera,sunDirection,night=0,paused:pause=false,reducedMotion:reduce=false,suspended:suspend=false}={}){
   if(disposed)return state();paused=!!pause;reducedMotion=!!reduce;suspended=!!suspend;
   const waves=clamp(settings.waves??strength.value),wind=clamp(settings.wind??.12),rain=clamp(settings.rain);
   if(!paused&&!suspended){
    strength.value=waves;
    if(!reducedMotion){
     const seconds=Math.max(0,Math.min(.1,Number(dt)||0));
     time.value+=seconds*.96*(1+wind*1.5);phase=(phase+seconds*1.8*(1+wind*3))%(2*Math.PI);
     // Zero-mean ±18 cm maximum: does not change the tide datum or admission level.
     waveOffset=waves>0?Math.sin(phase)*waves*(.04+wind*.14):0;
    }else waveOffset=0;
    uniforms.uWaveAmp.value=.05+waves*(.09+wind*.22);
    uniforms.uSparkAmt.value=reducedMotion?0:rain*(.35+.45*wind);
    uniforms.uGlintAmt.value=(.55+wind*.45)*(1-clamp(night)*.94);
    shorelineUniforms.uFoamAmt.value=(.18+waves*(.27+.4*wind))*(1-clamp(night)*.85);
   }
   if(sunDirection&&camera){sunView.copy(sunDirection).normalize().transformDirection(camera.matrixWorldInverse);}
   mesh.position.y=restingLevelHKPD+waveOffset;shorelineUniforms.uWaterY.value=mesh.position.y;return state();
  },
  dispose(){if(disposed)return;disposed=true;for(const [mat,old] of shoreMaterials){if(mat.onBeforeCompile===old.compile){mat.onBeforeCompile=old.previous;mat.customProgramCacheKey=old.key;mat.needsUpdate=true;}}shoreMaterials.clear();shorelineTexture?.dispose();mesh.removeFromParent();mesh.geometry.dispose();material.dispose();},
 };
}
