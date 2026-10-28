"""Check every scoped BASIC form for a new civic root-terrain inset.

Fail closed if any installed native actor or existing terrain patch touches the
domain: those cases require the separate full native/retained checks.
No source, terrain, acceptance policy or public viewer files are changed.
"""
import argparse
import sys
import uuid
import subprocess
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

BASE = ROOT / 'docs/astra-city/government-import'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--site', choices=['sha-tin', 'kowloon-city'], required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    count = 'four' if a.site == 'sha-tin' else 'three'
    prefix = f'government-xl-{a.site}-civic-{count}'
    batch = prefix + '-root-form-regression-v1-20261029'
    out, local = BASE / batch, HERE / 'local' / batch
    assert not out.exists()
    scope_name = prefix + '-terrain-scope-v1-20261029'
    runtime_name = prefix + '-proposed-ground-v1-20261029'
    inventory_name = 'government-xl-after-elegant-current-inventory-v1-20261029'
    refs, pins = [Path(__file__)], {}

    def take(name, filename):
        if name not in pins:
            _, pins[name] = authenticate(BASE / name)
            refs.append(BASE / name / 'result.json')
        path = BASE / name / filename
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    scope = take(scope_name, 'scope.json')
    assert scope['currentNativeActors'] == 7007
    assert not scope['touchingNativeUids'], 'Full native mesh regressions required'
    assert not scope['terrainContacts'], 'Existing terrain retention required'
    assert scope['positiveAreaTerrainOverlaps'] == 0
    forms = take(scope_name, 'form-obligations.json.gz')
    assert len(forms) == scope['intersectingForms']
    assert len(forms) == len({b['uid'] for b in forms})
    assert not any(b.get('modelGeometry') for b in forms)
    leasepath = local / 'reservation.json'
    resources = ['building:' + b['uid'] for b in forms]
    resources += ['terrain:city/data/terrain.json']
    if not a.owned:
        assert not local.exists()
        claim = reservations.claim('civic-root-regression-' + str(uuid.uuid4()),
                                   sorted(set(resources)), batch=batch, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], leasepath,
            [sys.executable, __file__, '--site', a.site, '--owned'])
    lease = read(leasepath)
    assert set(resources) <= set(lease['resources']) and reservations.owns(lease)
    inventory = take(inventory_name, 'complete-bounds.json.gz')
    installed = {r['uid'] for r in inventory['rows']}
    assert not installed.intersection(b['uid'] for b in forms)
    patches = take(runtime_name, 'terrain-candidates.json')
    assert len(patches) == 1 and set(patches[0]['uids']) == set(scope['uids'])
    assert not patches[0].get('replaces') and not patches[0].get('replacesMany')
    path = ROOT / patches[0]['path']
    assert digest(path.read_bytes()) == patches[0]['sha256']
    refs.append(path)
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    manifestsha = digest(manifestpath.read_bytes())
    assert manifestsha == pins[inventory_name][str(manifestpath.relative_to(ROOT))]
    refs.append(manifestpath)
    tiles = {t['id']: t for t in read(manifestpath)['tiles']}
    current, hashes = {}, {str(manifestpath.relative_to(ROOT)): manifestsha}
    for b in forms:
        tile = ROOT / '3d-viewer' / tiles[b['tile']]['url']
        key = str(tile.relative_to(ROOT))
        if key not in current:
            hashes[key] = digest(tile.read_bytes())
            assert hashes[key] == inventory['currentFormTileHashes'][key]
            current[key] = {r['uid']: r for r in read(tile)['buildings']}
            refs.append(tile)
        assert current[key][b['uid']] == b
    save(out / 'neighbour-inputs.json.gz', dict(
        rows=[dict(building=b, patchIndexes=[0], existingNative=False) for b in forms],
        inputHashes=hashes, candidateIds=scope['uids'], patches=patches,
        requiredNativeUids=[]))
    tool = HERE / 'check-neighbours-multi-retained.mjs'
    with (out / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str(out.relative_to(ROOT)) + '/'],
            cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    report = read(out / 'neighbour-checks.json')
    assert {r['uid'] for r in report['rows']} == {b['uid'] for b in forms}
    assert len(report['rows']) == len(forms)
    for path, sha in {**hashes, **report['inputHashes']}.items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    result = dict(uids=scope['uids'], forms=len(forms),
        basicFlags=[dict(uid=r['uid'], reasons=r['reasons'])
                    for r in report['rows'] if r['reasons']],
        installedNativeActorsTouching=0, existingTerrainContacts=0,
        installationApproved=False, publication=False, newlyInstalled=0,
        sourceGeometryChanges=0, scriptExternalAICalls=0,
        qualification='Complete region BASIC regression only; exact full 7007-actor scope proves no native actor or prior terrain touches this domain. Source identity, support, physical and visual acceptance remain separate.')
    save(out / 'summary.json', result)
    assert reservations.owns(lease)
    module('civic_root_regression_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'complete-new-root-civic-form-regression', list(dict.fromkeys(refs + [tool])), result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
