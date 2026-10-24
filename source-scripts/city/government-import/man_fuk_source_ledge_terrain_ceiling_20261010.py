"""One numeric terrain-only proposal derived from two unchanged original ledges.

This explicitly changes six incident terrain faces, never building geometry.
No source-surface equivalence, physical acceptance or publication is claimed.
"""
import copy,hashlib
import numpy as np
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
SOURCE='22b458321ca483c53324ee152cb27c382e5ac4dfd745974f169b1c551ac8a6c1'
POSITION='a7a909aeddfef9547fd495a23558b45352f07ecf4efd94ad258c6a7d78b65569'
INDEX='e6d01f8707b778eb0078e6ebade95258c02f8ee323026f174b1ed25c1c751450'
VERTEX=np.array([1964.1328125,35.49215316772461,-3135.40625])
IDS=[4640,4642,4645,4673,4674,4677]
FACES=[1546,1547,1548,1557,1558,1559]
def sha(a):return hashlib.sha256(a.tobytes()).hexdigest()
def propose(patch,source):
 assert hashlib.sha256(source).hexdigest()==SOURCE,'Unchanged complete original Man Fuk source required'
 tri=decode_original_world_triangles(source);assert tri.shape==(10661,3,3)
 ledges=tri[[9793,9794]];height=float(ledges[0,0,1]);assert np.all(ledges[:,:,1]==height) and height==34.86899948120117
 assert np.all(np.cross(ledges[:,1]-ledges[:,0],ledges[:,2]-ledges[:,0])[:,1]>0),'Original upward ledges required'
 p=np.asarray(patch['nativeMesh']['position'],dtype=np.float64).reshape(-1,3);idx=np.asarray(patch['nativeMesh']['index'],dtype=np.uint32).reshape(-1,3)
 assert sha(p)==POSITION and sha(idx)==INDEX,'Complete pre-proposal terrain changed'
 ids=np.flatnonzero(np.all(p==VERTEX,axis=1));assert ids.tolist()==IDS
 assert np.flatnonzero(np.any(np.isin(idx,ids),axis=1)).tolist()==FACES
 ceiling=float(np.float32(height-.01))
 if ceiling>height-.01:ceiling=float(np.nextafter(np.float32(ceiling),np.float32(-np.inf)))
 delta=float(VERTEX[1]-ceiling);assert 0<delta<.65,'Terrain-only correction exceeds the measured bounded cause'
 out=copy.deepcopy(patch);after=p.copy();after[ids,1]=ceiling
 assert np.array_equal(after[:,[0,2]],p[:,[0,2]]) and np.array_equal(after[np.setdiff1d(np.arange(len(p)),ids)],p[np.setdiff1d(np.arange(len(p)),ids)])
 out['nativeMesh']['position']=after.reshape(-1).tolist()
 assert out['nativeMesh']['index']==patch['nativeMesh']['index']
 proof=dict(contract='man-fuk-one-source-ledge-derived-terrain-vertex-ceiling-v1',sourceSHA256=SOURCE,completeOriginalFaces=len(tri),originalUpwardLedgeFaces=[9793,9794],originalUpwardLedgeCoordinates=ledges.tolist(),originalLedgeHeightHKPD=height,terrainCeilingHKPD=ceiling,declaredClearanceMarginM=.01,priorWholeTerrainPositionSHA256=POSITION,wholeTerrainIndexSHA256=INDEX,newWholeTerrainPositionSHA256=sha(after),changedTerrainVertexRecords=IDS,changedIncidentTerrainFaces=FACES,originalRepeatedTerrainVertex=VERTEX.tolist(),verticalTerrainChangeM=delta,allTerrainHorizontalCoordinatesUnchanged=True,allTerrainIndicesUnchanged=True,allOtherTerrainVerticesUnchanged=True,terrainProposalChanged=True,exactSameSurfaceClaim=False,sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False,qualification='Lower the one repeated candidate terrain vertex which causes the complete original ledge intersection. All six incident terrain faces change explicitly; complete finite-source, current native/basic neighbours and runtime must be rechecked. No terrain/source equivalence or wall/support waiver.')
 out['nativeMesh']['source']['manFukOriginalLedgeCeiling']=proof
 return out,proof
