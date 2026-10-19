"""Exact Central Library podium identity review; independent physical gates remain open."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-central-library-podium-identity-review-v1-20261019'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
PAIR = BASE / 'government-xl-central-library-private-ground-v1-20261019'
VIEWS = BASE / 'government-xl-central-library-loader-identity-v1-20261019'
CONTEXT = BASE / 'government-xl-next-twenty-original-identity-v1-20261018/232240:0'

def main():
    assert not DOC.exists()
    pins, refs = {}, [Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [VIEWS]:
            receipt = read(folder / 'result.json')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
            refs.append(folder / 'result.json')
            for e in receipt['evidenceRefs']:
                assert e['path'] not in pins or pins[e['path']] == e['sha256']
                pins[e['path']] = e['sha256']
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
    row = next(r for r in read(PAIR / 'selection.json.gz')['rows'] if r['uid'] == 'landsd/232240:0')
    proof = verify_files(row, read(CONTEXT / 'context.json'), LOCAL / '232240:0')
    old = read(CONTEXT / 'identity.json')
    for k in ['sourceSHA256', 'sourceFormSHA256', 'worldTrianglesSHA256', 'freshCurrentIdentity', 'reasons']:
        assert proof[k] == old[k], k
    assert proof['originalOwnership']['sourceGraphVerified']
    assert proof['exactCurrentComponentRoute']['qualified']
    assert proof['exactWholeCellCoverage']['covered']
    assert proof['geographicCell']['targetCoversWholeCell']
    assert set(proof['reasons']) == {'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-maximum-extent','full-source-target-coverage'}
    projection=proof['originalOwnership']['fullProjection']
    assert projection['exactObjectAndCSUID'] and .9210 < projection['targetCoveredBySourceProjection'] < .9211
    assert 19.539 < projection['sourceExcessMaximumDistanceFromTargetM'] < 19.540
    assert projection['sourceExcessCoveredByUnrelatedFormsM2']==0
    assert {f['uid'] for f in projection['intersectingForms']}=={'landsd/232240:0','landsd/227428:0'}
    import numpy as np,shapely
    from shapely.geometry import Polygon
    from exact_packed_world_geometry_20261009 import decode_original_world_triangles
    view=read(VIEWS/'input.json')['models'][0];projections=[]
    for m in [view,*view['originalComponents']]:
        asset=ROOT/m['assetPath'];assert digest(asset.read_bytes())==m['sourceSHA256'];refs.append(asset)
        triangles=decode_original_world_triangles(asset.read_bytes());projections.append(shapely.union_all(shapely.polygons(triangles[:,:,[0,2]])))
    assert len(projections)==2
    form=row['source']['building'];target=Polygon(form['rings'][0],form['rings'][1:]);missing=target.difference(projections[0]);remaining=missing.difference(projections[1])
    assert 423.07<missing.area<423.09 and 18.01<remaining.area<18.02
    save(DOC/'component-footprint-account.json',dict(podiumMissingTargetM2=missing.area,missingCoveredByInstalledMainM2=missing.intersection(projections[1]).area,remainingAfterBothOriginalsM2=remaining.area,remainingGeometry=shapely.to_geojson(remaining),targetAreaM2=target.area,combinedCoverage=1-remaining.area/target.area,qualification='Source component coverage context, not a geometry change or a new global threshold.'))
    refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    images = [VIEWS / (n + '.png') for n in ['whole', 'whole-reverse', 'frontage']]
    save(DOC / '232240:0-review.json', dict(
        uid=row['uid'], reviewer='Codex ROOT', reviewType='exact-original-podium-identity',
        sourceSHA256=row['sourceSHA256'], sourceFormSHA256=proof['sourceFormSHA256'],
        worldTrianglesSHA256=proof['worldTrianglesSHA256'], modelId=row['modelId'], sourceFaces=row['triangles'],
        identityOnlyApproved=True, identityReviewApproved=True,
        identityProof=dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True),
        rawProof=proof, rawReasonsRetained=proof['reasons'],
        imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())) for p in images],
        reviewBasis=[
            'Exact government ObjectID232240, podium CSUID3758415674P20060312, source graph and georef-cell route bind this unchanged original source to the current Central Library podium form.',
            'ROOT inspected all three complete original-source captures. Green podium terraces, lower perimeter, front steps and side extension align with the purple installed original main library component227428 in unchanged native pose. The broad extension follows the authored podium and does not intersect unrelated recorded building forms.',
            'The podium alone covers92.1068percent of its recorded footprint. Of423.0767m2 missing from the podium projection,405.0616m2 is supplied by the installed original main building. The remaining18.0150m2 is retained as an outline mismatch; the exact residual geometry is recorded. No claim of perfect outline agreement or repaired geometry is made.',
            'The original graph, exact government metadata and inspected complementary assembly establish identity despite conservative extent/coverage proxy flags. Preserve the entire source and all four raw flags in this source-specific decision; no blanket identity threshold change.',
            'Identity only. The remaining terrain intersection and final viewer acceptance are independent and remain unresolved. No placement, publication or installation approval is implied.'
        ], sourceIdentityReviewUsedAI=True, aiGeometryModelling=False,
        placementReviewed=False, publicationApproved=False, installationApproved=False))
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
        refs.append(ROOT / p)
    refs.extend([CONTEXT / 'context.json', CONTEXT / 'identity.json', HERE / 'exact_original_georef_cell_identity_20261009.py'])
    refs.extend(p for p in LOCAL.rglob('*') if p.is_file())
    module('times_square_podium_identity_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-original-podium-identity-review', list(dict.fromkeys(refs)),
        dict(uids=[row['uid']], identityAccepted=True, installationApproved=False))

if __name__ == '__main__':
    main()
