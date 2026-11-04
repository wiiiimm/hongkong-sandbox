/** Read-only saved guard binary64 boundaries; no terrain sampler or scene. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {gapBoundary} from './upton_six_basic_guard_samples_v1_20261012.mjs';
const path=process.argv[2],out=process.argv[3],bytes=readFileSync(path),input=JSON.parse(gunzipSync(bytes));
const uids=['landsd/72322:0','landsd/89540:0','landsd/258852:0','landsd/305600:0'];
const rows=uids.map(uid=>{const row=input.rows.find(r=>r.uid===uid);assert(row&&row.reasons.includes('increased-neighbour-ground-gap'));
 const base=row.exactCurrentForm.base+(row.exactCurrentForm.minimum||0);return{uid,base,boundary:gapBoundary(base,row.beforeGap[1]),
  failedSampleIDs:row.rows.filter(s=>base-s.afterHeight>Math.max(1,row.beforeGap[1])+.25).map(s=>s.sample),checks:row.checks};});
const result={rows,sourceGuardBytesSHA256:createHash('sha256').update(bytes).digest('hex'),originalBinary64SubtractionAndComparison:true,noSampleRegenerationOrTerrain:true};
writeFileSync(out,JSON.stringify(result)+'\n',{flag:'wx'});console.log(JSON.stringify(rows.map(r=>({uid:r.uid,checks:r.checks,failed:r.failedSampleIDs.length,minimum:r.boundary.minimumAcceptedBinary64HeightM}))));
