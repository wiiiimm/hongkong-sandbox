"""Compare complete old/new actual-renderer foundation objects for all17 originals."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-source-bound-foundation-readback-v1-20261028'
DOC = BASE/BATCH
OLD = BASE/'government-xl-southside-project-remaining-runtime-sequence-v1-20261028'
NEW = BASE/'government-xl-southside-source-bound-runtime-sequence-v1-20261028'


def main():
    assert not DOC.exists()
    refs, pins = [Path(__file__)], {}
    datasets = {}
    for label, directory in [('old', OLD), ('new', NEW)]:
        receipt, bound = authenticate(directory)
        assert receipt['capturedOriginals'] == 17
        refs.append(directory/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha
        datasets[label] = dict(receipt=receipt, foundations={}, sourceHashes={})
        for batch in receipt['actualRendererCohorts']:
            child, bound = authenticate(BASE/batch)
            refs.append(BASE/batch/'result.json')
            for path, sha in bound.items():
                assert path not in pins or pins[path] == sha
                pins[path] = sha
            selected = BASE/batch/'selection.json.gz'
            assert digest(selected.read_bytes()) == pins[str(selected.relative_to(ROOT))]
            refs.append(selected)
            assert all(r['status'] == 'captured' for r in child['rows'])
            for row in read(selected)['rows']:
                uid = row['uid']
                path = BASE/batch/(uid.split('/')[1]+'.json')
                assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
                refs.append(path)
                foundation = read(path)['foundation']
                old = datasets[label]['foundations'].get(uid)
                assert old is None or old == foundation, 'Repeated podium captures differ within one candidate'
                old_sha = datasets[label]['sourceHashes'].get(uid)
                assert old_sha is None or old_sha == row['sourceSHA256']
                datasets[label]['foundations'][uid] = foundation
                datasets[label]['sourceHashes'][uid] = row['sourceSHA256']
        assert len(datasets[label]['foundations']) == 17
        assert datasets[label]['sourceHashes'] == receipt['originalSourceSHA256ByUid']
    assert datasets['old']['sourceHashes'] == datasets['new']['sourceHashes']
    rows = []
    for uid in sorted(datasets['old']['foundations']):
        before, after = [datasets[label]['foundations'][uid] for label in ['old', 'new']]
        fields = sorted(set(before)|set(after))
        differences = [field for field in fields if before.get(field) != after.get(field)]
        rows.append(dict(uid=uid, sourceSHA256=datasets['new']['sourceHashes'][uid],
                         completeFoundationObjectEqual=not differences, differingFields=differences,
                         beforeBuried=before['fullyBuriedTriangles'], afterBuried=after['fullyBuriedTriangles'],
                         beforeUpward=before['fullyBuriedUpwardTriangles'], afterUpward=after['fullyBuriedUpwardTriangles'],
                         beforeMinimumGapM=before['minimumGapM'], afterMinimumGapM=after['minimumGapM']))
    result = dict(uids=[r['uid'] for r in rows], rows=rows, exactOriginalSourceHashesPreserved=True,
                  all17CompleteFoundationObjectsEqual=all(r['completeFoundationObjectEqual'] for r in rows),
                  all17BurialWarningCountsPreserved=all(r['beforeBuried'] == r['afterBuried'] and r['beforeUpward'] == r['afterUpward'] for r in rows),
                  sourceGeometryChanges=0, identityAccepted=False, physicalAccepted=False, installationApproved=False,
                  qualification='Full deep equality comparison of independently generated old six-node and NEW single-node actual-renderer foundation objects, not selected counts alone. Original-source hashes also compared across all17 and all repeated captures. Any differences remain explicit. Equal numeric diagnostics do not transfer identity/physical/browser acceptance or waive preserved warnings.')
    save(DOC/'summary.json', result)
    module('southside_source_bound_foundation_readback_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'independent-complete-old-new-17-source-foundation-object-readback', list(dict.fromkeys(refs)), result)
    print(dict(all17FoundationObjectsEqual=result['all17CompleteFoundationObjectsEqual'],
               allBurialCountsPreserved=result['all17BurialWarningCountsPreserved'],
               differences=[r for r in rows if not r['completeFoundationObjectEqual']]), flush=True)


if __name__ == '__main__':
    main()
