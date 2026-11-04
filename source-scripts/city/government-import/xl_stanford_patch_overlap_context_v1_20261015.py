"""Capture unchanged validator failures and compare original/repaired patch overlaps."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stanford-patch-overlap-context-v1-20261015';DOC=BASE/BATCH
MODEL='B365201779201063C0'
def context(t,bounds):
 polys=shapely.polygons(t[:,:,[0,2]]);ids=np.flatnonzero(shapely.area(polys)>1e-10);p=polys[ids];tree=shapely.STRtree(p);left,right=tree.query(p,predicate='intersects');rows=[]
 for a,b in zip(left,right):
  if a>=b:continue
  overlap=p[a].intersection(p[b])
  if overlap.area<=1e-10:continue
  rows.append({'faces':[int(ids[a]),int(ids[b])],'areaM2':float(overlap.area),'bounds':list(overlap.bounds)})
 union=shapely.union_all(p)
 return {'triangles':len(t),'positiveAreaPairs':len(rows),'pairs':rows,'projectedExcessM2':float(shapely.area(p).sum()-union.area),'rectangleDifferenceM2':float(union.symmetric_difference(shapely.box(*bounds)).area)}
def main():
 assert not DOC.exists();DOC.mkdir();prev=BASE/'government-xl-unmapped-source-floor-candidate-v1-20261015';receipt=read(prev/'result.json');refs=[Path(__file__),prev/'result.json']
 for q in receipt['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p)
 data=read(prev/(MODEL+'-private-terrain.json.gz'));probe=read(BASE/'government-xl-unmapped-floor-patch-probe-v1-20261015/probe.json')['rows'][1];resolution=module('stanford_patch_overlap',HERE/'resolve-pass.py');refs.append(HERE/'resolve-pass.py');parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);refs.append(parentpath);validator=resolution.validate_patch;results=[]
 recovery=read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows'];source=next(r for r in recovery if r['modelId']==MODEL)
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 asset=ROOT/source['asset']['path'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());lo,hi=tri.min((0,1)),tri.max((0,1));bounds=probe['bounds']
 for mode,key in [('original','allOriginalTerrainTriplets'),('repaired','allCandidateTerrainTriplets')]:
  native=np.asarray(data[key]);mask=(native[:,:,0].max(1)>=bounds[0])&(native[:,:,0].min(1)<=bounds[2])&(native[:,:,2].max(1)>=bounds[1])&(native[:,:,2].min(1)<=bounds[3]);native=native[mask];captured=[]
  def capture(candidate,parent):
   captured.append(candidate)
   validator(candidate,parent)
  resolution.validate_patch=capture
  try:
   resolution.make_patch({'uids':probe['uids'],'cells':probe['cells']},parent,native,[{'privateDiagnostic':mode}],native_core=[lo[0]-1,lo[2]-1,hi[0]+1,hi[2]+1],terrain_triangle_budget=100000);error=None
  except (AssertionError,ValueError)as e:error=str(e)
  finally:resolution.validate_patch=validator
  assert len(captured)==1;patch=captured[0];save(DOC/(mode+'-unapproved-patch.json.gz'),patch);m=patch['nativeMesh'];indices=np.asarray(m['index']).reshape(-1,3);literal=np.asarray(m['position']).reshape(-1,3)[indices];packed=literal.astype('<f4').astype(float)
  c={'mode':mode,'validatorError':error,'literal':context(literal,bounds),'float32':context(packed,bounds)};results.append(c);print({'mode':mode,'error':error,**{k:{a:b for a,b in c[k].items()if a!='pairs'}for k in ['literal','float32']}},flush=True)
 save(DOC/'overlap-context.json',{'rows':results,'sourceGeometryChanges':0,'publication':False,'qualification':'Patch capture invokes the unchanged validator and retains its rejection. No approval flags are added.'})
 module('freeze_stanford_overlap',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-vs-repaired-patch-overlap-attribution-v1',refs,{'uids':probe['uids'],'modelId':MODEL,'validatorErrors':[r['validatorError']for r in results],'fullAcceptance':False})
if __name__=='__main__':main()
