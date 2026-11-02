"""Recover the one nominated Dock1A original via the existing immutable cache."""
import shutil
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-source43101-dock-cached-original-v1-20261103'
PARENT = 'government-xl-source43101-dock-native-lookup-v1-20261103'
UIDS = ['landsd/43101:0', 'landsd/316521:0', 'landsd/316522:0']


def owned():
    local, out = HERE / 'local' / BATCH, BASE / BATCH
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    _, pins = authenticate(BASE / PARENT)
    p = BASE / PARENT / 'summary.json'
    assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
    parent = read(p)
    row = next(r for r in parent['rows'] if r['uid'] == UIDS[1])
    assert len(row['exactCachedNativeMatches']) == 1
    native = row['exactCachedNativeMatches'][0]
    tile = ROOT / parent['currentTile']['path']
    assert digest(tile.read_bytes()) == parent['currentTile']['sha256']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        sha, result = c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s', (native['cacheKey'],)).fetchone()
    assert sha == native['resultSHA256'] and native['model'] in result['models']
    artifacts = [a for a in result['artifacts'] if a['kind'] == 'original-and-prepared-sheet']
    assert artifacts and all(0 < a['bytes'] <= 2_000_000_000 for a in artifacts)
    assert shutil.disk_usage(local.parent).free > 3 * sum(a['bytes'] for a in artifacts) + 1_000_000_000
    outcome = dict(sheet=native['sheet'], cacheKey=native['cacheKey'], resultSha=sha, model=native['model'])
    evidence = dict(native=[outcome], rows=[UIDS[1]], sources={UIDS[1]: dict(building=row['currentViewerForm'])})
    evidence_path = local / 'exact-cache-input.json.gz'; save(evidence_path, evidence)
    prepare = module('source43101_existing_exact_cache_recovery', HERE.parent / 'enhancement-screening/shape_prepare.py')
    recovered = prepare.prepare(evidence_path, local / 'recovered', allow_source=False, workers=1, env_file=ROOT / '.env.modelling', reservation_receipt=lease)
    refs = [Path(__file__), HERE.parent / 'enhancement-screening/shape_prepare.py', BASE / PARENT / 'result.json', p, tile, evidence_path, local / 'recovered/geometry-inputs.json']
    assets = []
    for recovered_row in recovered['rows']:
        candidate = recovered_row['candidate']; asset = Path(candidate['path'])
        assert recovered_row['uid'] == UIDS[1] and digest(asset.read_bytes()) == native['model']['asset']['sha256'] == candidate['entry']['sha256']
        assert asset.stat().st_size == native['model']['asset']['bytes']
        refs.append(asset)
        assets.append(dict(uid=UIDS[1], path=str(asset.relative_to(ROOT)), sha256=digest(asset.read_bytes()), candidate=candidate, native=native))
    summary = dict(uids=UIDS, sourceSHA256=parent['sourceSHA256'], exactDockOriginals=assets, errors=recovered['errors'], methods=recovered['methods'],
                   sourceFallbackEnabled=False, sourceGeometryChanges=0, sourcePoseChanges=0, identityAccepted=False,
                   physicalAcceptance=False, installationApproved=False, publication=False,
                   qualification='Existing cache recovery only; this does not reinstate geometric screening or skip decisions. Exact cached Dock1A bytes, when present, enable whole original-source interface checks. Missing316522and43101metadata matches remain scoped to the preceding cached lookup, never government-wide absence. No actor is installed or accepted.')
    save(out / 'summary.json', summary)
    assert reservations.owns(lease)
    module('source43101_dock_cached_original_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'exact-existing-cache-dock1a-original-recovery', refs, summary)
    print(dict(recovered=len(assets), errors=recovered['errors']), flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not (BASE / BATCH).exists() and not (HERE / 'local' / BATCH).exists()
        claim = reservations.claim('source43101-dock-cache-' + str(uuid.uuid4()), ['building:' + u for u in UIDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], 'Exact source group reservation unavailable'
        execute_reserved(claim['reservation'], HERE / 'local' / BATCH / 'reservation.json', [sys.executable, __file__, '--owned'])
