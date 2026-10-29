"""Exact terminal-wall coverage bound to explicit current runtime and attribute jobs.

Native government terrain remains bound to its authenticated immutable cache.
No old renderer arrays or physical approvals are inherited.
"""
from pathlib import Path
import numpy as np
import argparse
from exact_ground_polygon_cover_v1_20261030 import prove as prove_area
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_ground_line_cover_v1_20261030 import prove
P='government-xl-disneyland-piers-after-passenger-'
BATCH=P+'75643-exact-shore-closure-v1-20261030'
UID='landsd/75643:0'
SHA='4c8e577256875f9ecc67fe5728e262113d852748ac743798b804f9b090f0dbc2'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch',required=True)
    parser.add_argument('--runtime',required=True)
    parser.add_argument('--buried',required=True)
    parser.add_argument('--attributes',required=True)
    args=parser.parse_args()
    assert all(v.startswith('government-xl-') and '/' not in v for v in vars(args).values())
    global BATCH
    BATCH=args.batch
    base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists()
    refs=[Path(__file__),HERE/'exact_ground_line_cover_v1_20261030.py',HERE/'test_exact_ground_line_cover_v1_20261030.py',HERE/'exact_ground_polygon_cover_v1_20261030.py',HERE/'test_exact_ground_polygon_cover_v1_20261030.py'];pins={}
    def take(suffix,path):
        batch=suffix
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    def doc(suffix,name='summary.json'):return take(suffix,base/suffix/name)
    selection=doc(args.runtime,'selection.json.gz')
    row=next(r for r in selection['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==SHA;refs.append(asset)
    attr=next(r for r in doc(args.attributes,'attributes.json.gz')['rows']if r['uid']==UID)
    assert attr['sourceSHA256']==SHA
    index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds={'packed':decode_original_world_triangles(asset.read_bytes())}
    for field in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:worlds[field]=np.asarray(attr[field]).reshape(-1,3)[index]
    buried=doc(args.buried,'75643:0.json')
    ids=[r['faceIndex']for r in buried['buriedFaces']];assert ids==[32612,32613]and all(not r['upward']for r in buried['buriedFaces'])
    ground=doc(P+'joint-government-ground-v1-20261030');checked=next(r for r in ground['rows']if r['uid']==UID)
    assert checked['sourceSHA256']==SHA and checked['nativeResultSHA256']==row['native']['resultSha']
    assert checked['originalTerrainFoundation']['fullyBuriedTriangles']==2 and checked['originalTerrainFoundation']['fullyBuriedUpwardTriangles']==0
    decoder=module('shore_closure_original_ground',HERE/'xl-second-pass.py');original_ground=[]
    govbatch=P+'joint-government-ground-v1-20261030'
    for name in checked['sourceTerrainPaths']:
        path=ROOT/name;assert digest(path.read_bytes())==pins[govbatch][name];refs.append(path)
        for item in read(path).get('buffers',[]):
            buffer=path.parent/item['uri'];assert digest(buffer.read_bytes())==pins[govbatch][str(buffer.relative_to(ROOT))];refs.append(buffer)
        original_ground.append(decoder.terrain_triangles(path))
    original_ground=np.concatenate(original_ground)
    runtime=args.runtime
    g=next(r for r in take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz')['rows']if r['uid']==UID)
    assert g['sourceSHA256']==SHA
    actual=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
    rows=[]
    for mode,tri in worlds.items():
        assert len(tri)==32634
        wall=tri[ids];normal=np.cross(wall[:,1]-wall[:,0],wall[:,2]-wall[:,0])
        assert np.all(np.linalg.norm(normal,axis=1)>0)
        assert np.all(np.abs(normal[:,1]) < .25*np.linalg.norm(normal,axis=1))
        assert np.ptp(wall[:,:,1])<1 and 4<float(wall[:,:,1].min())<float(wall[:,:,1].max())<6
        band=wall[:,:,2]-tri[:,:,2].min();assert band.min()==0 and band.max()<=.0625
        top=float(wall[:,:,1].max());source_rows=[]
        lo,hi=wall[:,:,[0,2]].reshape(-1,2).min(0),wall[:,:,[0,2]].reshape(-1,2).max(0)
        for name,terrain in [('same-cache-original-government-terrain',original_ground),('actual-current-private-drawn-ground',actual)]:
            mask=(terrain[:,:,0].max(1)>=lo[0])&(terrain[:,:,0].min(1)<=hi[0])&(terrain[:,:,2].max(1)>=lo[1])&(terrain[:,:,2].min(1)<=hi[1])
            selected=terrain[mask];faceids=np.flatnonzero(mask).tolist();proofs=[]
            for faceid,face in zip(ids,wall):
                points=np.unique(face[:,[0,2]],axis=0)
                if len(points)==2:
                    proof=prove(points[0],points[1],top,selected)
                    for piece in proof['pieces']:piece['completeGroundFaceIndex']=faceids[piece['groundFace']]
                else:
                    assert len(points)==3
                    proof=prove_area(face[:,[0,2]],top,selected)
                    proof['completeGroundFaceIndices']=[faceids[i]for i in proof['groundFaces']]
                proofs.append(dict(sourceFaceId=faceid,**proof))
            source_rows.append(dict(ground=name,facetProofs=proofs))
        rows.append(dict(mode=mode,sourceFaceIds=ids,sourceWallVertices=wall.tolist(),sourceTopM=top,terminalBoundaryBandM=float(band.max()),sourceWholeZExtentM=float(np.ptp(tri[:,:,2])),proofs=source_rows))
    result=dict(uids=[UID],sourceSHA256=SHA,completeOriginalFaces=32634,sourceFaceIds=ids,rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,allFourStreamsStrictContinuousNativeAndActualGroundCover=True,ordinaryBurialPolicyPassed=False,physicalAcceptance=False,installationApproved=False,qualification='Only two exact non-upward source terminal wall facets, within the low-Z1/16m boundary band of this exact original. Their entire projected line or positive-area triangle and conservative whole-wall maximum height are strictly below both authenticated native government terrain and actual proposed drawn ground in all four streams. Rational interval/plane-envelope and polygon-subtraction proof includes every covered segment, not samples or a tolerance waiver. Source-specific shoreline closure interpretation and full neighbour/browser/publication acceptance remain separate.')
    save(out/'summary.json',result);refs += [HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-second-pass.py']
    module('shore_closure_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-source-terminal-wall-continuous-government-and-current-ground-context',refs,result)
    print({'batch':BATCH,'completeFourWorldNativeAndActualFacetCover':True})

if __name__=='__main__':main()
