"""One bounded SOURCE-ONLY decision: grade evidence versus terrain-only impossibility.

No wall/downward role is accepted, no geometry generated, no current terrain or
host/root credit. Every one of 510 original failures survives this decision.
A witness can prove ordinary clearance impossible for the stated fixed-XZ
candidate family; absence of that certificate never proves terrain feasible.
"""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction as F
import importlib.util,uuid,time
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from exact_original_fixed_xz_terrain_clearance_infeasibility_v1_20261011 import verify as impossible
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-hoi-shing-bounded-installation-disposition-v1';DOC=BASE/BATCH
FINITE=BASE/'xl-terrain-recovery-20261011-hoi-shing-derived-ground-complete-original-finite-v2'
CLASS=BASE/'xl-terrain-recovery-20261011-hoi-shing-complete-burial-source-classification-v1'
SHELL=BASE/'xl-terrain-recovery-20261011-hoi-shing-three-downward-bodies-shell-context-v1'
GRAPH=BASE/'xl-terrain-recovery-20261011-hoi-shing-complete-original-edge-contact-graph-v1'
TIN=BASE/'xl-terrain-recovery-20261011-hoi-shing-two-original-authentic-tin-finite-v1'
PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011'
PRIMARY=BASE/'government-xl-hoi-shing-exact-72-face-primary-step-association-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [FINITE,CLASS,SHELL,GRAPH,TIN,PROBE,PRIMARY]:
  result=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
  receipts[folder.name]=result;refs.append(ref(folder/'result.json'))
 def bound(folder,p):
  assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 f=bound(FINITE,FINITE/'diagnostic.json.gz');cl=bound(CLASS,CLASS/'diagnostic.json.gz');shell=bound(SHELL,SHELL/'diagnostic.json.gz');graph=bound(GRAPH,GRAPH/'diagnostic.json.gz');s=bound(PROBE,PROBE/'selection.json.gz')
 primary=bound(PRIMARY,PRIMARY/'diagnostic.json.gz');assert primary['completeOriginalPartFaceIds']==[i-13841 for i in graph['components'][103]['globalOriginalFaces']]
 old=bound(TIN,HERE/'local'/TIN.name/'complete-authentic-source-tin-ground.json.gz')
 captured=bound(FINITE,HERE/'local'/FINITE.name/'complete-selected-derived-ground.json.gz')
 original=np.asarray(old['completeSelectedFacets'],float);ground=np.asarray(captured['complete11554DerivedFacets'],float)
 assert original.shape==ground.shape==(11554,3,3)and np.array_equal(original[:,:,[0,2]],ground[:,:,[0,2]])
 assert digest(ground.tobytes())==captured['completeDerivedGroundSHA256']and old['sourceCoveringWholeFacetIds']==captured['sameExactWholeOriginalFacetIDs']
 world=[];contexts=[];offset=0;raw=[]
 for row,data in zip(s['rows'],f['rows']):
  asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());refs.append(ref(asset))
  assert data['uid']==row['uid']and digest(tri.tobytes())==data['completeOriginalWorldSHA256']and digest(ground.tobytes())==data['completeUndeployedDerivedGroundSHA256']
  assert len(data['allFaces'])==len(data['completeAllOriginalFacetContexts'])==len(tri)
  assert [c['sourceFace']for c in data['completeAllOriginalFacetContexts']]==list(range(len(tri)))
  world.append(tri);contexts.extend(data['completeAllOriginalFacetContexts']);raw.extend(i+offset for i in data['unprovedOriginalFaces']);offset+=len(tri)
 world=np.concatenate(world);assert world.shape==(19374,3,3)and digest(world.tobytes())==graph['binding']['completeOriginalWorldSHA256']and len(raw)==510
 n=np.cross(world[:,1]-world[:,0],world[:,2]-world[:,0]);length=np.linalg.norm(n,axis=1);ratio=np.divide(n[:,1],length,out=np.zeros(len(world)),where=length>0)
 walls={int(i)for i in np.flatnonzero((length>0)&(np.abs(ratio)<=.25))}
 roofs={i for i,c in enumerate(contexts)if length[i]>0 and ratio[i]>.25 and c['groundProjectionCovered']is True and F(c['exactCertifiedLowerClearanceM'])>=-F(1,2)}
 eligible=walls|roofs;adj={i:set()for i in eligible};edgefaces=defaultdict(list)
 for i in sorted(eligible):
  for a,b in zip(world[i],np.roll(world[i],-1,axis=0)):edgefaces[tuple(sorted((tuple(a),tuple(b))))].append(i)
 for ids in edgefaces.values():
  for i in ids:adj[i].update(j for j in ids if j!=i)
 contacts=graph['oneExactPositiveWitnessPerContactingBodyPair'];assert len(contacts)==149;replayed=[]
 lease=reservations.claim('hoi-bounded-disposition-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert lease['ok'];reservation=lease['reservation']
 def renew():
  result=reservations.heartbeat(reservation);assert result['ok']
 try:
  for r in contacts:
   i,j=r['globalOriginalFaces'];points=intersection_points(rational_face(world[i]),rational_face(world[j]));exact=[[str(v)for v in p]for p in sorted(points)]
   assert len(points)>1 and exact==r['exactContact']['exactPoints'];used=i in eligible and j in eligible
   if used:adj[i].add(j);adj[j].add(i)
   replayed.append(dict(existingWitnessVerbatim=r,exactPointListReplay=exact,bothEndpointFacetsEligible=used))
  renew();parent={i:None for i in roofs};todo=deque(sorted(roofs))
  while todo:
   i=todo.popleft()
   for j in sorted(adj[i]):
    if j in walls and j not in parent:parent[j]=i;todo.append(j)
  affected_walls=sorted(set(raw)&walls)
  grade_candidates=[i for i in affected_walls if contexts[i]['maximumObservedGapM']is not None and contexts[i]['maximumObservedGapM']>0]
  grade=exact_upper_ground_interfaces(world,grade_candidates,ground);renew();bygrade=defaultdict(list)
  for r in grade:bygrade[r['sourceFace']].append(r)
  decisions=[]
  records=cl['all510OriginalFacetRecords'];assert len(records)==510 and sorted(r['globalOriginalFace']for r in records)==raw
  for r in records:
   i=r['globalOriginalFace'];certificates=[]
   # The saved strongest DERIVED witness is exact and independently on source.
   # AUTHENTIC facet evaluation can only strengthen the necessary lowering.
   w=min(r['actualFiniteNegativePointWitnesses'],key=lambda v:F(v['exactGapM']));j=w['originalSelectedDerivedGroundFace']
   cert=impossible(world[i],original[j],w['exactSourcePoint'])
   cert.update(originalSelectedGroundFace=j,originalWholeAuthenticSheetFace=old['sourceCoveringWholeFacetIds'][j],savedDerivedNegativeWitnessVerbatim=w)
   certificates.append(cert);path=[i]
   if i in walls:
    while path[-1]in parent and parent[path[-1]]is not None:path.append(parent[path[-1]])
   wall_path=i in walls and path[-1]in roofs;interfaces=bygrade[i]
   condition=('Needs independently justified original downward-body role; closed geometry alone gives no credit'if i not in walls else'Needs complete grade-spanning exterior role and host/root/current proof'if wall_path and interfaces else'Needs exact eligible exposed source continuation or original source correction; ordinary terrain family may be infeasible')
   decisions.append(dict(globalOriginalFace=i,originalPFace=r['sourceFace'],originalBody=r['originalBody'],rawCompleteFiniteContextVerbatim=r['completeFiniteContextVerbatim'],existingEligibleWallRoofPath=path,pathEndsAtOrdinaryClearOriginalRoof=wall_path,exactPositiveLengthUpperGradeInterfaces=interfaces,sourceGradeCrossingAndRoofPathEvidenceOnly=bool(wall_path and interfaces),terrainOnlyOrdinaryInfeasibilityWitnesses=certificates,ordinaryClearanceImpossibleUnderFixedXZTotal065=cert['ordinaryClearanceInfeasibleForThisCandidateFamily'],absenceOfInfeasibilityCertificateDoesNotProveFeasible=True,unresolvedAcceptanceCondition=condition,roleAssigned=False,rootOrBridgeCredit=False))
  refs.extend(ref(HERE/name)for name in ['exact_packed_world_geometry_20261009.py','exact_original_fixed_xz_terrain_clearance_infeasibility_v1_20261011.py','test_exact_original_fixed_xz_terrain_clearance_infeasibility_v1_20261011.py','exact_original_shell_intersections_20261009.py','exact_original_upper_ground_interfaces_20261009.py','exact_original_component_contacts_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py']);renew();assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=[r['uid']for r in s['rows']],all510RawOriginalFailuresPreserved=decisions,allExisting149SourceWitnessReplays=replayed,completeOriginalWorldSHA256=digest(world.tobytes()),completeOriginalAuthenticSelectedGroundSHA256=digest(original.tobytes()),explicitUndeployedDerivedGroundSHA256=digest(ground.tobytes()),threeClosedOriginalBodyGeometryVerbatim=shell['rows'],independentMappedStepEvidenceOnlyForBody103=True,existing149WitnessesNotCompleteContactEnumeration=True,allZeroFacetsRetainedWithoutSupportCredit=True,sourceOnly=True,currentAcceptance=False,terrainGenerated=False,sourceFunctionInferred=False,roleAssigned=False,hostQualification=False,rootOrBridgeCredit=False,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze_hoi_decision',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'bounded-hoi-original-grade-evidence-and-fixed-XZ-total065-ordinary-infeasibility-disposition-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=out['uids'],sourceOnly=True,currentAcceptance=False,all510RawOriginalFailuresPreserved=True,sourceGradePathEvidenceOnly=sum(d['sourceGradeCrossingAndRoofPathEvidenceOnly']for d in decisions),ordinaryClearanceImpossibleUnderFixedXZTotal065=sum(d['ordinaryClearanceImpossibleUnderFixedXZTotal065']for d in decisions),roleAssigned=False,newlyInstalled=0))
 finally:assert reservations.release(reservation)['ok']
if __name__=='__main__':main()
