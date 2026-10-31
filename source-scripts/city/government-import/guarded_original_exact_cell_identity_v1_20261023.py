"""Keep unavailable/unsupported source cells as bound identity holds, never approvals."""
from copy import deepcopy
import hashlib
import numpy as np
from exact_original_georef_cell_identity_20261009 import apply_exact_cell as exact_cell

REASON='exact-source-georef-cell-unavailable-or-unsupported'

def apply_exact_cell(proof,triangles,*,expected_binding,current_binding):
    cell=proof.get('geographicCell')
    if isinstance(cell,dict)and cell.get('precisionMetres')==1:
        return exact_cell(proof,triangles,expected_binding=expected_binding,current_binding=current_binding)
    assert expected_binding==current_binding
    tri=np.asarray(triangles,float)
    assert tri.ndim==3 and tri.shape[1:]==(3,3)and np.isfinite(tri).all()
    sha=hashlib.sha256(tri.astype('<f8').tobytes()).hexdigest()
    assert sha==proof['worldTrianglesSHA256']==current_binding['decodedWorldTrianglesSHA256']
    assert proof['uid']==current_binding['uid']and proof['sourceSHA256']==current_binding['sourceSHA256']
    out=deepcopy(proof)
    out.update(reasons=sorted(set(proof['reasons'])|{REASON}),passed=False,
        proof={k:False for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},
        exactCellAdapterApplied=False,exactWholeCellCoverage=dict(covered=False,wholeOriginalFacesAccounted=len(tri),unavailableOrUnsupportedCell=True),installationApproved=False,modelGeometryChanges=0)
    return out
