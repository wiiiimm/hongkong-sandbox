"""Preserve completed HKUST source context; no geometry replay or acceptance."""
import gzip
import importlib.util
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect

BASE = ROOT / 'docs/astra-city/government-import'
PACKET = BASE / 'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014'
DOC = BASE / 'government-xl-hkust-two-original-source-context-receipt-v1-20261014'
CURRENT = 'c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
EXPECTED_RESULT = '400089b7b12608e753c1ef28b56e63a9f872ab74b81bf159f6c02c724d5fb617'
EXPECTED_ARRAY_RECEIPT = '4d6896acaabb53db6f20aa05f82087543656f82c2101c426cab11c14b87c808b'


def main():
    assert digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes()) == CURRENT
    contract = read(PACKET / 'input-contract.json')
    for path, expected in contract['filePins'].items():
        assert digest((ROOT / path).read_bytes()) == expected, path
    assert digest((PACKET / 'two-original-target-interface-draft-v1.py').read_bytes()) == contract['callerSHA256']
    output = PACKET / 'two-original-scope-interface-output-v1'
    assert digest((output / 'result.json').read_bytes()) == EXPECTED_RESULT
    assert digest((PACKET / 'cached-complete-original-arrays-v1/array-receipt.json').read_bytes()) == EXPECTED_ARRAY_RECEIPT
    terminal = read(output / 'terminal.json')
    supervisor = read(PACKET / 'ROOT-TWO-ORIGINAL-CONTEXT-TERMINAL.json')
    assert terminal['complete'] and terminal['allInputHashesUnchanged'] and terminal['noGeometryChanges']
    assert terminal['resultSHA256'] == EXPECTED_RESULT
    assert supervisor['exitCode'] == 0 and supervisor['leaseReleased'] and supervisor['sourceGeometryChanges'] == 0
    result = read(output / 'result.json')
    assert result['uids'] == ['landsd/309822:0', 'landsd/232155:0']
    assert result['sourceTuples'] == contract['sourceTuples']
    assert result['sourceGeometryChanges'] == 0 and result['newlyInstalled'] == 0
    assert not result['currentAcceptance'] and not result['identityAccepted'] and not result['physicalAccepted']
    old = read(ROOT / contract['priorBindingsPath'])
    assert result['all227OldInterfaceNegativesVerbatim'] == old['historicalInterfaceRowVerbatim']
    assert result['towerOnlyExpandedTargetFailureVerbatim'] == old['historicalTowerGroupRoleVerbatim']['variants']
    for ref in result['arrayRefs'] + [result['interfaceResult'], result['lowerEdgeResult']]:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    contacts = read(output / 'complete-finite-interfaces.json.gz')
    assert contacts['allPairsExamined'] and contacts['sourceFacesOmitted'] == 0
    assert contacts['geometryChanges'] == 0 and not contacts['physicalSupportAccepted']
    assert len(contacts['contacts']) == result['interfaceResult']['records'] == 83
    assert result['interfaceResult']['fullPairBound'] == 12943 * 655
    for row in contacts['contacts']:
        assert 0 <= row['sourceFaceA'] < 12943 and 0 <= row['sourceFaceB'] < 655
    lower = read(output / 'complete-minimum-level-edge-context.json.gz')
    assert len(lower['completeMinimumLevelNonzeroEdges']) == 71
    assert lower['wholeEdgesWithoutCompleteExactContact'] == list(range(71))
    assert not lower['structuralSupportAccepted']
    scope = result['completeCurrentTileRawRingNomination']
    assert len(scope['nominated']) + len(scope['strictDisjointExclusions']) == scope['completeTileForms'] == 1383
    scoped_uids = [r['form']['uid'] for r in scope['nominated'] + scope['strictDisjointExclusions']]
    assert len(scoped_uids) == len(set(scoped_uids))
    target = read(PACKET / 'exact-provider-target-audit-output-v1/target-audit.json')
    assert len(target['records']) == 2 and all(r['literalPackedRingsEqualCurrent'] for r in target['records'])
    projections = {r['label']: r for r in result['projectionScope']}
    assert len(projections) == 4
    DOC.mkdir(exist_ok=True)
    review = {
        'resultSHA256': EXPECTED_RESULT,
        'arrayReceiptSHA256': EXPECTED_ARRAY_RECEIPT,
        'allLiteralInputPinsVerified': True,
        'completeTileForms': 1383,
        'contactRecords': 83,
        'minimumLevelEdges': 71,
        'minimumLevelEdgesWithoutCompleteExactContact': 71,
        'pairedExpandedTargetCoverage': projections['two-originals-against-expanded-target']['targetCoverage'],
        'providerPackedRingsEqualCurrent': True,
        'priorNegativesPreservedVerbatim': True,
        'currentAcceptance': False,
        'geometryCalculationsReplayed': False,
        'noStructuralRoleOrSupportCredit': True,
    }
    save(DOC / 'ROOT-REVIEW.json', review)
    paths = [p for p in PACKET.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [ROOT / p for p in contract['filePins']]
    paths += [Path(__file__)]
    spec = importlib.util.spec_from_file_location('existing_source_only_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    receipt = module.freeze(DOC.name, 'hkust-complete-two-original-source-context-v1', paths, {
        'uids': result['uids'],
        'sourceTuples': result['sourceTuples'],
        'currentManifestSHA256': CURRENT,
        'completedContextResultSHA256': EXPECTED_RESULT,
        'review': review,
        'identityAccepted': False,
        'supportAccepted': False,
        'physicalAccepted': False,
        'scriptFullAcceptancePassed': False,
        'currentHeldReason': 'paired-original-source-role-boundary-and-current-support-unresolved',
        'remainingReasonGroups': {
            'historicalInterfaceFailures': 227,
            'minimumLevelEdgesWithoutCompleteExactContact': 71,
            'expandedTargetCoverage': projections['two-originals-against-expanded-target']['targetCoverage'],
            'currentFourWorldPhysicalProofComplete': False,
        },
        'nextStep': 'Account for original tower/podium source roles and uncovered provider boundary; resolve existing support failures using unchanged source geometry and current terrain. Preserve independent neighbours and full physical/runtime/visual/publisher gates.',
    })
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
    for ref in receipt['evidenceRefs']:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    save(DOC / 'ROOT-VERIFIED.json', {'jobId': receipt['jobId'], 'neonResultExact': True, 'allEvidenceHashesVerified': True, 'evidenceRefCount': len(receipt['evidenceRefs']), 'newlyInstalled': 0})


if __name__ == '__main__':
    main()
