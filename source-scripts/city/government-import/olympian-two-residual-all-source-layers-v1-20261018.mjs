import{readFileSync,writeFileSync}from'node:fs';
import{gunzipSync,gzipSync}from'node:zlib';
import{supportSurface}from'./support-contact.mjs';
const dir=process.argv[2],data=JSON.parse(gunzipSync(readFileSync(dir+'/inputs.json.gz')));
const surfaces=data.sources.map(s=>({...s,surface:supportSurface(s)}));
const rows=data.points.map(p=>{const layers=[];for(const s of surfaces){if(s.uid===p.uid)continue;const hits=s.surface.intersectionDetails(p.position[0],p.position[2]);if(hits.length)layers.push({uid:s.uid,sourceSHA256:s.sourceSHA256,hits:hits.map(h=>({...h,gap:p.position[1]-h.height})),contactFaces:hits.filter(h=>p.position[1]-h.height>=-.1&&p.position[1]-h.height<=1)});}return{...p,layers,hasContactLayer:layers.some(s=>s.contactFaces.length),installationApproved:false};});
writeFileSync(dir+'/layers.json.gz',gzipSync(JSON.stringify({rows,fullAcceptance:false,qualification:'Every original finite nonvertical source layer at each unresolved point; contact interval unchanged. Contact layers do not waive maximum-surface, identity or physical requirements.'})));
console.log(JSON.stringify({points:rows.length,withContactLayer:rows.filter(x=>x.hasContactLayer).length,withoutContactLayer:rows.filter(x=>!x.hasContactLayer).length}));
