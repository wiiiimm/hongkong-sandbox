"""Retain exact original zero-area triangles without certifying visible support.

Nonzero triangle areas, however tiny, cannot use this classification. Original
bytes, indices and continuous ground clearance remain mandatory.
"""
import hashlib,json,numpy as np
from exact_original_shell_intersections_20261009 import rational_face,cross,sub

def verify(triangles,components,contexts,*,expected_binding,current_binding):
    tri=np.asarray(triangles,float)
    assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
    assert expected_binding==current_binding and current_binding
    assert current_binding['completeOriginalWorldTrianglesSHA256']==hashlib.sha256(tri.tobytes()).hexdigest()
    assert current_binding['originalBytesAndIndicesUnchanged'] is True
    assert current_binding['currentDrawnGroundSHA256'] and current_binding['completeOriginalSourceBindingSHA256']
    assert current_binding['continuousNonrenderingContextsSHA256']==hashlib.sha256(json.dumps(contexts,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    faces=[f for c in components for f in c['globalOriginalFaces']]
    assert len(set(faces))==len(faces) and all(type(f)is int and 0<=f<len(tri) for f in faces)
    assert set(map(int,contexts))==set(faces),'Omitted original nonrendering context'
    for f in faces:
        t=rational_face(tri[f]);assert not any(cross(sub(t[1],t[0]),sub(t[2],t[0]))),'Renderable original triangle cannot be classified nonrendering'
        c=contexts.get(str(f),contexts.get(f));assert c['sourceFace']==f
        assert c['sourceDegenerate'] is True and c['groundProjectionCovered'] is True
        assert c['minimum'] and np.isfinite(c['minimum']['minimumGapM']) and c['minimum']['minimumGapM']>=-.5,'Original nonrendering primitive still has strict continuous clearance failure'
    return dict(contract='complete-original-exact-zero-area-nonrendering-component-accounting-v1',verifiedNonrenderingAccounting=True,originalNonrenderingComponentCount=len(components),originalNonrenderingFaces=sorted(faces),sourceGeometryChanges=0,originalFacesOmitted=0,renderableSupportCreditGranted=False,installationApproved=False,qualification='Every classified original triangle has exactly zero rational cross-product area; the unchanged triangle rasteriser cannot draw a surface at any viewport. Original bytes/indices remain, each line/point has complete current continuous ground coverage and unchanged ordinary clearance. No small nonzero surface, visible floating component, support anchor or publication is credited.')
