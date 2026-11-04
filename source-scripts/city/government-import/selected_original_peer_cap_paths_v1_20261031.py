"""Replay cap paths against complete exact terrain-plus-original-peer clearance.

Positive finite source self-contacts only. No physical or support approval.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from complete_clearance_cap_paths_v2_20261024 import verify
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','low-faces','uid','peer','lease']:p.add_argument('--'+k,required=True)
    a=p.parse_args();lease=read(Path(a.lease));assert reservations.owns(lease) and {'building:'+a.uid,'building:'+a.peer}<=set(lease['resources']);assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,path):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    source=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid);g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid);attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
    low=take(a.low_faces,base/a.low_faces/'summary.json');assert low['sourceSHA256']==source['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256'] and set(low['uids'])=={a.uid,a.peer}
    producer=HERE/'selected_original_peer_low_face_context_v1_20261031.py';assert digest(producer.read_bytes())==pins[a.low_faces][str(producer.relative_to(ROOT))];refs.append(producer)
    ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);ground_sha=digest(ground.tobytes());asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds={'original':decode_original_world_triangles(asset.read_bytes()),**{name:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]for name,field in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]}}
    assert np.array_equal(worlds['literal'],np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)])
    peerrow=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.peer);peerattr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.peer)
    peerasset=ROOT/peerrow['candidate']['path'];peerraw=peerasset.read_bytes();assert digest(peerraw)==peerrow['sourceSHA256']==peerattr['sourceSHA256']==low['peerSourceSHA256'];refs.append(peerasset)
    pix=np.asarray(peerattr['completeOriginalIndex']).reshape(-1,3)
    peers={'original':decode_original_world_triangles(peerraw),**{name:np.asarray(peerattr[field],dtype='<f8').reshape(-1,3)[pix]for name,field in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]}}
    terrain=ground.copy();rows=[]
    for mode,tri in worlds.items():
        assert reservations.owns(lease)
        ground=np.concatenate([terrain,peers[mode]]);ground_sha=digest(ground.tobytes())
        proof=take(a.low_faces,base/a.low_faces/(mode+'.json.gz'));assert proof['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes()) and proof['groundSHA256']==ground_sha and proof['completeSourceFaces']==len(tri)==source['triangles']
        ids=[r['sourceFace']for r in proof['rows']];summary=next(r for r in low['rows']if r['mode']==mode);assert ids==summary['exactAffectedFaces'];pruned=int(np.count_nonzero(tri[:,:,1].min(1)-ground[:,:,1].max()>=-.5));assert pruned==proof['globalHeightBoundPrunedFaces']
        initial=verify(tri,ids);unresolved=[p['sourceFace']for p in initial['paths']if not p['hasExactSharedEdgeClearCapPath']];contacts=[]
        if unresolved:
            partial=exact_finite_contacts(tri,unresolved,tri,list(range(len(tri))))
            save(out/(mode+'-partial-contacts.json.gz'),partial)
            contacts=sorted({tuple(sorted((c['sourceFaceA'],c['sourceFaceB'])))for c in partial['contacts']if c['sourceFaceA']!=c['sourceFaceB'] and c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2})
        paths=verify(tri,ids,contacts);record=dict(initialSharedEdgeUnresolvedFaces=unresolved,mode=mode,sourceWorldSHA256=proof['sourceWorldSHA256'],completeDrawnGroundSHA256=ground_sha,completeDrawnGroundFacets=len(ground),completeGroundClearancePartition=paths)
        save(out/(mode+'.json.gz'),record);rows.append(record);print(dict(mode=mode,affected=len(ids),pathsPassed=paths['allAffectedHavePaths'],nonWallNegative=len(paths['negativeNonWallFaces'])),flush=True)
    result=dict(uids=[a.uid,a.peer],peerUid=a.peer,peerSourceSHA256=peerrow['sourceSHA256'],sourceSHA256=source['sourceSHA256'],rows=rows,allFourCompleteGroundClearCapPaths=all(r['completeGroundClearancePartition']['allAffectedHavePaths']for r in rows),sourceGeometryChanges=0,sourcePoseChanges=0,groundRootCredit=False,architectureReview=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Uses complete four-world source clearance partitions produced by exact finite-column checks against EVERY actual drawn ground facet, including zero-XZ/collapsed ground primitives. No filtered-ground hash substituted, no invented minimum for clear faces, and no tolerance bridging; exact positive partial original contacts are recomputed for previously unresolved source walls. Paths are original topology/cap-clearance evidence only; source wall role/placement/current foreign/browser/publication obligations remain.')
    assert reservations.owns(lease)
    save(out/'summary.json',result);refs.extend([HERE/'complete_clearance_cap_paths_v2_20261024.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']);module('complete_ground_cap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-complete-actual-ground-clearance-partition-and-original-cap-paths',refs,result)

if __name__=='__main__':main()
