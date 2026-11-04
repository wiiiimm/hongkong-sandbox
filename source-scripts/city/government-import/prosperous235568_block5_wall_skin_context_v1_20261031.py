"""Bind the ten original Block5 wall facets to complete compound clearance."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_wall_skin_escape_v1_20261031 import wall_escape
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-prosperous235568-';BATCH=P+'block5-wall-skin-context-v1-20261031';UID='landsd/235119:0';PEER='landsd/235568:0'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lease',required=True);a=ap.parse_args();lease=read(Path(a.lease));assert reservations.owns(lease)and {'building:'+UID,'building:'+PEER}<=set(lease['resources'])
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    runtime=P+'six-original-patch-runtime-v1-20261031';rows=take(runtime,'selection.json.gz')['rows'];source=next(r for r in rows if r['uid']==UID);attr=next(r for r in take(P+'six-original-attributes-v1-20261031','attributes.json.gz')['rows']if r['uid']==UID)
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==attr['sourceSHA256'];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds={'original':decode_original_world_triangles(asset.read_bytes()),**{name:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]for name,field in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]}}
    components=take(P+'block5-eight-wall-components-v1-20261031','summary.json');low=P+'block5-compound-lower-context-v1-20261031';take(low,'summary.json');caps=P+'block5-compound-cap-paths-v1-20261031';take(caps,'summary.json');views=take(P+'block5-compound-wall-views-v1-20261031','summary.json');assert len(views['exports'])==5
    results=[]
    for mode,tri in worlds.items():
        proof=take(low,mode+'.json.gz');assert proof['sourceWorldSHA256']==digest(tri.tobytes())
        cp=take(caps,mode+'.json.gz');assert cp['sourceWorldSHA256']==proof['sourceWorldSHA256'] and cp['completeDrawnGroundSHA256']==proof['groundSHA256']
        targets=[p['sourceFace']for p in cp['completeGroundClearancePartition']['paths']if not p['hasExactSharedEdgeClearCapPath']]
        assert targets==[343,344,345,346,1158,1159,1443,1444]
        ctx=next(r for r in components['rows']if r['mode']==mode);assert ctx['sourceWorldSHA256']==proof['sourceWorldSHA256'];component=ctx['faces'][0]['componentFaceIds'];assert len(component)==10 and all(r['componentFaceIds']==component for r in ctx['faces'])
        negative=[r['sourceFace']for r in proof['rows']];result=wall_escape(tri,component,negative,targets);assert result['clearOriginalWallFaces']==[1445,1446]and result['allTargetsReachClearOriginalWalls']
        save(out/(mode+'.json'),dict(mode=mode,sourceWorldSHA256=proof['sourceWorldSHA256'],completeCompoundGroundSHA256=proof['groundSHA256'],**result));results.append(dict(mode=mode,**result))
    for image in views['exports']:
        p=ROOT/image['path'];assert digest(p.read_bytes())==image['sha256'];refs.append(p)
    assert reservations.owns(lease)and digest(asset.read_bytes())==source['sourceSHA256'];manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[runtime][str(manifest.relative_to(ROOT))];refs.append(manifest)
    result=dict(uids=[UID,PEER],sourceSHA256=source['sourceSHA256'],rows=results,rawCapQueryStillFails=True,rawStrictCompoundFoundationStillFails=True,sourceRoleAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,groundRootCredit=False,qualification='All10facets of this exact shared-edge skin are near-vertical. The8negative wall facets have positive-length exact shared-edge routes to ordinary-clear wall facets1445/1446 in every representation. The upward-cap query failed because this entire skin has no upward cap. This is geometric wall-exposure context, not a new support root, engineering/closed-solid claim, strict-foundation pass, source-role or publication approval. Raw compound warnings remain.')
    save(out/'summary.json',result);refs.extend([HERE/'original_wall_skin_escape_v1_20261031.py',HERE/'test_original_wall_skin_escape_v1_20261031.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('prosperous_wall_escape_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-world-exact-original-wall-skin-escape-context',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
