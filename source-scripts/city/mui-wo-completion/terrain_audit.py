"""Evaluate a staged patch without modifying source heights or live city tiles."""
import collections,hashlib,importlib.util,json,pathlib,sys
from shapely.geometry import Polygon
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/mui-wo-completion';OUT=ROOT/'3d-viewer/city/data'
sys.path.insert(0,str(HERE));from audit_existing import load,grid_sample
spec=importlib.util.spec_from_file_location('fine_audit',HERE.parent/'mui-wo-buildings/fine_terrain_audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
def main():
 package=load(OUT/'mui-wo-buildings.json');byuid={b['uid']:b for b in package['buildings']};tileids={b['tile'] for b in byuid.values()};live={b['uid']:b for tileid in tileids for b in load(OUT/'tiles'/(tileid+'.json'))['buildings'] if b['uid'] in byuid}
 old={b['uid']:b for b in load(ROOT/'docs/astra-city/mui-wo-buildings/extension/integration.json')['rows']};terrain=a.FineTerrain(HERE/'staged-terrain-mui-wo.json');display=a.FineTerrain(terrain.path,rendered=True)
 grids=[(str(p.relative_to(ROOT)),load(p)) for p in [ROOT/'docs/astra-city/mui-wo-buildings/review/model-sample/terrain-source-5m.json',*sorted((HERE.parent/'mui-wo-models/staged').glob('*/terrain-source-5m.json')),*sorted((HERE/'staged').glob('*/terrain-source-5m.json'))]]
 counts=collections.Counter();rows=[]
 for i,(uid,b) in enumerate(sorted(live.items())):
  p=Polygon(b['rings'][0],b['rings'][1:]);t=terrain.extrema(p);dt=display.extrema(p);source=byuid[uid]['sourceAttributes'];values=a.m.render_elevations(source,t);model=b.get('modelGeometry');top=model['worldBounds'][1][1] if model else values['renderTopHeight'];fixedtop=model['worldBounds'][1][1] if model else b['base']+b['height'];whole=top<dt['min']-.1;partial=top<dt['max']-.1;prior=old[uid]
  samples=[{'path':path,'height':v} for path,g in grids if (v:=grid_sample(g,p.centroid.x,p.centroid.y)) is not None]
  reason='detailed-source-model' if model else 'source-roof-elevation' if source['TopHeight'] is not None else 'estimated-roof'
  row={'uid':uid,'name':b['name'],'locality':byuid[uid]['locality'],'sourceTop':source['TopHeight'],'sourceBase':source['BaseHeight'],'modelId':model['modelId'] if model else None,'previousWhole':prior['whollyBelow'],'previousPartial':prior['partlyBelow'],'whollyBelow':whole,'partlyBelow':partial,'cause':reason,'renderTop':top,'fixedPreviousTop':fixedtop,'fixedTopWhollyBelow':fixedtop<dt['min']-.1,'fixedTopPartlyBelow':fixedtop<dt['max']-.1,'terrain':dt,'previousTerrain':prior['terrain'],'sourceTINAtCentre':samples,'previousBase':b['base'],'proposedBase':values['base'],'missingBaseReestimated':values['base']!=b['base']}
  if row['missingBaseReestimated']:assert source['BaseHeight'] is None and source['TopHeight'] is None
  if source['BaseHeight'] is not None:assert values['base']==b['base']
  rows.append(row);counts['forms']+=1;counts['models']+=bool(model);counts['whollyBelow']+=whole;counts['partlyBelow']+=partial;counts['fixedTopWhole']+=row['fixedTopWhollyBelow'];counts['fixedTopPartial']+=row['fixedTopPartlyBelow'];counts['sourceTINCovered']+=bool(samples);counts['estimatedBasesChanged']+=row['missingBaseReestimated']
  if whole:counts['whole:'+reason]+=1
  if partial:counts['partial:'+reason]+=1
  counts['wholeResolved']+=prior['whollyBelow'] and not whole;counts['partialResolved']+=prior['partlyBelow'] and not partial;counts['newWhole']+=whole and not prior['whollyBelow'];counts['newPartial']+=partial and not prior['partlyBelow']
  if i%300==0:print(i,flush=True)
 report={'schemaVersion':1,'published':False,'counts':dict(counts),'baseline':{'whollyBelow':114,'partlyBelow':214,'models':1327},'terrainSha256':hashlib.sha256(terrain.path.read_bytes()).hexdigest(),'terrainBytes':terrain.path.stat().st_size,'policy':'Exact footprint intersections with rendered terrain triangles; 0.1 m roof tolerance. Recorded elevations and model triangles unchanged. Only both-missing source base/top estimates are proposed to follow improved terrain. Fixed-previous-top counts also reported separately.','rows':rows}
 (DOC/'terrain-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
