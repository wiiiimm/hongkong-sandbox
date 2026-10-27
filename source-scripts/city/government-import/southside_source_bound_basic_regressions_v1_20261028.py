"""Keep terrain-only and conditional 17-original compound BASIC checks separate."""
import argparse
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-source-bound-basic-regressions-v1-20261028'
DOC, LOCAL = BASE/BATCH, HERE/'local'/BATCH
LEASE = LOCAL/'reservation.json'
SCOPE = BASE/'government-xl-southside-six-partition-current-scope-v2-20261028'
SURFACE = BASE/'government-xl-southside-source-bound-surface-contract-v1-20261028'
CAP = BASE/'government-xl-southside-project-original-recovery-v1-20261028'


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    refs, pins, receipts = [Path(__file__)], {}, {}
    for batch in [SCOPE, SURFACE, CAP]:
        receipt, bound = authenticate(batch)
        receipts[batch.name] = receipt
        refs.append(batch/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    scope = take(SCOPE/'scope.json')
    assert not scope['touchingNativeUids'] and not scope['terrainContacts'] and scope['currentNativeActors'] == 6991
    surface = take(SURFACE/'summary.json')
    assert surface['singleNodeSurfaceContractPassed']
    candidate = surface['candidate']
    node = take(ROOT/candidate['path'])
    wanted = sorted(r['uid'] for r in take(CAP/'selection.json.gz')['rows'])
    assert len(wanted) == 17 and len(set(wanted)) == 17 and 'landsd/315025:0' in wanted
    forms = take(SCOPE/'form-obligations.json.gz')
    assert len(forms) == scope['intersectingForms'] == 84 and not any(f.get('modelGeometry') for f in forms)
    required = {('building:' if f['uid'].startswith('landsd/') else 'source-form:') + f['uid'] for f in forms}
    assert required | {'terrain:city/data/terrain.json'} <= set(lease['resources'])
    manifestpath = ROOT/'3d-viewer/city/data/manifest.json'
    manifest = take(manifestpath)
    hashes = {str(manifestpath.relative_to(ROOT)): digest(manifestpath.read_bytes())}
    tiles = {t['id']: t for t in manifest['tiles']}
    for form in forms:
        path = ROOT/'3d-viewer'/tiles[form['tile']]['url']
        take(path)
        hashes[str(path.relative_to(ROOT))] = digest(path.read_bytes())
    rootpath = ROOT/'3d-viewer/city/data/terrain.json'
    root = take(rootpath)
    builder = module('southside_source_bound_basic_extent', HERE/'resolve-pass-indexed-parent-clipping.py')
    bounds = builder.extent(node['coarseCells'], root)
    assert bounds == scope['regionalParentExtent'], 'Complete old scope cannot bind a different region'
    patches = [dict(**candidate, replaces=None, uids=wanted, bounds=bounds)]
    tool = HERE/'check-neighbours-multi-retained.mjs'
    modes = {}
    for name, targets in [('terrain-only', ['landsd/315025:0']), ('proposed-compound', wanted)]:
        directory = DOC/name
        save(directory/'neighbour-inputs.json.gz', dict(rows=[dict(building=f, patchIndexes=[0], existingNative=False) for f in forms],
                                                       inputHashes=hashes, candidateIds=targets, patches=patches, requiredNativeUids=[]))
        with (directory/'worker.log').open('w') as log:
            subprocess.run(['node', str(tool), str(directory.relative_to(ROOT))+'/',], cwd=ROOT,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        report = read(directory/'neighbour-checks.json')
        assert len(report['rows']) == 84 and {r['uid'] for r in report['rows']} == {f['uid'] for f in forms}
        for path, sha in report['inputHashes'].items():
            assert digest((ROOT/path).read_bytes()) == sha
            refs.append(ROOT/path)
        modes[name] = dict(candidateIds=targets, flags=[dict(uid=r['uid'], reasons=r['reasons']) for r in report['rows'] if r['reasons']])
        assert reservations.owns(lease)
    result = dict(uids=wanted, forms=84, modes=modes,
                  retainedBasicGuardsPassedConditionalOnAll17Originals=not modes['proposed-compound']['flags'],
                  terrainOnlyFlagsPreserved=True, proposedCompoundApproved=False,
                  installationApproved=False, physicalAccepted=False, identityAccepted=False,
                  sourceGeometryChanges=0, fullCurrentMapAcceptance=False,
                  qualification='Two separate unchanged conservative BASIC checks, both saved. Terrain-only keeps every other BASIC actor as a retained obligation. Conditional compound mode treats17 exact source nominees as proposed replacements; this mode is valid for publication only if all17 originals independently pass source identity, physical/runtime and browser acceptance and are installed atomically. No original source or BASIC flag is approved away, no actor hidden and no live catalogue/terrain changed.')
    save(DOC/'summary.json', result)
    refs.extend([tool, Path(builder.__file__)])
    assert reservations.owns(lease)
    module('southside_source_bound_basic_regressions_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'separate-terrain-only-and-conditional-compound-basic-regressions', list(dict.fromkeys(refs)), result)
    print({name: data['flags'] for name, data in modes.items()}, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    authenticate(SCOPE); authenticate(SURFACE)
    forms = read(SCOPE/'form-obligations.json.gz')
    resources = {('building:' if f['uid'].startswith('landsd/') else 'source-form:') + f['uid'] for f in forms}
    resources.add('terrain:city/data/terrain.json')
    claim = reservations.claim('southside-source-bound-basic-' + str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
