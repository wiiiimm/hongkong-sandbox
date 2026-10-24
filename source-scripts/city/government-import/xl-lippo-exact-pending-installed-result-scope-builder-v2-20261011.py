"""Inventory completed Lippo live output with unchanged stage closure contracts.

Read-only verifier input only. No new aliases, numeric leaves, exclusions,
verification certificate or installed credit is generated here.
"""
import argparse
import json
from pathlib import Path
from run import ROOT, HERE, read, digest

BATCH = 'government-xl-lippo-tower-exact-pending-resume-installed-v2-20261011'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
CATALOGUE = ROOT / '3d-viewer/city/data/official-models/government-xl-lippo-tower-current-basic-unchanged-stage-v2-20261011/catalogue.json'
POINTER = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage-contract', required=True)
    parser.add_argument('--extra-path', action='append', default=[])
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    contract = read(Path(args.stage_contract))
    assert isinstance(contract, dict) and isinstance(contract['paths'], list)
    for key in ['historicalManifestAliases', 'metadataLeafPaths',
                'metadataLeafJsonPointers', 'auditDeclarationContextRefs']:
        assert key in contract
    paths = set(contract['paths'])
    result = read(DOC / 'result.json')
    assert result['publication'] and result['newlyInstalled'] == 1
    assert result['batch'] == BATCH and result['resumedOriginalApprovalWithoutHistoryEdits']
    assert result['snapshotId'] == '8d35b6f1d6f6bcdc'
    assert result['installedUids'] == ['landsd/239465:0']
    assert result['fullXLCurrentCounts'] == dict(total=521, installedVerified=226, remaining=295)
    sync = read(DOC / 'neon-sync.json')
    assert sync['resultVerified'] and sync['jobId'] == result['jobId']
    pointer = read(POINTER)
    assert pointer['snapshotId'] == result['snapshotId'] == sync['snapshotId']
    manifest = ROOT / result['manifest']['path']
    assert digest(manifest.read_bytes()) == result['manifest']['sha256']
    assert result['manifest']['sha256'] != '4a6756a928b11a781d5eca86a22278994441985f532dba40a973f46df2902285'

    def add(path):
        path = Path(path).resolve()
        assert path.is_relative_to(ROOT) and path.is_file(), str(path)
        paths.add(str(path.relative_to(ROOT)))

    original = ROOT / 'docs/astra-city/government-import/government-xl-lippo-tower-current-basic-unchanged-installed-v1-20261011'
    for folder in [DOC, HERE / 'local' / BATCH, CATALOGUE.parent, original]:
        assert folder.is_dir(), str(folder)
        for path in folder.rglob('*'):
            if path.is_file():
                add(path)
    add(Path(__file__))
    for path in [POINTER, ROOT / pointer['inventory'],
                 ROOT / '3d-viewer/city/data/building-progress.json', manifest]:
        add(path)
    for path in args.extra_path:
        add(ROOT / path)
    refs = [*result['evidenceRefs'], result['liveBrowser'], result['manifest'], result['resumeAttempt']]
    original_acceptance = original / 'acceptance.json'
    assert digest(original_acceptance.read_bytes()) == 'f191d93907f340180e7dfd6eb87122620c6f15325fad9d8a8362c62ef2280ff1'
    add(original_acceptance)
    for ref in refs:
        path = ROOT / ref['path']
        assert digest(path.read_bytes()) == ref['sha256']
        add(path)
    assert all((ROOT / path).is_file() for path in paths)
    output = {**contract, 'paths': sorted(paths)}
    assert {k: v for k, v in output.items() if k != 'paths'} == {
        k: v for k, v in contract.items() if k != 'paths'}
    Path(args.out).write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(dict(paths=len(paths), pathInventoryOnly=True,
                          independentlyVerified=False, installationCreditGenerated=False,
                          inheritedStageContractsUnchanged=True)))

if __name__ == '__main__':
    main()
