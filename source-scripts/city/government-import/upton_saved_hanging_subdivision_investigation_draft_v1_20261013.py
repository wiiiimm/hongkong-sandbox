"""UNEXECUTED saved-gap hanging/subdivision inspection; no repair constructor."""
from pathlib import Path
from collections import defaultdict
from fractions import Fraction as F
import json,sys,time,uuid,subprocess
import numpy as np
import upton_saved_uncovered_packed_ancestor_boundary_attribution_draft_v1_20261013 as prior
from run import ROOT,HERE,read,save,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-saved-hanging-subdivision-packing-investigation-v1-20261013'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JOB='99e1e9daa5bde8286df4224360ab17934044b87d13226d7491e8700ca4860b6a'
ref,check=prior.ref,prior.check
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.prior.CURRENT
 receipt=read(prior.DOC/'result.json');assert receipt['jobId']==JOB
 output=read(prior.DOC/'complete-saved-failures-packed-ancestor-boundary-attribution.json.gz');assert len(output['rows'])==357
 kinds=[r['localGapAttribution']['savedCoverageVerbatim']['method']for r in output['rows']]
 assert kinds.count('closed-facet-interval-union')==100 and kinds.count('closed-facet-area-union')==257
 _,_,_,nomination,raw,provenance,source,current,drawn,_=prior.load()
 protected=[]
 for i,p in enumerate(provenance):
  if p.get('region')=='wholeCurrentProtectionFacet':
   assert p['kind']=='capturedCurrentRing'and p['savedInputByteExact']and not p['computedFragment']
   assert raw[i].tobytes()==current[p['originalFace']].tobytes()
   protected.append(dict(candidateFace=i,currentOriginalFace=p['originalFace'],rawTripletSHA256=prior.prior.prior.sha(raw[i]),sourceAttribution=p['completeCurrentSourceAttribution']))
 assert len(protected)==68
 return pins,receipt,output,raw,provenance,drawn,protected
def schema_only():
 _,_,o,r,p,d,protected=load()
 return dict(passed=True,caller=ref(Path(__file__)),completeSavedRows=357,intervalRows=100,areaRows=257,completeRawNativeFacets=len(r),literalWholeCurrentProtectedFacets=protected,noDBLeaseCoverageOrRepair=True)
def oriented_sides(point,t):
 q=[prior.xz(p)for p in t];area=prior.cross(q[0],q[1],q[2])
 return area,[prior.cross(a,b,point)if area>0 else-prior.cross(a,b,point)for a,b in zip(q,q[1:]+q[:1])]
def subdivision_relation(p,a,b,packed,pa,pb,literal_whole,protected_node_incident=False):
 txz=prior.segment_parameter(prior.xz(p),prior.xz(a),prior.xz(b))
 if txz is None or not 0<txz<1:return None
 t3=prior.segment_parameter(p,a,b);pt=prior.segment_parameter(prior.xz(packed),prior.xz(pa),prior.xz(pb))
 return dict(exactInteriorProjectedParameter=txz,exactFinite3DParameter=t3,projectedOnlyDifferentHeightLayer=t3 is None,packedNodeOnLongPackedProjectedEdge=pt is not None,packedParameter=pt,protectedWholeCurrentNodeIncident=protected_node_incident,protectedIncidentFamilyConstrainedUnresolved=literal_whole or protected_node_incident,eligibleComputed3DHangingSubdivisionNomination=t3 is not None and pt is None and not literal_whole and not protected_node_incident,noGeometryOrCoverageCredit=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,receipt,output,raw,provenance,drawn,protected=load()
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md')]+receipt['evidenceRefs']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 for q in refs:check(q);pulse()
 ideal=[];actual=[];vertices=defaultdict(list);packed_for_vertex={}
 for i,p in enumerate(provenance):
  t=tuple(tuple(F(v)for v in q)for q in p['exactOriginalPlanePoints'])if p.get('exactOriginalPlanePoints')is not None else prior.exact(raw[i]);cast=np.asarray(raw[i],dtype=np.float32).astype('<f8')
  order=[0,1,2]if drawn[i].tobytes()==cast.tobytes()else[0,2,1];assert drawn[i].tobytes()==cast[order].tobytes()
  t=tuple(t[j]for j in order);a=prior.exact(drawn[i]);ideal.append(t);actual.append(a)
  for v,(ip,ap)in enumerate(zip(t,a)):
   assert ip not in packed_for_vertex or packed_for_vertex[ip]==ap
   packed_for_vertex[ip]=ap;vertices[ip].append(dict(candidateFace=i,vertex=v))
  if i%256==0:pulse()
 protected_ids={q['candidateFace']for q in protected};targets={};point_rows=[]
 for row in output['rows']:
  for g in row['localGapAttribution']['savedFirstIntervalGapAttribution']:
   point=tuple(F(v)for v in g['exactSavedGapMidpointXZ']);face_rows=[]
   for i in g['idealFragmentPointMembershipCandidates']:
    ia,isides=oriented_sides(point,ideal[i]);pa,psides=oriented_sides(point,actual[i]);assert ia!=0 and all(x>=0 for x in isides)
    rejected=[e for e,s in enumerate(psides)if s<0]if pa!=0 else[]
    for e in rejected:targets.setdefault((i,e),[]).append(dict(uid=row['uid'],mode=row['mode'],sourceFace=row['sourceFace'],sourceFaceSHA256=row['sourceFaceSHA256'],exactSavedGapMidpointXZ=point))
    face_rows.append(dict(candidateFace=i,provenanceVerbatim=provenance[i],exactIdealProjectedArea2=ia,actualPackedProjectedArea2=pa,idealOrientedSideValues=isides,packedOrientedSideValues=psides,packedRejectingEdges=rejected,packedProjectedCollapseUncredited=pa==0,noWholeCoverageClaim=True))
   point_rows.append(dict(uid=row['uid'],mode=row['mode'],sourceFace=row['sourceFace'],exactSavedGapRecordVerbatim=g,idealContainingPackedRejectingFacets=face_rows))
  pulse()
 edge_rows=[]
 for (i,e),saved_points in sorted(targets.items()):
  a,b=ideal[i][e],ideal[i][(e+1)%3];pa,pb=actual[i][e],actual[i][(e+1)%3];lo=tuple(min(a[k],b[k])for k in [0,2]);hi=tuple(max(a[k],b[k])for k in [0,2]);nodes=[]
  nominated=[]
  for p in vertices:
   if all(lo[k]<=prior.xz(p)[k]<=hi[k]for k in range(2)):nominated.append(p)
  for p in sorted(nominated):
   packed=packed_for_vertex[p];protected_node_incident=any(q['candidateFace']in protected_ids for q in vertices[p]);relation=subdivision_relation(p,a,b,packed,pa,pb,i in protected_ids,protected_node_incident)
   if relation is None:continue
   nodes.append(dict(exactIdealXYZ=p,actualPackedXYZ=packed,**relation,allComplete11575VertexIncidents=[dict(**q,provenanceVerbatim=provenance[q['candidateFace']],literalWholeProtected=q['candidateFace']in protected_ids)for q in vertices[p]]))
  edge_rows.append(dict(candidateFace=i,edge=e,provenanceVerbatim=provenance[i],exactIdealLongEdgeXYZ=[a,b],actualPackedLongEdgeXYZ=[pa,pb],completeExactClosedBoundsNominatedVertexCount=len(nominated),completeInteriorSubdivisionNodes=nodes,allSavedGapPointRelations=saved_points,longEdgeLiteralWholeProtected=i in protected_ids,literalWholeEdgeCannotBeRetriangulated=True if i in protected_ids else False,completeActualCandidateCensusUsed=True,fullEdgePackingAlreadyAgreesFromPriorEvidence=True,noAutomaticHoldFromExteriorIncidence=True));pulse()
 DOC.mkdir(parents=True);save(DOC/'complete-saved-gap-hanging-subdivision-investigation.json.gz',prior.serial(dict(intervalPointRows=point_rows,rejectingLongEdgeRows=edge_rows,literalWholeCurrentProtectionVerbatim=protected,completeSavedFailureRowsVerbatim=output['rows'],areaRowsStillUnlocated=257,noAreaUnionOrWholeActorProofReplayed=True,noOriginalSourceOrCandidateGeometryEdited=True,repairNotConstructed=True,physicalAccepted=False,installationApproved=False)))
 refs +=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 for q in refs:check(q);pulse()
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.prior.CURRENT;pulse(True)
 prior.prior.prior.module(prior.prior.prior.FREEZER,'upton_hanging_inspection_freezer').freeze(BATCH,'saved-gap-and-exact-hanging-subdivision-only',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=prior.prior.prior.OWNED+[prior.prior.prior.SECONDARY,prior.prior.prior.NATIVE],sourceOnly=True,completeSavedRows=357,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--inspect-saved-hanging-subdivisions-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 uids=prior.prior.prior.OWNED+[prior.prior.prior.SECONDARY,prior.prior.prior.NATIVE,prior.prior.prior.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-hanging-subdivision-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
