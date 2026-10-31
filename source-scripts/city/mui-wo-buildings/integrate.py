"""Publish official-primary footprints through the existing city tile pipeline.
Re-run safely: restore the frozen OSM baseline before resolving overlap. Source
vertices/elevations stay unchanged; estimates and terrain reconciliation stay labelled.
"""
import collections,gzip,json,math,pathlib,sys
from shapely.geometry import Polygon
from shapely.strtree import STRtree
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'3d-viewer/city/data'
sys.path.insert(0,str(HERE));from build import render_elevations

def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,separators=(',',':')))
def counts(t):return {'buildings':len(t['buildings']),'roads':len(t['roads']),'parks':len(t['parks']),'heights':dict(collections.Counter(b['heightSource'] for b in t['buildings']))}
def main():
 package=json.loads((OUT/'mui-wo-buildings.json').read_text());manifest=json.loads((OUT/'manifest.json').read_text());tiles={p.stem:json.loads(p.read_text()) for p in (OUT/'tiles').glob('*.json')}
 baseline=json.loads(gzip.decompress((HERE/'osm-baseline.json.gz').read_bytes()))['buildings']
 # Reverse only this official layer before the deterministic re-merge.
 for t in tiles.values():t['buildings']=[b for b in t['buildings'] if not b['id'].startswith('landsd/')]
 ids={b['uid'] for t in tiles.values() for b in t['buildings']}
 for b in baseline:
  if b['uid'] not in ids:tiles[b['tile']]['buildings'].append(b)
 osm={b['uid']:b for t in tiles.values() for b in t['buildings']};polys=[Polygon(b['rings'][0],b['rings'][1:]) for b in package['buildings']];tree=STRtree(polys)
 removed=set();matches={}
 for b in baseline:
  p=Polygon(b['rings'][0],b['rings'][1:]);candidates=[]
  for i in tree.query(p):
   area=p.intersection(polys[i]).area
   if area>0.01:candidates.append((int(i),area,area/p.area,area/polys[i].area))
  # Official coverage takes precedence; small edge slivers are documented, not new duplicate blocks.
  if any(a>=.15 or c>=.5 for _,_,a,c in candidates):removed.add(b['uid'])
  for i,area,a,c in candidates:
   if a>=.5 or c>=.5:matches.setdefault(i,[]).append((area,b))
 fine=json.loads((ROOT/'docs/astra-city/mui-wo-buildings/fine-terrain-audit.json').read_text());fine_by_id={b['uid']:b for b in fine['buildings']}
 models_path=ROOT/'docs/astra-city/mui-wo-buildings/review/model-sample/model-geometries.json'
 models=json.loads(models_path.read_text())['byBuildingUid'] if models_path.exists() else {}
 official=[]
 for i,raw in enumerate(package['buildings']):
  b=dict(raw);b['sourceDataset']='landsd-mui-wo';b.pop('coverage',None);b.pop('locality',None);b.pop('terrain',None)
  audit=fine_by_id[b['uid']];b.update(render_elevations(b['sourceAttributes'],audit['fineTerrain']));b['terrainAudit']={k:audit[k] for k in ('roofWhollyBelowTerrain','roofPartlyBelowTerrain','baseWhollyAboveTerrain')}
  if b['base']>audit['fineTerrain']['min']+.5:
   b['foundationBase']=audit['fineTerrain']['min'];b['foundationPolicy']='Illustrative foundation down to the DTM minimum; source base and roof unchanged'
  if b['uid'] in models:b['modelGeometry']=models[b['uid']]
  if i in matches:
   old=max(matches[i],key=lambda x:x[0])[1];b['osmRef']=old['id'];b['parent']=old.get('parent',old['id']);b['kind']=old['kind'] if old['kind']!='yes' else b['kind']
   if not b['name']:b['name']=old['name']
   if not b['zh']:b['zh']=old['zh']
  official.append(b)
 for t in tiles.values():t['buildings']=[b for b in t['buildings'] if b['uid'] not in removed]
 for b in official:tiles.setdefault(b['tile'],dict(id=b['tile'],buildings=[],roads=[],parks=[]))['buildings'].append(b)
 metadata=[];size=manifest['tileSize'];all_buildings=[]
 for key,t in sorted(tiles.items()):
  x,z=map(int,key.split('_'));bounds=[x*size,z*size,(x+1)*size,(z+1)*size]
  for b in t['buildings']:
   for px,pz in b['rings'][0]:bounds=[min(bounds[0],px),min(bounds[1],pz),max(bounds[2],px),max(bounds[3],pz)]
  t['bounds']=bounds;path=OUT/'tiles'/f'{key}.json';content=json.dumps(t,ensure_ascii=False,separators=(',',':')).encode()
  if not path.exists() or path.read_bytes()!=content:path.write_bytes(content)
  metadata.append(dict(id=key,bounds=bounds,centre=[(x+.5)*size,(z+.5)*size],url=f'city/data/tiles/{key}.json',bytes=len(content),counts=counts(t)));all_buildings.extend(t['buildings'])
 catalog=[{k:b[k] for k in ('id','uid','tile','name','zh','height','heightSource','levels','base','centre')}|({'parent':b['parent']} if b.get('parent') else {}) for b in all_buildings if b['name'] or b['zh']]
 dump(OUT/'catalogue.json',catalog);dump(OUT/'overview.json',{k:[b['centre'] for b in t['buildings']] for k,t in tiles.items() if t['buildings']})
 manifest.update(tiles=metadata,supplementalSources=package['supplementalSources'],source='Lands Department / Hong Kong SAR Government and OpenStreetMap contributors',coveragePolicy='Official LandsD primary building coverage in Mui Wo; OSM coverage elsewhere. All official Mui Wo polygons/types retained. Overlapping OSM massing replaced; matching names and uses retained as supplemental evidence.',heightPolicy='LandsD BaseHeight/TopHeight are approximate absolute HKPD elevations; valid differences set building height without adding terrain again. Missing values use labelled estimates. OSM retains tagged/floor-count/type estimates.',terrainPatches=[{'url':'city/data/terrain-mui-wo.json','resolution':5,'area':'Mui Wo','source':json.loads((OUT/'terrain-mui-wo.json').read_text())['meta']['source']}])
 manifest['counts']={'buildings':len(all_buildings),'roads':sum(len(t['roads']) for t in tiles.values()),'parks':sum(len(t['parks']) for t in tiles.values()),'heights':dict(collections.Counter(b['heightSource'] for b in all_buildings))}
 manifest['heightEstimateCounts']=dict(collections.Counter(b.get('heightRule','generic') for b in all_buildings if b['heightSource']=='estimated'))
 manifest['officialCoverage']={'sourceRecords':package['counts']['sourceRecords'],'renderedComponents':len(official),'replacedOSMForms':len(removed),'area':'Mui Wo','sourceIds':len({b['id'] for b in official}),'detailedModels':sum('modelGeometry' in b for b in official)};dump(OUT/'manifest.json',manifest)
 report={**manifest['officialCoverage'],'cityForms':len(all_buildings),'osmFormsRetained':len(all_buildings)-len(official),'recordedHeightForms':sum(b['heightSource']=='landsd' for b in official),'estimatedHeightForms':sum(b['heightSource']=='estimated' for b in official),'replacedOSM':sorted(removed),'officialSourceIds':sorted(b['id'] for b in official),'policy':manifest['coveragePolicy']};dump(ROOT/'docs/astra-city/mui-wo-buildings/integration.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ('replacedOSM','officialSourceIds')},indent=2))
if __name__=='__main__':main()
