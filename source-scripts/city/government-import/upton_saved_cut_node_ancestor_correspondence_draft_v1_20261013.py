"""UNEXECUTED two-edge saved cut-node attribution; no packing repair or union replay."""
from pathlib import Path
from collections import defaultdict
from fractions import Fraction as F
import sys,json,time,uuid,subprocess
import numpy as np
import upton_saved_hanging_subdivision_investigation_draft_v1_20261013 as prior
from upton_two_original_six_mask_partition_v1_20261012 import mask
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import projected_mask
from run import ROOT,HERE,read,save,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-saved-cut-node-ancestor-correspondence-v1-20261013'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JOB='9c99aebc039537788fde09021ce0f7987ae6f21a4d151156d832866eb70e61f1'
ref,check=prior.ref,prior.check
exact,serial,xz,segment_parameter,inside=prior.prior.exact,prior.prior.serial,prior.prior.xz,prior.prior.segment_parameter,prior.prior.inside_projected_point
def plane_residual(p,t):
 a,b,c=t;u=tuple(b[k]-a[k]for k in range(3));v=tuple(c[k]-a[k]for k in range(3))
 n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
 return dict(exactUnnormalisedNormal=n,exactSignedPlaneResidual=sum(n[k]*(p[k]-a[k])for k in range(3)),exactDegenerate=n==(0,0,0),noHeightOrRoleCredit=True)
def triangle_sides(p,t):
 return prior.oriented_sides(p,t)
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 receipt=read(prior.DOC/'result.json');assert receipt['jobId']==JOB
 output=read(prior.DOC/'complete-saved-gap-hanging-subdivision-investigation.json.gz')
 rows=output['rejectingLongEdgeRows'];assert [(r['candidateFace'],r['edge'])for r in rows]==[(381,0),(382,0)]
 assert all(not r['completeInteriorSubdivisionNodes']and r['provenanceVerbatim']['originalFace']==35677 for r in rows)
 ends=[{tuple(F(v)for v in p)for p in r['exactIdealLongEdgeXYZ']}for r in rows];common=ends[0]&ends[1];assert len(common)==1;node=common.pop()
 _,_,_,nomination,raw,provenance,source,current,drawn,_=prior.prior.load()
 v6=prior.prior.prior.V6;envelopes=read(v6/'complete-protection-arithmetic-envelopes.json.gz');masks=[];mask_origins=defaultdict(list)
 for e in envelopes['envelopes']:
  assert len(e['envelopeMaskIDs'])==len(e['exactEnvelopeTriangles'])
  for i,t in zip(e['envelopeMaskIDs'],e['exactEnvelopeTriangles']):
   t=[tuple(F(v)for v in p)for p in t];assert prior.prior.cross(t[0],t[1],t[2])>0
   if i==len(masks):masks.append(t)
   else:assert 0<=i<len(masks)and set(t)==set(masks[i])
   mask_origins[i].append(dict(kind='savedArithmeticEnvelope',origin=e['origin'],envelopeVerbatim=e))
 for q in envelopes['wholeNativeSelected']:
  i=len(masks);masks.append(projected_mask(current[q['currentFace']]));mask_origins[i].append(dict(kind='wholeCurrentNativeFacetMask',selectionVerbatim=q,currentOriginalTriplet=exact(current[q['currentFace']])))
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.prior.prior.CURRENT
 return pins,receipt,output,nomination,raw,provenance,source,current,drawn,node,masks,mask_origins
def schema_only():
 p,r,o,n,raw,pv,s,c,d,node,masks,origins=load()
 return dict(passed=True,caller=ref(Path(__file__)),targetEdges=[[381,0],[382,0]],ancestorTINFace=35677,cutNode=serial(node),completeCandidateFacets=11575,completeSourceFacets=122721,completeCurrentFacets=9214,savedNegativeRows=357,areaRowsUnlocated=257,reconstructedOrderedProtectionMasks=len(masks),noMathWorkerOrLease=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,receipt,out,nom,raw,pv,source,current,drawn,node,masks,mask_origins=load()
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md')]+receipt['evidenceRefs']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 for q in refs:check(q);pulse()
 ideal=[];actual=[];incidents=[]
 for i,p in enumerate(pv):
  t=tuple(tuple(F(v)for v in q)for q in p['exactOriginalPlanePoints'])if p.get('exactOriginalPlanePoints')is not None else exact(raw[i]);cast=np.asarray(raw[i],dtype=np.float32).astype('<f8')
  order=[0,1,2]if drawn[i].tobytes()==cast.tobytes()else[0,2,1];assert drawn[i].tobytes()==cast[order].tobytes();t=tuple(t[j]for j in order);a=exact(drawn[i]);ideal.append(t);actual.append(a)
  for j,ip in enumerate(t):
   if xz(ip)==xz(node):incidents.append(dict(candidateFace=i,vertex=j,exact3DNodeIncident=ip==node,projectedDifferentHeight=ip!=node,idealXYZ=ip,actualPackedXYZ=a[j],provenanceVerbatim=p,literalWholeCurrentProtected=p.get('region')=='wholeCurrentProtectionFacet'))
  if i%256==0:pulse()
 packed_nodes={tuple(r['actualPackedXYZ'])for r in incidents if r['exact3DNodeIncident']};assert len(packed_nodes)==1;packed_node=packed_nodes.pop()
 boundary=[];mask_sides=[]
 for i,m in enumerate(masks):
  old=[prior.prior.cross(a,b,xz(node))for a,b in zip(m,m[1:]+m[:1])];new=[prior.prior.cross(a,b,xz(packed_node))for a,b in zip(m,m[1:]+m[:1])]
  if all(v>=0 for v in old)or all(v>=0 for v in new)or any(v==0 for v in old):mask_sides.append(dict(mask=i,exactIdealNodeSideValues=old,actualPackedNodeAgainstIdealMaskSides=new,idealInside=all(v>=0 for v in old),packedInsideIdealMask=all(v>=0 for v in new),originsVerbatim=mask_origins[i]))
  for j,(a,b)in enumerate(zip(m,m[1:]+m[:1])):
   parameter=segment_parameter(xz(node),a,b)
   if parameter is not None:boundary.append(dict(mask=i,edge=j,exactFiniteParameter=parameter,exactMaskEdgeXZ=[a,b],originsVerbatim=mask_origins[i],packedNodeSignedSideAgainstUnchangedIdealBoundary=prior.prior.cross(a,b,xz(packed_node))))
  pulse()
 rectangle_sides=[]
 for kind,box in [('domain',nom['domain']),('core',nom['core'])]:
  for axis,lower,upper in [(0,box[0],box[2]),(2,box[1],box[3])]:
   for name,value in [('lower',F(float(lower))),('upper',F(float(upper)))]:rectangle_sides.append(dict(kind=kind,axis=axis,side=name,value=value,idealNodeSignedCoordinateDifference=node[axis]-value,actualPackedNodeSignedCoordinateDifference=packed_node[axis]-value,exactIdealBoundaryIncident=node[axis]==value))
 # Closed XZ bounds preserve projected-only source layers; exact 3D plane and
 # finite edge membership are separate. No source/ground coverage union replay.
 point=np.asarray([float(v)for v in node],dtype='<f8');lo=np.nextafter(point,-np.inf);hi=np.nextafter(point,np.inf);assert all(F(float(lo[k]))<=node[k]<=F(float(hi[k]))for k in range(3))
 lows,highs=source.min(axis=1),source.max(axis=1);broad=np.flatnonzero(np.all(highs[:,[0,2]]>=lo[[0,2]],axis=1)&np.all(lows[:,[0,2]]<=hi[[0,2]],axis=1))
 source_ids=[i for i in broad if all(F(float(lows[i,k]))<=node[k]<=F(float(highs[i,k]))for k in [0,2])];ancestor_rows=[]
 for i in source_ids:
  t=exact(source[i]);edges=[]
  for j in range(3):
   parameter=segment_parameter(node,t[j],t[(j+1)%3]);projected=segment_parameter(xz(node),xz(t[j]),xz(t[(j+1)%3]))
   if projected is not None:edges.append(dict(edge=j,exactFinite3DParameter=parameter,exactFiniteProjectedParameter=projected,originalEdgeXYZ=[t[j],t[(j+1)%3]]))
  ancestor_rows.append(dict(originalSourceFace=int(i),originalTripletSHA256=prior.prior.prior.prior.sha(source[i]),untouchedOriginalXYZ=t,exactNodeWithinOriginalXYZBounds=all(F(float(lows[i,k]))<=node[k]<=F(float(highs[i,k]))for k in range(3)),idealNodePlane=plane_residual(node,t),packedNodePlane=plane_residual(packed_node,t),finiteEdgeRelations=edges))
 source_row=next(r for r in ancestor_rows if r['originalSourceFace']==35677);assert not source_row['idealNodePlane']['exactDegenerate']and source_row['idealNodePlane']['exactSignedPlaneResidual']==0
 current_ids=[i for i,p in enumerate(pv)if p['kind']=='capturedCurrentRing'];points=[]
 saved_lookup={(r['uid'],r['mode'],r['sourceFace']):r for r in out['completeSavedFailureRowsVerbatim']}
 for r in out['intervalPointRows']:
  point=tuple(F(v)for v in r['exactSavedGapRecordVerbatim']['exactSavedGapMidpointXZ']);saved=saved_lookup[(r['uid'],r['mode'],r['sourceFace'])]['completeSavedSourceRecordVerbatim'];xyz=exact(saved['unchangedSourceXYZ'])
  ideal_masks=[i for i,m in enumerate(masks)if all(prior.prior.cross(a,b,point)>=0 for a,b in zip(m,m[1:]+m[:1]))]
  # Every complete current fragment is considered; point evidence cannot stand
  # for whole coverage or height, and different current layers remain separate.
  current_ideal=[i for i in current_ids if inside(point,ideal[i])];current_actual=[i for i in current_ids if inside(point,actual[i])]
  points.append(dict(uid=r['uid'],mode=r['mode'],sourceFace=r['sourceFace'],sourceFaceSHA256=saved['sourceFaceSHA256'],completeBoundWorldSHA256=saved['wholeWorldSHA256'],completeUnchangedSourceFacetXYZ=xyz,completeFacetClosedBoundsXYZ=[[min(p[k]for p in xyz)for k in range(3)],[max(p[k]for p in xyz)for k in range(3)]],savedCompleteFiniteProofVerbatim=saved['savedFiniteRecordVerbatim'],exactGapPointXZ=point,idealProtectionMaskMembership=ideal_masks,completeCurrentIdealPointMembership=current_ideal,completeCurrentActualPackedPointMembership=current_actual,sourceRejectingEdgesVerbatim=r['idealContainingPackedRejectingFacets'],noWholeRegionMovementHeightCoverageOrRoleClaim=True));pulse()
 area=[]
 for r in out['completeSavedFailureRowsVerbatim']:
  cov=r['localGapAttribution']['savedCoverageVerbatim']
  if cov['method']=='closed-facet-area-union':area.append(dict(uid=r['uid'],mode=r['mode'],sourceFace=r['sourceFace'],savedCoverageVerbatim=cov,availableSavedCoverageFieldNames=sorted(cov),uncoveredPolygonCoordinatesSaved=False,noLocationInvented=True))
 assert len(points)==100 and len(area)==257
 DOC.mkdir(parents=True);save(DOC/'complete-saved-cut-node-ancestor-correspondence.json.gz',serial(dict(cutNodeIdealXYZ=node,cutNodeActualPackedXYZ=packed_node,allCompleteCandidateNodeIncidents=incidents,protectionBoundaryCorrespondences=boundary,nodeProtectionSideConstraints=mask_sides,domainAndCoreCoordinateConstraints=rectangle_sides,completeClosedProjectedSourceAncestorNominees=ancestor_rows,intervalPointRows=points,areaRows=area,originalRejectingEdgeRowsVerbatim=out['rejectingLongEdgeRows'],whole68ProtectedTripletsVerbatim=out['literalWholeCurrentProtectionVerbatim'],completeAll357RawNegativesRetained=True,noRepairConstructorOrWholeCoverageReplayed=True,physicalAccepted=False,installationApproved=False)))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 for q in refs:check(q);pulse()
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.prior.prior.CURRENT;pulse(True)
 prior.prior.prior.prior.module(prior.prior.prior.prior.FREEZER,'upton_cut_node_freezer').freeze(BATCH,'saved-two-edge-cut-node-ancestor-only',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=prior.prior.prior.prior.OWNED+[prior.prior.prior.prior.SECONDARY,prior.prior.prior.prior.NATIVE],sourceOnly=True,completeSavedRows=357,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--attribute-saved-cut-node-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 uids=prior.prior.prior.prior.OWNED+[prior.prior.prior.prior.SECONDARY,prior.prior.prior.prior.NATIVE,prior.prior.prior.prior.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-cut-node-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
