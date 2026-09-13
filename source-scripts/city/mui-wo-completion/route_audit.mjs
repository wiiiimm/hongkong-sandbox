/** Staged Mui Wo route replay using the existing Navigation and route-test helpers. */
import {writeFileSync} from 'node:fs';
import {root,read,stagedContext} from './context.mjs';
import {makeRouteNavigation,replayRoute} from '../tai-o-completion/route_navigation.mjs';
const candidate=read('docs/astra-city/mui-wo-completion/routes-staged.json'),promenade=read('source-scripts/city/mui-wo-completion/promenade-route.json'),reports=[];
for(const leg of candidate.legs){
 if(!leg.centreline)continue;
 const line=leg.id==='ferry-promenade--muiwo-town'?promenade.walkCentreline:leg.centreline,nav=makeRouteNavigation(stagedContext({...leg,centreline:line}));
 const forward=replayRoute(nav,line);
 if(!forward.passed&&forward.position){const [x,y,z]=forward.position;forward.nearby=Array.from({length:8},(_,i)=>{const angle=i*Math.PI/4,px=x+Math.cos(angle)*.08,pz=z+Math.sin(angle)*.08;return {x:px,z:pz,heights:nav.groundHeights(px,pz).map(h=>({y:h,collision:nav.collides(px,pz,h,h+1.8,.55,true)?.id||nav.collides(px,pz,h,h+1.8,.55,true)?.uid||null})),walkHeight:nav.walkHeight(px,pz,y,.08)};});}
 const reverse=forward.passed?replayRoute(makeRouteNavigation(stagedContext({...leg,centreline:line})),line,{reverse:true}):null;
 reports.push({id:leg.id,originalSourceLengthMetres:leg.lengthMetres,derivedPromenadeLine:line!==leg.centreline,forward,reverse});
 console.log(leg.id,JSON.stringify({forward,reverse}));
}
writeFileSync(root+'/docs/astra-city/mui-wo-completion/routes-diagnostic.json',JSON.stringify({stage:'Improved staged terrain, exact source building/bridge collisions, bounded lower-estuary water and visible estimated approaches',reports},null,2)+'\n');
