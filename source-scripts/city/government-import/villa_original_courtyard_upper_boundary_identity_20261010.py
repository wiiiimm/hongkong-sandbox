"""Proposed named original courtyard-edge identity, never a physical certificate.

The distinct canopy has no primary surveyed height or recovered original. Its
current estimated basic mesh stays an independent physical actor. This kernel
uses the primary common boundary, full source ownership and exactly 16 authored
upper faces; it does not claim real-world canopy clearance or shared ownership.
Complete current/native/provider acquisition and raw preflight bindings belong
to a separate current adapter before any production promotion.
"""
from copy import deepcopy
from datetime import datetime, timezone
import numpy as np
import shapely
from run import digest
from exact_mesh_components import face_components
from no1_garden_original_overhead_roof_edge_identity_20261010 import polygon, primary_polygon

UID = 'landsd/89917:0'
FOREIGN = 'landsd/325786:0'
SOURCE_SHA = '4407cbd52574f50e6b6bdddc6e581c96bbd0653426f89df0e490ae0b2096935d'
WORLD_SHA = '78d1003ea73bba4ccb0c8cf2210d6b1e4fb89dad247773fe999ac5027a775f78'
EXPECTED = {UID: ('2162333401P20050627', 1105779586, 'Podium'),
            FOREIGN: ('2162233384T20211022', 1910216544, 'Open-sided Structure')}
ROLE_FACES = {6727, 6728, 6733, 6737, 6738, 6743, 6744, 6750,
              14689, 14690, 14693, 14699, 14700, 14705, 14706, 14712}
RAW_REASONS = {'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2',
               'full-source-unrelated-overlap'}
POLICY = 'named-original-villa-courtyard-upper-boundary-identity-proposal-v1'


def named_proof(previous, row, own, current_forms, primary, missing_foreign):
    assert row['uid'] == UID and row['modelId'] == 'B216233340102062G0'
    assert row['sourceSHA256'] == SOURCE_SHA
    assert previous['uid'] == UID and previous['sourceSHA256'] == SOURCE_SHA
    assert previous['originalOwnership']['sourceGraphVerified']
    assert previous['originalOwnership']['originalRootName'] == row['modelId']
    own = np.asarray(own, float)
    assert own.shape == (16669, 3, 3) and np.isfinite(own).all()
    assert digest(own.astype('<f8').tobytes()) == WORLD_SHA, 'Complete original source world/pose differs'
    forms = {b['uid']: b for b in current_forms}
    assert len(forms) == len(current_forms) and UID in forms and FOREIGN in forms
    assert forms[UID] == row['source']['building']
    assert len(primary) == 2
    providers = {}
    for uid, (csuid, bid, kind) in EXPECTED.items():
        b = forms[uid]
        assert (b['buildingCSUID'], b['buildingId'], b['structureType']) == (csuid, bid, kind)
        matches = [f for f in primary if f['attributes']['BuildingCSUID'] == csuid]
        assert len(matches) == 1
        f = matches[0]
        p = f['attributes']
        providers[uid] = f
        assert (p['Status'], p['BuildingID'], p['BuildingBlockType'], str(p['GeoRefNo'])) == ('Active', bid, kind, csuid[:10])
        assert datetime.fromtimestamp(p['DateCreate']/1000, timezone.utc).strftime('%Y%m%d') == csuid[11:]
        assert p['BaseHeight'] == b['baseHeightHKPD'] and p['TopHeight'] == b['topHeightHKPD']
    assert providers[UID]['attributes']['TopHeight'] == 11.9
    other = forms[FOREIGN]
    assert other['baseHeightHKPD'] is None and other['topHeightHKPD'] is None
    assert other['baseSource'] == 'terrain-estimated' and other['heightSource'] == 'estimated'
    assert other['base'] == 6.014 and other['height'] == 3.0
    assert providers[FOREIGN]['attributes']['Storeys'] is None
    assert missing_foreign['uid'] == FOREIGN and missing_foreign['exactNativeMatches'] == 0
    assert missing_foreign['currentSource']['building'] == other
    assert not missing_foreign.get('profiles'), 'A newly available original requires independent complete native silhouette evaluation'
    parts = face_components(own)
    assert len(parts) == 58 and len(parts[0]) == 11783 and ROLE_FACES <= set(parts[0])
    role = own[sorted(ROLE_FACES)]
    normal = np.cross(role[:, 1]-role[:, 0], role[:, 2]-role[:, 0])
    assert (normal[:, 1] > 0).all(), 'Every named face must remain an original upward finite roof edge'
    assert (role[:, :, 1] > providers[UID]['attributes']['TopHeight']).all()
    # Original duplicate face records are retained, never simplified or omitted.
    _, counts = np.unique(role.reshape(16, 9), axis=0, return_counts=True)
    assert sorted(counts.tolist()) == [2] * 8
    role_min = float(role[:, :, 1].min())
    estimated_top = float(other['base'] + other['height'])
    assert role_min > estimated_top, 'Actual current estimated actor must remain below the entire named upper surface'
    projection = shapely.union_all(shapely.polygons(own[:, :, [0, 2]]))
    others = [b for b in current_forms if b['uid'] not in {UID, FOREIGN}]
    foreign_shapes = shapely.union_all([polygon(b['rings']) for b in others])
    reasons = [r for r in previous['reasons'] if r not in RAW_REASONS]
    checks = {}
    for label, target, foreign_target in [
        ('current', polygon(forms[UID]['rings']), polygon(other['rings'])),
        ('primary', primary_polygon(providers[UID]), primary_polygon(providers[FOREIGN]))]:
        assert target.intersection(foreign_target).area == 0
        common = target.boundary.intersection(foreign_target.boundary)
        assert common.length > 0, 'Independent provider/current boundaries must genuinely coincide'
        extra = projection.difference(target)
        overlap = extra.intersection(foreign_target)
        ids = {i for i, t in enumerate(own) if shapely.Polygon(t[:, [0, 2]]).intersection(overlap).area > 0}
        assert ids == ROLE_FACES, 'Complete full-source excess must account for exactly all16 named authored records'
        measures = dict(targetCoverage=projection.intersection(target).area/target.area,
            maximumSourceExtentM=float(shapely.distance(shapely.points(own[:, :, [0, 2]].reshape(-1, 2)), target).max()),
            allOtherForeignExcessM2=float(extra.intersection(foreign_shapes).area),
            rawNamedForeignExcessM2=float(overlap.area), allNamedOverlapFaceIds=sorted(ids),
            primaryOrCurrentSharedBoundaryLengthM=float(common.length),
            separatePrimaryOrCurrentFootprintIntersectionM2=0.0,
            maximumNamedRoofEdgeExtentFromOwnBoundaryM=float(shapely.distance(shapely.points(role[:, :, [0, 2]].reshape(-1, 2)), target).max()))
        checks[label] = measures
        if not (.95 <= measures['targetCoverage'] <= 1.000000001 and measures['maximumSourceExtentM'] <= 10 and measures['allOtherForeignExcessM2'] <= 1):
            reasons.append('complete-source-' + label + '-spatial-bound')
    raw = sorted(set(previous['reasons']) & RAW_REASONS)
    assert raw
    out = deepcopy(previous)
    passed = not reasons
    out.update(policy=POLICY, passed=passed, reasons=sorted(set(reasons)),
        rawUnrelatedOverlapReasonsRetained=raw, explicitDistinctCanopyUID=FOREIGN,
        completeOriginalWorldSHA256=WORLD_SHA, completeOriginalFaces=16669, completeOriginalParts=58,
        completeOriginalMainBodyFaceIds=parts[0].tolist(), allRawNamedOverlapFaceIds=sorted(ROLE_FACES),
        independentFullSourceSpatialChecks=checks, completeCurrentForeignActorsRetained=current_forms,
        allOtherActorsStillForeignUIDs=sorted(b['uid'] for b in others),
        sourceUpperBoundaryMinimumYHKPD=role_min, actualEstimatedCurrentCanopyTop=estimated_top,
        originalForeignNativeUnavailable=True, surveyedCanopySeparationClaim=False,
        wholeOwnMainBodyOverheadClaim=False, commonOwnershipClaim=False, structuralSupportClaim=False,
        foreignRemoval=False, foreignCollisionExemption=False, foreignTerrainExemption=False,
        physicalAccepted=False, installationApproved=False, sourceGeometryChanges=0,
        proof={k: passed for k in ['exactObjectId', 'exactBuildingCSUID', 'uniqueViewerMatch', 'identityAccepted']},
        qualification='Proposed identity-only interpretation of exactly16 byte-bound upward source-owned courtyard-edge records in the unchanged complete mainbody. Current and primary Podium/Open-sidedStructure polygons share an exact boundary and zero area, while real source strips/raw overlap remain. Foreign surveyed heights/original geometry are unavailable; only actual current estimated mesh separation is measured. All foreign physical/collision/terrain checks remain independent. No legal/shared ownership, function, structural support, whole-component overhead, foreign omission or tolerance credit.')
    return out
