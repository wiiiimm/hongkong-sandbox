"""Acquire 17 exact unchanged project originals, preferring one local cache scan."""
import argparse
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
from run import ROOT, HERE, read, save, digest, reservations, NATIVE_RUN, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
import shape_prepare

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-southside-project-original-recovery-v1-20261028'
DOC, LOCAL = BASE / BATCH, HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'
LOOKUP = BASE / 'government-xl-southside-project-original-units-lookup-v1-20261028'


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    assert shutil.disk_usage(ROOT).free >= 3 * 1024**3
    _, pins = authenticate(LOOKUP)
    path = LOOKUP / 'lookup.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    lookup = read(path)
    assert lookup['uniqueExactMatches'] == len(lookup['rows']) == 17
    assert not lookup['noExactMatches'] and not lookup['multipleExactMatches']
    assert {'building:' + r['uid'] for r in lookup['rows']} <= set(lease['resources'])
    refs = [Path(__file__), LOOKUP / 'result.json', path, Path(shape_prepare.__file__)]
    wanted, sources, native = {}, {}, []
    for row in lookup['rows']:
        uid, match = row['uid'], row['matches'][0]
        model, form = match['model'], row['source']['building']
        entry = model['candidate']
        for left, right in [('uid', 'uid'), ('objectId', 'objectId'), ('buildingCSUID', 'buildingCSUID'),
                            ('recordedBaseHeight', 'baseHeightHKPD'), ('recordedTopHeight', 'topHeightHKPD')]:
            assert entry[left] == form[right]
        assert entry['sha256'] == model['asset']['sha256'] and entry['bytes'] <= 2 * 1024**2
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert digest(tile.read_bytes()) == row['source']['tileSHA256']
        assert next(b for b in read(tile)['buildings'] if b['uid'] == uid) == form
        refs.append(tile)
        wanted[entry['sha256']] = entry['bytes']
        sources[uid] = row['source']
        native.append(dict(sheet=match['sheet'], cacheKey=match['nativeCacheKey'], resultSha=match['nativeResultSHA256'], model=model))
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for record in lookup['checkedNativeRecords']:
            assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (record['cacheKey'],)).fetchone() == (record['resultSHA256'],)
    # One bounded filename scan across local source caches. Hash only requested
    # names, once per successful source; never trust a hash-shaped filename.
    files = subprocess.check_output(['rg', '--files', '--hidden', '--no-ignore', '-g', '*.glb.gz',
                                     'source-scripts/city', '3d-viewer/city/data'], cwd=ROOT, text=True).splitlines()
    seeded = {}
    cache = LOCAL / 'recovered/assets'
    cache.mkdir(parents=True)
    for name in files:
        p = ROOT / name
        sha = p.name.removesuffix('.glb.gz')
        if sha not in wanted or sha in seeded:
            continue
        raw = p.read_bytes()
        if digest(raw) == sha and len(raw) == wanted[sha]:
            (cache / p.name).write_bytes(raw)
            seeded[sha] = name
            refs.append(p)
    inp = LOCAL / 'recovery-inputs.json.gz'
    save(inp, dict(nativeRun=NATIVE_RUN, rows=sorted(sources), sources=sources, native=native))
    print(dict(exactLocalSources=len(seeded), requested=17, packedBytes=sum(wanted.values())), flush=True)
    prepared = shape_prepare.prepare(inp, LOCAL / 'recovered', allow_source=True, workers=2,
                                     env_file=ROOT / '.env.modelling', reservation_receipt=lease)
    rows, missing = [], []
    for row in lookup['rows']:
        match = row['matches'][0]
        model = match['model']
        entry = deepcopy(model['candidate'])
        asset = cache / (entry['sha256'] + '.glb.gz')
        if not asset.exists():
            missing.append(row['uid'])
            continue
        assert digest(asset.read_bytes()) == entry['sha256'] and asset.stat().st_size == entry['bytes']
        entry['rootTranslation'] = [-834500, 0, 816500]
        entry['proceduralWindows'] = False
        assert entry['publicationApproved'] is False and entry['placementReviewed'] is False
        rows.append(dict(uid=row['uid'], source=row['source'], modelId=model['modelId'], triangles=model['triangles'],
                         native=dict(cacheKey=match['nativeCacheKey'], resultSha=match['nativeResultSHA256'], model=model),
                         candidate=dict(path=str(asset.relative_to(ROOT)), entry=entry), originalGeometryOnly=True,
                         sourceSHA256=entry['sha256']))
        refs.append(asset)
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifestpath.read_bytes()) == pins[str(manifestpath.relative_to(ROOT))]
    refs.extend([manifestpath, inp])
    save(DOC / 'selection.json.gz', dict(rows=rows, manifestSHA256=digest(manifestpath.read_bytes())))
    result = dict(uids=sorted(sources), recoveredCount=len(rows), missing=missing, errors=prepared['errors'],
                  methods=prepared['methods'], exactLocalSources=len(seeded), localSourcePaths=seeded,
                  recoveredPackedBytes=sum(r['candidate']['entry']['bytes'] for r in rows),
                  installationApproved=False, identityAccepted=False, physicalAccepted=False, sourceGeometryChanges=0,
                  qualification='17 exact current UID/CSUID-bound indexed originals; verified local bytes preferred, existing guarded acquisition only for missing sources. Immutable original geometry and pose retained. This is source acquisition and an unapproved diagnostic selection, not source identity/placement/support or installation acceptance. No screening or optimisation queue was run.')
    save(DOC / 'summary.json', result)
    refs.extend(p for p in (LOCAL / 'recovered').rglob('*') if p.is_file() and p.suffix != '.zip')
    assert reservations.owns(lease)
    module('southside_project_original_recovery_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-17-project-originals-recovery-and-unapproved-selection', list(dict.fromkeys(refs)), result)
    print(dict(recovered=len(rows), missing=missing, errors=prepared['errors']), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    authenticate(LOOKUP)
    lookup = read(LOOKUP / 'lookup.json')
    claim = reservations.claim('southside-project-originals-' + str(uuid.uuid4()),
                               ['building:' + row['uid'] for row in lookup['rows']], batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
