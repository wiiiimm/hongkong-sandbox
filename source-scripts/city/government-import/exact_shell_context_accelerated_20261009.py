"""Versioned exact intersection proof with conservative original AABB exclusion."""
from itertools import combinations
import numpy as np
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,segment_has,cross,sub


def shell_self_intersections(triangles,*,maximum_faces=1000):
    assert 1<=len(triangles)<=maximum_faces<=1000
    tri=np.asarray(triangles,dtype=float)
    faces=[rational_face(f) for f in triangles]
    assert all(any(cross(sub(f[1],f[0]),sub(f[2],f[0]))) for f in faces)
    low,high=tri.min(axis=1),tri.max(axis=1)
    failures=[];pairs=exact=legal_contacts=0
    for i,j in combinations(range(len(faces)),2):
        pairs+=1
        if np.any(low[i]>high[j]) or np.any(low[j]>high[i]):continue
        exact+=1;a,b=faces[i],faces[j];points=intersection_points(a,b)
        if not points:continue
        shared=sorted(set(a)&set(b))
        legal=(len(shared)==1 and points==set(shared)) or (
            len(shared)==2 and all(segment_has(shared[0],shared[1],p) for p in points))
        if legal:legal_contacts+=1
        else:failures.append({'faces':[i,j],'sharedSourceVertices':len(shared),
                             'intersectionPoints':[[str(v) for v in p] for p in sorted(points)]})
    return {'sourceFaces':len(faces),'trianglePairsChecked':pairs,'exactIntersectionPairs':exact,
            'disjointOriginalAABBExcludedPairs':pairs-exact,'legalSharedContacts':legal_contacts,
            'invalidIntersections':failures,'selfIntersectionFree':not failures,
            'coordinateArithmetic':'exact-rational-of-original-decoded-binary-coordinates',
            'geometryChanges':0,'toleranceWaivers':0,'placementAccepted':False}
