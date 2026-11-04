/** Private test adapter, deliberately not imported by the production viewer.
 * Hints require independently reviewed exact source and terrain evidence before
 * any publisher may persist them. This module grants no approval.
 */
import * as THREE from '../vendor/three.module.js';
import {mergeGeometries} from '../vendor/BufferGeometryUtils.js';
import {describeBuilding as originalDescription,createBuildingGeometry as originalGeometry} from './building-geometry-core.js';
import {sourceBoundBasicBottom} from './source-bound-basic-ground.js';

export function describeBuilding(building){
 const original=originalDescription(building);
 if(!building.nativeFallbackGround||building.modelGeometry)return original;
 const bottom=sourceBoundBasicBottom(building),core=original.parts.find(p=>p.kind==='building');
 if(!core||original.openSided||original.model||core.bottom!==building.nativeFallbackGround.originalBottom)throw new Error('BASIC continuation requires an unchanged ordinary core');
 const continuation={kind:'basic-ground-continuation',rings:core.rings,bounds:core.bounds,bottom,top:core.bottom,windows:false,illustrative:true};
 return {...original,parts:[...original.parts,continuation],sourceBoundBasicContinuation:true};
}
export function collisionVolumes(building){return describeBuilding(building).parts;}
export function createBuildingGeometry(building){
 const description=describeBuilding(building),core=originalGeometry(building);
 const part=description.parts.find(p=>p.kind==='basic-ground-continuation');
 if(!part)return core;
 const open=ring=>ring.length>1&&ring[0][0]===ring.at(-1)[0]&&ring[0][1]===ring.at(-1)[1]?ring.slice(0,-1):ring;
 const path=ring=>open(ring).map(([x,z])=>new THREE.Vector2(x,-z));
 const shape=new THREE.Shape(path(part.rings[0]));
 for(const hole of part.rings.slice(1))shape.holes.push(new THREE.Path(path(hole)));
 const addition=new THREE.ExtrudeGeometry(shape,{depth:part.top-part.bottom,bevelEnabled:false,steps:1,curveSegments:1});
 // Snap only NEW vertices at both planes. The original body and roof arrays are
 // retained byte for byte, including their original Float32 endpoint rounding.
 const positions=addition.attributes.position;
 for(let i=0;i<positions.count;i++){
  const x=positions.getX(i),z=-positions.getY(i),upper=positions.getZ(i)>0;
  positions.setXYZ(i,x,Math.fround(upper?part.top:part.bottom),z);
 }
 addition.computeVertexNormals();addition.clearGroups();
 addition.setAttribute('cityWindows',new THREE.Float32BufferAttribute(new Float32Array(positions.count),1));
 const result=mergeGeometries([core,addition],false);
 core.dispose();addition.dispose();
 if(!result)throw new Error('BASIC continuation merge failed');
 return result;
}
