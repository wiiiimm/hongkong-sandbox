"""Exact rational grade-segment versus complete terrain-facet column comparison.

Keeps non-dyadic intersection coordinates exact and includes vertical/collapsed
terrain projections. Diagnostic only, no source edits or acceptance credit.
"""
from fractions import Fraction as F
from itertools import combinations
from exact_original_triangle_pair_column_gap_20261010 import rref


def verify(start, end, ground):
    segment = [tuple(F(v) for v in point) for point in [start, end]]
    triangle = [tuple(F(v) for v in point) for point in ground]
    assert all(len(p) == 3 for p in segment + triangle) and len(triangle) == 3
    equations = [[F(1), F(1), F(0), F(0), F(0), F(1)], [F(0), F(0), F(1), F(1), F(1), F(1)]]
    equations.extend([[segment[j][axis] for j in range(2)] + [-triangle[j][axis] for j in range(3)] + [F(0)] for axis in [0, 2]])
    independent, _ = rref(equations)
    records = []
    if independent is not None:
        rank = len(independent)
        for columns in combinations(range(5), rank):
            reduced, pivots = rref([[row[j] for j in columns] + [row[-1]] for row in independent])
            if reduced is None or len(pivots) != rank:
                continue
            weights = [F(0)] * 5
            for k, row in enumerate(reduced):
                weights[columns[pivots[k]]] = row[-1]
            if min(weights) < 0:
                continue
            assert all(sum(c * x for c, x in zip(row[:-1], weights)) == row[-1] for row in equations)
            a = tuple(sum(weights[j] * segment[j][axis] for j in range(2)) for axis in range(3))
            b = tuple(sum(weights[j + 2] * triangle[j][axis] for j in range(3)) for axis in range(3))
            assert a[0] == b[0] and a[2] == b[2]
            records.append(dict(exactWeights=[str(x) for x in weights], exactSegmentPoint=[str(x) for x in a], exactGroundPoint=[str(x) for x in b], exactGapM=str(a[1] - b[1])))
    minimum = min((F(r['exactGapM']) for r in records), default=None)
    return dict(exactClosedProjectionsMeet=bool(records), exactMinimumColumnGapM=str(minimum) if minimum is not None else None, segmentOnOrAboveWholeGroundFacet=minimum is None or minimum >= 0, exactBasicFeasibleVertices=records, sourceCoordinatesRounded=False, groundFacetOmitted=False, installationApproved=False)
