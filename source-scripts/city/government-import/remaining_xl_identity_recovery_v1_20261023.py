"""Finish failed identity chunks from existing current captures; no capture restart or admission."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys
import time
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','parent']:p.add_argument('--'+k,required=True)
    p.add_argument('--parent-pid',type=int,required=True);a=p.parse_args()
    assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();out.mkdir()
    parent=base/a.parent;deadline=time.monotonic()+14400
    while not(parent/'result.json').exists():
        assert time.monotonic()<deadline,'Parent observation deadline; do not restart captures'
        command=Path('/proc')/str(a.parent_pid)/'cmdline'
        assert command.exists(),'Parent stopped without completed receipt; investigate, do not restart'
        args=command.read_bytes().split(b'\0')
        assert len(args)>2 and args[1].endswith(b'/remaining_xl_current_scene_batch_v2_20261023.py')and a.parent.encode()in args,'Exact parent process changed'
        save(out/'waiting.json',dict(parent=a.parent,verifiedParentPid=a.parent_pid,observation='exact-live-cmdline',publication=False))
        time.sleep(20)
    parentreceipt,pins=authenticate(parent);selectionpath=parent/'selection.json';summarypath=parent/'summary.json'
    for path in [selectionpath,summarypath]:assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
    selected=read(selectionpath);prior=read(summarypath);expected={u for chunk in selected['chunks']for u in chunk}
    assert len(expected)==selected['selected']==178
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']
    refs=[Path(__file__),parent/'result.json',selectionpath,summarypath,manifest,HERE/'selected_original_identity_v3_20261023.py',HERE/'guarded_original_exact_cell_identity_v1_20261023.py',HERE/'acceptance-policy.py']
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1'}
    def process(chunk):
        number=chunk['chunk'];uids=chunk['uids'];runtime=next(j['batch']for j in chunk['completedJobs']if j['batch'].endswith('-runtime'))
        rr,rp=authenticate(base/runtime);assert set(rr['uids'])==set(uids)
        if chunk['status']=='current-scene-checked':
            identity=chunk['batches']['identity'];authenticate(base/identity)
            return dict(chunk=number,rows=chunk['rows'],identityBatch=identity,runtimeBatch=runtime,recovered=False)
        assert chunk['status']=='script-adapter-investigation'and chunk['stoppedAt']=='identity','Unexpected earlier failure; preserve it for investigation'
        identity=a.batch+'-chunk-'+str(number).zfill(2)+'-identity'
        with(out/(str(number).zfill(2)+'-identity.log')).open('w')as log:
            subprocess.run([sys.executable,str(HERE/'selected_original_identity_v3_20261023.py'),'--batch',identity,'--capture',runtime],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        authenticate(base/identity)
        metrics=read(base/runtime/'metrics.json');foundation=read(base/runtime/'summary.json');source=read(base/runtime/'selection.json.gz');ids=read(base/identity/'summary.json')
        bymetric={r['uid']:r for r in metrics['rows']};byfoundation={r['uid']:r for r in foundation['rows']};bysource={r['uid']:r for r in source['rows']};byidentity={r['uid']:r for r in ids['rows']}
        assert set(bymetric)==set(byfoundation)==set(bysource)==set(byidentity)==set(uids)
        policy=module('recovered_current_policy_'+str(number),HERE/'acceptance-policy.py');rows=[]
        for uid in uids:
            s,m,f,i=bysource[uid],bymetric[uid],byfoundation[uid],byidentity[uid]
            proof=read(base/identity/uid.split('/')[1]/'identity.json')['proof']
            reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=s['sourceSHA256'],identityProof=proof),m,metrics['profiles']['mobile'])
            whole=f['status']=='captured'and f['completeTerrainTriangles']==f['triangles']and f['fullyBuriedTriangles']==0
            ready=not reasons and i['passed']and whole
            status='ready-for-all-mode-and-browser-checks'if ready else'runtime-investigation'if m.get('error')else'current-scene-investigation'
            rows.append(dict(uid=uid,sourceSHA256=s['sourceSHA256'],status=status,rawPolicyReasons=reasons,identityReasons=i['reasons'],foundation=f,installationApproved=False,permanentRejection=False))
        result=dict(chunk=number,rows=rows,identityBatch=identity,runtimeBatch=runtime,recovered=True)
        save(out/('chunk-'+str(number).zfill(2)+'.json'),result);print(dict(chunk=number,completed=len(rows),counts=dict(Counter(r['status']for r in rows))),flush=True)
        return result
    with ThreadPoolExecutor(max_workers=2)as pool:chunks=list(pool.map(process,prior['chunks']))
    rows=[r for c in chunks for r in c['rows']];assert len(rows)==len({r['uid']for r in rows})==len(expected)and{r['uid']for r in rows}==expected
    consumed={}
    for chunk in chunks:
        for name in [chunk['identityBatch'],chunk['runtimeBatch']]:
            receipt,pin=authenticate(base/name);refs.append(base/name/'result.json')
            for path,sha in pin.items():assert path not in consumed or consumed[path]==sha;consumed[path]=sha
    for path,sha in consumed.items():assert digest((ROOT/path).read_bytes())==sha,path
    assert digest(manifest.read_bytes())==selected['manifestSHA256']
    save(out/'rows.json.gz',rows)
    result=dict(uids=sorted(expected),fixedXLTotal=selected['fixedXLTotal'],installed=selected['installed'],unfinished=selected['unfinished'],completedMappedThisPass=len(rows),recentlyCheckedExcluded=selected['excluded'],unmatchedSourceKeys=selected['unmatchedSourceKeys'],recoveredIdentityChunks=sum(c['recovered']for c in chunks),counts=dict(Counter(r['status']for r in rows)),chunks=chunks,installationApproved=False,publication=False,newlyInstalled=0,permanentRejection=False,sourceGeometryChanges=0,scriptExternalAICalls=0,qualification='Every selected source has current V3 renderer/height bindings and strict source identity diagnostics. Unsupported cells remain explicit per-source holds; no failing record aborts its chunk. Fresh captures reused unchanged, no automatic installation, source corruption or permanent-rejection credit.')
    assert result['completedMappedThisPass']+len(result['recentlyCheckedExcluded'])+len(result['unmatchedSourceKeys'])==result['unfinished']
    save(out/'summary.json',result);module('remaining_identity_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-current-xl-identity-recovery',refs,result)
    print({k:result[k]for k in ['completedMappedThisPass','recoveredIdentityChunks','counts']},flush=True)

if __name__=='__main__':main()
