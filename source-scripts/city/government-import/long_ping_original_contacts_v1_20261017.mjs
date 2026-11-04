/** Compare canonical contact samples to original TIN, without acceptance overrides. */
import fs from 'node:fs';
import zlib from 'node:zlib';
import {lowRimSamples,supportSurface,measureSupport} from './support-contact.mjs';
import {verifySupportInterface} from './support-interface.mjs';
const [runtime,terrain,output]=process.argv.slice(2);
const g=JSON.parse(zlib.gunzipSync(fs.readFileSync(runtime))).rows[0];
const original=JSON.parse(zlib.gunzipSync(fs.readFileSync(terrain)));
const geom=tri=>{const position=tri.flat(Infinity);return {position,index:Array.from({length:position.length/3},(_,i)=>i)}};
let bottom=Infinity;for(const i of g.index)bottom=Math.min(bottom,g.position[i*3+1]);
const rim=lowRimSamples(g,bottom),candidate=geom(g.drawnGroundGeometry),source=geom(original);
const cs=supportSurface(candidate),ss=supportSurface(source);
const comparison=rim.map(position=>{const a=cs.height(position[0],position[2]),b=ss.height(position[0],position[2]);return {position,candidateHeight:a,originalHeight:b,delta:a===null||b===null?null:a-b}});
const originalCheck=measureSupport(rim,ss),candidateCheck=verifySupportInterface(g,bottom,candidate);
const failures=candidateCheck.unresolved.map(f=>({...f,originalHeight:ss.height(f.position[0],f.position[2]),originalSupportFaces:ss.intersectionDetails(f.position[0],f.position[2])}));
const result={uid:g.uid,sourceSHA256:g.sourceSHA256,bottom,originalCheck,candidateCheck,comparison,failures,maxTerrainDelta:Math.max(...comparison.filter(x=>x.delta!==null).map(x=>Math.abs(x.delta))),missingOriginal:comparison.filter(x=>x.originalHeight===null).length,installationApproved:false};
fs.writeFileSync(output,JSON.stringify(result));
console.log(JSON.stringify({samples:rim.length,sourceFailures:originalCheck.failed.length,remaining:candidateCheck.unresolved.length,maxTerrainDelta:result.maxTerrainDelta,missingOriginal:result.missingOriginal}));
