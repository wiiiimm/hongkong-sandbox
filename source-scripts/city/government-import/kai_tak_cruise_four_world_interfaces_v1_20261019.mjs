import{readFileSync,writeFileSync}from'node:fs';import{gunzipSync,gzipSync}from'node:zlib';
import{supportSurface}from'./support-contact.mjs';import{verifySupportInterface}from'./support-interface.mjs';
const dir=process.argv[2],input=JSON.parse(gunzipSync(readFileSync(dir+'/inputs.json.gz'))),interfaces=[],contacts=[];
for(const[mode,w]of Object.entries(input.worlds)){const tri=w['landsd/263423:0'],support={position:tri.flat(2),index:Array.from({length:tri.length*3},(_,i)=>i)},surface=supportSurface(support);
 for(const[uid,t]of Object.entries(w)){if(uid==='landsd/263423:0')continue;const position=t.flat(2),index=Array.from({length:t.length*3},(_,i)=>i),bottom=Math.min(...t.flat().map(v=>v[1]));const proof=verifySupportInterface({position,index},bottom,support);interfaces.push({uid,mode,proof});}
 for(const r of input.paths){const p=r.contact.point,h=surface.height(p[0],p[2]),gap=h===null?null:p[1]-h;contacts.push({mode,uid:r.uid,position:r.position,contact:p,gap,contactPassed:gap!==null&&gap>=-.1&&gap<=1});}}
writeFileSync(dir+'/interfaces.json.gz',gzipSync(JSON.stringify({rows:interfaces,installationApproved:false})));writeFileSync(dir+'/contacts.json.gz',gzipSync(JSON.stringify({rows:contacts,installationApproved:false})));console.log(JSON.stringify({interfaces:interfaces.length,pathContacts:contacts.length,passed:contacts.filter(r=>r.contactPassed).length}));
