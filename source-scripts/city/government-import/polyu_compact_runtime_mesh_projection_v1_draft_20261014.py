"""UNEXECUTED byte-exact mesh-only runtime projection; no geometry changes."""
import hashlib,struct
import numpy as np
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
TAG=b'polyu-native-mesh-f64-le-u32-le-v1\0'

def mesh_binding(mesh):
    assert set(mesh)=={'position','index'}
    assert all(type(v)in(int,float)for v in mesh['position'])and all(type(v)is int for v in mesh['index'])
    p=np.asarray(mesh['position'],dtype='<f8');ix=np.asarray(mesh['index'],dtype='<i8')
    assert p.ndim==ix.ndim==1 and len(p)%3==len(ix)%3==0 and len(p)>0 and len(ix)>0 and np.isfinite(p).all()
    assert ix.min()>=0 and ix.max()<len(p)//3 and ix.max()<=2**32-1
    unsigned=ix.astype('<u4');h=hashlib.sha256(TAG+struct.pack('<QQ',len(p),len(ix)));h.update(p.tobytes());h.update(unsigned.tobytes())
    raw=p.reshape(-1,3)[ix.reshape(-1,3)]
    return dict(completePositionVertices=len(p)//3,completeIndexedFaces=len(ix)//3,
        positionBinary64LE_SHA256=hashlib.sha256(p.tobytes()).hexdigest(),indexUint32LE_SHA256=hashlib.sha256(unsigned.tobytes()).hexdigest(),
        completeMeshTupleSHA256=h.hexdigest(),completeIndexedRawBinary64LE_SHA256=hashlib.sha256(raw.tobytes()).hexdigest(),
        tupleEncoding='polyu-native-mesh-f64-le-u32-le-v1',unusedPositionsIncluded=True,signedZeroBitsIncluded=True)

def project(mesh,source_ref,expected_binding,preservation):
    distinct_refs([source_ref]);binding=mesh_binding(mesh);assert binding==expected_binding
    assert set(preservation)=={'unchangedPriorFacets','unchangedOldMappings','unchangedPrefixFacets','retainedPriorPositionVertices'}
    assert all(type(v)is int and v>=0 for v in preservation.values())
    assert preservation['unchangedPriorFacets']<=binding['completeIndexedFaces']and preservation['retainedPriorPositionVertices']<=binding['completePositionVertices']
    return dict(schema='compact-polyu-parent-cell-runtime-mesh-v1',sourceNominationRef=dict(source_ref),meshBinding=binding,
        preservationCounts=dict(preservation),newNativeMesh=dict(position=list(mesh['position']),index=list(mesh['index'])),
        physicalAccepted=False,installationApproved=False,fullProvenanceValidatedInPythonNotRepeatedInNode=True)

def verify(projection,source_ref,expected_binding,preservation):
    assert projection['schema']=='compact-polyu-parent-cell-runtime-mesh-v1'and projection['sourceNominationRef']==source_ref
    assert not projection['physicalAccepted']and not projection['installationApproved']
    assert projection['meshBinding']==expected_binding and projection['preservationCounts']==preservation
    assert mesh_binding(projection['newNativeMesh'])==expected_binding
    return projection
