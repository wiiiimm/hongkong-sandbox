"""Fail-closed qualification of the exact Star Ferry original and repaired terrain."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-star-ferry-functional-applicability-v2-20261019';DOC=BASE/BATCH
UID='landsd/210032:0';SHA='a8635ec84493ea64fa8b803bc5ea6e90f1dcd46979674e9d6d24445067491de7'
MODES={'original','literal','explicitLeftF32','explicitBalancedF32'}
ACTORS={'landsd/205767:0','landsd/209787:0','landsd/211702:0','landsd/264745:0','landsd/73140:0'}
def folder(n):return BASE/('government-xl-star-ferry-'+n+'-20261019')
def inputs():
    return dict(decision=read(folder('source-relationship-review-v2')/'ROOT-SOURCE-RELATIONSHIP-REVIEW.json'),identity=read(folder('identity-review-v1')/'210032:0-review.json'),foundations=[read(folder('four-mode-foundations-v2')/('210032:0-'+m+'.json')) for m in sorted(MODES)],attribution=read(folder('all-contact-ground-attribution-v2')/'attribution.json'),metric=read(folder('retained-wrapper-metrics-v3')/'metrics.json')['rows'][0],retained=read(folder('retained-wrapper-metrics-v3')/'retained-proof.json'),scope=read(folder('complete-neighbours-v3')/'unchanged-outside-domain.json'),neighbours=read(folder('complete-neighbours-v3')/'summary.json'),native=read(folder('complete-neighbours-v3')/'native-neighbour-checks.json'),validation=read(folder('ordinary-validation-v3')/'validation.json'))
def qualify(decision,identity,foundations,attribution,metric,retained,scope,neighbours,native,validation):
    assert decision['uid']==identity['uid']==metric['uid']==UID
    assert decision['sourceSHA256']==identity['sourceSHA256']==metric['sourceSHA256']==attribution['summary']['sourceSHA256']==SHA
    assert identity['identityOnlyApproved'] and identity['identityProof']['identityAccepted']
    assert decision['reviewer']=='Codex ROOT' and decision['originalSurveyedRelationshipAccepted']
    assert decision['rawStrictGroundContactPassed'] is False and decision['rawStrictFoundationPassed'] is True
    assert decision['geometryOrPoseChanges']==0 and not decision['installationApproved'] and not decision['publicationApproved']
    assert len(foundations)==4 and {f['mode'] for f in foundations}==MODES
    bindings=[]
    for f in foundations:
        assert f['uid']==UID and f['sourceSHA256']==SHA and f['strictFoundationAccepted']
        assert f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==42334
        assert f['foundation']['fullyBuriedTriangles']==f['foundation']['fullyBuriedUpwardTriangles']==0
        assert next(d for d in decision['checks'] if d['mode']==f['mode'])['wholeWorldSHA256']==f['wholeWorldSHA256']
        bindings.append(dict(uid=UID,mode=f['mode'],sourceSHA256=SHA,wholeWorldSHA256=f['wholeWorldSHA256']))
    rim=set(decision['lowRimFaceIds']);matched=[r for r in attribution['faces'] if r['faceId'] in rim]
    assert len(rim)==len(matched)==4332 and all(r['maximumTerrainDifferenceMetres']==0 for r in matched)
    assert not attribution['summary']['candidateFullyBuriedIds'] and not attribution['summary']['originalTerrainFullyBuriedIds']
    assert metric['sourcePreserved'] and metric['checks']==156597 and metric['missingTerrain']==0 and metric['maxSamplerDelta']==0
    assert retained['otherChildrenUnchanged']==12
    assert {r['id']:r['retainedTriangles'] for r in retained['children']}=={'government-native-central-hullett-house':10675,'government-native-205767-0':9114}
    assert all(r['missing']==0 for r in retained['children']) and scope['retainedProof']==retained
    assert set(scope['requiredNativeUids'])==set(neighbours['requiredNativeUids'])==ACTORS
    assert neighbours['forms']==38 and not neighbours['basicReasons'] and not neighbours['unresolvedNatives']
    assert set(native['blocked'])==set(native['resolved'])=={r['uid'] for r in native['rows']}==ACTORS
    assert all(r['passed'] for r in native['rows'])
    from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
    assert all(closed_disjoint(r['completeFourWorldBounds'],scope['changedExtent']) for r in scope['excludedRegionalActors'])
    assert validation['models']==validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0
    assert len(validation['results'])==1 and validation['results'][0]['uid']==UID and validation['results'][0]['concerns']==['sampled-terrain-above-model-bottom']
    return dict(uids=[UID],sourceBindings=bindings,sourceScopedApplicabilityAccepted=True,remainingPhysicalReasons=[],rawStrictGroundContactPassed=False,rawStrictFoundationPassed=True,rawNumericalFailuresRemainFailed=True,rawMetric=metric,rawDiagnosticConcerns=validation['results'][0]['concerns'],sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,publicationApproved=False,installationApproved=False,stagedAndLiveBrowserStillRequired=True,qualification='Exact original Star Ferry low-rim relationship only. All4332lowrimfaces reproduce original TIN offsets; allfourcompletefoundations and all38basic/fiveinstalled-neighbour regressions pass. Complete retained terrain facets preserved. Numerical-gap fallback changes require this fresh candidate binding and browser acceptance. No generic tolerance changes.')
def main():
    assert not DOC.exists();pins={};refs=[Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for name in ['source-relationship-review-v2','complete-neighbours-v3','retained-wrapper-metrics-v3','ordinary-validation-v3']:
            p=folder(name)/'result.json';r=read(p)
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
            for e in r['evidenceRefs']:
                assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    data=inputs();q=qualify(**data)
    policy=module('star_policy',HERE/'acceptance-policy.py');metrics=read(folder('retained-wrapper-metrics-v3')/'metrics.json')
    raw=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SHA,identityProof=data['identity']['identityProof']),data['metric'],metrics['profiles']['mobile'])
    assert set(raw)=={'terrain-intersects-source-over-0.5m'}
    q['rawPolicyReasons']=raw;save(DOC/'qualification.json',q)
    refs.extend([HERE/'acceptance-policy.py',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py'])
    module('star_functional_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'star-ferry-exact-original-functional-applicability',list(dict.fromkeys(refs)),dict(uids=[UID],sourceScopedApplicabilityAccepted=True,installationApproved=False))
if __name__=='__main__':main()
