"""Restrict rounding repairs to derived returns strictly outside the source core."""
import numpy as np
import shapely


def verify_return_scope(positions,index,lineage,changed_faces,core):
    faces=np.asarray(positions,float).reshape(-1,3)[np.asarray(index).reshape(-1,3)]
    assert len(lineage)==len(faces)and changed_faces
    rows=[]
    for i in changed_faces:
        assert lineage[i]['kind']in ['unchanged','parent-fragment','original-inset-or-return']
        polygon=shapely.Polygon(faces[i][:,[0,2]])
        distance=float(polygon.distance(core))
        assert distance>.01,'repair-face-touches-model-protected-source-core'
        rows.append(dict(face=int(i),lineageKind=lineage[i]['kind'],minimumDistanceFromCoreM=distance))
    return dict(changedFaces=rows,minimumFaceDistanceFromProtectedCoreM=min(r['minimumDistanceFromCoreM']for r in rows),allChangedFacesStrictlyOutsideSourceCore=True)
