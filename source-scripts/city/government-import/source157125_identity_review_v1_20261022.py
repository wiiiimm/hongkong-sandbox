"""Review exact original unnamed-source identity, retaining coverage warnings."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-source157125-source-identity-review-v1-20261022'


def main():
    doc = BASE / BATCH
    assert not doc.exists()
    refs = [Path(__file__)]

    def take(batch, name):
        folder = BASE / batch
        _, pins = authenticate(folder)
        p = folder / name
        assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
        refs.extend([folder / 'result.json', p])
        return p

    identity = read(take('government-xl-source157125-current-identity-v1-20261022', '157125:0/identity.json'))
    assert identity['sourceSHA256'] == '61a4184f849ef10821ec04819ba8527dba5dfcb5bdb3284c48a1f44d3778707d'
    assert identity['originalOwnership']['sourceGraphVerified']
    assert identity['exactCurrentComponentRoute']['qualified'] and identity['exactWholeCellCoverage']['covered']
    c = identity['freshCurrentIdentity']
    assert c['exactObjectAndCSUID'] and c['target']['objectId'] == 157125
    assert c['target']['buildingCSUID'] == '3651120546T20050430'
    assert set(identity['reasons']) == {'fresh-current-spatial-bound:targetCoveredBySourceProjection', 'full-source-target-coverage'}
    assert c['unrelatedIntersectingForms'] == 0 and c['sourceExcessCoveredByAnyOtherFormM2'] == 0
    assert abs(c['targetCoveredBySourceProjection'] - .8669879867788073) < 1e-12
    image = take('government-xl-source157125-identity-imagery-v1-20261022', '157125:0.png')
    provenance = read(take('government-xl-source157125-identity-imagery-v1-20261022', 'provenance.json'))
    for tile in provenance['tiles']:
        p = ROOT / tile['path']
        assert digest(p.read_bytes()) == tile['sha256']
        refs.append(p)
    plan = take('government-xl-source157125-original-identity-context-v1-20261022', 'whole-source-plan.png')
    for tile, sha in identity['exactRouteTileHashes'].items():
        p = ROOT / '3d-viewer' / tile
        assert digest(p.read_bytes()) == sha
        refs.append(p)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == identity['exactRouteManifestSHA256']
    refs.append(manifest)
    review = dict(uids=['landsd/157125:0'], uid='landsd/157125:0', reviewer='Codex ROOT',
                  sourceSHA256=identity['sourceSHA256'], sourceFormSHA256=identity['sourceFormSHA256'],
                  worldTrianglesSHA256=identity['worldTrianglesSHA256'], identityReviewApproved=True,
                  identityOnlyApproved=True, identityProof=dict(exactObjectId=True, exactBuildingCSUID=True,
                                                               uniqueViewerMatch=True, identityAccepted=True),
                  sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
                  imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())) for p in [image, plan]],
                  rawReasonsRetained=identity['reasons'], rawSpatialContext=c,
                  observations=[
                      'Exact original graph, unique current OBJECTID157125/CSUID3651120546T20050430 routing and whole one-metre geographic-cell coverage bind this complete unchanged source to the current unnamed building. No landmark name is invented.',
                      'ROOT inspected the unfitted official Lands aerial, complete source plan and two complete perspectives. The long polygonal outline, stepped roof sections and circular interior feature align with the photographed structure at the original placement. This is not a displaced different building.',
                      'Complete source projection covers86.69879867788073percent of the solid current footprint. The main difference is an interior opening surrounding the circular source feature; the source outer edge extends at most0.10811454862307252m from the recorded footprint. Raw coverage failures and all original faces remain unchanged.',
                      'The aerial supports the identity and arrangement, but cannot establish the exact floor/open-sky arrangement of the interior opening. This identity-only review does not invent a floor, fill source geometry, certify component function or approve physical placement.',
                      'No different current building footprint intersects the complete source projection. Full current terrain/contact/foreign/browser acceptance remains separate.'
                  ],
                  decision='Accept identity for this exact immutable complete original revision only; preserve automatic footprint coverage failures.',
                  installationApproved=False, placementReviewed=False, publicationApproved=False,
                  sourceGeometryChanges=0)
    save(doc / 'ROOT-IDENTITY-REVIEW.json', review)
    module('olympic_identity_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-original-identity-only-interpretation', refs, review)


if __name__ == '__main__':
    main()
