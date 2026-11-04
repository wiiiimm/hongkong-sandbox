"""Bind an already checked explicit flat replacement to the native regression schema.

Uses the same existing replacement contract as the full BASIC regression. This
is metadata only; retained source/terrain geometry approval remains outstanding.
"""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from flat_native_replacement_collection_v1_20261028 import verify
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'patch', 'scope', 'form-checks', 'lease-file']:
        p.add_argument('--' + name, required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.patch, a.scope, a.form_checks])
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    lease = read(Path(a.lease_file))
    assert reservations.owns(lease)
    pins, receipts, refs = {}, {}, [Path(__file__), HERE / 'flat_native_replacement_collection_v1_20261028.py']
    for batch in [a.patch, a.scope, a.form_checks]:
        receipts[batch], pins[batch] = authenticate(base / batch)
        refs.append(base / batch / 'result.json')

    def take(batch, path):
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    scope = take(a.scope, base / a.scope / 'scope.json')
    forms = take(a.scope, base / a.scope / 'form-obligations.json.gz')
    required = {('building:' if b['uid'].startswith('landsd/') else 'source-form:') + b['uid'] for b in forms}
    required.update('building:' + u for u in scope['uids'])
    required.add('terrain:city/data/terrain.json')
    proposal = receipts[a.patch]
    assert proposal['status'] == 'private-terrain-validator-passed' and proposal['installationApproved'] is False
    candidate = proposal['candidate']
    path = ROOT / candidate['path']
    patch = take(a.patch, path)
    assert digest(path.read_bytes()) == candidate['sha256']
    originals = {}
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    current = take(a.scope, manifest)
    for r in proposal['replacedNativeTerrain']:
        assert r['url'] in {q['url'] for q in current['terrainPatches']}
        old = ROOT / '3d-viewer' / r['url']
        assert digest(old.read_bytes()) == r['sha256']
        refs.append(old)
        originals[r['url']] = read(old)
        required.add('terrain:' + r['url'])
    assert required <= set(lease['resources'])
    replacements = verify(scope, proposal, originals, patch)
    binding = dict(replaces=replacements[0]) if len(replacements) == 1 else dict(replacesMany=replacements)
    expected = dict(**candidate, **binding, uids=scope['uids'], bounds=scope['regionalParentExtent'])
    checked = take(a.form_checks, base / a.form_checks / 'neighbour-inputs.json.gz')
    assert checked['patches'] == [expected] and checked['candidateIds'] == scope['uids']
    assert checked['rows'] and [r['building'] for r in checked['rows']] == forms
    for path, sha in checked['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    assert digest(manifest.read_bytes()) == checked['inputHashes'][str(manifest.relative_to(ROOT))]
    result = dict(uids=scope['uids'], candidate=expected, sourceSHA256ByUid=proposal['sourceSHA256ByUid'], replacedNativeTerrain=proposal['replacedNativeTerrain'], currentManifestSHA256=digest(manifest.read_bytes()), sourceGeometryChanges=0, terrainGeometryChanges=0, installationApproved=False, publication=False, qualification='Exact already-emitted BASIC regression input bound to the same existing flat-native replacement metadata contract. Every raw BASIC flag remains. No retained-triangle identity, physical, native-source, support, browser or publication approval is granted; unchanged full native regression remains required.')
    save(out / 'summary.json', result)
    assert reservations.owns(lease)
    module('flat_original_replacement_schema_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'existing-flat-replacement-exact-regression-schema-binding-only', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
