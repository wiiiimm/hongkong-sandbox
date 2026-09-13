"""Stage source/terrain diagnostics using the existing exact footprint/grid audit."""
import collections,gzip,hashlib,json,math,pathlib,sys
import numpy as np
from shapely.geometry import Polygon,box
from shapely.strtree import STRtree
from run import HERE,ROOT,DOC,CONFIG,module
sys.path.insert(0,str(HERE.parent/'mui-wo-models'))
a=module('shared_fine_audit',HERE.parent/'mui-wo-buildings/fine_terrain_audit.py')
grid_sample=module('existing_source_grid_sample',HERE.parent/'mui-wo-completion/audit_existing.py').grid_sample
def load(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def main():
 package=load(HERE/'building-selection.json.gz');models=load(HERE/'model-geometries.json.gz')['byBuildingUid'];terrain=a.FineTerrain(HERE/CONFIG['terrainOutput']);display=a.FineTerrain(terrain.path,rendered=True);baseline=a.FineTerrain(ROOT/'3d-viewer/city/data/terrain.json',rendered=True)
 grids=[(str(p.relative_to(ROOT)),load(p)) for p in sorted((HERE/'staged').glob('*/terrain-source-5m.json'))]
 rows=[];counts=collections.Counter();triangles=collections.Counter();tileBytes=collections.Counter();heightDifferences=[]
 for b in package['buildings']:
  p=Polygon(b['rings'][0],b['rings'][1:]);raw=terrain.extrema(p);ground=display.extrema(p);old=baseline.extrema(p);attrs=b['sourceAttributes'];values=a.m.render_elevations(attrs,raw);model=models.get(b['uid']);top=model['worldBounds'][1][1] if model else values['renderTopHeight'];previousTop=b['base']+b['height'];whole=top<ground['min']-.1;partial=top<ground['max']-.1
  if attrs['BaseHeight'] is not None:assert values['base']==b['base']
  changed=values['base']!=b['base'];assert not changed or attrs['BaseHeight'] is None and attrs['TopHeight'] is None
  coverage=[{'file':path,'height':v} for path,data in grids if (v:=grid_sample(data,p.centroid.x,p.centroid.y)) is not None]
  cause='selection buffer outside current source TIN; archival DTM' if not coverage else 'detailed-source-model versus grid' if model else 'recorded-outline versus terrain revision' if attrs['TopHeight'] is not None else 'estimated absent source elevation'
  row={'uid':b['uid'],'sourceBaseHeight':attrs['BaseHeight'],'sourceTopHeight':attrs['TopHeight'],'modelId':model['modelId'] if model else None,'sourceTile':model['sourceTile'] if model else None,'proposedBase':values['base'],'previousBase':b['base'],'baseEstimateChanged':changed,'renderTop':top,'previousTop':previousTop,'baselineTerrain':old,'rawTerrain':raw,'renderedTerrain':ground,'previousWhole':previousTop<old['min']-.1,'previousPartial':previousTop<old['max']-.1,'whollyBelow':whole,'partlyBelow':partial,'fixedOutlineWhole':previousTop<ground['min']-.1,'fixedOutlinePartial':previousTop<ground['max']-.1,'cause':cause,'sourceTINAtCentre':coverage,'proposedHeightFields':values}
  rows.append(row)
  for key,flag in [('forms',True),('models',bool(model)),('sourceTINCovered',bool(coverage)),('previousWhole',row['previousWhole']),('previousPartial',row['previousPartial']),('whollyBelow',whole),('partlyBelow',partial),('baseEstimatesChanged',changed),('fixedOutlineWhole',row['fixedOutlineWhole']),('fixedOutlinePartial',row['fixedOutlinePartial'])]:counts[key]+=flag
  if partial:counts['partial:'+cause]+=1
  if model:triangles[b['tile']]+=model['triangles'];tileBytes[b['tile']]+=len(json.dumps(model,separators=(',',':')).encode())
 sourceBuild=load(DOC/'build.json');polygons=[Polygon(b['rings'][0],b['rings'][1:]) for b in package['buildings']];tree=STRtree(polygons);unmatched=[]
 for r in sourceBuild['unmatched']:
  aa,bb=r['worldBounds'];shape=box(aa[0],aa[2],bb[0],bb[2]);near=[]
  for i in tree.query(shape.buffer(15)):
   b=package['buildings'][int(i)];poly=polygons[int(i)];near.append({'uid':b['uid'],'geoRefNo':b['sourceAttributes'].get('GeoRefNo'),'sameGeoRefNo':str(b['sourceAttributes'].get('GeoRefNo'))==r['geoRefNo'],'bboxOverlapM2':shape.intersection(poly).area,'centroidDistanceM':shape.centroid.distance(poly.centroid)})
  unmatched.append({**r,'nearbyCandidates':sorted(near,key=lambda x:x['centroidDistanceM'])[:6],'policy':'Diagnostic bounding-box neighbours only; no replacement identity is inferred.'})
 raw=terrain.path.read_bytes();values=load(terrain.path);downloads=[load(HERE/'sources'/t/'download.json') for t in CONFIG['tiles']]
 report={'schemaVersion':1,'staged':True,'sectionId':'10.7','scope':CONFIG['scope'],'counts':dict(counts),'terrain':{'file':str(terrain.path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'width':values['w'],'height':values['h'],'cellMetres':5,'nonPositiveVertices':sum(v<=0 for v in values['elev']),'renderedTransitionVertices':sum(v is not None for v in values.get('renderedElev',[]))},'modelBudget':{'compressedBytes':(HERE/'model-geometries.json.gz').stat().st_size,'uncompressedBytes':sourceBuild['uncompressedBytes'],'triangles':sum(triangles.values()),'trianglesByCityTile':dict(triangles),'embeddedJSONBytesByCityTile':dict(tileBytes),'largestModelTriangles':max(m['triangles'] for m in models.values()),'policy':'Exact source triangles. Village-scale draw geometry is modest; JSON transfer should be compressed. No new runtime loader was built.'},'acquisition':{'sourceArchiveBytes':sum(d['sourceArchiveBytes'] for d in downloads),'transferredBytes':sum(d['transferredBytes'] for d in downloads),'cacheBytes':sum(d['bytes'] for d in downloads)},'unmatched':unmatched,'rows':rows,'limits':['Footprint/highest-roof versus terrain extrema is a conservative diagnostic, not per-face occlusion proof.','Recorded government geometry, identities and elevation attributes remain unchanged; source model roof extrema are distinct from approximate outline fields.','Only both-missing source elevation estimates may follow the staged terrain; their updates remain labelled estimates.','Wetland hydrology, tide level and current shoreline geometry are not inferred from building models or flattened from the DTM. Source TINs inherit the established non-positive DTM water-mask preservation policy.','No live tiles, manifest, arrivals or terrain were published.']}
 (DOC/'terrain-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('rows','unmatched')},indent=2))
if __name__=='__main__':main()
