"""One explicit terrain-vertex proposal, solved from complete finite wall columns.

All unchanged government geometry remains literal. The terrain is changed;
physical, support, current neighbours and runtime must be independently rerun.
"""
import copy,hashlib
from fractions import Fraction as F
import numpy as np
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify as column
from original_bound_facet_wall_context_v2_20261010 import exposure_at_vertex
SOURCE='22b458321ca483c53324ee152cb27c382e5ac4dfd745974f169b1c551ac8a6c1'
POSITION='01ad431a53d654e114a5b07af6efede7a9a840b4bc259425d90737f981989e39'
INDEX='e6d01f8707b778eb0078e6ebade95258c02f8ee323026f174b1ed25c1c751450'
VERTEX=np.array([1892.4375,32.67086410522461,-3061.390625])
IDS=[2828,2830,2833,13946,13947,14147,27053,27054]
INCIDENT=[942,943,944,4648,4649,4715,9017,9018]
SOURCE_FACES=[2958,2959,2961]
def sha(a):return hashlib.sha256(a.tobytes()).hexdigest()
def propose(patch,raw):
 assert hashlib.sha256(raw).hexdigest()==SOURCE
 source=decode_original_world_triangles(raw);assert source.shape==(10661,3,3)
 p=np.asarray(patch['nativeMesh']['position'],float).reshape(-1,3);idx=np.asarray(patch['nativeMesh']['index'],np.uint32).reshape(-1,3)
 assert sha(p)==POSITION and sha(idx)==INDEX,'Complete prior terrain differs'
 ids=np.flatnonzero(np.all(p==VERTEX,axis=1));assert ids.tolist()==IDS
 assert np.flatnonzero(np.isin(idx,ids).any(1)).tolist()==INCIDENT
 ground=p[idx];delta=F(0);records=[];margin=F(1,100)
 for face in SOURCE_FACES:
  vertex=source[face,int(np.argmax(source[face,:,1]))];point=np.repeat(vertex[None,:],3,axis=0)
  xz=ground[:,:,[0,2]];near=np.flatnonzero((xz.max(1)>=vertex[[0,2]]).all(1)&(xz.min(1)<=vertex[[0,2]]).all(1));seen=False
  for g in near:
   proof=column(point,ground[g]);affected=[k for k in range(3) if int(idx[g,k]) in IDS]
   for witness in proof['allExactBasicFeasibleColumnVertices']:
    seen=True;weights=list(map(F,witness['exactGroundBarycentricWeights']));coefficient=sum((weights[k] for k in affected),F(0));gap=F(witness['exactGapM']);required=F(0)
    if gap<margin:
     assert coefficient>0,'Independent unmoved facet blocks exposure'
     required=(margin-gap)/coefficient;delta=max(delta,required)
    records.append(dict(sourceFace=face,terrainFace=int(g),witness=witness,movedVertexWeight=str(coefficient),requiredVerticalChangeM=str(required)))
  assert seen,'Complete finite original vertex coverage required'
 assert 0<delta<F(65,100),'Bounded measured terrain cause exceeded'
 target=F(float(VERTEX[1]))-delta;ceiling=np.float32(float(target))
 if F(float(ceiling))>target:ceiling=np.nextafter(ceiling,np.float32(-np.inf))
 after=p.copy();after[ids,1]=float(ceiling)
 assert np.array_equal(after[:,[0,2]],p[:,[0,2]]) and np.array_equal(after[np.setdiff1d(np.arange(len(p)),ids)],p[np.setdiff1d(np.arange(len(p)),ids)])
 newground=after[idx];exposure=[]
 for face in SOURCE_FACES:
  vertex=source[face,int(np.argmax(source[face,:,1]))];proof=exposure_at_vertex(vertex,newground);assert F(proof['exactExposureLowerBoundM'])>=margin;exposure.append(dict(sourceFace=face,proof=proof))
 out=copy.deepcopy(patch);out['nativeMesh']['position']=after.reshape(-1).tolist();assert out['nativeMesh']['index']==patch['nativeMesh']['index']
 proof=dict(contract='man-fuk-three-original-walls-one-terrain-vertex-exposure-proposal-v1',sourceSHA256=SOURCE,completeOriginalFaces=10661,originalWallFaces=SOURCE_FACES,originalWallCoordinates=source[SOURCE_FACES].tolist(),priorWholeTerrainPositionSHA256=POSITION,newWholeTerrainPositionSHA256=sha(after),wholeTerrainIndexSHA256=INDEX,originalRepeatedTerrainVertex=VERTEX.tolist(),changedTerrainVertexRecords=IDS,changedIncidentTerrainFaces=INCIDENT,exactMinimumSolvedVerticalChangeM=str(delta),actualFloat32VerticalChangeM=float(VERTEX[1]-ceiling),newTerrainVertexHeightM=float(ceiling),declaredOriginalVertexExposureMarginM=str(margin),allFiniteOriginalColumnConstraints=records,verifiedFiniteOriginalVertexExposures=exposure,allOtherTerrainVerticesUnchanged=True,allTerrainHorizontalCoordinatesUnchanged=True,allTerrainIndicesUnchanged=True,terrainProposalChanged=True,exactSameSurfaceClaim=False,sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False,qualification='Lower only the repeated candidate terrain vertex whose finite column interpolation buries the three unchanged original walls. Solve against every basic feasible finite column witness, round down to Float32 and independently verify exact closed projection coverage and10mm original-vertex exposure. All8 incident terrain faces explicitly change; no source-role, root, neighbour or physical exemption.')
 out['nativeMesh']['source']['manFukOriginalWallExposure']=proof
 return out,proof
