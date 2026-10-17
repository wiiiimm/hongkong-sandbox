"""Isolated exact-output acceleration; not integrated into the running producer.

Same Fraction geometry, first occurrence ownership and complete mask accounting.
No source simplification, tolerance, acceptance or production input modification.
"""
from fractions import Fraction as F
from math import gcd, lcm
import polyu_five_mask_source_plane_partition_v1_20261014 as oracle


def _disjoint(a, b):
    return a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1]


def _integer_plane(plane):
    """Positive exact scalar only; clip ratios and closed signs are unchanged."""
    denominator = lcm(*(v.denominator for v in plane))
    values = tuple(v.numerator * (denominator // v.denominator) for v in plane)
    divisor = gcd(*values)
    assert divisor > 0
    return tuple(v // divisor for v in values)


class PreparedMasks:
    def __init__(self, records):
        self.masks = oracle.masks_from_records(records)
        self.aliases = {}
        signatures = {}
        self.planes = {}
        for mi, mask in enumerate(self.masks):
            # Retain ordered triangle, bounds AND ordered plane identities.
            # Geometrically equal but differently ordered masks are NOT merged.
            key = (tuple(mask['triangle']), tuple(mask['bounds']), tuple(mask['planes']))
            first = signatures.setdefault(key, mi)
            self.aliases.setdefault(first, []).append(mi)
            if first == mi:
                self.planes[mi] = tuple(_integer_plane(p) for p in mask['planes'])
        self.first_ids = tuple(self.aliases)
        self.tree = self._build(self.first_ids) if self.first_ids else None

    def _build(self, ids):
        boxes = [self.masks[i]['bounds'] for i in ids]
        bound = (min(b[0] for b in boxes), min(b[1] for b in boxes),
                 max(b[2] for b in boxes), max(b[3] for b in boxes))
        if len(ids) <= 8:
            return bound, ids, None, None
        axis = 0 if bound[2] - bound[0] >= bound[3] - bound[1] else 1
        ordered = sorted(ids, key=lambda i: (self.masks[i]['bounds'][axis] +
                                            self.masks[i]['bounds'][axis + 2], i))
        middle = len(ordered) // 2
        return bound, None, self._build(ordered[:middle]), self._build(ordered[middle:])

    def relevant(self, bound):
        first = []
        def visit(node):
            if node is None or _disjoint(bound, node[0]):
                return
            if node[1] is not None:
                first.extend(i for i in node[1] if not _disjoint(bound, self.masks[i]['bounds']))
            else:
                visit(node[2]); visit(node[3])
        visit(self.tree)
        first.sort()  # Exact original first-owner order, never BVH traversal order.
        all_ids = sorted(i for mi in first for i in self.aliases[mi])
        return first, all_ids


def _split_positive(poly, planes, axis):
    """Same ordered positive-area outputs as oracle.split for positive polygons.

    oracle.clip returns the unchanged clean polygon for an all-positive plane.
    An all-nonpositive plane with at least one negative leaves the same whole
    outside polygon; its inside line/point has zero area and partition discards
    it. No fragment-AABB shortcut drops the oracle's incidental subdivisions.
    """
    required = oracle.old.intrinsic_area(poly, axis)
    assert required > 0
    remaining, outside = poly, []
    for plane in planes:
        values = [plane[0] * p[0] + plane[1] * p[2] + plane[2] for p in remaining]
        if min(values) >= 0:
            continue
        if max(values) <= 0:
            outside.append(remaining)
            remaining = []
            break
        part = oracle.old.clip(remaining, tuple(-v for v in plane))
        if oracle.old.intrinsic_area(part, axis):
            outside.append(part)
        remaining = oracle.old.clip(remaining, plane)
    assert required == sum((oracle.old.intrinsic_area(p, axis) for p in outside), F(0)) + oracle.old.intrinsic_area(remaining, axis)
    return remaining, outside


def partition(ideal, prepared, *, protected_literal=False):
    assert isinstance(prepared, PreparedMasks)
    face = oracle.points(ideal); n = oracle.normal(face)
    if n[1] == 0:
        return dict(inside=[], outside=[face], projectedVerticalOrZeroPreservedWhole=True,
                    noAffineHeightOrCoverageCredit=True, completeOwnPlanePartition=True)
    axis = max(range(3), key=lambda k: abs(n[k]))
    required = oracle.old.intrinsic_area(face, axis)
    pending, inside = [face], []
    first, relevant = prepared.relevant(oracle.bb(face))
    for mi in first:
        following = []
        for poly in pending:
            hit, rest = _split_positive(poly, prepared.planes[mi], axis)
            following.extend(rest)
            if oracle.old.intrinsic_area(hit, axis):
                inside.append(dict(mask=mi, polygon=hit))
        pending = following
        if not pending:
            break
    inside_area = sum((oracle.old.intrinsic_area(r['polygon'], axis) for r in inside), F(0))
    outside_area = sum((oracle.old.intrinsic_area(p, axis) for p in pending), F(0))
    assert inside_area + outside_area == required
    if protected_literal:
        assert inside_area == 0, 'protected literal intersects proposed restoration: unresolved'
    for poly in pending + [r['polygon'] for r in inside]:
        assert all(sum(n[k] * (v[k] - face[0][k]) for k in range(3)) == 0 for v in poly)
    return dict(inside=inside, outside=pending, exactWholeIntrinsicArea=required,
                exactInsideMaskUnionIntrinsicArea=inside_area, exactOutsideMaskUnionIntrinsicArea=outside_area,
                completeRelevantClosedAABBMasks=relevant, allOtherMasksStrictlyClosedAABBDisjoint=True,
                maskFirstOwnershipPreventsDuplicateArea=True, completeOwnPlanePartition=True,
                closedBoundariesRetained=True, noGEOSToleranceOrBuffer=True)
