import {readFile,writeFile} from 'node:fs/promises';
import * as THREE from '../../../../3d-viewer/vendor/three.module.js';
import {makeNature} from '../../../../3d-viewer/city/world.js';
import {BuildingIndex,makeTerrainSampler,inPolygon} from '../../../../3d-viewer/city/geo.js';
import {CityStreaming,disposeGroup} from '../../../../3d-viewer/city/streaming.js';
const base=new URL('../../../../',import.meta.url),load=async path=>JSON.parse(await readFile(new URL(path,base),'utf8'));
const manifest=await load('3d-viewer/city/data/manifest.json'),terrain=await load('3d-viewer/city/data/terrain.json'),sampler=makeTerrainSampler(terrain),regional=await load('3d-viewer/city/data/regional/urban.json');
let treesInPark=0,treesInsidePitch=0;const examples=[];
for(const id of ['1_0','2_0']){
 const tile=manifest.tiles.find(t=>t.id===id);if(!tile)continue;const data=await load('3d-viewer/'+tile.url),parks=data.parks.filter(p=>p.name==='Victoria Park');if(!parks.length)continue;
 const [x,z]=id.split('_').map(Number),s=manifest.tileSize,nature=makeNature(data.parks,terrain,sampler,new BuildingIndex(data.buildings),{bounds:[x*s,z*s,(x+1)*s,(z+1)*s],seed:(x*73856093^z*19349663)>>>0});
 CityStreaming.prototype.setSurfaceExclusions.call({cache:{entries:new Map([[id,{nature}]])}},regional.surfaces);
 const mesh=nature.group.children.find(child=>child.isInstancedMesh),matrix=new THREE.Matrix4(),position=new THREE.Vector3();
 for(let i=0;i<mesh.count;i++){
  mesh.getMatrixAt(i,matrix);position.setFromMatrixPosition(matrix);
  if(!parks.some(park=>inPolygon(position.x,position.z,park.rings)))continue;treesInPark++;
  const pitch=regional.surfaces.find(p=>p.kind==='pitch'&&inPolygon(position.x,position.z,p.rings));
  if(pitch){treesInsidePitch++;if(examples.length<6)examples.push({treeWorld:[position.x,position.z],pitch: pitch.id,source:pitch.source,sport:pitch.tags?.sport});}
 }
 disposeGroup(nature.group);
}
const result={location:'Victoria Park',treesInPark,treesInsidePitch,examples};await writeFile(new URL('tree-overlap.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
