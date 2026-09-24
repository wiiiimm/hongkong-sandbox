"""Prepare source-node-connected Mui Wo village routes using existing public-path rules."""
import collections,gzip,hashlib,importlib.util,json,math,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/mui-wo-completion'
sys.path.insert(0,str(HERE.parent));from build_city import xy
spec=importlib.util.spec_from_file_location('existing_route_helpers',HERE.parent/'tai-o-completion/route_build.py');shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
SOURCE=HERE.parent/'snapshots/outlying-west.json.gz';PLACES=HERE.parent/'regional/nt/surfaces-osm.json.gz'
# Government-operated village lanes support shared pedestrian/vehicle access.
# Motor-vehicle restrictions alone are not a foot-access restriction.
def permitted(tags):
 if shared.permitted(tags):return True
 return tags.get('highway')=='unclassified' and tags.get('ownership')=='government' and tags.get('operation')=='government' and not any(tags.get(k) in shared.RESTRICTED_ACCESS for k in ('access','foot')) and tags.get('area')!='yes' and tags.get('indoor')!='yes' and not tags.get('tunnel')
ANCHORS=[('wangtong',2295473896),('paknganheung',993408542),('taiteitong',1004444168),('lukteitong',13287206330)]
def graph_data():
 config=json.loads((HERE/'route-config.json').read_text()) if (HERE/'route-config.json').exists() else {};excluded={frozenset(r['nodes']) for r in config.get('excludedEdges',[])}
 raw=SOURCE.read_bytes();data=json.loads(gzip.decompress(raw));ways={};nodes={};graph=collections.defaultdict(list)
 for e in data['elements']:
  if e['type']!='way' or not e.get('geometry') or not permitted(e.get('tags',{})):continue
  geometry=e['geometry'];points=[list(xy(p['lon'],p['lat'])) for p in geometry]
  if not any(-18700<x<-14500 and 100<z<4300 for x,z in points):continue
  if len(e['nodes'])!=len(points):raise ValueError('Incomplete source nodes')
  ways[e['id']]=e
  for id,p in zip(e['nodes'],points):
   if id in nodes and math.dist(nodes[id],p)>.001:raise ValueError('Source-node geometry disagreement')
   nodes[id]=p
  for a,b in zip(e['nodes'],e['nodes'][1:]):
   if frozenset([a,b]) in excluded:continue
   dist=math.dist(nodes[a],nodes[b]);graph[a].append((b,dist,e['id']));graph[b].append((a,dist,e['id']))
 return config,raw,data,ways,nodes,graph
def main():
 config,raw,data,ways,nodes,graph=graph_data()
 places={e['id']:e for e in json.loads(gzip.decompress(PLACES.read_bytes()))['elements'] if e['type']=='node'};stops=[]
 for id,nid in ANCHORS:
  place_nid=nid;e=places[nid];p=list(xy(e['lon'],e['lat']));near=sorted((math.dist(p,coord),node) for node,coord in nodes.items())[:40]
  if id in config.get('stops',{}):nid=config['stops'][id]['sourceNode'];near=[(math.dist(p,nodes[nid]),nid)]+near
  stops.append({'id':id,'sourcePlaceNode':place_nid,'sourcePlaceName':e['tags']['name:en'],'sourcePlace':p,'lat':e['lat'],'lon':e['lon'],'sourceNode':near[0][1],'nodePosition':nodes[near[0][1]],'offsetFromPlaceNodeM':near[0][0]})
 # Closest source graph points to existing town/beach arrivals are reported, not
 # silently used as connectors from unverified camera coordinates.
 for id,p in [('muiwo-town',[-16551.2,2282]),('silvermine-beach',[-16577.2,1896.6]),('ferry-promenade',[-16420,2660])]:
  distance,node=min((math.dist(p,q),n) for n,q in nodes.items());stops.append({'id':id,'sourceNode':node,'nodePosition':nodes[node],'anchorWorld':p,'offsetFromAnchorM':distance})
 byid={p['id']:p for p in stops};itinerary=['ferry-promenade','muiwo-town','silvermine-beach','wangtong','paknganheung','taiteitong','lukteitong'];legs=[]
 for a,b in zip(itinerary,itinerary[1:]):
  try:edges=shared.shortest(graph,byid[a]['sourceNode'],byid[b]['sourceNode'])
  except ValueError as error:legs.append({'from':a,'to':b,'error':str(error)});continue
  nodeids=[edges[0][0]]+[e[1] for e in edges];line=[nodes[n] for n in nodeids];segments=[]
  for i,(na,nb,way) in enumerate(edges):
   e=ways[way];tags=e['tags']
   if segments and segments[-1]['sourceWayId']==way:segments[-1]['toIndex']=i+1
   else:segments.append({'sourceWayId':way,'source':'https://www.openstreetmap.org/way/'+str(way),'fromIndex':i,'toIndex':i+1,'tags':tags,'kind':'bridge' if tags.get('bridge')=='yes' else 'steps' if tags.get('highway')=='steps' else 'shared-government-lane' if tags.get('highway')=='unclassified' else 'path'})
  legs.append({'id':a+'--'+b,'from':a,'to':b,'centreline':line,'nodeIds':nodeids,'segments':segments,'lengthMetres':sum(math.dist(x,y) for x,y in zip(line,line[1:])),'continuousWalkVerified':False})
 result={'schemaVersion':1,'sectionId':'10.6','stage':'source-connected route candidates; public context, source bridge deck and actual collision/navigation verification pending','stops':stops,'legs':legs,'graph':{'ways':len(ways),'nodes':len(nodes)},'reviewedRouteConfig':config,'sources':[{'file':str(SOURCE.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'snapshot':data['osm3s']['timestamp_osm_base']},{'file':str(PLACES.relative_to(ROOT)),'sha256':hashlib.sha256(PLACES.read_bytes()).hexdigest()}],'limits':['No joining of disconnected source ways or shifting source geometry.','Nearest source graph points are candidates, not validated walking arrivals or access permissions.','The southern non-Mui Wo hamlet with the same Wang Tong name is explicitly excluded by source-node identity.']}
 (DOC/'routes-staged.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'graph':result['graph'],'stops':stops,'legs':[{k:v for k,v in l.items() if k not in ('centreline','nodeIds','segments')} for l in legs]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
