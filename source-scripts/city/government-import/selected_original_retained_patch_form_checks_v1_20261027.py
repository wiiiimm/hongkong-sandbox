"""Run unchanged base-form regression checks with one explicitly retained flat native replacement."""
import argparse
import subprocess
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'scope', 'inventory', 'patch']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / args.batch
    assert not doc.exists()
    refs, receipts, pins = [Path(__file__)], {}, {}
    for name in [args.scope, args.inventory, args.patch]:
        receipt, bound = authenticate(base / name)
        receipts[name] = receipt
        refs.append(base / name / 'result.json')
        for key, sha in bound.items():
            assert key not in pins or pins[key] == sha
            pins[key] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    scope = take(base / args.scope / 'scope.json')
    # Exact explicit replacement is verified below before any inputs are emitted.
    forms = take(base / args.scope / 'form-obligations.json.gz')
    inventory = take(base / args.inventory / 'complete-bounds.json.gz')
    native = {r['uid'] for r in inventory['rows']}
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = take(manifestpath)
    tiles = {r['id']: r for r in manifest['tiles']}
    loaded, hashes = {}, {str(manifestpath.relative_to(ROOT)): digest(manifestpath.read_bytes())}
    for form in forms:
        tileid = form['tile']
        if tileid not in loaded:
            path = ROOT / '3d-viewer' / tiles[tileid]['url']
            loaded[tileid] = {b['uid']: b for b in take(path)['buildings']}
            hashes[str(path.relative_to(ROOT))] = digest(path.read_bytes())
        assert loaded[tileid][form['uid']] == form
    candidate = receipts[args.patch]['candidate']
    path = ROOT / candidate['path']
    assert digest(path.read_bytes()) == candidate['sha256']
    refs.append(path)
    from flat_native_replacement_scope_v1_20261027 import verify
    receipt = receipts[args.patch]
    records = receipt.get('replacedNativeTerrain', [])
    assert len(records) == 1
    old = records[0]
    assert old['url'] in {r['url'] for r in manifest['terrainPatches']}
    oldpath = ROOT / '3d-viewer' / old['url']
    assert digest(oldpath.read_bytes()) == old['sha256']
    refs.extend([oldpath, HERE / 'flat_native_replacement_scope_v1_20261027.py'])
    replacement = verify(scope, receipt, read(oldpath), read(path))
    patch = dict(**candidate, replaces=replacement, uids=scope['uids'], bounds=scope['regionalParentExtent'])
    save(doc / 'neighbour-inputs.json.gz', dict(inputHashes=hashes, candidateIds=scope['uids'], patches=[patch], rows=[dict(building=b, existingNative=b['uid'] in native, patchIndexes=[0]) for b in forms]))
    tool = HERE / 'check-neighbours.mjs'
    with (doc / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str(doc.relative_to(ROOT)) + '/'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    checks = read(doc / 'neighbour-checks.json')
    assert len(checks['rows']) == len(forms)
    flagged = [r for r in checks['rows'] if r['reasons']]
    result = dict(uids=scope['uids'], forms=len(forms), flagged=flagged, ordinaryFlagged=sum(not r['existingNative'] for r in flagged), installationApproved=False, publication=False, sourceGeometryChanges=0, scriptExternalAICalls=0)
    save(doc / 'summary.json', result)
    for name, sha in checks['inputHashes'].items():
        assert digest((ROOT / name).read_bytes()) == sha
        refs.append(ROOT / name)
    refs.append(tool)
    module('selected_form_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'whole-selected-wrapper-form-regression', list(dict.fromkeys(refs)), result)
    print(dict(forms=len(forms), flagged=len(flagged), ordinaryFlagged=result['ordinaryFlagged']), flush=True)


if __name__ == '__main__':
    main()
