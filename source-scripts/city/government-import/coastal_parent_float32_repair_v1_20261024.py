"""Conservative Float32 height rounding for derived parent-return vertices only."""
from fractions import Fraction as F
import numpy as np
from exact_below_floor_triangle_gap_v1_20261023 import verify
from exact_original_projection_coverage_v2_20261010 import exact_coverage

MAXIMUM_LIFT_M = .001


def ceil_float32(value, increment):
    old=float(np.float32(value))
    assert np.isfinite(old) and increment>=0
    exact=F(old)+increment
    rounded=np.float32(float(exact))
    while F(float(rounded))<exact:
        rounded=np.nextafter(rounded,np.float32(np.inf),dtype=np.float32)
    new=float(rounded)
    assert np.isfinite(new) and new>=old
    assert new-old<=MAXIMUM_LIFT_M,'coastal-repair-exceeds-numerical-budget'
    return new


def audit(positions,index,parent):
    vertices=np.asarray(positions,dtype=np.float32).astype(float).reshape(-1,3)
    faces=vertices[np.asarray(index).reshape(-1,3)]
    ground=np.asarray(parent,float);xz=ground[:,:,[0,2]];rows=[]
    for i in np.flatnonzero(faces[:,:,1].min(1)<1.2):
        face=faces[i];lo,hi=face[:,[0,2]].min(0),face[:,[0,2]].max(0)
        ids=np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1))
        pairs=[dict(parentFace=int(j),**verify(face,ground[j]))for j in ids]
        gaps=[F(r['exactMinimumFiniteColumnGapM'])for r in pairs if r['exactClosedHorizontalProjectionsMeet']]
        assert gaps,'uncovered-coastal-face'
        coverage=exact_coverage(face,ground);minimum=min(gaps)
        rows.append(dict(candidateFace=int(i),exactMinimumGapM=str(minimum),projectionCovered=coverage['exactProjectionCovered'],passed=minimum>=0 and coverage['exactProjectionCovered'],coverage=coverage,pairs=pairs))
    return rows


def repaired_positions(positions,index,audit_rows):
    original=np.asarray(positions,float).reshape(-1,3)
    rendered=original.astype(np.float32).astype(float)
    faces=np.asarray(index).reshape(-1,3);targets={}
    for row in audit_rows:
        assert row['projectionCovered'],'height-repair-cannot-repair-missing-coverage'
        gap=F(row['exactMinimumGapM'])
        if gap>=0:continue
        for vertex in rendered[faces[row['candidateFace']]]:
            key=tuple(vertex);targets[key]=max(targets.get(key,vertex[1]),ceil_float32(vertex[1],-gap))
    assert targets,'no-coastal-regression-to-repair'
    output=original.copy();changed=[]
    # All occurrences of a shared rendered vertex receive exactly the same height.
    for i,vertex in enumerate(rendered):
        value=targets.get(tuple(vertex))
        if value is not None:
            assert value>=original[i,1]
            output[i,1]=value;changed.append(i)
    assert np.array_equal(output[:,[0,2]],original[:,[0,2]])
    assert np.all(output[:,1]>=original[:,1])
    lifts=output[:,1]-original[:,1]
    assert float(lifts.max())<=MAXIMUM_LIFT_M
    return output,dict(changedVertexIndices=changed,changedRenderedVertexKeys=len(targets),maximumLiftM=float(lifts.max()),minimumLiftM=float(lifts[changed].min()),noHorizontalCoordinateChanges=True,allHeightChangesNonnegative=True)
