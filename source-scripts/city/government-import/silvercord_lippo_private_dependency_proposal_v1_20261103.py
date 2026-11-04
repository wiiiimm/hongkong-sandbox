"""Prepare an exact private support-only catalogue migration; never publish it."""
import copy
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v4_20261103 import execute_reserved
from dependency_preflight import inspect_dependencies

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-private-dependency-proposal-v1-20261103'
LOCAL = HERE / 'local' / BATCH
RUNTIME = 'government-xl-silvercord-lippo-five-original-floor-runtime-v1-20261103'
OWNER, PODIUM = 'landsd/239465:0', 'landsd/231645:0'
SUPPORTS = {'landsd/237843:0': PODIUM, 'landsd/238659:0': 'landsd/233997:0',
            'landsd/239032:0': 'landsd/233997:0'}
UIDS = ['landsd/233997:0', PODIUM, *SUPPORTS]


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and not (BASE / BATCH).exists()
    _, pins = authenticate(BASE / RUNTIME)
    selected_path = BASE / RUNTIME / 'selection.json.gz'
    assert digest(selected_path.read_bytes()) == pins[str(selected_path.relative_to(ROOT))]
    selection = read(selected_path)
    sources = {r['uid']: r for r in selection['rows']}
    assert set(sources) == set(UIDS)
    refs = [Path(__file__), BASE / RUNTIME / 'result.json', selected_path]
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    mh = digest(manifest_path.read_bytes())
    assert mh == selection['manifestSHA256']
    manifest = read(manifest_path)
    refs.append(manifest_path)
    all_models, matches, current_pins = [], [], {}
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        catalogue = read(path)
        current_pins[str(path.relative_to(ROOT))] = digest(path.read_bytes())
        refs.append(path)
        all_models.extend(catalogue['models'])
        for entry in catalogue['models']:
            if entry['uid'] == OWNER:
                matches.append((url, path, catalogue, entry))
    assert len(all_models) == len({r['uid'] for r in all_models}) == 7101
    assert not set(UIDS) & {r['uid'] for r in all_models}
    assert len(matches) == 1
    url, path, before, owner = matches[0]
    assert owner['sha256'] == '2ca41f96bdce41f47c95891182450878c1fc694b12c3ae22bbeb29ff07cc276c'
    assert owner['supportDependencies'] == [dict(uid=PODIUM, state='surveyed-footprint-fallback', csuid='3551417531P20050812')]
    asset = path.parent / owner['asset']
    assert digest(asset.read_bytes()) == owner['sha256']
    refs.append(asset)
    pointer = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    snapshot = read(pointer)['snapshotId']
    refs.append(pointer)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',
                          (snapshot, OWNER)).fetchone() == ('installed-verified', owner['sha256'])
    candidates = []
    for uid in sorted(UIDS):
        row = sources[uid]
        source_asset = ROOT / row['candidate']['path']
        assert digest(source_asset.read_bytes()) == row['sourceSHA256'] == row['candidate']['entry']['sha256']
        refs.append(source_asset)
        entry = copy.deepcopy(row['candidate']['entry'])
        entry.update(asset='assets/' + row['sourceSHA256'] + '.glb.gz', proceduralWindows=False,
                     activationGroup=sorted(UIDS), placementReviewed=False, publicationApproved=False,
                     identityReviewApproved=False, sourceIdentityReviewed=False)
        assert not entry.get('suppressesBuildingUids')
        entry['supportDependencies'] = []
        if uid in SUPPORTS:
            peer = sources[SUPPORTS[uid]]
            entry['supportDependencies'] = [dict(uid=peer['uid'], state='candidate',
                buildingCSUID=peer['source']['building']['buildingCSUID'], sha256=peer['sourceSHA256'])]
        candidates.append(entry)
    old_report = inspect_dependencies(all_models, candidates)
    blockers = [(r['uid'], q['reason'], q.get('affectedUids')) for r in old_report['rows'] for q in r['blockers']]
    assert blockers == [(PODIUM, 'fallback-dependency-migration-required', [OWNER])]
    after = copy.deepcopy(before)
    changed = next(r for r in after['models'] if r['uid'] == OWNER)
    changed['supportDependencies'] = [dict(uid=PODIUM, state='installed',
        buildingCSUID=sources[PODIUM]['source']['building']['buildingCSUID'], sha256=sources[PODIUM]['sourceSHA256'])]
    assert {k: v for k, v in owner.items() if k != 'supportDependencies'} == {
        k: v for k, v in changed.items() if k != 'supportDependencies'}
    assert all(a == z or a['uid'] == z['uid'] == OWNER for a, z in zip(before['models'], after['models']))
    proposed_models = [changed if r['uid'] == OWNER else r for r in all_models]
    report = inspect_dependencies(proposed_models, candidates)
    assert len(report['rows']) == 5 and not any(r['blockers'] for r in report['rows'])
    out = BASE / BATCH
    after_path = out / 'lippo-tower-catalogue-after.json'
    save(after_path, after)
    save(out / 'private-five-original-catalogue.json', dict(schemaVersion=1, kind='unapproved-private-original-assembly',
        crs='EPSG:2326', verticalDatum='Hong Kong Principal Datum', rootTranslation=[-834500, 0, 816500], models=candidates))
    save(out / 'before-dependency-preflight.json', old_report)
    save(out / 'private-after-dependency-preflight.json', report)
    update = dict(ownerUid=OWNER, ownerSHA256=owner['sha256'], url=url,
        beforeSHA256=current_pins[str(path.relative_to(ROOT))], source=str(after_path.relative_to(ROOT)),
        sha256=digest(after_path.read_bytes()), beforeEntry=owner, afterEntry=changed,
        changedFields=['supportDependencies'], sourceGeometryChanges=0,
        approvalScope='Private proposal only. Requires exact native support/source-role, stage, browser lifecycle, guarded publication and independent readback.')
    for name, sha in current_pins.items():
        assert digest((ROOT / name).read_bytes()) == sha
    assert reservations.owns(lease) and digest(manifest_path.read_bytes()) == mh
    refs.extend(HERE / n for n in ['dependency_preflight.py'])
    refs.append(ROOT / 'source-scripts/city/island-detail-integration/model_dependencies.py')
    result = dict(uids=[*UIDS, OWNER], sourceSHA256ByUid={u: sources[u]['sourceSHA256'] for u in UIDS},
        currentManifestSHA256=mh, currentInstalledSnapshot=snapshot, installedSupportUpdate=update,
        retainedOwnerGeometryAndAllOtherMetadataUnchanged=True, privateAfterDependencyBlockers=0,
        supportByUid=SUPPORTS, requiredAtomicGroup=sorted(UIDS), sourceGeometryChanges=0,
        sourcePoseChanges=0, supportMigrationApproved=False, physicalAcceptance=False,
        placementReviewed=False, installationApproved=False, publication=False, newlyInstalled=0,
        qualification=__doc__ + ' Uses existing installed/candidate dependency states and unchanged publisher preflight semantics. All five private entries remain explicitly unapproved. Current public catalogue/manifest/asset bytes are untouched.')
    save(out / 'summary.json', result)
    module('exact_private_lippo_owner_migration', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'private-exact-five-original-support-and-retained-owner-metadata-proposal', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('private-original-support-migration-' + str(uuid.uuid4()),
            ['building:' + uid for uid in [*UIDS, OWNER]] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
