/** Existing support-interface checks for explicitly captured coordinate representations. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {verifySupportInterface} from './support-interface.mjs';
const [input,output]=process.argv.slice(2),worlds=JSON.parse(gunzipSync(readFileSync(input)));
assert.deepEqual(Object.keys(worlds).sort(),['explicitBalancedF32','explicitLeftF32','literal','original']);
const rows=[];
for(const [mode,{source,support}]of Object.entries(worlds)){
 assert(source.position.length%9===0&&support.position.length%9===0);
 const geometry=position=>({position,index:Array.from({length:position.length/3},(_,i)=>i)});
 let bottom=Infinity;for(let i=1;i<source.position.length;i+=3)bottom=Math.min(bottom,source.position[i]);
 rows.push({mode,interface:verifySupportInterface(geometry(source.position),bottom,geometry(support.position))});
}
writeFileSync(output,gzipSync(JSON.stringify({rows,installationApproved:false})));
