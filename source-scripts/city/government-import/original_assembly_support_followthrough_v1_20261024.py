"""Run strict support/finite-path diagnostics for measured original assembly pairs.

No support dependency is adopted and no identity/physical/publication approval is given.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','pairs']:parser.add_argument('--'+key,required=True)
    for key in ['child','parent']:parser.add_argument('--'+key,action='append',required=True)
    parser.add_argument('--workers',type=int,default=2)
    args=parser.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [args.batch,args.runtime,args.attributes,args.pairs])
    assert 1<=args.workers<=4
    children=set(args.child);parents=set(args.parent)
    assert not children&parents and len(children)==len(args.child)and len(parents)==len(args.parent)
    base=ROOT/'docs/astra-city/government-import';out=base/args.batch;assert not out.exists()
    pair_result,pins=authenticate(base/args.pairs);pairpath=base/args.pairs/'summary.json'
    assert digest(pairpath.read_bytes())==pins[str(pairpath.relative_to(ROOT))]
    pairs=read(pairpath);assert children|parents<=set(pairs['uids'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest.read_bytes())
    nominated=[]
    for child in sorted(children):
        for parent in sorted(parents):
            rows=[r for r in pairs['rows']if{r['uid'],r['peerUid']}=={child,parent}]
            assert len(rows)==4 and{r['mode']for r in rows}=={'original','literal','leftF32','balancedF32'}
            if all(not r['strictBoundsSeparated']and r['positiveSurfaceContacts']>0 for r in rows):nominated.append((child,parent))
    assert nominated and len(nominated)<=32
    out.mkdir()

    def work(pair):
        child,parent=pair;stem=args.batch+'-'+child.split('/')[1].split(':')[0]+'-'+parent.split('/')[1].split(':')[0]
        strict=stem+'-strict';paths=stem+'-paths'
        commands=[['original_pair_four_world_support_v1_20261023.py','--batch',strict,'--runtime',args.runtime,'--attributes',args.attributes,'--supported',child,'--support',parent]]
        completed=[]
        def call(command):
            logpath=out/(child.split('/')[1]+'--'+parent.split('/')[1]+'--'+str(len(completed))+'.log')
            with logpath.open('w')as log:
                proc=subprocess.run([sys.executable,str(HERE/command[0]),*command[1:]],cwd=ROOT,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'},stdout=log,stderr=subprocess.STDOUT)
            save(logpath.with_suffix('.json'),dict(command=command,exitCode=proc.returncode))
            assert proc.returncode==0,(child,parent,command[0])
            completed.append(command[0])
        call(commands[0])
        strict_receipt,_=authenticate(base/strict);summary=read(base/strict/'summary.json')
        result=dict(uid=child,supportUid=parent,strictBatch=strict,strictJobId=strict_receipt['jobId'],strictAllFourPassed=summary['allFourModesPassed'],dependencyAdopted=False)
        if not summary['allFourModesPassed']:
            command=['original_four_world_contact_paths_v1_20261023.py','--batch',paths,'--capture',args.runtime,'--attributes',args.attributes,'--support-checks',strict,'--uid',child,'--support',parent]
            call(command);receipt,_=authenticate(base/paths);s=read(base/paths/'summary.json')
            result.update(pathsBatch=paths,pathsJobId=receipt['jobId'],allUnresolvedHaveFinitePaths=s['allUnresolvedHaveFinitePaths'],pathCounts=[dict(mode=r['mode'],targets=r['targets'],verified=r['verifiedPaths'],remaining=r['remaining'])for r in s['rows']])
        print(result,flush=True)
        return result

    with ThreadPoolExecutor(max_workers=args.workers)as pool:results=list(pool.map(work,nominated))
    assert digest(manifest.read_bytes())==manifest_sha
    result=dict(uids=sorted(children|parents),nominatedPairs=len(nominated),rows=results,currentManifestSHA256=manifest_sha,
        sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,
        qualification='All nominated positive original-surface pairs checked in all4 coordinate streams. These are alternative support diagnostics, not adopted dependencies or physical acceptance. Preserve every raw strict/path failure and assess authored roles and actual ground separately.')
    save(out/'summary.json',result)
    refs=[Path(__file__),base/args.pairs/'result.json',pairpath,manifest]
    for r in results:
        for key in ['strictBatch','pathsBatch']:
            if key in r:refs.extend([base/r[key]/'result.json',base/r[key]/'summary.json'])
    refs.extend(HERE/name for name in ['original_pair_four_world_support_v1_20261023.py','original_four_world_contact_paths_v1_20261023.py'])
    module('original_assembly_support_followthrough_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch,'complete-measured-original-support-pair-followthrough-no-acceptance',refs,result)


if __name__=='__main__':main()
