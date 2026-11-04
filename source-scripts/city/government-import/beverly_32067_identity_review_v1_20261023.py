"""Review only Beverly Garden Block 5's exact-source footprint coverage difference."""
from pathlib import Path
from copy import deepcopy
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = 'government-xl-beverly-32067-source-identity-review-v1-20261023'
    out = base / batch
    assert not out.exists()
    names = dict(identity='government-xl-beverly-32067-current-identity-v1-20261023', capture='government-xl-beverly-32067-current-capture-v1-20261023', plots='government-xl-beverly-32067-source-identity-views-v1-20261023', official='government-xl-beverly-32067-official-topographic-context-v1-20261023')
    refs, cache = [Path(__file__)], {}
    def take(key, name):
        folder = base / names[key]
        if key not in cache:
            cache[key] = authenticate(folder)[1]
            refs.append(folder / 'result.json')
        path = folder / name
        assert digest(path.read_bytes()) == cache[key][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    raw = take('identity', '32067:0/identity.json')
    context = take('identity', '32067:0/context.json')['identity']
    selection = take('capture', 'selection.json.gz')
    row, = selection['rows']
    uid = 'landsd/32067:0'
    assert row['uid'] == raw['uid'] == uid and row['modelId'] == 'B450401899901063C0'
    assert row['source']['building']['buildingCSUID'] == '4504018999T20050430'
    assert raw['originalOwnership']['sourceGraphVerified'] and raw['originalOwnership']['originalRootName'] == row['modelId']
    assert raw['exactCurrentComponentRoute']['qualified'] and raw['exactCurrentComponentRoute']['uid'] == uid
    assert raw['exactWholeCellCoverage']['covered'] and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted'] == 12093
    assert raw['geographicCell']['targetCoversWholeCell']
    assert not raw['passed'] and set(raw['reasons']) == {'fresh-current-spatial-bound:targetCoveredBySourceProjection', 'full-source-target-coverage'}
    assert context['unrelatedIntersectingForms'] == context['sourceExcessCoveredByUnrelatedFormsM2'] == 0
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == raw['sourceSHA256'] == row['sourceSHA256']
    refs.append(asset)
    tri = decode_original_world_triangles(asset.read_bytes())
    assert len(tri) == 12093 and digest(tri.astype('<f8').tobytes()) == raw['worldTrianglesSHA256']
    projection = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]))
    form = row['source']['building']
    target = shapely.Polygon(form['rings'][0], form['rings'][1:])
    missing = target.difference(projection)
    shell = shapely.union_all([shapely.Polygon(p.exterior) for p in shapely.get_parts(projection) if p.geom_type == 'Polygon'])
    assert projection.intersection(target).area / target.area == context['targetCoveredBySourceProjection']
    plots = take('plots', 'summary.json')
    assert plots['sourceSHA256'] == raw['sourceSHA256'] and plots['originalWorldSHA256'] == raw['worldTrianglesSHA256']
    take('official', 'summary.json')
    images = []
    for key, name in [('plots', 'whole-source-plan.png'), ('plots', 'whole-source-perspectives.png'), ('official', 'official-map-comparison.png')]:
        path = base / names[key] / name
        assert digest(path.read_bytes()) == cache[key][str(path.relative_to(ROOT))]
        refs.append(path)
        images.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == raw['exactRouteManifestSHA256']
    refs.append(manifest)
    for url, sha in raw['exactRouteTileHashes'].items():
        path = ROOT / '3d-viewer' / url
        assert digest(path.read_bytes()) == sha
        refs.append(path)
    tile = ROOT / '3d-viewer' / row['source']['tile']
    assert next(f for f in read(tile)['buildings'] if f['uid'] == uid) == form
    refs.append(tile)
    proof = dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True)
    review = dict(uid=uid, reviewer='Codex ROOT', modelId=row['modelId'], sourceSHA256=raw['sourceSHA256'], sourceFormSHA256=raw['sourceFormSHA256'], worldTrianglesSHA256=raw['worldTrianglesSHA256'], completeSourceFaces=12093, identityOnlyApproved=True, identityReviewApproved=True, identityProof=proof, rawIdentityVerbatim=raw, rawReasonsRetained=raw['reasons'], imagesActuallyInspected=images, targetCoveredBySourceProjection=context['targetCoveredBySourceProjection'], missingTargetAreaM2=missing.area, internalHoleMissingAreaM2=missing.intersection(shell).area, outsideShellMissingAreaM2=missing.difference(shell).area, reviewBasis=['The original root, exact ObjectID/CSUID, complete geographic cell and unique Tower route bind this unchanged source to Beverly Garden Block 5. No unrelated current footprint overlaps the source.', 'ROOT inspected both full-source diagrams and the independent official LandsD basemap comparison. The source main cross-shaped tower wings align with the mapped building; its lower connecting appendages and facade detail remain part of the original source. No manual alignment or pose change was used.', 'The raw 94.294817% footprint coverage failure is preserved. Missing area is 35.619272m2: 9.669158m2 inside projected shell holes and 25.950114m2 outside that shell, including open recesses and outline differences. The whole missing area is not called an internal void. The simpler recorded footprint differs from the detailed authored tower; this is a source assignment interpretation, not a change to the 95% automatic rule.', 'Accept only the exact source identity and these two coverage reasons. Terrain/contact, height/placement, foundations, collision, all neighbours, device/browser and publication remain independent. Map acquisition date is unconfirmed; the map is geographic context, not centimetre-level or survey-date proof.'], sourceIdentityReviewUsedAI=True, aiGeometryModelling=False, sourceGeometryChanges=0, placementReviewed=False, physicalAccepted=False, publicationApproved=False, installationApproved=False)
    interpreted = deepcopy(raw)
    interpreted.update(passed=True, reasons=[], proof=proof, rawIdentityVerbatim=raw, sourceSpecificIdentityReview=review, installationApproved=False, physicalAccepted=False)
    save(out / 'ROOT-IDENTITY-REVIEW.json', review)
    save(out / 'reviewed-identity.json', interpreted)
    refs.append(HERE / 'exact_packed_world_geometry_20261009.py')
    module('beverly_identity_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'exact-source-tower-footprint-identity-review', refs, dict(uids=[uid], identityAccepted=True, rawReasonsRetained=raw['reasons'], installationApproved=False, physicalAccepted=False, sourceGeometryChanges=0, sourceIdentityReviewUsedAI=True))


if __name__ == '__main__':
    main()
