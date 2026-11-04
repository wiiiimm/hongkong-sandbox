"""Source-only probe of BASIC37934 over exact original West Kowloon podium.

No current-scene acceptance or dependency edits. Historical original coordinate
streams stay labelled; a fresh actual BASIC mesh is captured under current hashes.
"""
from pathlib import Path
import subprocess
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-west-kowloon-bus-';batch=prefix+'retained-basic37934-support-probe-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(name,file):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime=prefix+'all-buried-inset-runtime-v1-20261024';selected=take(runtime,'selection.json.gz');assert len(selected['rows'])==1;row=selected['rows'][0];assert row['uid']=='landsd/255415:0'
    attrs=take(prefix+'all-buried-inset-prephysical-v1-20261024-attributes','attributes.json.gz');a=attrs['rows'][0];assert a['uid']==row['uid'] and a['sourceSHA256']==row['sourceSHA256']
    forms=take(prefix+'all-buried-inset-scope-v1-20261024','form-obligations.json.gz');basic=next(r for r in forms if r['uid']=='landsd/37934:0')
    manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest.read_bytes());m=read(manifest);tile=next(t['url']for t in m['tiles']if t['id']==basic['tile']);tilepath=ROOT/'3d-viewer'/tile;assert next(b for b in read(tilepath)['buildings']if b['uid']==basic['uid'])==basic
    refs.extend([manifest,tilepath]);save(out/'basic-inputs.json',dict(manifestSHA256=manifest_sha,currentInputHashes={str(tilepath.relative_to(ROOT)):digest(tilepath.read_bytes())},rows=[dict(building=basic,tile=str(tilepath.relative_to(ROOT)))]))
    tool=HERE/'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs'
    with(out/'basic.log').open('w')as log:subprocess.run(['node',str(tool),str((out/'basic-inputs.json').relative_to(ROOT)),str((out/'basic.json').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    capture=read(out/'basic.json');target=capture['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);idx=np.asarray(a['completeOriginalIndex']).reshape(-1,3)
    worlds={'original':decode_original_world_triangles(asset.read_bytes()),**{name:np.asarray(a[field]).reshape(-1,3)[idx]for name,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
    support_tool=HERE/'wave_retained_basic_support_v1_20261017.mjs';rows=[]
    for mode,tri in worlds.items():
        folder=out/mode;save(folder/'input.json.gz',dict(rows=[target],podium=tri.tolist()))
        with(folder/'worker.log').open('w')as log:subprocess.run(['node',str(support_tool),str(folder.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        report=read(folder/'support.json.gz');proof=report['rows'][0]['proof'];rows.append(dict(mode=mode,sourceWorldSHA256=digest(tri.astype('<f8').tobytes()),proof=proof))
        for path,sha in report['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
        print(dict(mode=mode,passed=proof['passed'],samples=proof['samples'],strictContacts=proof['strictContacts'],unresolved=len(proof['unresolved'])),flush=True)
    for path,sha in capture['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    assert digest(manifest.read_bytes())==manifest_sha
    result=dict(uids=[row['uid'],basic['uid']],originalUid=row['uid'],basicUid=basic['uid'],sourceSHA256=row['sourceSHA256'],historicalOriginalCaptureManifestSHA256=selected['manifestSHA256'],currentBasicCaptureManifestSHA256=manifest_sha,currentBasicForm=basic,rows=rows,allFourStrictSupportPassed=all(r['proof']['passed']for r in rows),currentRendererAcceptance=False,sourceGeometryChanges=0,sourcePoseChanges=0,dependencyEdits=0,installationApproved=False,publication=False,qualification='Existing canonical support-interface checks only. Actual unchanged original source in four authenticated historical coordinate streams versus fresh current BASIC geometry. Does not rebind whole current scene, resolve its neighbour flag, alter dependencies or approve installation. Source/manifest refresh remains necessary after other installations.')
    save(out/'summary.json',result);refs.extend([tool,support_tool,HERE/'exact_packed_world_geometry_20261009.py']);module('west_basic_support_probe_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'west-kowloon-retained-basic-over-original-four-world-source-probe',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
