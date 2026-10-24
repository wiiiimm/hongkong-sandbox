"""Full original native geometry protection, no bounding rectangle proxy credit.

Every original face projection, including lines and points, must be covered by
the exact protected existing-parent region and strictly disjoint from every new
source face. Foundation, all native actors and runtime remain separate checks.
"""
import hashlib
import numpy as np
import shapely
from shapely.geometry import box

def verify(native_triangles, source_triangles, protected, *, expected_binding, current_binding):
    native=np.asarray(native_triangles,float);source=np.asarray(source_triangles,float)
    for t in [native,source]:assert t.ndim==3 and t.shape[1:]==(3,3) and len(t) and np.isfinite(t).all()
    assert expected_binding==current_binding and current_binding
    assert current_binding['nativeDecodedWorldTrianglesSHA256']==hashlib.sha256(native.tobytes()).hexdigest()
    assert current_binding['sourceDecodedWorldTrianglesSHA256']==hashlib.sha256(source.tobytes()).hexdigest()
    for k in ['nativeSourceSHA256','nativeCatalogueSHA256','sourceSHA256','currentManifestSHA256','currentNativeParentSHA256']:
        assert current_binding[k], 'Missing original/current protection binding'
    assert protected.is_valid and not protected.is_empty
    # Polygon-only unions would silently omit original vertical and collapsed faces.
    npj=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in native])
    spj=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in source])
    assert npj.disjoint(spj),'Original native/source geometry projections touch'
    assert protected.covers(npj),'Protected existing terrain misses original native face projection'
    low=native.min(axis=(0,1));high=native.max(axis=(0,1));bounds=box(low[0],low[2],high[0],high[2])
    return {'contract':'complete-original-native-projection-parent-protection-v1',
            'sourceAndCurrentBindings':current_binding,'completeOriginalNativeFaces':len(native),
            'completeNewOriginalSourceFaces':len(source),'allOriginalFacesIncludingVerticalCollapsedAccounted':True,
            'originalNativeProjectionStrictlyDisjointFromNewSource':True,
            'nativeProjectionDistanceM':float(npj.distance(spj)),
            'completeOriginalNativeProjectionCoveredByProtectedParent':True,
            'protectedProjectionWKB_SHA256':hashlib.sha256(protected.wkb).hexdigest(),
            'nativeProjectionWKB_SHA256':hashlib.sha256(npj.wkb).hexdigest(),
            'sourceProjectionWKB_SHA256':hashlib.sha256(spj.wkb).hexdigest(),
            'rawWholeBoundsProjectionOverlapM2':float(bounds.intersection(spj).area),
            'sourceGeometryChanges':0,'installationApproved':False,
            'qualification':'Exact full original mesh projection protection only; raw bounding-box overlap is retained. Complete current native/source foundation, neighbours, sampler/runtime/browser and publication remain mandatory.'}
