/** Record every canonical rim and strict measured support root; no admission change. */
import{readFileSync,writeFileSync}from'node:fs';
import{gunzipSync,gzipSync}from'node:zlib';
import{createHash}from'node:crypto';
import{lowRimSamples,supportSurface,measureSupport}from'./support-contact.mjs';
const inputPath=process.argv[2],outputPath=process.argv[3];
if(!inputPath||!outputPath)throw new Error('Require input and output paths');
const raw=readFileSync(inputPath),input=JSON.parse(gunzipSync(raw));
if(input.rows.length!==1)throw new Error('Exactly one explicitly bound source required');
const source=input.rows[0],position=input.podium.flat(2),surface=supportSurface({position,index:Array.from({length:position.length/3},(_,i)=>i)});
const bottom=Math.min(...source.position.filter((_,i)=>i%3===1));
const rim=lowRimSamples(source,bottom),strict=measureSupport(rim,surface);
const roots=rim.map((position,sampleIndex)=>{
 const details=surface.intersectionDetails(position[0],position[2]);
 const provider=details.at(-1)||null, supportHeight=provider?.height??null;
 const gap=supportHeight===null?null:position[1]-supportHeight;
 return {sampleIndex,position,supportHeight,gap,strictAccepted:gap!==null&&gap>=strict.minimumGap&&gap<=strict.maximumGap,provider};
});
if(roots.filter(r=>r.strictAccepted).length!==strict.contacts)throw new Error('Canonical strict-root count changed');
writeFileSync(outputPath,gzipSync(JSON.stringify({uid:source.uid,inputSHA256:createHash('sha256').update(raw).digest('hex'),strict,roots,sourceGeometryChanges:0,supportApproved:false,installationApproved:false})));
