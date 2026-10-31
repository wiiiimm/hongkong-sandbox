"""Identify already approved sub-2mm input holes without claiming full coverage.

Only private derived-terrain preparation uses this diagnostic. It neither fills
holes nor approves a model/output. Existing numerical area/distance bounds apply
independently to the raw input and actual production Float32 representation.
"""
import copy,hashlib
import numpy as np
import shapely
from float32_coverage import approve_roundoff,geometry_sha
from native_patch_resolution import projected_context

def check(patch,outer,rendered,expected_sha):
    assert rendered['sourcePatchSHA256']==expected_sha
    assert rendered['identicalRenderedPositionBytes']is True and rendered['identicalRenderedIndices']is True
    original_sha=geometry_sha(patch);declared=patch['nativeMesh']['source'].get('numericalCoverageGap');assert declared and declared['policy']=='parent-grid-fallback'
    g=patch['meta']['georef'];bounds=(g['bE']-834500,816500-g['bN'],g['bE']-834500+(patch['w']-1)*g['aE'],816500-g['bN']-(patch['h']-1)*g['aN'])
    extent=shapely.box(*bounds);assert outer.difference(extent).is_empty,'Return domain extends beyond the native input extent'
    raw=copy.deepcopy(patch);raw_proof=approve_roundoff(raw,bounds)
    assert declared==raw_proof,'Original numerical gap declaration is stale or changed'
    normalized=copy.deepcopy(patch);positions=np.asarray(patch['nativeMesh']['position'],dtype='<f4')
    assert hashlib.sha256(positions.tobytes()).hexdigest()==rendered['renderedPositionsSHA256'],'Production Float32 input changed'
    normalized['nativeMesh']['position']=positions.astype('<f8').tolist()
    # The raw declaration is not transferred to changed Float32 coordinates.
    rendered_proof=approve_roundoff(normalized,bounds)
    _,polygons,whole_missing,_=projected_context(normalized,bounds);domain=shapely.union_all(polygons)
    direct_missing=outer.difference(domain)
    # outer is wholly inside extent, so A\U = A intersection (extent\U).
    # Use that exact set identity instead of subtracting two independently
    # rounded GEOS overlay results. No coordinate snap or area waiver is used.
    missing=outer.intersection(whole_missing);assert not missing.is_empty
    assert geometry_sha(patch)==original_sha and patch['nativeMesh']['source']['numericalCoverageGap']==declared
    return dict(legacyStrictCoverageSatisfied=False,missingSetEmpty=False,missingAreaM2=float(missing.area),missingWKT=missing.wkt,directOverlayMissingWKT=direct_missing.wkt,setIdentityProof='outer subset extent; outer minus rendered union equals outer intersection (extent minus rendered union)',rawInputGeometrySHA256=original_sha,rawInputCoverageProof=raw_proof,renderedInputCoverageProof=rendered_proof,actualRenderedPositionsSHA256=rendered['renderedPositionsSHA256'],wholeReturnInsideNativeExtent=True,noNewInputHoleAllowance=True,sourceGeometryChanges=0,qualification='Exact pre-existing input holes only. Raw declaration revalidated and actual Float32 input independently passes unchanged0.25m2/2mm numerical policy. Original input is unmodified; raw missing-set failure retained. Output coverage/native boundary/source foundations/neighbours/runtime/visual/publication remain separate.')
