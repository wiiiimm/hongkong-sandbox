"""Attach verified geometry to current territory tiles, preserving every source form.
Does not re-run the old local-only OSM/official overlap merge.
"""
import collections,gzip,hashlib,importlib.util,json,pathlib,sys
from shapely.geometry import Polygon
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'3d-viewer/city/data';DOC=ROOT/'docs/astra-city/mui-wo-buildings/extension'
sys.path.insert(0,str(HERE.parent));from publish_tiles import publish,dump
spec=importlib.util.spec_from_file_location('fine_terrain_audit',HERE.parent/'mui-wo-buildings/fine_terrain_audit.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

def read(path):return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())

def publish_models(payload_path=None,package_path=None,terrain_path=None,doc=DOC,foundation_mode='update',area='Mui Wo'):
 payload_path=payload_path or HERE/'model-geometries.json.gz';package_path=package_path or OUT/'mui-wo-buildings.json';terrain_path=terrain_path or OUT/'terrain-mui-wo.json'
 previous_overview=(OUT/'overview.json').read_bytes()
 manifest=json.loads((OUT/'manifest.json').read_text());before_counts=manifest['counts'];tiles={p.stem:json.loads(p.read_text()) for p in (OUT/'tiles').glob('*.json')}
 package=read(package_path);attrs={b['uid']:b['sourceAttributes'] for b in package['buildings']}
 payload=read(payload_path);models=payload['byBuildingUid'];terrain=audit.FineTerrain(terrain_path);display_terrain=audit.FineTerrain(terrain_path,rendered=True)
 rows=[];counts=collections.Counter();changed=[];seen=set();model_seen=set();revised_estimates=[]
 for tile in tiles.values():
  for b in tile['buildings']:
   assert b['uid'] not in seen,b['uid'];seen.add(b['uid'])
   if b['uid'] not in attrs:continue
   old=dict(b);p=Polygon(b['rings'][0],b['rings'][1:]);t=terrain.extrema(p)
   source=attrs[b['uid']];values=audit.m.render_elevations(source,t);rule=values.pop('heightRule');values.pop('renderTopHeight')
   key=next((k for k,v in manifest['heightRules'].items() if v==rule),None)
   if key is None:key='landsd-'+str(len(manifest['heightRules']));manifest['heightRules'][key]=rule
   b.update(values,heightRule=key)
   if b['base']!=old['base']:revised_estimates.append({'uid':b['uid'],'oldBase':old['base'],'newBase':b['base'],'baseSource':b['baseSource']});assert source['BaseHeight'] is None and source['TopHeight'] is None
   if foundation_mode=='update':
    if b['base']>t['min']+.5:b['foundationBase']=t['min'];b['foundationPolicy']='Illustrative foundation down to the DTM minimum; source base and roof unchanged'
    else:b.pop('foundationBase',None);b.pop('foundationPolicy',None)
   else:assert foundation_mode=='preserve'
   if b['uid'] in models:
    assert b['buildingCSUID']==models[b['uid']]['buildingCSUID'];b['modelGeometry']=models[b['uid']];model_seen.add(b['uid'])
   model=b.get('modelGeometry');top=model['worldBounds'][1][1] if model else b['base']+b['height'];bottom=model['worldBounds'][0][1] if model else b['base']
   outline_top=source['TopHeight'];display_t=display_terrain.extrema(p);whole=top<display_t['min']-.1;partial=top<display_t['max']-.1
   b['terrainAudit']={'roofWhollyBelowTerrain':whole,'roofPartlyBelowTerrain':partial,'baseWhollyAboveTerrain':bottom>display_t['max']+.5}
   reason='model/source-TIN or grid mismatch' if model else 'outline-revision versus terrain mismatch' if b['heightSource']=='landsd' else 'estimated missing elevation/height'
   if whole:counts['whollyBelow']+=1;counts['whollyBelow:'+reason]+=1
   if partial:counts['partlyBelow']+=1;counts['partlyBelow:'+reason]+=1
   counts['detailed' if model else 'outlineFallback']+=1
   rows.append({'uid':b['uid'],'name':b['name'],'modelId':model.get('modelId') if model else None,'sourceTile':model.get('sourceTile','10-SW-12C') if model else None,'sourceBaseHeight':source['BaseHeight'],'sourceTopHeight':outline_top,'renderBase':b['base'],'renderHeight':b['height'],'displayBottom':bottom,'displayTop':top,'terrain':display_t,'rawTerrain':t,'whollyBelow':whole,'partlyBelow':partial,'causeCategory':reason})
   assert b['rings']==old['rings'] and b['baseHeightHKPD']==old['baseHeightHKPD'] and b['topHeightHKPD']==old['topHeightHKPD']
   if b!=old:changed.append(b['uid'])
 assert model_seen==set(models),(len(model_seen),len(models))
 assert len(rows)==len(attrs)
 manifest['officialCoverage']['detailedModels']=sum('modelGeometry' in b for tile in tiles.values() for b in tile['buildings'])
 sources={m['file']:m for m in manifest.get('detailedModelSources',[])}
 sources.update({m['file']:{k:v for k,v in m.items() if k!='counts'} for m in payload['sourceManifests']});manifest['detailedModelSources']=list(sources.values())
 terrain_url=str(terrain_path.relative_to(ROOT/'3d-viewer'))
 patches={p['url']:p for p in manifest.get('terrainPatches',[])};patches[terrain_url]={'url':terrain_url,'resolution':5,'area':area,'source':read(terrain_path)['meta']['source']};manifest['terrainPatches']=list(patches.values())
 features=publish(tiles,manifest)
 if json.loads(previous_overview)==json.loads((OUT/'overview.json').read_bytes()):(OUT/'overview.json').write_bytes(previous_overview)
 assert manifest['counts']==before_counts,'Geometry-only publication must preserve territory forms and height classifications'
 report={'cityCounts':manifest['counts'],'officialCoverage':manifest['officialCoverage'],'changedForms':len(changed),'counts':dict(counts),'estimatedBasesRecomputed':revised_estimates,'matchedGeometryCount':len(model_seen),'sourcePayloadSha256':hashlib.sha256(payload_path.read_bytes()).hexdigest(),'terrainSha256':hashlib.sha256(terrain_path.read_bytes()).hexdigest(),'manifestSha256':hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest(),'rows':rows,'limits':['Source footprint and recorded base/top elevations are retained unchanged.','Source roof-model extrema are distinguished from outline BaseHeight/TopHeight.','Roof-versus-terrain tests compare the highest roof model elevation with terrain extrema across the official footprint; they are conservative conflict diagnostics, not per-roof-face occlusion measurements.','Only absent source elevations are re-estimated from the improved terrain; foundations remain illustrative.']}
 (doc/'integration.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('rows','estimatedBasesRecomputed')},indent=2))
 return report
def main():publish_models()
if __name__=='__main__':main()
