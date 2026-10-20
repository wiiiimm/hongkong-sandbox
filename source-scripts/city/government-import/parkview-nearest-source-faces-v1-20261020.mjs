/** Exact nearest finite source faces; diagnostic distances are not acceptance tolerances. */
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {supportSurface} from './support-contact.mjs';
const base=process.argv[2],out=process.argv[3],inputs=JSON.parse(gunzipSync(readFileSync(base+'/input.json.gz'))).rows,accounts=JSON.parse(gunzipSync(readFileSync(base+'/contacts.json.gz'))).rows,rows=[];
function nearest(g,p){const triangle=new THREE.Triangle(),point=new THREE.Vector3(...p),closest=new THREE.Vector3();let best=Infinity,record=null;for(let i=0;i<g.index.length;i+=3){[triangle.a,triangle.b,triangle.c].forEach((v,k)=>v.fromArray(g.position,g.index[i+k]*3));triangle.closestPointToPoint(point,closest);const distance=point.distanceToSquared(closest);if(distance<best){best=distance;record={faceIndex:i/3,distanceM:Math.sqrt(distance),closest:closest.toArray(),vertices:[triangle.a.toArray(),triangle.b.toArray(),triangle.c.toArray()]};}}return record;}
for(const r of inputs.filter(r=>r.mode==='literal')){
 const a=accounts.find(a=>a.uid===r.uid&&a.mode===r.mode),surface=supportSurface(r.support),points=[];
 for(const p of a.mapped.filter(p=>!p.supportFacesAtOriginalPoint.length)){
  const layers=surface.intersectionDetails(p.position[0],p.position[2]);
  points.push({...p,nearestOriginalPodium:nearest(r.support,p.position),layers:layers.map(layer=>({...layer,nearestOriginalTower:nearest(r.source,[p.position[0],layer.height,p.position[2]])}))});
 }
 const summary={uid:r.uid,mode:r.mode,points:points.length,nearestPodiumRangeM:[Math.min(...points.map(p=>p.nearestOriginalPodium.distanceM)),Math.max(...points.map(p=>p.nearestOriginalPodium.distanceM))],noProjectedPodiumLayer:points.filter(p=>!p.layers.length).length};
 rows.push({...summary,points,sourceWorldSHA256:r.sourceWorldSHA256,supportWorldSHA256:r.supportWorldSHA256,installationApproved:false});console.log(JSON.stringify(summary));
}
const inputHashes={};for(const p of [base+'/input.json.gz',base+'/contacts.json.gz','source-scripts/city/government-import/parkview-nearest-source-faces-v1-20261020.mjs','source-scripts/city/government-import/support-contact.mjs','3d-viewer/vendor/three.module.js'])inputHashes[p]=createHash('sha256').update(readFileSync(p)).digest('hex');
writeFileSync(out,gzipSync(JSON.stringify({rows,inputHashes,installationApproved:false,geometryChanges:0})));
