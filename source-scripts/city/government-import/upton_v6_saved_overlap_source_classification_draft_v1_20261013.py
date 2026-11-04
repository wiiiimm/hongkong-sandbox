"""UNEXECUTED bounded saved-area ancestor audit; no constructor or approval."""
from pathlib import Path
import json,time,uuid,sys,subprocess,collections
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
import upton_two_original_complete_mask_current_nam_enclosure_draft_v6_20261013 as prior
from upton_v6_saved_overlap_source_classification_v1_20261013 import classify,verify_complete
from upton_inherited_overlap_boundary_v1_20261012 import overlap_pair
from upton_actual_candidate_clearance_audit_v1_20261012 import candidate_surface
from upton_captured_ground_tuple_representation_v1_20261012 import adapt_captured_ground
from upton_parent_tin_regression_bookkeeping_v1_20261012 import sha
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-v6-saved-positive-area-source-ancestor-audit-v1-20261013'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LEASE=LOCAL/'reservation.json'
PREVIOUS=prior.DOC;HELPER=HERE/'upton_v6_saved_overlap_source_classification_v1_20261013.py'
TEST=HERE/'test_upton_v6_saved_overlap_source_classification_v1_20261013.py'
METHOD=PROPOSAL/'METHOD.md';VALIDATION=PROPOSAL/'helper-validation.json'
JOB='e1644ed54461d7004245bafb5efd6c9c1c270a38a704a03d9bd426a4b97ed8a8'
RESULT_SHA='4bcc511ea099f169402a0dd0d6e97a34705839882650dd7fc6bad17fb4898145'
ref,check=prior.ref,prior.check

def schema_only():
    pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
    for q in pins['codeRefs']+pins['inputRefs']:check(q)
    r=read(PREVIOUS/'result.json');assert r['jobId']==JOB and ref(PREVIOUS/'result.json')['sha256']==RESULT_SHA
    overlap=read(PREVIOUS/'new-geometry-measured-overlap-and-exact-height-attribution.json.gz')
    rows=overlap['exactMeasuredPairNominations'];assert len(rows)==66119
    assert dict(collections.Counter(q['proof']['exactProjectedDimension'] for q in rows))==dict(area=2128,line=15007,point=48984)
    assert read(PREVIOUS/'real-validator-outcome.json')['actualAssertion']=='Native terrain contains overlapping height surfaces'
    assert overlap['measured']['candidateGeometryCanonicalSHA256']=='04550a2df291612b5f37c2920f7ec0077f4efd1ae9860eec96b8b0dd692291aa'
    assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.CURRENT
    return dict(passed=True,caller=ref(Path(__file__)),method=ref(METHOD),completeSavedPairRows=66119,selectedPositiveAreaRows=2128,noDBLeaseOrNewGeometryMath=True)

def owned():
    lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists();last=time.monotonic()
    def pulse(force=False):
        nonlocal last
        if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
    schema_only();pre=read(PROPOSAL/'schema-preflight.json');assert pre['passed'] and pre['caller']==ref(Path(__file__))
    v=read(VALIDATION);assert (v['passedTests'],v['failedTests'],v['exitCode'])==(12,0,0)
    assert v['helper']==ref(HELPER) and v['test']==ref(TEST);check(v['log'])
    pins=read(PROPOSAL/'draft-pins.json');refs=pins['codeRefs']+pins['inputRefs']+[ref(Path(__file__)),ref(METHOD),ref(PROPOSAL/'draft-pins.json'),ref(VALIDATION),v['log'],ref(PROPOSAL/'schema-preflight.json')]
    r=read(PREVIOUS/'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',r)
    for q in r['evidenceRefs']+[ref(PREVIOUS/'result.json')]:check(q);refs.append(q);pulse()
    def fence():
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.CURRENT;pulse(True)
    fence();nom=read(PREVIOUS/'complete-nominations-before-guards.json.gz');overlap=read(PREVIOUS/'new-geometry-measured-overlap-and-exact-height-attribution.json.gz');patch=read(PREVIOUS/'private-native-terrain-candidate.json.gz')
    actual=candidate_surface(patch,nom['candidateFaceProvenance']);assert len(actual)==11575
    src=read(check(nom['allSourceOriginalTriplets']));source=np.asarray(src['allOriginalTriplets'],dtype='<f8')
    assert source.shape==(122721,3,3) and sha(source)==src['completeSourceSHA256']=='3ace7f401040b2109fd196c603f506d42f0238292742e528c3c46f786b2d93e6'
    attr=read(check(nom['allCurrentTriplets']));current,representation=adapt_captured_ground(attr['rows'][0],expected_faces=9214,expected_ground_sha='b4916dac0a7c911a5b20e7dde729fa9a99fca63fa01896db8380523e6158670a',expected_source_counts=[('3d-viewer/city/data/terrain.json',32),('3d-viewer/city/data/government-native-79882-0.json',9182)])
    source_inv=nom['wholeSourceOriginalFaceInventory'];current_inv=nom['wholeCurrentFaceInventory'];assert len(source_inv)==122721 and len(current_inv)==9214
    current_attribution=read(PREVIOUS/'packed-source-current-before-compatibility.json.gz')['completeCurrentAttribution']
    def ancestor(p):
        kind=p['kind'];assert kind in ['originalTIN','capturedCurrentRing'];i=p['originalFace'];arr,inv=(source,source_inv)if kind=='originalTIN'else(current,current_inv)
        assert type(i)is int and 0<=i<len(arr) and inv[i]['originalFace']==i and inv[i]['originalFaceSHA256']==sha(arr[i])
        if kind=='capturedCurrentRing':assert p['completeCurrentSourceAttribution']==current_attribution[i]
        return arr[i],dict(kind=kind,originalFace=i,completeSavedAncestorTriplet=arr[i].tolist(),orderedAncestorSHA256=sha(arr[i]),sourceInput=nom['allSourceOriginalTriplets']if kind=='originalTIN'else nom['allCurrentTriplets'],currentSourceAttribution=p.get('completeCurrentSourceAttribution'))
    area_rows=[q for q in overlap['exactMeasuredPairNominations']if q['proof']['exactProjectedDimension']=='area'];out=[];counts=collections.Counter();DOC.mkdir(parents=True)
    for n,q in enumerate(area_rows):
        i,j=q['leftFace'],q['rightFace'];assert q['leftProvenance']==nom['candidateFaceProvenance'][i] and q['rightProvenance']==nom['candidateFaceProvenance'][j]
        a,ar=ancestor(q['leftProvenance']);b,br=ancestor(q['rightProvenance']);comparison=overlap_pair(actual[i],actual[j],a,b)
        row=classify(q,comparison);row['completeAncestors']=[ar,br];out.append(row);counts[row['classification']]+=1;pulse()
        if (n+1)%64==0:print(json.dumps(dict(positiveAreaAncestorRows=n+1,expected=2128)),flush=True)
    proof=verify_complete(area_rows,out)
    save(DOC/'complete-2128-saved-area-pair-source-ancestor-classification.json.gz',dict(rows=out,summary=dict(counts),**proof,noNewPairSearchNoConstructorNoActorOrRayRepeat=True))
    save(DOC/'diagnostic.json.gz',dict(classification=ref(DOC/'complete-2128-saved-area-pair-source-ancestor-classification.json.gz'),candidate=ref(PREVIOUS/'private-native-terrain-candidate.json.gz'),completeCandidateCanonicalSHA256=overlap['measured']['candidateGeometryCanonicalSHA256'],all66119MeasuredNominationsPreserved=ref(PREVIOUS/'new-geometry-measured-overlap-and-exact-height-attribution.json.gz'),rawValidatorFailure=ref(PREVIOUS/'real-validator-outcome.json'),savedRingGridParentComparisonIsNotBaseParentValidatorProof=True,actualValidatorParent=ref(ROOT/'3d-viewer/city/data/terrain.json'),sampled64PairPlaneAgreementIsNotProductionSamplerAudit=True,allOtherCandidatePhysicalAndSourceObligationsRemain=True,noApprovalWritten=True,physicalAccepted=False,installationApproved=False))
    refs +=[ref(p)for p in DOC.iterdir()if p.is_file()];fence()
    prior.load_module(prior.FREEZER,'upton_bounded_ancestor_freezer').freeze(BATCH,'private-saved-positive-area-source-ancestor-diagnostic',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=prior.UIDS+[prior.NATIVE],sourceOnly=True,candidateOnly=True,completePositiveAreaRows=2128,newlyInstalled=0,physicalAccepted=False,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json')))

def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
    if '--owned'in sys.argv:return owned()
    assert '--classify-saved-positive-area-ancestors-only'in sys.argv and not DOC.exists() and not LOCAL.exists()
    uids=prior.UIDS+[prior.SECONDARY,prior.NATIVE,prior.FOREIGN]
    resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
    claim=reservations.claim('upton-v6-area-ancestors-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
