"""Attach verified geometry to current territory tiles, preserving every source form.
Does not re-run the old local-only OSM/official overlap merge.
"""
import collections,gzip,hashlib,importlib.util,json,pathlib,sys
from shapely.geometry import Polygon
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'3d-viewer/city/data';DOC=ROOT/'docs/astra-city/mui-wo-buildings/extension'
sys.path.insert(0,str(HERE.parent));from publish_tiles import publish,dump
spec=importlib.util.spec_from_file_location('fine_terrain_audit',HERE.parent/'mui-wo-buildings/fine_terrain_audit.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

def main():
 previous_overview=(OUT/'overview.json').read_bytes()
 manifest=json.loads((OUT/'manifest.json').read_text());before_counts=manifest['counts'];tiles={p.stem:json.loads(p.read_text()) for p in (OUT/'tiles').glob('*.json')}
 package=json.loads((OUT/'mui-wo-buildings.json').read_text());attrs={b['uid']:b['sourceAttributes'] for b in package['buildings']}
 payload=json.loads(gzip.decompress((HERE/'model-geometries.json.gz').read_bytes()));models=payload['byBuildingUid'];terrain=audit.FineTerrain(OUT/'terrain-mui-wo.json')
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
   if b['base']>t['min']+.5:b['foundationBase']=t['min'];b['foundationPolicy']='Illustrative foundation down to the DTM minimum; source base and roof unchanged'
   else:b.pop('foundationBase',None);b.pop('foundationPolicy',None)
   if b['uid'] in models:
    assert b['buildingCSUID']==models[b['uid']]['buildingCSUID'];b['modelGeometry']=models[b['uid']];model_seen.add(b['uid'])
   model=b.get('modelGeometry');top=model['worldBounds'][1][1] if model else b['base']+b['height'];bottom=model['worldBounds'][0][1] if model else b['base']
   outline_top=source['TopHeight'];whole=top<t['min']-.1;partial=top<t['max']-.1
   b['terrainAudit']={'roofWhollyBelowTerrain':whole,'roofPartlyBelowTerrain':partial,'baseWhollyAboveTerrain':bottom>t['max']+.5}
   reason='model/source-TIN or grid mismatch' if model else 'outline-revision versus terrain mismatch' if b['heightSource']=='landsd' else 'estimated missing elevation/height'
   if whole:counts['whollyBelow']+=1;counts['whollyBelow:'+reason]+=1
   if partial:counts['partlyBelow']+=1;counts['partlyBelow:'+reason]+=1
   counts['detailed' if model else 'outlineFallback']+=1
   rows.append({'uid':b['uid'],'name':b['name'],'modelId':model.get('modelId') if model else None,'sourceTile':model.get('sourceTile','10-SW-12C') if model else None,'sourceBaseHeight':source['BaseHeight'],'sourceTopHeight':outline_top,'renderBase':b['base'],'renderHeight':b['height'],'displayBottom':bottom,'displayTop':top,'terrain':t,'whollyBelow':whole,'partlyBelow':partial,'causeCategory':reason})
   assert b['rings']==old['rings'] and b['baseHeightHKPD']==old['baseHeightHKPD'] and b['topHeightHKPD']==old['topHeightHKPD']
   if b!=old:changed.append(b['uid'])
 assert model_seen==set(models),(len(model_seen),len(models))
 assert len(rows)==2408
 manifest['officialCoverage']['detailedModels']=sum('modelGeometry' in b for tile in tiles.values() for b in tile['buildings'])
 manifest['detailedModelSources']=[{k:v for k,v in m.items() if k!='counts'} for m in payload['sourceManifests']]
 features=publish(tiles,manifest)
 if json.loads(previous_overview)==json.loads((OUT/'overview.json').read_bytes()):(OUT/'overview.json').write_bytes(previous_overview)
 assert manifest['counts']==before_counts,'Geometry-only publication must preserve territory forms and height classifications'
 report={'cityCounts':manifest['counts'],'officialCoverage':manifest['officialCoverage'],'changedForms':len(changed),'counts':dict(counts),'estimatedBasesRecomputed':revised_estimates,'matchedGeometryCount':len(model_seen),'sourcePayloadSha256':hashlib.sha256((HERE/'model-geometries.json.gz').read_bytes()).hexdigest(),'terrainSha256':hashlib.sha256((OUT/'terrain-mui-wo.json').read_bytes()).hexdigest(),'manifestSha256':hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest(),'rows':rows,'limits':['Source footprint and recorded base/top elevations are retained unchanged.','Source roof-model extrema are distinguished from outline BaseHeight/TopHeight.','Roof-versus-terrain tests compare the highest roof model elevation with terrain extrema across the official footprint; they are conservative conflict diagnostics, not per-roof-face occlusion measurements.','Only absent source elevations are re-estimated from the improved terrain; foundations remain illustrative.']}
 (DOC/'integration.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('rows','estimatedBasesRecomputed')},indent=2))
if __name__=='__main__':main()
