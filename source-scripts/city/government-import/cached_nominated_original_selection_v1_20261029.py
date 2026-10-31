"""Bind already cached nominated originals without acquisition or conversion.

This does not call or alter the archive recovery worker or its 3 GiB guard.
Missing bytes fail closed. Original assets remain at their existing paths.
"""
import argparse
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import uuid
from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--lookup', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.lookup])
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / a.batch, HERE / 'local' / a.batch
    assert not out.exists()
    lookup_dir = base / a.lookup
    _, pins = authenticate(lookup_dir)
    path = lookup_dir / 'lookup.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    lookup = read(path)
    rows = lookup['rows']
    assert 0 < len(rows) <= 20 and len(rows) == len({r['uid'] for r in rows})
    assert all(len(r['matches']) == 1 and r['matches'][0]['model'].get('candidate') for r in rows)
    leasepath = local / 'reservation.json'
    resources = ['building:' + r['uid'] for r in rows]
    resources += ['native-model:' + r['matches'][0]['sourceKey'] for r in rows]
    if not a.owned:
        assert not local.exists()
        claim = reservations.claim('cached-original-selection-' + str(uuid.uuid4()),
                                   sorted(resources), batch=a.batch, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], leasepath,
            [sys.executable, __file__, '--batch', a.batch, '--lookup', a.lookup, '--owned'])
    lease = read(leasepath)
    assert reservations.owns(lease)
    refs = [Path(__file__), lookup_dir / 'result.json', path]
    assets = subprocess.check_output(['rg', '--files', '--hidden', '--no-ignore',
        '-g', '*.glb.gz', 'source-scripts/city', '3d-viewer/city/data'],
        cwd=ROOT, text=True).splitlines()
    selected = []
    with connect() as db:
        db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        for row in rows:
            match = row['matches'][0]
            current = db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',
                                 (match['nativeCacheKey'],)).fetchone()
            model, form = match['model'], row['source']['building']
            assert current and current[0] == match['nativeResultSHA256']
            assert next(m for m in current[1]['models'] if m['modelId'] == model['modelId']) == model
            entry = deepcopy(model['candidate'])
            for x, y in [('uid', 'uid'), ('objectId', 'objectId'), ('buildingCSUID', 'buildingCSUID'),
                         ('recordedBaseHeight', 'baseHeightHKPD'), ('recordedTopHeight', 'topHeightHKPD')]:
                assert entry[x] == form[y]
            assert entry['sha256'] == model['asset']['sha256'] and entry['bytes'] <= 2 * 1024**2
            assert entry['publicationApproved'] is False and entry['placementReviewed'] is False
            tile = ROOT / '3d-viewer' / row['source']['tile']
            assert digest(tile.read_bytes()) == row['source']['tileSHA256']
            assert [b for b in read(tile)['buildings'] if b['uid'] == row['uid']] == [form]
            refs.append(tile)
            wanted = entry['sha256'] + '.glb.gz'
            found = None
            for filename in assets:
                asset = ROOT / filename
                if asset.name != wanted:
                    continue
                raw = asset.read_bytes()
                if len(raw) == entry['bytes'] and digest(raw) == entry['sha256']:
                    found = asset
                    break
            assert found is not None, 'Cached original absent; use guarded acquisition separately'
            refs.append(found)
            entry['rootTranslation'] = [-834500, 0, 816500]
            entry['proceduralWindows'] = False
            selected.append(dict(uid=row['uid'], source=row['source'], modelId=model['modelId'],
                triangles=model['triangles'], native=dict(cacheKey=match['nativeCacheKey'],
                resultSha=match['nativeResultSHA256'], model=model),
                candidate=dict(path=str(found.relative_to(ROOT)), entry=entry),
                originalGeometryOnly=True, sourceSHA256=entry['sha256']))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    refs.append(manifest)
    save(out / 'selection.json.gz', dict(rows=selected, manifestSHA256=digest(manifest.read_bytes())))
    result = dict(uids=sorted(r['uid'] for r in rows), cachedOriginals=len(selected),
        downloads=0, conversions=0, copiedAssetBytes=0, sourceGeometryChanges=0,
        identityAccepted=False, physicalAccepted=False, installationApproved=False,
        publication=False, newlyInstalled=0,
        qualification='Existing packed bytes only, freshly hash/size checked against exact current UID/CSUID and immutable native result. No archive access, conversion, acquisition worker guard change or prior acceptance transfer.')
    save(out / 'summary.json', result)
    assert reservations.owns(lease)
    module('cached_nominated_original_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'exact-existing-cached-original-selection-no-acquisition', refs, result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
