"""Run ordinary regressions for every form in the three new coastal domains."""
from pathlib import Path
import subprocess
import uuid
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = 'government-xl-depot120104-three-member-neighbours-v1-20261029'
    scope = 'government-xl-depot120104-three-member-scope-v1-20261029'
    surface = 'government-xl-depot120104-three-member-surface-v2-20261029'
    inventory = 'government-xl-after-unnamed265269-native-bounds-v1-20261029'
    out = base / batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(name, path):
        if name not in pins:
            pins[name] = authenticate(base / name)[1]
            refs.append(base / name / 'result.json')
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    context = take(scope, base / scope / 'scope.json')
    assert context['currentNativeActors'] == 7018 and context['touchingNativeUids'] == [] and context['terrainContacts'] == []
    forms = take(scope, base / scope / 'form-obligations.json.gz')
    assert len(forms) == len({f['uid'] for f in forms}) == context['intersectingForms'] == 4
    inv = take(inventory, base / inventory / 'complete-bounds.json.gz')
    assert len(inv['rows']) == 7018
    decision = take(surface, base / surface / 'summary.json')
    assert decision['status'] == 'private-three-member-chain-surface-validator-passed' and decision['newTerrainMembers'] is True
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == decision['currentManifest']['sha256']
    refs.append(manifest)
    hashes = {str(manifest.relative_to(ROOT)): digest(manifest.read_bytes())}
    tiles = {r['id']: r for r in read(manifest)['tiles']}
    for f in forms:
        path = ROOT / '3d-viewer' / tiles[f['tile']]['url']
        name = str(path.relative_to(ROOT))
        assert digest(path.read_bytes()) == inv['currentFormTileHashes'][name]
        assert next(b for b in read(path)['buildings'] if b['uid'] == f['uid']) == f
        hashes[name] = digest(path.read_bytes())
        refs.append(path)
    patches = []
    for member in decision['members']:
        candidate = member['candidate']
        node = take(surface, ROOT / candidate['path'])
        assert member['newTerrainMember'] and 'replaces' not in member and node['meta']['targetUids'] == context['uids']
        patches.append(dict(**candidate, uids=context['uids']))
    claim = reservations.claim('depot-new-coast-neighbours-' + str(uuid.uuid4()), ['building:' + f['uid'] for f in forms] + ['terrain:city/data/terrain.json'], batch=batch, ttl=1800)
    assert claim['ok']
    lease = claim['reservation']
    try:
        save(out / 'neighbour-inputs.json.gz', dict(rows=[dict(building=f, patchIndexes=[0, 1, 2], existingNative=False) for f in forms], inputHashes=hashes, candidateIds=context['uids'], patches=patches, requiredNativeUids=[]))
        tool = HERE / 'check-neighbours-multi-retained.mjs'
        with (out / 'worker.log').open('w') as log:
            subprocess.run(['node', str(tool), str(out.relative_to(ROOT)) + '/'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=900)
        checks = read(out / 'neighbour-checks.json')
        assert {r['uid'] for r in checks['rows']} == {f['uid'] for f in forms}
        for name, sha in checks['inputHashes'].items():
            assert digest((ROOT / name).read_bytes()) == sha
            refs.append(ROOT / name)
        result = dict(uids=context['uids'], rows=checks['rows'], basicFlags=[r for r in checks['rows'] if r['reasons']],
                      currentNativeActorsChecked=7018, requiredNativeUids=[], forms=4,
                      completeScopeVerified=True, installationApproved=False, publication=False,
                      qualification='Every form touching the three exact new coastal domains is checked under unchanged ordinary before/after terrain regression rules. The complete7018actor bound census nominates zero native neighbours and zero retained terrain patches. Flags remain unapproved; no canopy or other form is silently excluded.')
        save(out / 'summary.json', result)
        assert reservations.owns(lease)
        refs.append(tool)
        module('depot_new_terrain_neighbours_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'complete-new-coastal-domain-ordinary-neighbour-regressions', refs, result)
        print(dict(forms=4, flags=[dict(uid=r['uid'], reasons=r['reasons']) for r in result['basicFlags']]), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
