"""Exact top-envelope/terrain intersections and all-vertex placement diagnostics.
Reuse native source baking, terrain elevation policy and source-TIN audit helpers.
No live data changes. Terrain under model bases is measured, never fitted to them.
"""
import collections, importlib.util, math, sys
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely.strtree import STRtree
from run import HERE,ROOT,DOC,load,dump,sha,existing_folders
sys.path.insert(0,str(HERE.parent/'mui-wo-final-review'))
from audit import fine,plane_values,polygons,source_piece_audit,terrain_index
from bake_model_geometry import bake

def clipped_plane(poly,values,threshold):
 coords=list(poly.exterior.coords)[:-1];out=[]
 for i,p in enumerate(coords):
  q=coords[(i+1)%len(coords)];a=values[i]-threshold;b=values[(i+1)%len(coords)]-threshold
  if a>=0:out.append(p)
  if (a>=0)!=(b>=0):t=a/(a-b);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
 return Polygon(out) if len(out)>=3 else Polygon()

def projected(triangles):
 valid=[];shapes=[]
 for tri in triangles:
  shape=Polygon(tri[:,[0,2]])
  if shape.area>1e-8:valid.append(tri);shapes.append(shape)
 return np.asarray(valid),shapes

def upper_envelope(triangles):
 tris,shapes=projected(triangles);tree=STRtree(shapes);visible=[]
 for i,(tri,shape) in enumerate(zip(tris,shapes)):
  result=shape
  for j in tree.query(shape,predicate='intersects'):
   if i==j:continue
   overlap=shape.intersection(shapes[j])
   if overlap.area<1e-9:continue
   for part in polygons(overlap):
    coords=list(part.exterior.coords)[:-1];delta=plane_values(tris[j],coords)-plane_values(tri,coords)
    # Coplanar duplicates belong only to the earliest source triangle.
    if max(abs(delta))<1e-5:
     if j<i:result=result.difference(part)
    elif max(delta)>1e-5:result=result.difference(clipped_plane(part,delta,1e-5))
   if result.is_empty:break
  if result.area>1e-9:visible.append((tri,result))
 return visible

def grid_triangles(sampler,area):
 g=sampler.g;x0,z0,x1,z1=area.bounds
 c0,c1=sorted([(x+834500-g['bE'])/g['aE'] for x in [x0,x1]]);r0,r1=sorted([(816500-z-g['bN'])/g['aN'] for z in [z0,z1]])
 tris=[]
 for r in range(max(0,math.floor(r0)),min(sampler.dem['h']-1,math.ceil(r1))):
  for c in range(max(0,math.floor(c0)),min(sampler.w-1,math.ceil(c1))):
   points=[]
   for cc,rr in [(c,r),(c+1,r),(c,r+1),(c+1,r+1)]:
    x=g['aE']*cc+g['bE']-834500;z=816500-g['aN']*rr-g['bN'];points.append([x,sampler.ground(x,z),z])
   tris.extend([[points[0],points[1],points[2]],[points[1],points[3],points[2]]])
 return np.asarray(tris)

def surface_contacts(envelope,terrain):
 tris,shapes=projected(terrain);tree=STRtree(shapes);totalArea=0;coveredArea=0;high=[];maximum=-math.inf;minimum=math.inf
 for roof,area in envelope:
  totalArea+=area.area
  for i in tree.query(area,predicate='intersects'):
   for clip in polygons(area.intersection(shapes[i])):
    if clip.area<1e-9:continue
    coveredArea+=clip.area;coords=list(clip.exterior.coords)[:-1];delta=plane_values(tris[i],coords)-plane_values(roof,coords);maximum=max(maximum,float(max(delta)));minimum=min(minimum,float(min(delta)))
    # Clip a convex terrain triangle by the linear terrain/roof plane difference.
    triCoords=list(shapes[i].exterior.coords)[:-1];triDelta=plane_values(tris[i],triCoords)-plane_values(roof,triCoords)
    high.append(clip.intersection(clipped_plane(shapes[i],triDelta,.1)))
 return {'topEnvelopeArea':totalArea,'coveredArea':coveredArea,'terrainAboveRoofArea':unary_union(high).area if high else 0,'maximumTerrainMinusRoof':maximum if math.isfinite(maximum) else None,'minimumTerrainMinusRoof':minimum if math.isfinite(minimum) else None}

def main():
 parentPath=ROOT/'3d-viewer/city/data/terrain-mui-wo.json';parentSha=sha(parentPath.read_bytes());parent=load(parentPath);terrain=fine.DemSampler(parent,rendered=True)
 catalogue=load(HERE/'compact/catalogue.json');sourceEvidence={r['uid']:r for r in load(DOC/'compact-assets.json')['assets']};baseline={b['uid']:b for b in load(ROOT/'3d-viewer/city/data/mui-wo-buildings.json')['buildings']};rows=[];geometry={}
 for n,entry in enumerate(catalogue['models']):
  uid=entry['uid'];b=baseline[uid];e=sourceEvidence[uid];file=ROOT/e['sourceEntry'];folder=file.parents[2];m=load(folder/'manifest.json');spec=next(s for s in m['models'] if s['id']==entry['modelId']);positions=np.asarray(bake(spec,folder)['position']).reshape(-1,3);triangles=positions.reshape(-1,3,3);envelope=upper_envelope(triangles);roofEnvelope=[(t,p) for t,p in envelope if abs(np.cross(t[1]-t[0],t[2]-t[0])[1])/np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))>=.25];hull=unary_union([p for _,p in envelope]);footprint=Polygon(b['rings'][0],b['rings'][1:]);area=hull.union(footprint);ground=grid_triangles(terrain,area);contact=surface_contacts(roofEnvelope,ground);fullContact=surface_contacts(envelope,ground);ft=terrain.extrema(footprint)
  verts=np.unique(positions,axis=0);clearance=np.array([v[1]-terrain.ground(v[0],v[2]) for v in verts]);base=entry['worldBounds'][0][1];baseVertices=verts[verts[:,1]<=base+.1];baseClearance=[v[1]-terrain.ground(v[0],v[2]) for v in baseVertices]
  row={'uid':uid,'modelId':entry['modelId'],'sourceTile':entry['sourceTile'],'worldBounds':entry['worldBounds'],'footprintTerrain':ft,'meshVertices':len(verts),'meshVertexClearance':{'min':float(min(clearance)),'max':float(max(clearance)),'belowTerrain':int((clearance<-.1).sum())},'minimumBaseVertices':len(baseVertices),'baseVertexClearance':{'min':float(min(baseClearance)),'max':float(max(baseClearance))},'highestRoofBelowFootprintMaximum':entry['worldBounds'][1][1]<ft['max']-.1,'minimumBaseAboveWholeFootprint':base>ft['max']+.5,'surface':contact,'fullProjectedSurfaceIncludingSteepWalls':fullContact}
  row['requiresReview']=contact['terrainAboveRoofArea']>1e-5 or row['minimumBaseAboveWholeFootprint'] or contact['coveredArea']<contact['topEnvelopeArea']-.01
  rows.append(row);geometry[uid]={'envelope':roofEnvelope,'footprint':footprint,'extent':area}
  if n%50==0:print(n,uid,row['requiresReview'],flush=True)
 # Load each source TIN only once, and only for flagged buildings.
 flagged=[r for r in rows if r['requiresReview']];native=collections.defaultdict(list)
 folders={load(p/'manifest.json')['tile']:p for p in existing_folders()};folders.update({p.name:p for p in (HERE/'staged').iterdir()})
 for tile,folder in folders.items():
  m=load(folder/'manifest.json');bounds=m['terrain']['worldBounds'];extent=box(bounds[0][0],bounds[0][2],bounds[1][0],bounds[1][2]);targets=[r for r in flagged if geometry[r['uid']]['extent'].intersects(extent)]
  if not targets:continue
  print('Source TIN',tile,len(targets),flush=True);_,_,_,_,usable,tree=terrain_index(folder)
  for row in targets:
   geo=geometry[row['uid']];ids=tree.query(geo['extent'],predicate='intersects');contacts=surface_contacts(geo['envelope'],usable[ids]);metrics,_,_=source_piece_audit(geo['footprint'],row['worldBounds'][1][1],(usable,tree));native[row['uid']].append({'tile':tile,'revision':m['tileRevision'],'footprint':metrics,'surface':contacts})
 for r in rows:r['nativeSourceChecks']=native[r['uid']]
 assert sha(parentPath.read_bytes())==parentSha,'Terrain changed during audit; rerun'
 report={'parentTerrain':'city/data/terrain-mui-wo.json','parentSha256':parentSha,'models':len(rows),'requiresReview':sum(r['requiresReview'] for r in rows),'safeOnCurrentTerrain':[r['uid'] for r in rows if not r['requiresReview']],'rows':rows,'method':'Exact source upper surface envelope (occluded lower faces removed) intersected with all current rendered 5m terrain triangles. Roofing surfaces have absolute vertical normal component >=0.25 (up to75.5degree inclination); steep wall skins are still measured in the separate complete projected surface and every unique vertex, not mistaken for buried roofs. Every unique source mesh vertex and minimum-base vertex is measured separately. Full unchanged footprint extrema checked. Roof tolerance 0.1m, entire floating footprint tolerance0.5m. Source mesh elevations unchanged.'}
 dump(DOC/'placement-audit.json',report);print({k:v for k,v in report.items() if k not in ('rows','safeOnCurrentTerrain')});print('flagged',[(r['uid'],r['surface']['maximumTerrainMinusRoof'],r['minimumBaseAboveWholeFootprint']) for r in flagged])
if __name__=='__main__':main()
