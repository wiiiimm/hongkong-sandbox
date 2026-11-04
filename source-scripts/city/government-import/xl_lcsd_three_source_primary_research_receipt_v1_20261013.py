"""Freeze completed primary research only; never identity or physical acceptance."""
from pathlib import Path
import importlib.util
from run import ROOT, HERE, read, save, digest

BATCH = 'government-xl-lcsd-three-source-primary-research-receipt-v1-20261013'
BASE = ROOT / 'docs/astra-city/government-import'
PACKET = BASE / 'government-xl-lcsd-three-source-primary-identity-research-v1-20261013'
DOC = BASE / BATCH
CURRENT = 'c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
FREEZER = HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py'

def verify():
    pins = read(PACKET / 'review-file-pins.json')
    validation = read(PACKET / 'actual-closure-validation.json')
    assert validation['allPassed'] and validation['literalInputCount'] == len(pins['allInputHashes']) == 39
    paths = [ROOT / p for p in pins['allInputHashes']]
    for path in paths:
        assert digest(path.read_bytes()) == pins['allInputHashes'][str(path.relative_to(ROOT))]
    assert digest((PACKET / 'source-bound-findings.json').read_bytes()) == validation['resultSHA256']
    assert digest((PACKET / 'review-file-pins.json').read_bytes()) == validation['reviewPinsSHA256']
    findings = read(PACKET / 'source-bound-findings.json')
    assert findings['currentManifestSHA256'] == digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes()) == CURRENT
    assert not findings['identityAccepted'] and not findings['physicalAccepted'] and not findings['currentAcceptance']
    assert findings['geometryChanges'] == 0 and not findings['permanentRejection']
    assert [r['uid'] for r in findings['cases']] == ['landsd/281463:0', 'landsd/236418:0', 'landsd/232240:0']
    assert all(r['currentFormEqualsSavedForm'] for r in findings['cases'])
    return findings, paths + [p for p in PACKET.rglob('*') if p.is_file()] + [Path(__file__)]

def main():
    assert not DOC.exists()
    findings, paths = verify()
    DOC.mkdir()
    save(DOC / 'research-account.json', dict(primaryPacket=str(PACKET.relative_to(ROOT)), sourceBoundFindings=({'path': str((PACKET/'source-bound-findings.json').relative_to(ROOT)), 'sha256': digest((PACKET/'source-bound-findings.json').read_bytes())}), rawFindingsVerbatim=findings, sourceOnly=True, identityAccepted=False, physicalAccepted=False, currentAcceptance=False, noModelReviewWrites=True))
    spec = importlib.util.spec_from_file_location('lcsd_primary_research_freezer', FREEZER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.freeze(BATCH, 'completed-primary-source-research-only', paths, dict(uids=[r['uid'] for r in findings['cases']], sourceOnly=True, identityAccepted=False, physicalAccepted=False, currentAcceptance=False, sourceIdentityResearchUsedAI=True, modelReviewWrites=False, remainingReason='Exact source/site component correspondence unresolved; primary leads do not grant identity or physical acceptance.', nextStep='281463: exact provider/site-podium component scope. 236418: actual245RS plan and cover/walkway component mapping. 232240: full low-wing/missing423m2 boundary mapping and dimensioned plan if unresolved.', primaryResearchAccount=str((DOC/'research-account.json').relative_to(ROOT)), currentManifestSHA256=CURRENT))

if __name__ == '__main__':
    main()
