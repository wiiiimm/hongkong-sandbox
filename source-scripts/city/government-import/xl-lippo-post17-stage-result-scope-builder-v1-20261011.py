"""Inventory closed Lippo stage outputs with the existing source contracts.

This produces a verifier input, not a verification or installation certificate.
It preserves every inherited alias, metadata leaf and audit context verbatim;
stage outputs gain no new exclusions. Run only after the stage has finished.
"""
import argparse
import json
from pathlib import Path
from run import ROOT, HERE, read, digest

BATCH = 'government-xl-lippo-tower-current-basic-unchanged-stage-v2-20261011'
BASE = ROOT / 'docs/astra-city/government-import'
SOURCE_CERT = BASE / 'government-xl-lippo-post17-current-source-root-closure-v1-20261011/root-closed-scope.json'
SCRIPT_NAMES = [
    'xl-lippo-tower-current-basic-unchanged-stage-v2-20261011.py',
    'xl-lippo-current-basic-solid-browser-v1-20261011.mjs',
    'lippo_current_basic_drawn_carrier_witness_v1_20261011.mjs',
    'test_lippo_current_basic_drawn_carrier_witness_v1_20261011.mjs',
    'xl-lippo-tower-current-basic-unchanged-live-install-v1-20261011.py',
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-contract', required=True)
    parser.add_argument('--source-scope', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    contract = read(Path(args.source_contract))
    assert isinstance(contract, dict) and isinstance(contract['paths'], list)
    for key in ['historicalManifestAliases', 'metadataLeafPaths',
                'metadataLeafJsonPointers', 'auditDeclarationContextRefs']:
        assert key in contract
    inherited = read(Path(args.source_scope))
    assert isinstance(inherited, list) and inherited
    paths = set(contract['paths']) | set(inherited)
    cert = read(SOURCE_CERT)
    assert cert['independentlyVerified'] and cert['verifiedReferenceVersions'] > 0
    assert set(inherited) <= set(cert['paths'])
    stage = read(BASE / BATCH / 'acceptance.json')
    assert stage['passed'] and stage['failures'] == []
    assert stage['uids'] == ['landsd/239465:0']
    assert stage['newlyInstalled'] == stage['sourceGeometryChanges'] == stage['terrainGeometryChanges'] == 0
    assert not stage['publication'] and stage['livePublicationRequired']

    def add(path):
        path = Path(path).resolve()
        assert path.is_relative_to(ROOT) and path.is_file(), str(path)
        paths.add(str(path.relative_to(ROOT)))

    for folder in [BASE / BATCH, HERE / 'accepted' / BATCH,
                   HERE / 'local' / BATCH, SOURCE_CERT.parent]:
        assert folder.is_dir(), str(folder)
        for path in folder.rglob('*'):
            if path.is_file():
                add(path)
    for name in SCRIPT_NAMES:
        add(HERE / name)
    add(Path(__file__))
    for ref in [*stage['evidenceRefs'], stage['stagedBrowser']]:
        path = ROOT / ref['path']
        assert digest(path.read_bytes()) == ref['sha256']
        add(path)
    assert all((ROOT / path).is_file() for path in paths)
    output = {**contract, 'paths': sorted(paths)}
    # The only changed contract field is its complete path inventory.
    assert {k: v for k, v in output.items() if k != 'paths'} == {
        k: v for k, v in contract.items() if k != 'paths'}
    Path(args.out).write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(dict(paths=len(paths), pathInventoryOnly=True,
                          independentlyVerified=False, installationApproved=False,
                          inheritedContractFieldsUnchanged=True)))

if __name__ == '__main__':
    main()
