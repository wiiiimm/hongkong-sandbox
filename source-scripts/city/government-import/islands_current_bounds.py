"""Capture current whole native bounds, reusing only byte-identical old actors.

Read-only diagnostic: includes unused POSITION vertices and four coordinate
streams. No acceptance or terrain changes. Unchanged source metadata/form/module
tuples are mandatory for reuse, not just a matching geometry hash.
"""
import argparse
from pathlib import Path
import subprocess
from islands_direct_stage import ROOT, HERE, read, save, sha, rel
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds


def capture(out):
    assert not out.exists()
    prior = ROOT / 'docs/astra-city/government-import/government-xl-after-parkview16-current-native-bounds-v1-20261104'
    oldbounds = read(prior / 'complete-bounds.json.gz')
    oldinput = read(prior / 'input.json.gz')
    runtime = read(prior / 'inventory.json.gz')
    assert oldinput['currentBoundOnly'] and runtime['startAndEndInputHashesVerified']
    assert runtime['wholeUnusedPositionVerticesIncluded'] and not runtime['errors']
    for path, digest in runtime['inputHashes'].items():
        if path.startswith('3d-viewer/') and not path.startswith('3d-viewer/city/data/'):
            assert sha(ROOT / path) == digest, path
    old = {r['uid']: r for r in oldbounds['rows']}
    oldtuples = {r['uid']: r for r in oldinput['rows']}
    assert len(old) == 7109 and set(old) == set(oldtuples)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = sha(manifest_path)
    manifest = read(manifest_path)
    models, refs = {}, []
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        refs.append({'path': rel(path), 'sha256': sha(path)})
        for entry in read(path)['models']:
            assert entry['uid'] not in models
            asset = path.parent / entry['asset']
            assert sha(asset) == entry['sha256']
            models[entry['uid']] = {'entry': entry, 'path': rel(asset)}
    assert set(old) <= set(models)
    forms = {}
    for tile in manifest['tiles']:
        for form in read(ROOT / '3d-viewer' / tile['url'])['buildings']:
            if form['uid'] in models:
                assert form['uid'] not in forms
                forms[form['uid']] = form
    assert set(forms) == set(models)
    for uid, row in oldtuples.items():
        assert models[uid]['entry'] == row['rawCurrentEntry']
        assert forms[uid] == row['currentBuilding']
        assert models[uid]['entry']['sha256'] == old[uid]['sourceSHA256'] == row['source']['sha256']
    additions = sorted(set(models) - set(old))
    frozen = {'currentManifest': {'path': rel(manifest_path), 'sha256': manifest_sha},
              'currentCatalogueRefs': refs, 'evidenceRefs': [],
              'expectedSourceByUid': {u: [models[u]['entry']['sha256'], models[u]['entry']['triangles']] for u in additions},
              'rows': [{'uid': u, **models[u], 'building': forms[u]} for u in additions]}
    save(out / 'addition-input.json.gz', frozen)
    # The unchanged renderer capture accepts at most 40 exact actors per call.
    # Keep that guard and aggregate independently bound, disjoint captures.
    attributes = {'rows': [], 'inputHashes': {}, 'chunkRefs': [],
                  'startEndAllInputsVerified': True, 'sourceGeometryChanges': 0}
    for start in range(0, len(additions), 40):
        members = additions[start:start + 40]
        chunk = {**frozen, 'rows': frozen['rows'][start:start + 40],
                 'expectedSourceByUid': {u: frozen['expectedSourceByUid'][u] for u in members}}
        inp = out / f'addition-chunk-{start // 40:03d}-input.json.gz'
        dst = out / f'addition-chunk-{start // 40:03d}-attributes.json.gz'
        save(inp, chunk)
        subprocess.run(['node', str(HERE / 'selected_original_render_attributes_v1.mjs'),
                        rel(inp), rel(dst)], cwd=ROOT, check=True)
        captured = read(dst)
        assert captured['startEndAllInputsVerified']
        assert [r['uid'] for r in captured['rows']] == members
        assert captured['sourceGeometryChanges'] == 0
        for path, digest in captured['inputHashes'].items():
            assert sha(ROOT / path) == digest, path
            assert path not in attributes['inputHashes'] or attributes['inputHashes'][path] == digest
            attributes['inputHashes'][path] = digest
        attributes['rows'].extend(captured['rows'])
        attributes['chunkRefs'].append({'path': rel(dst), 'sha256': sha(dst),
                                       'input': rel(inp), 'inputSHA256': sha(inp)})
    assert [r['uid'] for r in attributes['rows']] == additions
    for path, digest in attributes['inputHashes'].items():
        assert sha(ROOT / path) == digest, path
    save(out / 'addition-attributes.json.gz', attributes)
    bounds = list(old.values())
    for row in attributes['rows']:
        proof = packed_world_bounds((ROOT / models[row['uid']]['path']).read_bytes())
        assert proof['completeOriginalTriangles'] == models[row['uid']]['entry']['triangles']
        bounds.append({'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'],
                       'completeFourWorldBounds': [proof['originalWholeSourceBounds'], row['completeLiteralWorldBounds'],
                          row['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],
                          row['completeExplicitBalancedFloat32ModelMatrixWorldBounds']],
                       'completeOriginalPOSITIONProof': proof})
    assert len(bounds) == len(models) and sha(manifest_path) == manifest_sha
    save(out / 'complete-bounds.json.gz', {'rows': bounds, 'currentManifest': frozen['currentManifest'],
         'oldExactBoundsReused': len(old), 'freshAdditions': len(additions),
         'verifiedCurrentEntryAndFormTuples': True, 'sourceGeometryChanges': 0})
    print({'nativeActors': len(models), 'reused': len(old), 'fresh': len(additions)}, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    capture(parser.parse_args().output.resolve())
