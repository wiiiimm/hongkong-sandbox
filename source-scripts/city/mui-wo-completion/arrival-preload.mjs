/** Run the unchanged arrival validator against staged data without publishing it. */
import fs from 'node:fs';
import {syncBuiltinESMExports} from 'node:module';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..'),read=fs.readFileSync;
const parse=p=>JSON.parse(read(path.join(root,p)));
const terrain=parse('3d-viewer/city/data/terrain.json'),hydro=parse('source-scripts/city/mui-wo-completion/hydro-mui-wo.json');
const original=terrain.hydro;
terrain.hydro={...hydro,water:[...(original?.water||[]),...hydro.water],bounds:original?[Math.min(original.bounds[0],hydro.bounds[0]),Math.min(original.bounds[1],hydro.bounds[1]),Math.max(original.bounds[2],hydro.bounds[2]),Math.max(original.bounds[3],hydro.bounds[3])]:hydro.bounds};
const estimates=new Map(parse('docs/astra-city/mui-wo-completion/terrain-audit.json').rows.filter(r=>r.missingBaseReestimated).map(r=>[r.uid,r.proposedBase]));
fs.readFileSync=function(file,options){
 const p=file instanceof URL?fileURLToPath(file):String(file);let out;
 if(p===path.join(root,'3d-viewer/city/data/terrain.json'))out=JSON.stringify(terrain);
 else if(p===path.join(root,'3d-viewer/city/data/terrain-mui-wo.json'))return read(path.join(root,'source-scripts/city/mui-wo-completion/staged-terrain-mui-wo.json'),options);
 else if(p.startsWith(path.join(root,'3d-viewer/city/data/tiles/'))&&p.endsWith('.json')){
  const data=JSON.parse(read(file));let changed=false;
  for(const b of data.buildings)if(estimates.has(b.uid)){b.base=estimates.get(b.uid);changed=true;}
  if(changed)out=JSON.stringify(data);
 }
 if(out===undefined)return read(file,options);
 const encoding=typeof options==='string'?options:options?.encoding;return encoding?out:Buffer.from(out);
};
syncBuiltinESMExports();
