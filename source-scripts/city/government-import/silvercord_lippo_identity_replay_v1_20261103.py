"""Freshly replay both exact reviewed source identities under canonical leases."""
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v3_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from silvercord_lippo_reviewed_identity_v1_20261103 import EXPECTED, REVIEW, verify_files

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-reviewed-identity-replay-v1-20261103'
RUNTIME = 'government-xl-silvercord-lippo-current-checks-v1-20261101-runtime'
IDENTITY = 'government-xl-silvercord-lippo-current-checks-v1-20261101-identity'
LOCAL = HERE / 'local' / BATCH


def owned():
    lease = read(LOCAL / 'reservation.json'); assert reservations.owns(lease)
    refs = [Path(__file__), HERE / 'silvercord_lippo_reviewed_identity_v1_20261103.py',
            HERE / 'exact_original_georef_cell_identity_20261009.py',
            HERE / 'government_georef_cell_identity.py', HERE / 'routed_original_cell_identity.py']
    pins = {}
    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]; refs.append(BASE / batch / 'result.json')
        p = BASE / batch / name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p); return read(p)
    selected = take(RUNTIME, 'selection.json.gz')['rows']
    assert len(selected) == 2 and {r['uid'] for r in selected} == set(EXPECTED)
    take(REVIEW, 'decisions.json')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; manifest_sha = digest(manifest.read_bytes()); refs.append(manifest)
    rows = []
    for row in selected:
        assert reservations.owns(lease)
        context = take(IDENTITY, row['uid'].split('/')[1] + '/context.json')
        proof = verify_files(row, context, LOCAL / row['uid'].split('/')[1])
        assert proof['identityAccepted'] and proof['passed'] and not proof['installationApproved']
        assert proof['exactRouteManifestSHA256'] == manifest_sha
        out = BASE / BATCH / row['uid'].split('/')[1] / 'identity.json'; save(out, proof); refs.append(out)
        refs.append(ROOT / row['candidate']['path'])
        for tile, sha in context['neighbourTileHashes'].items():
            p = ROOT / '3d-viewer' / tile; assert digest(p.read_bytes()) == sha; refs.append(p)
        rows.append(dict(uid=row['uid'], sourceSHA256=row['sourceSHA256'], passed=True,
                         rawReasons=proof['rawCurrentIdentity']['reasons'], providerObjectIdExact=False,
                         currentProviderObjectId=proof['currentProviderObjectId'], cachedViewerObjectId=proof['cachedViewerObjectId'],
                         identityOnly=True, physicalAccepted=False, installationApproved=False))
    assert digest(manifest.read_bytes()) == manifest_sha and reservations.owns(lease)
    summary = dict(rows=rows, currentManifestSHA256=manifest_sha, bothCurrentIdentitiesReplayed=True,
                   positiveIdentityAdapterImplemented=True, generalIdentityCheckerChanged=False,
                   sourceGeometryChanges=0, sourcePoseChanges=0, scriptExternalAICalls=0,
                   physicalAcceptance=False, terrainAccepted=False, installationApproved=False,
                   publication=False, newlyInstalled=0,
                   next='Use this explicit exact-source adapter in a fresh pair preparation. Complete original terrain, retained actor/support and runtime guards before any installation. No current provider OBJECTID equality is claimed.')
    save(BASE / BATCH / 'summary.json', summary)
    module('silvercord_lippo_identity_replay_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'fresh-exact-reviewed-original-podium-pair-identity-replay', list(dict.fromkeys(refs)), summary)
    print(dict(bothCurrentIdentitiesReplayed=True, newlyInstalled=0), flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('silvercord-lippo-reviewed-identity-' + str(uuid.uuid4()),
                                   ['building:' + u for u in EXPECTED] + ['immutable-source-proof:' + BATCH],
                                   batch=BATCH, ttl=3600)
        assert claim['ok'], 'Exact original source group unavailable'
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
