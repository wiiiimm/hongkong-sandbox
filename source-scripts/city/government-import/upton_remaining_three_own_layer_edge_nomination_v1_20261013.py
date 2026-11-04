"""Three remaining thin-gap own-layer edge nominations; no geometry acceptance."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,time,uuid,subprocess
import numpy as np
import upton_current_ring12_actual_production_capture_draft_v1_20261013 as capture
import upton_current_ring12_saved_actual_union_delta_draft_v1_20261013 as finite
import upton_four_foreign_gap_hanging_edges_v1_20261013 as edges
from upton_own_layer_projected_subdivision_helper_v1_20261013 import own_layer_subdivision
from sparkle_current_native_renderer_winding_20261011 import drawn_native_faces
from run import ROOT,HERE,read,save,connect,reservations
ref,check=capture.ref,capture.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-remaining-three-own-layer-edge-nomination-v1-20261013'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
TARGETS={732:1,734:2,736:1}
RECEIPTS=[(capture.DOC,'8054682423db19952e6f6de614c792245a43a601ae363b3055d0e42100a1f06d'),(finite.DOC,'c6b49de5e64e0033b086b80f97c92047db802ff0e46446e7777b65274eb78583'),(edges.DOC,'b73ec2b945ba6f2862458686a54d7eadf42948485a2d6ca0385dcbec946fdee0')]

def serial(v):
 if isinstance(v,F):return str(v)
 if isinstance(v,dict):return{k:serial(x)for k,x in v.items()}
 if isinstance(v,(list,tuple)):return[serial(x)for x in v]
 return v

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 for folder,job in RECEIPTS:assert read(folder/'result.json')['jobId']==job
 _,_,nom,raw,pv,inp=capture.load();assert raw.shape==(11577,3,3)
 patch=read(capture.DOC/'private-native-terrain-candidate.json.gz')
 previous=read(finite.DOC/'complete-actual-union-finite-delta.json.gz');assert previous['newGroundSHA256']==finite.GROUND_SHA and previous['completeNewDrawnFaces']==11605
 secondary=next(r for r in previous['actors']if r['uid']==finite.baseline.SECONDARY)
 assert len(secondary['worlds'])==4 and all(r['findings']['currentClearCandidateUnproved']==[87,205,228]for r in secondary['worlds'])
 for actor in previous['actors']:
  if actor['uid']in finite.baseline.OWNED:assert all(not r['findings']['candidateOrdinaryUnproved']for r in actor['worlds'])
 packet=read(edges.DOC/'four-foreign-gap-hanging-edge-nominations.json.gz');rows=[r for r in packet['rejectingEdgeRows']if r['candidateFace']in TARGETS]
 assert len(rows)==3 and {r['candidateFace']:r['edge']for r in rows}==TARGETS
 mapping=nom['computedCurrentRing12PreviousCandidateMapping'];protected={r['newCandidate']for r in nom['protectedWholeCurrentTripletsUnchanged']};assert len(protected)==68
 for r in rows:
  i=r['candidateFace'];p=pv[i];assert mapping[i]['newCandidateFaces']==[i]and mapping[i]['allOldRawBytesUnchanged']and p==r['provenanceVerbatim']
  assert p['kind']=='originalTIN'and p['originalFace']==49215 and p['region']=='sourceOutsideProtection'and not r['protectedTarget']and i not in protected
  aliases=r['completeInteriorSubdivisionNodes'];assert len(aliases)==3 and all(a['projectedOnlyDifferentHeightLayer']and not a['protectedWholeCurrentNodeIncident']for a in aliases)
  assert len({(a['exactIdealXYZ'][0],a['exactIdealXYZ'][2])for a in aliases})==1 and len({a['exactInteriorProjectedParameter']for a in aliases})==1
  assert len({(a['actualPackedXYZ'][0],a['actualPackedXYZ'][2])for a in aliases})==1
  for alias in aliases:
   for incident in alias['completeVertexIncidents']:
    ids=mapping[incident['candidateFace']]['newCandidateFaces'];assert len(ids)==1 and mapping[incident['candidateFace']]['allOldRawBytesUnchanged']and ids[0]not in protected and ids[0]not in TARGETS
 original=read(check(nom['originalNomination']));src=read(check(nom['originalSourceTriplets']));source=np.asarray(src['allOriginalTriplets'],dtype='<f8');assert source.shape==(122721,3,3)and finite.sha(source)==src['completeSourceSHA256']=='3ace7f401040b2109fd196c603f506d42f0238292742e528c3c46f786b2d93e6'
 assert original['wholeSourceOriginalFaceInventory'][49215]['originalFaceSHA256']==finite.sha(source[49215])
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.legacy.CURRENT
 return pins,nom,raw,pv,patch,rows,mapping,source[49215],previous,protected

def schema_only():
 p,n,r,pv,patch,rows,m,a,old,protected=load()
 return dict(passed=True,caller=ref(Path(__file__)),remainingForeignFacets=[87,205,228],targetCandidateFaces=sorted(TARGETS),completeSourceFacets=122721,originalAncestorFace=49215,threeOtherHeightAliasesPerTarget=True,oneExactSavedProjectedNodePerTarget=True,completeOldCandidateFacets=11577,protectedWholeCurrentTriplets=68,allSourceAndCurrentAndForeignObligationsRetained=True,noNewOwnYProjectedRelationPartitionPackingDBLeaseOrWorker=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,nom,raw,pv,patch,rows,mapping,ancestor,previous,protected=load()
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']
 for folder,job in RECEIPTS:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',receipt)
  refs+=[ref(folder/'result.json')]+receipt['evidenceRefs']
 for q in refs:check(q);pulse()
 drawn,_=drawn_native_faces(patch['nativeMesh']);assert drawn.shape==(11577,3,3)
 protected_points=[point for i in protected for point in pv[i].get('exactOriginalPlanePoints',raw[i].tolist())]
 outcomes=[];pieces={};alias_bindings=[];DOC.mkdir()
 for row in rows:
  i=row['candidateFace'];proof=None
  try:
   ideal=tuple(tuple(F(v)for v in point)for point in pv[i]['exactOriginalPlanePoints']);cast=np.asarray(raw[i],dtype='<f4').astype('<f8');order=[0,1,2]if drawn[i].tobytes()==cast.tobytes()else[0,2,1]
   assert drawn[i].tobytes()==cast[order].tobytes();triangle=tuple(ideal[k]for k in order)
   assert serial([triangle[row['edge']],triangle[(row['edge']+1)%3]])==row['exactIdealLongEdgeXYZ']
   aliases=row['completeInteriorSubdivisionNodes']
   for alias in aliases:
    for incident in alias['completeVertexIncidents']:
     j=mapping[incident['candidateFace']]['newCandidateFaces'][0];p=pv[j];base=tuple(tuple(F(v)for v in point)for point in p.get('exactOriginalPlanePoints',raw[j].tolist()));fcast=np.asarray(raw[j],dtype='<f4').astype('<f8');f_order=[0,1,2]if drawn[j].tobytes()==fcast.tobytes()else[0,2,1]
     assert drawn[j].tobytes()==fcast[f_order].tobytes()
     assert serial(base[f_order[incident['vertex']]])==alias['exactIdealXYZ']and serial([F(v)for v in drawn[j][incident['vertex']]])==alias['actualPackedXYZ']
     alias_bindings.append(dict(target=i,oldIncidentVerbatim=incident,newIncidentFace=j,unchangedWholeRawTripletSHA256=finite.sha(raw[j]),unchangedWholeRawTriplet=raw[j].tolist(),otherLayerIdealXYZ=alias['exactIdealXYZ'],otherLayerPackedXYZ=alias['actualPackedXYZ'],otherLayerYNotCopiedOrMoved=True))
   proof=own_layer_subdivision(triangle,raw[i][order],row['edge'],[a['exactIdealXYZ']for a in aliases],[a['actualPackedXYZ']for a in aliases],ancestor.tolist(),aliases[0]['exactInteriorProjectedParameter'],protected_target=i in protected,protected_points=protected_points)
   pieces[i]=proof['packedPieceTriplets'];outcomes.append(dict(oldCandidateFace=i,savedRejectingEdgeVerbatim=row,feasibleOwnLayerSubdivision=True,exactOwnLayerProof=proof,noOtherHeightLayerBridge=True,noCoverageOrPhysicalApproval=True))
  except (AssertionError,ValueError,KeyError)as e:outcomes.append(dict(oldCandidateFace=i,savedRejectingEdgeVerbatim=row,feasibleOwnLayerSubdivision=False,attemptedProof=proof,unresolvedReason=type(e).__name__+': '+str(e),noSnapToleranceOrOtherLayerYWaiver=True,noSourceCorruptionOrPermanentRejectionCredit=True))
  pulse()
 save(DOC/'three-own-layer-projected-subdivision-feasibility.json.gz',serial(dict(rows=outcomes,allOtherLayerVertexIncidentBindings=alias_bindings,completeFullOriginalAncestorXYZ=ancestor.tolist(),completePreviousFiniteNegatives=ref(finite.DOC/'complete-actual-union-finite-delta.json.gz'),remainingThreeWholeForeignFacetsAndAllFourWorldsHeld=True,notACompletePackedCoverageHeightMAXRuntimeProof=True,physicalAccepted=False,installationApproved=False)))
 if set(pieces)==set(TARGETS):
  candidate=[];provenance=[];new_mapping=[]
  for i,(face,p)in enumerate(zip(raw,pv)):
   ids=[]
   for part,q in enumerate(pieces.get(i,[face.tolist()])):
    value=np.asarray(q,dtype='<f8');j=len(candidate);candidate.append(value);record={**p,'candidateFace':j,'rawNominationFaceSHA256':finite.sha(value)}
    if i in TARGETS:
     result=next(r['exactOwnLayerProof']for r in outcomes if r['oldCandidateFace']==i);record.update(computedFragment=True,savedInputByteExact=False,exactOriginalPlanePoints=serial(result['exactPartitionProof']['exactPiecesXYZ'][part]),computedOwnLayerProjectedSubdivision=dict(oldCandidateFace=i,originalFace=49215,part=part,exactNodeXYZ=serial(result['exactOwnLayerNodeXYZ']),ownYOnly=True,noOtherLayerYReuse=True))
    else:assert value.tobytes()==face.tobytes()
    provenance.append(record);ids.append(j)
   new_mapping.append(dict(oldCandidateFace=i,newCandidateFaces=ids,allOldRawBytesUnchanged=i not in TARGETS));pulse()
  candidate=np.asarray(candidate,dtype='<f8');assert candidate.shape==(11580,3,3)
  kept=[]
  for r in nom['protectedWholeCurrentTripletsUnchanged']:
   ids=new_mapping[r['newCandidate']]['newCandidateFaces'];assert len(ids)==1 and candidate[ids[0]].tobytes()==raw[r['newCandidate']].tobytes();kept.append({**r,'newCandidate':ids[0]})
  for b in alias_bindings:
   old=b['newIncidentFace'];ids=new_mapping[old]['newCandidateFaces'];assert len(ids)==1 and candidate[ids[0]].tobytes()==raw[old].tobytes()
  cumulative=[{**r,'newCandidateFaces':[j for i in r['newCandidateFaces']for j in new_mapping[i]['newCandidateFaces']],'allOldRawBytesUnchanged':r['allOldRawBytesUnchanged']and not any(i in TARGETS for i in r['newCandidateFaces'])}for r in nom['completeOldNewIndexMapping']]
  output={**nom,'candidateRawPositionTriplets':candidate.tolist(),'candidateFaceProvenance':provenance,'completeOldNewIndexMapping':cumulative,'protectedWholeCurrentTripletsUnchanged':kept,'previousRing12Nomination':ref(capture.NOM_DOC/'private-source-family-subdivision-nomination.json.gz'),'computedOwnLayer11577To11580Mapping':new_mapping,'threeOwnLayerSubdivisionProofs':outcomes,'allOther11574RawTripletsUnchanged':True,'all68ProtectedLiteralTripletsUnchanged':True,'allOtherLayerVertexIncidentBindings':alias_bindings,'wholeSourceAndForeignAndCoverageFiniteSeamMAXRuntimeAcceptancePending':True,'originalBuildingGeometryPoseChanges':0,'physicalAccepted':False,'installationApproved':False}
  save(DOC/'private-own-layer-projected-edge-subdivision-nomination.json.gz',serial(output))
 for q in refs:check(q);pulse()
 refs+=[ref(p)for p in DOC.iterdir()if p.is_file()]
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.legacy.CURRENT and reservations.owns(lease)
 capture.legacy.module(capture.legacy.FREEZER,'upton_own_layer_edge_freezer').freeze(BATCH,'private-three-own-layer-projected-edge-feasibility-nomination-only',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=capture.legacy.OWNED+[capture.legacy.SECONDARY,capture.legacy.NATIVE],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--test-own-layer-projected-edge-subdivision-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 uids=capture.legacy.OWNED+[capture.legacy.SECONDARY,capture.legacy.NATIVE,capture.legacy.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-own-layer-projected-edges-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
