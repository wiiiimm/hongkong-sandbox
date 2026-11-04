"""Bound D's exact source identity; preserve both raw footprint-coverage failures."""
from copy import deepcopy
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-beverly-d-after-fe-exact-identity-review-v1-20261025'
UID = 'landsd/255541:0'
SHA = 'c998eee48b38a47635f3c2344c58cfac3533518b16629c3ab69df1d124ae244d'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        p = BASE / batch / name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)

    prefix = 'government-xl-beverly-ad-after-fe-'
    selection = take(prefix + 'runtime-v2-20261025', 'selection.json.gz')
    source = next(r for r in selection['rows'] if r['uid'] == UID)
    raw = take(prefix + 'identity-v1-20261025', '255541:0/identity.json')
    context = take(prefix + 'identity-v1-20261025', '255541:0/context.json')['identity']
    assert source['modelId'] == raw['originalOwnership']['originalRootName'] == 'B371601498801063C0'
    form = source['source']['building']
    assert form['buildingCSUID'] == '3716014988T20050430' and source['sourceSHA256'] == raw['sourceSHA256'] == SHA
    assert raw['originalOwnership']['sourceGraphVerified'] and raw['exactCurrentComponentRoute']['qualified']
    assert raw['exactWholeCellCoverage']['covered'] and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted'] == 14819
    assert raw['geographicCell']['targetCoversWholeCell'] and raw['freshCurrentIdentity']['exactObjectAndCSUID']
    assert not raw['passed'] and set(raw['reasons']) == {'fresh-current-spatial-bound:targetCoveredBySourceProjection', 'full-source-target-coverage'}
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == SHA
    refs.append(asset)
    tri = decode_original_world_triangles(asset.read_bytes())
    assert len(tri) == 14819 and digest(tri.astype('<f8').tobytes()) == raw['worldTrianglesSHA256']
    target = shapely.Polygon(form['rings'][0], form['rings'][1:])
    projection = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]))
    missing = target.difference(projection)
    shell = shapely.union_all([shapely.Polygon(p.exterior) for p in shapely.get_parts(projection) if p.geom_type == 'Polygon'])
    assert projection.intersection(target).area / target.area == context['targetCoveredBySourceProjection']
    assert context['targetCoveredBySourceProjection'] == 0.9342413622267347 and context['unrelatedIntersectingForms'] == 1
    foreign_batch = prefix + 'foreign-basics-v1-20261025'
    foreign = take(foreign_batch, 'summary.json')
    neighbour = next(r for r in foreign['rows'] if r['uid'] == UID and r['foreignUid'] == 'landsd/70279:0')
    assert all(r['allFiniteContactPairs'] == 0 for r in neighbour['modes'])
    basic = take(foreign_batch, 'basic.json')
    shelter = next(r for r in basic['rows'] if r['uid'] == 'landsd/70279:0')
    shelter_tri = np.asarray(shelter['position']).reshape(-1, 3)[np.asarray(shelter['index']).reshape(-1, 3)]
    gap = float(tri[:, :, 1].min() - shelter_tri[:, :, 1].max())
    assert gap > 10, 'Unrelated lower structure needs independent role investigation'
    primary = prefix + 'primary-records-v1-20261025'
    footprint = next(r['attributes'] for r in take(primary, 'footprints.json')['features'] if r['attributes']['BuildingCSUID'] == form['buildingCSUID'])
    relation = next(r['attributes'] for r in take(primary, 'relations.json')['features'] if r['attributes']['BuildingCSUID'] == form['buildingCSUID'])
    structure = next(r['attributes'] for r in take(primary, 'structures.json')['features'] if r['attributes']['BuildingStructureID'] == relation['BuildingStructureID'])
    assert footprint['BuildingID'] == form['buildingId'] == 1103130746
    assert footprint['BuildingNameEN'] == form['name'] == 'Beverly Hill Block D'
    assert footprint['Storeys'] == structure['Storeys'] == 37 and structure['OPNo'] == 'H141/88'
    images = []
    for batch, names in [
        ('government-xl-beverly-255541-after-fe-source-views-v1-20261025', ['whole-source-plan.png', 'whole-source-perspectives.png']),
        ('government-xl-beverly-d-after-fe-official-map-v1-20261025', ['official-map-comparison.png']),
    ]:
        take(batch, 'summary.json')
        for name in names:
            p = BASE / batch / name
            assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
            refs.append(p)
            images.append(dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == raw['exactRouteManifestSHA256']
    refs.append(manifest)
    proof = dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True)
    review = dict(uid=UID, reviewer='Codex ROOT', modelId=source['modelId'], sourceSHA256=SHA,
                  sourceFormSHA256=raw['sourceFormSHA256'], worldTrianglesSHA256=raw['worldTrianglesSHA256'],
                  completeSourceFaces=14819, identityOnlyApproved=True, identityReviewApproved=True,
                  identityProof=proof, rawIdentityVerbatim=raw, rawReasonsRetained=raw['reasons'],
                  imagesActuallyInspected=images, targetCoveredBySourceProjection=context['targetCoveredBySourceProjection'],
                  missingTargetAreaM2=missing.area, internalHoleMissingAreaM2=missing.intersection(shell).area,
                  outsideShellMissingAreaM2=missing.difference(shell).area, sourceExcessAreaM2=projection.difference(target).area,
                  unrelatedShelterMaximumY=float(shelter_tri[:, :, 1].max()), sourceMinimumY=float(tri[:, :, 1].min()),
                  sourceAboveCompleteShelterByM=gap, primaryFootprint=footprint, primaryStructure=structure,
                  reviewBasis=[
                      'Exact original root/graph, stable CSUID/BuildingID, unique current Tower routing and the complete geographic cell bind this immutable source to Block D. Fresh primary records independently identify the37-storey tower under H141/88.',
                      'ROOT inspected complete source plan/perspectives and the independent LandsD basemap comparison. The coherent cross-shaped tower aligns with the mapped building; repeated facade appendages and the northern outline difference remain part of the unchanged original. No shift, scaling, trimming or manual alignment was performed.',
                      'Keep the raw93.424136% footprint coverage failure and both reasons verbatim. Missing footprint area is separately split into internal holes and outside-shell outline differences; the entire deficit is not described as a void. This exact-source assignment decision does not lower the95% automatic rule.',
                      'The one unrelated footprint overlap belongs to lower open-sided structure70279. Complete actual BASIC geometry is more than10m below every source vertex, and all before-BASIC/four-source-world contact checks are zero. It is not assigned as a support or included in D.',
                      'Only exact source identity and its two coverage reasons are interpreted here. Terrain, podium support, source/native roles, collision, browser/device images and publication remain independent. Official basemap date is unconfirmed; geographic context does not establish centimetre-level or matching-date survey accuracy.',
                  ], sourceIdentityReviewUsedAI=True, aiGeometryModelling=False, sourceGeometryChanges=0,
                  placementReviewed=False, physicalAccepted=False, publicationApproved=False, installationApproved=False)
    interpreted = deepcopy(raw)
    interpreted.update(passed=True, reasons=[], proof=proof, rawIdentityVerbatim=raw,
                       sourceSpecificIdentityReview=review, installationApproved=False, physicalAccepted=False)
    save(out / 'ROOT-IDENTITY-REVIEW.json', review)
    save(out / 'reviewed-identity.json', interpreted)
    refs.append(HERE / 'exact_packed_world_geometry_20261009.py')
    module('beverly_d_identity_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'exact-source-tower-footprint-identity-review', refs, dict(uids=[UID], identityAccepted=True, rawReasonsRetained=raw['reasons'], sourceAboveCompleteShelterByM=gap, installationApproved=False, physicalAccepted=False, sourceGeometryChanges=0, sourceIdentityReviewUsedAI=True))


if __name__ == '__main__':
    main()
