"""UNEXECUTED append/count/provenance and named historical-manifest binding."""
from pathlib import Path
import hashlib
import numpy as np
from polyu_compact_runtime_mesh_projection_v1_draft_20261014 import mesh_binding

HISTORICAL='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
MANIFEST='3d-viewer/city/data/manifest.json'
def historical_manifest(context):
    rows=[q for q in context['mutableCurrentByteSnapshots']if q['original']['path']==MANIFEST]
    assert len(rows)==1;row=rows[0];assert row['original']['sha256']==row['savedHistoricalBytes']['sha256']==HISTORICAL
    assert row['savedHistoricalBytes']['path']!=MANIFEST
    return row['savedHistoricalBytes']

def resolve_source_ref(q,archive,root):
    if q['path']==MANIFEST:
        assert q['sha256']==HISTORICAL and archive['sha256']==HISTORICAL
        result=dict(archive)
    else:result=dict(q)
    p=Path(root)/result['path'];assert p.is_file()and hashlib.sha256(p.read_bytes()).hexdigest()==result['sha256'],result['path']
    return result

def grid_domain(patch):
    w,h=patch['w'],patch['h'];g=patch['meta']['georef']
    assert type(w)is type(h)is int and w>1 and h>1 and g['W']==w and g['H']==h
    assert g['aE']>0 and g['aN']<0 and all(len(patch[k])==w*h for k in ['elev','renderedElev','vegetation'])
    return [g['bE']-834500,816500-g['bN'],g['bE']+(w-1)*g['aE']-834500,816500-(g['bN']+(h-1)*g['aN'])]

def validate_append(nom,old_mesh,old_binding,new_binding):
    assert nom['schema']=='private-polyu-append-complete-legacy-source-region-nomination-v1'
    assert not nom['currentAcceptance']and not nom['physicalAccepted']and not nom['installationApproved']
    assert nom['previousCompleteMeshBinding']==old_binding==mesh_binding(old_mesh)
    mesh=nom['newNativeMesh'];assert nom['newCompleteMeshBinding']==new_binding==mesh_binding(mesh)
    old_faces=old_binding['completeIndexedFaces'];old_vertices=old_binding['completePositionVertices']
    assert nom['oldFaceProvenanceRange']==[0,old_faces]and nom['originalPositionBufferAndIndexPrefixUnchanged']
    assert np.asarray(mesh['position'][:len(old_mesh['position'])],dtype='<f8').tobytes()==np.asarray(old_mesh['position'],dtype='<f8').tobytes()
    assert mesh['index'][:len(old_mesh['index'])]==old_mesh['index']
    raw=np.asarray(mesh['position'],dtype='<f8').reshape(-1,3)[np.asarray(mesh['index'],dtype=np.int64).reshape(-1,3)]
    appended=nom['appendAccount']['appendedFaces'];assert [q['candidateFace']for q in appended]==list(range(old_faces,len(raw)))
    assert new_binding['completePositionVertices']==old_vertices+3*len(appended)
    accounts={}
    for account in nom['sourceRegionAccounts']:
        pointer=account['target']['sourcePointer'];key=(pointer['oldPrivateFace'],pointer['outsidePolygon']);assert key not in accounts;accounts[key]=account
    for k,row in enumerate(appended):
        assert row['kind']=='appendedLegacyExactSourceRegionOwnPlaneCellEnclosure'and not row['physicalAccepted']and row['originalBuildingGeometryPoseUnchanged']
        p=row['sourcePointer'];account=accounts[(p['oldPrivateFace'],p['outsidePolygon'])];assert account['target']['sourcePointer']==p
        piece=account['exactOwnPlaneCellEnclosure']['triangles'][row['localTriangle']]
        assert row['completeIdealSourcePlanePoints']==piece['idealSourcePlanePoints']and row['exactVerticalSourcePlaneResidualM']==piece['exactVerticalSourcePlaneResidualM']
        assert raw[row['candidateFace']].tobytes()==np.asarray(row['packedTriplet'],dtype='<f8').tobytes()==np.asarray(piece['packedPieceTriplet'],dtype='<f8').tobytes()
        assert mesh['index'][3*row['candidateFace']:3*(row['candidateFace']+1)]==list(range(old_vertices+3*k,old_vertices+3*k+3))
    existing={q.tobytes()for q in raw}
    for row in nom['appendAccount']['exactExistingRepresentations']:
        assert row['exactXYZAlreadyPresent']and row['noNewAcceptanceCredit'];p=row['sourcePointer'];account=accounts[(p['oldPrivateFace'],p['outsidePolygon'])]
        assert p==account['target']['sourcePointer'];piece=account['exactOwnPlaneCellEnclosure']['triangles'][row['localTriangle']]
        assert np.asarray(piece['packedPieceTriplet'],dtype='<f8').tobytes()in existing
    return raw
