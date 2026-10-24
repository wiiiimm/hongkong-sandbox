"""Lease-guarded publication of six reviewed unchanged originals."""
import argparse
import json
import sys
from pathlib import Path
from contextlib import contextmanager
import park_avenue239350_qualified_stage_v1_20261018 as stage
from run import connect, reservations, dict_row
from fixed_xl_source_binding import resolve_uid
ROOT, HERE, BASE = stage.ROOT, stage.HERE, stage.BASE
BATCH = 'government-xl-park-avenue239350-original-installed-v1-20261018'
REVIEW = stage.REVIEW
BROWSER = BASE/'government-xl-park-avenue239350-browser-1280-v3-20261018'
MOBILE = BASE/'government-xl-park-avenue239350-browser-390-v2-20261018'
check = stage.check
stage.SOURCES = stage.read(REVIEW/'ROOT-SOURCE-REVIEW.json')['sourceSHA256ByUid']

def inventory_delta(previous, models, *, manifest_sha, snapshot):
    assert previous['manifestSHA256'] == manifest_sha and previous['snapshotId'] == snapshot
    assert len(previous['rows']) == len({row['sourceKey'] for row in previous['rows']}) == previous['counts']['total'] == 521
    assert len(models) == 6 and {model['uid']:model['sha256'] for model in models} == stage.SOURCES
    keys = {model['originalSourceKey'] for model in models}
    assert len(keys) == 6
    matched = [row for row in previous['rows'] if row['sourceKey'] in keys]
    assert matched and all(not row['installedVerified'] for row in matched)
    uids = [resolve_uid(row, models) for row in matched]
    assert len(set(uids)) == len(matched) and set(uids) <= set(stage.SOURCES)
    return dict(returnedModels=6,fixedXLTotal=521,newFixedXLUids=uids,
                newFixedXLSourceKeys=[row['sourceKey'] for row in matched],expectedFixedXLDelta=len(matched),
                previousInstalled=previous['counts']['installedVerified'])

def evidence():
    result = stage.read(stage.DOC/'result.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone() == ('complete',result)
    pins = {}
    for item in result['evidenceRefs']:
        assert item['path'] not in pins or pins[item['path']] == item
        pins[item['path']] = item
    for item in pins.values(): check(item)
    qualification = stage.read(stage.DOC/'qualification.json')
    assert qualification['privateStageQualified'] and qualification['sourceSHA256ByUid'] == stage.SOURCES
    check(qualification['currentManifest'])
    review = stage.read(REVIEW/'ROOT-SOURCE-REVIEW.json')
    assert review['originalSourceReviewAccepted'] and review['sourceSHA256ByUid'] == stage.SOURCES
    models = stage.read(stage.STAGE/'catalogue.json')['models']
    assert len(models) == 6 and {model['uid']:model['sha256'] for model in models} == stage.SOURCES
    for model in models:
        assert all(model.get(key) is True for key in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved'])
        assert model['proceduralWindows'] is False and not model.get('suppressesBuildingUids')
        assert [dep['uid'] for dep in model['supportDependencies']] == review['supportDependencies'].get(model['uid'],[])
        assert all(dep['sha256'] == stage.SOURCES[dep['uid']] and dep['state'] == 'installed' for dep in model['supportDependencies'])
    for directory in [BROWSER,MOBILE]:
        report = stage.read(directory/'staged-browser.json')
        assert report['passed'] and not report['errors']
        assert len(report['views']) == 12 and len(report['jointViews']) == 6 and len(report['retainedNativeOwnViews']) == 76
    terrain = stage.read(stage.STAGE/'plan.json')['topLevelTerrainPatches']
    assert len(terrain) == 1 and terrain[0] == qualification['terrainCandidate']
    patch = terrain[0]
    assert patch['sha256'] == review['terrainCandidate']['sha256']
    assert patch['replaces'] == review['terrainCandidate']['replaces']
    check(patch['nativeReview'])
    check(dict(path=patch['source'],sha256=patch['sha256']))
    forms = stage.read(BASE/'government-xl-park-avenue239350-joint-validation-v1-20261018/neighbour-inputs.json.gz')['rows']
    uids = {row['building']['uid'] for row in forms} | set(stage.SOURCES)
    return {('building:' if uid.startswith('landsd/') else 'source-form:')+uid for uid in uids} | {'terrain:'+patch['replaces']['url']} | {'terrain:city/data/terrain.json'}

def assert_publication_idle():
    check(stage.read(stage.DOC/'qualification.json')['currentManifest'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('plan'); parser.add_argument('--receipt',required=True)
    parser.add_argument('--phase',required=True); parser.add_argument('--apply',action='store_true')
    args = parser.parse_args()
    assert args.phase == BATCH and (ROOT/args.plan).resolve() == stage.STAGE/'plan.json'
    keys = evidence(); lease = json.loads(Path(args.receipt).read_text())
    @contextmanager
    def guard():
        with connect() as db:
            db.row_factory = dict_row
            db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
            current = reservations._current(db,lease)
            assert current and keys <= set(current['resources'])
            assert_publication_idle()
            yield
    with guard(): pass
    pub = stage.module('olympian_atomic_publisher',HERE.parent/'island-detail-integration/publish.py')
    pub.PUBLICATION_GUARD = guard
    pub.DOC = ROOT/'docs/astra-city/model-integration-20260909'/args.phase
    sys.argv = ['publish.py',args.plan] + (['--apply'] if args.apply else [])
    pub.main()

if __name__ == '__main__': main()
