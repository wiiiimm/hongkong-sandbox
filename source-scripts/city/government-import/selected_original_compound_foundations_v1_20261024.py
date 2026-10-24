"""Measure full original sources against terrain plus explicitly named original peers.

Diagnostic only: original-authored crossings and failed samples remain unapproved.
"""
import argparse
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes']:p.add_argument('--'+key,required=True)
    p.add_argument('--pair',action='append',required=True,help='sourceUid=supportUid')
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()
    pairs=[tuple(v.split('='))for v in a.pair];assert all(len(v)==2 and v[0]!=v[1]for v in pairs)and len(set(pairs))==len(pairs)
    refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selected=take(a.runtime,base/a.runtime/'selection.json.gz');rows={r['uid']:r for r in selected['rows']}
    runtime=take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz');captured={r['uid']:r for r in runtime['rows']}
    attrs=take(a.attributes,base/a.attributes/'attributes.json.gz');at={r['uid']:r for r in attrs['rows']}
    wanted={u for pair in pairs for u in pair};assert wanted<=rows.keys()and wanted<=captured.keys()and wanted<=at.keys()
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    worlds={'original':{}}
    for uid in wanted:
        r=rows[uid];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==captured[uid]['sourceSHA256'];refs.append(asset)
        worlds['original'][uid]=decode_original_world_triangles(asset.read_bytes())
    for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode]={uid:np.asarray(at[uid][field],dtype='<f8').reshape(-1,3)[np.asarray(at[uid]['completeOriginalIndex']).reshape(-1,3)]for uid in wanted}
    kernel=module('selected_compound_foundation',HERE/'xl-final-script-pass.py');results=[]
    for mode,world in worlds.items():
        for uid,parent in pairs:
            source=world[uid];assert len(source)==rows[uid]['triangles'];ground=np.asarray(captured[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
            support=np.concatenate([ground,world[parent]]);b=rows[uid]['source']['building']
            f=kernel.foundation_context(source,support,Polygon(b['rings'][0],b['rings'][1:]))
            r=dict(uid=uid,supportUid=parent,mode=mode,sourceSHA256=rows[uid]['sourceSHA256'],supportSourceSHA256=rows[parent]['sourceSHA256'],worldSHA256=digest(source.tobytes()),supportWorldSHA256=digest(support.tobytes()),foundation=f)
            results.append(r);save(out/(uid.replace('/','-').replace(':','-')+'--'+parent.split('/')[1]+'--'+mode+'.json'),r)
            print(uid,parent,mode,{k:v for k,v in f.items()if k!='components'},flush=True)
    assert digest(manifest.read_bytes())==selected['manifestSHA256']
    result=dict(uids=sorted(wanted),rows=results,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,qualification='Complete existing foundation kernel over unchanged originals and current captured terrain in all four coordinate streams. Peer surfaces are diagnostic compound envelopes, not earth. Preserve every negative; this alone grants no source-role, support, crossing, identity or publication approval.')
    save(out/'summary.json',result);refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('selected_compound_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-four-world-original-compound-foundations',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
