"""DRAFT complete far-owning body finite contacts to all other genuine original bodies."""
from pathlib import Path
from collections import Counter
import json
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,cross,sub,dot
from exact_original_component_contacts_20261009 import contact_measure
from science_museum_original_open_sided_contact_topology_attribution_v1_20261011 import relative_interior
B=ROOT/'docs/astra-city/government-import'
OLD=B/'government-xl-youth-square173512-original-body-extent-podium-contacts-v2-20261011'
DOC=B/'government-xl-youth-square173512-far-body-full-source-finite-contacts-v1-20261011'
UID='landsd/173512:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();d=read(OLD/'diagnostic.json.gz');r=read(OLD/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 source=d['sources'][UID];asset=ROOT/source['path'];assert ref(asset)==source
 t=decode_original_world_triangles(asset.read_bytes());assert t.shape==(13100,3,3)and digest(t.astype('<f8').tobytes())==d['worldSHA256'][UID]
 census=d['originalCensuses'][UID];bodies=census['sharedEdgeConnectedComponents'];assert len(bodies)==372
 labels={f:k for k,fs in enumerate(bodies)for f in fs};assert set(labels)|set(census['exactNonrenderingOriginalFaces'])==set(range(13100))
 selected=sorted({row['body']for row in d['all286HistoricalGroupFarFaces']});assert selected==[6,152,153]
 fs=sorted(f for body in selected for f in bodies[body]);assert len(fs)==524
 others=np.array(sorted(labels),dtype=int);lo=t.min(1);hi=t.max(1);cache={};rows=[];domain=0;tested=0
 def face(i):
  if i not in cache:cache[i]=rational_face(t[i])
  return cache[i]
 for i in fs:
  valid=others[np.array([labels[int(j)]!=labels[i]and(not labels[int(j)]in selected or int(j)>i)for j in others],bool)]
  domain+=len(valid)
  js=valid[np.all(hi[valid]>=lo[i],axis=1)&np.all(hi[i]>=lo[valid],axis=1)]
  for j0 in js:
   j=int(j0);tested+=1;assert tested<=250000,'Explicit exact-pair compute bound exceeded; no partial qualification'
   a,z=face(i),face(j);points=sorted(intersection_points(a,z))
   if not points:continue
   measure=contact_measure(points);na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nz=cross(sub(z[1],z[0]),sub(z[2],z[0]));cop=not any(cross(na,nz))and all(dot(na,sub(v,a[0]))==0 for v in z);mid=tuple(sum(v[k]for v in points)/len(points)for k in range(3))
   rows.append(dict(originalFaces=[i,j],originalBodies=[labels[i],labels[j]],coplanar=cop,bothRelativeInteriorCrossing=not cop and measure['dimension']>0 and relative_interior(a,mid)and relative_interior(z,mid),**measure))
 summaries=[]
 for body in selected:
  contacts=[r for r in rows if body in r['originalBodies']]
  summaries.append(dict(body=body,completeOriginalFaces=bodies[body],positiveFiniteContactedBodies=sorted({other for row in contacts if row['dimension']>0 for other in row['originalBodies']if other!=body}),pointOnlyContactedBodies=sorted({other for row in contacts if row['dimension']==0 for other in row['originalBodies']if other!=body}),dimensionCounts=dict(Counter(row['dimension']for row in contacts)),contactFaces=[row['originalFaces']for row in contacts],allContactsMountSupportIdentityUnqualified=True))
 assert ref(asset)==source
 refs=[ref(p)for p in [Path(__file__),asset,OLD/'diagnostic.json.gz',OLD/'result.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'science_museum_original_open_sided_contact_topology_attribution_v1_20261011.py',HERE/'test_science_museum_contact_relative_interior_v1_20261011.py']]
 save(DOC/'diagnostic.json.gz',dict(uid=UID,source=source,worldSHA256=d['worldSHA256'][UID],fullOriginalFaces=13100,completeGenuineBodies=372,selectedFarBodies=selected,completeSelectedFaces=fs,completeOtherBodyFacetPairDomain=domain,completeInclusive3DAABBPairsTested=tested,allExactContacts=rows,completeSelectedBodySummaries=summaries,allOther372BodyObligationsRetained=True,prior286FarAndForeignAndSampledBurialFailuresRetained=True,sourceOnly=True,currentAcceptance=False,identityAccepted=False,mountSupportRootCredit=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,qualification='Complete finite contacts of all524faces of far-owning bodies6/152/153 to every other genuine original source body; shared-edge census remains unchanged. Point contacts cannot bridge. Positive finite surface intersections and relative-interior crossings are geometric authored relationships, not architectural function, solid collision, support or extent exemption. Every source face/body and all historical/current guards survive.',evidenceRefs=refs))
 print(json.dumps(dict(selectedFaces=len(fs),completePairDomain=domain,exactPairs=tested,finiteContacts=len(rows),summaries=summaries)),flush=True)
if __name__=='__main__':main()
