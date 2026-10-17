"""Source-bound interpretation of the original Orchards lower connection.

Identity only. All original faces remain subject to physical acceptance.
"""
from copy import deepcopy
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import digest
UID='landsd/254629:0'
SHA='132aa978b271794e7cdde00a3a431e0585fc334af822e102b218335f52ff4b98'
WORLD='5e76b3a39f25cd38f87283ebaac8418015d5c8f5e0bfc7becd32ae9216635a11'
RAW=['fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent']
def interpret(raw,row,tri,forms,review):
 tri=np.asarray(tri,dtype='<f8');assert tri.shape==(11517,3,3) and digest(tri.tobytes())==WORLD
 assert row['uid']==raw['uid']==UID and row['sourceSHA256']==raw['sourceSHA256']==SHA
 assert raw['worldTrianglesSHA256']==WORLD and raw['reasons']==RAW and not raw['passed']
 assert raw['originalOwnership']['sourceGraphVerified'] and raw['originalOwnership']['originalRootName']=='B401241601501063C0'
 assert raw['exactWholeCellCoverage']['covered'] and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==11517
 assert review['uid']==UID and review['sourceSHA256']==SHA and review['faceCount']==239
 own=[f for f in forms if f['uid']==UID];pod=[f for f in forms if f['uid']=='landsd/233002:0'];assert len(own)==len(pod)==1
 own,pod=own[0],pod[0];assert own==row['source']['building']
 assert own['parent']==pod['parent']=='way/100512374' and own['buildingCSUID']=='4012416015T20050430' and own['base']==45.3
 assert pod['base']==18.3 and abs(pod['base']+pod['height']-45.3)<1e-9
 target=Polygon(own['rings'][0],own['rings'][1:]);podium=Polygon(pod['rings'][0],pod['rings'][1:])
 dist=shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),target).reshape(-1,3)
 ids=np.flatnonzero(dist.max(axis=1)>10);assert ids.tolist()==review['sourceFaces']
 role=tri[ids];projection=shapely.union_all(shapely.polygons(role[:,:,[0,2]]))
 assert podium.covers(projection) and role[:,:,1].min()>=pod['base'] and role[:,:,1].max()<own['base']
 # The unchanged extent limit still applies to every non-role face.
 remaining=np.setdiff1d(np.arange(len(tri)),ids);assert dist[remaining].max()<=10
 out=deepcopy(raw);out.update(policy='orchards-byte-bound-original-lower-connection-identity-v1',rawConnectionExtentIdentity=deepcopy(raw),rawExtentReasonsRetained=RAW,connectionRoleOriginalFaceIDs=ids.tolist(),ordinaryExtentFaceCount=len(remaining),reasons=[],passed=True,proof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,sourceInterpretationUsedAI=True,qualification='Named original lower connection interpreted using original-root ownership, exact byte/geometry binding, whole current podium containment and reviewed architect/pair imagery. Full source target coverage, foreign overlap and GeoRef proofs retained. No structural support, collision, terrain, foundation, runtime or publication credit.')
 return out
