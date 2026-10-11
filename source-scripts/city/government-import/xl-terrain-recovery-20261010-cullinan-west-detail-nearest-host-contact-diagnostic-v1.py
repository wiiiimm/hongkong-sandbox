"""Explain original mounting negatives; approximate distances are not certificates."""
import importlib.util,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-cullinan-west-detail-nearest-host-contact-diagnostic-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261010-cullinan-west-three-current-original-complete-support-v1';PROBE=BASE/'government-xl-terrain-recovery-cullinan-west-three-complete-original-current-probe-v1-20261010';MOUNT=BASE/'xl-terrain-recovery-20261010-cullinan-west-complete-original-literal-detail-facets-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def distance(point,t):
 a,b,c=t;u=b-a;v=c-a;n=np.cross(u,v);n2=n@n;best=np.inf
 if n2:
  foot=point-n*((point-a)@n)/n2;matrix=np.array([[u@u,u@v],[u@v,v@v]])
  try:x,y=np.linalg.solve(matrix,np.array([(foot-a)@u,(foot-a)@v]))
  except np.linalg.LinAlgError:x=y=-1
  if x>=0 and y>=0 and x+y<=1:best=np.linalg.norm(point-foot)
 for a,b in [(a,b),(b,c),(c,a)]:
  e=b-a;e2=e@e;s=np.clip((point-a)@e/e2,0,1)if e2 else 0;best=min(best,np.linalg.norm(point-(a+s*e)))
 return float(best)
def main():
 assert not DOC.exists();g=read(GRAPH/'diagnostic.json.gz');sel=read(PROBE/'selection.json.gz');assets=[ROOT/next(r for r in sel['rows']if r['uid']==a['uid'])['candidate']['path']for a in g['actors']];tri=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets]);assert digest(tri.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256'];rows=[]
 for row in read(MOUNT/'diagnostic.json.gz')['rows'][:3]:
  ids=row['completeFaces'];hosts=row['completeRootedFiniteHostFaceScope'];points=np.unique(tri[ids].reshape(-1,3),axis=0);distances=[]
  for p in points:
   values=[distance(p,t)for t in tri[hosts]];m=int(np.argmin(values));distances.append(dict(vertex=p.tolist(),approximateNearestRootedFiniteFacetDistanceM=values[m],hostFace=hosts[m]))
  contacts=[];pairs=0
  for i in ids:
   if not np.any(np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0])):continue
   near=[j for j in hosts if np.all(tri[j].max(axis=0)>=tri[i].min(axis=0))and np.all(tri[j].min(axis=0)<=tri[i].max(axis=0))]
   for j in near:
    if not np.any(np.cross(tri[j,1]-tri[j,0],tri[j,2]-tri[j,0])):continue
    pairs+=1;ps=intersection_points(rational_face(tri[i]),rational_face(tri[j]))
    if ps:contacts.append(dict(detailFace=i,rootedHostFace=j,exactPoints=[[str(x)for x in p]for p in sorted(ps)],positiveDimension=len(ps)>1))
  rows.append(dict(component=row['component'],completeOriginalFaces=ids,completeCandidateRootedFiniteHostFaces=hosts,allOriginalVertexApproximateNearestDistances=distances,completeClosedAABBEligibleTrianglePairs=pairs,allExactSourceContacts=contacts,minimumApproximateVertexDistanceM=min(r['approximateNearestRootedFiniteFacetDistanceM']for r in distances),maximumApproximateVertexDistanceM=max(r['approximateNearestRootedFiniteFacetDistanceM']for r in distances),approximateDistancesNotContinuousCertificates=True,visualRoleAccepted=False,structuralRootCredit=False));print(dict(component=row['component'],approximateMin=rows[-1]['minimumApproximateVertexDistanceM'],approximateMax=rows[-1]['maximumApproximateVertexDistanceM'],exactContacts=len(contacts)),flush=True)
 refs=[ref(p)for p in [Path(__file__),*assets,GRAPH/'diagnostic.json.gz',GRAPH/'result.json',PROBE/'selection.json.gz',MOUNT/'diagnostic.json.gz',MOUNT/'result.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py']];save(DOC/'diagnostic.json.gz',dict(uids=[a['uid']for a in g['actors']],rows=rows,sourceOnlyDiagnostic=True,evidenceRefs=refs,sourceGeometryChanges=0,installationApproved=False));sp=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(sp);sp.loader.exec_module(f);f.freeze(BATCH,'original-three-original-detail-nearest-finite-host-and-exact-point-contact-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[a['uid']for a in g['actors']],sourceOnlyDiagnostic=True,sourceGeometryChanges=0,visualRoleAccepted=False))
if __name__=='__main__':main()
