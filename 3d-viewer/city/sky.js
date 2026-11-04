import * as THREE from '../vendor/three.module.js';
import {starPosition} from '../vendor/astro.js';
import {getSkyState,horizontalDirection} from './sky-time.js';
export {getSkyState} from './sky-time.js';

const RAD=Math.PI/180;
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const smooth=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t);};

function starColour(bv){
 // B−V → an illustrative blue/white/amber appearance, preserving catalogue ordering.
 const colour=new THREE.Color('#d9e8ff');
 if(bv<.45)colour.lerp(new THREE.Color('#fff9ed'),clamp((bv+.3)/.75));
 else colour.set('#fff9ed').lerp(new THREE.Color('#ffbf82'),clamp((bv-.45)/1.35));
 return colour;
}

function starMaterial(){
 return new THREE.ShaderMaterial({
  uniforms:{uFade:{value:0},uMagnitude:{value:2.8},uPixelRatio:{value:Math.min(globalThis.devicePixelRatio||1,2)}},
  transparent:true,depthWrite:false,fog:false,blending:THREE.AdditiveBlending,
  vertexShader:`
   #include <common>
   #include <logdepthbuf_pars_vertex>
   attribute float magnitude; attribute vec3 starColour;
   varying vec3 vColour; varying float vFade;
   uniform float uMagnitude; uniform float uPixelRatio;
   void main(){
    vColour=starColour;
    vFade=smoothstep(0.0,.10,position.y)*(1.0-smoothstep(uMagnitude-.5,uMagnitude+.3,magnitude));
    gl_PointSize=clamp(5.1-magnitude*.72,1.4,7.0)*uPixelRatio;
    gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);
    #include <logdepthbuf_vertex>
   }`,
  fragmentShader:`
   #include <logdepthbuf_pars_fragment>
   uniform float uFade; varying vec3 vColour; varying float vFade;
   void main(){
    vec2 p=gl_PointCoord*2.0-1.0;float r=dot(p,p);
    float alpha=exp(-r*4.5)*(1.0-smoothstep(.65,1.0,r))*uFade*vFade;
    if(alpha<.006)discard;
    gl_FragColor=vec4(vColour,alpha);
    #include <logdepthbuf_fragment>
    #include <encodings_fragment>
   }`
 });
}

function lineMaterial(opacity){
 return new THREE.ShaderMaterial({
  uniforms:{uFade:{value:0},uOpacity:{value:opacity}},transparent:true,depthWrite:false,fog:false,
  vertexShader:`
   #include <common>
   #include <logdepthbuf_pars_vertex>
   varying float vAltitude;
   void main(){vAltitude=position.y;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);
    #include <logdepthbuf_vertex>
   }`,
  fragmentShader:`
   #include <logdepthbuf_pars_fragment>
   uniform float uFade;uniform float uOpacity;varying float vAltitude;
   void main(){float alpha=uFade*uOpacity*smoothstep(0.0,.08,vAltitude);if(alpha<.004)discard;
    gl_FragColor=vec4(.53,.73,1.0,alpha);
    #include <logdepthbuf_fragment>
    #include <encodings_fragment>
   }`
 });
}

function sunTexture(){
 const canvas=document.createElement('canvas');canvas.width=canvas.height=128;
 const ctx=canvas.getContext('2d'),gradient=ctx.createRadialGradient(64,64,0,64,64,64);
 gradient.addColorStop(0,'rgba(255,252,229,1)');gradient.addColorStop(.16,'rgba(255,246,218,1)');
 gradient.addColorStop(.19,'rgba(255,220,158,.65)');gradient.addColorStop(.40,'rgba(255,202,133,.11)');
 gradient.addColorStop(1,'rgba(255,189,117,0)');ctx.fillStyle=gradient;ctx.fillRect(0,0,128,128);
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;return texture;
}

function moonMaterial(){
 return new THREE.ShaderMaterial({
  uniforms:{uLight:{value:new THREE.Vector3()},uOpacity:{value:1}},transparent:true,depthWrite:false,fog:false,
  vertexShader:`
   #include <common>
   #include <logdepthbuf_pars_vertex>
   varying vec2 vUv;
   void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);
    #include <logdepthbuf_vertex>
   }`,
  fragmentShader:`
   #include <logdepthbuf_pars_fragment>
   uniform vec3 uLight;uniform float uOpacity;varying vec2 vUv;
   float sea(vec2 p,vec2 centre,float radius){return 1.0-smoothstep(radius*.55,radius,length(p-centre));}
   void main(){
    vec2 p=vUv*2.0-1.0;float rr=dot(p,p);if(rr>1.0)discard;
    vec3 normal=vec3(p,sqrt(1.0-rr));
    float direct=smoothstep(-.025,.045,dot(normal,uLight));
    float maria=sea(p,vec2(-.25,.28),.38)*.15+sea(p,vec2(.23,.12),.32)*.17+sea(p,vec2(-.08,-.21),.26)*.13;
    float limb=.72+.28*normal.z;
    vec3 lit=vec3(.86,.90,.95)*(1.0-maria)*limb;
    vec3 colour=lit*(.018+direct*.95);
    gl_FragColor=vec4(colour,(1.0-smoothstep(.965,1.0,rr))*uOpacity);
    #include <logdepthbuf_fragment>
    #include <encodings_fragment>
   }`
 });
}

/** Camera-centred, fog-free sky, using the original app's real star catalogue.
 * update() anchors every frame; ephemeris/star uploads are cached for 5 simulated seconds.
 * Coordinates are city axes (east +x, up +y, south +z), all directions are unit vectors.
 */
export async function createSky({scene,camera,catalogueURL=new URL('../data/hk-sky.json',import.meta.url)}){
 const response=await fetch(catalogueURL);if(!response.ok)throw new Error(`Sky catalogue: HTTP ${response.status}`);
 const catalogue=await response.json();
 if(!Array.isArray(catalogue.stars)||!Array.isArray(catalogue.constellations))throw new Error('Invalid sky catalogue');
 const group=new THREE.Group();group.name='Hong Kong sky';scene.add(group);
 const starCount=catalogue.stars.length,positions=new Float32Array(starCount*3),colours=new Float32Array(starCount*3),magnitudes=new Float32Array(starCount);
 const hrIndex=new Map(),members=new Map();
 catalogue.stars.forEach((star,i)=>{hrIndex.set(star[0],i);const c=starColour(star[4]);colours.set([c.r,c.g,c.b],i*3);magnitudes[i]=star[3];});
 const constellations=catalogue.constellations.map(c=>{
  const result={...c,segments:c.lines.map(([a,b])=>[hrIndex.get(a),hrIndex.get(b)]).filter(pair=>pair.every(Number.isInteger))};
  for(const hr of c.stars){if(!members.has(hr))members.set(hr,[]);members.get(hr).push({iau:c.iau,en:c.en,zh:c.zh});}
  return result;
 });
 const starGeo=new THREE.BufferGeometry();starGeo.setAttribute('position',new THREE.BufferAttribute(positions,3).setUsage(THREE.DynamicDrawUsage));
 starGeo.setAttribute('starColour',new THREE.BufferAttribute(colours,3));starGeo.setAttribute('magnitude',new THREE.BufferAttribute(magnitudes,1));
 const stars=new THREE.Points(starGeo,starMaterial());stars.name='BSC5 catalogue stars';stars.frustumCulled=false;group.add(stars);
 const figures=new THREE.LineSegments(new THREE.BufferGeometry(),lineMaterial(.18));figures.name='Constellation figures';figures.frustumCulled=false;group.add(figures);
 const selectedFigure=new THREE.LineSegments(new THREE.BufferGeometry(),lineMaterial(.82));selectedFigure.name='Selected constellation';selectedFigure.frustumCulled=false;group.add(selectedFigure);
 const sunMap=sunTexture(),sun=new THREE.Sprite(new THREE.SpriteMaterial({map:sunMap,transparent:true,depthWrite:false,fog:false,blending:THREE.AdditiveBlending}));sun.name='Sun';group.add(sun);
 const moon=new THREE.Mesh(new THREE.PlaneGeometry(2,2),moonMaterial());moon.name='Moon';moon.frustumCulled=false;group.add(moon);
 const right=new THREE.Vector3(),up=new THREE.Vector3(),toViewer=new THREE.Vector3(),solarVector=new THREE.Vector3(),rotation=new THREE.Matrix4(),raycaster=new THREE.Raycaster();
 const A=new THREE.Vector3(),B=new THREE.Vector3(),P=new THREE.Vector3();
 let astronomy=null,lastKey='',disposed=false,showFigures=false,selected=null,presentation={stargazing:false,cloudCover:0,limitingMagnitude:2.8},visibleStars=0,starFade=0,coordinateUpdates=0;

 function writeLines(mesh,records){
  const values=[];
  for(const c of records)for(const [a,b]of c.segments){
   A.fromArray(positions,a*3);B.fromArray(positions,b*3);
   // Short spherical arcs remain on the distant sky rather than cutting through it.
   const count=Math.max(1,Math.ceil(A.angleTo(B)/(3*RAD)));
   for(let i=0;i<count;i++)for(const t of [i/count,(i+1)/count]){P.copy(A).lerp(B,t).normalize();values.push(P.x,P.y,P.z);}
  }
  const previous=mesh.geometry;mesh.geometry=new THREE.BufferGeometry();mesh.geometry.setAttribute('position',new THREE.Float32BufferAttribute(values,3));previous.dispose();
 }
 function choose(iau){
  const next=constellations.find(c=>c.iau===iau)||null;
  if(next?.iau===selected?.iau)return;
  selected=next;writeLines(selectedFigure,selected?[selected]:[]);
 }
 function update({date=new Date(),lat=22.3,lon=114.17,stargazing=false,cloudCover=0,limitingMagnitude=stargazing?5.3:2.8}={}){
  if(disposed)return;
  const key=`${Math.floor(date.getTime()/5000)}:${lat.toFixed(5)}:${lon.toFixed(5)}`;
  if(key!==lastKey){
   astronomy=getSkyState(date,lat,lon);
   for(let i=0;i<starCount;i++){
    const star=catalogue.stars[i],horizontal=starPosition(date,lat,lon,star[1]*15*RAD,star[2]*RAD),direction=horizontalDirection(horizontal.azimuth,horizontal.altitude);
    positions.set([direction.x,direction.y,direction.z],i*3);
   }
   starGeo.attributes.position.needsUpdate=true;writeLines(figures,constellations);writeLines(selectedFigure,selected?[selected]:[]);lastKey=key;coordinateUpdates++;
  }
  presentation={stargazing:!!stargazing,cloudCover:clamp(cloudCover),limitingMagnitude:clamp(limitingMagnitude,1,6)};
  const radius=Math.min(85000,camera.far*.82);group.position.copy(camera.position);group.scale.setScalar(radius);
  const moonWash=stargazing?1:1-.32*astronomy.moon.fraction*Math.max(0,astronomy.moon.direction.y);
  starFade=(stargazing?1:astronomy.starVisibility)*moonWash*(stargazing?1:1-smooth(.12,.92,presentation.cloudCover));
  stars.material.uniforms.uFade.value=starFade;stars.material.uniforms.uMagnitude.value=presentation.limitingMagnitude;
  stars.visible=starFade>.005;
  figures.material.uniforms.uFade.value=starFade;figures.visible=showFigures&&stars.visible;
  selectedFigure.material.uniforms.uFade.value=starFade;selectedFigure.visible=!!selected&&stars.visible;
  visibleStars=0;if(stars.visible)for(let i=0;i<starCount;i++)if(positions[i*3+1]>.02&&magnitudes[i]<presentation.limitingMagnitude+.3)visibleStars++;
  sun.position.copy(astronomy.sun.direction);sun.scale.setScalar(2*Math.tan(.533*RAD/.36));
  sun.visible=!stargazing&&astronomy.sun.altitudeDeg>-.3;sun.material.opacity=1-.88*presentation.cloudCover;
  sun.material.color.set('#ffffff').lerp(new THREE.Color('#ffbc79'),1-smooth(0,12,astronomy.sun.altitudeDeg));
  moon.position.copy(astronomy.moon.direction);moon.scale.setScalar(Math.tan(Math.asin(1737.4/astronomy.moon.distance)));
  moon.visible=astronomy.moon.altitudeDeg>0;
  moon.material.uniforms.uOpacity.value=(stargazing?1:1-.86*presentation.cloudCover)*(stargazing?1:.38+.62*astronomy.night);
  toViewer.copy(astronomy.moon.direction).multiplyScalar(-1);right.crossVectors(camera.up,toViewer);
  if(right.lengthSq()<1e-8)right.set(1,0,0);right.normalize();up.crossVectors(toViewer,right).normalize();
  rotation.makeBasis(right,up,toViewer);moon.quaternion.setFromRotationMatrix(rotation);
  solarVector.copy(astronomy.sun.direction);moon.material.uniforms.uLight.value.set(solarVector.dot(right),solarVector.dot(up),solarVector.dot(toViewer));
  return astronomy;
 }
 return {
  update,
  setConstellations(value){showFigures=!!value;figures.visible=showFigures&&stars.visible;},
  setSelectedConstellation:choose,
  // NDC x/y are in [-1,1]. Picks the closest visible catalogue star within 2.5°.
  // A click on a constellation member traces that figure and returns bilingual metadata.
  pick(ndc,angularTolerance=2.5){
   if(!astronomy||starFade<.01)return null;
   raycaster.setFromCamera(ndc,camera);const direction=raycaster.ray.direction;
   let best=-1,bestDot=Math.cos(angularTolerance*RAD);
   for(let i=0;i<starCount;i++){
    if(positions[i*3+1]<=.02||magnitudes[i]>presentation.limitingMagnitude+.3)continue;
    const dot=direction.x*positions[i*3]+direction.y*positions[i*3+1]+direction.z*positions[i*3+2];
    if(dot>bestDot){bestDot=dot;best=i;}
   }
   if(best<0){choose(null);return null;}
   const star=catalogue.stars[best],figuresForStar=members.get(star[0])||[];choose(figuresForStar[0]?.iau||null);
   return {hr:star[0],magnitude:star[3],altitudeDeg:Math.asin(clamp(positions[best*3+1],-1,1))/RAD,constellations:figuresForStar};
  },
  get state(){return {astronomy,catalogueStars:starCount,constellationCount:constellations.length,visibleStars,starFade,coordinateUpdates,...presentation,constellations:showFigures,selected:selected?{iau:selected.iau,en:selected.en,zh:selected.zh}:null};},
  dispose(){if(disposed)return;disposed=true;scene.remove(group);for(const object of [stars,figures,selectedFigure,moon]){object.geometry.dispose();object.material.dispose();}sun.material.dispose();sunMap.dispose();}
 };
}
