"""Bind 31 disjoint source-TIN proposals to every current touching actor."""
from islands_direct_stage import ROOT, HERE, read, save, sha, rel
from pathlib import Path


def main():
    base = ROOT / 'docs/astra-city/government-import/government-islands-peng-chau-disjoint-terrain-20261106-v1'
    out = base / 'runtime-current'
    assert not out.exists()
    bounds_path = ROOT / 'docs/astra-city/government-import/government-islands-peng-chau-disjoint-bounds-20261106-v2/complete-bounds.json.gz'
    bounds = read(bounds_path)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    assert sha(manifest_path) == bounds['currentManifest']['sha256']
    selection = read(base / 'selection.json.gz')
    assert selection['manifestSHA256'] == sha(manifest_path)
    identities_path = ROOT / 'docs/astra-city/government-import/government-islands-peng-chau-identity-20261106-v1/identities.json.gz'
    identities = {r['uid']: r for r in read(identities_path)['rows']}
    for row in selection['rows']:
        if identities[row['uid']]['passed']:
            row['identityProof'] = identities[row['uid']]['proof']
    neighbours = read(base / 'neighbour-inputs.json.gz')
    rows = {r['building']['uid']: r for r in neighbours['rows']}
    pins = dict(neighbours['inputHashes'])
    for path, digest in pins.items():
        assert sha(ROOT / path) == digest, path
    forms = {}
    for tile in read(manifest_path)['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        pins[rel(path)] = sha(path)
        for form in read(path)['buildings']:
            forms[form['uid']] = form
    nominations = {}
    for actor in bounds['rows']:
        hit = set()
        for lo, hi in actor['completeFourWorldBounds']:
            for i, patch in enumerate(neighbours['patches']):
                x0, z0, x1, z1 = patch['bounds']
                if hi[0] >= x0 and lo[0] <= x1 and hi[2] >= z0 and lo[2] <= z1:
                    hit.add(i)
        if hit:
            uid = actor['uid']; nominations[uid] = sorted(hit)
            if uid not in rows:
                rows[uid] = {'building': forms[uid], 'patchIndexes': sorted(hit), 'existingNative': True}
            else:
                rows[uid]['patchIndexes'] = sorted(set(rows[uid]['patchIndexes']) | hit)
                rows[uid]['existingNative'] = True
    for path in (Path(__file__), bounds_path, identities_path,
                 bounds_path.parent / 'addition-attributes.json.gz'):
        pins[rel(path)] = sha(path)
    save(out / 'selection.json.gz', selection)
    save(out / 'neighbour-inputs.json.gz', {**neighbours, 'rows': list(rows.values()),
         'inputHashes': pins, 'fullSourceNativeNominations': nominations})
    save(out / 'scope.json', {'currentNativeActors': len(bounds['rows']),
         'affectedForms': len(rows), 'wholeSourceNativeNominations': nominations,
         'sourceGeometryChanges': 0, 'publication': False})
    print({'candidates': len(selection['rows']), 'affectedForms': len(rows), 'nativeNominations': len(nominations)}, flush=True)


if __name__ == '__main__':
    main()
