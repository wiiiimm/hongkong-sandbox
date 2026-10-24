"""Review exact original station identity, preserving raw GIS extent warnings."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-olympic-station-source-identity-review-v1-20261022'


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

    identity = read(take('government-xl-olympic-station-band-identity-v1-20261022', '81242:0/identity.json'))
    assert identity['sourceSHA256'] == 'd2d1f09a8119649d7ffdfaacc0070a118bd32a16729d9b5ae4d72eea58990ded'
    assert identity['originalOwnership']['sourceGraphVerified']
    assert identity['exactCurrentComponentRoute']['qualified'] and identity['exactWholeCellCoverage']['covered']
    c = identity['freshCurrentIdentity']
    assert c['exactObjectAndCSUID'] and c['target']['objectId'] == 81242
    assert c['target']['buildingCSUID'] == '3455519866T20050430'
    assert set(identity['reasons']) == {'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM', 'full-source-maximum-extent'}
    assert c['unrelatedIntersectingForms'] == 0 and c['sourceExcessCoveredByAnyOtherFormM2'] == 0
    assert c['targetCoveredBySourceProjection'] > .9999
    image = take('government-xl-olympic-station-identity-imagery-v1-20261022', '81242:0.png')
    provenance = read(take('government-xl-olympic-station-identity-imagery-v1-20261022', 'provenance.json'))
    for tile in provenance['tiles']:
        p = ROOT / tile['path']
        assert digest(p.read_bytes()) == tile['sha256']
        refs.append(p)
    plan = take('government-xl-olympic-station-original-identity-context-v1-20261022', 'whole-source-plan.png')
    for tile, sha in identity['exactRouteTileHashes'].items():
        p = ROOT / '3d-viewer' / tile
        assert digest(p.read_bytes()) == sha
        refs.append(p)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == identity['exactRouteManifestSHA256']
    refs.append(manifest)
    review = dict(uids=['landsd/81242:0'], uid='landsd/81242:0', reviewer='Codex ROOT',
                  sourceSHA256=identity['sourceSHA256'], sourceFormSHA256=identity['sourceFormSHA256'],
                  worldTrianglesSHA256=identity['worldTrianglesSHA256'], identityReviewApproved=True,
                  identityOnlyApproved=True, identityProof=dict(exactObjectId=True, exactBuildingCSUID=True,
                                                               uniqueViewerMatch=True, identityAccepted=True),
                  sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
                  imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())) for p in [image, plan]],
                  rawReasonsRetained=identity['reasons'], rawSpatialContext=c,
                  observations=[
                      'Exact original graph, unique current OBJECTID/CSUID routing and whole one-metre geographic-cell coverage bind this complete original source to Olympic Station.',
                      'ROOT inspected the unfitted official Lands aerial and full-source plan. The elongated main roof, two enlarged roof sections, parallel station sides and longer end structures correspond to the photographed station in its original pose.',
                      'The government source covers 99.99766707803467 percent of the current footprint. Its source projection includes 1999.9818514127635 square metres outside that footprint, extending as far as 31.229618070271865 metres. These raw values remain unchanged; the longer station end and side structures are visible in the aerial.',
                      'No different current building footprint intersects the complete source projection. This identity decision does not approve ground contact, collision, terrain edits, every small component function or publication.'
                  ],
                  decision='Accept identity for this exact immutable complete original revision only; preserve automatic extent failures.',
                  installationApproved=False, placementReviewed=False, publicationApproved=False,
                  sourceGeometryChanges=0)
    save(doc / 'ROOT-IDENTITY-REVIEW.json', review)
    module('olympic_identity_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-original-identity-only-interpretation', refs, review)


if __name__ == '__main__':
    main()
