"""Compare exact originals/current/live footprints and bind inspected diagrams.

Diagnostic only. Preserve every identity failure and grant no installation credit.
"""
from pathlib import Path
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-greenfield-after-fung-yip-'
BATCH = P + 'source-footprint-context-v1-20261025'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, filename):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        p = BASE / batch / filename
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)

    selection = take(P + 'selection-v1-20261025', 'selection.json.gz')
    primary = take(P + 'primary-records-v1-20261025', 'footprints.json')
    official = {f['attributes']['BuildingCSUID']: f for f in primary['features']}
    permit = take(P + 'complete-permit-v1-20261025', 'summary.json')
    assert permit['allRequestedPermitRecordsReturned']
    assert permit['permits'] == ['NT231/89', 'NT44/90', 'NT8/90']
    assert permit['completePermitStructures'] == 14 and permit['completePermitFootprints'] == 13
    permit_features = take(P + 'complete-permit-v1-20261025', 'complete-permit-footprints.json')['features']
    permit_ids = {f['attributes']['BuildingCSUID'] for f in permit_features}
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    permit_forms = []
    for tile in read(manifest)['tiles']:
        p = ROOT / '3d-viewer' / tile['url']
        matched = [f for f in read(p)['buildings'] if f.get('buildingCSUID') in permit_ids]
        if matched:
            refs.append(p)
            permit_forms.extend(matched)
    assert len(permit_forms) == 13 and len({f['buildingCSUID'] for f in permit_forms}) == 13
    assert sum(f['structureType'] == 'Tower' for f in permit_forms) == 11
    assert not ({'2930423797T20050430', '2929423757T20050430', '2921923713T20050430'} & permit_ids)
    rows, images = [], []
    for row in selection['rows']:
        uid, form = row['uid'], row['source']['building']
        identity = take(P + 'identity-v1-20261025', uid.split('/')[1] + '/identity.json')
        assert identity['sourceSHA256'] == row['sourceSHA256']
        assert identity['originalOwnership']['sourceGraphVerified'] and identity['exactCurrentComponentRoute']['qualified']
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        refs.append(asset)
        tri = decode_original_world_triangles(asset.read_bytes())
        assert len(tri) == row['triangles']
        current = shapely.Polygon(form['rings'][0], form['rings'][1:])
        feature = official[form['buildingCSUID']]
        rings = [[(float(e)-834500, 816500-float(n)) for e, n in ring] for ring in feature['geometry']['rings']]
        live = shapely.symmetric_difference_all([shapely.Polygon(r) for r in rings])
        assert live.is_valid and current.is_valid and feature['attributes']['Status'] == 'Active'
        projection = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]))
        missing = current.difference(projection)
        coordinates = shapely.get_coordinates(missing)
        metrics = dict(
            uid=uid, sourceSHA256=row['sourceSHA256'], completeOriginalFaces=len(tri),
            currentFootprintAreaM2=current.area,
            liveCurrentSymmetricDifferenceM2=current.symmetric_difference(live).area,
            sourceCoverageCurrent=float(current.intersection(projection).area/current.area),
            sourceCoverageLive=float(live.intersection(projection).area/live.area),
            missingCurrentAreaM2=missing.area, missingGeometryType=missing.geom_type,
            missingBoundaryVerticesMaximumDistanceToSourceM=float(shapely.distance(shapely.points(coordinates), projection).max()) if len(coordinates) else 0,
            vertexMetricIsNotContinuousMaximumProof=True,
            exactSourceGraphVerified=True, exactCurrentComponentRouteQualified=True,
            exactWholeGeorefCellCovered=identity['exactWholeCellCoverage']['covered'],
            rawIdentityReasonsRetained=identity['reasons'],
            publishedPermitFamilyIncludesThisCSUID=form['buildingCSUID'] in permit_ids)
        if uid == 'landsd/198115:0':
            assert .943 < metrics['sourceCoverageCurrent'] < .945
            assert .938 < metrics['sourceCoverageLive'] < .940
            assert 12.58 < missing.area < 12.60
        rows.append(metrics)
        batch = 'government-xl-greenfield-' + uid.split('/')[1].split(':')[0] + '-after-fung-yip-identity-views-v1-20261025'
        take(batch, 'summary.json')
        for name in ['whole-source-plan.png', 'whole-source-perspectives.png']:
            p = BASE / batch / name
            assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
            refs.append(p)
            images.append(dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()), actuallyViewed=True))
    assert len(images) == 8 and digest(manifest.read_bytes()) == selection['manifestSHA256']
    result = dict(
        uids=[r['uid'] for r in rows], rows=rows, imagesActuallyViewed=images,
        completePermitFamilies=permit, permitViewerForms=[dict(uid=f['uid'], name=f.get('name'), csuid=f['buildingCSUID'], structureType=f['structureType']) for f in permit_forms],
        currentManifestSHA256=selection['manifestSHA256'], reviewer='ROOT',
        sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False,
        identityAccepted=False, physicalAcceptance=False, installationApproved=False,
        humanStatus='In process', newlyInstalled=0,
        observations=[
            'ROOT opened all8complete original plan/perspective diagrams. Primary258419 is the curved multi-level podium with street-side extensions.195705 is a small low rectangular structure;198115 is a long low roof/wall assembly with upstanding roof blocks;332916 is a low circular structure with perimeter supports. Source labels/types alone do not establish whole-landmark architecture.',
            'The main podium has three official permit relations; their complete families map to11estate towers and2podiums. The three selected auxiliary CSUIDs have fresh live footprints but are NOT in those permit families. Do not infer their membership or ownership from the podium permit evidence.',
            '195705covers100percent of both current and fresh live target footprints while failing complete one-metre cell coverage.198115covers94.4009percent of current and93.8749percent of live footprint. The12.5879m2current gap remains real; do not round it to95percent or call the vertex-distance metric a continuous certificate.',
            'The full four-source role/identity interpretation remains incomplete. Current private terrain/neighbour/support/browser binding still needs refresh. No failure is waived, no sources are corrupted or permanently rejected by this diagnostic, and no AI geometry task or human decision has been established.'
        ])
    save(out / 'summary.json', result)
    refs += [HERE / 'exact_packed_world_geometry_20261009.py']
    module('greenfield_current_context', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'complete-current-original-live-footprint-context-and-inspected-diagrams', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
