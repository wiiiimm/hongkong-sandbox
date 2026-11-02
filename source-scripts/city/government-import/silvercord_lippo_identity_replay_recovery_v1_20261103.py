"""Freeze completed V2 identity results after its metadata-only uids failure.

Revalidate exact source/current inputs and reviewed predicates, without decoding
or redoing the completed geometric projection. No public assets are changed.
"""
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect, NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v3_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from silvercord_lippo_reviewed_identity_v2_20261103 import EXPECTED, REVIEW, reviewed_proof

BASE = ROOT / 'docs/astra-city/government-import'
PRIOR = 'government-xl-silvercord-lippo-reviewed-identity-replay-v2-20261103'
BATCH = 'government-xl-silvercord-lippo-reviewed-identity-replay-recovered-v1-20261103'
LOCAL = HERE / 'local' / BATCH
RUNTIME = 'government-xl-silvercord-lippo-current-checks-v1-20261101-runtime'


def owned():
    lease = read(LOCAL / 'reservation.json'); assert reservations.owns(lease)
    prior = BASE / PRIOR; summary = read(prior / 'summary.json')
    assert summary['bothCurrentIdentitiesReplayed'] and not summary['installationApproved'] and 'uids' not in summary
    refs = [Path(__file__), HERE / 'silvercord_lippo_reviewed_identity_v2_20261103.py',
            HERE / 'silvercord_lippo_identity_replay_v2_20261103.py', prior / 'summary.json']
    review, pins = authenticate(BASE / REVIEW); path = BASE / REVIEW / 'decisions.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]; refs += [BASE / REVIEW / 'result.json', path]
    decisions = {d['uid']: d for d in read(path)['decisions']}; assert set(decisions) == set(EXPECTED)
    _, native_pins = authenticate(BASE / RUNTIME); path = BASE / RUNTIME / 'selection.json.gz'
    assert digest(path.read_bytes()) == native_pins[str(path.relative_to(ROOT))]; refs += [BASE / RUNTIME / 'result.json', path]
    selected = {r['uid']: r for r in read(path)['rows']}; assert set(selected) == set(EXPECTED)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == summary['currentManifestSHA256']; refs.append(manifest)
    prefixes = {v[1][1:11] for v in EXPECTED.values()}; route_hashes = {}; sources = []
    for tile in read(manifest)['tiles']:
        path = ROOT / '3d-viewer' / tile['url']; raw = path.read_bytes()
        matching = [f for f in read(path)['buildings'] if str(f.get('buildingCSUID') or '')[:10] in prefixes]
        if matching:
            route_hashes[tile['url']] = digest(raw); refs.append(path); sources.extend(matching)
    assert {f['uid'] for f in sources} == set(EXPECTED) and len(sources) == 2
    for uid, row in selected.items():
        path = prior / uid.split('/')[1] / 'identity.json'; proof = read(path); refs.append(path)
        expected = reviewed_proof(proof['rawCurrentIdentity'], decisions[uid])
        expected['boundedIdentityReview'] = dict(jobId=review['jobId'], path=str((BASE / REVIEW / 'decisions.json').relative_to(ROOT)), sha256=pins[str((BASE / REVIEW / 'decisions.json').relative_to(ROOT))])
        assert proof == expected and proof['exactRouteTileHashes'] == route_hashes
        assert proof['exactRouteManifestSHA256'] == summary['currentManifestSHA256']
        assert next(f for f in sources if f['uid'] == uid) == row['source']['building']
        asset = ROOT / row['candidate']['path']; assert digest(asset.read_bytes()) == EXPECTED[uid][0]; refs.append(asset)
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            assert db.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',
                              (NATIVE_RUN, row['native']['cacheKey'])).fetchone() == (row['native']['resultSha'],)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == summary['currentManifestSHA256']
    out = BASE / BATCH
    result = dict(summary, uids=sorted(EXPECTED), recoveredCompletedGeometryWithoutRepeating=True,
                  priorFreezeError="KeyError('uids')", sourceCorrupt=False, permanentRejection=False)
    save(out / 'summary.json', result)
    module('reviewed_identity_metadata_recovery_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'recovered-completed-exact-reviewed-pair-identity', list(dict.fromkeys(refs)), result)
    print(dict(bothCurrentIdentitiesReplayed=True, metadataRecovered=True, newlyInstalled=0), flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('reviewed-identity-metadata-recovery-' + str(uuid.uuid4()),
                                   ['building:' + u for u in EXPECTED] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok']
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
