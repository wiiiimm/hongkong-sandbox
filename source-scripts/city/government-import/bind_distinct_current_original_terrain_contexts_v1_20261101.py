"""Bind independently checked bodies to byte-identical current provider terrain.

Historical native terrain identities remain unchanged. This records a distinct
terrain revision and exposes its exact bytes to existing private diagnostics.
"""
import argparse
import copy
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--capture', required=True)
    p.add_argument('--context', action='append', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.capture, *a.context])
    assert 1 <= len(a.context) == len(set(a.context)) <= 8
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    lp = HERE / 'local' / a.batch / 'reservation.json'
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(batch, name):
        if batch not in pins:
            _, pins[batch] = authenticate(base / batch)
            refs.append(base / batch / 'result.json')
        f = base / batch / name
        assert digest(f.read_bytes()) == pins[batch][str(f.relative_to(ROOT))]
        refs.append(f)
        return read(f)
    selection = take(a.capture, 'selection.json.gz')
    selected = {r['uid']: r for r in selection['rows']}
    contexts = [take(n, 'summary.json') for n in a.context]
    rows = [r for c in contexts for r in c['rows']]
    uids = sorted(r['uid'] for r in rows)
    assert len(uids) == len(set(uids)) and set(uids) <= set(selected)
    if not a.owned:
        assert not lp.parent.exists()
        claim = reservations.claim('distinct-current-terrain-binding-' + str(uuid.uuid4()),
            ['building:' + u for u in uids] + ['immutable-source-proof:' + a.batch], batch=a.batch, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(lp)
    assert reservations.owns(lease)
    common_paths, common_hashes, output = None, None, []
    for name, context in zip(a.context, contexts):
        assert not context['installationApproved'] and not context['physicalAcceptance'] and not context['publication']
        for row in context['rows']:
            uid = row['uid']
            source = selected[uid]
            asset = ROOT / source['candidate']['path']
            assert digest(asset.read_bytes()) == row['sourceSHA256'] == source['sourceSHA256']
            assert row['completeSourceFaces'] == source['triangles']
            assert row['uncoveredSourceProjectionAreaM2'] == 0 and not row['missingOriginalTerrain']
            assert row['status'] == 'separate-current-provider-original-tin-source-only-context'
            refs.append(asset)
            hashes = []
            for rawpath in row['sourceTerrainPaths']:
                f = ROOT / rawpath
                assert digest(f.read_bytes()) == pins[name][rawpath]
                refs.append(f)
                buffers = []
                for buffer in read(f)['buffers']:
                    body = f.parent / buffer['uri']
                    assert digest(body.read_bytes()) == pins[name][str(body.relative_to(ROOT))]
                    refs.append(body)
                    buffers.append((buffer['uri'], digest(body.read_bytes())))
                hashes.append((digest(f.read_bytes()), buffers))
            if common_paths is None:
                common_paths, common_hashes = row['sourceTerrainPaths'], hashes
            assert hashes == common_hashes, 'Different current terrain bytes require separate domains'
            bound = copy.deepcopy(row)
            bound.update(sourceTerrainPaths=common_paths, nativeResultSHA256=source['native']['resultSha'],
                nativeBodyCacheKey=source['native']['cacheKey'], historicalNativeTerrainIdentityUnchanged=True,
                terrainMatchesHistoricalNativeRevision=False, originalContextBatch=name)
            output.append(bound)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] and reservations.owns(lease)
    refs.append(manifest)
    result = dict(uids=uids, rows=output, sourceGeometryChanges=0, terrainGeometryChanges=0,
        historicalNativeRecordsChanged=False, physicalAcceptance=False, installationApproved=False, publication=False,
        qualification=__doc__ + ' Native result SHA binds the unchanged building body only; current provider terrain is explicitly a separate revision. Canonical paths are shared only after glTF and every buffer match byte-for-byte. No old scene or acceptance transfer.')
    save(out / 'summary.json', result)
    module('distinct_current_terrain_context_binding', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'distinct-current-original-terrain-byte-identity-context-binding-no-acceptance', list(dict.fromkeys(refs)), result)

if __name__ == '__main__':
    main()
