"""Identify original shared lower floors beneath the peer's higher surfaces."""
import argparse,sys,uuid
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_convex_projection_coverage_v1_20261024 import rational,uncovered,area2
from exact_original_triangle_pair_column_gap_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-prosperous235568-';BATCH=P+'block4-shared-lower-floor-context-v1-20261031';UID='landsd/236076:0';PEER='landsd/235568:0'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lease');a=ap.parse_args()
    if not a.lease:
        from north_pair_nonwall_topology_v1_20261027 import execute_reserved
        local=HERE/'local'/BATCH;assert not local.exists()and not(BASE/BATCH).exists()
        claim=reservations.claim('prosperous-shared-floor-'+str(uuid.uuid4()),['building:'+UID,'building:'+PEER,'terrain:city/data/terrain.json'],batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],local/'reservation.json',[sys.executable,__file__,'--lease',str(local/'reservation.json')])
    lease=read(Path(a.lease));assert reservations.owns(lease)and {'building:'+UID,'building:'+PEER}<=set(lease['resources']);out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime=P+'six-original-patch-runtime-v1-20261031';selection=take(runtime,'selection.json.gz');rows={r['uid']:r for r in selection['rows']};attrs={r['uid']:r for r in take(P+'six-original-attributes-v1-20261031','attributes.json.gz')['rows']};worlds={}
    for uid in [UID,PEER]:
        row,attr=rows[uid],attrs[uid];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==attr['sourceSHA256'];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        worlds[uid]={'original':decode_original_world_triangles(asset.read_bytes()),**{mode:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
    roles=P+'236076-junction-roles-v1-20261031';rs=take(roles,'summary.json');assert rs['uids']==[PEER,UID]and rs['sourceSHA256ByUid']=={u:rows[u]['sourceSHA256']for u in [UID,PEER]};original=take(roles,'original.json.gz')
    prior=P+'block4-compound-buried-face-ids-v1-20261031';burial=take(prior,'summary.json');assert burial['countsAndAreaExactlyReproduced'];ids=[2721,2722,2723,2735];nominees={i:sorted({c['sourceFaceA']for c in original if c['sourceFaceB']==i and c['dimension']==2 and c['contactRole']=='shared-plane-area-contact'})for i in ids};assert all(nominees.values());results=[]
    for mode,tri in worlds[UID].items():
        assert reservations.owns(lease);bound=take(prior,mode+'.json');assert bound['fullyBuriedUpwardFaceIds']==ids and bound['sourceWorldSHA256ByUid']=={u:digest(worlds[u][mode].tobytes())for u in [UID,PEER]};parts=[]
        for i in ids:
            source=tri[i];peer=worlds[PEER][mode][nominees[i]];remaining=uncovered(rational(source[:,[0,2]]),[rational(t[:,[0,2]])for t in peer]);assert not remaining,'No tolerance credit for missing floor coverage';proofs=[];gaps=[]
            for j,t in zip(nominees[i],peer):
                q=verify(source,t);assert q['exactClosedHorizontalProjectionsMeet'];gaps.extend(Fraction(v['exactGapM'])for v in q['allExactBasicFeasibleColumnVertices']);proofs.append(dict(peerFace=j,proof=q))
            # Retain the actual small literal offset. Existing strict native contact bounds only.
            assert min(gaps)>=Fraction(-1,10)and max(gaps)<=1
            parts.append(dict(sourceFace=i,sourceVertices=source.tolist(),peerFaces=nominees[i],sourceProjectedAreaExact=str(abs(area2(rational(source[:,[0,2]])))/2),uncoveredProjectedAreaExact='0',entireClosedProjectionCovered=True,exactMinimumLowerFloorGapM=str(min(gaps)),exactMaximumLowerFloorGapM=str(max(gaps)),exactlyCoincident=all(g==0 for g in gaps),withinExistingStrictNativeInterfaceInterval=True,finitePairProofs=proofs))
        record=dict(mode=mode,sourceWorldSHA256ByUid=bound['sourceWorldSHA256ByUid'],completeCompoundGroundSHA256=bound['completeCompoundGroundSHA256'],floors=parts);save(out/(mode+'.json'),record);results.append(dict(mode=mode,fullyFlaggedUpwardFaces=ids,allCompleteLowerFloorCoverage=True,allWithinExistingStrictNativeInterfaceInterval=True,allExactlyCoincident=all(p['exactlyCoincident']for p in parts)))
    assert reservations.owns(lease)
    for uid in worlds:assert digest((ROOT/rows[uid]['candidate']['path']).read_bytes())==rows[uid]['sourceSHA256']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    result=dict(uids=[UID,PEER],sourceSHA256ByUid=rs['sourceSHA256ByUid'],rows=results,rawHighestSurfaceBurialCountsUnchanged=True,strictFoundationAccepted=False,sourceRoleAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='All4fullyflagged upward facets are exactly covered in projection by independently rebuilt lower original peer floors in all4streams. Exact finite-column gaps are0in original/Float32 and recorded near-1e-14m in literal coordinates, all inside the unchanged strict[-0.1,1]m native interface interval. No buffers, snapping, epsilon coverage, source edits, new roots or general under-roof exception. The prior highest-surface compound warning remains; this measured lower-floor relationship is source-role context only.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_convex_projection_coverage_v1_20261024.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py']);module('prosperous_shared_floor_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-four-world-original-shared-lower-floor-context',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
