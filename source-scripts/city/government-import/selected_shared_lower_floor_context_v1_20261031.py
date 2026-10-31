"""Measure exact lower-floor correspondence for an explicit original-source batch."""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_shared_lower_floor_v1_20261031 import floor_context
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import'
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','assembly','peer']:ap.add_argument('--'+k,required=True)
    ap.add_argument('--part',action='append',required=True,help='uid,complete-buried-face-census-batch');ap.add_argument('--lease');a=ap.parse_args()
    parts=dict(p.split(',',1)for p in a.part);assert len(parts)==len(a.part)and a.peer not in parts and 0<len(parts)<=16
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.runtime,a.attributes,a.assembly,*parts.values()]);out=BASE/a.batch;assert not out.exists();actors=sorted([a.peer,*parts])
    if not a.lease:
        local=HERE/'local'/a.batch;assert not local.exists();claim=reservations.claim('shared-lower-floor-'+str(uuid.uuid4()),['building:'+u for u in actors],batch=a.batch,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],local/'reservation.json',[sys.executable,__file__,*sys.argv[1:],'--lease',str(local/'reservation.json')])
    lease=read(Path(a.lease));assert reservations.owns(lease)and {'building:'+u for u in actors}<=set(lease['resources']);refs=[Path(__file__)];pins={}
    def take(batch,name=None,path=None):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=path if path is not None else BASE/batch/(name or 'summary.json');assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take(a.runtime,'selection.json.gz');rows={r['uid']:r for r in selection['rows']};attrs={r['uid']:r for r in take(a.attributes,'attributes.json.gz')['rows']};assembly=take(a.assembly);worlds={}
    for uid in actors:
        row,attr=rows[uid],attrs[uid];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==attr['sourceSHA256']==assembly['sourceSHA256ByUid'][uid];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        worlds[uid]={'original':decode_original_world_triangles(asset.read_bytes()),**{m:np.asarray(attr[f],dtype='<f8').reshape(-1,3)[ix]for m,f in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
    results=[]
    for uid,census in parts.items():
        c=take(census);assert c['sourceSHA256ByUid']=={u:rows[u]['sourceSHA256']for u in [uid,a.peer]}and c['countsAndAreaExactlyReproduced']
        pair=[r for r in assembly['rows']if {r['uid'],r['peerUid']}=={uid,a.peer}and r['mode']=='original'];assert len(pair)==1;pair=pair[0];assert not pair['strictBoundsSeparated']
        raw=take(a.assembly,path=ROOT/pair['rawPath']);assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0 and len(raw['contacts'])==sum(pair['contactDimensions'].values())
        side='A'if pair['uid']==uid else'B';other='B'if side=='A'else'A';nominees={}
        original_census=take(census,'original.json');ids=original_census['fullyBuriedUpwardFaceIds'];assert ids
        for i in ids:nominees[i]=sorted({r['sourceFace'+other]for r in raw['contacts']if r['sourceFace'+side]==i and r['dimension']==2 and r['sourcePrimitiveDimensionA']==r['sourcePrimitiveDimensionB']==2})
        for mode,tri in worlds[uid].items():
            assert reservations.owns(lease);bound=take(census,mode+'.json');assert bound['fullyBuriedUpwardFaceIds']==ids and bound['sourceWorldSHA256ByUid']=={u:digest(worlds[u][mode].tobytes())for u in [uid,a.peer]};floors=[]
            for i in ids:
                peer=worlds[a.peer][mode][nominees[i]];proof=floor_context(tri[i],peer);floors.append(dict(sourceFace=i,sourceVertices=tri[i].tolist(),peerFaceIds=nominees[i],**proof))
            row=dict(uid=uid,mode=mode,sourceWorldSHA256ByUid=bound['sourceWorldSHA256ByUid'],completeCompoundGroundSHA256=bound['completeCompoundGroundSHA256'],floors=floors,allFullyFlaggedUpwardFacesHaveLowerPeerCorrespondence=all(f['completeLowerPeerCorrespondence']for f in floors));save(out/(uid.split('/')[1]+'-'+mode+'.json'),row);results.append({k:v for k,v in row.items()if k!='floors'});print(dict(uid=uid,mode=mode,faces=ids,correspondence=row['allFullyFlaggedUpwardFacesHaveLowerPeerCorrespondence']),flush=True)
    assert reservations.owns(lease)
    for uid in actors:assert digest((ROOT/rows[uid]['candidate']['path']).read_bytes())==rows[uid]['sourceSHA256']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    summary=dict(uids=actors,sourceSHA256ByUid={u:rows[u]['sourceSHA256']for u in actors},rows=results,allLowerPeerCorrespondence=all(r['allFullyFlaggedUpwardFacesHaveLowerPeerCorrespondence']for r in results),rawHighestSurfaceBurialFlagsUnchanged=True,sourceRoleAccepted=False,strictFoundationAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Positive-area saved original peer contacts nominate face IDs only. Exact full projected coverage and finite-column height extrema independently recomputed in every represented world with the existing strict native interval. Missing correspondences are measured negative results, not failed jobs/corrupt sources. No upper-roof flags erased, new roots, acceptance or generic under-roof exception.')
    save(out/'summary.json',summary);refs.extend([HERE/'original_shared_lower_floor_v1_20261031.py',HERE/'test_original_shared_lower_floor_v1_20261031.py',HERE/'exact_convex_projection_coverage_v1_20261024.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'exact_packed_world_geometry_20261009.py']);module('shared_lower_floor_batch_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'explicit-original-batch-four-world-shared-lower-floor-context',list(dict.fromkeys(refs)),summary)
if __name__=='__main__':main()
