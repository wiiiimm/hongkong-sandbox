import {writeFileSync} from 'node:fs';
import {root,read,stagedContext} from './context.mjs';
import {makeRouteNavigation,replayRoute} from '../tai-o-completion/route_navigation.mjs';
const source=read('source-scripts/city/mui-wo-completion/arrival-connector.json'),ctx=stagedContext(source);
const forward=replayRoute(makeRouteNavigation(ctx),source.centreline),reverse=replayRoute(makeRouteNavigation(ctx),source.centreline,{reverse:true});
writeFileSync(root+'/docs/astra-city/mui-wo-completion/arrival-connection.json',JSON.stringify({source,forward,reverse,passed:forward.passed&&reverse.passed},null,2)+'\n');console.log(JSON.stringify({forward,reverse},null,2));
