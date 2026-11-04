"""Run unchanged strict support-interface probes on joined original captures.

No terrain/foundation or physical acceptance is inferred from these probes.
"""
import argparse
from pathlib import Path
import subprocess
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','runtime','attributes','uid','support']:
        p.add_argument('--'+name,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch
    assert a.batch.startswith('government-xl-') and '/'not in a.batch and not out.exists() and not local.exists()
    assert a.uid!=a.support
    refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selected=take(a.runtime,'selection.json.gz');attrs=take(a.attributes,'attributes.json.gz');assert attrs['startEndAllInputsVerified']
    by={r['uid']:r for r in selected['rows']};attrs={r['uid']:r for r in attrs['rows']};worlds={};hashes={}
    for uid in [a.uid,a.support]:
        row=by[uid];attr=attrs[uid];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==attr['sourceSHA256'];refs.append(asset);hashes[uid]=row['sourceSHA256']
        ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        worlds[uid]=dict(original=decode_original_world_triangles(asset.read_bytes()))
        worlds[uid].update({mode:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]})
        assert all(len(t)==row['triangles'] and np.isfinite(t).all()for t in worlds[uid].values())
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    payload={mode:dict(source=dict(position=worlds[a.uid][mode].reshape(-1).tolist()),support=dict(position=worlds[a.support][mode].reshape(-1).tolist()))for mode in worlds[a.uid]}
    source=local/'input.json.gz';destination=out/'interfaces.json.gz';save(source,payload);out.mkdir(parents=True)
    tool=HERE/'four_world_support_probe_v1.mjs';subprocess.run(['node',str(tool),str(source),str(destination)],cwd=ROOT,check=True)
    rows=read(destination)['rows'];assert {r['mode']for r in rows}==set(payload) and len(rows)==4
    result=dict(uids=[a.uid,a.support],sourceSHA256ByUid=hashes,rows=rows,
                sourceWorldSHA256ByMode={mode:{uid:digest(worlds[uid][mode].astype('<f8').tobytes())for uid in worlds}for mode in payload},
                sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,
                qualification='Unmodified strict support-interface.mjs run against every represented original source face. Raw unresolved witnesses preserved. Does not establish terrain/foundation, architectural intent, load dependencies or installation acceptance.')
    save(out/'summary.json',result);refs.extend([source,tool,HERE/'support-interface.mjs',HERE/'exact_packed_world_geometry_20261009.py'])
    module('cross_capture_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'strict-original-cross-capture-four-world-support-probe',refs,result)
    print([dict(mode=r['mode'],interfaceKeys=list(r['interface']),unresolved=len(r['interface']['unresolved']))for r in rows],flush=True)


if __name__=='__main__':main()
