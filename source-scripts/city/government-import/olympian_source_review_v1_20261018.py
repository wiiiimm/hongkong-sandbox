"""Exact 13-original acceptance, preserving source-specific diagnostic decisions."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-olympian-source-review-v1-20261018'
def folder(name):
    return BASE / ('government-xl-olympian-two-' + name + '-20261018')
def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))

def main():
    doc = BASE / BATCH
    assert not doc.exists()
    identity = BASE / 'government-xl-olympian-identity-roster-v1-20261018'
    dependencies = BASE / 'government-xl-olympian-support-dependencies-v1-20261018'
    browsers = [BASE / f'government-xl-olympian-dependency-browser-{width}-v1-20261018' for width in (390, 1280)]
    names = [identity, dependencies, *browsers, *[folder(name) for name in [
        'thirteen-foundations-v2', 'three-podium-terrain-v2', 'grade-review-v1',
        'original-interface-review-v1', 'park-interface-review-v1',
        'hoi-yu-prior-review-v2', 'current-native-scope-v1', 'browser-390-fallback-v5']]]
    pins, refs = {}, [Path(__file__)]
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        for directory in names:
            path = directory / 'result.json'
            result = read(path)
            assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone() == ('complete', result)
            refs.append(path)
            for item in result['evidenceRefs']:
                assert item['path'] not in pins or pins[item['path']] == item['sha256']
                pins[item['path']] = item['sha256']
    for path, sha in pins.items():
        assert digest((ROOT / path).read_bytes()) == sha, path
    roster = read(identity / 'roster.json')['models']
    models = {row['uid']: row for row in roster}
    assert len(models) == len(roster) == 13 and all(row['identityAccepted'] for row in roster)
    support = read(dependencies / 'dependencies.json')['dependencies']
    assert len(support) == 10 and set(support) < set(models)
    foundations = read(folder('thirteen-foundations-v2') / 'summary.json')
    assert foundations['allModesPassed'] and len(foundations['rows']) == 52
    assert {(row['uid'], row['mode']) for row in foundations['rows']} == {(uid, mode) for uid in models for mode in ['original', 'literal', 'left', 'balanced']}
    assert all(row['passed'] and row['covered'] == row['faces'] and row['buried'] == row['upwardBuried'] == 0 for row in foundations['rows'])
    grade = read(folder('grade-review-v1') / 'ROOT-GRADE-REVIEW.json')
    assert grade['originalGradeInterpretationAccepted'] and all(models[uid]['sourceSHA256'] == sha for uid, sha in grade['sourceSHA256ByUid'].items())
    interfaces = [read(folder(name) / 'ROOT-INTERFACE-REVIEW.json') for name in ['original-interface-review-v1', 'park-interface-review-v1']]
    assert all(review['sourceSpecificInterfaceInterpretationAccepted'] for review in interfaces)
    assert set(uid for review in interfaces for uid in review['uids']) == set(support)
    terrain_dir = folder('three-podium-terrain-v2')
    candidate = read(terrain_dir / 'terrain-candidates.json')[0]
    assert digest((ROOT / candidate['path']).read_bytes()) == candidate['sha256']
    validation = read(terrain_dir / 'validation.json')
    assert validation['loaderAccepted'] == validation['checksPassed'] == 3 and validation['exceptions'] == 0
    assert read(terrain_dir / 'final-terrain-budget.json')['passed']
    basic = read(terrain_dir / 'neighbour-checks.json')
    assert len(basic['patches']) == 1 and set(basic['patches'][0]['blockedBy']) == set(support)
    native = read(terrain_dir / 'native-neighbour-checks.json')['rows']
    assert len(native) == len({row['uid'] for row in native}) == 25
    assert [row['uid'] for row in native if not row['passed']] == ['landsd/177605:0']
    assert all(row['terrain']['newlyWhollyBuried'] == row['terrain']['newlyUpwardWhollyBuried'] == 0 for row in native)
    hoi = read(folder('hoi-yu-prior-review-v2') / 'result.json')
    assert hoi['currentSourcesAndDependencyUnchanged'] and hoi['existingExactSourceSupportReviewVerified']
    # Preserve the raw generic Hoi Yu failure; use only its authenticated,
    # unchanged prior source/support review, not a blanket neighbour waiver.
    assert hoi['threePodiumCandidateTerrainRegression'] == next(row for row in native if row['uid'] == 'landsd/177605:0')
    browser_refs = []
    for directory, width in zip(browsers, (390, 1280)):
        report = read(directory / 'staged-browser.json')
        assert report['passed'] and not report['errors']
        views = [view for view in report['views'] if 'time' in view]
        assert len(views) == 26 and {(view['uid'], view['time']) for view in views} == {(uid, time) for uid in models for time in ['15:00', '22:00']}
        assert all(view['sourceSHA256'] == models[view['uid']]['sourceSHA256'] for view in views)
        assert len(report['jointViews']) == 13
        retained = report['retainedNativeOwnViews']
        assert len(retained) == 50 and {(view['uid'], view['time']) for view in retained} == {(row['uid'], time) for row in native for time in ['15:00', '22:00']}
        browser_refs.append(ref(directory / 'staged-browser.json'))
        staged = read(HERE / 'local' / directory.name / 'catalogue.json')['models']
        assert {entry['uid'] for entry in staged} == set(models)
        for entry in staged:
            assert entry['sha256'] == models[entry['uid']]['sourceSHA256']
            assert [dep['uid'] for dep in entry['supportDependencies']] == support.get(entry['uid'], [])
            assert all(dep['sha256'] == models[dep['uid']]['sourceSHA256'] for dep in entry['supportDependencies'])
    fallback = read(folder('browser-390-fallback-v5') / 'staged-browser.json')
    failures = [view for view in fallback['views'] if view.get('phase') == 'failed-download']
    assert fallback['passed'] and not fallback['errors'] and len(failures) == 13
    assert {view['uid'] for view in failures} == set(models) and all(view['fallbackRetained'] and view['fallbackFaces'] > 0 for view in failures)
    decision = dict(uids=list(models), originalSourceReviewAccepted=True,
        sourceSHA256ByUid={uid: row['sourceSHA256'] for uid, row in models.items()},
        identityRoster=ref(identity / 'roster.json'), supportDependencies=support,
        terrainCandidate=candidate, browserEvidence=browser_refs,
        sourceSpecificReviewEvidence=[ref(folder(name) / filename) for name, filename in [
            ('grade-review-v1', 'ROOT-GRADE-REVIEW.json'), ('original-interface-review-v1', 'ROOT-INTERFACE-REVIEW.json'),
            ('park-interface-review-v1', 'ROOT-INTERFACE-REVIEW.json'), ('hoi-yu-prior-review-v2', 'result.json')]],
        rawDiagnosticsPreserved=True, sourceGeometryChanges=0, sourcePoseChanges=0,
        sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False, publication=False,
        limitations=['Original source-specific acceptance only; no engineering certification or global threshold waiver.',
                    'Authored grade gaps and buried lower-wall portions remain exactly as documented in the grade review.',
                    'Guarded publication and live verification are still required.'],
        reviewer='Codex ROOT')
    save(doc / 'ROOT-SOURCE-REVIEW.json', decision)
    result = module('source_review_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'olympian-thirteen-original-source-review-v1', [*refs, *[ROOT / path for path in pins]],
        dict(uids=list(models), originalSourceReviewAccepted=True, publication=False))
    print(result['jobId'], flush=True)

if __name__ == '__main__':
    main()
