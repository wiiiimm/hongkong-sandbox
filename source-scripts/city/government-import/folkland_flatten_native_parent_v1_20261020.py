"""Private complete parent replacement retaining all disjoint original facets."""
from pathlib import Path
import copy,uuid
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
import native_patch_resolution as repair
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-folkland-flatten-native-parent-v1-20261020';DOC=BASE/BATCH
SRC=BASE/'government-xl-folkland-native-parent-candidate-v1-20261020'
def main():
 assert not DOC.exists();receipt=read(SRC/'result.json');pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']};refs=[Path(__file__),SRC/'result.json']
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 def consume(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 local=consume(SRC/'unapproved-local-surface.json');summary=consume(SRC/'summary.json');parentpath=ROOT/'3d-viewer'/local['meta']['parentTerrain'];parent=consume(parentpath)
 bb=summary['replacementBounds'];region=shapely.box(*bb);old=repair._faces(parent);new=repair._faces(local)
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['private-terrain-proposal:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();polys=shapely.polygons(old[:,:,[0,2]]);hits=set(map(int,shapely.STRtree(polys).query(region,predicate='intersects')));out=[];unchanged=0;cut=0;removed=0;vertical=[]
  for i,face in enumerate(old):
   if i not in hits or polys[i].intersection(region).area<=1e-10:
    out.append(face);unchanged+=1
    if i in hits and polys[i].area<=1e-10:vertical.append(i)
    continue
   rest=polys[i].difference(region)
   if rest.is_empty:removed+=1;continue
   normal=np.cross(face[1]-face[0],face[2]-face[0]);assert abs(normal[1])>1e-10;cut+=1
   for part in shapely.get_parts(rest):
    if part.geom_type!='Polygon':continue
    for triangle in repair._triangles(part):
     coords=np.asarray(triangle.exterior.coords)[:3];heights=face[0,1]-(normal[0]*(coords[:,0]-face[0,0])+normal[2]*(coords[:,1]-face[0,2]))/normal[1];out.append(np.column_stack([coords[:,0],heights,coords[:,1]]))
  out.extend(new);tri=np.asarray(out);patch=copy.deepcopy(parent);patch['id']='folkland-parent-private-v1-20261020';patch['nativeMesh']['position']=tri.reshape(-1).tolist();patch['nativeMesh']['index']=list(range(len(tri)*3));patch['nativeMesh'].pop('sourceOverlap',None)
  patch['nativeMesh']['source']['folklandLocalReplacement']={'bounds':bb,'priorParentSHA256':digest(parentpath.read_bytes()),'localSurfaceSHA256':digest((SRC/'unapproved-local-surface.json').read_bytes()),'policy':'Disjoint parent faces retained verbatim at runtime Float32 precision; boundary cuts retain original planes; private source terrain inserted without nested meshes. No approval inherited.'}
  save(DOC/'unapproved-complete-parent.json',patch)
  builder=module('folkland_complete_validation',HERE/'resolve-pass-indexed-parent-clipping.py');rootpath=ROOT/'3d-viewer'/parent['meta']['parentTerrain'];root=read(rootpath);refs.append(rootpath);failure=None
  try:builder.validate_patch(patch,root)
  except Exception as e:failure=dict(type=type(e).__name__,message=str(e))
  result=dict(uids=summary['uids'],installationApproved=False,liveChanges=False,sourceBuildingGeometryChanges=0,previousParentFaces=len(old),newParentFaces=len(tri),unchangedParentFaces=unchanged,cutParentFaces=cut,removedParentFaces=removed,verticalFacesTouchingReplacement=vertical,validatorFailure=failure,parentNativeUids=summary['parentNativeUids'],nextStep='Resolve any exact validation failure, then run complete affected-domain, all-neighbour, runtime and visual acceptance. This is private, not installed.')
  assert reservations.owns(lease);assert digest(parentpath.read_bytes())==pins[str(parentpath.relative_to(ROOT))]
  save(DOC/'summary.json',result);refs.extend([HERE/'native_patch_resolution.py',HERE/'resolve-pass-indexed-parent-clipping.py'])
  module('folkland_flatten_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-complete-native-parent-construction',refs,result);print(result,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
