import {writeFileSync} from 'node:fs';
import {root,read,sampler,stagedSurfaces} from './context.mjs';
const surfaces=stagedSurfaces(false),rows=[];
for(const r of read('source-scripts/city/mui-wo-completion/opening-candidates.json')){
 const y=surfaces.heights(...r.inside)[0];if(!Number.isFinite(y)||sampler.mappedWater(...r.outside))continue;
 let pass=true;
 for(let t=0;t<=1;t+=.025){const x=r.outside[0]+(r.inside[0]-r.outside[0])*t,z=r.outside[1]+(r.inside[1]-r.outside[1])*t;if(surfaces.collision(x,z,y+.32,y+1.8,.6)){pass=false;break;}}
 if(pass)rows.push({...r,sourceY:y,ground:sampler.height(...r.outside)});
}
writeFileSync(root+'/source-scripts/city/mui-wo-completion/opening-scan.json',JSON.stringify(rows,null,2)+'\n');console.log(JSON.stringify(rows.slice(0,10),null,2),rows.length);
