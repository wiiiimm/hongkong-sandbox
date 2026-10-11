/** Original lower-envelope versus original TIN, diagnostic only; no acceptance edits. */
import {readFileSync,writeFileSync,existsSync,mkdirSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
const root=new URL('../../../',import.meta.url),[modelsPath,terrainPath,outPath]=process.argv.slice(2),inputHashes={};
assert(modelsPath&&terrainPath&&outPath&&!existsSync(new URL(outPath,root)));
const hash=b=>createHash('sha256').update(b).digest('hex');
function load(path){const raw=readFileSync(new URL(path,root));inputHashes[path]=hash(raw);return JSON.parse(gunzipSync(raw));}
const models=load(modelsPath).rows,terrains=load(terrainPath).rows,rows=[];
for(const model of models){
 const terrain=terrains.find(t=>t.uid===model.uid);assert(terrain);
 const encoded=Buffer.alloc(model.triangles.length*9*8);model.triangles.flat(2).forEach((v,i)=>encoded.writeDoubleLE(v,i*8));assert.equal(hash(encoded),model.worldTrianglesSHA256);
 const position=terrain.terrainTriangles.flat(2),surface=nativeTerrainSurface({position,index:Array.from({length:position.length/3},(_,i)=>i)});
 const inverted=model.triangles.flatMap(t=>t.flatMap(([x,y,z])=>[x,-y,z]));
 const envelope=nativeTerrainSurface({position:inverted,index:Array.from({length:inverted.length/3},(_,i)=>i)});
 let checks=0,lowerChecks=0,missingTerrain=0,missingLowerProfile=0,minLowerGap=Infinity,maxLowerGap=-Infinity,lowerWithinStrictContact=0,lowerBelowPenetrationLimit=0;const contactFaceOrientations={steep:0,upward:0,downward:0};
 const contacts=[];const bottom=model.worldBounds[0][1];
 const check=(x,y,z,kind,faceIndex,normalY)=>{checks++;const invertedHeight=envelope.height(x,z);if(invertedHeight===null){missingLowerProfile++;return;}const lower=-invertedHeight;
  // Classification diagnostic uses the existing sampler comparison allowance.
  if(Math.abs(y-lower)>.004)return;
  lowerChecks++;const ground=surface.height(x,z);if(ground===null){missingTerrain++;return;}const gap=y-ground;minLowerGap=Math.min(minLowerGap,gap);maxLowerGap=Math.max(maxLowerGap,gap);
  if(gap<-.5)lowerBelowPenetrationLimit++;
  if(gap>=-.5&&gap<=.1){lowerWithinStrictContact++;contactFaceOrientations[Math.abs(normalY)<.15?'steep':normalY>=0?'upward':'downward']++;if(contacts.length<100)contacts.push({faceIndex,faceNormalY:normalY,point:[x,y,z],ground,gap,kind,aboveGlobalBottomM:y-bottom,withinOldGlobalLowRim:y<=bottom+.35});}
 };
 for(let faceIndex=0;faceIndex<model.triangles.length;faceIndex++){const t=model.triangles[faceIndex],a=t[1].map((v,i)=>v-t[0][i]),b=t[2].map((v,i)=>v-t[0][i]),n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],length=Math.hypot(...n);if(length<1e-12)continue;const normalY=n[1]/length;for(const p of t)check(...p,'vertex',faceIndex,normalY);check(...[0,1,2].map(a=>t.reduce((s,p)=>s+p[a],0)/3),'face-centre',faceIndex,normalY);}
 rows.push({uid:model.uid,sourceSHA256:model.sourceSHA256,worldTrianglesSHA256:model.worldTrianglesSHA256,checks,lowerChecks,missingTerrain,missingLowerProfile,minLowerGap:Number.isFinite(minLowerGap)?minLowerGap:null,maxLowerGap:Number.isFinite(maxLowerGap)?maxLowerGap:null,lowerWithinStrictContact,lowerBelowPenetrationLimit,contactFaceOrientations,firstContacts:contacts,identityAccepted:false,installationApproved:false,qualification:'Lower-envelope contact evidence only. Source projection holes and unsupported separate components are not resolved. Face orientation is diagnostic only: upward ground/terrace faces cannot establish structural support. Original numeric global-rim gate is unchanged; no replacement metric, model, terrain or approval is produced.'});
}
for(const path of ['source-scripts/city/government-import/original-lower-profile-contact-diagnostic-v2.mjs','3d-viewer/city/native-terrain.js'])inputHashes[path]=hash(readFileSync(new URL(path,root)));
mkdirSync(new URL('.',new URL(outPath,root)),{recursive:true});writeFileSync(new URL(outPath,root),JSON.stringify({rows,inputHashes,publication:false,newlyInstalled:0,modelGeometryChanges:0,scriptExternalAICalls:0},null,2)+'\n');
console.log(JSON.stringify(rows.map(({firstContacts,...r})=>({...r,contactsOutsideGlobalLowRim:firstContacts.filter(c=>!c.withinOldGlobalLowRim).length}))));
