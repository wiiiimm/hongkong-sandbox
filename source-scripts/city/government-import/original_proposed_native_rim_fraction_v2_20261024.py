"""Bind exact current arrays to the unchanged runtime low-rim support diagnostic."""
import argparse,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','support']:p.add_argument('--'+key,required=True)
    p.add_argument('--uid',action='append',required=True);a=p.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.runtime,a.attributes])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(name,filename):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        path=base/name/filename;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selected={r['uid']:r for r in take(a.runtime,'selection.json.gz')['rows']};attrsdata=take(a.attributes,'attributes.json.gz');assert attrsdata['startEndAllInputsVerified'];attrs={r['uid']:r for r in attrsdata['rows']}
    assert len(a.uid)==len(set(a.uid)) and a.support not in a.uid
    worlds={};positions={}
    for uid in [a.support,*a.uid]:
        r,at=selected[uid],attrs[uid];path=ROOT/r['candidate']['path'];raw=path.read_bytes();assert digest(raw)==r['sourceSHA256']==at['sourceSHA256'];refs.append(path);ix=np.asarray(at['completeOriginalIndex']).reshape(-1,3)
        worlds[uid]=dict(original=decode_original_world_triangles(raw))
        # Keep the exact runtime vertex weighting in the original stream too.
        # Expanding triangle corners would count shared vertices repeatedly.
        unique,first=np.unique(ix.reshape(-1),return_index=True)
        assert np.array_equal(unique,np.arange(len(at['completeLiteralWorldPosition'])//3))
        original_positions=worlds[uid]['original'].reshape(-1,3)[first]
        assert np.array_equal(original_positions[ix],worlds[uid]['original'])
        positions[uid]=dict(original=original_positions)
        for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
            positions[uid][mode]=np.asarray(at[field]).reshape(-1,3);worlds[uid][mode]=positions[uid][mode][ix]
    inputpath=out/'input.json.gz';save(inputpath,dict(supportEntry=selected[a.support]['candidate']['entry'],supportWorlds={k:v.tolist()for k,v in worlds[a.support].items()},actors=[dict(uid=u,entry=selected[u]['candidate']['entry'],positionWorlds={k:v.tolist()for k,v in positions[u].items()})for u in a.uid]));refs.append(inputpath)
    tool=HERE/'original_proposed_native_rim_fraction_v1_20261024.mjs';reportpath=out/'runtime-rim-fractions.json'
    with(out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(inputpath),str(reportpath)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    report=read(reportpath);assert report['inputSHA256']==digest(inputpath.read_bytes());assert len(report['rows'])==4*len(a.uid);refs.extend([tool,reportpath,HERE.parent/'assembly-support-review/triangles.mjs',HERE/'check-native-neighbours-current-installed-v4-20261022.mjs',HERE/'exact_packed_world_geometry_20261009.py'])
    result=dict(uids=[a.support,*a.uid],supportUid=a.support,rows=[{k:v for k,v in r.items()if k!='witnesses'}for r in report['rows']],allFourActorFractionsPass=report['allFourActorFractionsPass'],sourceGeometryChanges=0,dependencyMetadataChanges=0,originalRuntimeVertexIndexWeightingPreserved=True,installationApproved=False,publication=False)
    save(out/'summary.json',result);module('proposed_original_native_rim_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-unchanged-viewer-rim-rule-for-proposed-original-support',refs,result);print(result['rows'],flush=True)


if __name__=='__main__':main()
