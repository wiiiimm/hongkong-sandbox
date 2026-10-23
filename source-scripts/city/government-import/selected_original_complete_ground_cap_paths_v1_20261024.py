"""Replay cap paths against complete exact four-world/all-drawn-ground clearance proofs."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from complete_clearance_cap_paths_v1_20261024 import verify


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','low-faces','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,path):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    source=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid);g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid);attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
    low=take(a.low_faces,base/a.low_faces/'summary.json');assert low['sourceSHA256']==source['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256'] and low['uids']==[a.uid]
    producer=HERE/'selected_original_four_world_low_face_context_v1_20261024.py';assert digest(producer.read_bytes())==pins[a.low_faces][str(producer.relative_to(ROOT))];refs.append(producer)
    ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);ground_sha=digest(ground.tobytes());asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds={'original':decode_original_world_triangles(asset.read_bytes()),**{name:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]for name,field in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]}}
    assert np.array_equal(worlds['literal'],np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)])
    rows=[]
    for mode,tri in worlds.items():
        proof=take(a.low_faces,base/a.low_faces/(mode+'.json.gz'));assert proof['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes()) and proof['groundSHA256']==ground_sha and proof['completeSourceFaces']==len(tri)==source['triangles']
        ids=[r['sourceFace']for r in proof['rows']];summary=next(r for r in low['rows']if r['mode']==mode);assert ids==summary['exactAffectedFaces'];pruned=int(np.count_nonzero(tri[:,:,1].min(1)-ground[:,:,1].max()>=-.5));assert pruned==proof['globalHeightBoundPrunedFaces']
        paths=verify(tri,ids);record=dict(mode=mode,sourceWorldSHA256=proof['sourceWorldSHA256'],completeDrawnGroundSHA256=ground_sha,completeDrawnGroundFacets=len(ground),completeGroundClearancePartition=paths)
        save(out/(mode+'.json.gz'),record);rows.append(record);print(dict(mode=mode,affected=len(ids),pathsPassed=paths['allAffectedHavePaths'],nonWallNegative=len(paths['negativeNonWallFaces'])),flush=True)
    result=dict(uids=[a.uid],sourceSHA256=source['sourceSHA256'],rows=rows,allFourCompleteGroundClearCapPaths=all(r['completeGroundClearancePartition']['allAffectedHavePaths']for r in rows),sourceGeometryChanges=0,sourcePoseChanges=0,groundRootCredit=False,architectureReview=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Uses complete four-world source clearance partitions produced by exact finite-column checks against EVERY actual drawn ground facet, including zero-XZ/collapsed ground primitives. No filtered-ground hash substituted, no invented minimum for clear faces, and no tolerance bridging. Paths are original topology/cap-clearance evidence only; source wall role/placement/current foreign/browser/publication obligations remain.')
    save(out/'summary.json',result);refs.extend([HERE/'complete_clearance_cap_paths_v1_20261024.py',HERE/'exact_packed_world_geometry_20261009.py']);module('complete_ground_cap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-complete-actual-ground-clearance-partition-and-original-cap-paths',refs,result)

if __name__=='__main__':main()
