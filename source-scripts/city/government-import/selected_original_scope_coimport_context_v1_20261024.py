"""Bind exact co-import candidates to an existing complete terrain scene scope.

Changes diagnostic candidate membership only. No retained native or unrelated
basic is omitted; source acceptance and replacement review remain separate.
"""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'scope', 'runtime']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.scope, a.runtime])
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    for name in [a.scope, a.runtime]:
        _, pins[name] = authenticate(base / name)
        refs.append(base / name / 'result.json')
    def take(name, filename):
        path = base / name / filename
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    scope = take(a.scope, 'scope.json')
    forms = take(a.scope, 'form-obligations.json.gz')
    native = take(a.scope, 'native-obligations.json.gz')
    selection = take(a.runtime, 'selection.json.gz')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == pins[a.scope][str(manifest.relative_to(ROOT))]
    refs.append(manifest)
    byuid = {f['uid']: f for f in forms}
    uids = [r['uid'] for r in selection['rows']]
    assert len(uids) == len(set(uids)) and set(scope['uids']) <= set(uids)
    installed = set()
    for url in read(manifest)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        installed.update(m['uid'] for m in read(path)['models'])
        refs.append(path)
    assert not installed.intersection(uids)
    for row in selection['rows']:
        assert byuid[row['uid']] == row['source']['building']
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert digest(tile.read_bytes()) == row['source']['tileSHA256']
        assert [f for f in read(tile)['buildings'] if f['uid'] == row['uid']] == [row['source']['building']]
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == row['candidate']['entry']['sha256']
        refs.extend([tile, asset])
    scope['uids'] = uids
    scope['coImportContextOnly'] = True
    save(out / 'scope.json', scope)
    save(out / 'form-obligations.json.gz', forms)
    save(out / 'native-obligations.json.gz', native)
    save(out / 'summary.json', dict(uids=uids, forms=len(forms), touchingNativeUids=scope['touchingNativeUids'], installationApproved=False, publication=False, sourceGeometryChanges=0, qualification='Same complete forms and native obligations, with exact current original co-import rows explicitly bound. Candidate membership conveys no physical/identity/support or installation approval.'))
    # Bind every prior current-scene input without changing its bytes.
    for key, sha in pins[a.scope].items():
        path = ROOT / key
        assert digest(path.read_bytes()) == sha
        refs.append(path)
    module('original_scope_coimport_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'explicit-current-original-coimport-scene-context', list(dict.fromkeys(refs)), read(out / 'summary.json'))


if __name__ == '__main__':
    main()
