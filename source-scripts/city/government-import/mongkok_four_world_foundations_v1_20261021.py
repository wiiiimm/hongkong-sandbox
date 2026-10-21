"""Complete stadium foundations in original, literal and both explicit Float32 modes."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mongkok-four-world-foundations-v1-20261021';DOC=BASE/BATCH

def main():
    assert not DOC.exists();refs=[Path(__file__)];pins={}
    def take(batch,p):
        _,ps=authenticate(BASE/batch);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/batch/'result.json',p]);return read(p)
    batch='government-xl-mongkok-inset-pair-runtime-v1-20261021';selection=take(batch,BASE/batch/'selection.json.gz')['rows'];runtime=take(batch,HERE/'local'/batch/'after-geometry.json.gz');geometry={r['uid']:r for r in runtime['rows']}
    batch='government-xl-mongkok-actual-render-attributes-v1-20261021';attrs=take(batch,BASE/batch/'attributes.json.gz');attributes={r['uid']:r for r in attrs['rows']};final=module('stadium_four_foundations',HERE/'xl-final-script-pass.py');results=[]
    for row in selection:
        uid=row['uid'];a=attributes[uid];g=geometry[uid];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
        worlds={'original':decode_original_world_triangles(asset.read_bytes())}
        for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
            worlds[mode]=np.asarray(a[field],dtype='<f8').reshape(-1,3)[np.asarray(a['completeOriginalIndex']).reshape(-1,3)]
        assert np.array_equal(worlds['literal'],np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)])
        ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building'];foot=Polygon(b['rings'][0],b['rings'][1:])
        for mode,t in worlds.items():
            assert len(t)==row['triangles'];foundation=final.foundation_context(t,ground,foot);save(DOC/(uid.split('/')[1]+'-'+mode+'.json'),dict(uid=uid,mode=mode,foundation=foundation))
            result=dict(uid=uid,mode=mode,worldSHA256=digest(t.astype('<f8').tobytes()),**{k:v for k,v in foundation.items()if k!='components'});results.append(result);print(uid,mode,result['fullyBuriedTriangles'],flush=True)
    passed=all(r['completeTerrainTriangles']==r['triangles']and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in results)
    summary=dict(uids=[r['uid']for r in selection],rows=results,allFourWorldFoundationsPassed=passed,installationApproved=False);save(DOC/'summary.json',summary)
    for k,h in pins.items():assert digest((ROOT/k).read_bytes())==h
    refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py']);module('stadium_four_foundations_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-stadium-four-world-foundations',list(dict.fromkeys(refs)),summary)
if __name__=='__main__':main()
