"""Closed finite-ground AABB pruning, retaining the complete input binding.

Only facets strictly disjoint from an outward enclosing projected AABB can be
excluded. Touching, point and line projections remain. The nested unchanged
kernel certifies its explicitly identified subset, never a relabelled full
ground input. No role, root, structural or installation credit.
"""
from fractions import Fraction as F
import hashlib, math
import numpy as np
from exact_original_rational_interface_segment_clearance_20261011 import rational, verify
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces

def sha(a): return hashlib.sha256(a.tobytes()).hexdigest()

def enclosing_float(value, lower):
    value=F(value); result=float(value)
    assert math.isfinite(result), 'Finite representable projected coordinates required'
    if lower and F(result)>value: result=math.nextafter(result,-math.inf)
    if not lower and F(result)<value: result=math.nextafter(result,math.inf)
    assert math.isfinite(result)
    assert (F(result)<=value) if lower else (F(result)>=value)
    return result

class CompleteGround:
    def __init__(self, ground):
        self.ground=np.array(ground,dtype=np.float64,copy=True,order='C')
        assert self.ground.ndim==3 and self.ground.shape[1:]==(3,3)
        assert len(self.ground)>0 and np.isfinite(self.ground).all()
        self.lower=self.ground[:,:,[0,2]].min(axis=1)
        self.upper=self.ground[:,:,[0,2]].max(axis=1)
        self.ground_sha=sha(self.ground)
        self.bounds_sha=sha(np.concatenate([self.lower,self.upper],axis=1))
        for a in [self.ground,self.lower,self.upper]: a.flags.writeable=False

    def verify_binding(self):
        assert sha(self.ground)==self.ground_sha
        assert np.array_equal(self.lower,self.ground[:,:,[0,2]].min(axis=1))
        assert np.array_equal(self.upper,self.ground[:,:,[0,2]].max(axis=1))
        assert sha(np.concatenate([self.lower,self.upper],axis=1))==self.bounds_sha

    def select(self, points):
        assert len(points) and all(len(p)==3 for p in points)
        exact=[tuple(rational(x) for x in p) for p in points]
        low=[min(p[a] for p in exact) for a in [0,2]]
        high=[max(p[a] for p in exact) for a in [0,2]]
        lo=np.array([enclosing_float(x,True) for x in low])
        hi=np.array([enclosing_float(x,False) for x in high])
        # Binary64 comparisons on finite extrema are exact ordering, with an
        # outward enclosing query. Every strict comparison proves separation.
        disjoint=np.any((self.upper<lo)|(self.lower>hi),axis=1)
        ids=np.flatnonzero(~disjoint)
        assert len(ids)+int(disjoint.sum())==len(self.ground)
        assert np.all(np.any((self.upper[disjoint]<lo)|(self.lower[disjoint]>hi),axis=1))
        proof=dict(contract='complete-closed-ground-projected-aabb-subset-v1',
            completeGroundSHA256=self.ground_sha,completeGroundFacetCount=len(self.ground),
            completeProjectedBoundsSHA256=self.bounds_sha,
            exactProjectedLower=list(map(str,low)),exactProjectedUpper=list(map(str,high)),
            outwardEnclosingFloatLower=lo.tolist(),outwardEnclosingFloatUpper=hi.tolist(),
            selectedOriginalGroundFaces=ids.tolist(),selectedFacetCount=len(ids),
            strictlyDisjointNoncandidateCount=int(disjoint.sum()),
            everyNoncandidateStrictlyDisjoint=True,touchingAndCollapsedProjectionsRetained=True,
            sourceOnly=True,rootOrStructuralCredit=False)
        return ids,proof

    def segment(self,endpoints):
        assert len(endpoints)==2 and all(len(p)==3 for p in endpoints)
        exact=[tuple(rational(x) for x in p) for p in endpoints]
        assert exact[0]!=exact[1]
        ids,selection=self.select(endpoints)
        nested=verify(endpoints,self.ground[ids]) if len(ids) else None
        return dict(contract='complete-ground-closed-aabb-rational-interface-diagnostic-v1',
            selection=selection,selectedGroundKernelProof=nested,
            originalGroundFaceBySelectedKernelFace=ids.tolist(),
            closedWholeSegmentProjectionCovered=bool(nested and nested['closedWholeSegmentProjectionCovered']),
            strictlyExposedWholePositiveInterface=bool(nested and nested['strictlyExposedWholePositiveInterface']),
            exactMinimumGapM=nested['exactMinimumGapM'] if nested else None,
            noFullInputRelabelling=True,rootOrStructuralCredit=False)

    def grade(self,triangles,face_id):
        triangles=np.asarray(triangles,float)
        assert triangles.ndim==3 and triangles.shape[1:]==(3,3) and np.isfinite(triangles).all()
        assert type(face_id) is int and 0<=face_id<len(triangles)
        points=[[str(F(float(v))) for v in p] for p in triangles[face_id]]
        ids,selection=self.select(points)
        nested=exact_upper_ground_interfaces(triangles,[face_id],self.ground[ids]) if len(ids) else []
        # Keep the nested kernel's own selected-input IDs untouched. The outer
        # records are explicit copies remapped into the complete ground.
        mapped=[]
        for row in nested:
            intervals=[]
            for interval in row['exactActiveUpperGroundIntervals']:
                intervals.append(dict(interval,candidateGroundFacets=[int(ids[i]) for i in interval['candidateGroundFacets']]))
            mapped.append(dict(row,originalGroundFace=int(ids[row['originalGroundFace']]),exactActiveUpperGroundIntervals=intervals))
        return dict(contract='complete-ground-closed-aabb-upper-interface-diagnostic-v1',
            selection=selection,selectedGroundKernelWitnesses=nested,
            originalGroundFaceBySelectedKernelFace=ids.tolist(),exactUpperGroundIntervals=mapped,
            noFullInputRelabelling=True,rootOrStructuralCredit=False)
