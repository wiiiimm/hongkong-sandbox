"""Run the unchanged conservative BASIC neighbour checker on all 84 scoped forms."""
import argparse
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-southside-six-partition-basic-regressions-v1-20261028'
DOC, LOCAL = BASE / BATCH, HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'
SCOPE = BASE / 'government-xl-southside-six-partition-current-scope-v2-20261028'


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    _, pins = authenticate(SCOPE)
    refs = [Path(__file__), SCOPE / 'result.json']

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    scope = take(SCOPE / 'scope.json')
    assert scope['allSixReconstructedNodesRevalidated'] and scope['currentNativeActors'] == 6991
    assert not scope['touchingNativeUids'] and not scope['terrainContacts']
    assert scope['positiveAreaTerrainOverlaps'] == 0
    forms = take(SCOPE / 'form-obligations.json.gz')
    assert len(forms) == scope['intersectingForms'] == 84 and not any(f.get('modelGeometry') for f in forms)
    keys = [('building:' if f['uid'].startswith('landsd/') else 'source-form:') + f['uid'] for f in forms]
    assert set(keys + ['terrain:city/data/terrain.json']) <= set(lease['resources'])
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = take(manifestpath)
    hashes = {str(manifestpath.relative_to(ROOT)): digest(manifestpath.read_bytes())}
    tiles = {t['id']: t for t in manifest['tiles']}
    for form in forms:
        path = ROOT / '3d-viewer' / tiles[form['tile']]['url']
        take(path)
        hashes[str(path.relative_to(ROOT))] = digest(path.read_bytes())
    builder = module('southside_basic_regression_extent', HERE / 'resolve-pass-indexed-parent-clipping.py')
    root = take(ROOT / '3d-viewer/city/data/terrain.json')
    patches = []
    for j in range(6):
        path = SCOPE / 'private-nodes' / ('strip-' + str(j) + '.json.gz')
        node = take(path)
        patches.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()),
                            replaces=None, uids=scope['uids'], bounds=builder.extent(node['coarseCells'], root)))
    save(DOC / 'neighbour-inputs.json.gz', dict(rows=[dict(building=f, patchIndexes=list(range(6)), existingNative=False) for f in forms],
                                              inputHashes=hashes, candidateIds=scope['uids'], patches=patches, requiredNativeUids=[]))
    tool = HERE / 'check-neighbours-multi-retained.mjs'
    with (DOC / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str(DOC.relative_to(ROOT)) + '/'], cwd=ROOT,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    report = read(DOC / 'neighbour-checks.json')
    assert len(report['rows']) == len(forms)
    assert {r['uid'] for r in report['rows']} == {f['uid'] for f in forms}
    for path, sha in report['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    flags = [dict(uid=r['uid'], reasons=r['reasons']) for r in report['rows'] if r['reasons']]
    result = dict(uids=scope['uids'], forms=len(forms), basicFlags=flags, allBasicGuardsPassed=not flags,
                  requiredNativeUids=[], installationApproved=False, physicalAccepted=False, identityAccepted=False,
                  sourceGeometryChanges=0, fullCurrentMapAcceptance=False,
                  qualification='Unchanged conservative BASIC neighbour checker over all current scoped forms. Zero installed/inline native neighbours and zero installed terrain overlaps were independently nominated in the complete current scope. Raw flags retained; sampling is not exact source-geometry identity, source physical acceptance or browser approval.')
    save(DOC / 'summary.json', result)
    assert reservations.owns(lease)
    refs.extend([tool, Path(builder.__file__)])
    module('southside_basic_regressions_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'unchanged-basic-neighbour-regressions-for-complete-six-strip-scope', list(dict.fromkeys(refs)), result)
    print(dict(forms=len(forms), flags=flags), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    authenticate(SCOPE)
    forms = read(SCOPE / 'form-obligations.json.gz')
    keys = [('building:' if f['uid'].startswith('landsd/') else 'source-form:') + f['uid'] for f in forms]
    claim = reservations.claim('southside-six-partition-basic-' + str(uuid.uuid4()),
                               sorted(set(keys + ['building:landsd/315025:0', 'terrain:city/data/terrain.json'])),
                               batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
