"""Measure original sources against nominated natives' current BASIC fallback.

Diagnostic only. No dependencies, source geometry, acceptance or viewer writes.
Native detail contacts and BASIC fallback contacts are distinct obligations.
"""
import argparse
from pathlib import Path
import subprocess
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'runtime', 'attributes', 'scope', 'inventory']:
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--uid', action='append', help='Explicit source subset; every nominated native fallback remains required')
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    out = base / args.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        path = base / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(args.runtime, 'selection.json.gz')
    attrs = {r['uid']: r for r in take(args.attributes, 'attributes.json.gz')['rows']}
    scope = take(args.scope, 'summary.json')
    inventory = take(args.inventory, 'complete-bounds.json.gz')
    natives = {r['uid']: r for r in inventory['rows']}
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    sha = digest(manifest.read_bytes())
    assert sha == selection['manifestSHA256'] == scope['currentManifestSHA256']
    assert sha == pins[args.inventory][str(manifest.relative_to(ROOT))]
    refs.append(manifest)
    source_rows = {r['uid']: r for r in selection['rows']}
    assert set(source_rows) == set(scope['uids']) == set(attrs)
    if args.uid:
        assert len(args.uid) == len(set(args.uid)) and set(args.uid) <= set(source_rows)
        source_rows = {u: r for u, r in source_rows.items() if u in args.uid}
        attrs = {u: r for u, r in attrs.items() if u in args.uid}
        scope = {**scope, 'uids': sorted(args.uid), 'rows': [r for r in scope['rows'] if r['uid'] in args.uid]}
    assert set(source_rows) == set(scope['uids']) == set(attrs)
    forms, pairs = {}, []
    for row in scope['rows']:
        assert row['currentNativeActorsChecked'] == len(natives)
        for form in take(args.scope, row['uid'].split('/')[1] + '-forms.json.gz'):
            key = form['building']['uid']
            assert key not in forms or forms[key] == form
            forms[key] = form
        for native in row['nearbyNativeActors']:
            known = natives[native['uid']]
            assert known['sourceSHA256'] == native['sourceSHA256']
            assert known['completeFourWorldBounds'] == native['completeFourWorldBounds']
            pairs.append((row['uid'], native['uid']))
    assert pairs
    missing = {other for _, other in pairs} - forms.keys()
    recovered = []
    for key, expected_sha in inventory['currentFormTileHashes'].items():
        if not missing:
            break
        tile = ROOT / key
        assert digest(tile.read_bytes()) == expected_sha
        matches = [f for f in read(tile)['buildings'] if f['uid'] in missing]
        if not matches:
            continue
        refs.append(tile)
        assert key.startswith('3d-viewer/city/data/tiles/')
        for form in matches:
            uid = form['uid']
            assert uid not in forms
            forms[uid] = dict(building=form, tile=key.removeprefix('3d-viewer/'), tileSHA256=expected_sha)
            recovered.append(dict(uid=uid, tile=key, tileSHA256=expected_sha))
            missing.remove(uid)
    assert not missing, ('Missing current native fallback forms', sorted(missing))
    save(out / 'expanded-current-form-scope.json', dict(rows=recovered, allNominatedFallbacksIncluded=True,
         qualification='Exact installed native fallback forms recovered from the authenticated whole-map current tile census, not invented, suppressed or omitted.'))
    catalogues = {}
    for url in read(manifest)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        refs.append(path)
        for entry in read(path)['models']:
            assert entry['uid'] not in catalogues
            catalogues[entry['uid']] = (entry, path)
    for _, uid in pairs:
        entry, catalogue = catalogues[uid]
        assert entry['sha256'] == natives[uid]['sourceSHA256']
        assert entry['buildingCSUID'] == forms[uid]['building']['buildingCSUID']
        asset = catalogue.parent / entry['asset']
        assert digest(asset.read_bytes()) == entry['sha256']
        refs.append(asset)
    hashes = {}
    for form in forms.values():
        tile = ROOT / '3d-viewer' / form['tile']
        key = str(tile.relative_to(ROOT))
        assert digest(tile.read_bytes()) == form['tileSHA256'] == inventory['currentFormTileHashes'][key]
        assert [b for b in read(tile)['buildings'] if b['uid'] == form['building']['uid']] == [form['building']]
        refs.append(tile)
        hashes[key] = form['tileSHA256']
    input_path, basic_path = out / 'basic-input.json', out / 'basic.json'
    save(input_path, dict(manifestSHA256=sha, currentInputHashes=hashes,
                         rows=[dict(building=f['building'], tile='3d-viewer/' + f['tile']) for f in forms.values()]))
    tool = HERE / 'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs'
    with (out / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str(input_path), str(basic_path)], cwd=ROOT,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    basic = read(basic_path)
    assert basic['startAndEndInputHashesVerified'] and basic['currentManifestSHA256'] == sha
    meshes = {r['uid']: np.asarray(r['position']).reshape(-1, 3)[np.asarray(r['index']).reshape(-1, 3)] for r in basic['rows']}
    results = []
    for uid, other in pairs:
        row, attr = source_rows[uid], attrs[uid]
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == attr['sourceSHA256']
        refs.append(asset)
        index = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
        worlds = {'before-basic': meshes[uid], 'original': decode_original_world_triangles(asset.read_bytes())}
        for mode, key in [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
            worlds[mode] = np.asarray(attr[key]).reshape(-1, 3)[index]
        modes = []
        target = meshes[other]
        for mode, tri in worlds.items():
            proof = exact_finite_contacts(tri, list(range(len(tri))), target, list(range(len(target))))
            assert proof['allPairsExamined'] and proof['sourceFacesOmitted'] == 0
            save(out / (uid.split('/')[1] + '--' + other.split('/')[1] + '--' + mode + '.json.gz'), proof)
            modes.append(dict(mode=mode, completeSourceFaces=len(tri), completeFallbackFaces=len(target),
                              finiteContactPairs=len(proof['contacts']),
                              positiveSurfaceContactPairs=sum(c['sourcePrimitiveDimensionA'] == 2 and c['sourcePrimitiveDimensionB'] == 2 and c['dimension'] > 0 for c in proof['contacts'])))
            print(dict(uid=uid, nativeFallbackUid=other, **modes[-1]), flush=True)
        entry = catalogues[other][0]
        results.append(dict(uid=uid, nativeFallbackUid=other, sourceSHA256=row['sourceSHA256'],
                            nativeSHA256=entry['sha256'], rawCurrentNativeEntry=entry,
                            exactCurrentFallbackForm=forms[other], modes=modes))
    for path, expected in basic['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == expected
        refs.append(ROOT / path)
    assert digest(manifest.read_bytes()) == sha
    result = dict(uids=sorted(source_rows), rows=results, currentManifestSHA256=sha,
                  sourceGeometryChanges=0, nativeMetadataChanges=0, installationApproved=False,
                  publication=False, dependencyApproval=False,
                  qualification='Every nominated native current BASIC fallback is checked against the complete before-BASIC and four unchanged original coordinate streams. Current native detail flags and bytes remain unchanged. Raw contacts require role review; no availability edge, support approval, identity approval or publication is inferred.')
    save(out / 'summary.json', result)
    refs.extend([tool, HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'exact_original_finite_triangle_contacts_20261010.py', HERE / 'exact_original_shell_intersections_20261009.py', HERE / 'exact_original_component_contacts_20261009.py'])
    module('native_fallback_diagnostic_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'complete-original-current-native-basic-fallback-contacts-diagnostic', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
