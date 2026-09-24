/** One continuous four-kilometre actual Navigation replay; no intermediate resets. */
import {writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {root,read,stagedContext,stagedSurfaces} from './context.mjs';
import {makeRouteNavigation,replayRoute} from '../tai-o-completion/route_navigation.mjs';
import {InfrastructureSurfaces} from '../../../3d-viewer/city/infrastructure-data.js';
const source=read('docs/astra-city/mui-wo-completion/routes-staged.json'),promenade=read('source-scripts/city/mui-wo-completion/promenade-route.json'),line=[],stops=[];
for(const leg of source.legs){
 const points=leg.id==='ferry-promenade--muiwo-town'?promenade.walkCentreline:leg.centreline;
 if(!points)throw Error('Missing source-connected route '+leg.id);
 if(line.length&&Math.hypot(line.at(-1)[0]-points[0][0],line.at(-1)[1]-points[0][1])>1e-6)throw Error('Disconnected route join');
 if(!line.length){stops.push({id:leg.from,index:0});line.push(points[0]);}
 line.push(...points.slice(1));stops.push({id:leg.to,index:line.length-1});
}
const ctx=stagedContext({centreline:line}),options={maxFrames:90000},forward=replayRoute(makeRouteNavigation(ctx),line,options),reverse=replayRoute(makeRouteNavigation(ctx),line,{...options,reverse:true});
const noApproaches=replayRoute(makeRouteNavigation({...ctx,surfaces:stagedSurfaces(false)}),line,options),noSourceFloors=replayRoute(makeRouteNavigation({...ctx,surfaces:new InfrastructureSurfaces()}),line,options),highWater=replayRoute(makeRouteNavigation({...ctx,waterLevel:6}),line,options);
const passed=forward.passed&&reverse.passed&&!noApproaches.passed&&!noSourceFloors.passed&&!highWater.passed;
const report={schemaVersion:1,staged:true,passed,method:'One Navigation.setMode at each end, then actual held-W/heading updates at≤1/60s through all seven stops; no waypoint teleports, source collision overrides or floor substitutions.',walkCentrelineSha256:createHash('sha256').update(JSON.stringify(line)).digest('hex'),stops,walkCentreline:line,source:source.sources,forward,reverse,negativeCases:{noApproaches,noSourceFloors,highWater},maxFrames:90000,originalDefaultFrameGuard:60000,sourceMeshesChanged:false};
writeFileSync(root+'/docs/astra-city/mui-wo-completion/route-navigation.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed,forward,reverse,negativeCases:report.negativeCases},null,2));if(!passed)process.exitCode=1;
