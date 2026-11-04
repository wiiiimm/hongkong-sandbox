"""UNEXECUTED V3 ideal-surface proposal; DIFFERENT outside tessellation from V2.

Original government building/source bytes and poses are untouched. Removing
incidental outside cuts is scripted coplanar terrain subdivision/consolidation,
not an assertion of unchanged packed rendering or an acceptance transfer.
"""
from fractions import Fraction as F
import polyu_five_mask_source_plane_partition_fast_v1_20261014 as v2


def _positive_hit(poly, planes):
    """Closed convex intersection only; no outside subdivision is generated."""
    hit = poly
    for plane in planes:
        if not hit:
            break
        values = [plane[0] * p[0] + plane[1] * p[2] + plane[2] for p in hit]
        if min(values) >= 0:
            continue
        if max(values) < 0:
            return []
        hit = v2.oracle.old.clip(hit, plane)
    return hit


def partition(ideal, prepared, *, protected_literal=False, progress=None):
    """Exact ideal own-plane inside union/outside complement, every mask accounted.

    A zero-area hit leaves the complete original fragment including all closed
    point/line contacts. The existing caller gives zero-area hits no new height
    or positive-area coverage credit. This differs from V2's incidental cuts;
    fresh actual packing/renderer/physical checks are mandatory.
    """
    assert isinstance(prepared, v2.PreparedMasks)
    face = v2.oracle.points(ideal); n = v2.oracle.normal(face)
    if n[1] == 0:
        return dict(inside=[], outside=[face], projectedVerticalOrZeroPreservedWhole=True,
                    noAffineHeightOrCoverageCredit=True, completeOwnPlanePartition=True,
                    packedOutputEquivalenceClaimed=False, freshPackedQualificationRequired=True)
    axis = max(range(3), key=lambda k: abs(n[k]))
    required = v2.oracle.old.intrinsic_area(face, axis)
    pending, inside, decisions = [face], [], []
    first, relevant = prepared.relevant(v2.oracle.bb(face))
    for mi in first:
        before = sum((v2.oracle.old.intrinsic_area(p, axis) for p in pending), F(0))
        following = []; added = F(0)
        counts = dict(inputFragments=len(pending), strictlyDisjointClosedAABB=0,
                      exactZeroAreaHits=0, fullPositiveHits=0, partialPositiveHits=0)
        for poly in pending:
            poly_area = v2.oracle.old.intrinsic_area(poly, axis)
            assert poly_area > 0
            if v2._disjoint(v2.oracle.bb(poly), prepared.masks[mi]['bounds']):
                following.append(poly); counts['strictlyDisjointClosedAABB'] += 1
                continue
            hit = _positive_hit(poly, prepared.planes[mi])
            hit_area = v2.oracle.old.intrinsic_area(hit, axis)
            if hit_area == 0:
                following.append(poly); counts['exactZeroAreaHits'] += 1
                continue
            if hit_area == poly_area:
                # Closed containment: same entire own-plane polygon, earlier owner.
                inside.append(dict(mask=mi, polygon=poly)); added += poly_area
                counts['fullPositiveHits'] += 1
                continue
            assert 0 < hit_area < poly_area
            actual_hit, rest = v2._split_positive(poly, prepared.planes[mi], axis)
            assert actual_hit == hit and v2.oracle.old.intrinsic_area(actual_hit, axis) == hit_area
            following.extend(rest); inside.append(dict(mask=mi, polygon=actual_hit)); added += hit_area
            counts['partialPositiveHits'] += 1
        after = sum((v2.oracle.old.intrinsic_area(p, axis) for p in following), F(0))
        assert before == added + after
        decisions.append(dict(mask=mi, **counts, exactAreaBefore=before,
                              exactAssignedInsideArea=added, exactAreaAfter=after,
                              outputFragments=len(following)))
        pending = following
        if progress is not None:
            progress(dict(mask=mi, masksProcessed=len(decisions), relevantUniqueMasks=len(first),
                          pendingFragments=len(pending), assignedInsidePolygons=len(inside),
                          exactRemainingArea=after, diagnosticOnly=True))
        if not pending:
            break
    inside_area = sum((v2.oracle.old.intrinsic_area(r['polygon'], axis) for r in inside), F(0))
    outside_area = sum((v2.oracle.old.intrinsic_area(p, axis) for p in pending), F(0))
    assert inside_area + outside_area == required
    if protected_literal:
        assert inside_area == 0, 'protected literal intersects proposed restoration: unresolved'
    for poly in pending + [row['polygon'] for row in inside]:
        assert all(sum(n[k] * (p[k] - face[0][k]) for k in range(3)) == 0 for p in poly)
    return dict(inside=inside, outside=pending, exactWholeIntrinsicArea=required,
                exactInsideMaskUnionIntrinsicArea=inside_area, exactOutsideMaskUnionIntrinsicArea=outside_area,
                completeRelevantClosedAABBMasks=relevant,
                relevantUniqueFirstOccurrenceMasks=first,
                allOriginalMaskOccurrenceAliases={i:prepared.aliases[i] for i in first},
                maskDecisionAccounting=decisions,
                masksNotVisitedAfterCompleteInsideAssignment=first[len(decisions):],
                allOtherMasksStrictlyClosedAABBDisjoint=True,
                maskFirstOwnershipPreventsDuplicateArea=True,
                completeOwnPlanePartition=True, closedBoundariesRetained=True,
                noGEOSToleranceOrBuffer=True, idealContinuousSourcePlaneUnionPreserved=True,
                outsideTessellationMayDifferFromV2=True,
                packedOutputEquivalenceClaimed=False,
                freshPackedQualificationRequired=True)
