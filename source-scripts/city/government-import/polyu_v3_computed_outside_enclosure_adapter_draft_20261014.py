"""UNEXECUTED V3 constructor adapter; untouched literal/prefix/parent packing.

Only affected computed outside polygons take the reviewed immediate-cell path.
Its closed projection observations are diagnostics, not new admission gates.
"""
from fractions import Fraction as F
import polyu_face891_outside_float32_cell_enclosure_v1_draft_20261014 as enclosure


def affected_outside(proof,ideal,shared_cells,*,protected_literal=False):
    assert not protected_literal,'protected literal cannot use computed enclosure'
    assert not proof.get('projectedVerticalOrZeroPreservedWhole')
    assert F(proof['exactInsideMaskUnionIntrinsicArea'])>0,'unaffected source must retain old raw triplet'
    pieces=[];account=[]
    for ordinal,poly in enumerate(proof['outside']):
        points=enclosure.prior.rational_points(poly)
        result=enclosure.enclose(enclosure.prior.projected(points),ideal,shared_cells)
        normal=result['sourcePlane']['normal']
        for local,triangle in enumerate(result['triangles']):
            pieces.append(dict(exactOwnPlanePoints=triangle['idealSourcePlanePoints'],
                packedPieceTriplet=triangle['packedPieceTriplet'],
                exactPackedSourcePlaneResiduals=[v*normal[1]for v in triangle['exactVerticalSourcePlaneResidualM']],
                packingResidualsMeasuredNotWaived=True,noOtherLayerYUsed=True,
                enclosureOutsidePolygon=ordinal,enclosureLocalTriangle=local,
                exactOutsideExpansionAreaM2=result['exactHullExpansionAreaM2'],
                packedGeometryChangedFreshQualificationRequired=True))
        account.append(dict(outsidePolygon=ordinal,**result))
    return pieces,dict(completeComputedOutsidePolygonAccounting=account,
        onlyAffectedComputedOutsideUsesEnclosure=True,protectedLiteralAndPrefixNotModified=True,
        ownPlanePreservedBeforeStorage=True,closedProjectionFindingsNotAdmissionGate=True,
        currentParentRestorationPackingUnchanged=True,
        freshExpandedRegionLayerCompatibilityOrdinaryAndRuntimePending=True)
