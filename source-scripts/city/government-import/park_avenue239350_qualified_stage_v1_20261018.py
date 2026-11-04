"""Stage six unchanged originals and their reviewed single-parent terrain."""
from pathlib import Path
import shutil
import sys
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-park-avenue239350-qualified-stage-v1-20261018'
DOC = BASE / BATCH
STAGE = HERE / 'accepted' / BATCH
REVIEW = BASE / 'government-xl-park-avenue239350-source-review-v1-20261018'

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
    old = HERE / 'local/government-xl-park-avenue239350-browser-1280-v3-20261018'
    catalogue = read(old / 'catalogue.json')
    assert len(catalogue['models']) == 6
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
    save(STAGE/'catalogue-index.json', dict(models=6,catalogues=['catalogue.json']))
    shutil.copyfile(old/'source-forms.json', STAGE/'source-forms.json')
    candidate = decision['terrainCandidate']
    check(dict(path=candidate['path'],sha256=candidate['sha256']))
    terrain_file = STAGE/'government-park-avenue239350-original-v1-20261018.json'
    shutil.copyfile(ROOT/candidate['path'],terrain_file)
    terrain = dict(source=str(terrain_file.relative_to(ROOT)),sha256=candidate['sha256'],
                   destination='city/data/'+terrain_file.name,resolution=5,
                   area='Park Avenue / Charming Garden original terrain',replaces=candidate['replaces'])
    raw_path = BASE/'government-xl-park-avenue239350-native-regression-v1-20261018/native-neighbour-checks.json'
    native = read(raw_path)
    hoi_path = BASE/'government-xl-park-avenue239350-hoi-yu-prior-review-v2-20261018/result.json'
    hoi = read(hoi_path)
    resolved = []
    for row in native['rows']:
        if row['passed']:
            resolved.append(row)
        else:
            assert row['uid'] == 'landsd/177605:0' and row == hoi['threePodiumCandidateTerrainRegression']
            assert hoi['currentSourcesAndDependencyUnchanged'] and hoi['existingExactSourceSupportReviewVerified']
            resolved.append(dict(row,passed=True,rawPassed=False,exactPriorSupportReview=ref(hoi_path),
                                 qualification='Unchanged original support acceptance; complete current terrain regression has zero newly buried faces. Raw generic support failure retained.'))
    fullcheck = DOC/'reviewed-native-neighbour-checks.json'
    save(fullcheck,dict(rows=resolved,rawReport=ref(raw_path),sourceReview=ref(REVIEW/'ROOT-SOURCE-REVIEW.json'),aiCalls=0,modelGeometryChanges=0))
    patch = read(terrain_file)
    for index, replacement in enumerate([terrain['replaces']]):
        assert set(replacement['retainedUids']) <= {row['uid'] for row in resolved}
        path = DOC/f'native-replacement-review-{index}.json'
        save(path,dict(status='approved-for-integration',supersededURL=replacement['url'],
                       supersededSHA256=replacement['sha256'],replacementSHA256=candidate['sha256'],
                       sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,
                       retainedUids=replacement['retainedUids'],replacementTargetUids=patch['meta']['targetUids'],
                       fullMeshCheck=ref(fullcheck),sourceReview=ref(REVIEW/'ROOT-SOURCE-REVIEW.json')))
        terrain['nativeReview'] = ref(path)
    url = 'city/data/official-models/'+BATCH+'/catalogue.json'
    save(STAGE/'plan.json',dict(areas=[dict(area='Park Avenue / Charming Garden six unchanged originals',
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
        BATCH,'park-avenue-six-qualified-original-stage-v1',
        [Path(__file__),REVIEW/'result.json',
         *[ROOT/path for path in pins],*[path for path in STAGE.rglob('*') if path.is_file()]],
        dict(uids=list(roster),privateStageQualified=True,publisherDryRunPassed=True,publication=False))
    print(result['jobId'],flush=True)

if __name__ == '__main__':
    main()
