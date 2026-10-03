/** HKS-222: persistent/batched actual viewer terrain sampler; never acceptance. */
import {readFileSync, writeFileSync, createReadStream} from 'node:fs';
import {createInterface} from 'node:readline';
import {createHash} from 'node:crypto';
import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
const root = new URL('../../../', import.meta.url), hashes = {};
function read(path) {
  const bytes = readFileSync(new URL(path, root));
  hashes[path] = createHash('sha256').update(bytes).digest('hex');
  return JSON.parse(bytes);
}
const manifest = read('3d-viewer/city/data/manifest.json');
const terrain = read('3d-viewer/city/data/terrain.json');
terrain.patches = (manifest.terrainPatches || []).map(p => read('3d-viewer/' + p.url));
const sampler = makeTerrainSampler(terrain);
async function check(input, output) {
  const rows = [];
  for await (const line of createInterface({input:createReadStream(input), crlfDelay:Infinity})) {
    if (!line.trim()) continue;
    const entry = JSON.parse(line);
    try {
      const covered = entry.position.map(([x,y,z],i) => ({i,x,y,z})).filter(p=>sampler.contains(p.x,p.z));
      const gaps = covered.map(p=>p.y-sampler.height(p.x,p.z));
      if (gaps.some(v => !Number.isFinite(v))) throw new Error('Non-finite terrain samples');
      const rimGaps = covered.flatMap((p,i)=>entry.lowRimSampleMask?.[p.i]?[gaps[i]]:[]);
      const resolutions = covered.map(p=>sampler.resolutionAt(p.x,p.z));
      rows.push({outcomeId:entry.outcomeId,status:!gaps.length?'outside-terrain-coverage':gaps.length===entry.position.length?'diagnostic-complete':'diagnostic-partial-coverage',sampledVertices:entry.position.length,coveredSamples:gaps.length,outsideTerrainSamples:entry.position.length-gaps.length,sourceVertices:entry.sourceVertices,sourceLowRimVertices:entry.sourceLowRimVertices,sampledLowRimVertices:entry.sampledLowRimVertices,minimumGap:gaps.length?Math.min(...gaps):null,maximumGap:gaps.length?Math.max(...gaps):null,lowRimGapRange:rimGaps.length?[Math.min(...rimGaps),Math.max(...rimGaps)]:null,terrainResolutionRange:resolutions.length?[Math.min(...resolutions),Math.max(...resolutions)]:null,belowTerrainQuarterMetre:gaps.filter(v=>v<-.25).length,aboveTerrainTwoMetres:gaps.filter(v=>v>2).length,method:entry.method,placementApproved:false});
    } catch(error) {rows.push({outcomeId:entry.outcomeId,status:'failed',error:String(error)});}
  }
  writeFileSync(output, JSON.stringify({status:'diagnostic-complete',rows,hashes,verticalScale:1,qualification:'Actual viewer sampler and manifest patches pinned when this worker starts. Capped source vertex samples, not full burial/support proof. Above-ground towers and below-grade foundations are diagnostic, not automatic acceptance or rejection.'})+'\n');
}
const args = process.argv.slice(2);
if (args[0] === '--server') {
  for await (const line of createInterface({input:process.stdin, crlfDelay:Infinity})) {
    if (!line.trim()) continue;
    try {const {input,output}=JSON.parse(line);await check(input,output);process.stdout.write(JSON.stringify({ok:true})+'\n');}
    catch(error) {process.stdout.write(JSON.stringify({ok:false,error:String(error)})+'\n');}
  }
} else {
  if (args.length !== 2) throw new Error('Expected samples.jsonl output.json or --server');
  await check(...args);
}
