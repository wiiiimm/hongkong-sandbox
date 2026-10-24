"""Diagnose a proposed original against an unchanged installed native support.

Read-only diagnostic. Rebinds historical arrays only when all captured inputs
except the explicitly superseded manifest remain byte identical, and verifies
current raw catalogue membership and current complete inventory bounds. No
approval, dependency metadata, geometry, terrain or publication is changed.
"""
import argparse
from pathlib import Path
import subprocess
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_four_world_contact_paths_v1_20261023 import paths
from pool_incident_wall_contacts_v1_20261017 import closest

FIELDS = [('literal', 'completeLiteralWorldPosition'),
          ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
          ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]
BASE = ROOT / 'docs/astra-city/government-import'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'attributes', 'inventory', 'native-contacts',
                'historical-attributes', 'uid', 'support']:
        parser.add_argument('--' + key, required=True)
    a = parser.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    out = BASE / a.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    def doc(batch, name):
        return take(batch, BASE / batch / name)

    selection = doc(a.runtime, 'selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid'] == a.uid)
    geom = next(r for r in take(a.runtime, HERE / 'local' / a.runtime / 'runtime-geometry.json.gz')['rows'] if r['uid'] == a.uid)
    source_attrs = doc(a.attributes, 'attributes.json.gz')
    assert source_attrs['startEndAllInputsVerified']
    child = next(r for r in source_attrs['rows'] if r['uid'] == a.uid)
    old_child = next(r for r in doc(a.historical_attributes, 'attributes.json.gz')['rows'] if r['uid'] == a.uid)
    assert child == old_child, 'Historical contact source arrays changed'
    native_input = doc(a.native_contacts, 'native-input.json.gz')
    native_attrs = doc(a.native_contacts, 'native-attributes.json.gz')
    assert native_attrs['startEndAllInputsVerified'] and native_attrs['productionCataloguePreparationReplayed']
    original_native = next(r for r in native_input['rows'] if r['uid'] == a.support)
    parent = next(r for r in native_attrs['rows'] if r['uid'] == a.support)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    current_sha = digest(manifest.read_bytes())
    assert current_sha == selection['manifestSHA256']
    # The sole allowed historical-input difference is the additive manifest.
    for name, sha in native_attrs['inputHashes'].items():
        path = ROOT / name
        if path == manifest:
            continue
        assert digest(path.read_bytes()) == sha, name
        refs.append(path)
    current = read(manifest)
    cat = ROOT / original_native['cataloguePath']
    assert cat in [ROOT / '3d-viewer' / url for url in current['officialModelCatalogues']]
    entries = [r for r in read(cat)['models'] if r['uid'] == a.support]
    assert entries == [original_native['entry']]
    inventory = doc(a.inventory, 'complete-bounds.json.gz')
    assert pins[a.inventory][str(manifest.relative_to(ROOT))] == current_sha
    bound = next(r for r in inventory['rows'] if r['uid'] == a.support)
    assert bound['sourceSHA256'] == parent['sourceSHA256'] == entries[0]['sha256']
    for i, key in enumerate(['completeLiteralWorldBounds', 'completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds', 'completeExplicitBalancedFloat32ModelMatrixWorldBounds'], 1):
        assert parent[key] == bound['completeFourWorldBounds'][i]
    refs.extend([manifest, cat])
    worlds = {}
    for uid, attr, asset, sha in [(a.uid, child, ROOT / row['candidate']['path'], row['sourceSHA256']),
                                  (a.support, parent, ROOT / original_native['path'], entries[0]['sha256'])]:
        raw = asset.read_bytes()
        assert digest(raw) == sha == attr['sourceSHA256']
        refs.append(asset)
        index = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
        worlds[uid] = {'original': decode_original_world_triangles(raw), **{
            mode: np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[index]
            for mode, field in FIELDS}}
    actual = np.asarray(geom['position']).reshape(-1, 3)[np.asarray(geom['index']).reshape(-1, 3)]
    assert np.array_equal(actual, worlds[a.uid]['literal'])
    ground = np.asarray(geom['drawnGroundGeometry']).reshape(-1, 3, 3)
    form = row['source']['building']
    polygon = Polygon(form['rings'][0], form['rings'][1:])
    final = module('installed_support_foundation', HERE / 'xl-final-script-pass.py')
    tool = HERE / 'wave_retained_basic_support_v1_20261017.mjs'
    rows = []
    for mode, triangles in worlds[a.uid].items():
        support = worlds[a.support][mode]
        folder = out / mode
        position = triangles.reshape(-1).tolist()
        save(folder / 'input.json.gz', dict(rows=[dict(uid=a.uid, position=position, index=list(range(len(position) // 3)))], podium=support.tolist()))
        with (folder / 'worker.log').open('w') as log:
            subprocess.run(['node', str(tool), str(folder.relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        result = read(folder / 'support.json.gz')
        proof = result['rows'][0]['proof']
        assert result['rows'][0]['uid'] == a.uid
        for name, sha in result['inputHashes'].items():
            assert digest((ROOT / name).read_bytes()) == sha
            refs.append(ROOT / name)
        contact_name = a.uid.split('/')[1] + '--' + a.support.split('/')[1] + '--' + mode + '.json.gz'
        contacts = doc(a.native_contacts, contact_name)
        targets = []
        lo, hi = triangles.min(1), triangles.max(1)
        for witness in proof['unresolved']:
            point = np.asarray(witness['position'])
            broad = np.flatnonzero(np.all(lo <= point + .001, axis=1) & np.all(hi >= point - .001, axis=1))
            incident = [int(i) for i in broad if np.linalg.norm(np.cross(triangles[i, 1] - triangles[i, 0], triangles[i, 2] - triangles[i, 0])) > 0 and np.linalg.norm(closest(point, triangles[i]) - point) <= .001]
            assert incident
            targets.append(dict(witness=witness, incidentFaces=incident))
        verified = paths(triangles, dict(targets=targets, proof=contacts))
        foundation = final.foundation_context(triangles, np.concatenate([ground, support]), polygon)
        item = dict(mode=mode, support=proof, compoundFoundation=foundation,
                    unresolved=len(targets), finitePaths=sum(r['verifiedPath'] is not None for r in verified),
                    sourceWorldSHA256ByUid={uid: digest(w[mode].astype('<f8').tobytes()) for uid, w in worlds.items()})
        save(folder / 'diagnostic.json.gz', dict(**item, paths=verified))
        rows.append(item)
        print({k: item[k] for k in ['mode', 'unresolved', 'finitePaths']}, flush=True)
    summary = dict(uids=[a.uid, a.support], supportedUid=a.uid, installedSupportUid=a.support, currentManifestSHA256=current_sha,
                   historicalManifestSHA256=native_input['currentManifest']['sha256'],
                   historicalSourceArraysIdentical=True, allOtherHistoricalNativeInputsIdentical=True,
                   rows=rows, installationApproved=False, physicalSupportAccepted=False,
                   sourceGeometryChanges=0, nativeMetadataChanges=0, terrainEdits=False)
    save(out / 'summary.json', summary)
    refs += [HERE / n for n in ['xl-final-script-pass.py', 'original_four_world_contact_paths_v1_20261023.py', 'pool_incident_wall_contacts_v1_20261017.py', 'exact_packed_world_geometry_20261009.py']]
    module('installed_support_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'proposed-original-unchanged-installed-support-diagnostic', list(dict.fromkeys(refs)), summary)


if __name__ == '__main__':
    main()
