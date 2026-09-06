"""Build mapped bridge/elevated-link centre-lines and source-node-connected access.
No route invention, height estimates, geometry simplification or network access.
"""
from __future__ import annotations
import collections,gzip,hashlib,json,math,pathlib,re,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'source-scripts/city'))
from build_city import xy,coords,geometry,polys,packed
from shapely.geometry import LineString,Point
from shapely.strtree import STRtree
OUT=ROOT/'3d-viewer/city/data/bridges.json';DOC=ROOT/'docs/astra-city/bridges'
WALK={'footway','path','pedestrian','steps','cycleway','corridor'}
BRIDGE_VALUES={'yes','viaduct','covered','building','boardwalk','movable','cantilever','aqueduct','pier','partial','stacked','trestle','low_water_crossing'}
GROUPS={'island-west':'island','island-east':'island','kowloon':'kowloon','lantau':'lantau','nt-southwest':'ntwest','nt-northwest':'ntwest','nt-central':'nteast','nt-northeast':'nteast','sai-kung':'nteast','nt-north':'ntnorth','outlying-west':'islands','outlying-south':'islands'}


def scalar(value):
 if value is None or not re.fullmatch(r'-?\d+(?:\.\d+)?',str(value).strip()):return None
 n=float(value);return int(n) if n.is_integer() else n

def metres(value):
 # Ambiguous lists/ranges, imperial units and non-numeric text stay in raw tags.
 if value is None:return None
 m=re.fullmatch(r'\s*(-?\d+(?:\.\d+)?)\s*(?:m|metres|meters)?\s*',str(value))
 return float(m[1]) if m else None

def levels(value):
 if value is None:return []
 tokens=re.split('[;,]',str(value));parsed=[scalar(v.strip()) for v in tokens]
 return parsed if all(v is not None for v in parsed) else []

def classify(tags):
 kind=tags.get('highway')
 if not kind or kind in ('construction','proposed','elevator') or tags.get('area')=='yes' or tags.get('location')=='underground':return None
 if tags.get('bridge') in BRIDGE_VALUES:return 'bridge'
 if kind not in WALK or tags.get('tunnel') in ('yes','building_passage') or tags.get('bridge')=='no':return None
 level=levels(tags.get('level'));layer=scalar(tags.get('layer'));minimum=metres(tags.get('min_height'))
 if level and max(level)>0 or layer is not None and layer>0 or minimum is not None and minimum>0:return 'elevated-link'
 return None

def read_sources():
 records={};sources=[];origin={};duplicates=0;baseline=set();node_coordinates={}
 paths=[p for p in sorted((ROOT/'source-scripts/city/snapshots').glob('*.json.gz')) if not p.name.startswith('activity-')]
 supplement=HERE/'hong-kong-bridges-osm.json.gz'
 if supplement.exists():paths.append(supplement)
 districts=HERE/'hong-kong-districts-osm.json.gz'
 if districts.exists():paths.append(districts)
 for path in paths:
  raw=path.read_bytes();obj=json.loads(gzip.decompress(raw));file=str(path.relative_to(ROOT));snapshot=path.name.removesuffix('.json.gz')
  sources.append(dict(file=file,sha256=hashlib.sha256(raw).hexdigest(),timestamp=obj.get('osm3s',{}).get('timestamp_osm_base'),elements=len(obj['elements']),licence='ODbL-1.0',attribution='OpenStreetMap contributors'))
  timestamp=obj.get('osm3s',{}).get('timestamp_osm_base','')
  for e in obj['elements']:
   for node,point in zip(e.get('nodes',[]),e.get('geometry',[])):
    previous=node_coordinates.get(node)
    if previous is None or (timestamp,file)>=(previous['timestamp'],previous['file']):node_coordinates[node]=dict(lat=point['lat'],lon=point['lon'],timestamp=timestamp,file=file)
   oid=f'{e["type"]}/{e["id"]}'
   if oid in records:duplicates+=1
   records[oid]=e
   if snapshot in GROUPS:origin[oid]=snapshot;baseline.add(oid)
 updated_ways=0;updated_nodes=set()
 for e in records.values():
  updates=[]
  for index,(node,point) in enumerate(zip(e.get('nodes',[]),e.get('geometry',[]))):
   latest=node_coordinates[node]
   if point['lat']!=latest['lat'] or point['lon']!=latest['lon']:
    updates.append(dict(nodeId=node,sourceFile=latest['file'],sourceTimestamp=latest['timestamp'],original=[point['lon'],point['lat']],resolved=[latest['lon'],latest['lat']]))
    e['geometry'][index]=dict(lat=latest['lat'],lon=latest['lon']);updated_nodes.add(node)
  if updates:e['_nodeCoordinateUpdates']=updates;updated_ways+=1
 return records,sources,origin,duplicates,baseline,dict(updatedWays=updated_ways,updatedNodeIds=len(updated_nodes),rule='Use the newest retained source coordinate for each original OSM node ID; raw snapshots remain unchanged.')

def projected_parts(element,boundary):
 if not element.get('geometry') or len(element['geometry'])<2:return []
 points=coords(element['geometry']);line=LineString(points)
 if not line.is_valid or line.length<.1:return []
 clipped=line.intersection(boundary)
 if clipped.is_empty:return []
 return [clipped] if clipped.geom_type=='LineString' else [p for p in getattr(clipped,'geoms',[]) if p.geom_type=='LineString' and p.length>.1]

def main():
 records,sources,origin,duplicates,baseline,coordinate_audit=read_sources();boundary=geometry(records['relation/913110']);selected={};rejected=collections.Counter();source_lines={}
 district_names=[];district_polys=[]
 for e in records.values():
  t=e.get('tags',{});name=t.get('name:en','')
  if e['type']=='relation' and t.get('admin_level')=='6' and (name.endswith('District') or name=='Lok Ma Chau Loop'):
   polygon=geometry(e).intersection(boundary)
   if not polygon.is_empty:district_names.append(name);district_polys.append(polygon)
 district_tree=STRtree(district_polys)
 def district_for(line):
  centre=line.interpolate(.5,normalized=True);candidates=[i for i in district_tree.query(centre) if district_polys[i].covers(centre)]
  if not candidates:return 'Boundary waters / unassigned'
  return district_names[min(candidates,key=lambda i:district_names[i])]

 for oid,e in records.items():
  if e['type']!='way':continue
  t=e.get('tags',{});role=classify(t)
  if not role:
   if t.get('bridge') not in (None,'no'):rejected['unusableOrUnknownBridgeTag']+=1
   continue
  parts=projected_parts(e,boundary)
  if not parts:rejected['outsideBoundaryOrDegenerate']+=1;continue
  selected[oid]=role;source_lines[oid]=parts
 # A candidate access way must share an ORIGINAL source node at one of its ends
 # with a selected bridge/link. XY proximity and unrelated crossings are insufficient.
 bridge_nodes=collections.defaultdict(set)
 for oid in selected:
  for node in records[oid].get('nodes',[]):bridge_nodes[node].add(oid)
 
 for oid,e in records.items():
  if oid in selected or e['type']!='way':continue
  t=e.get('tags',{});nodes=e.get('nodes',[])
  if t.get('highway') not in WALK or t.get('area')=='yes' or not nodes or t.get('location')=='underground' or t.get('tunnel') in ('yes','building_passage'):continue
  linked={node:bridge_nodes[node] for node in (nodes[0],nodes[-1]) if bridge_nodes.get(node)}
  if not linked:continue
  parts=projected_parts(e,boundary)
  if not parts:continue
  selected[oid]='access';source_lines[oid]=parts
 exports=[]
 for oid in sorted(selected,key=lambda s:int(s.split('/')[1])):
  e=records[oid];tags=e.get('tags',{});role=selected[oid];original=coords(e['geometry']);nodes=e.get('nodes',[])
  node_lookup={(round(p[0],2),round(p[1],2)):nodes[i] for i,p in enumerate(original) if i<len(nodes)}
  for part_index,line in enumerate(source_lines[oid]):
   path=[[round(x,2),round(z,2)] for x,z in line.coords]
   if len({tuple(p) for p in path})<2:rejected['roundingDegenerate']+=1;continue
   # Consecutive vertices remain untouched: stair endpoints and shared junctions matter.
   id=oid if len(source_lines[oid])==1 else oid+':'+str(part_index)
   record=dict(id=id,source='https://www.openstreetmap.org/'+oid,path=path,nodes=[node_lookup.get(tuple(p)) for p in path],kind=tags['highway'],role=role,bridge=tags.get('bridge') if role=='bridge' else 'elevated-link' if role=='elevated-link' else None,layer=scalar(tags.get('layer')),tags=tags,district=district_for(line),length=round(line.length,2))
   evidence=[]
   if role=='bridge':evidence.append('bridge-tag')
   if tags.get('indoor')=='yes':record['interior']=True
   for key,field,parser in [('level','level',scalar),('width','width',metres),('height','height',metres),('min_height','minHeight',metres),('ele','ele',metres)]:
    if key in tags:
     value=parser(tags[key])
     if value is not None and (key not in ('width','height','min_height') or value>0 or key=='min_height' and value==0):record[field]=value
     if key in ('level','height','min_height','ele'):evidence.append(key+'-tag')
   lv=levels(tags.get('level'))
   if len(lv)>1:record['levels']=lv
   if record['layer'] is not None:evidence.append('layer-ordering')
   record['elevationEvidence']=evidence
   if 'covered' in tags:record['covered']=tags['covered'] in ('yes','arcade','colonnade')
   elif tags.get('bridge')=='covered':record['covered']=True
   if tags.get('name'):record['name']=tags.get('name:en',tags['name'])
   zh=tags.get('name:zh-Hant',tags.get('name:zh'))
   if zh:record['zh']=zh
   if e.get('_nodeCoordinateUpdates'):record['coordinateUpdates']=e['_nodeCoordinateUpdates']
   exports.append(record)
 # Restrict links to node IDs actually retained after clipping, including an
 # explicit vertex index so the renderer can join decks without geometric guessing.
 bridge_exports_by_node=collections.defaultdict(set)
 for record in exports:
  if record['role']!='access':
   for node in record['nodes']:
    if node is not None:bridge_exports_by_node[node].add(record['id'])
 result=[]
 for record in exports:
  if record['role']=='access':
   connections=[]
   for index in (0,len(record['nodes'])-1):
    node=record['nodes'][index];bridge_ids=bridge_exports_by_node.get(node)
    if bridge_ids:connections.append(dict(nodeId=node,pathIndex=index,position=record['path'][index],bridgeIds=sorted(bridge_ids)))
   if not connections:rejected['clippedAccessLostConnection']+=1;continue
   record['connections']=connections;record['connectsTo']=sorted({id for c in connections for id in c['bridgeIds']})
  result.append(record)
 # Separate polygon outlines avoid drawing one shared deck repeatedly for each
 # traffic centre-line. Link only matching-layer routes with >=90% containment.
 lines=[LineString(r['path']) for r in result if r['role']!='access'];line_records=[r for r in result if r['role']!='access'];tree=STRtree(lines);decks=[]
 for oid,e in sorted(records.items()):
  t=e.get('tags',{})
  if t.get('man_made')!='bridge':continue
  shape=geometry(e)
  if shape is None or shape.is_empty:continue
  for i,p in enumerate(polys(shape.intersection(boundary))):
   if p.area<5 or p.area>200000:continue
   linked=[];layer=scalar(t.get('layer'))
   for index in tree.query(p):
    record=line_records[index]
    if layer is None or record['layer']!=layer:continue
    if lines[index].intersection(p.buffer(.1)).length/max(.01,lines[index].length)>=.9:linked.append(record['id'])
   if linked:
    rings=[[[round(x,2),round(z,2)] for x,z in ring.coords] for ring in [p.exterior,*p.interiors]]
    from shapely.geometry import Polygon
    if not Polygon(rings[0],rings[1:]).is_valid:rejected['invalidRoundedDeckOutline']+=1;continue
    decks.append(dict(id=oid+':deck:'+str(i),source='https://www.openstreetmap.org/'+oid,rings=rings,bridgeIds=sorted(linked),tags=t,linkEvidence='Matching explicit layer and at least 90% centre-line containment'))
 counts=dict(records=len(result),uniqueSourceWays=len({r['source'] for r in result}),roles=dict(collections.Counter(r['role'] for r in result)),kinds=dict(collections.Counter(r['kind'] for r in result)),districts=dict(sorted(collections.Counter(r['district'] for r in result).items())),interior=sum(bool(r.get('interior')) for r in result),vertices=sum(len(r['path']) for r in result),taggedWidth=sum('width' in r for r in result),taggedHeight=sum('height' in r for r in result),taggedMinHeight=sum('minHeight' in r for r in result),taggedAbsoluteElevation=sum('ele' in r for r in result),deckOutlines=len(decks))
 data=dict(schemaVersion=1,bridges=result,decks=decks,sources=sources,counts=counts);OUT.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
 audit=dict(counts=counts,coordinateNormalisation=coordinate_audit,duplicateInputRecordsCollapsed=duplicates,rejections=dict(rejected),boundarySource='https://www.openstreetmap.org/relation/913110',supplementRetained=(HERE/'hong-kong-bridges-osm.json.gz').exists(),supplementOnlyWays=sum(r['source'].removeprefix('https://www.openstreetmap.org/') not in baseline for r in result),byDistrictAndRole={district:dict(collections.Counter(r['role'] for r in result if r['district']==district)) for district in sorted({r['district'] for r in result})},precision='Coordinates projected from OSM and rounded to 0.01 m; no claim of centimetre source accuracy. No bridge line simplification.',districtDefinition='Midpoint containment in the 18 retained OSM district boundaries, clipped to Hong Kong. Lok Ma Chau Loop is a separate source boundary. Boundary ties use a deterministic alphabetical choice; these are OSM geometry statistics, not an official bridge census.',completeness='All usable tagged highway bridge/elevated walking segments in the retained snapshots, plus directly endpoint-connected access ways. OSM gaps and untagged inter-building links remain unknown.')
 DOC.mkdir(parents=True,exist_ok=True);(DOC/'verification.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');print(json.dumps(counts,indent=2));return data,audit
if __name__=='__main__':main()
