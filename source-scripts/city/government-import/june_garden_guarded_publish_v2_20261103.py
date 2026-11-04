"""Lease-fenced publication of the exact qualified six June Garden originals.

Preparation is read-only. A completed qualified stage and inspected exports are
mandatory; this adapter never creates reviews or awards installation credit.
"""
import argparse
import sys
from contextlib import contextmanager
from pathlib import Path

from run import ROOT, HERE, read, save, digest, connect, reservations, dict_row
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_coordinated_retained_contract_v1_20261027 import verify_metadata
from june_garden_publisher_hooks_v3_20261103 import SOURCES, SUPPORTS, P, SMALL, DESTINATIONS, install
from june_garden_qualified_stage_v4_20261103 import PHYSICAL, TERRAIN, PATCH, ATOMIC

BASE = ROOT/'docs/astra-city/government-import'
BROWSER = 'government-xl-june-garden-mobile-recovery-v1-20261103'
SUPPLEMENT = 'government-xl-june-garden-retained-camera-supplement-v3-20261103'
QUALIFIED = 'government-xl-june-garden-qualified-stage-v4-20261103'
STAGE = HERE/'accepted'/QUALIFIED
BATCH = 'government-xl-june-garden-original-installed-v2-20261103'
PLAN = BASE/'government-xl-tower3-june-garden-six-originals-current-v1-20261102-plan.json'


def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))


def exact_plan(plan, surface):
    assert set(plan) == {'areas', 'topLevelTerrainPatches'}
    assert len(plan['areas']) == 1
    area = plan['areas'][0]
    assert set(area) == {'area', 'catalogue', 'destination'}
    assert area['catalogue'] == str((STAGE/'catalogue.json').relative_to(ROOT))
    assert area['destination'] == 'city/data/official-models/'+QUALIFIED+'/catalogue.json'
    entries = plan['topLevelTerrainPatches']
    assert len(entries) == len(surface['members']) == 3
    assert len({e['source'] for e in entries}) == len({e['destination'] for e in entries}) == 3
    assert {m['member'] for m in surface['members']} == set(DESTINATIONS)
    for member in surface['members']:
        entry = next(e for e in entries if e['source'] == member['candidate']['path'])
        assert set(entry) == {'source', 'sha256', 'destination', 'resolution', 'area', 'replaces', 'nativeReview'}
        assert entry['sha256'] == member['candidate']['sha256']
        assert entry['replaces'] == member['replaces']
        assert entry['destination'] == DESTINATIONS[member['member']]
        assert entry['destination'] != entry['replaces']['url']
    return True


def evidence():
    receipts, pins = {}, {}
    def take(batch):
        receipt, declared = authenticate(BASE/batch)
        receipts[batch] = receipt
        for path, sha in {**declared, str((BASE/batch/'result.json').relative_to(ROOT)):ref(BASE/batch/'result.json')['sha256']}.items():
            assert path not in pins or pins[path] == sha, 'Conflicting evidence binding'
            pins[path] = sha
        return receipt
    for batch in [QUALIFIED, PHYSICAL, TERRAIN, PATCH, ATOMIC, BROWSER, SUPPLEMENT]:
        take(batch)
    reuse = receipts[BROWSER]['reusedDesktopEvidence']
    archive = take(reuse['archiveBatch'])
    assert ref(BASE/reuse['archiveBatch']/'result.json')['sha256'] == reuse['archiveResultSHA256']
    assert archive['sourceSHA256ByUid'] == SOURCES
    # Hash each distinct declared input once; all public old actors and bytes
    # bound by the archive are checked again at this publication phase.
    for path, sha in pins.items():
        target = (ROOT/path).resolve()
        assert target.is_relative_to(ROOT.resolve()) and digest(target.read_bytes()) == sha, path
    qualification = read(BASE/QUALIFIED/'qualification.json')
    assert qualification['uids'] == sorted(SOURCES) and qualification['sourceSHA256ByUid'] == SOURCES
    assert all(qualification[k] is True for k in [
        'identityAccepted', 'sourceSpecificPhysicalInterpretationAccepted', 'visualAcceptance', 'privateStageQualified'])
    assert qualification['existingNativeReaccepted'] is False and qualification['publication'] is False
    assert qualification['sourceGeometryChanges'] == qualification['sourcePoseChanges'] == 0
    manifest = ref(ROOT/'3d-viewer/city/data/manifest.json')
    assert manifest['sha256'] == qualification['currentManifestSHA256']
    originals = read(BASE/BROWSER/'complete-unapproved-source-entries.json')
    catalogue = read(STAGE/'catalogue.json')
    verify_metadata(catalogue['models'], SOURCES, SUPPORTS, originals, {P:None, SMALL:None})
    for model in catalogue['models']:
        assert all(model[k] is True for k in ['sourceIdentityReviewed', 'identityReviewApproved', 'placementReviewed', 'publicationApproved'])
        assert model['sourceFunctionalApplicability'] == ref(BASE/QUALIFIED/'qualification.json')
        assert ref(STAGE/model['asset'])['sha256'] == SOURCES[model['uid']]
    surface = receipts[PATCH]
    plan = read(STAGE/'plan.json'); exact_plan(plan, surface)
    retained = {r['uid'] for r in read(BASE/TERRAIN/'summary.json')['rows']}
    assert len(retained) == 69 and not retained & set(SOURCES)
    config = read(STAGE/'live-browser-config.json')
    assert set(config['additionalRetainedUids']) == retained
    assert not config['availabilityOverlays'] and not config['catalogueReplacements']
    resources = set(read(PLAN)['resources'])
    assert {'building:'+u for u in retained | set(SOURCES)} <= resources
    assert {'terrain:'+m['replaces']['url'] for m in surface['members']} <= resources
    assert 'terrain:city/data/terrain.json' in resources
    return resources, surface, originals, manifest, pins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--receipt')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    assert not (args.prepare_only and args.apply)
    resources, surface, originals, manifest, pins = evidence()
    if args.prepare_only:
        assert not args.receipt
        save(BASE/(BATCH+'-proposal')/'publisher-preflight.json', dict(
            passed=True, resources=sorted(resources), sourceSHA256ByUid=SOURCES,
            stageReceipt=ref(BASE/QUALIFIED/'result.json'), publication=False))
        print(dict(preflightPassed=True, canonicalResources=len(resources), publication=False), flush=True)
        return
    assert args.receipt and not (BASE/BATCH/'installed-acceptance.json').exists()
    lease = read(Path(args.receipt))
    @contextmanager
    def fence():
        with connect() as db:
            db.row_factory = dict_row
            db.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            live = reservations._current(db, lease)
            assert live and resources <= set(live['resources'])
            assert ref(ROOT/'3d-viewer/city/data/manifest.json') == manifest
            yield
    with fence():
        pass
    publisher = module('june_exact_original_publisher', HERE.parent/'island-detail-integration/publish.py')
    install(publisher, ROOT, surface, originals, manifest['sha256'])
    publisher.PUBLICATION_GUARD = fence
    publisher.DOC = ROOT/'docs/astra-city/model-integration-20260909'/BATCH
    sys.argv = ['publish.py', str((STAGE/'plan.json').relative_to(ROOT))] + (['--apply'] if args.apply else [])
    publisher.main()


if __name__ == '__main__':
    main()
