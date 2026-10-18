"""Stage four unchanged originals and their reviewed single-parent terrain."""
from pathlib import Path
import shutil
import sys
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-nobhill-qualified-stage-v1-20261018'
DOC = BASE / BATCH
STAGE = HERE / 'accepted' / BATCH
REVIEW = BASE / 'government-xl-nobhill-source-review-v1-20261018'

def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))

def check(item):
    assert ref(ROOT / item['path']) == item, item['path']

def main():
    assert not DOC.exists() and not STAGE.exists()
    result = read(REVIEW / 'result.json')
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone() == ('complete', result)
    pins = {}
    for item in result['evidenceRefs']:
        assert item['path'] not in pins or pins[item['path']] == item
        pins[item['path']] = item
    for item in pins.values(): check(item)
    decision = read(REVIEW / 'ROOT-SOURCE-REVIEW.json')
    assert decision['originalSourceReviewAccepted']
    roster = {row['uid']:row for row in read(ROOT / decision['identityRoster']['path'])['models']}
    old = HERE / 'local/government-xl-nobhill-browser-1280-v1-20261018'
    catalogue = read(old / 'catalogue.json')
    assert len(catalogue['models']) == 4
    for entry in catalogue['models']:
        uid = entry['uid']
        assert entry['sha256'] == roster[uid]['sourceSHA256'] == decision['sourceSHA256ByUid'][uid]
        assert not entry.get('suppressesBuildingUids')
        assert [dep['uid'] for dep in entry['supportDependencies']] == decision['supportDependencies'].get(uid, [])
        entry.update(sourceIdentityReviewed=True, identityReviewApproved=True, placementReviewed=True,
                     publicationApproved=True, proceduralWindows=False, originalSourceKey=roster[uid]['sourceKey'],
                     sourceIdentityReview=ref(REVIEW/'ROOT-SOURCE-REVIEW.json'),
                     sourceFunctionalApplicability=ref(REVIEW/'ROOT-SOURCE-REVIEW.json'),
                     sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
                     placementReview='Exact original 1x source; source-specific identity, lower-interface and original-grade reviews; all four-coordinate foundations and current neighbours; desktop/mobile support residency, picking, collision and visible fallback checked.')
        # All providers are co-published in this exact reviewed assembly.
        for dep in entry['supportDependencies']:
            assert dep['sha256'] == roster[dep['uid']]['sourceSHA256']
            dep['state'] = 'installed'
        target = STAGE / entry['asset']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(old / entry['asset'], target)
        assert digest(target.read_bytes()) == entry['sha256']
    save(STAGE/'catalogue.json', catalogue)
    save(STAGE/'catalogue-index.json', dict(models=4,catalogues=['catalogue.json']))
    shutil.copyfile(old/'source-forms.json', STAGE/'source-forms.json')
    candidate = decision['terrainCandidate']
    check(dict(path=candidate['path'],sha256=candidate['sha256']))
    terrain_file = STAGE/'government-nobhill-original-v1-20261018.json'
    shutil.copyfile(ROOT/candidate['path'],terrain_file)
    terrain = dict(source=str(terrain_file.relative_to(ROOT)),sha256=candidate['sha256'],
                   destination='city/data/'+terrain_file.name,resolution=5,
                   area='Nob Hill original terrain')
    scope_path = BASE/'government-xl-nobhill98845-native-scope-v1-20261018/scope.json'
    scope = read(scope_path)
    assert scope['allCurrentActorsNominated'] and scope['touchingNativeUids'] == []
    assert not candidate.get('replaces') and not candidate.get('replacesMany')
    save(DOC/'reviewed-native-neighbour-checks.json',dict(rows=[],completeCurrentScope=ref(scope_path),sourceReview=ref(REVIEW/'ROOT-SOURCE-REVIEW.json'),qualification='All current installed actors have complete four-world bounds disjoint from the changed parent extent.'))
    url = 'city/data/official-models/'+BATCH+'/catalogue.json'
    save(STAGE/'plan.json',dict(areas=[dict(area='Nob Hill four unchanged originals',
         catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)],topLevelTerrainPatches=[terrain]))
    config = read(old/'browser-config.json')
    config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url,terrain=[terrain])
    save(STAGE/'browser-config.json',config)
    save(DOC/'qualification.json',dict(privateStageQualified=True,sourceSHA256ByUid=decision['sourceSHA256ByUid'],
         currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),sourceReviews=[ref(REVIEW/'ROOT-SOURCE-REVIEW.json')],
         noTerrainChange=False,terrainCandidate=terrain,publication=False))
    pub = module('olympian_stage_publisher',HERE.parent/'island-detail-integration/publish.py')
    pub.DOC = DOC/'publisher-dry-run'
    sys.argv = ['publish.py',str((STAGE/'plan.json').relative_to(ROOT))]
    pub.main()
    assert not read(pub.DOC/'publication-plan.json')['published']
    for item in pins.values(): check(item)
    result = module('olympian_stage_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'park-avenue-four-qualified-original-stage-v1',
        [Path(__file__),REVIEW/'result.json',
         *[ROOT/path for path in pins],*[path for path in STAGE.rglob('*') if path.is_file()]],
        dict(uids=list(roster),privateStageQualified=True,publisherDryRunPassed=True,publication=False))
    print(result['jobId'],flush=True)

if __name__ == '__main__':
    main()
