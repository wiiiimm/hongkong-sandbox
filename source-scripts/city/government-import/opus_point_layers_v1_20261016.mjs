/** Exact same-source layer context for Opus's one failing point; no acceptance. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {supportSurface} from './support-contact.mjs';
const root=new URL('../../../',import.meta.url),dir=process.argv[2],read=p=>JSON.parse(p.endsWith('.gz')?gunzipSync(readFileSync(new URL(p,root))):readFileSync(new URL(p,root)));
const input=read(dir+'input.json'),g=read(input.geometryPath).rows[0],contacts=read(input.contactsPath),failures=contacts.failures;
assert.equal(g.index.length/3,12382);assert.equal(failures.length,2);assert.deepEqual(failures[0].position,failures[1].position);
const excluded=new Set(failures.flatMap(f=>f.sourceFaces));assert.deepEqual([...excluded].sort((a,b)=>a-b),[11326,12324]);const sourceIds=[],index=[];
for(let i=0;i<g.index.length;i+=3)if(!excluded.has(i/3)){sourceIds.push(i/3);index.push(...g.index.slice(i,i+3));}
const point=failures[0].position,surface=supportSurface({position:g.position,index}),hits=surface.intersectionDetails(point[0],point[2]).map(h=>({...h,originalSourceFace:sourceIds[h.faceIndex],gapM:point[1]-h.height}));
const summary={sourceFaces:12382,excludedIncidentFaces:[...excluded],otherSourceFaces:index.length/3,point,terrainGapM:failures[0].gapM,allIntersections:hits.length,strictContactLayers:hits.filter(h=>h.gapM>=-.1&&h.gapM<=1).length,fullAcceptance:false};
writeFileSync(new URL(dir+'layers.json',root),JSON.stringify({summary,hits}));writeFileSync(new URL(dir+'summary.json',root),JSON.stringify(summary));console.log(JSON.stringify(summary));
