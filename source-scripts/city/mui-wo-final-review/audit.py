"""Audit only the 13 retained Mui Wo roof flags against original TIN triangles.
No live source/building/terrain mutation. Existing decoder/projection is reused.
"""
import collections,hashlib,importlib.util,json,math,pathlib,sys
import numpy as np
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/mui-wo-final-review';OUT=ROOT/'3d-viewer/city/data'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from resample_model_terrain import terrain_index
spec=importlib.util.spec_from_file_location('shared_fine_audit',HERE.parent/'mui-wo-buildings/fine_terrain_audit.py');fine=importlib.util.module_from_spec(spec);spec.loader.exec_module(fine)
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def polygons(g):
 if isinstance(g,Polygon):return [g] if not g.is_empty else []
 return [p for child in getattr(g,'geoms',[]) for p in polygons(child)]
def plane_values(tri,points):
 a,b,c=tri;uv=np.linalg.solve(np.array([[b[0]-a[0],c[0]-a[0]],[b[2]-a[2],c[2]-a[2]]]),(np.asarray(points)-a[[0,2]]).T)
 return a[1]+uv[0]*(b[1]-a[1])+uv[1]*(c[1]-a[1])
def above(poly,tri,top):
 # Clip a convex triangle-intersection piece against its linear height plane.
 coords=list(poly.exterior.coords)[:-1];heights=plane_values(tri,coords);result=[]
 for i,p in enumerate(coords):
  q=coords[(i+1)%len(coords)];a=heights[i]-top;b=heights[(i+1)%len(coords)]-top
  if a>=0:result.append(p)
  if (a>=0)!=(b>=0):t=a/(a-b);result.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
 return Polygon(result) if len(result)>=3 else Polygon()
def source_piece_audit(poly,top,item):
 usable,tree=item;points=[];exceeded=[];coverage=[];candidates=tree.query(poly,predicate='intersects')
 for i in candidates:
  tri=usable[i]
  for clip in polygons(tree.geometries[i].intersection(poly)):
   if clip.area<1e-10:continue
   coverage.append(clip);coords=list(clip.exterior.coords);heights=plane_values(tri,coords)
   points.extend(([float(x),float(y)],float(h)) for (x,y),h in zip(coords,heights))
   # Clip the convex source triangle first, then intersect the real footprint;
   # this retains disconnected pieces and courtyard holes without bridging them.
   high=clip.intersection(above(tree.geometries[i],tri,top+.1))
   if not high.is_empty:exceeded.append(high)
 centre=poly.centroid;centre_h=[]
 for i in tree.query(centre,predicate='covered_by'):centre_h.extend(plane_values(usable[i],[[centre.x,centre.y]]))
 return {'intersectingTriangles':len(candidates),'coverageArea':unary_union(coverage).area if coverage else 0,'minimum':min((h for p,h in points),default=None),'maximum':max((h for p,h in points),default=None),'maximumPoint':max(points,key=lambda row:row[1])[0] if points else None,'centre':float(max(centre_h)) if centre_h else None,'areaAboveHighestRoofPlusTolerance':unary_union(exceeded).area if exceeded else 0},coverage,exceeded

def main():
 previous=load(ROOT/'docs/astra-city/mui-wo-completion/terrain-audit.json');flags=[r for r in previous['rows'] if r['partlyBelow']];assert len(flags)==13
 package=load(OUT/'mui-wo-buildings.json');original={b['uid']:b for b in package['buildings']};uids={r['uid'] for r in flags};wanted={original[u]['tile'] for u in uids};live={b['uid']:b for t in wanted for b in load(OUT/'tiles'/(t+'.json'))['buildings'] if b['uid'] in uids};assert set(live)==uids
 patch=load(OUT/'terrain-mui-wo.json');terrain=fine.FineTerrain(OUT/'terrain-mui-wo.json',rendered=True);g=patch['meta']['georef'];values=np.full((patch['h'],patch['w']),np.nan);owners={}
 for row in patch['meta']['detailSources']:
  path=ROOT/row['file'];d=load(path);dg=d['meta']['georef'];c=round((dg['bE']-g['bE'])/5);r=round((g['bN']-dg['bN'])/5);a=np.asarray([v if v is not None else np.nan for v in d['elev']]).reshape(d['h'],d['w']);dest=values[r:r+d['h'],c:c+d['w']];valid=np.isfinite(a);assert not np.any(np.isfinite(dest)&valid);dest[valid]=a[valid]
 valid=np.isfinite(values)&(np.asarray(patch['elev']).reshape(values.shape)>0);interior=valid.copy();weight=np.zeros(values.shape)
 for _ in range(3):
  padded=np.pad(interior,1,constant_values=False);interior&=padded[:-2,1:-1]&padded[2:,1:-1]&padded[1:-1,:-2]&padded[1:-1,2:];weight+=interior/3
 records={}
 for flag in flags:
  uid=flag['uid'];b=live[uid];p=Polygon(b['rings'][0],b['rings'][1:]);t=terrain.extrema(p);top=b['modelGeometry']['worldBounds'][1][1] if b.get('modelGeometry') else b['base']+b['height'];c=(p.centroid.x+834500-g['bE'])/5;r=(816500-p.centroid.y-g['bN'])/-5
  nodes=[]
  for rr in [math.floor(r),math.floor(r)+1]:
   for cc in [math.floor(c),math.floor(c)+1]:nodes.append({'world':[g['bE']+cc*5-834500,816500-g['bN']+rr*5],'current':patch['elev'][rr*patch['w']+cc],'source':float(values[rr,cc]) if np.isfinite(values[rr,cc]) else None,'sourceWeight':float(weight[rr,cc])})
  records[uid]={'uid':uid,'name':b['name'],'centre':b['centre'],'footprintArea':p.area,'rings':b['rings'],'modelId':b.get('modelGeometry',{}).get('modelId'),'structureType':b['structureType'],'sourceAttributes':original[uid]['sourceAttributes'],'renderBase':b['base'],'highestRenderRoof':top,'currentTerrain':t,'currentPartial':top<t['max']-.1,'previousCase':flag,'interpolationNodes':nodes,'sources':[],'_polygon':p,'_coverage':[],'_exceeded':[]}
 folders=[ROOT/'docs/astra-city/mui-wo-buildings/review/model-sample',*sorted((HERE.parent/'mui-wo-models/staged').iterdir()),*sorted((HERE.parent/'mui-wo-completion/staged').iterdir())]
 provenance=[]
 for folder in folders:
  mf=folder/'manifest.json'
  if not mf.exists():continue
  manifest=load(mf);bounds=manifest['terrain']['worldBounds'];extent=box(bounds[0][0],bounds[0][2],bounds[1][0],bounds[1][2]);relevant=[r for r in records.values() if extent.intersects(r['_polygon'])]
  if not relevant:continue
  print('Reading',manifest['tile'],len(relevant),'cases',flush=True)
  m,s,triangles,valid,usable,tree=terrain_index(folder);provenance.append({'manifest':str(mf.relative_to(ROOT)),'manifestSha256':sha(mf),'tile':m['tile'],'revision':m['tileRevision'],'source':s['sourceEntry'],'sourceHashes':s['sourceHashes']})
  for r in relevant:
   metrics,coverage,exceeded=source_piece_audit(r['_polygon'],r['highestRenderRoof'],(usable,tree));r['sources'].append({'tile':m['tile'],'revision':m['tileRevision'],**metrics});r['_coverage'].extend(coverage);r['_exceeded'].extend(exceeded)
  del tree,triangles,usable
 for r in records.values():
  p=r.pop('_polygon');r['sourceCoveredArea']=unary_union(r.pop('_coverage')).area;r['nativeTerrainAboveHighestRoofArea']=unary_union(r.pop('_exceeded')).area;r['sourceCoveredFraction']=r['sourceCoveredArea']/p.area
  r['sourceMaximum']=max((s['maximum'] for s in r['sources'] if s['maximum'] is not None),default=None)
 report={'schemaVersion':1,'scope':'Exactly the 13 documented partial roof flags from HKS-192. No source heights or live data changed.','inputs':[{'file':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [OUT/'terrain-mui-wo.json',OUT/'mui-wo-buildings.json',ROOT/'docs/astra-city/mui-wo-completion/terrain-audit.json']],'sourceTINs':provenance,'cases':list(records.values()),'counts':{'cases':13,'currentPartial':sum(r['currentPartial'] for r in records.values()),'nativeHighestRoofPartial':sum(r['nativeTerrainAboveHighestRoofArea']>1e-6 for r in records.values())},'limitations':['Highest roof over the source outline is a conservative screen. Detailed per-roof-face occlusion remains pending; this screen does not certify every roof face.','Native terrain/outline revisions may differ; a source contradiction is not authority to raise a recorded roof.','Source footprint detail and model terrain are visualisation data, not surveyed bathymetry or finished architecture.']}
 DOC.mkdir(parents=True,exist_ok=True);(DOC/'exact-source-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['counts']))
 for r in records.values():print(r['uid'],'roof',round(r['highestRenderRoof'],3),'gridmax',r['currentTerrain']['max'],'TINmax',round(r['sourceMaximum'],3) if r['sourceMaximum'] is not None else None,'highArea',round(r['nativeTerrainAboveHighestRoofArea'],3),'coverage',round(r['sourceCoveredFraction'],4))
if __name__=='__main__':main()
