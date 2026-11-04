"""Bounded sixteen-pair source ancestor diagnostic; no MAX, metadata or approval."""
from pathlib import Path
import json,sys,time,uuid,subprocess,collections
import numpy as np
import upton_three_own_layer_actual_production_capture_draft_v1_20261013 as capture
import upton_current_ring12_actual_production_capture_draft_v1_20261013 as old_capture
import upton_current_ring12_changed_area_pair_ancestor_draft_v1_20261013 as previous_pairs
from upton_actual_candidate_clearance_audit_v1_20261012 import candidate_surface
from upton_whole_current_facet_protection_v1_20261012 import exact_overlap_attribution
from upton_inherited_overlap_boundary_v1_20261012 import overlap_pair
from upton_v6_saved_overlap_source_classification_v1_20261013 import classify
from upton_captured_ground_tuple_representation_v1_20261012 import adapt_captured_ground
from upton_parent_tin_regression_bookkeeping_v1_20261012 import sha
from run import ROOT,HERE,read,save,connect,reservations
ref,check=capture.ref,capture.check
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-three-own-layer-changed-area-pair-ancestor-v1-20261013'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
GEOMETRY='259c7833fa18c53105353229fe892f0610bdb87fd44ddf86edf032c09a07d792'
RECEIPTS=[(capture.DOC,'e75d2f586b7a86fa6b4094fbfb53d70951b45c3f9420bcad0abd228b7111bbd2'),(previous_pairs.DOC,'168154b4c8c1994c061124649d2c8df1daf4aba6269bfec973be706ee8b37444')]
CHANGED=[[732,744],[732,7464],[732,7465],[732,10172],[733,744],[733,7464],[733,7465],[733,10172],[735,744],[735,10172],[736,744],[736,10172],[737,738],[737,739],[738,739],[739,10172]]
TESTS=['test_upton_v6_saved_overlap_source_classification_v1_20261013.py','test_upton_inherited_overlap_boundary_v1_20261012.py','test_upton_whole_current_facet_protection_v1_20261012.py']

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 for folder,job in RECEIPTS:assert read(folder/'result.json')['jobId']==job
 _,_,nom,raw,pv,inp=capture.load()
 patch=read(capture.DOC/'private-native-terrain-candidate.json.gz');assert previous_pairs.old_pairs.previous.canonical(patch)==GEOMETRY
 actual=candidate_surface(patch,pv);assert actual.shape==(11580,3,3)
 measured=read(capture.DOC/'new-scoped-geometry-measured-overlap.json.gz')['measured'];assert measured['candidateGeometryCanonicalSHA256']==GEOMETRY
 new_area=[r for r in measured['allProjectedIntersectingPairs']if r['projectedDimension']=='area'];assert len(new_area)==2141
 assert len({(r['leftFace'],r['rightFace'])for r in new_area})==2141
 prior=read(old_capture.NOM_DOC/'private-source-family-subdivision-nomination.json.gz');old_raw=np.asarray(prior['candidateRawPositionTriplets'],dtype='<f8');old_pv=prior['candidateFaceProvenance']
 old_actual=candidate_surface(read(old_capture.DOC/'private-native-terrain-candidate.json.gz'),old_pv)
 correspondence=read(previous_pairs.DOC/'complete2130-saved-area-pair-source-ancestor-diagnostic.json.gz');assert correspondence['completeSavedPositiveAreaPairs']==len(correspondence['rows'])==2130 and correspondence['unresolvedRows']==0
 old_measured=read(old_capture.DOC/'new-scoped-geometry-measured-overlap.json.gz')['measured']
 old_area={(r['leftFace'],r['rightFace']):r for r in old_measured['allProjectedIntersectingPairs']if r['projectedDimension']=='area'}
 old_records={(r['newSavedMeasuredPairVerbatim']['leftFace'],r['newSavedMeasuredPairVerbatim']['rightFace']):r for r in correspondence['rows']};assert len(old_records)==2130 and set(old_records)==set(old_area)
 assert old_raw.shape==(11577,3,3)and old_actual.shape==(11577,3,3)
 assert nom['previousRing12Nomination']==ref(old_capture.NOM_DOC/'private-source-family-subdivision-nomination.json.gz')
 original=read(check(nom['originalNomination']));assert nom['originalNomination']==prior['originalNomination']and nom['originalSourceTriplets']==original['allSourceOriginalTriplets']
 source_input=read(check(original['allSourceOriginalTriplets']));source=np.asarray(source_input['allOriginalTriplets'],dtype='<f8')
 assert source.shape==(122721,3,3)and sha(source)==source_input['completeSourceSHA256']=='3ace7f401040b2109fd196c603f506d42f0238292742e528c3c46f786b2d93e6'
 attr=read(check(original['allCurrentTriplets']));current,representation=adapt_captured_ground(attr['rows'][0],expected_faces=9214,expected_ground_sha='b4916dac0a7c911a5b20e7dde729fa9a99fca63fa01896db8380523e6158670a',expected_source_counts=[('3d-viewer/city/data/terrain.json',32),('3d-viewer/city/data/government-native-79882-0.json',9182)])
 si,ci=original['wholeSourceOriginalFaceInventory'],original['wholeCurrentFaceInventory']
 assert len(si)==len(source)and len(ci)==len(current)
 for arr,inv in [(source,si),(current,ci)]:
  for i,r in enumerate(inv):assert r['originalFace']==i and r['originalFaceSHA256']==sha(arr[i])and r['completeOriginalTripletRetainedInSavedInput']
 attribution=read(capture.V6/'packed-source-current-before-compatibility.json.gz')['completeCurrentAttribution'];assert len(attribution)==9214
 for i,r in enumerate(attribution):assert r['globalCurrentFace']==i and r['globalOrderedSavedFaceSHA256']==sha(current[i])
 def ancestor(p):
  kind=p['kind'];assert kind in ['originalTIN','capturedCurrentRing'];i=p['originalFace'];assert type(i)is int
  arr,inv=(source,si)if kind=='originalTIN'else(current,ci);assert 0<=i<len(arr)and inv[i]['originalFaceSHA256']==sha(arr[i])
  if kind=='capturedCurrentRing':assert p['completeCurrentSourceAttribution']==attribution[i]
  return arr[i],dict(kind=kind,originalFace=i,completeSavedAncestorTriplet=arr[i].tolist(),orderedAncestorSHA256=sha(arr[i]),sourceInput=original['allSourceOriginalTriplets']if kind=='originalTIN'else original['allCurrentTriplets'],currentSourceAttribution=p.get('completeCurrentSourceAttribution'))
 inverse={j:r['oldCandidateFace']for r in nom['computedOwnLayer11577To11580Mapping']for j in r['newCandidateFaces']};assert set(inverse)==set(range(11580))
 rows=[];changed=[];seen=set();failures=[]
 for r in new_area:
  a,b=r['leftFace'],r['rightFace'];assert a<b and r['leftProvenance']==pv[a]and r['rightProvenance']==pv[b]
  aa,ar=ancestor(pv[a]);bb,br=ancestor(pv[b]);ancestors=[ar,br]
  if inverse[a] in {732,734,736} or inverse[b] in {732,734,736}:
   changed.append(dict(newSavedMeasuredPairVerbatim=r,completeAncestors=ancestors));continue
  i,j=inverse[a],inverse[b];key=(i,j)
  try:
   assert key in old_records and key not in seen
   saved=old_records[key];assert saved['newSavedMeasuredPairVerbatim']==old_area[key]and saved['noCopiedApproval']and not saved['physicalAccepted']and not saved['installationApproved']
   assert raw[a].tobytes()==old_raw[i].tobytes()and raw[b].tobytes()==old_raw[j].tobytes()
   assert actual[a].tobytes()==old_actual[i].tobytes()and actual[b].tobytes()==old_actual[j].tobytes()
   assert raw[a].astype('<f4').tobytes()==old_raw[i].astype('<f4').tobytes()and raw[b].astype('<f4').tobytes()==old_raw[j].astype('<f4').tobytes()
   assert pv[a]=={**old_pv[i],'candidateFace':a}and pv[b]=={**old_pv[j],'candidateFace':b}
   old_class=saved.get('freshSourceAncestorClassification',saved.get('oldSourceAncestorClassificationVerbatim'));assert old_class is not None;assert ancestors==old_class['completeAncestors']and old_class['noCopiedApproval']and not old_class['physicalAccepted']and not old_class['installationApproved']
   normalized={**r,'leftFace':i,'rightFace':j,'leftProvenance':old_pv[i],'rightProvenance':old_pv[j]};assert normalized==old_area[key]
   seen.add(key);rows.append(dict(newSavedMeasuredPairVerbatim=r,completeAncestors=ancestors,oldSourceAncestorClassificationVerbatim=old_class,completePreviousPairCorrespondenceVerbatim=saved,previousCandidateFaces=[i,j],bothRawAndFloat32TripletsExactlyEqual=True,completeAncestorArraysExactlyEqual=True,oldLabelsRemainOldGeometryContext=True,noOldKernelHashOrApprovalRelabelling=True,noCopiedApproval=True,physicalAccepted=False,installationApproved=False))
  except (AssertionError,KeyError)as e:
   failures.append(dict(newSavedMeasuredPairVerbatim=r,completeAncestors=ancestors,previousCandidateFaces=[i,j],reason='Exact complete pair/raw/Float32/provenance/ancestor correspondence failed: '+str(e),unresolved=True,noAcceptanceCredit=True))
 assert [[r['newSavedMeasuredPairVerbatim']['leftFace'],r['newSavedMeasuredPairVerbatim']['rightFace']]for r in changed]==CHANGED
 assert len(rows)+len(failures)==2125 and len(changed)==16
 unresolved_old=[old_records[k]for k in sorted(set(old_records)-seen)]
 assert len(unresolved_old)==5+len(failures)
 for i,part in [(738,0),(739,1)]:
  p=pv[i];line=p['computedOwnLayerProjectedSubdivision'];assert p['kind']=='originalTIN'and p['originalFace']==49215 and line['oldCandidateFace']==736 and line['originalFace']==49215 and line['part']==part and line['ownYOnly']and line['noOtherLayerYReuse']
 assert pv[738]['computedOwnLayerProjectedSubdivision']['exactNodeXYZ']==pv[739]['computedOwnLayerProjectedSubdivision']['exactNodeXYZ']
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.legacy.CURRENT
 return pins,nom,raw,actual,new_area,rows,changed,failures,unresolved_old,ancestor,representation

def schema_only():
 p,n,r,a,area,reused,changed,failures,old,ancestor,representation=load()
 return dict(passed=True,caller=ref(Path(__file__)),completeNewSavedAreaPairs=len(area),eligibleExactPairAncestorReuse=len(reused),freshChangedPairNominations=len(changed),unresolvedReuseCorrespondences=len(failures),oldUnconsumedHistoricalPairs=len(old),completeSourceFacets=122721,completeCurrentFacets=9214,sibling738739SameSource49215OwnLayer736Parts01=True,geometryCanonicalSHA256=GEOMETRY,noExactPairOrAncestorCalculationDBLeaseOrWorker=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>15:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,nom,raw,actual,area,reused,changed,failures,old,ancestor,representation=load()
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']
 for folder,job in RECEIPTS:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',receipt)
  refs+=[ref(folder/'result.json')]+receipt['evidenceRefs']
 for q in refs:check(q);pulse()
 fresh=[];unresolved=[];DOC.mkdir(parents=True)
 for row in changed:
  r=row['newSavedMeasuredPairVerbatim'];a,b=r['leftFace'],r['rightFace'];aa,ar=ancestor(nom['candidateFaceProvenance'][a]);bb,br=ancestor(nom['candidateFaceProvenance'][b])
  proof=comparison=raw_proof=raw_comparison=None
  try:
   raw_proof=exact_overlap_attribution(raw[a],raw[b],aa,bb)
   raw_comparison=overlap_pair(raw[a],raw[b],aa,bb)
   proof=exact_overlap_attribution(actual[a],actual[b],aa,bb)
   comparison=overlap_pair(actual[a],actual[b],aa,bb)
   pair=dict(leftFace=a,rightFace=b,leftProvenance=r['leftProvenance'],rightProvenance=r['rightProvenance'],measuredProjectedDimension=r['projectedDimension'],proof=proof)
   result=classify(pair,comparison);result['completeAncestors']=[ar,br]
   fresh.append(dict(newSavedMeasuredPairVerbatim=r,freshSourceAncestorClassification=result,freshRawExactPairProof=raw_proof,freshRawAncestorComparison=raw_comparison,rawAndFloat32AreSeparateExactRepresentations=True,allExactKernelsUnchanged=True,noCopiedApproval=True,physicalAccepted=False,installationApproved=False))
  except (AssertionError,KeyError,ValueError)as e:
   unresolved.append(dict(**row,freshExactPairProof=proof,freshAncestorComparison=comparison,freshRawExactPairProof=raw_proof,freshRawAncestorComparison=raw_comparison,measuredAreaNeverOverridesExactDimension=True,reason=type(e).__name__+': '+str(e),unresolved=True,noCopiedApproval=True,physicalAccepted=False,installationApproved=False))
  pulse()
 by_pair=lambda r:(r['newSavedMeasuredPairVerbatim']['leftFace'],r['newSavedMeasuredPairVerbatim']['rightFace'])
 complete={by_pair(r):r for r in reused+failures+fresh+unresolved};expected=[(r['leftFace'],r['rightFace'])for r in area]
 assert len(complete)==len(expected)==2141 and set(complete)==set(expected)
 save(DOC/'complete2141-saved-area-pair-source-ancestor-diagnostic.json.gz',dict(rows=[complete[k]for k in expected],completeSavedPositiveAreaPairs=2141,exactUnchangedPairReuse=len(reused),freshChangedPairProofs=len(fresh),unresolvedRows=len(failures)+len(unresolved),oldUnconsumedHistoricalPairContexts=old,previousHistoricalPairContextsVerbatim=read(previous_pairs.DOC/'complete2130-saved-area-pair-source-ancestor-diagnostic.json.gz')['oldUnconsumedHistoricalPairContexts'],completeSourceFacets=122721,completeCurrentFacets=9214,currentRepresentation=representation,noNewAllPairsSearch=True,noOldKernelHashOrApprovalRelabelling=True,noApprovalWritten=True,physicalAccepted=False,installationApproved=False))
 sibling=complete[(738,739)];save(DOC/'sibling738-739-exact-diagnostic.json.gz',dict(completePairDiagnostic=sibling,nominationOnlyUntilExactPredicatesPass=True,noTinyAreaWaiver=True,noSourceOverlapApproval=True))
 save(DOC/'diagnostic.json.gz',dict(candidate=ref(capture.DOC/'private-native-terrain-candidate.json.gz'),newGeometryCanonicalSHA256=GEOMETRY,completeSavedMeasuredPairs=ref(capture.DOC/'new-scoped-geometry-measured-overlap.json.gz'),onlySixteenChangedPairCalculations=True,rawAndFloat32ExactRepresentationsSeparate=True,noMAXRayValidatorOrMetadataApproval=True,noPhysicalOrInstallationApproval=True,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.iterdir()if p.is_file()]
 for q in refs:check(q);pulse()
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.legacy.CURRENT and reservations.owns(lease)
 capture.legacy.module(capture.legacy.FREEZER,'upton_three_own_layer_changed_pair_freezer').freeze(BATCH,'private-three-own-layer-bounded-sixteen-area-pair-source-ancestor-diagnostic',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=capture.legacy.OWNED+[capture.legacy.SECONDARY,capture.legacy.NATIVE],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--classify-saved-three-own-layer-sixteen-area-pairs-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 uids=capture.legacy.OWNED+[capture.legacy.SECONDARY,capture.legacy.NATIVE,capture.legacy.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-three-own-layer-sixteen-area-ancestors-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
