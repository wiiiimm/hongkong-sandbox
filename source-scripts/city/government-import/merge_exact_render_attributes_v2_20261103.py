"""Rebind old attributes after exact current entries/forms/renderer-array parity.

Only the old manifest may differ. All other declared bytes must remain current.
Historical manifests remain separately authenticated; no approval transfers.
"""
import argparse
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

MANIFEST = '3d-viewer/city/data/manifest.json'


def verify_row(source, captured_input, attr, geometry):
    assert source['uid'] == captured_input['uid'] == attr['uid'] == geometry['uid']
    assert source['source']['building'] == captured_input['building']
    assert source['candidate']['entry'] == captured_input['entry']
    assert source['sourceSHA256'] == attr['sourceSHA256'] == geometry['sourceSHA256']
    assert np.array_equal(np.asarray(geometry['index']), np.asarray(attr['completeOriginalIndex']))
    assert np.array_equal(np.asarray(geometry['position']), np.asarray(attr['completeLiteralWorldPosition']))


def add_current_hash(hashes, name, sha, current):
    if name == MANIFEST:
        assert name in hashes and hashes[name] == current(name)
        return
    assert current(name) == sha, name
    assert name not in hashes or hashes[name] == sha, name
    hashes[name] = sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--runtime', required=True)
    parser.add_argument('--attributes', action='append', required=True)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [args.batch, args.runtime, *args.attributes])
    assert len(args.attributes) == len(set(args.attributes)) == 2
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / args.batch, HERE / 'local' / args.batch
    refs, pins = [Path(__file__)], {}

    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selected = take(args.runtime, base / args.runtime / 'selection.json.gz')
    sources = {r['uid']: r for r in selected['rows']}
    assert len(sources) == len(selected['rows']) and sources
    leasefile = local / 'reservation.json'
    if not args.owned:
        assert not local.exists() and not out.exists()
        claim = reservations.claim('exact-current-attribute-rebind-' + str(uuid.uuid4()),
            ['building:' + uid for uid in sources] + ['immutable-source-proof:' + args.batch], batch=args.batch, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], leasefile, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(leasefile)
    assert reservations.owns(lease) and not out.exists()
    current = lambda name: digest((ROOT / name).read_bytes())
    manifest_sha = current(MANIFEST)
    assert selected['manifestSHA256'] == manifest_sha == pins[args.runtime][MANIFEST]
    refs.append(ROOT / MANIFEST)
    hashes = {MANIFEST: manifest_sha}
    geometry = {r['uid']: r for r in take(args.runtime, HERE / 'local' / args.runtime / 'runtime-geometry.json.gz')['rows']}
    assert set(geometry) == set(sources)
    rows, closure, historical = {}, None, []
    for batch in args.attributes:
        data = take(batch, base / batch / 'attributes.json.gz')
        captured = take(batch, base / batch / 'input.json.gz')
        assert data['startEndAllInputsVerified'] is True
        old_inputs = {r['uid']: r for r in captured['rows']}
        assert len(old_inputs) == len(captured['rows']) == len(data['rows'])
        if closure is None:
            closure = data['completeRecursiveProductionModuleClosure']
        else:
            assert closure == data['completeRecursiveProductionModuleClosure']
        for name, sha in pins[batch].items():
            if name != MANIFEST:
                assert current(name) == sha, name
                refs.append(ROOT / name)
        for name, sha in data['inputHashes'].items():
            add_current_hash(hashes, name, sha, current)
            if name != MANIFEST:
                refs.append(ROOT / name)
        historical.append(dict(batch=batch, manifestSHA256=pins[batch][MANIFEST], currentManifestSHA256=manifest_sha))
        for row in data['rows']:
            uid = row['uid']
            assert uid in sources and uid not in rows
            source = sources[uid]
            verify_row(source, old_inputs[uid], row, geometry[uid])
            tile = ROOT / '3d-viewer' / source['source']['tile']
            assert digest(tile.read_bytes()) == source['source']['tileSHA256']
            assert [b for b in read(tile)['buildings'] if b['uid'] == uid] == [source['source']['building']]
            asset = ROOT / source['candidate']['path']
            assert digest(asset.read_bytes()) == source['sourceSHA256']
            refs.extend([tile, asset])
            rows[uid] = row
    assert set(rows) == set(sources) and reservations.owns(lease) and current(MANIFEST) == manifest_sha
    save(out / 'attributes.json.gz', dict(rows=[rows[u] for u in sorted(rows)], inputHashes=hashes,
        completeRecursiveProductionModuleClosure=closure, startEndAllInputsVerified=True,
        exactCurrentRuntimeArraysVerified=True, sourceGeometryChanges=0, currentAcceptance=False,
        nativeReacceptance=False, explicitArithmeticOnlyNotUniversalGPUCameraGuarantee=True))
    result = dict(uids=sorted(rows), sourceSHA256ByUid={u: sources[u]['sourceSHA256'] for u in rows},
        currentManifestSHA256=manifest_sha, historicalManifestBindings=historical,
        completeEntriesAndFormsExactlyEqual=True, exactCurrentLiteralArraysAndIndexesVerified=True,
        allOtherDeclaredBytesUnchanged=True, previousCapturesRecomputed=False,
        sourceGeometryChanges=0, installationApproved=False, physicalAcceptance=False, publication=False,
        qualification=__doc__)
    save(out / 'summary.json', result)
    module('exact_current_attribute_manifest_rebind', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'exact-current-source-entry-form-array-and-module-attribute-reuse', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
