"""Bind proven retained-basic support and complete model-only physical evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,jobs
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from finite_height_clearance_bound_v1_20261023 import verify as finite_bound


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-two-basic-supported-physical-review-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime='government-xl-two-basic-supported-current-capture-v1-20261023';selection=take(runtime,base/runtime/'selection.json.gz');sourceby={r['uid']:r for r in selection['rows']};sources={u:r['sourceSHA256']for u,r in sourceby.items()}
    finite='government-xl-two-basic-supported-four-world-finite-v1-20261023';q=take(finite,base/finite/'summary.json');assert q['wholeSourceFiniteClearancePassed']and q['allCanonicalBasicSupportModesPassed'];modes=take(finite,base/finite/'mode-inputs.json.gz')['rows'];checks=take(finite,base/finite/'mode-checks.json.gz')['rows'];assert len(checks)==8and all(r['proof']['passed']and not r['proof']['unresolved']for r in checks)
    scope='government-xl-two-basic-supported-current-model-scope-v1-20261023';sc=take(scope,base/scope/'summary.json');assert all(not r['nearbyNativeActors']for r in sc['rows'])
    foreign='government-xl-two-basic-supported-current-foreign-contacts-v1-20261023';f=take(foreign,base/foreign/'summary.json');assert f['foreignPairs']==3and all(m['positiveContactPairs']==0and m['projectedOverlapAreaM2']==0for r in f['rows']for m in r['modes'])
    identity='government-xl-remaining-178-v3-current-scene-v1-20261023-chunk-03-identity';identity_proofs={}
    metrics=take(runtime,base/runtime/'metrics.json');policy=module('basic_supported_ordinary_policy',HERE/'acceptance-policy.py')
    bindings=[];support_clearance=[]
    basic='government-xl-remaining-current-basic-podium-contacts-v1-20261023';basic_rows={r['uid']:r for r in take(basic,base/basic/'checks.json.gz')['rows']}
    for uid,row in sourceby.items():
        proof=take(identity,base/identity/uid.split('/')[1]/'identity.json');assert proof['passed']and proof['sourceSHA256']==sources[uid];assert all(proof['proof'][k]for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']);identity_proofs[uid]=proof['proof']
        metric=next(r for r in metrics['rows']if r['uid']==uid);reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=sources[uid],identityProof=proof['proof']),metric,metrics['profiles']['mobile']);assert reasons==['ground-contact-unresolved'],(uid,reasons)
        basic_row=basic_rows[uid];assert basic_row['usableBasicSupportDiagnostic'];support=basic_row['supportForm'];payload=next(r for r in modes if r['uid']==uid)
        for mode in payload['modes']:
            bound=finite_bound(mode['geometry']['position'],payload['supportGeometry']['position']);assert bound['ordinaryClearanceBoundProved'];support_clearance.append(dict(uid=uid,mode=mode['mode'],**bound))
        bindings.append(dict(uid=uid,supportUid=basic_row['supportUid'],supportCSUID=support['buildingCSUID'],dependencyMode='retained-current-basic-podium',currentBasicForm=support,currentBasicFormSHA256=digest(jobs.encode(support).encode()),completeIndexedBasicGeometrySHA256=digest(jobs.encode(payload['supportGeometry']).encode()),supportEvidence=dict(path=str((base/basic/'checks.json.gz').relative_to(ROOT)),sha256=digest((base/basic/'checks.json.gz').read_bytes())),sourceSHA256=sources[uid],mustRemainBasicAndUnsuppressed=True,futureReplacementRequiresDependentRevalidation=True))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==sc['currentManifestSHA256'];refs.append(manifest)
    resources=sorted({'building:'+u for u in sources}|{'building:'+r['supportUid']for r in bindings}|{'building:'+form['building']['uid']for r in sc['rows']for form in take(scope,base/scope/(r['uid'].split('/')[1]+'-forms.json.gz'))})
    review=dict(uids=list(sources),sourceSHA256ByUid=sources,sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldSourceClearance=True,completeFourWorldCanonicalRetainedBasicSupport=True,completeCurrentNeighbourChecks=sum(r['currentFormsWithinTwoMetreRegion']for r in sc['rows']),identityProof={k:all(v[k]for v in identity_proofs.values())for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},identityProofByUid=identity_proofs,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),retainedCurrentBasicSupportUids=[r['supportUid']for r in bindings],retainedBasicSupportDependencies=bindings,leaseResources=resources,terrainEdits=False,sourceGeometryChanges=0,installationApproved=False,visualAcceptance=False,publication=False,qualification='Original towers retain their exact current basic podiums. All4world contact and complete finite terrain/support clearance prove physical support without a ground-contact waiver, source translation or terrain edit. Exact foreign surfaces/projected overlap are clear, all6861nativebounds are disjoint. Raw floating-plane false negatives remain archived. Future support replacement/suppression must revalidate dependent originals; final dependency guard and staged/live visual/picking/collision/failure evidence are still required.')
    save(out/'support-clearance.json',support_clearance);save(out/'ROOT-PHYSICAL-REVIEW.json',review);refs.extend([HERE/'finite_height_clearance_bound_v1_20261023.py',HERE/'acceptance-policy.py']);module('two_basic_physical_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'two-model-only-originals-retained-basic-physical-review',refs,review);print(dict(sources=2,neighbourForms=review['completeCurrentNeighbourChecks'],terrainEdits=False),flush=True)

if __name__=='__main__':main()
