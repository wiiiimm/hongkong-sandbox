"""Consolidate only changed terrain fragments inside each original parent face.

Preserve production Float32 finite surfaces, flat normals and vertex colours.
Untouched parent faces remain literal. Government building meshes are not inputs.
"""
from collections import defaultdict
from copy import deepcopy
import numpy as np
from constant_colour_terrain_consolidation_v1 import consolidate_patch

def recover(output,lineage,parent,context):
    faces=np.asarray(output,dtype='<f8');parent=np.asarray(parent,dtype='<f8')
    assert len(faces)==len(lineage)and np.isfinite(faces).all()
    groups=defaultdict(list);unchanged={}
    for i,row in enumerate(lineage):
        p=row['parentFace'];assert type(p)is int and 0<=p<len(parent)
        if row['kind']=='unchanged':
            assert p not in unchanged and np.array_equal(faces[i],parent[p]);unchanged[p]=i
        else:
            assert row['kind']in ['parent-fragment','ramp-plane-core','ramp-derived-return'];groups[(p,row['kind'])].append(i)
    assert not set(unchanged)&{p for p,_ in groups}
    kept=[faces[i]for p,i in sorted(unchanged.items())];rows=[deepcopy(lineage[i])for p,i in sorted(unchanged.items())];certificates=[]
    for (p,kind),ids in sorted(groups.items()):
        patch=deepcopy(context);patch['nativeMesh']['position']=faces[ids].reshape(-1).tolist();patch['nativeMesh']['index']=list(range(len(ids)*3));value,certificate=consolidate_patch(patch)
        assert certificate['allOriginalFacesAccounted']and certificate['sourceVerticesOnly']and certificate['mixedColourFacesRetainedUnchanged']and certificate['flatNormalsAndFinitePlaneSurfacesPreserved']
        # All changed land fragments retain the existing minimum, independent of
        # their lineage kind. No low pre-existing face is changed by this helper.
        assert np.isfinite(value).all()and value[:,:,1].min()>=1.2
        start=len(kept);kept.extend(value);fields=sorted({lineage[i]['fieldFace']for i in ids if 'fieldFace'in lineage[i]})
        rows.extend(dict(parentFace=p,kind=kind,sourceFieldFaces=fields)for _ in value)
        certificates.append(dict(parentFace=p,kind=kind,inputFaceIndices=ids,outputFaceRange=[start,len(kept)],certificate=certificate))
    result=np.asarray(kept,dtype='<f8');assert len(result)<=len(faces)and len(result)==len(rows)
    assert all(np.array_equal(result[i],parent[p])for i,p in enumerate(sorted(unchanged)))
    return result,rows,dict(inputFaces=len(faces),outputFaces=len(result),savedFaces=len(faces)-len(result),unchangedParentFaces=len(unchanged),unchangedParentFaceIds=sorted(unchanged),allUntouchedParentFacesLiteral=True,noConsolidationAcrossParentFaces=True,productionFloat32SurfacesNormalsAndColoursPreserved=True,buildingGeometryInputs=False,groups=certificates)
