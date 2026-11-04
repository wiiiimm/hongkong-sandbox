"""DRAFT complete original171 cross-body finite contacts; geometry only, no role/support credit."""
from pathlib import Path
import json,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,cross,sub,dot
from exact_original_component_contacts_20261009 import contact_measure
from science_museum_original_open_sided_contact_topology_attribution_v1_20261011 import relative_interior
B=ROOT/'docs/astra-city/government-import';C=B/'government-xl-science-museum-open-sided-original-gltf-identity-comparison-v3-20261011';T=B/'government-xl-science-museum-original-open-sided-contact-topology-attribution-v1-20261011';U=B/'government-xl-science-museum-original-raw-uv-body-atlas-registration-v1-20261011';DOC=B/'government-xl-science-museum-original171-cross-body-contact-inventory-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 for folder in [C,T,U]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 arr=C/'complete-original-viewer-coordinate-diagnostic.npz'
 with np.load(arr,allow_pickle=False)as n:tri=n['triangles']
 c=read(C/'diagnostic.json.gz');assert tri.shape==(171,3,3)and digest(tri.astype('<f8').tobytes())==c['completeAuthoredMatrixWorldTrianglesSHA256'];t=read(T/'diagnostic.json.gz');labels={f:b['body']for b in t['originalOpenBodyDetails']for f in b['originalFaces']};zeros=t['originalOpen171FaceCensus']['exactNonrenderingOriginalFaces'];assert set(labels)|set(zeros)==set(range(171));lo=tri.min(1);hi=tri.max(1);pairs=0;records=[];possible=0
 for i in range(171):
  for j in range(i+1,171):
   if i not in labels or j not in labels or labels[i]==labels[j]:continue
   possible+=1
   if not(np.all(hi[i]>=lo[j])and np.all(hi[j]>=lo[i])):continue
   pairs+=1;a,b=rational_face(tri[i]),rational_face(tri[j]);pts=sorted(intersection_points(a,b))
   if not pts:continue
   measure=contact_measure(pts);na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]));coplanar=not any(cross(na,nb))and all(dot(na,sub(p,a[0]))==0 for p in b);mid=tuple(sum(p[k]for p in pts)/len(pts)for k in range(3));records.append(dict(originalFaces=[i,j],nonzeroEdgeBodies=[labels[i],labels[j]],coplanar=coplanar,noncoplanarBothRelativeInteriorSurfaceCrossing=not coplanar and measure['dimension']>0 and relative_interior(a,mid)and relative_interior(b,mid),**measure))
 adj={i:set()for i in range(5)}
 for r in records:
  if r['dimension']>0:a,b=r['nonzeroEdgeBodies'];adj[a].add(b);adj[b].add(a)
 reached={0};pending=[0]
 while pending:
  for i in sorted(adj[pending.pop()]):
   if i not in reached:reached.add(i);pending.append(i)
 refs=[ref(p)for p in [Path(__file__),arr,C/'diagnostic.json.gz',C/'result.json',T/'diagnostic.json.gz',T/'result.json',U/'diagnostic.json.gz',U/'result.json',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'science_museum_original_open_sided_contact_topology_attribution_v1_20261011.py']];save(DOC/'diagnostic.json.gz',dict(sourceOnly=True,currentAcceptance=False,identityAccepted=False,installationApproved=False,geometryChanges=0,source171WorldSHA256=c['completeAuthoredMatrixWorldTrianglesSHA256'],completeCrossBodyFacetPairsConsidered=possible,completeInclusiveUnpadded3DAABBPairsTested=pairs,allOriginalCrossBodyFiniteContacts=records,exactZeroSourceFacesPreserved=zeros,zeroFacesProvideNoConnectivityBridge=True,completeBodyPositiveDimensionalContactAdjacency={b:sorted(s)for b,s in adj.items()},body0GeometricContactReachableOnly=sorted(reached),noArchitectureOrPhysicalSupportRoleGranted=True,noGroundOrRootCredit=True,noPointOnlyBridgeCredit=True,allFiveBodyObligationsPreserved=True,preserved53OriginalMuseumProperSurfaceCrossings=True,qualification='Complete unchanged original source finite cross-body interface inventory only. Positive-dimensional reachability is geometric contact, not architectural joint validity, lower-boundary mount, physical support, grade root or a structural/visual role approval. Actual primary entrance/body evidence and whole source/current/F32/ground/foreign/native/runtime gates remain. Point-only/zero faces cannot bridge any body.',evidenceRefs=refs));print(json.dumps(dict(crossBodyPairs=possible,exactAABBPairs=pairs,contacts=len(records),geometricReachableOnly=sorted(reached),currentAcceptance=False)))
if __name__=='__main__':main()
