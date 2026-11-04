import{readFileSync,writeFileSync}from'node:fs';import{gunzipSync,gzipSync}from'node:zlib';import{supportSurface}from'./support-contact.mjs';
const dir=process.argv[2],input=JSON.parse(gunzipSync(readFileSync(dir+'/inputs.json.gz'))),rows=[];
for(const[mode,w]of Object.entries(input.worlds)){const tri=['landsd/265851:0','landsd/239351:0'].flatMap(u=>w[u]),surface=supportSurface({position:tri.flat(2),index:Array.from({length:tri.length*3},(_,i)=>i)});for(const r of input.paths){const p=r.contact.point,h=surface.height(p[0],p[2]),gap=h===null?null:p[1]-h;rows.push({mode,uid:r.uid,position:r.position,contact:p,gap,contactPassed:gap!==null&&gap>=-.1&&gap<=1});}}
writeFileSync(dir+'/contacts.json.gz',gzipSync(JSON.stringify({rows,fullAcceptance:false})));
console.log(JSON.stringify({checks:rows.length,passed:rows.filter(r=>r.contactPassed).length}));
