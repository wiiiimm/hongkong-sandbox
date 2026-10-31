"""Reuse exact unchanged source-only contact work; transfer no terrain acceptance."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
OLD = 'government-xl-fung-yip-full-native-domain-'
NEW = 'government-xl-fung-yip-after-inone-'
BATCH = NEW + 'original-contact-rebind-v1-20261025'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs = [Path(__file__)]
    receipts = {}
    historical_input_differences = []

    def take(batch, name):
        receipt, pins = authenticate(BASE / batch)
        receipts[batch] = receipt['jobId']
        refs.append(BASE / batch / 'result.json')
        # Rehash frozen outputs, including original support/path partitions.
        # Historical mutable scene inputs grant no current-scene acceptance.
        for path, sha in pins.items():
            p = ROOT / path
            actual = digest(p.read_bytes()) if p.exists() else None
            if p.is_relative_to(BASE / batch):
                assert actual == sha
                refs.append(p)
            elif actual != sha:
                historical_input_differences.append(dict(
                    batch=batch, path=path, historicalSHA256=sha,
                    currentSHA256=actual, acceptanceTransferred=False))
        p = BASE / batch / name
        assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
        return read(p)

    old = take(OLD + 'attributes-v1-20261024', 'attributes.json.gz')
    current = take(NEW + 'attributes-v1-20261025', 'attributes.json.gz')
    assert old['rows'] == current['rows']
    sources = {r['uid']: r['sourceSHA256'] for r in current['rows']}
    assert set(sources) == {'landsd/254815:0', 'landsd/79883:0'}
    pairs = take(OLD + 'pairs-v1-20261024', 'summary.json')
    assert pairs['sourceSHA256ByUid'] == sources
    strict = take(OLD + 'support-followthrough-v1-20261024-254815-79883-strict', 'summary.json')
    paths = take(OLD + 'support-followthrough-v1-20261024-254815-79883-paths', 'summary.json')
    assert strict['sourceSHA256ByUid'] == sources
    assert not strict['allFourModesPassed']
    assert paths['allUnresolvedHaveFinitePaths']
    assert len(strict['rows']) == len(paths['rows']) == 4
    assert all(r['remaining'] == 0 and r['targets'] == r['verifiedPaths'] == 32
               and not r['strictInterfacePassed'] for r in paths['rows'])
    result = dict(
        uids=sorted(sources), sourceSHA256ByUid=sources,
        completeRendererAttributeRowsIdentical=True, authenticatedJobs=receipts,
        historicalInputDifferences=historical_input_differences,
        sourceOnlyContactEvidenceRebound=True, strictSupportPassed=False,
        all32UnresolvedProbesHaveFiniteSourcePathsInAllFourStreams=True,
        physicalAcceptance=False, installationApproved=False, publication=False,
        terrainAcceptanceTransferred=False, sourceGeometryChanges=0,
        sourcePoseChanges=0, aiGeometryModelling=False,
        qualification='Exact complete renderer attribute rows, original indices and all coordinate streams are identical. Reuse unchanged original-to-original pair, strict support and finite source-path diagnostics only. The strict support failure remains false. Changed terrain, neighbours, source-role interpretation and browser/publication acceptance require their own current evidence.')
    save(out / 'summary.json', result)
    module('fung_contact_rebind', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'unchanged-original-only-contact-rebind', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
