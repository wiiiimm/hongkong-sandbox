"""Join retained building-use tags and spatial land use to the committed city forms.
No geometry is changed; the sidecar records each classification's evidence.
"""
import collections,gzip,hashlib,json,pathlib,re
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from build_city import ROOT,OUT,geometry,polys
HERE=pathlib.Path(__file__).resolve().parent
HOME={'residential','apartments','apartment','house','detached','semidetached_house','terrace','dormitory','bungalow','houseboat'}
WORK={'office','school','college','university','kindergarten','industrial','warehouse','civic','government','courthouse','service','garage','garages','shed','parking','place_of_worship'}
NIGHT={'hotel','hospital','fire_station','police','hostel','guest_house','nursing_home'}
RETAIL={'retail','shop','mall','supermarket','department_store','restaurant','cafe','fast_food','bar','pub','marketplace','cinema'}
def profile(value):
 values=set(re.split('[;,]',value or ''))
 if values&HOME:return 0
 if values&NIGHT:return 2
 if values&RETAIL:return 4
 if values&WORK:return 1
 return None
def tagged(t):
 # Current use outranks structural building type; shop tags on a home describe its lower floor.
 if 'building:use' in t and profile(t['building:use']) is not None:
  p=profile(t['building:use']);return p,'building:use',3.5 if p==0 and (set(re.split('[;,]',t['building:use']))&RETAIL or t.get('shop')) else 0
 p=profile(t.get('building:part'))
 if p is not None:return p,'building:part',0
 for key in ['tourism','amenity']:
  p=profile(t.get(key))
  if p is not None:return p,key,0
 p=profile(t.get('building'))
 if p==0:return p,'building',3.5 if t.get('shop') or t.get('mall')=='yes' else 0
 if t.get('shop') not in (None,'no','vacant') or t.get('mall')=='yes':
  return (2 if t.get('opening_hours')=='24/7' else 4),'shop' if t.get('shop') else 'mall',0
 if t.get('office') not in (None,'no','vacant'):return 1,'office',0
 if p is not None:return p,'building',0
 return None

def related_refs(building, records):
 # A large mall footprint can overlap both its podium and a named office tower.
 # Prefer the identity matching the official building name before the area winner.
 def names(values):
  return {re.sub(r'[^\w]', '', str(value)).casefold() for value in values if value}
 identities=names([building.get('name'),building.get('zh')])
 refs=list(dict.fromkeys(oid for oid in [building.get('osmRef'),building.get('parent'),*building.get('osmRefs',[])] if oid))
 def same_name(oid):
  tags=records.get(oid,{}).get('tags',{})
  return bool(identities & names([tags.get(key) for key in ['name','name:en','name:zh','name:zh-Hant']]))
 return sorted(refs,key=lambda oid:not same_name(oid))

def main():
 manifest=json.loads((OUT/'manifest.json').read_text());records={};sources=[]
 for source in sorted(manifest['sources'],key=lambda x:x['snapshot']):
  raw=gzip.decompress((ROOT/source['file']).read_bytes());assert hashlib.sha256(raw).hexdigest()==source['sha256']
  data=json.loads(raw);sources.append({k:source[k] for k in ['file','sha256','snapshot']})
  for e in data['elements']:records[f'{e["type"]}/{e["id"]}']=e
 raw=gzip.decompress((HERE/'snapshots/activity-landuse.json.gz').read_bytes());land=json.loads(raw)
 if land.get('remark'):raise ValueError('Partial land-use data')
 sources.append({'file':str((HERE/'snapshots/activity-landuse.json.gz').relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'snapshot':land['osm3s']['timestamp_osm_base']})
 land_records={f'{e["type"]}/{e["id"]}':e for e in land['elements']}
 # Regional snapshots contain later retained land-use tags across the expanded territory.
 # Replace overlaps only when the regional snapshot is at least as recent.
 for source in sorted(manifest['sources'],key=lambda x:x['snapshot']):
  region=json.loads(gzip.decompress((ROOT/source['file']).read_bytes()))
  for e in region['elements']:
   if e.get('tags',{}).get('landuse') in {'residential','commercial','industrial','retail'}:
    oid=f'{e["type"]}/{e["id"]}'
    if oid not in land_records or source['snapshot']>=land['osm3s']['timestamp_osm_base']:land_records[oid]=e
 geos=[];uses=[]
 for e in land_records.values():
  p={'residential':0,'commercial':1,'industrial':1,'retail':4}.get(e.get('tags',{}).get('landuse'))
  if p is None:continue
  g=geometry(e)
  if g is None:continue
  for polygon in polys(g):
   if polygon.area>8:geos.append(polygon);uses.append((p,f'{e["type"]}/{e["id"]}',e['tags']['landuse']))
 tree=STRtree(geos);overrides=json.loads((HERE/'activity-overrides.json').read_text());entries={};counts=collections.Counter();basis=collections.Counter();podiums=0
 activity_dir=OUT/'activity';activity_dir.mkdir(exist_ok=True)
 for tile in manifest['tiles']:
  tile_entries={}
  for b in json.loads((ROOT/'3d-viewer'/tile['url']).read_text())['buildings']:
   rule=next((r for r in overrides if r['id'] in [b['id'],b.get('parent'),*b.get('osmRefs',[])] and b['height']>=r.get('minBuildingHeight',0)),None)
   entry=None
   if rule:entry={'profile':rule['profile'],'source':'research','ref':rule['source'],'retailTop':rule['retailTop']}
   for oid,source in [(b['id'],'building-tag')]+[(oid,'parent-tag') for oid in related_refs(b,records)]:
    if entry:break
    t=records.get(oid,{}).get('tags',{});result=tagged(t)
    if result:
     p,key,retail=result;entry={'profile':p,'source':source,'ref':oid,'tag':key+'='+t.get(key,''),'retailTop':retail}
   if not entry:
    p=Polygon(b['rings'][0],b['rings'][1:]).buffer(0)
    matches=[int(i) for i in tree.query(p) if geos[i].intersection(p).area>=p.area*.5]
    if matches:
     i=min(matches,key=lambda i:(geos[i].area,uses[i][1]));profile_id,oid,kind=uses[i]
     entry={'profile':profile_id,'source':'landuse','ref':oid,'tag':'landuse='+kind,'retailTop':0}
   if not entry:
    p=profile(b['kind']);p=1 if p is None and b['kind']=='commercial' else 3 if p is None else p
    entry={'profile':p,'source':'fallback','ref':b['id'],'tag':'building='+b['kind'],'retailTop':0}
   entries[b['uid']]=entry;tile_entries[b['uid']]=entry;counts[entry['profile']]+=1;basis[entry['source']]+=1;podiums+=entry['retailTop']>0
  sidecar=activity_dir/(tile['id']+'.json');temporary=sidecar.with_suffix('.json.tmp');temporary.write_text(json.dumps({'buildings':tile_entries},ensure_ascii=False,separators=(',',':')));temporary.replace(sidecar)
 manifest['activityTiles']=True;temporary=OUT/'manifest.json.tmp';temporary.write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')));temporary.replace(OUT/'manifest.json')
 result={'version':1,'profiles':['home','office','overnight','mixed','retail'],'licence':'ODbL-1.0','sources':sources,'overrideFile':'source-scripts/city/activity-overrides.json','landusePolygons':len(geos),'counts':dict(counts),'basisCounts':dict(basis),'splitUseForms':podiums,'policy':'Building current-use tags, building-part tags and related OSM tags before smallest land-use polygon covering at least half the footprint; for government forms, strongly overlapping OSM identities matching the official name precede the largest overlap; documented research overrides for mixed-use landmarks. Land use is an inference, not verified tenancy. Unknown uses remain labelled estimates.','buildings':entries}
 (OUT/'activity.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
 print(json.dumps({k:v for k,v in result.items() if k not in ['buildings','sources']},indent=2))
if __name__=='__main__':main()
