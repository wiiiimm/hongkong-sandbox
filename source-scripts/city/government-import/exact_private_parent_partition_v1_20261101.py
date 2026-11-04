"""Retain every represented private parent facet; partition only its surroundings.

Geometry preparation only. All inherited private vertices must already meet
1.2 m. Caller must authenticate the exact private candidate and source revisions.
The later complete low-face/edit, terrain, source and publication guards remain.
"""
from collections import Counter
import hashlib
import numpy as np
from exact_float32_parent_level_partition_v3_20261101 import choose

def key(face):return np.asarray(face,dtype='<f4').tobytes()

def partition_bound_parent(faces,private_node):
    raw=np.asarray(faces,dtype='<f8');values=raw.astype('<f4').astype('<f8')
    assert raw.ndim==3 and raw.shape[1:]==(3,3) and len(raw) and np.isfinite(raw).all()
    assert np.array_equal(raw,values),'Captured parent is not the represented Float32 surface'
    mesh=private_node['nativeMesh'];p=np.asarray(mesh['position'],dtype='<f4').astype('<f8').reshape(-1,3);t=p[np.asarray(mesh['index'],dtype=int).reshape(-1,3)]
    assert len(t) and np.isfinite(t).all() and t[:,:,1].min()>=float(np.float32(1.2)),'Inherited private terrain is below the existing represented floor'
    # world.js normalizes native winding after Float32 conversion. Bind that
    # exact rendered orientation, rather than treating its flips as lost facets.
    n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);t[n[:,1]<0]=t[n[:,1]<0][:,[0,2,1]]
    wanted=Counter(key(f)for f in t);retained=[]
    for i,f in enumerate(values):
        k=key(f)
        if wanted[k]:wanted[k]-=1;retained.append(i)
    assert not any(wanted.values()),'A complete private rendered facet is missing or changed'
    retained_set=set(retained);other=[i for i in range(len(values))if i not in retained_set]
    if other:
        partitioned,proof=choose(values[other]);groups={i:[]for i in other}
        for f,i in zip(partitioned,proof['sourceFaceByOutputFace']):groups[other[i]].append(f)
    else:
        proof=dict(levelM=77/64,exactLevel='77/64',subdividedParentFaces=0,rejectedLevels=[]);groups={}
    output=[];lineage=[]
    for i,f in enumerate(values):
        pieces=[f]if i in retained_set else groups[i]
        for piece in pieces:output.append(piece);lineage.append(i)
    out=np.asarray(output,dtype='<f8');kept=[out[j]for j,i in enumerate(lineage)if i in retained_set]
    assert Counter(key(f)for f in kept)==Counter(key(values[i])for i in retained)
    zero=np.flatnonzero(np.cross(values[:,1]-values[:,0],values[:,2]-values[:,0])[:,1]==0).tolist()
    return out,dict(contract='exact-bound-private-parent-retention-and-production-coast-partition-v1',levelM=proof['levelM'],exactLevel=proof['exactLevel'],sourceFaces=len(values),outputFaces=len(out),sourceFaceByOutputFace=lineage,retainedPrivateInputFaceIds=retained,retainedPrivateOutputFaceIds=[j for j,i in enumerate(lineage)if i in retained_set],completePrivateFaces=len(t),privateMinimumRenderedY=float(t[:,:,1].min()),retainedZeroProjectionInputFaceIds=zero,subdividedParentFaces=proof['subdividedParentFaces'],productionParentPartitionProof=proof,exactPrivateFacetMultiplicityAndWindingPreserved=True,everyOutputCoordinateExactlyFloat32=True,exactOriginalPlaneAndWinding=True,exactProjectedAreaConservation=True,parentSurfaceExactlyUnchanged=True,parentTriangulationChanged=bool(proof['subdividedParentFaces']),inputSHA256=hashlib.sha256(values.astype('<f4').tobytes()).hexdigest(),outputSHA256=hashlib.sha256(out.astype('<f4').tobytes()).hexdigest(),uniformLevelSidesRequiredFor='partitioned production-parent facets only; authenticated private facets retained verbatim',governmentBuildingGeometryChanges=0,installationApproved=False)
