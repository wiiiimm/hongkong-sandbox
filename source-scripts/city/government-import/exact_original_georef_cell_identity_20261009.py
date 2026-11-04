"""Exact whole-cell coverage fallback; all other identity reasons stay unchanged."""
from copy import deepcopy
import hashlib
import numpy as np
from exact_original_projection_coverage_20261009 import exact_coverage

REASON='original-source-does-not-cover-whole-georef-cell'
POLICY='original-routed-georef-cell-exact-finite-facet-coverage-v1'

def apply_exact_cell(proof,triangles,*,expected_binding,current_binding):
    assert expected_binding==current_binding
    tri=np.asarray(triangles,float)
    assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
    sha=hashlib.sha256(tri.astype('<f8').tobytes()).hexdigest()
    assert sha==proof['worldTrianglesSHA256']==current_binding['decodedWorldTrianglesSHA256']
    assert proof['uid']==current_binding['uid'] and proof['sourceSHA256']==current_binding['sourceSHA256']
    cell=proof['geographicCell'];assert cell['precisionMetres']==1
    bounds=np.asarray(cell['worldXZBounds'],float);assert bounds.shape==(4,) and np.isfinite(bounds).all()
    x0,z0,x1,z1=bounds;assert x1-x0==z1-z0==1 and np.all(bounds==np.floor(bounds))
    faces=np.asarray([[[x0,0,z0],[x1,0,z0],[x1,0,z1]],[[x0,0,z0],[x1,0,z1],[x0,0,z1]]],float)
    halves=[exact_coverage(f,tri) for f in faces]
    covered=all(p['exactProjectionCovered'] for p in halves)
    out=deepcopy(proof);reasons=list(out['reasons'])
    replaced=[]
    if covered and cell['targetCoversWholeCell'] and REASON in reasons:
        reasons.remove(REASON);replaced=[REASON]
    passed=not reasons
    out.update(policy=POLICY,underlyingIdentityPolicy=proof['policy'],rawFloatingIdentity=deepcopy(proof),
        exactWholeCellCoverage={'wholeOriginalFacesAccounted':len(tri),'halves':halves,'covered':covered,
                                'rawProjectionCoversWholeCell':cell['originalProjectionCoversWholeCell'],
                                'rawNumericalCoverage':deepcopy(cell['projectionNumericalCoverage'])},
        replacedFloatingCoverageReasons=replaced,reasons=sorted(set(reasons)),passed=passed,
        proof={k:passed for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},
        installationApproved=False,modelGeometryChanges=0,
        qualification='Identity only. Exact finite closed original projected facets cover both halves of the unchanged complete one-metre GeoRef cell. No buffers, area tolerances, new source faces or target changes. Original floating failure remains; every other original/current unique source, root, CSUID/type, target-cell, extent, coverage and foreign-form reason remains. Physical, support, terrain, foundation, runtime and browser gates are independent.')
    return out

def verify_files(row,context,local):
    from run import ROOT,digest
    from routed_original_cell_identity import verify_files as routed_verify_files
    from exact_packed_world_geometry_20261009 import decode_original_world_triangles
    raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
    current=routed_verify_files(row,context,local)
    tri=decode_original_world_triangles(raw)
    assert len(tri)==row['triangles']==row['native']['model']['triangles']
    binding={'uid':row['uid'],'sourceSHA256':digest(raw),'decodedWorldTrianglesSHA256':digest(tri.astype('<f8').tobytes())}
    return apply_exact_cell(current,tri,expected_binding=binding,current_binding=binding)
