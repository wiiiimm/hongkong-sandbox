// Mapped plan geometry and source-node connectivity, with explicitly estimated
// deck elevations on the retained terrain. OSM layer/height are not deck metres.
const PEDESTRIAN=new Set(['footway','pedestrian','path','steps','cycleway','living_street']);
const numeric=v=>typeof v==='number'&&Number.isFinite(v)?v:null;
const affirmative=v=>v===true||['yes','covered','viaduct','boardwalk','cantilever','movable','trestle','aqueduct'].includes(v);
const sourceId=record=>String(record.source||record.id).replace(/^https?:\/\/www\.openstreetmap\.org\//,'');
function validPath(record){return Array.isArray(record.path)&&record.path.length>=2&&record.path.every(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite));}
function lengths(path){const output=[0];for(let i=1;i<path.length;i++)output.push(output.at(-1)+Math.hypot(path[i][0]-path[i-1][0],path[i][1]-path[i-1][1]));return output;}
function inferredClearance(record){
 const tags=record.tags||{},minimum=numeric(record.minHeight),level=numeric(record.level),layer=numeric(record.layer);
 if(minimum!==null&&minimum>=0&&minimum<80)return {height:minimum+.35,basis:'Estimated deck from mapped minimum height plus 0.35 m deck thickness; terrain and datum remain approximate.'};
 if(level!==null&&level>0&&level<20)return {height:level*3.5,basis:'Estimated deck using mapped floor level × 3.5 m; a floor level is not a surveyed elevation.'};
 const stack=layer!==null&&layer>1?Math.min(layer-1,6)*4:0;
 return {height:5.2+stack,basis:'Estimated 5.2 m pedestrian clearance'+(stack?' with visual separation for mapped stacking order':'')+'. Layer is an ordering tag, not a measured height.'+(tags.height||record.height?' Total structure height is retained as a tag and is not used as deck elevation.':'')};
}
export function prepareBridges(data,sampler){
 if(data?.schemaVersion!==1||!Array.isArray(data.bridges))throw new Error('Invalid mapped bridge inventory');
 const candidates=[],seen=new Set();
 for(const input of data.bridges){
  if(!input.id||!input.source||!validPath(input))throw new Error('Invalid bridge path '+input.id);
  if(seen.has(input.id))throw new Error('Duplicate bridge '+input.id);seen.add(input.id);
  const tags=input.tags||{},kind=input.kind||tags.highway,role=input.role||'bridge';
  if(!PEDESTRIAN.has(kind))continue;
  // An ordinary indoor floor corridor must not become an outdoor skybridge.
  if(role==='elevated-link'&&tags.indoor&&tags.indoor!=='no'&&!affirmative(input.bridge)&&!affirmative(tags.bridge))continue;
  if(role==='access'&&!input.connectsTo?.length)continue;
  const widthTag=numeric(input.width),width=widthTag!==null&&widthTag>=.6&&widthTag<=40?widthTag:kind==='steps'?2:kind==='cycleway'?3.2:kind==='pedestrian'?4:2.8;
  const ground=input.path.map(([x,z])=>sampler.height(x,z));
  const distance=lengths(input.path),length=distance.at(-1);if(length<.1)continue;
  // A long ground trail touching a bridge is not itself an elevated approach.
  if(role==='access'&&(length>180||!(kind==='steps'||tags.ramp==='yes'||tags.incline&&tags.incline!=='0')))continue;
  const {height,basis}=inferredClearance(input);
  const initial=input.path.map((p,i)=>ground[0]+(ground.at(-1)-ground[0])*distance[i]/length+height);
  const lift=Math.max(0,...ground.map((g,i)=>g+Math.min(2,height)-initial[i]));
  candidates.push({...input,kind,role,width,widthBasis:widthTag!==null&&widthTag>=.6&&widthTag<=40?'Mapped width in metres':'Estimated width for mapped path type',covered:input.covered===true||input.covered==='yes'||tags.covered==='yes',estimatedElevation:true,elevationBasis:role==='access'?'Estimated access slope between source-connected bridge nodes and terrain; no surveyed stair profile.':basis,distance,length,ground,levels:initial.map(y=>y+lift),sourceId:sourceId(input)});
 }
 // Only actual shared OSM node IDs join spans; coincident crossings stay apart.
 const network=new Map();
 for(const record of candidates.filter(r=>r.role!=='access'))for(let i=0;i<record.path.length;i++){
  const node=record.nodes?.[i];if(node===null||node===undefined)continue;
  const key=String(node);network.set(key,Math.max(network.get(key)??-Infinity,record.levels[i]));
 }
 const emitted=new Set(candidates.filter(r=>r.role!=='access').flatMap(r=>[r.id,r.sourceId]));
 const output=[];
 for(const record of candidates){
  if(record.role==='access'&&!record.connectsTo.some(id=>emitted.has(id)))continue;
  const anchors=[];
  for(let i=0;i<record.path.length;i++){
   const node=record.nodes?.[i],connected=node!==null&&node!==undefined&&network.has(String(node));
   if(connected)anchors.push([i,network.get(String(node))]);
  }
  if(record.role==='access'&&!anchors.length)continue;
  const fallback=i=>record.role==='access'?record.ground[i]+.16:record.levels[i];
  if(!anchors.some(([i])=>i===0))anchors.unshift([0,fallback(0)]);
  if(!anchors.some(([i])=>i===record.path.length-1))anchors.push([record.path.length-1,fallback(record.path.length-1)]);
  let segment=0;
  const deckPath=record.path.map(([x,z],i)=>{
   while(segment<anchors.length-2&&anchors[segment+1][0]<i)segment++;
   const [a,ya]=anchors[segment],[b,yb]=anchors[segment+1]||anchors[segment],span=record.distance[b]-record.distance[a];
   const u=span?(record.distance[i]-record.distance[a])/span:0;
   return [x,ya+(yb-ya)*u,z];
  });
  const xs=record.path.map(p=>p[0]),zs=record.path.map(p=>p[1]),half=record.width/2;
  const {distance,ground,levels,...clean}=record;
  output.push({...clean,deckPath,bounds:[Math.min(...xs)-half,Math.min(...zs)-half,Math.max(...xs)+half,Math.max(...zs)+half],aboveGround:deckPath.reduce((sum,p,i)=>sum+p[1]-ground[i],0)/deckPath.length});
 }
 return output;
}
