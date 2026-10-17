"""Preserve verified primary Museum context; no geometry or approval work."""
import importlib.util
from run import ROOT, HERE, read, save, digest, connect

BASE = ROOT / 'docs/astra-city/government-import'
PACKET = BASE / 'government-xl-heritage165054-primary-site-review-v1-20261014'
DOC = BASE / 'government-xl-heritage165054-primary-review-receipt-v1-20261014'


def main():
    findings = read(PACKET / 'source-bound-findings.json')
    review = read(PACKET / 'ROOT-REVIEW.json')
    assert digest((PACKET / 'source-bound-findings.json').read_bytes()) == 'b52281c7d8beef0d2ba594b0ee5fd1f714dda5fb54a15748efe609b247948670'
    assert len(review['filePins']) == 37
    for ref in review['filePins']:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    assert findings['source']['uid'] == 'landsd/165054:0'
    assert not any(findings['flags'].values())
    DOC.mkdir(exist_ok=True)
    save(DOC / 'ROOT-REVIEW.json', {
        'completeLiteralPinsVerified': 37,
        'actualImagesInspected': ['government-photo-b.jpg', 'operator-ground-floor-actual-3000w.png', 'cedd-STM10495-museum-context-actual-crop.png'],
        'preciseSourceFacetOrOwnershipMatchEstablished': False,
        'noBuildingGeometryCalculations': True,
        'sourceGeometryChanges': 0,
    })
    paths = [p for p in PACKET.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [ROOT / ref['path'] for ref in review['filePins']]
    paths += [HERE / 'heritage165054_primary_review_receipt_v1_20261014.py']
    spec = importlib.util.spec_from_file_location('heritage_existing_source_receipt_only', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.freeze(DOC.name, 'heritage-museum-bounded-primary-canopy-site-context-v1', paths, {
        'uids': ['landsd/165054:0'],
        'sourceBinding': findings['source'],
        'identityAccepted': False,
        'physicalAccepted': False,
        'currentAcceptance': False,
        'scriptFullAcceptancePassed': False,
        'currentHeldReason': 'original-low-extent-and-independent-canopy-correspondence-unproved',
        'newEvidence': 'Official entrance canopy/colonnade photographs, operator floor plan and 2021 location-bound Museum/carpark site plan. No exact original facet or property-ownership correspondence established.',
        'remainingIndependentActors': ['landsd/104467:0', 'landsd/57455:0'],
        'retainedFarOriginalFaces': 462,
        'nextStep': 'Bind complete unchanged original coordinates to all462 far source facets and independent1106/2 overlap facet IDs, then review exact source-feature correspondence. Preserve support/current physical/runtime/visual/publisher gates.',
    })
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone() == ('complete', result)
    for ref in result['evidenceRefs']:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    save(DOC / 'ROOT-VERIFIED.json', {'jobId': result['jobId'], 'exactNeonReadback': True, 'allEvidenceHashesVerified': True, 'evidenceRefCount': len(result['evidenceRefs']), 'newlyInstalled': 0})


if __name__ == '__main__':
    main()
