"""Exact current scene delta and dynamic append binding; no acceptance."""
import copy
import numpy as np
from polyu_compact_runtime_mesh_projection_v1_draft_20261014 import mesh_binding
from polyu_append_historical_capture_binding_v1_draft_20261014 import grid_domain
OLD='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
CURRENT='12971667a74b07de90ce5ee29999f44a6bf297de84ec7916a629bc42725cd82c'
UPTON_CAT='city/data/official-models/government-xl-upton-joint-original-dimension-private-stage-v2-20261014/catalogue.json'
AQUA_CAT='city/data/official-models/government-xl-aqua-marine193086-original-private-stage-v1-20261014/catalogue.json'
UPTON_PATCH='city/data/government-native-upton-certified6170-joint-original-dimension-v2-20261014.json'
OLD_PATCH='city/data/government-native-79882-0.json'
def scene_delta(old,current):
 expected=copy.deepcopy(old);expected['officialModelCatalogues']=old['officialModelCatalogues']+[UPTON_CAT,AQUA_CAT]
 matches=[i for i,p in enumerate(old['terrainPatches'])if p['url']==OLD_PATCH];assert len(matches)==1
 changed=[p for p in current['terrainPatches']if p not in old['terrainPatches']];assert len(changed)==1 and changed[0]['url']==UPTON_PATCH
 # Actual installed publisher replaces the sole entry in place; order matters.
 expected['terrainPatches'][matches[0]]=changed[0]
 assert current==expected,'unexpected current field/catalogue/terrain/order delta'
 return dict(addedCatalogueURLs=[UPTON_CAT,AQUA_CAT],removedTerrainURL=OLD_PATCH,addedTerrainURL=UPTON_PATCH,
             oldSceneRemainsHistorical=True,noOldManifestRestore=True)
def terrain_disjoint(patch,domain):
 bounds=grid_domain(patch);assert not patch.get('patches')and not patch.get('hydro')
 if patch.get('nativeMesh'):
  p=np.asarray(patch['nativeMesh']['position'],dtype='<f4').astype('<f8').reshape(-1,3);assert len(p)and np.isfinite(p).all()
  lo=p[:,[0,2]].min(0);hi=p[:,[0,2]].max(0)
  bounds=[min(bounds[0],lo[0]),min(bounds[1],lo[1]),max(bounds[2],hi[0]),max(bounds[3],hi[1])]
 assert bounds[2]<domain[0]or bounds[0]>domain[2]or bounds[3]<domain[1]or bounds[1]>domain[3],'changed terrain can touch full PolyU domain'
 return dict(completeGridAndUnusedActualF32PositionBoundsXZ=list(map(float,bounds)),strictClosedDomainDisjoint=True,
             notNativeBuildingMeshSeparationCredit=True)
def append_binding(nom,old):
 mesh=nom['newNativeMesh'];oldmesh={k:old['nativeMesh'][k]for k in ['position','index']}
 previous=mesh_binding(oldmesh);assert previous==nom['previousCompleteMeshBinding']
 current=mesh_binding(mesh);assert current==nom['newCompleteMeshBinding']
 assert previous['completeIndexedFaces']==148459 and previous['completePositionVertices']==587502
 assert np.asarray(mesh['position'][:587502*3],dtype='<f8').tobytes()==np.asarray(oldmesh['position'],dtype='<f8').tobytes()
 assert mesh['index'][:148459*3]==oldmesh['index']
 rows=nom['appendedFaces'];assert [p['candidateFace']for p in rows]==list(range(148459,current['completeIndexedFaces']))
 assert current['completePositionVertices']==587502+3*len(rows)
 raw=np.asarray(mesh['position'],dtype='<f8').reshape(-1,3)
 for k,row in enumerate(rows):
  i=row['candidateFace'];assert mesh['index'][i*3:i*3+3]==list(range(587502+3*k,587502+3*k+3))
  assert raw[mesh['index'][i*3:i*3+3]].tobytes()==np.asarray(row['packing']['packedTriplet'],dtype='<f8').tobytes()
  assert row['packing']['packedYNotAboveOwnAuthenticatedParentPlane']and row['completeNewPieceOrdinaryCompatibility']['eligible']
 assert len(nom['completeParentAccounts'])==12 and [p['parentFacet']for p in nom['completeParentAccounts']]==list(range(12))
 actual=[i for p in nom['completeParentAccounts']for i in p['newCandidateFaces']];assert actual==list(range(148459,current['completeIndexedFaces']))
 assert nom['all148459OldFacesAnd587502PositionsIncludingUnusedExactlyPreserved']and nom['sourceOverlapMustBeReviewedForNewGeometry']and not nom['currentAcceptance']
 return current
