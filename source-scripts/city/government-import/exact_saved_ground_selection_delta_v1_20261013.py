"""Future-only continuation of authenticated complete closed-AABB selections.

No production caller imports this module. Authenticate the prior receipt/chunk,
actor/world/source-face bytes and complete selection before calling. A digest
supplied by the selection's producer cannot establish completeness by itself.
"""
from collections import defaultdict, deque
import hashlib
import json
import numpy as np
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround, enclosing_float, sha
from exact_original_rational_interface_segment_clearance_20261011 import rational


def selection_sha(selection):
    return hashlib.sha256(json.dumps(selection, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _query(points):
    assert len(points) and all(len(p) == 3 for p in points)
    exact = [tuple(rational(x) for x in p) for p in points]
    low = [min(p[a] for p in exact) for a in [0, 2]]
    high = [max(p[a] for p in exact) for a in [0, 2]]
    lo = np.array([enclosing_float(x, True) for x in low])
    hi = np.array([enclosing_float(x, False) for x in high])
    return low, high, lo, hi


def _binding(ground, ids, query):
    low, high, lo, hi = query
    return dict(contract='complete-closed-ground-projected-aabb-subset-v1',
        completeGroundSHA256=ground.ground_sha, completeGroundFacetCount=len(ground.ground),
        completeProjectedBoundsSHA256=ground.bounds_sha,
        exactProjectedLower=list(map(str, low)), exactProjectedUpper=list(map(str, high)),
        outwardEnclosingFloatLower=lo.tolist(), outwardEnclosingFloatUpper=hi.tolist(),
        selectedOriginalGroundFaces=ids.tolist(), selectedFacetCount=len(ids),
        strictlyDisjointNoncandidateCount=len(ground.ground)-len(ids),
        everyNoncandidateStrictlyDisjoint=True, touchingAndCollapsedProjectionsRetained=True,
        sourceOnly=True, rootOrStructuralCredit=False)


class SavedGroundSelectionDelta:
    """One full-array byte bijection; per-query work depends on delta + selection.

    Keys are ordered binary64 XYZ triplets, including height, vertex order and
    signed zero. Duplicate occurrences match one-to-one. CompleteGround copies
    and freezes both whole inputs. Run verify_binding at transaction boundaries.
    """
    def __init__(self, old_ground, new_ground):
        self.old = CompleteGround(old_ground)
        self.new = CompleteGround(new_ground)
        queues = defaultdict(deque)
        for j, face in enumerate(self.new.ground):
            queues[face.tobytes()].append(j)
        mapping = np.full(len(self.old.ground), -1, dtype='<i8')
        for i, face in enumerate(self.old.ground):
            q = queues[face.tobytes()]
            if q:
                mapping[i] = q.popleft()
        self.old_to_new = mapping
        self.removed = np.flatnonzero(mapping < 0)
        self.added = np.array(sorted(j for q in queues.values() for j in q), dtype='<i8')
        self._check_partition()
        self.bijection_sha = sha(mapping)
        self.removed_sha = sha(self.removed)
        self.added_sha = sha(self.added)
        self.unchanged_count = int((mapping >= 0).sum())
        for a in [self.old_to_new, self.removed, self.added]:
            a.flags.writeable = False

    def _check_partition(self):
        m = self.old_to_new
        assert m.shape == (len(self.old.ground),) and (m >= -1).all()
        kept = np.flatnonzero(m >= 0)
        matched = m[kept]
        assert (matched < len(self.new.ground)).all() and len(set(matched.tolist())) == len(matched)
        assert self.old.ground[kept].tobytes() == self.new.ground[matched].tobytes()
        assert np.array_equal(self.removed, np.flatnonzero(m < 0))
        assert np.array_equal(self.added, np.setdiff1d(np.arange(len(self.new.ground)), matched))
        assert not {f.tobytes() for f in self.old.ground[self.removed]} & {f.tobytes() for f in self.new.ground[self.added]}

    def verify_binding(self):
        """Full O(G) audit once per transaction boundary, never per query."""
        self.old.verify_binding()
        self.new.verify_binding()
        self._check_partition()
        assert sha(self.old_to_new) == self.bijection_sha
        assert sha(self.removed) == self.removed_sha and sha(self.added) == self.added_sha
        assert self.unchanged_count == int((self.old_to_new >= 0).sum())

    def select(self, points, saved_selection, *, authenticated_selection_sha,
               authenticated_selected_ground_sha):
        """Return precisely the oracle's sorted IDs, binding, plus continuation.

        Hashes must originate in verified complete prior evidence and identical
        actor/world/source-face bytes. No full old selector is replayed. Exact
        clipping must not tighten this conservative outward-AABB contract.
        """
        assert selection_sha(saved_selection) == authenticated_selection_sha
        query = _query(points)
        saved_ids = saved_selection['selectedOriginalGroundFaces']
        assert all(type(i) is int and 0 <= i < len(self.old.ground) for i in saved_ids)
        assert saved_ids == sorted(set(saved_ids))
        old_ids = np.array(saved_ids, dtype='<i8')
        assert saved_selection == _binding(self.old, old_ids, query)
        assert sha(self.old.ground[old_ids]) == authenticated_selected_ground_sha
        mapped = self.old_to_new[old_ids]
        retained = mapped[mapped >= 0]
        _, _, lo, hi = query
        disjoint = np.any((self.new.upper[self.added] < lo) |
                          (self.new.lower[self.added] > hi), axis=1)
        added_selected = self.added[~disjoint]
        new_ids = np.sort(np.concatenate([retained, added_selected]))
        assert len(set(new_ids.tolist())) == len(new_ids)
        binding = _binding(self.new, new_ids, query)
        same = bool((mapped >= 0).all() and not len(added_selected))
        if same:
            assert self.old.ground[old_ids].tobytes() == self.new.ground[mapped].tobytes()
        continuation = dict(contract='authenticated-complete-ground-selection-delta-v1',
            oldSelectionVerbatim=saved_selection, oldSelectionSHA256=authenticated_selection_sha,
            oldSelectedGroundSHA256=authenticated_selected_ground_sha,
            oldCompleteGroundSHA256=self.old.ground_sha, newCompleteGroundSHA256=self.new.ground_sha,
            globalOccurrenceBijectionSHA256=self.bijection_sha,
            completeOldFacetCount=len(self.old.ground), completeNewFacetCount=len(self.new.ground),
            completeUnchangedOccurrences=self.unchanged_count,
            completeRemovedOldFaces=self.removed.tolist(), completeAddedNewFaces=self.added.tolist(),
            removedSelectedOldFaces=old_ids[mapped < 0].tolist(),
            addedSelectedNewFaces=added_selected.tolist(), newFaceByOldSelectedFace=mapped.tolist(),
            completeSelectedTripletMultisetExactlyEqual=same,
            addedFacetAABBTests=len(self.added), unchangedFacetAABBTests=0,
            completePriorSelectionMustBeAuthenticated=True,
            noOldKernelHashOrNegativeContextRelabelling=True,
            noFiniteKernelOrGeometryOrAcceptanceChange=True)
        return new_ids, binding, continuation
