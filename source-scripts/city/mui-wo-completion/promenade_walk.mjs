/** Derive a route within the verified public source deck, around unchanged furniture. */
import {writeFileSync} from 'node:fs';
import {root,read,stagedContext,models} from './context.mjs';
import {InfrastructureSurfaces} from '../../../3d-viewer/city/infrastructure-data.js';
const config=read('source-scripts/city/mui-wo-completion/promenade-route.json'),deck=models.find(m=>m.id===config.sourceModelId),floor=new InfrastructureSurfaces();floor.add(deck);
const ctx=stagedContext({centreline:[config.sourceDeckEntry,config.target]}),step=.25,cache=new Map();
function node(c,r){const key=`${c},${r}`;if(cache.has(key))return cache.get(key);const x=c*step,z=r*step,y=floor.heights(x,z)[0];const p=Number.isFinite(y)&&!ctx.index.collision(x,z,y,y+1.8,.7)&&!ctx.surfaces.collision(x,z,y+.32,y+1.8,.7)?{key,c,r,x,z,y}:null;cache.set(key,p);return p;}
function nearest(p){let candidates=[];for(let c=Math.round(p[0]/step)-6;c<=Math.round(p[0]/step)+6;c++)for(let r=Math.round(p[1]/step)-6;r<=Math.round(p[1]/step)+6;r++){const n=node(c,r);if(n)candidates.push(n);}return candidates.sort((a,b)=>Math.hypot(a.x-p[0],a.z-p[1])-Math.hypot(b.x-p[0],b.z-p[1]))[0];}
const start=nearest(config.sourceDeckEntry),end=nearest(config.target);if(!start||!end)throw Error('No clear floor entry/exit');
const scores=new Map([[start.key,0]]),parents=new Map(),nodes=new Map([[start.key,start]]),open=[{...start,score:0}],closed=new Set();let found=false;
while(open.length){open.sort((a,b)=>b.score-a.score);const current=open.pop();if(closed.has(current.key))continue;if(current.key===end.key){found=true;break;}closed.add(current.key);
 for(const [dc,dr] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]){
  const n=node(current.c+dc,current.r+dr);if(!n||closed.has(n.key)||Math.abs(n.y-current.y)>.25)continue;
  // Axis-separated runtime movement must not clip a diagonal corner.
  if(dc&&dr&&(!node(current.c+dc,current.r)||!node(current.c,current.r+dr)))continue;
  const cost=scores.get(current.key)+Math.hypot(dc,dr)*step;if(cost>=(scores.get(n.key)??Infinity))continue;
  scores.set(n.key,cost);parents.set(n.key,current.key);nodes.set(n.key,n);open.push({...n,score:cost+Math.hypot(n.x-end.x,n.z-end.z)});
 }
}
if(!found)throw Error('No collision-clear continuous route within the original public floor');
let keys=[end.key];while(keys.at(-1)!==start.key)keys.push(parents.get(keys.at(-1)));keys.reverse();const line=[config.sourceDeckEntry,...keys.map(k=>{const p=nodes.get(k);return [p.x,p.z];}),config.target];
const original=read('docs/astra-city/mui-wo-completion/routes-staged.json').legs[0],i=original.nodeIds.indexOf(config.sourceStreetNode);
config.sourceDeckLine=line;config.walkCentreline=[...original.centreline.slice(0,i+1),config.outsideOpening,...line];config.floorRoute={gridMetres:step,collisionRadiusMetres:.7,actorHeightMetres:1.8,sourceFloorOnly:true,obstaclesRemoved:false,visitedCells:closed.size,lengthMetres:scores.get(end.key),method:'A* within the selected original public floor faces, using the city source-mesh and building collision functions; a0.7m planning radius reserves margin for the actual0.55m walking actor. Quarter-metre nodes are derived simulation guidance, not surveyed positions.'};
writeFileSync(root+'/source-scripts/city/mui-wo-completion/promenade-route.json',JSON.stringify(config,null,2)+'\n');console.log(config.floorRoute);
