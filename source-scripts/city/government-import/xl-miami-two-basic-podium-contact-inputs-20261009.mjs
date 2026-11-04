/** Pin exact current renderer podium geometry and both full original streams. */
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
const root=new URL('../../../',import.meta.url),hash=b=>createHash('sha256').update(b).digest('hex'),inputHashes={};
const read=p=>{const bytes=readFileSync(new URL(p,root));inputHashes[p]=hash(bytes);return JSON.parse(p.endsWith('.gz')?gunzipSync(bytes):bytes);};
const dir='docs/astra-city/government-import/government-xl-miami-two-original-staged-20261009/';mkdirSync(new URL(dir,root),{recursive:true});
const manifest=read('3d-viewer/city/data/manifest.json'),stage=read(dir+'stage-inputs.json');assert.equal(inputHashes['3d-viewer/city/data/manifest.json'],stage.currentManifestSHA256);
const tile='3d-viewer/city/data/tiles/-10_-5.json',building=read(tile).buildings.find(b=>b.uid==='landsd/232089:0');assert(building&&building.buildingCSUID==='1484725876P20060311');
const sourceRows=read('docs/astra-city/government-import/government-xl-miami-nine-original-contact-20261009/all-original-source-contact-inputs.json.gz').rows.filter(r=>Object.hasOwn(stage.sourceSHA256s,r.uid));assert.equal(sourceRows.length,2);for(const s of sourceRows)assert.equal(s.sourceSHA256,stage.sourceSHA256s[s.uid]);
const g=createBuildingGeometry(building);try{
 const body={position:Array.from(g.attributes.position.array),index:g.index?Array.from(g.index.array):Array.from({length:g.attributes.position.count},(_,i)=>i)};
 for(const p of ['3d-viewer/city/building-geometry.js','source-scripts/city/government-import/xl-miami-two-basic-podium-contact-inputs-20261009.mjs'])inputHashes[p]=hash(readFileSync(new URL(p,root)));
 for(const [p,h] of Object.entries(inputHashes))assert.equal(hash(readFileSync(new URL(p,root))),h,p);
 writeFileSync(new URL(dir+'basic-podium-original-contact-inputs.json.gz',root),gzipSync(JSON.stringify({currentForm:building,currentRendererBody:body,currentRendererPositionFloat32SHA256:hash(Buffer.from(new Float32Array(body.position).buffer)),rows:sourceRows,inputHashes,sourceGeometryChanges:0,currentActorChanges:0,physicalSupportApproval:false})));
 console.log(JSON.stringify({uid:building.uid,completeCurrentTriangles:body.index.length/3,completeOriginalFaces:sourceRows.map(s=>({uid:s.uid,faces:s.index.length/3})),currentActorChanges:0}));
}finally{g.dispose();}
