import * as THREE from '../vendor/three.module.js';
import {distanceToBounds} from './tile-cache.js';

// These are the original staged parents, not inferred building or walking IDs.
export const CABLE_SOURCE_PARENTS=Object.freeze({
 'tsing-ma':Object.freeze(['I244492317107063C0','I254702348107063C0','B250112338101063C0','B250222334201063C0','B263302377501063C0','B263422373701063C0'].map(id=>'landsd-infrastructure/'+id)),
 'ting-kau':Object.freeze(['landsd-infrastructure/I259872443407063C0']),
});
const names={'tsing-ma':'Tsing Ma · illustrative suspension cables','ting-kau':'Ting Kau · illustrative stay cables'};
const chinese={'tsing-ma':'青馬大橋 · 纜索示意','ting-kau':'汀九橋 · 斜拉索示意'};
function prepare(data,parents){
 const m=data?.modelGeometry,p=m?.position,b=m?.worldBounds,required=parents[data?.region];
 if(data?.schemaVersion!==1||data.kind!=='illustrative-bridge-cables'||data.estimatedGeometry!==true||data.walkable!==false||typeof data.id!=='string'||!data.id||!required?.length||!required.every(id=>typeof id==='string'&&id)||typeof data.sourceUrl!=='string'||!/^https?:\/\//.test(data.sourceUrl)||!Array.isArray(data.limits)||!data.limits.every(s=>typeof s==='string')||!Array.isArray(p)||!p.length||p.length%9||p.length>900000||!p.every(Number.isFinite)||!['normal','colour'].every(key=>Array.isArray(m[key])&&m[key].length===p.length&&m[key].every(Number.isFinite))||!Array.isArray(b)||b.length!==2||!b.every(v=>Array.isArray(v)&&v.length===3&&v.every(Number.isFinite))||b[0].some((v,i)=>v>b[1][i])||data.counts?.originalSourceModels!==0||data.counts?.illustrativeTriangles!==p.length/9||m.triangles!==p.length/9)throw Error('Invalid illustrative cable packet');
 if(m.colour.some(v=>v<0||v>1))throw Error('Invalid illustrative cable colours');
 for(let i=0;i<p.length;i++)if(p[i]<b[0][i%3]-.001||p[i]>b[1][i%3]+.001)throw Error('Illustrative cable bounds mismatch');
 let surface=false;for(let i=0;i<p.length&&!surface;i+=9){const a=new THREE.Vector3(p[i+3]-p[i],p[i+4]-p[i+1],p[i+5]-p[i+2]),c=new THREE.Vector3(p[i+6]-p[i],p[i+7]-p[i+1],p[i+8]-p[i+2]);surface=a.cross(c).lengthSq()>1e-16;}
 if(!surface)throw Error('Empty illustrative cable geometry');
 return {...data,name:names[data.region]||data.id,zh:chinese[data.region]||'',source:data.sourceUrl,sourceTriangles:0,illustrativeTriangles:p.length/9,requiredParents:[...required],worldBounds:b,bounds:[b[0][0],b[0][2],b[1][0],b[1][2]],focus:b[0].map((v,i)=>(v+b[1][i])/2),accessNote:'Illustrative cable geometry. No walking surface or public access is added.'};
}
function geometry(record){
 const g=new THREE.BufferGeometry(),m=record.modelGeometry;
 for(const [key,field]of [['position','position'],['normal','normal'],['color','colour']])g.setAttribute(key,new THREE.Float32BufferAttribute(m[field],3));
 g.computeBoundingBox();g.computeBoundingSphere();return g;
}
export class BridgeCables {
 constructor({scene,onChange,parentsByRegion=CABLE_SOURCE_PARENTS,fetchImpl=globalThis.fetch}={}){
  this.group=new THREE.Group();this.group.name='Illustrative bridge cables · not surveyed geometry';scene?.add(this.group);
  this.onChange=onChange;this.parentsByRegion=parentsByRegion;this.fetch=fetchImpl.bind(globalThis);this.records=new Map();this.meshes=new Map();this.requests=new Map();this.errors=new Map();this.loadedPackages=new Set();this.focus=[0,0];this.radius=3000;this.parentSourceIds=new Set();this.closed=false;
 }
 load(url){
  if(this.closed)return Promise.resolve(false);if(this.loadedPackages.has(url))return Promise.resolve(true);if(this.requests.has(url))return this.requests.get(url).promise;
  const controller=new AbortController();this.errors.delete(url);
  const promise=Promise.resolve().then(async()=>{
   try{
    if(this.closed)return false;const response=await this.fetch(url,{signal:controller.signal});if(!response.ok)throw Error('HTTP '+response.status);
    const record=prepare(await response.json(),this.parentsByRegion);if(this.closed||controller.signal.aborted)return false;
    const old=this.records.get(record.id);
    if(old&&(old.region!==record.region||['position','normal','colour'].some(key=>old.modelGeometry[key].length!==record.modelGeometry[key].length||old.modelGeometry[key].some((v,i)=>v!==record.modelGeometry[key][i]))))throw Error('Conflicting illustrative cable packet '+record.id);
    if([...this.records.values()].some(r=>r.region===record.region&&r.id!==record.id))throw Error('Duplicate illustrative cable region '+record.region);
    if(!old){
     const mesh=new THREE.Mesh(geometry(record),new THREE.MeshStandardMaterial({vertexColors:true,roughness:.58,metalness:.32}));mesh.name=record.name;mesh.castShadow=mesh.receiveShadow=true;mesh.userData.cableId=record.id;mesh.visible=false;
     this.records.set(record.id,record);this.meshes.set(record.id,mesh);this.group.add(mesh);
    }
    this.loadedPackages.add(url);this.plan(...this.focus,this.radius,this.parentSourceIds);return true;
   }catch(error){if(!this.closed&&!controller.signal.aborted)this.errors.set(url,error.message||String(error));return false;}
   finally{this.requests.delete(url);if(!this.closed)this.onChange?.();}
  });
  this.requests.set(url,{controller,promise});this.onChange?.();return promise;
 }
 retry(){return Promise.all([...this.errors.keys()].map(url=>this.load(url))).then(values=>values.every(Boolean));}
 plan(x,z,radius=3000,parentSourceIds=this.parentSourceIds){
  if(this.closed||!Number.isFinite(x)||!Number.isFinite(z))return;
  this.focus=[x,z];this.radius=Number.isFinite(radius)?Math.max(0,Math.min(5000,radius)):3000;this.parentSourceIds=new Set(parentSourceIds||[]);
  for(const [id,record]of this.records)this.meshes.get(id).visible=record.requiredParents.every(parent=>this.parentSourceIds.has(parent))&&distanceToBounds(x,z,record.bounds)<=this.radius;
 }
 pickMeshes(){return this.closed||!this.group.visible?[]:[...this.meshes.values()].filter(mesh=>mesh.visible);}
 featureAt(hit){const mesh=hit?.object;return mesh?.parent===this.group&&this.pickMeshes().includes(mesh)?this.records.get(mesh.userData.cableId):undefined;}
 geometryFor(record){if(this.records.get(record.id)!==record)throw Error('Unknown illustrative cable selection');return geometry(record);}
 get stats(){const enabled=this.pickMeshes();return {packets:this.records.size,visiblePackets:enabled.length,illustrativeTriangles:[...this.records.values()].reduce((n,r)=>n+r.illustrativeTriangles,0),visibleTriangles:enabled.reduce((n,m)=>n+m.geometry.attributes.position.count/3,0),sourceTriangles:0,waitingForParents:[...this.records.values()].filter(r=>!r.requiredParents.every(id=>this.parentSourceIds.has(id))).map(r=>r.id),pending:this.requests.size,errors:[...this.errors.keys()]};}
 dispose(){if(this.closed)return;this.closed=true;for(const r of this.requests.values())r.controller.abort();this.requests.clear();for(const mesh of this.meshes.values()){mesh.geometry.dispose();mesh.material.dispose();}this.group.clear();this.group.removeFromParent();this.records.clear();this.meshes.clear();this.loadedPackages.clear();this.errors.clear();}
}
export const createBridgeCables=options=>new BridgeCables(options);
