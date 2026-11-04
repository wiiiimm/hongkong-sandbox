/** Current-territory sampler parity and timing against an immutable Git baseline. */
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {makeTerrainSampler,ORIGIN} from '../../../3d-viewer/city/geo.js';
const root=new URL('../../../',import.meta.url),baseline=process.argv[2],output=process.argv[3];
assert(/^[a-f0-9]{8,40}$/.test(baseline||'')&&output,'Explicit immutable baseline commit and output required');
const refs=[],hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const load=path=>{const bytes=readFileSync(new URL(path,root));refs.push({path,sha256:hash(bytes)});return JSON.parse(bytes);};
const old=execFileSync('git',['show',baseline+':3d-viewer/city/geo.js'],{cwd:root,encoding:'utf8'});
const oldModule=old.replace(/from '\.\/([^']+)'/g,(_,path)=>"from '"+new URL('3d-viewer/city/'+path,root).href+"'");
const legacy=await import('data:text/javascript;base64,'+Buffer.from(oldModule).toString('base64'));
const manifest=load('3d-viewer/city/data/manifest.json'),data=load('3d-viewer/city/data/terrain.json');
data.patches=manifest.terrainPatches.map(entry=>load('3d-viewer/'+entry.url));
const samplers=[legacy.makeTerrainSampler(data),makeTerrainSampler(data)],points=[];
function addGrid(p){const g=p.meta.georef;for(const [c,r] of [[0,0],[p.w-1,p.h-1],[.13,.31],[(p.w-1)/2,(p.h-1)/2],[p.w-1,0],[0,p.h-1]])points.push([g.bE-ORIGIN[0]+c*g.aE,ORIGIN[1]-g.bN-r*g.aN]);for(const child of p.patches||[])addGrid(child);}
addGrid(data);
const hydroProbes=[[-30523.45,3546.88],[-30400,3550],[-30556.76,3396.27],[-30685,3680],[-30450,3120],[-31300,3900]];points.push(...hydroProbes);
for(let x=-1400;x<800;x+=25)for(let z=-5300;z< -1600;z+=25)points.push([x+.125,z+.375]);
const sample=(sampler,point)=>['height','raw','resolutionAt'].map(method=>{try{return {value:sampler[method](...point)};}catch(error){return {error:error.name+': '+error.message};}});
const start=performance.now(),expected=points.map(point=>sample(samplers[0],point)),legacyMs=performance.now()-start;
const next=performance.now();for(let i=0;i<points.length;i++)assert.deepEqual(sample(samplers[1],points[i]),expected[i],'Changed terrain at '+points[i]);const indexedMs=performance.now()-next;
for(const path of ['3d-viewer/city/geo.js','3d-viewer/city/terrain-patch-index.js','3d-viewer/city/native-terrain.js','3d-viewer/city/rendered-patch-height.js']){const bytes=readFileSync(new URL(path,root));refs.push({path,sha256:hash(bytes)});}
refs.push({path:'source-scripts/city/government-import/terrain-sampler-parity.mjs',sha256:hash(readFileSync(import.meta.url.replace('file://','')))});
const report={baselineCommit:baseline,baselineGeoSHA256:hash(old),points:points.length,queries:points.length*3,identical:true,legacyMs,indexedMs,speedup:legacyMs/indexedMs,hydroProbes:hydroProbes.map(point=>({point,legacy:sample(samplers[0],point),indexed:sample(samplers[1],point)})),inputRefs:refs,modelGeometryChanges:0,terrainGeometryChanges:0};
const dest=new URL(output,root);mkdirSync(new URL('.',dest),{recursive:true});writeFileSync(dest,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({...report,inputRefs:report.inputRefs.length}));
