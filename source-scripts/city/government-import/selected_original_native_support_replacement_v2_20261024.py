"""Compare installed native strict support against its current basic and proposed original.

Four complete coordinate representations, unchanged canonical support-interface
rules; diagnostic only, never changes dependencies or grants installation credit.
"""
import argparse, subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','native-contacts','runtime','attributes','neighbours','uid','support']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-') and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    native=take(a.native_contacts,'native-input.json.gz');n=next(r for r in native['rows']if r['uid']==a.uid)
    selected=take(a.runtime,'selection.json.gz');s=next(r for r in selected['rows']if r['uid']==a.support)
    na=next(r for r in take(a.native_contacts,'native-attributes.json.gz')['rows']if r['uid']==a.uid)
    sa=next(r for r in take(a.attributes,'attributes.json.gz')['rows']if r['uid']==a.support)
    neighbours=take(a.neighbours,'neighbour-inputs.json.gz');basic=next(r for r in neighbours['rows']if r['building']['uid']==a.support)
    dependencies=n['entry'].get('supportDependencies',[])
    assert any(r['uid']==a.support and r['state']=='surveyed-footprint-fallback' and r['csuid']==s['candidate']['entry']['buildingCSUID']for r in dependencies)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    matching=[]
    for tile,sha in neighbours['inputHashes'].items():
        if '/tiles/' in tile:
            path=ROOT/tile;assert digest(path.read_bytes())==sha;refs.append(path)
            for form in read(path)['buildings']:
                if form['uid']==a.support:
                    assert form==basic['building'];matching.append(tile)
    assert len(matching)==1
    basic_tool=HERE/'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs'
    save(out/'basic-input.json',dict(manifestSHA256=selected['manifestSHA256'],currentInputHashes=neighbours['inputHashes'],rows=[dict(building=basic['building'],tile=matching[0])]))
    with(out/'basic.log').open('w')as log:subprocess.run(['node',str(basic_tool),str((out/'basic-input.json').relative_to(ROOT)),str((out/'basic.json').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    before=read(out/'basic.json');b=before['rows'][0];bt=np.asarray(b['position']).reshape(-1,3)[np.asarray(b['index']).reshape(-1,3)]
    fields={'literal':'completeLiteralWorldPosition','leftF32':'completeExplicitLeftAssociatedFloat32WorldPosition','balancedF32':'completeExplicitBalancedFloat32WorldPosition'}
    def worlds(attr,path,sha):
        assert digest(path.read_bytes())==sha==attr['sourceSHA256'];refs.append(path);idx=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        return {'original':decode_original_world_triangles(path.read_bytes()),**{k:np.asarray(attr[f]).reshape(-1,3)[idx]for k,f in fields.items()}}
    nw=worlds(na,ROOT/n['path'],n['entry']['sha256']);sw=worlds(sa,ROOT/s['candidate']['path'],s['sourceSHA256'])
    tool=HERE/'wave_retained_basic_support_v1_20261017.mjs';rows=[]
    for mode,tri in nw.items():
        reports={}
        for label,lower in [('currentBasic',bt),('proposedOriginal',sw[mode])]:
            folder=out/mode/label;position=tri.reshape(-1).tolist();save(folder/'input.json.gz',dict(rows=[dict(uid=a.uid,position=position,index=list(range(len(position)//3)))],podium=lower.tolist()))
            with(folder/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(folder.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
            report=read(folder/'support.json.gz');reports[label]=report['rows'][0]['proof']
            for path,sha in report['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
            r=reports[label];print(dict(mode=mode,support=label,passed=r['passed'],samples=r['samples'],strictContacts=r['strictContacts'],unresolved=len(r['unresolved'])),flush=True)
        rows.append(dict(mode=mode,reports=reports))
    for path,sha in before['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    assert digest(manifest.read_bytes())==selected['manifestSHA256']
    result=dict(uids=[a.uid,a.support],supportedUid=a.uid,supportUid=a.support,rawCurrentSupportDependencies=dependencies,rows=rows,allFourProposedStrictPassed=all(r['reports']['proposedOriginal']['passed']for r in rows),sourceGeometryChanges=0,dependencyMetadataChanges=0,installationApproved=False,publication=False,qualification='Actual current installed native and proposed original meshes in four complete coordinate representations tested against unchanged canonical strict support interface. Current BASIC rendered mesh retained as measured baseline, not assumed passing. Raw failures remain. No foundation, identity, collision, dependency replacement or publication approval.')
    save(out/'summary.json',result);refs.extend([tool,basic_tool,HERE/'exact_packed_world_geometry_20261009.py'])
    module('native_support_replacement_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-current-native-basic-to-original-support-replacement-diagnostic',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
