"""DRAFT complete original14body finite contact inventory; no mount/root/role/identity approval."""
from pathlib import Path
from collections import Counter
import json,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,cross,sub,dot
from exact_original_component_contacts_20261009 import contact_measure
from science_museum_original_open_sided_contact_topology_attribution_v1_20261011 import relative_interior
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-mongkok-stadium-complete-original-far-extent-body-attribution-v1-20261011';PROFILE=B/'government-xl-mongkok-stadium-original62-face-profile-primary-registration-v2-20261011';METHOD=B/'government-xl-mongkok-stadium-original14-body-finite-contact-method-v1-20261011/METHOD.md';DOC=B/'government-xl-mongkok-stadium-original14-body-finite-contact-inventory-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();d=read(OLD/'diagnostic.json.gz');profile=read(PROFILE/'diagnostic.json.gz')
 for base in [OLD,PROFILE]:
  r=read(base/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 asset=ROOT/d['source']['path'];assert ref(asset)==d['source'];tri=decode_original_world_triangles(asset.read_bytes());assert tri.shape==(15456,3,3)and digest(tri.astype('<f8').tobytes())==d['completeOriginalWorldSHA256']==profile['completeOriginalWorldSHA256'];bodies=d['completeOriginalNonzeroBodyCensus']['sharedEdgeConnectedComponents'];zeros=d['completeOriginalNonzeroBodyCensus']['exactNonrenderingOriginalFaces'];assert len(bodies)==14 and len(zeros)==15;labels={i:k for k,fs in enumerate(bodies)for i in fs};assert set(labels)|set(zeros)==set(range(15456));lo=tri.min(1);hi=tri.max(1);records=[];possible=0;tested=0;rf={}
 def face(i):
  if i not in rf:rf[i]=rational_face(tri[i])
  return rf[i]
 for k,fs in enumerate(bodies):
  others=np.asarray([i for z in bodies[k+1:]for i in z],int);possible+=len(fs)*len(others)
  for i in fs:
   if not len(others):continue
   js=others[np.all(hi[others]>=lo[i],axis=1)&np.all(hi[i]>=lo[others],axis=1)];tested+=len(js)
   for j0 in js:
    j=int(j0);a,z=face(i),face(j);points=sorted(intersection_points(a,z))
    if not points:continue
    measure=contact_measure(points);na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nz=cross(sub(z[1],z[0]),sub(z[2],z[0]));cop=not any(cross(na,nz))and all(dot(na,sub(p,a[0]))==0 for p in z);mid=tuple(sum(p[t]for p in points)/len(points)for t in range(3));records.append(dict(originalFaces=[i,j],originalNonzeroBodies=[labels[i],labels[j]],exactIntersectionPoints=[[str(v)for v in p]for p in points],coplanar=cop,bothRelativeInteriorSurfaceCrossing=not cop and measure['dimension']>0 and relative_interior(a,mid)and relative_interior(z,mid),**measure))
  print(json.dumps(dict(completeBodiesThrough=k,exactAABBPairs=tested,allFiniteContacts=len(records))),flush=True)
 summary=[]
 for a in range(14):
  for z in range(a+1,14):
   rows=[r for r in records if r['originalNonzeroBodies']==[a,z]];summary.append(dict(originalBodies=[a,z],positiveLengthOrAreaPairs=sum(r['dimension']>0 for r in rows),pointOnlyPairs=sum(r['dimension']==0 for r in rows),coplanarPairs=sum(r['coplanar']for r in rows),bothRelativeInteriorSurfaceCrossingPairs=sum(r['bothRelativeInteriorSurfaceCrossing']for r in rows),allFacetPairs=[r['originalFaces']for r in rows],mountSupportRootRolesUnqualified=True))
 obligations=[dict(originalBody=k,completeOriginalFaceIDs=fs,positiveContactedOriginalBodies=sorted({other for r in records if r['dimension']>0 and k in r['originalNonzeroBodies']for other in r['originalNonzeroBodies']if other!=k}),pointOnlyContactProvidesNoBridge=True,architectureIdentityFunctionMountSupportRootUnresolved=True)for k,fs in enumerate(bodies)]
 refs=[ref(p)for p in [Path(__file__),METHOD,asset,OLD/'diagnostic.json.gz',OLD/'result.json',PROFILE/'diagnostic.json.gz',PROFILE/'result.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'science_museum_original_open_sided_contact_topology_attribution_v1_20261011.py',HERE/'test_science_museum_contact_relative_interior_v1_20261011.py']];assert ref(asset)==d['source'];save(DOC/'diagnostic.json.gz',dict(uid='landsd/240332:0',source=d['source'],completeOriginalFaces=15456,completeOriginalWorldSHA256=d['completeOriginalWorldSHA256'],completeNonzeroBodies=14,exactZeroOriginalFaces=zeros,completeCrossBodyFacetPairsConsidered=possible,completeInclusiveUnpadded3DAABBPairsTested=tested,allExactOriginalCrossBodyContacts=records,all91BodyPairSummaries=summary,complete14BodyObligations=obligations,sourceOnly=True,currentAcceptance=False,identityAccepted=False,extentGuardWaived=False,architectureRoleAccepted=False,mountSupportRootCredit=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,qualification='Complete original14body finite surface contact inventory and all91body-pair summaries; point/zero cannot bridge. Positive surface intersections and both-relative-interior crossings are diagnostic authored surface relationships, not solid collision, function, attachment, support/root or body approval. All14 obligations, full350.641m2 outside projection, all62far/12.871m extent and identity/current ground/foreign/native/runtime obligations survive.',evidenceRefs=refs));print(json.dumps(dict(sourceOnly=True,possiblePairs=possible,exactPairs=tested,contacts=len(records),currentAcceptance=False)))
if __name__=='__main__':main()
