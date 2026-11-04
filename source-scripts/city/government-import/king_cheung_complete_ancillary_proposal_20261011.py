"""Named complete original canopy proposal; diagnostic only, never identity approval.

All 104 proposed ancillary faces remain in every full projection/foreign test.
The 18,638 other faces keep the ordinary 10m vertex-extent contract. Neither
source ownership nor the architectural interpretation supplies a ground root.
"""
from datetime import datetime, timezone
import hashlib
import numpy as np
import shapely

UID = 'landsd/95691:0'
CSUID = '3080039468T20140728'
MODEL = 'B308003946801063C0'
SOURCE_SHA = 'daad7e84a632e97cd7af9c354dd3d6c122e2e1afc0afdc751f752a0f909cd119'
WORLD_SHA = '534046e403d3eb70a384e56be5294b294e5469e48aea57b9e3edd8e5d4028a78'
PART_FACES = {39: list(range(2012, 2092)) + list(range(2797, 2803)) + [18372, 18373],
              43: list(range(2803, 2811)), 44: list(range(2811, 2819))}
ROLE_IDS = sorted(f for faces in PART_FACES.values() for f in faces)
RAW_REASONS = ['fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM',
               'full-source-maximum-extent']

def polygon(rings):
    result = shapely.GeometryCollection()
    for ring in rings:
        result = result.symmetric_difference(shapely.Polygon(ring))
    assert result.is_valid and result.area > 0
    return result

def spatial_metrics(triangles, role_ids, target, foreign):
    """Unchanged ordinary vertex-extent/area limits; full source is never cut."""
    tri = np.asarray(triangles, dtype='<f8')
    assert tri.ndim == 3 and tri.shape[1:] == (3, 3) and np.isfinite(tri).all()
    assert role_ids == sorted(set(role_ids)) and all(0 <= i < len(tri) for i in role_ids)
    mask = np.ones(len(tri), bool)
    mask[role_ids] = False
    assert mask.any() and target.is_valid and target.area > 0
    projection = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]))
    distances = shapely.distance(shapely.points(tri[:, :, [0, 2]].reshape(-1, 2)), target).reshape(-1, 3)
    values = dict(completeSourceFaces=len(tri), completeSourceProjectionAreaM2=float(projection.area),
                  completeSourceTargetCoverage=float(target.intersection(projection).area / target.area),
                  fullRawVertexExtentMetres=float(distances.max()),
                  allOtherSourceFaces=len(tri) - len(role_ids),
                  allOtherSourceVertexExtentMetres=float(distances[mask].max()),
                  proposedAncillaryRawVertexExtentMetres=float(distances[role_ids].max()) if role_ids else None,
                  allFarVertexWitnessFaceIds=np.flatnonzero(distances.max(axis=1) > 10).tolist(),
                  completeSourceForeignExcessM2=float(projection.difference(target).intersection(foreign).area),
                  proposedAncillaryFacesOmittedFromProjection=False,
                  extentMethod='ordinary maximum projected source-vertex distance; not a finite-interior maximum certificate')
    values['ordinarySpatialGuardsOnCompleteProjectionAndRemainingFaces'] = (
        .95 <= values['completeSourceTargetCoverage'] <= 1.000000001 and
        values['allOtherSourceVertexExtentMetres'] <= 10 and values['completeSourceForeignExcessM2'] <= 1)
    return values

def proposal(previous, row, triangles, forms, provider, topology, low_contacts):
    tri = np.asarray(triangles, dtype='<f8')
    assert tri.shape == (18742, 3, 3) and np.isfinite(tri).all()
    assert hashlib.sha256(tri.tobytes()).hexdigest() == previous['worldTrianglesSHA256'] == WORLD_SHA
    assert row['uid'] == previous['uid'] == UID and row['modelId'] == MODEL and row['triangles'] == 18742
    assert row['sourceSHA256'] == previous['sourceSHA256'] == SOURCE_SHA
    assert previous['reasons'] == RAW_REASONS and not previous['passed']
    assert previous['originalOwnership']['sourceGraphVerified']
    assert previous['originalOwnership']['originalRootName'] == MODEL
    assert previous['exactWholeCellCoverage']['covered'] and previous['exactWholeCellCoverage']['wholeOriginalFacesAccounted'] == 18742
    groups = topology['sharedEdgeConnectedComponents']
    assert len(groups) == 908
    assert all(groups[i] == faces for i, faces in PART_FACES.items())
    assert len(ROLE_IDS) == 104 and len(set(ROLE_IDS)) == 104
    assert low_contacts['completeWorldSHA256'] == WORLD_SHA and low_contacts['completeFaces'] == 18742
    parts = low_contacts['completeLowParts']
    assert [p['component'] for p in parts] == [39, 43, 44]
    for p in parts:
        assert p['completeOriginalFaceIds'] == PART_FACES[p['component']]
        assert np.array_equal(np.asarray(p['completeOriginalTriangles']), tri[p['completeOriginalFaceIds']])
        assert p['allOtherOriginalFacesExamined'] == 18742 - len(p['completeOriginalFaceIds'])
        assert p['contacts']['allPairsExamined'] and p['contacts']['sourceFacesOmitted'] == 0
        expected_other = {39: 44, 43: None, 44: 39}[p['component']]
        contacts = p['contacts']['contacts']
        assert len(contacts) == (0 if expected_other is None else 8)
        assert all(c['otherRealComponent'] == expected_other and c['dimension'] == 1 for c in contacts)
    own = [f for f in forms if f['uid'] == UID]
    assert len({f['uid'] for f in forms}) == len(forms) and len(own) == 1 and own[0] == row['source']['building']
    assert (own[0]['buildingCSUID'], own[0]['buildingId'], own[0]['structureType']) == (CSUID, 1810130490, 'Tower')
    assert not provider.get('error') and not provider.get('exceededTransferLimit') and len(provider['features']) == 1
    assert provider['spatialReference'].get('latestWkid', provider['spatialReference'].get('wkid')) == 2326
    record = provider['features'][0]; a = record['attributes']
    assert (a['Status'], a['BuildingCSUID'], a['BuildingID'], a['BuildingBlockType'], str(a['GeoRefNo'])) == ('Active', CSUID, 1810130490, 'Tower', '3080039468')
    assert datetime.fromtimestamp(a['DateCreate'] / 1000, timezone.utc).strftime('%Y%m%d') == '20140728'
    official = polygon([[(x - 834500, 816500 - y) for x, y in ring] for ring in record['geometry']['rings']])
    foreign = shapely.union_all([polygon(f['rings']) for f in forms if f['uid'] != UID])
    checks = {name: spatial_metrics(tri, ROLE_IDS, target, foreign)
              for name, target in [('current', polygon(own[0]['rings'])), ('primary', official)]}
    assert all(set(v['allFarVertexWitnessFaceIds']) <= set(ROLE_IDS) for v in checks.values())
    return dict(uids=[UID], originalModelId=MODEL, sourceSHA256=SOURCE_SHA, completeWorldSHA256=WORLD_SHA,
                proposedRole='source-owned freestanding estate entrance canopy and posts; architectural interpretation only',
                completeFaces=18742, proposedAncillaryFaceIds=ROLE_IDS,
                completeSourcePartFaceIds={str(k): v for k, v in PART_FACES.items()}, ordinaryExtentFaces=18638,
                fullSourceSpatialChecks=checks, rawReasonsRetained=previous['reasons'], rawIdentityPassed=False,
                completeWholeGeoRefCellProofRetained=previous['exactWholeCellCoverage'],
                allOtherForeignUIDs=sorted(f['uid'] for f in forms if f['uid'] != UID),
                completeSourceContactsRetained=parts, sourceRootOwnershipRetained=True,
                photoInterpretationIsNotPrecisePlanRegistration=True, planRegistrationAccepted=False,
                canopyToMainBodyContactAccepted=False, freestandingGroundRootsStillRequired=[39, 43, 44],
                sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False, sourceGeometryChanges=0,
                sourceOnly=True, identityAccepted=False, currentAcceptance=False,
                physicalAccepted=False, structuralSupportAccepted=False, installationApproved=False,
                proposalSpatialGuardsSatisfied=all(v['ordinarySpatialGuardsOnCompleteProjectionAndRemainingFaces'] for v in checks.values()))
