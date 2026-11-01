"""Reuse exact pair mathematics only after complete current array equality.

No identity, placement, physical or publication approval transfers. Historical
manifest bindings remain historical; the fresh runtime binds the current one.
"""
import itertools
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-harbour-glory-current-pair-binding-v1-20261102'
OLD = 'government-xl-harbour-glory-eleven-shared-e12-current-v1-20261101'
CURRENT = 'government-xl-harbour-glory-eleven-after-shangrila-v2-20261102'
PAIRS = 'government-xl-harbour-glory-eleven-original-contacts-v1-20261102-pairs'
MODES = {'original', 'literal', 'leftF32', 'balancedF32'}


def main():
    out = BASE / BATCH
    lp = HERE / 'local' / (BATCH + '-lease') / 'reservation.json'
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, name):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    fresh_selection = take(CURRENT + '-runtime', 'selection.json.gz')
    sources = {r['uid']: r['sourceSHA256'] for r in fresh_selection['rows']}
    assert len(sources) == 11
    resources = sorted('building:' + uid for uid in sources)
    if '--owned' not in sys.argv:
        assert not lp.parent.exists()
        claim = reservations.claim('harbour-current-pairs-' + str(uuid.uuid4()),
                                   resources, batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], lp,
                                [sys.executable, __file__, '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and set(lease['resources']) == set(resources)
    old_selection = take(OLD + '-runtime', 'selection.json.gz')
    old_rows = {r['uid']: r for r in old_selection['rows']}
    assert set(old_rows) == set(sources)
    for row in fresh_selection['rows']:
        old = old_rows[row['uid']]
        assert row['sourceSHA256'] == old['sourceSHA256']
        assert row['source'] == old['source']
        assert row['candidate']['entry'] == old['candidate']['entry']
        for item in [row, old]:
            path = ROOT / item['candidate']['path']
            assert digest(path.read_bytes()) == sources[row['uid']]
            refs.append(path)
    fresh = take(CURRENT + '-attributes', 'attributes.json.gz')
    old = take(OLD + '-attributes', 'attributes.json.gz')
    current_rows = {r['uid']: r for r in fresh['rows']}
    previous_rows = {r['uid']: r for r in old['rows']}
    assert set(current_rows) == set(previous_rows) == set(sources)
    # Compare complete records, including every POSITION/index, all arithmetic
    # streams, rendered meshes and unused vertices; no bounds-only shortcut.
    assert current_rows == previous_rows
    assert fresh['startEndAllInputsVerified'] and old['startEndAllInputsVerified']
    assert fresh['completeRecursiveProductionModuleClosure'] == old['completeRecursiveProductionModuleClosure']
    pair = take(PAIRS, 'summary.json')
    assert pair['sourceSHA256ByUid'] == sources and pair['completeUnorderedPairs'] == 55
    expected = {(a, b, mode) for a, b in itertools.combinations(sorted(sources), 2) for mode in MODES}
    actual = {(r['uid'], r['peerUid'], r['mode']) for r in pair['rows']}
    assert len(pair['rows']) == len(actual) == 220 and actual == expected
    # Pin unchanged exact contact kernels, not merely the saved count rows.
    for name, sha in pins[PAIRS].items():
        if name.endswith('.py'):
            path = ROOT / name
            assert digest(path.read_bytes()) == sha
            refs.append(path)
    for row in pair['rows']:
        if 'rawPath' in row:
            path = ROOT / row['rawPath']
            assert digest(path.read_bytes()) == pins[PAIRS][row['rawPath']]
            refs.append(path)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    sha = digest(manifest.read_bytes())
    assert sha == fresh_selection['manifestSHA256']
    refs.append(manifest)
    assert reservations.owns(lease)
    result = dict(uids=sorted(sources), sourceSHA256ByUid=sources,
                  currentManifestSHA256=sha, currentRuntime=CURRENT + '-runtime',
                  historicalPairBatch=PAIRS, completeSourceRecordsIdentical=True,
                  completeFourWorldArraysIdentical=True, productionClosureIdentical=True,
                  completeUnorderedPairs=55, coordinateModes=sorted(MODES), rows=pair['rows'],
                  sourceGeometryChanges=0, sourcePoseChanges=0, physicalAcceptance=False,
                  installationApproved=False, publication=False,
                  qualification='Exact numeric evidence reuse only; all current ground, neighbour, visual, physical and publication checks remain required.')
    save(out / 'summary.json', result)
    module('harbour_current_pairs_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'complete-current-original-pair-array-equality-no-approval-transfer',
        list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
