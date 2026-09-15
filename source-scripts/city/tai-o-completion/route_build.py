"""Assemble a continuous public Tai O route from retained OSM node topology.

No network, invented connectors, source geometry edits or runtime modifications.
Run with the existing Astra Python environment; projection/access rules are reused.
"""
from __future__ import annotations
import collections,gzip,hashlib,heapq,json,math,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent))
from build_city import xy
from build_places import RESTRICTED_ACCESS
SOURCE=ROOT/'source-scripts/city/snapshots/outlying-west.json.gz'
DOC=ROOT/'docs/astra-city/tai-o-completion'
# These mapped pedestrian streets and their explicit connectors were reviewed.
# Unnamed spurs into residences and private/ambiguous residential decks are excluded.
WAY_IDS={1187601801,1187601819,856416287,49887220,48126232,507688251,
         377823160,377823158,377823159,507696948,170697246,244106714}
ITINERARY=[11027730022,4971966766,1818531021,1818531023,611687216]
PUBLIC_REFERENCES=[
 {'url':'https://www.td.gov.hk/en/transport_in_hong_kong/public_transport/ferries/service_details/index_t.html','publisher':'Transport Department','supports':'The ferry service uses Tai O Promenade Landing Steps. The route starts on the public promenade above the tidal landing steps; it does not descend to a vessel.'},
 {'url':'https://www.cedd.gov.hk/eng/about-us/organisation/ceo/pwd/port-main/public_piers/nti/index.html','publisher':'Civil Engineering and Development Department','supports':'Public landing facilities IP099 and IP100 are Tai O Promenade Landing No.1 and No.2.'},
 {'url':'https://www.islands.gov.hk/en/explores-tai-o-tai-chung-bridge-tai-o-creek-pedestrian-bridge.php','publisher':'Islands District Office','supports':'Tai Chung Bridge is the main pedestrian drawbridge between Tai O Market Street and Wing On Street. This official description takes precedence over the conflicting OSM floating-structure tag.'},
 {'url':'https://www.heritage.gov.hk/en/financial-assistance-for-maintenance-scheme/information-on-applications/2017-2018/kwan-tai-temple/index.html','publisher':'Commissioner for Heritage Office','supports':'Kwan Tai Temple is on Kat Hing Back Street; the published public-access arrangement is 06:00–17:00. This route stops outside its frontage and does not imply access to the interior.'},
 {'url':'https://www.discoverhongkong.com/eng/place-to-go/travel.guide-solo.html','publisher':'Hong Kong Tourism Board','supports':'Visitor destination at 86–88 Kat Hing Street supports the public visitor-street context. No access to private buildings/decks is inferred.'},
]


def permitted(tags):
 return tags.get('highway') in {'pedestrian','footway','path','living_street','steps'} and not any(tags.get(k) in RESTRICTED_ACCESS for k in ('access','foot')) and tags.get('area')!='yes' and tags.get('indoor')!='yes' and not tags.get('tunnel') and tags.get('location')!='underground'


def shortest(graph,start,end):
 queue=[(0,start,[])];seen=set()
 while queue:
  length,node,edges=heapq.heappop(queue)
  if node in seen:continue
  if node==end:return edges
  seen.add(node)
  for target,distance,way in sorted(graph[node]):
   heapq.heappush(queue,(length+distance,target,edges+[(node,target,way)]))
 raise ValueError(f'No source-node-connected public route from {start} to {end}')


def build():
 raw=SOURCE.read_bytes();data=json.loads(gzip.decompress(raw))
 ways={e['id']:e for e in data['elements'] if e['type']=='way' and e['id'] in WAY_IDS}
 if set(ways)!=WAY_IDS:raise ValueError('Missing retained route ways')
 nodes={};graph=collections.defaultdict(list)
 for way,e in ways.items():
  if not permitted(e['tags']):raise ValueError(f'Restricted or unsupported route way {way}')
  if len(e['nodes'])!=len(e['geometry']):raise ValueError(f'Incomplete source geometry {way}')
  for node,p in zip(e['nodes'],e['geometry']):
   point=list(xy(p['lon'],p['lat']))
   if node in nodes and math.dist(nodes[node],point)>1e-6:raise ValueError('Source-node coordinate mismatch')
   nodes[node]=point
  for a,b in zip(e['nodes'],e['nodes'][1:]):
   d=math.dist(nodes[a],nodes[b]);graph[a].append((b,d,way));graph[b].append((a,d,way))
 edges=[]
 for start,end in zip(ITINERARY,ITINERARY[1:]):edges.extend(shortest(graph,start,end))
 node_ids=[edges[0][0]]+[e[1] for e in edges]
 centreline=[nodes[n] for n in node_ids]
 # Join the current checked arrival to its exact position on the same source way.
 arrival=json.loads((HERE.parent/'arrival-overrides.json').read_text())['places']['taiopromenade']
 arrival_way=int(arrival['arrivalSource'].split('/')[-1]);point=arrival['spawn'];near=[]
 for i,(a,b,way) in enumerate(edges):
  if way!=arrival_way:continue
  pa,pb=centreline[i:i+2];dx,dz=pb[0]-pa[0],pb[1]-pa[1]
  fraction=max(0,min(1,((point[0]-pa[0])*dx+(point[1]-pa[1])*dz)/(dx*dx+dz*dz)))
  projected=[pa[0]+dx*fraction,pa[1]+dz*fraction]
  near.append((math.dist(point,projected),i,fraction,projected))
 if not near:raise ValueError('Current arrival is not on a reviewed route source way')
 distance,trim,fraction,projected=min(near)
 if distance>.1:raise ValueError('Arrival exceeds its documented decimetre rounding tolerance')
 start={'placeId':'taiopromenade','position':point,'sourceWayId':arrival_way,'sourceUrl':arrival['arrivalSource'],'sourceNodes':node_ids[trim:trim+2],'fraction':fraction,'projectedPosition':projected,'roundingConnectorMetres':distance,'note':'The existing validated arrival is rounded to0.1m. Its short connector goes to the exact projection on the same public source edge.'}
 centreline=[point,projected]+centreline[trim+1:]
 node_ids=[None,None]+node_ids[trim+1:]
 edges=[(None,None,arrival_way),(None,node_ids[2],arrival_way)]+edges[trim+1:]
 segments=[]
 for i,(a,b,way) in enumerate(edges):
  e=ways[way];tags=e['tags']
  if segments and segments[-1]['sourceWayId']==way:segments[-1]['toIndex']=i+1
  else:
   kind='bridge' if tags.get('bridge')=='yes' else 'steps' if tags['highway']=='steps' else 'crossing' if tags.get('footway')=='crossing' else 'path'
   segment={'fromIndex':i,'toIndex':i+1,'sourceWayId':way,'sourceUrl':f'https://www.openstreetmap.org/way/{way}','tags':tags,'kind':kind,'name':tags.get('name:en',tags.get('name','Mapped public footway'))}
   if kind=='bridge':segment.update(bridgeId=f'way/{way}',widthMetres=None,widthSource='Not recorded in retained centreline; use independently reviewed bridge surface geometry.',requiresWalkingSurface=True)
   if tags.get('virtual')=='yes' or tags.get('note'):segment['geometryCaveat']='The retained map marks this centreline as virtual or affected by imagery distortion; no surveyed alignment is claimed.'
   if way==856416287:segment['crossingNote']='Mapped pedestrian approach also records two unmarked lanes; permitted service-vehicle conflict cannot be excluded. No marked road crossing is invented.'
   segments.append(segment)
 cumulative=[0.0]
 for a,b in zip(centreline,centreline[1:]):cumulative.append(cumulative[-1]+math.dist(a,b))
 for segment in segments:segment['lengthMetres']=round(cumulative[segment['toIndex']]-cumulative[segment['fromIndex']],3)
 stop_specs=[('promenade-landing','Promenade landing approach','海濱長廊碼頭入口',None,1187601819),('wing-on-street','Wing On Street','永安街',4982373284,49887220),('tai-chung-bridge','Tai Chung Bridge','大涌橋',611687308,507688251),('tai-o-market','Tai O Market frontage','大澳街市門前',4971966766,244105525),('kwan-tai-temple','Kwan Tai Temple frontage','關帝古廟門前',1818531021,507687002),('kat-hing-street','Kat Hing Street','吉慶街',611687216,244106714)]
 stops=[];start_index=0
 for id,title,zh,node,way in stop_specs:
  i=node_ids.index(node,start_index);start_index=i
  stops.append({'id':id,'title':title,'zh':zh,'index':i,'sourceNodeId':node,'distanceMetres':round(cumulative[i],3),'source':f'https://www.openstreetmap.org/way/{way}'})
 return {'schemaVersion':1,'id':'tai-o-village-walk','title':'Tai O village walk','zh':'大澳漁村漫步','sectionId':'10.10','coordinateSystem':'World metres: x=EPSG:2326 easting−834500, z=816500−northing; route has no assumed elevation.','status':'source-verified-runtime-pending','arrivalInterpolation':start,'centreline':centreline,'nodeIds':node_ids,'segments':segments,'stops':stops,'lengthMetres':round(cumulative[-1],3),'publicAccessReviewed':True,'continuousWalkVerified':False,'sourceOffsets':[],'sources':[{'file':str(SOURCE.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'snapshotUTC':data['osm3s']['timestamp_osm_base'],'attribution':'OpenStreetMap contributors','licence':'ODbL-1.0'},*PUBLIC_REFERENCES],'limits':['A mapped public visitor route, not a surveyed accessibility guarantee or live GPS route.','Only source-node-connected footways and pedestrian streets are used. Private and ambiguous residential decks, tidal landing stairs, temple interiors and ferry boarding are excluded.','The market-frontage visit includes a short return along the same public street before continuing to the temple.','No steps or marked road crossings occur on this retained route; the shared pedestrian/service approach is flagged explicitly.','Bridge elevation and width require the reviewed walking surface; map layer/structure tags do not establish a safe deck height.','Runtime walking acceptance requires continuously replaying Navigation across the whole route after channel, collision and bridge integration.']}

if __name__=='__main__':
 route=build();DOC.mkdir(parents=True,exist_ok=True)
 (DOC/'route.json').write_text(json.dumps(route,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'lengthMetres':route['lengthMetres'],'vertices':len(route['centreline']),'segments':len(route['segments']),'stops':len(route['stops']),'bridges':[s['bridgeId'] for s in route['segments'] if s['kind']=='bridge']}))
