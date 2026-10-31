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
 let checks=0,lowerChecks=0,missingTerrain=0,missingLowerProfile=0,minLowerGap=Infinity,maxLowerGap=-Infinity,lowerWithinStrictContact=0,lowerBelowPenetrationLimit=0;
 const contacts=[];const bottom=model.worldBounds[0][1];
 const check=(x,y,z,kind)=>{checks++;const invertedHeight=envelope.height(x,z);if(invertedHeight===null){missingLowerProfile++;return;}const lower=-invertedHeight;
  // Classification diagnostic uses the existing sampler comparison allowance.
  if(Math.abs(y-lower)>.004)return;
  lowerChecks++;const ground=surface.height(x,z);if(ground===null){missingTerrain++;return;}const gap=y-ground;minLowerGap=Math.min(minLowerGap,gap);maxLowerGap=Math.max(maxLowerGap,gap);
  if(gap<-.5)lowerBelowPenetrationLimit++;
  if(gap>=-.5&&gap<=.1){lowerWithinStrictContact++;if(contacts.length<100)contacts.push({point:[x,y,z],ground,gap,kind,aboveGlobalBottomM:y-bottom,withinOldGlobalLowRim:y<=bottom+.35});}
 };
 for(const t of model.triangles){for(const p of t)check(...p,'vertex');check(...[0,1,2].map(a=>t.reduce((s,p)=>s+p[a],0)/3),'face-centre');}
 rows.push({uid:model.uid,sourceSHA256:model.sourceSHA256,worldTrianglesSHA256:model.worldTrianglesSHA256,checks,lowerChecks,missingTerrain,missingLowerProfile,minLowerGap:Number.isFinite(minLowerGap)?minLowerGap:null,maxLowerGap:Number.isFinite(maxLowerGap)?maxLowerGap:null,lowerWithinStrictContact,lowerBelowPenetrationLimit,firstContacts:contacts,identityAccepted:false,installationApproved:false,qualification:'Lower-envelope contact evidence only. Source projection holes and unsupported separate components are not resolved. Original numeric global-rim gate is unchanged; no replacement metric, model, terrain or approval is produced.'});
}
for(const path of ['source-scripts/city/government-import/original-lower-profile-contact-diagnostic.mjs','3d-viewer/city/native-terrain.js'])inputHashes[path]=hash(readFileSync(new URL(path,root)));
mkdirSync(new URL('.',new URL(outPath,root)),{recursive:true});writeFileSync(new URL(outPath,root),JSON.stringify({rows,inputHashes,publication:false,newlyInstalled:0,modelGeometryChanges:0,scriptExternalAICalls:0},null,2)+'\n');
console.log(JSON.stringify(rows.map(({firstContacts,...r})=>({...r,contactsOutsideGlobalLowRim:firstContacts.filter(c=>!c.withinOldGlobalLowRim).length}))));
