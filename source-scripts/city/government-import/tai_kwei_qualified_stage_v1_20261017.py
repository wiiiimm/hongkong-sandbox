"""Qualify unchanged Tai Kwei only after complete original/rendered clearance; dry run only."""
from pathlib import Path
import shutil, sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-tai-kwei-qualified-stage-v1-20261017'
DOC=BASE/BATCH
STAGE=HERE/'accepted'/BATCH
UID='landsd/106413:0'
SHA='797e15e504a549f44c02b55fe11ab769dec45f27f5174c4dc6dc313a7562fe79'
SOURCES={UID:SHA}
SOURCE_KEY='adf1d085a79951ff976393a3672cda66812a6fd2482559fc4b7435331c50964b/B346442034301063C0'
FOLDERS=['complete-finite-v1','candidate-physical-v2','current-native-scope-v1','runtime-capture-v1','browser-policy-review-v1','private-terrain-v1','reviewed-identity-v1','private-browser-v2']
def folder(n):return BASE/('government-xl-tai-kwei-'+n+'-20261017')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def verify():
    pins={}
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for n in FOLDERS:
            p=folder(n)/'result.json';r=read(p)
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
            for e in r['evidenceRefs']+[ref(p)]:
                assert e['path'] not in pins or pins[e['path']]==e
                pins[e['path']]=e
    for p,e in pins.items():assert ref(ROOT/p)==e,p
    return pins

def main():
    # Fail before any output if the running finite worker has not finished.
    finite=read(folder('complete-finite-v1')/'summary.json')
    assert finite['complete'] and finite['ownAllStrict'] and finite['neighbourNoIntroducedFailures']
    assert not DOC.exists() and not STAGE.exists()
    pins=verify()
    capture=read(folder('runtime-capture-v1')/'capture-report.json.gz')
    assert capture['strictExteriorUnchanged']
    attrs=read(folder('runtime-capture-v1')/'attributes.json.gz')['rows']
    basic=read(folder('runtime-capture-v1')/'basic-actors.json.gz')['rows']
    expected={r['uid']:{'original','literal','leftF32','balancedF32'} for r in attrs}
    for r in basic:
        assert r['uid'] not in expected and r['identityArithmeticAllThreeExactlyEqual']
        expected[r['uid']]={'basicLiteralAndBothF32'}
    assert len(expected)==finite['actors']==66
    actual={}
    for r in finite['rows']:
        key=(r['uid'],r['mode']);assert key not in actual;actual[key]=r
        assert not r['uncovered']['after'] and not r['introducedUnproved']
        if r['uid']==UID:assert not r['unproved']['after'] and r['faces']==13114
    assert set(actual)=={(u,m)for u,modes in expected.items()for m in modes}
    scope=read(folder('current-native-scope-v1')/'scope.json')['touchingNativeUids']
    assert set(scope)==set(expected)-{r['uid']for r in basic}-{UID}
    phys=read(folder('candidate-physical-v2')/'result.json')
    assert phys['strictFoundationAccepted'] and not phys['basicNeighbourFailures']
    assert all(r['passed']for r in phys['installedNativeResults'])
    assert {r['uid']for r in phys['installedNativeResults']}==set(scope)
    policy=read(folder('browser-policy-review-v1')/'policy.json')
    images=read(folder('browser-policy-review-v1')/'ROOT-IMAGE-INSPECTION.json')
    assert policy['uid']==UID and policy['sourceSHA256']==SHA
    assert not policy['remainingMobilePolicyReasons'] and not policy['loaderConcerns']
    assert images['sourceGeometryAppearanceAccepted'] and images['proceduralWindows'] is False
    for e in images['imagesActuallyViewed']:assert ref(ROOT/e['path'])==e
    identity=read(folder('reviewed-identity-v1')/'identity-review.json')
    assert identity['identityReviewApproved'] and identity['sourceSHA256']==SHA
    prior=HERE/'local'/folder('private-browser-v2').name
    cat=read(prior/'catalogue.json');assert len(cat['models'])==1
    entry=cat['models'][0];assert entry['uid']==UID and entry['sha256']==SHA and entry['proceduralWindows'] is False
    candidate=read(folder('private-terrain-v1')/'terrain-candidates.json')[0]
    terrain=ROOT/candidate['path'];assert ref(terrain)['sha256']==candidate['sha256']
    old=ROOT/'3d-viewer'/candidate['replaces']['url'];assert ref(old)['sha256']==candidate['replaces']['sha256']
    patch=read(terrain)
    DOC.mkdir();STAGE.mkdir()
    qualification=dict(currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),uid=UID,sourceSHA256=SHA,sourceGeometryChanges=0,sourcePoseChanges=0,privateStageQualified=True,publication=False,completeFiniteEvidence=ref(folder('complete-finite-v1')/'result.json'),inspectedBrowserEvidence=ref(folder('browser-policy-review-v1')/'result.json'),affectedActors=66,affectedNativeUids=scope,existingNeighbourBaselineFailuresNotWaived=True)
    save(DOC/'qualification.json',qualification)
    review=dict(status='approved-for-integration',supersededURL=candidate['replaces']['url'],supersededSHA256=candidate['replaces']['sha256'],replacementSHA256=candidate['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=candidate['replaces']['retainedUids'],replacementTargetUids=patch['meta']['targetUids'],fullMeshCheck=ref(folder('candidate-physical-v2')/'native-neighbour-checks.json'),completeFiniteCheck=qualification['completeFiniteEvidence'])
    save(DOC/'native-replacement-review.json',review)
    entry.update(originalSourceKey=SOURCE_KEY,sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=ref(folder('reviewed-identity-v1')/'identity-review.json'),placementReview='Unchanged government source at 1x scale; complete original and rendered finite checks, strict foundation, all affected neighbours and desktop/mobile views passed.',sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True)
    asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True);shutil.copyfile(prior/entry['asset'],asset);assert ref(asset)['sha256']==SHA
    save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']))
    shutil.copyfile(prior/'source-forms.json',STAGE/'source-forms.json')
    dest=STAGE/'government-native-tai-kwei-original-v1-20261017.json';shutil.copyfile(terrain,dest)
    t=dict(source=str(dest.relative_to(ROOT)),sha256=ref(dest)['sha256'],destination='city/data/'+dest.name,resolution=5,area='Tai Kwei original-source terrain',replaces=candidate['replaces'],nativeReview=ref(DOC/'native-replacement-review.json'))
    url='city/data/official-models/'+BATCH+'/catalogue.json'
    save(STAGE/'plan.json',dict(areas=[dict(area='Tai Kwei unchanged original',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)],topLevelTerrainPatches=[t]))
    config=read(prior/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url,terrain=[t]);save(STAGE/'browser-config.json',config)
    pub=module('tai_kwei_existing_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main()
    assert not read(pub.DOC/'publication-plan.json')['published']
    for p,e in pins.items():assert ref(ROOT/p)==e,p
    module('tai_kwei_qualified_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'tai-kwei-qualified-original-stage-v1',[Path(__file__),*[ROOT/p for p in pins],*[p for p in STAGE.rglob('*')if p.is_file()]],dict(uids=[UID],privateStageQualified=True,publisherDryRunPassed=True,fullAcceptance=False,nextStep='Atomic installation with rollback and live desktop/mobile verification; no installed credit yet.'))
if __name__=='__main__':main()
