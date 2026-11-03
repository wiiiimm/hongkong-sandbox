"""Rebind unchanged reviewed podium identities to the complete current tile route.

Historical reviews remain immutable. Every old direct input except the manifest
must still match, and every current tile is scanned before identity is reused.
This does not grant physical, placement or publication approval.
"""
import copy
import json
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect, NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from component_type_resolution import resolve
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from silvercord_lippo_reviewed_identity_v2_20261103 import EXPECTED

BASE = ROOT/'docs/astra-city/government-import'
PRIOR = 'government-xl-silvercord-lippo-reviewed-identity-replay-recovered-v1-20261103'
IDENTITIES = 'government-xl-silvercord-lippo-reviewed-identity-replay-v2-20261103'
RUNTIME = 'government-xl-silvercord-lippo-current-checks-v1-20261101-runtime'
BATCH = 'government-xl-silvercord-lippo-current-identity-binding-v1-20261103'
LOCAL = HERE/'local'/BATCH
MANIFEST = '3d-viewer/city/data/manifest.json'


def bind_identity(proof, row, sources, route_hashes, current_manifest_sha, historical_ref):
    """Reuse geometry only when all complete current records/routes are identical."""
    uid = row['uid']
    sha, model_id, faces, _, provider_id = EXPECTED[uid]
    assert proof['passed'] and proof['identityAccepted']
    assert proof['sourceSHA256'] == row['sourceSHA256'] == sha
    assert row['modelId'] == model_id and row['triangles'] == faces
    assert proof['completeRecordProjection'] is True
    assert proof['exactRouteTileHashes'] == route_hashes
    assert proof['proof'] == dict(exactObjectId=True, exactBuildingCSUID=True,
                                uniqueViewerMatch=True, identityAccepted=True)
    assert proof['providerObjectIdExact'] is False and proof['currentProviderObjectId'] == provider_id
    assert all(proof[k] is False for k in ['physicalAccepted', 'placementApproved',
                                          'collisionExemption', 'installationApproved', 'publication'])
    candidates = [s for s in sources
                  if str(s['building'].get('buildingCSUID') or '')[:10] == model_id[1:11]]
    assert len(candidates) == 1 and candidates[0] == row['source']
    route = resolve(row['native']['model'], candidates)
    assert route == proof['exactCurrentComponentRoute'], 'Complete current component route changed'
    assert route['qualified'] and route['uid'] == uid and route['source'] == row['source']
    target = proof['freshCurrentIdentity']['target']
    assert target == {key:row['source']['building'][key] for key in target}
    updated = copy.deepcopy(proof)
    updated['exactRouteManifestSHA256'] = current_manifest_sha
    updated['currentManifestBinding'] = dict(
        historicalIdentity=historical_ref,
        historicalManifestSHA256=proof['exactRouteManifestSHA256'],
        currentManifestSHA256=current_manifest_sha,
        completeCurrentTileScan=True, allHistoricalNonManifestInputsUnchanged=True,
        completeSourceProjectionReused=True, geometryCalculationsRepeated=0)
    return updated


def owned():
    lease = read(LOCAL/'reservation.json')
    assert reservations.owns(lease) and not (BASE/BATCH).exists()
    receipt, pins = authenticate(BASE/PRIOR)
    assert receipt['bothCurrentIdentitiesReplayed'] and set(receipt['uids']) == set(EXPECTED)
    assert MANIFEST in pins
    refs = [Path(__file__), BASE/PRIOR/'result.json', HERE/'component_type_resolution.py',
            HERE/'government_georef_cell_identity.py']
    for path, sha in pins.items():
        if path == MANIFEST:
            continue
        assert digest((ROOT/path).read_bytes()) == sha, 'Historical identity input changed: '+path
        refs.append(ROOT/path)
    manifest_path = ROOT/MANIFEST
    manifest_raw = manifest_path.read_bytes()
    manifest_sha = digest(manifest_raw)
    manifest = json.loads(manifest_raw)
    prefixes = {item[1][1:11] for item in EXPECTED.values()}
    sources, route_hashes, tile_hashes = [], {}, {}
    urls = [tile['url'] for tile in manifest['tiles']]
    assert len(urls) == len(set(urls)), 'Duplicate current tile routes'
    for url in urls:
        path = ROOT/'3d-viewer'/url
        assert path.resolve().is_relative_to((ROOT/'3d-viewer').resolve())
        raw = path.read_bytes()
        sha = digest(raw)
        tile_hashes[url] = sha
        matches = [b for b in json.loads(raw)['buildings']
                   if str(b.get('buildingCSUID') or '')[:10] in prefixes]
        # Also reject a duplicate UID hidden under a different component prefix.
        assert all(b['uid'] not in EXPECTED or b in matches for b in json.loads(raw)['buildings'])
        if matches:
            route_hashes[url] = sha
            sources.extend(dict(building=b, tile=url, tileSHA256=sha) for b in matches)
            refs.append(path)
    assert len(sources) == 2 and {s['building']['uid'] for s in sources} == set(EXPECTED)
    selection = read(BASE/RUNTIME/'selection.json.gz')
    assert {r['uid'] for r in selection['rows']} == set(EXPECTED)
    rows = []
    for row in selection['rows']:
        path = BASE/IDENTITIES/row['uid'].split('/')[1]/'identity.json'
        proof = read(path)
        assert proof['exactRouteManifestSHA256'] == pins[MANIFEST]
        ref = dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))
        rebound = bind_identity(proof, row, sources, route_hashes, manifest_sha, ref)
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            assert db.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',
                              (NATIVE_RUN, row['native']['cacheKey'])).fetchone() == (row['native']['resultSha'],)
        save(BASE/BATCH/row['uid'].split('/')[1]/'identity.json', rebound)
        rows.append(dict(uid=row['uid'], sourceSHA256=row['sourceSHA256'], passed=True,
                         providerObjectIdExact=False, geometryCalculationsRepeated=0))
    assert reservations.owns(lease) and digest(manifest_path.read_bytes()) == manifest_sha
    for url, sha in tile_hashes.items():
        assert digest((ROOT/'3d-viewer'/url).read_bytes()) == sha
    refs.append(manifest_path)
    save(BASE/BATCH/'complete-current-tile-hashes.json', tile_hashes)
    result = dict(uids=sorted(EXPECTED), rows=rows, bothCurrentIdentitiesRebound=True,
                  currentManifestSHA256=manifest_sha, historicalManifestSHA256=pins[MANIFEST],
                  currentTilesScanned=len(tile_hashes), exactRouteTileHashes=route_hashes,
                  allHistoricalNonManifestInputsUnchanged=True, geometryCalculationsRepeated=0,
                  sourceGeometryChanges=0, sourcePoseChanges=0, scriptExternalAICalls=0,
                  physicalAcceptance=False, placementApproved=False, installationApproved=False, publication=False)
    save(BASE/BATCH/'summary.json', result)
    module('silvercord_current_identity_binding_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'unchanged-complete-podium-identities-bound-to-current-whole-map-route',
        list(dict.fromkeys(refs)), result)
    print(dict(bothCurrentIdentitiesRebound=True, currentTilesScanned=len(tile_hashes), geometryCalculationsRepeated=0), flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE/BATCH).exists()
        claim = reservations.claim('silvercord-current-identity-binding-'+str(uuid.uuid4()),
            ['building:'+u for u in EXPECTED]+['immutable-source-proof:'+BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL/'reservation.json', [sys.executable, __file__, '--owned'])
