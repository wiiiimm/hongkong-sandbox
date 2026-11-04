"""Rebind unchanged original candidates to the current catalogue without approval."""
import argparse
from copy import deepcopy
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'prior', 'inventory', 'attributes', 'runtime']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.prior, a.inventory, a.attributes, a.runtime])
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    for name in [a.prior, a.inventory, a.attributes, a.runtime]:
        pins[name] = authenticate(base / name)[1]
        refs.append(base / name / 'result.json')

    def take(name, filename):
        path = base / name / filename
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selected = take(a.prior, 'selection.json.gz')
    rows = deepcopy(selected['rows'])
    attrs = {r['uid']: r for r in take(a.attributes, 'attributes.json.gz')['rows']}
    inventory = take(a.inventory, 'complete-bounds.json.gz')
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifest_path.read_bytes())
    assert manifest_sha == pins[a.inventory][str(manifest_path.relative_to(ROOT))]
    refs.append(manifest_path)
    manifest = read(manifest_path)
    installed = set()
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        assert digest(path.read_bytes()) == pins[a.inventory][str(path.relative_to(ROOT))]
        installed.update(m['uid'] for m in read(path)['models'])
        refs.append(path)
    assert installed == {r['uid'] for r in inventory['rows']}
    assert not installed.intersection(r['uid'] for r in rows)
    # Historical captures remain usable for source-surface diagnostics only if
    # their renderer/coordinate modules still match the current bound inventory.
    for name in ['official-models.js', 'official-model-assets.js', 'geo.js']:
        path = ROOT / '3d-viewer/city' / name
        key = str(path.relative_to(ROOT))
        assert digest(path.read_bytes()) == pins[a.runtime][key] == pins[a.inventory][key]
        refs.append(path)
    for key, sha in pins[a.attributes].items():
        if key.endswith(('.js', '.mjs')):
            path = ROOT / key
            assert digest(path.read_bytes()) == sha
            refs.append(path)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for row in rows:
            uid = row['uid']
            assert uid in attrs
            tile = ROOT / '3d-viewer' / row['source']['tile']
            key = str(tile.relative_to(ROOT))
            assert digest(tile.read_bytes()) == inventory['currentFormTileHashes'][key] == row['source']['tileSHA256']
            assert [f for f in read(tile)['buildings'] if f['uid'] == uid] == [row['source']['building']]
            asset = ROOT / row['candidate']['path']
            assert digest(asset.read_bytes()) == row['sourceSHA256'] == attrs[uid]['sourceSHA256'] == row['candidate']['entry']['sha256']
            native = row['native']
            record = db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s', (native['cacheKey'],)).fetchone()
            assert record and record[0] == native['resultSha']
            assert next(m for m in record[1]['models'] if m['modelId'] == row['modelId']) == native['model']
            assert not any(row['candidate']['entry'].get(k) for k in ['placementReviewed', 'publicationApproved', 'identityReviewApproved', 'sourceIdentityReviewed'])
            refs.extend([tile, asset])
    assert digest(manifest_path.read_bytes()) == manifest_sha
    save(out / 'selection.json.gz', dict(rows=rows, manifestSHA256=manifest_sha))
    result = dict(uids=[r['uid'] for r in rows], currentNativeActors=len(installed), currentManifestSHA256=manifest_sha, sourceGeometryChanges=0, sourcePoseChanges=0, installationApproved=False, publication=False, qualification='Exact assets, current complete forms, native-stage records and unchanged renderer modules verified. Rebinds selection only; no historical physical, identity, terrain, neighbour or publication approval transferred.')
    module('refresh_original_selection_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'current-unchanged-original-selection-rebind', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
