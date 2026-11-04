"""UNEXECUTED saved GEOS coverage locator; no geometry/threshold changes."""
from fractions import Fraction as F
import numpy as np
from shapely.geometry import Polygon,box,mapping
from shapely.ops import unary_union
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from polyu_saved_hole_mask_attribution_v1_draft_20261014 import probe

def source_descriptor(p,face):
    assert p['candidateFace']==face
    ancestor=p.get('ancestor',{})
    return dict(candidateFace=face,kind=p['kind'],inUntouched1485Prefix=face<1485,
        inUnchanged8011OldSourceFamily=face<8011,
        oldPrivateFace=p.get('oldPrivateFace',ancestor.get('oldPrivateFace')),
        capturedParentFacet=ancestor.get('capturedParentFacet'),
        mask=p.get('mask'),partitionPointer=p.get('partitionProofReference'),
        insideCell=p.get('computedInsideCellEnclosure'),outsideCell=p.get('computedOutsideCellEnclosure'),
        fullProvenanceRemainsInBoundNominee=True,noArchitecturalOrPhysicalRoleClaim=True)

def regions(geometry):
    if geometry.is_empty or geometry.area==0:return []
    if geometry.geom_type=='Polygon':return [geometry]
    assert geometry.geom_type in['MultiPolygon','GeometryCollection']
    return [p for g in geometry.geoms for p in regions(g)if p.area>0]

def measure(raw,domain):
    polygons=[Polygon(t[:,[0,2]])for t in raw];included=[p for p in polygons if p.area>1e-10]
    extent=box(*domain);union=unary_union(included);missing=extent.difference(union);outside=union.difference(extent)
    return polygons,dict(completeNativeFaces=len(raw),validatorIncludedFaces=len(included),existingFaceAreaAdmissionM2=1e-10,
        existingCoverageToleranceM2=max(.001,extent.area*1e-7),measuredMissingAreaM2=missing.area,
        measuredOutsideAreaM2=outside.area,measuredSymmetricDifferenceAreaM2=union.symmetric_difference(extent).area,
        missingGeometry=mapping(missing),outsideGeometry=mapping(outside),
        sameValidatorGEOSMeasurementNotExactFractionWholeUnion=True,noToleranceOrApprovalChange=True),missing,outside

def attribute_component(component,ordinal,kind,complete,raw,polygons,provenance):
    bounds=list(component.bounds);xmin,zmin,xmax,zmax=bounds
    ids,binding=complete.select([(F(xmin),F(0),F(zmin)),(F(xmax),F(0),F(zmax))])
    adjacent=[]
    for value in ids:
        j=int(value);p=polygons[j];boundary=p.boundary.intersection(component.boundary)
        if not boundary.is_empty:
            adjacent.append(dict(**source_descriptor(provenance[j],j),actualPackedTriplet=raw[j].tolist(),
                projectedFacetGeometry=mapping(p),measuredBoundaryIntersection=mapping(boundary),
                measuredBoundaryLengthM=boundary.length,GEOSIntersectionLocatorOnly=True))
    witness=component.representative_point();xz=(F(witness.x),F(witness.y));membership=probe(xz,raw,complete,native_admission=True)
    return dict(region=ordinal,kind=kind,measuredAreaM2=component.area,absoluteXZBounds=bounds,geometry=mapping(component),
        closedFacetBroadphase=binding,adjacentMeasuredBoundaryFacets=adjacent,
        completeClosedBBoxNominations=[source_descriptor(provenance[int(j)],int(j))for j in ids],
        GEOSRepresentativeDiagnosticPoint=dict(x=witness.x,z=witness.y,exactBinary64XZ=[str(x)for x in xz],
            nativeClosedMembership=membership,notClaimedExactAreaWitness=True),
        noBufferNearestSourceGuessOrSourceRoleAcceptance=True)
