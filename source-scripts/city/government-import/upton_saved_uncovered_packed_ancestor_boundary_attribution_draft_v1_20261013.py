"""UNEXECUTED narrow saved-negative/packing attribution; no coverage union replay."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import json,sys,time,uuid,subprocess
import numpy as np
import upton_v6_saved_coverage_failure_attribution_draft_v1_20261013 as prior
from exact_original_projection_coverage_20261009 import cross
from run import ROOT,HERE,read,save,connect,reservations
from sparkle_current_native_renderer_winding_20261011 import drawn_native_faces
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-saved-uncovered-packed-ancestor-boundary-attribution-v1-20261013'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JOB='4348f47adf4f17433b6302f5c5e95599fded247a008804c6b1e1f5b208931608'
ref,check=prior.ref,prior.check
def exact(t):return tuple(tuple(F(float(v))for v in p)for p in t)
def serial(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:serial(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [serial(v)for v in x]
 return x
def key(a,b):return tuple(sorted((tuple(a),tuple(b))))
def xz(p):return(p[0],p[2])
def segment_parameter(p,a,b):
 # Exact closed finite membership, including zero-length descriptors.
 d=tuple(b[i]-a[i]for i in range(len(a)));axes=[i for i,v in enumerate(d)if v]
 if not axes:return F(0)if p==a else None
 t=(p[axes[0]]-a[axes[0]])/d[axes[0]]
 return t if 0<=t<=1 and all(p[i]==a[i]+t*d[i]for i in range(len(a)))else None
def inside_projected_point(p,t):
 v=[xz(q)for q in t];orientation=cross(v[0],v[1],v[2])
 if orientation==0:return False # Same nonzero-projection union admission; no zero credit.
 signs=[cross(a,b,p)for a,b in zip(v,v[1:]+v[:1])]
 return all(s>=0 for s in signs)if orientation>0 else all(s<=0 for s in signs)
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.CURRENT
 receipt=read(prior.DOC/'result.json');assert receipt['jobId']==JOB
 attribution=read(prior.DOC/'complete-main89-four-world-basic17-saved-attribution.json.gz');assert len(attribution['rows'])==357
 nomination=read(prior.V6/'complete-nominations-before-guards.json.gz')
 raw=np.asarray(nomination['candidateRawPositionTriplets'],dtype='<f8');assert raw.shape==(11575,3,3)
 provenance=nomination['candidateFaceProvenance'];assert [q['candidateFace']for q in provenance]==list(range(11575))
 source=np.asarray(read(check(nomination['allSourceOriginalTriplets']))['allOriginalTriplets'],dtype='<f8');assert source.shape==(122721,3,3)
 current_record=read(check(nomination['allCurrentTriplets']));current=np.asarray(current_record['rows'][0]['completeActualDrawnTriplets'],dtype='<f8').reshape(-1,3,3);assert current.shape==(9214,3,3)
 patch=read(prior.prior.HERE/'local'/prior.prior.MAX.name/'private-upton-v6-geometry-bound-overlap-reviewed.json')
 drawn,transform=drawn_native_faces(patch['nativeMesh']);assert drawn.shape==raw.shape
 position=np.asarray(patch['nativeMesh']['position'],dtype='<f8').reshape(-1,3);index=np.asarray(patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3)
 assert position[index].tobytes()==raw.tobytes()
 for i,q in enumerate(provenance):assert q['rawNominationFaceSHA256']==prior.prior.sha(raw[i])
 return pins,receipt,attribution,nomination,raw,provenance,source,current,drawn,transform
def schema_only():
 p,r,a,n,raw,pv,s,c,d,t=load()
 return dict(passed=True,caller=ref(Path(__file__)),savedFailureRows=357,completeNativeCandidateFaces=11575,originalTINFacets=len(s),savedCurrentFacets=len(c),allCandidateOrderAndRawSHAExact=True,noFiniteUnionRayPartitionOrDB=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,receipt,attribution,nomination,raw,provenance,source,current,drawn,transform=load()
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md')]+receipt['evidenceRefs']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 for q in refs:check(q);pulse()
 ideal=[];actual=[];edges3=defaultdict(list);edgesXZ=defaultdict(list);packedXZ=defaultdict(list)
 for i,p in enumerate(provenance):
  t=tuple(tuple(F(v)for v in x)for x in p['exactOriginalPlanePoints'])if p.get('exactOriginalPlanePoints')is not None else exact(raw[i])
  # Rational incidence identifies +0/-0 geometrically; untouched raw/draw
  # signed-zero bytes remain bound by the existing SHA and winding checks.
  assert np.array_equal(np.asarray([[float(v)for v in q]for q in t],dtype=np.float32),np.asarray(raw[i],dtype=np.float32))
  cast=np.asarray(raw[i],dtype=np.float32).astype('<f8');order=[0,1,2]if drawn[i].tobytes()==cast.tobytes()else[0,2,1]
  assert drawn[i].tobytes()==cast[order].tobytes();t=tuple(t[j]for j in order);a=exact(drawn[i]);ideal.append(t);actual.append(a)
  for e in range(3):
   loc=dict(candidateFace=i,edge=e);u,v=t[e],t[(e+1)%3];aa,bb=a[e],a[(e+1)%3]
   edges3[key(u,v)].append(loc);edgesXZ[key(xz(u),xz(v))].append(loc);packedXZ[key(xz(aa),xz(bb))].append(loc)
  if i%256==0:pulse()
 needed=sorted({m['provenance']['candidateFace']for r in attribution['rows']for g in r['selectedGroundProvenance']for m in g['allExactCandidateFaceOrigins']})
 candidates=[]
 for i in needed:
  p=provenance[i];ancestors=[]
  if p['kind']in ['originalTIN','capturedCurrentRing']:
   array=source if p['kind']=='originalTIN'else current;inventory=nomination['wholeSourceOriginalFaceInventory']if p['kind']=='originalTIN'else nomination['wholeCurrentFaceInventory'];j=p['originalFace']
   assert inventory[j]['originalFace']==j and inventory[j]['originalFaceSHA256']==prior.prior.sha(array[j])
   ancestors.append(dict(kind=p['kind'],originalFace=j,originalTripletSHA256=prior.prior.sha(array[j]),exactOriginalXYZ=exact(array[j])))
  else:
   j=p['currentSurfaceFace'];ancestors.append(dict(kind='currentSurfaceForRuledJoin',originalFace=j,originalTripletSHA256=prior.prior.sha(current[j]),exactOriginalXYZ=exact(current[j])))
   for q in p['origins']:
    j=q['originalSourceFace'];ancestors.append(dict(kind='sourceForRuledJoin',originalFace=j,originalTripletSHA256=prior.prior.sha(source[j]),exactOriginalXYZ=exact(source[j]),exactCutEdge=q['exactCutEdge'],cutCauses=q['cutCauses']))
  vertex_rows=[]
  for v,(ip,ap)in enumerate(zip(ideal[i],actual[i])):
   boundary=[]
   for ancestor in ancestors:
    t=ancestor['exactOriginalXYZ'];pt=np.asarray([[float(x)for x in a]for a in t],dtype=np.float32).astype('<f8');pt=exact(pt)
    for e in range(3):
     parameter=segment_parameter(xz(ip),xz(t[e]),xz(t[(e+1)%3]))
     if parameter is not None:
      actual_parameter=segment_parameter(xz(ap),xz(pt[e]),xz(pt[(e+1)%3]))
      boundary.append(dict(ancestorKind=ancestor['kind'],originalFace=ancestor['originalFace'],edge=e,exactIdealParameter=parameter,packedAncestorEdgeXZ=[xz(pt[e]),xz(pt[(e+1)%3])],packedPointOnPackedAncestorClosedEdge=actual_parameter is not None,packedExactParameter=actual_parameter,noCoverageOrRepairCredit=True))
   vertex_rows.append(dict(vertex=v,exactIdealXYZ=ip,actualPackedXYZ=ap,exactPackingDeltaXYZ=tuple(ap[k]-ip[k]for k in range(3)),ancestorBoundaryCorrespondences=boundary))
  er=[]
  for e in range(3):
   u,v=ideal[i][e],ideal[i][(e+1)%3];a,b=actual[i][e],actual[i][(e+1)%3];pk=key(xz(a),xz(b));mates=edgesXZ[key(xz(u),xz(v))]
   er.append(dict(edge=e,exactIdealXYZ=[u,v],actualPackedXYZ=[a,b],allExactIdeal3DEdgeIncidents=edges3[key(u,v)],allExactIdealProjectedEdgeIncidents=mates,allActualPackedProjectedEdgeIncidents=packedXZ[pk],idealProjectedMatesWithDifferentPackedEdges=[q for q in mates if key(xz(actual[q['candidateFace']][q['edge']]),xz(actual[q['candidateFace']][(q['edge']+1)%3]))!=pk],oneSidedEdgeIsNotAutomaticHold=True,projectedCoincidenceDoesNotProve3DMount=True))
  candidates.append(dict(candidateFace=i,provenanceVerbatim=p,completeAncestorTriplets=ancestors,completeVertices=vertex_rows,completeEdges=er));pulse()
 ideal_boxes=[(tuple(min(p[k]for p in t)for k in [0,2]),tuple(max(p[k]for p in t)for k in [0,2]))for t in ideal]
 gap_rows=[];cache={}
 for r in attribution['rows']:
  coverage=r['exactSavedCoverageVerbatim'];sig=(r['sourceFaceSHA256'],json.dumps(coverage,sort_keys=True),tuple(g['actualDrawFace']for g in r['selectedGroundProvenance']))
  if sig not in cache:
   intervals=[]
   if coverage['method']=='closed-facet-interval-union':
    pts=[xz(q)for q in exact(r['unchangedSourceXYZ'])];pairs=[(p,q)for p in pts for q in pts];a,b=max(pairs,key=lambda pq:sum((pq[0][k]-pq[1][k])**2 for k in range(2)));assert a!=b
    gaps=coverage['firstExactParameterGaps'];tail=not gaps and F(coverage['exactCoveredParameterThrough'])<1
    if tail:gaps=[[coverage['exactCoveredParameterThrough'],'1']]
    for lo,hi in gaps:
     lo,hi=F(lo),F(hi);assert 0<=lo<hi<=1;t=(lo+hi)/2;point=tuple(a[k]+t*(b[k]-a[k])for k in range(2))
     local=sorted({m['provenance']['candidateFace']for g in r['selectedGroundProvenance']for m in g['allExactCandidateFaceOrigins']})
     ideal_nominated=[j for j,(lo_box,hi_box)in enumerate(ideal_boxes)if all(lo_box[k]<=point[k]<=hi_box[k]for k in range(2))]
     intervals.append(dict(savedGapParameters=[lo,hi],tailGapFromSavedFinalReach=tail,exactLongestProjectedPair=[a,b],exactSavedGapMidpointXZ=point,complete11575IdealClosedBoundsNominees=ideal_nominated,idealFragmentPointMembershipCandidates=[j for j in ideal_nominated if inside_projected_point(point,ideal[j])],packedFragmentPointMembershipWithinSavedSelectedDrawOrigins=[j for j in local if inside_projected_point(point,actual[j])],savedWholeActualGroundCoverageNegativeRetained=True,pointMembershipOnlyNotWholeFacetProof=True))
   cache[sig]=dict(savedCoverageVerbatim=coverage,savedFirstIntervalGapAttribution=intervals,areaGapPolygonCoordinatesNotSaved=coverage['method']=='closed-facet-area-union',noInventedAreaGapLocation=True)
  gap_rows.append(dict(uid=r['uid'],mode=r['mode'],sourceFace=r['sourceFace'],sourceFaceSHA256=r['sourceFaceSHA256'],completeSavedSourceRecordVerbatim=r,localGapAttribution=cache[sig],allPriorNegativesRetained=True));pulse()
 DOC.mkdir(parents=True);save(DOC/'complete-saved-failures-packed-ancestor-boundary-attribution.json.gz',serial(dict(rows=gap_rows,relevantCandidateFaces=candidates,complete11575CandidateEdgeCensus=True,allRawNegativesAndAncestorLayersRetained=True,packingRepairNotConstructed=True,conditionalRepairMechanism='Only if exact saved ideal correspondence is broken by independent packing: review shared boundary subdivision/packing across full affected fragments on unchanged ancestor surfaces; new geometry would require separate full coverage/ordinary/foreign/runtime validation.',noCoverageUnionActorRayConstructorOrAcceptanceReplay=True,physicalAccepted=False,installationApproved=False)))
 refs +=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 for q in refs:check(q);pulse()
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.CURRENT;pulse(True)
 prior.prior.module(prior.prior.FREEZER,'upton_saved_boundary_attribution_freezer').freeze(BATCH,'saved-negative-and-exact-ancestor-packing-attribution-only',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=prior.prior.OWNED+[prior.prior.SECONDARY,prior.prior.NATIVE],sourceOnly=True,completeSavedNegativeRows=357,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--attribute-saved-packed-boundaries-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 uids=prior.prior.OWNED+[prior.prior.SECONDARY,prior.prior.NATIVE,prior.prior.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-saved-boundary-attribution-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
