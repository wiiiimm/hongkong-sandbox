"""Validate and check a current scene with two disjoint private original-TIN insets.

No installation, support replacement or publication approval is produced.
"""
import argparse
from pathlib import Path
import subprocess
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'inventory']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.runtime, a.inventory])
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    for name in [a.runtime, a.inventory]:
        _, pins[name] = authenticate(base / name)
        refs.append(base / name / 'result.json')

    def take(name, path):
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    inventory = take(a.inventory, base / a.inventory / 'complete-bounds.json.gz')
    selection = take(a.runtime, base / a.runtime / 'selection.json.gz')
    candidates = take(a.runtime, base / a.runtime / 'terrain-candidates.json')
    assert len(candidates) == 2
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = take(a.inventory, manifestpath)
    manifest_sha = digest(manifestpath.read_bytes())
    assert manifest_sha == selection['manifestSHA256']
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    root = take(a.runtime, rootpath)
    builder = module('disjoint_scene_extent', HERE / 'resolve_pass_indexed_parent_clipping_v2.py')
    domains, effective = [], []
    for candidate in candidates:
        path = ROOT / candidate['path']
        patch = take(a.runtime, path)
        assert digest(path.read_bytes()) == candidate['sha256']
        builder.validate_patch(patch, root)
        bounds = builder.extent(patch['coarseCells'], root)
        domain = shapely.box(*bounds)
        values = np.asarray(patch['nativeMesh']['position']).reshape(-1, 3)
        for coords in [values, values.astype('float32').astype('float64')]:
            assert domain.covers(shapely.box(*[float(x) for x in [coords[:,0].min(), coords[:,2].min(), coords[:,0].max(), coords[:,2].max()]]))
        domains.append(domain)
        assert list(bounds) == candidate['bounds']
        effective.append(dict(**candidate))
    assert domains[0].intersection(domains[1]).area == 0
    domain = shapely.union_all(domains)
    terrain = []
    for entry in manifest['terrainPatches']:
        path = ROOT / '3d-viewer' / entry['url']
        refs.append(path)
        node = read(path)
        extent = builder.extent(node['coarseCells'], root)
        contacts = []
        def visit(item, hierarchy):
            if 'nativeMesh' in item:
                xyz = np.asarray(item['nativeMesh']['position']).reshape(-1, 3)
                xyz = np.concatenate([xyz, xyz.astype('float32').astype('float64')])
                box = shapely.box(float(xyz[:,0].min()), float(xyz[:,2].min()), float(xyz[:,0].max()), float(xyz[:,2].max()))
                if domain.intersects(box):
                    contacts.append(dict(hierarchy=hierarchy, packedBounds=list(box.bounds), overlapAreaM2=domain.intersection(box).area))
            for i, child in enumerate(item.get('patches', [])):
                visit(child, hierarchy + [i])
        visit(node, [])
        area = domain.intersection(shapely.box(*extent)).area
        if contacts or area > 0:
            terrain.append(dict(url=entry['url'], coarseOverlapAreaM2=area, packedContacts=contacts))
    assert not any(t['coarseOverlapAreaM2'] > 0 or any(c['overlapAreaM2'] > 0 for c in t['packedContacts']) for t in terrain), 'Explicit retained-terrain review required'
    forms = []
    hashes = {str(manifestpath.relative_to(ROOT)): manifest_sha}
    for entry in manifest['tiles']:
        path = ROOT / '3d-viewer' / entry['url']
        key = str(path.relative_to(ROOT))
        assert digest(path.read_bytes()) == inventory['currentFormTileHashes'][key]
        refs.append(path)
        for form in read(path)['buildings']:
            points = [v for ring in form.get('rings', []) for v in ring]
            if not points:
                continue
            points = np.asarray(points)
            box = shapely.box(float(points[:,0].min()), float(points[:,1].min()), float(points[:,0].max()), float(points[:,1].max()))
            indices = [i for i, own in enumerate(domains) if own.intersects(box)]
            if indices:
                forms.append(dict(building=form, patchIndexes=indices))
                hashes[key] = inventory['currentFormTileHashes'][key]
    assert len(forms) == len({r['building']['uid'] for r in forms})
    native = {r['uid'] for r in inventory['rows']}
    obligations = [r for r in inventory['rows'] if not closed_disjoint(r['completeFourWorldBounds'], list(domain.bounds))]
    uids = [r['uid'] for r in selection['rows']]
    save(out / 'scope.json', dict(uids=uids, currentManifestSHA256=manifest_sha, currentNativeActors=len(native), terrainContacts=terrain, positiveAreaTerrainOverlaps=0, touchingNativeUids=[r['uid'] for r in obligations], intersectingForms=len(forms), domainWKT=domain.wkt, patches=effective, installationApproved=False))
    save(out / 'native-obligations.json.gz', obligations)
    save(out / 'neighbour-inputs.json.gz', dict(inputHashes=hashes, candidateIds=uids, patches=effective, rows=[dict(**r, existingNative=r['building']['uid'] in native) for r in forms]))
    tool = HERE / 'check-neighbours.mjs'
    with (out / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str(out.relative_to(ROOT)) + '/'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    checks = read(out / 'neighbour-checks.json')
    assert len(checks['rows']) == len(forms)
    for name, sha in checks['inputHashes'].items():
        assert digest((ROOT / name).read_bytes()) == sha
        refs.append(ROOT / name)
    assert digest(manifestpath.read_bytes()) == manifest_sha
    flagged = [r for r in checks['rows'] if r['reasons']]
    result = dict(uids=uids, currentManifestSHA256=manifest_sha, currentNativeActors=len(native), forms=len(forms), flagged=flagged, touchingNativeUids=[r['uid'] for r in obligations], terrainContacts=terrain, bothCandidatesRevalidated=True, disjointPositiveArea=True, sourceGeometryChanges=0, installationApproved=False, publication=False, qualification='Fresh validation and complete closed union-domain ordinary-form diagnostics. All new source forms are co-import candidates, not silently credited as retained basics. Every changed native requires full-mesh checks. Shared-edge compatibility, source support, identity, retained dependency replacement and browser approval remain separate.')
    save(out / 'summary.json', result)
    refs += [tool, HERE / 'resolve_pass_indexed_parent_clipping_v2.py', HERE / 'heritage_saved_native_bounds_binding_v1_20261014.py']
    module('disjoint_scene_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'current-disjoint-original-terrain-pair-complete-scene-diagnostics', list(dict.fromkeys(refs)), result)
    print(dict(forms=len(forms), flagged=flagged, native=range(len(obligations))), flush=True)


if __name__ == '__main__':
    main()
