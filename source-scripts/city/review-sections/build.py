#!/usr/bin/env python3
"""Deterministic project review areas, not official neighbourhood boundaries.
Native HAD district polygons are partitioned by retained source place anchors.
Explicit OSM island ownership overrides ordinary nearest-anchor cells.
"""
import collections,gzip,hashlib,json,pathlib,re,sys
import shapely
from shapely.geometry import Polygon,MultiPolygon,Point,MultiPoint,box
from shapely.ops import unary_union,nearest_points
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent));from build_city import xy,geometry
OUT=ROOT/'3d-viewer/city/data/review-sections.json';DOC=ROOT/'docs/astra-city/review-sections'
VERSION='had-2016-project-2026-09-07-v1'
CODES={'CW':'01','WC':'02','EST':'03','STH':'04','YTM':'05','SSP':'06','KLC':'07','WTS':'08','KT':'09','ILD':'10','TW':'11','KC':'12','ST':'13','TP':'14','SK':'15','TM':'16','YL':'17','NTH':'18'}
def sid(value):
 a,b=value.split('.');return f'{int(a):02}.{int(b)}'
def poly_parts(g):
 if g.geom_type=='Polygon':return [g] if not g.is_empty else []
 return [p for c in getattr(g,'geoms',[]) for p in poly_parts(c)]
def polygonal(g):return unary_union(poly_parts(g))
def load_districts():
 result={}
 for f in json.loads((HERE/'sources/districts.json').read_text())['features']:
  assert len(f['geometry']['rings'])==1,'Review changed official topology before reuse'
  result[CODES[f['attributes']['AREA_CODE']]]={'geometry':Polygon([(x-834500,816500-y) for x,y in f['geometry']['rings'][0]]),'attributes':f['attributes']}
 return result
def checklist():
 text=(ROOT/'docs/astra-city/SECTION-CHECKLIST.md').read_text();districts={k:v.strip() for k,v in re.findall(r'^## (\d{2})\. ([^\n]+)',text,re.M)}
 names={sid(k):v.strip() for k,v in re.findall(r'^- \[[ x]\] \*\*(\d+\.\d+)\*\*\s+([^\n]+)',text,re.M)}
 assert len(names)==132;return names,districts
def anchors():
 out=[]
 for region in ('urban','nt','islands'):
  path=ROOT/f'3d-viewer/city/data/regional/{region}.json'
  for p in json.loads(path.read_text())['places']:
   out.append({'id':p['id'],'sectionId':sid(p['sectionId']),'point':xy(p['lon'],p['lat']),'title':p['title'],'source':p['source'],'sourceFile':str(path.relative_to(ROOT)),'lat':p['lat'],'lon':p['lon']})
 return sorted(out,key=lambda p:(tuple(map(int,p['sectionId'].split('.'))),p['id']))
def load_islands():
 config=json.loads((HERE.parent/'regional/islands/config.json').read_text())
 rules={r['source']:{**r,'sections':[sid(s) for s in r['sections']],'basis':'Existing regional island ownership configuration'} for r in config['islands']}
 for source,sections in {'relation/10599238':['12.4','12.5','12.6'],'relation/10742015':['04.3'],'relation/12922927':['11.5'],'relation/3845760':['15.8'],'relation/9602761':['15.8'],'relation/12926382':['15.9'],'way/9560720':['15.8'],'way/9563706':['15.9'],'relation/8371865':['18.8'],'relation/8371885':['18.8'],'way/9563887':['18.8'],'relation/13023733':['15.6','15.7']}.items():
  rules[source]={'source':source,'sections':sections,'basis':'Named island grouping in the section checklist; source island footprint'}
 elements={};paths=sorted((HERE.parent/'regional/islands/snapshots').glob('*.json.gz'))
 extra=HERE/'sources/islands.json.gz'
 if extra.exists():paths.append(extra)
 hashes=[]
 for path in paths:
  raw=path.read_bytes();data=json.loads(gzip.decompress(raw));hashes.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'timestamp':data.get('osm3s',{}).get('timestamp_osm_base')})
  for e in data.get('elements',[]):
   if e.get('tags',{}).get('place') in ('island','islet') or f"{e['type']}/{e['id']}" in rules:elements[f"{e['type']}/{e['id']}"]=e
 result=[]
 for key,rule in rules.items():
  e=elements.get(key)
  if not e:raise ValueError('Missing retained island '+key)
  g=geometry(e)
  if g is None or g.is_empty:raise ValueError('Missing island polygon '+key)
  result.append({**rule,'geometry':g,'name':e.get('tags',{}).get('name:en',e.get('tags',{}).get('name',key))})
 return result,hashes,elements

def partition(clip,sites):
 """Voronoi union per section. Identical source anchors are rejected, never jittered."""
 pairs=[(s['sectionId'],s['point']) for s in sites]
 assert len({tuple(p) for _,p in pairs})==len(pairs),'Duplicate review anchors need an explicit policy'
 if len(pairs)==1:return {pairs[0][0]:clip}
 cells=shapely.voronoi_polygons(MultiPoint([p for _,p in pairs]),extend_to=box(-100000,-100000,100000,100000),ordered=True)
 groups=collections.defaultdict(list)
 for (key,_),cell in zip(pairs,cells.geoms):groups[key].append(cell.intersection(clip))
 return {k:polygonal(unary_union(v)) for k,v in groups.items()}

def main():
 names,district_names=checklist();districts=load_districts();places=anchors();islands,island_sources,elements=load_islands();seeds=[];exceptions=[]
 for p in places:
  p=dict(p);g=districts[p['sectionId'].split('.')[0]]['geometry'];pt=Point(p['point'])
  if not g.covers(pt):
   distance=g.distance(pt);actual=[key for key,v in districts.items() if v['geometry'].covers(pt)]
   # Partitioning-only seed, 5 m inside the requested district. The original destination is unchanged.
   q=nearest_points(g.buffer(-5),pt)[0];p['point']=(q.x,q.y)
   exceptions.append({'placeId':p['id'],'sectionId':p['sectionId'],'title':p['title'],'sourcePoint':list(pt.coords)[0],'source':p['source'],'actualDistricts':actual,'outsideRequestedDistrictMetres':distance,'partitionSeed':p['point'],'note':'Source destination remains in the neighbouring district. A derived interior seed only preserves this project section in the partition; it is not a relocated visit point.'})
  seeds.append(p)
 island_seeds=[];island_district_conflicts=[]
 for rule in islands:
  allowed_districts={s.split('.')[0] for s in rule['sections']}
  for district,record in districts.items():
   clipped=polygonal(rule['geometry'].intersection(record['geometry']))
   if clipped.area<=1:continue
   if district not in allowed_districts:
    island_district_conflicts.append({'source':rule['source'],'name':rule['name'],'requestedSections':rule['sections'],'actualDistrict':district,'areaM2':clipped.area,'note':'Island outline crosses the official district spine. This piece remains in the official district and its ordinary inferred review partition; no official border is moved.'})
    continue
   allowed=[s for s in rule['sections'] if s.startswith(district+'.')]
   if len(allowed)==1:
    q=max(poly_parts(clipped),key=lambda p:p.area).representative_point()
    island_seeds.append({'id':'island-'+rule['source'],'sectionId':allowed[0],'point':(q.x,q.y),'source':'https://www.openstreetmap.org/'+rule['source'],'title':rule['name'],'basis':'Derived interior anchor of a retained island footprint with explicit single-section ownership; helps group nearby offshore waters.'})
 seeds.extend(island_seeds)
 result={};ownership=[];district_audit=[]
 for district,record in sorted(districts.items()):
  dg=record['geometry'];ds=[p for p in seeds if p['sectionId'].split('.')[0]==district];areas=partition(dg,ds)
  # Smaller explicit island rules win if footprints overlap. Coastline polygons are constraints, not replacement district borders.
  assigned=Polygon()
  for rule in sorted(islands,key=lambda r:(r['geometry'].area,r['source'])):
   allowed=[s for s in rule['sections'] if s.split('.')[0]==district]
   if not allowed:continue
   cut=polygonal(rule['geometry'].intersection(dg).difference(assigned))
   if cut.is_empty:continue
   local=partition(cut,[p for p in ds if p['sectionId'] in allowed]);assigned=unary_union([assigned,cut])
   for s in areas:areas[s]=polygonal(areas[s].difference(cut))
   for s,g in local.items():areas[s]=polygonal(unary_union([areas.get(s,Polygon()),g]))
   ownership.append({'source':rule['source'],'name':rule['name'],'district':district,'sections':allowed,'areaM2':cut.area,'basis':rule['basis']})
  union=unary_union(list(areas.values()));district_audit.append({'district':district,'sourceAreaM2':dg.area,'partitionAreaM2':union.area,'symmetricDifferenceM2':union.symmetric_difference(dg).area,'overlapM2':sum(g.area for g in areas.values())-union.area})
  result.update(areas)
 sections=[]
 for key in sorted(names,key=lambda k:tuple(map(int,k.split('.')))):
  g=result[key];assert g.is_valid and not g.is_empty,(key,shapely.is_valid_reason(g));di=key.split('.')[0];own=[p for p in places if p['sectionId']==key];inside=[Point(p['point']) for p in own if g.covers(Point(p['point']))]
  label=inside[0] if inside else max(poly_parts(g),key=lambda p:p.area).representative_point()
  # Decimal source precision is kept; no independent simplification can open shared-boundary gaps.
  polygons=[{'rings':[list(map(list,p.exterior.coords))]+[list(map(list,r.coords)) for r in p.interiors]} for p in sorted(poly_parts(g),key=lambda p:(-p.area,p.bounds))]
  notes=['Approximate project review area, not an official neighbourhood boundary.','Official HAD district outline includes marine waters; internal divisions are inferred from retained place anchors and explicit island ownership.']
  if any(e['sectionId']==key for e in exceptions):notes.append('One or more checklist destinations lie in a neighbouring official district; see geography-audit.json. Source destination coordinates are unchanged.')
  sections.append({'id':key,'name':names[key],'district':di,'districtName':district_names[di],'polygons':polygons,'label':[label.x,label.y],'bounds':list(g.bounds),'placeIds':[p['id'] for p in own],'sourceNotes':notes})
 source_manifest=json.loads((HERE/'source-manifest.json').read_text())
 input_paths=[ROOT/'docs/astra-city/SECTION-CHECKLIST.md',HERE.parent/'regional/islands/config.json']+[ROOT/f'3d-viewer/city/data/regional/{r}.json' for r in ('urban','nt','islands')]
 input_sources=[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in input_paths]
 provenance={'officialDistricts':source_manifest,'projectInputs':input_sources,'islandSources':island_sources,'algorithm':'District-clipped Euclidean Voronoi cells grouped by section; explicit retained island footprint ownership, smaller footprints first. Outside-district anchors use a derived 5 m interior partition seed; destination coordinates remain unchanged.','crs':'EPSG:2326','axes':'x=E-834500, z=816500-N','boundaryMeaning':'Official district jurisdiction outlines including coastal waters; approximate project review subdivisions, not official neighbourhood boundaries.','licence':'HAD open data and OpenStreetMap contributors, ODbL-1.0','anchorSource':'Existing regional place coordinates, before any adjusted walking spawn; all 132 checklist sections have anchors.','anchorExceptions':exceptions,'islandDerivedAnchors':island_seeds,'islandDistrictConflicts':island_district_conflicts}
 data={'schemaVersion':1,'boundaryVersion':VERSION,'provenance':provenance,'sections':sections}
 temporary=OUT.with_suffix('.json.tmp');temporary.write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False)+'\n');temporary.replace(OUT)
 audit={'boundaryVersion':VERSION,'sourceDistricts':18,'sections':len(sections),'places':len(places),'anchorExceptions':exceptions,'islandOwnership':ownership,'islandDerivedAnchors':island_seeds,'islandDistrictConflicts':island_district_conflicts,'districtTopology':district_audit,'vertices':sum(len(r) for s in sections for p in s['polygons'] for r in p['rings']),'bytes':OUT.stat().st_size,'gzipBytes':len(gzip.compress(OUT.read_bytes(),mtime=0)),'components':sum(len(s['polygons']) for s in sections),'holes':sum(len(p['rings'])-1 for s in sections for p in s['polygons']),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'output':str(OUT.relative_to(ROOT))}
 DOC.mkdir(exist_ok=True,parents=True);(DOC/'geography-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k not in ['anchorExceptions','islandOwnership','islandDerivedAnchors','islandDistrictConflicts','districtTopology']},indent=2))
if __name__=='__main__':main()
